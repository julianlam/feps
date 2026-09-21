---
slug: "c0d0"
authors: Julian Lam <julian@nodebb.org>
status: DRAFT
discussionsTo: https://activitypub.space/topic/639/fep-c0d0-context-locking
dateReceived: 2026-09-18
---
# FEP-c0d0: Context Locking


## Summary

Context locking (and its inverse, unlocking) refer to the action whereby a topic no longer accepts new replies.

This proposal introduces a `locked` property on the context object, and a new activity type, `Lock`, to signal changes to a topic's locked state across the fediverse. Unlocking is expressed with the standard ActivityStreams [`Undo` activity][Undo], applied to the original `Lock`. It builds on [FEP 1b12: Group federation][1b12] for audience identification (the `audience` property) and the `Announce` wrapping pattern, and on [FEP fe34: Origin-based security model][OriginBasedSecurityModel] for authorization.

This FEP is a sibling of [FEP f15d: Context Relocation and Removal][f15d], which covers the `Move` and `Remove` moderation actions.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].


## Assumptions

### Nomenclature

The Forums and Threaded Discussions Task Force (ForumWG) has [identified a common nomenclature][Nomenclature] when referring to organized objects in a threaded discussion model. The two terms used in this FEP are described below:

#### Context

A group of related objects (i.e. via reply-association) is referred to as a "context". Other terms for this concept would be "topic" or "thread".

#### Audience

Contexts (see above) can be further grouped together into "audiences". Other terms for this concept would be "community", "category", or "forum". In ActivityPub, audiences usually take the form of a [`Group` Actor type][GroupActor].


### Referencing threaded objects as a whole

ActivityPub implementations differ in how they represent the aggregated collection of threaded objects.

Some implementations represent these collections as a distinct abstraction (e.g. a context.)

Others make no such distinction and represent them via the root-level object (e.g. link aggregators.)

The resolvable contexts tree of FEPs _requires_ that abstraction in order to communicate actions pertaining to it in an explicit manner.

For more information, see [FEP 7888][7888].


### Topic locking

A context may be in a **locked** state, in which new replies are not accepted. Locking and unlocking a context is a moderation action, typically performed by a moderator of the context's audience.

This FEP assumes the resolvable-contexts model of [FEP 7888][7888], in which a context is addressable as a discrete object so that actions pertaining to it (such as locking) can be communicated explicitly.


## Prior art

### Lemmy

The `Lock` activity is not new. [Lemmy][LemmyFederation] already uses a `Lock` activity in the same manner and intent: to lock a thread so that no new replies can be created.

``` json
{
    id: "http://lemmy-alpha:8541/activities/lock/cb48761d-9e8c-42ce-aacb-b4bbe6408db2",
    actor: "http://lemmy-alpha:8541/u/lemmy_alpha",
    to: ["https://www.w3.org/ns/activitystreams#Public"],
    object: "http://lemmy-alpha:8541/post/2",
    cc: ["http://lemmy-alpha:8541/c/main"],
    type: "Lock",
    audience: "http://lemmy-alpha:8541/c/main",
}
```

The distinction between Lemmy's usage and this FEP is what the `object` property points to:

* In **Lemmy**, `object` is the post itself — a `Page` (Note-like) object. Lemmy has no separate context abstraction: the top-level post is both the root object and, implicitly, the thread, so pointing `object` at the post is sufficient to identify the thread being locked.
* In **this FEP**, `object` is a **resolvable context** (per [FEP 7888][7888]) — a distinct, addressable object that represents the thread as a whole, separate from its root post.

This reflects the broader divergence described in [Referencing threaded objects as a whole](#referencing-threaded-objects-as-a-whole). Because the two `object` values are different kinds of objects (a `Page`/`Note` versus a context), a receiver of one form is not expected to understand the other.

### GoToSocial interaction controls

[GoToSocial][GotoSocialInteractionControls] implements per-object **interaction controls** via an `interactionPolicy` property on post-like objects (`Note`, `Article`, `Question`, …), with `canLike`, `canReply`, and `canAnnounce` sub-policies. The closest analogue to locking a context is a `canReply` policy that permits no automatic replies:

``` json
{
    interactionPolicy: {
        canReply: {
            automaticApproval: [],
        },
    },
}
```

This is materially different from the `Lock` activity in two ways:

* **Scope.** An `interactionPolicy` is attached to a single post-like object, not to a context. GoToSocial has no context abstraction, and each reply in a thread carries its own policy, so the scope of a thread can widen post-hoc. A `Lock` targets the resolvable context as a whole and applies to every object in it — including cross-origin (mirrored) objects — so no new replies are accepted to any of them.
* **Hardness.** GoToSocial always enforces two *implicit assumptions*, regardless of the stated policy: the post author can always reply to their own post, and any actor mentioned in or replied to by a post can always reply. A `canReply` policy of `automaticApproval: []` therefore does not in fact lock the thread for the author (or for mentioned/replied-to actors). This FEP does **not** adopt those implicit assumptions: a locked context accepts no new replies, full stop.


## The `locked` property

A resolvable context (per [FEP 7888][7888]) MUST expose a `locked` property, a boolean value indicating the context's current locked state.

* `locked: true` — the context does not accept new replies.
* `locked: false` — the context accepts new replies.

The `locked` property represents the *current state* of the context. The `Lock` activity and its `Undo`, described below, signal *changes* to that state; a receiver SHOULD update the `locked` property of a mirrored context when it processes such an activity.

For robustness, receivers SHOULD treat an absent `locked` property as `false`.


## The `Lock` activity

When a context is locked, a `Lock` activity is published to the followers of the context's audience.

``` json
{
    @context: [
        "https://www.w3.org/ns/activitystreams",
        {
            "Lock": "https://w3id.org/fep/c0d0/Lock"
        }
    ],
    id: "https://example.social/context/123#activity/lock/<timestamp>",
    type: "Lock",
    actor: "https://example.social/uid/1",
    audience: "https://example.social/audience/1",
    object: "https://example.social/context/123",
}
```

Note the following properties:

* `actor` is the user actor carrying out the action; typically a moderator (see [Security Considerations](#security))
* `audience` is the context's audience (a `Group` actor), per [FEP 1b12][1b12]
* `object` is the context (a resolvable context, per [FEP 7888][7888])

### Unlocking via `Undo`

Unlocking a context is expressed with the standard ActivityStreams 2.0 [`Undo` activity][Undo], whose `object` is the `Lock` activity being undone:

``` json
{
    @context: [
        "https://www.w3.org/ns/activitystreams",
        {
            "Lock": "https://w3id.org/fep/c0d0/Lock"
        }
    ],
    id: "https://example.social/context/123#activity/undo/<timestamp>",
    type: "Undo",
    actor: "https://example.social/uid/1",
    object: "https://example.social/context/123#activity/lock/<timestamp>",
}
```

Per ActivityStreams 2.0, the `object` of an `Undo` is the activity being undone — not the context itself. A receiver resolves the referenced `Lock` activity and applies the unlock to its `object` (the context).

>[!NOTE]
> `Lock` is not a standard ActivityStreams type. Implementations SHOULD declare it in `@context`, expanded to the FEP namespace (`https://w3id.org/fep/c0d0/Lock`) per [FEP 888d][888d], to avoid collisions. Receivers SHOULD resolve the bare `Lock` term to this URI, and SHOULD also accept the full URI used directly in `type`. The `Undo` type is standard ActivityStreams 2.0 and requires no such declaration.

### `Audience` wrapper

Implementations MAY wrap the `Lock` activity (or its `Undo`) in an `Announce` activity, with the audience's `Group` actor as the `actor` and the audience's followers among the recipients. Receivers are recommended to support both the direct and wrapped forms.

``` json
{
    @context: [
        "https://www.w3.org/ns/activitystreams",
        {
            "Lock": "https://w3id.org/fep/c0d0/Lock"
        }
    ],
    id: "https://example.social/audience/1#activity/announce/<timestamp>",
    type: "Announce",
    actor: "https://example.social/audience/1",
    to: ["https://www.w3.org/ns/activitystreams#Public"],
    cc: ["https://example.social/audience/1/followers"],
    object: {
        id: "https://example.social/context/123#activity/lock/<timestamp>",
        type: "Lock",
        actor: "https://example.social/uid/1",
        audience: "https://example.social/audience/1",
        object: "https://example.social/context/123",
    },
}
```

When the wrapped form is used, the `audience` property on the inner `Lock` activity and the `Announce`'s `actor` SHOULD identify the same audience.


## Reception

A receiver of a `Lock` activity, or the `Undo` of one (direct, or via `Announce`) SHOULD:

1. Resolve the target context: for a `Lock`, this is its `object`; for an `Undo`, this is the `object` of the referenced `Lock` activity. If the context is not mirrored locally, the activity SHOULD be ignored.
2. Verify authorization (see [Security Considerations](#security)).
3. Update the context's locked state accordingly, attributing the change to the activity's `actor`.

Receivers SHOULD treat these activities as idempotent: locking an already-locked context, or unlocking an already-unlocked context, is a no-op.

>[!NOTE]
> A **lock** is functionally different from a **removal** (see [FEP f15d][f15d]). A locked context is still visible and readable; it simply no longer accepts new replies.


## Security Considerations

### Same-Origin Check

As per [FEP fe34][OriginBasedSecurityModel], a `Lock` activity (or its `Undo`) is assumed to be authentic if the `actor` and the context's `audience` are same-origin.

### Moderator Collection Check

[FEP-1b12: Group federation][1b12] describes the use of an `OrderedCollection` referenced in an audience's `attributedTo` [to represent an audience's moderators](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md#group-moderation).

If the `actor` of the `Lock` activity (or its `Undo`) is not same-origin to the context's `audience`, this collection SHOULD be cross-referenced for authorization.

### Superseding the Same-Origin Check

The same-origin check is a coarse, origin-based authorization: it trusts every actor from the audience's origin, and on its own cannot authorize a cross-origin moderator.

Implementations MAY supersede the same-origin check by using the audience's moderator collection (see [Moderator Collection Check](#moderator-collection-check)) as the authoritative source of authorization. When superseding, an `actor` is authorized if and only if it is a member of that collection, regardless of origin. This permits cross-origin moderators and denies same-origin non-moderators.

Superseding is OPTIONAL, but RECOMMENDED where the audience exposes a moderator collection, as it provides precise, per-actor authorization. Where no moderator collection is exposed, the same-origin check remains in effect.


## Implementors

* NodeBB (as of v4.17.0)


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary), 2017
- a, [FEP 7888: Demystifying the context property][7888], 2023
- Julian Lam, [ForumWG Nomenclature][Nomenclature], 2024
- Felix Ableitner, [FEP-1b12: Group federation][1b12], 2022
- silverpill, [FEP fe34][OriginBasedSecurityModel]: Origin-based security model
- [FEP 888d: Using https://w3id.org/fep as a base for FEP-specific namespaces][888d], 2023
- Julian Lam, Felix Ableitner, Rimu Atkinson, [FEP f15d: Context Relocation and Removal][f15d], 2026
- Lemmy, [Federation documentation][LemmyFederation]
- GoToSocial, [Interaction controls][GotoSocialInteractionControls]

[ActivityPub]: https://www.w3.org/TR/activitypub/
[7888]: https://w3id.org/fep/7888
[1b12]: https://w3id.org/fep/1b12
[Nomenclature]: https://github.com/swicg/forums/issues/4
[OriginBasedSecurityModel]: https://w3id.org/fep/fe34
[888d]: https://w3id.org/fep/888d
[f15d]: https://w3id.org/fep/f15d
[LemmyFederation]: https://join-lemmy.org/docs/contributors/05-federation.html
[GotoSocialInteractionControls]: https://docs.gotosocial.org/en/latest/federation/interaction_controls/
[GroupActor]: https://www.w3.org/TR/activitystreams-vocabulary/#dfn-group
[Undo]: https://www.w3.org/TR/activitystreams-core/#activity-undo
[RFC-2119]: https://www.ietf.org/rfc/rfc2119

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
