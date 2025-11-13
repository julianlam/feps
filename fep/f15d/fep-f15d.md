---
slug: "f15d"
authors: Julian Lam <julian@nodebb.org>
status: DRAFT
dateReceived: 2025-11-10
discussionsTo: *TBD*
---
# FEP-f15d: Context Relocation and Removal


## Summary

Threaded applications often have the need to move and remove content between groups/communities for curation purposes (i.e. resolving miscategorization, spam, etc.)

This is an extension of the [Resolvable Contexts][7888] tree of FEPs.


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


## Relocation

When a publisher relocates a context from one audience to another, a `Move` activity is published to both audiences' followers.

``` json
{
    @context: "https://www.w3.org/ns/activitystreams",
    id: "https://example.social/context/123#activity/move/<timestamp>",
    type: "Move",
    actor: "https://example.social/uid/1",
    to: ["https://www.w3.org/ns/activitystreams#Public"],
    cc: [
        "https://example.social/audience/1/followers",
        "https://example.social/audience/2/followers",
    ],
    object: "https://example.social/context/1",
    origin: "https://example.social/audience/1",
    target: "https://example.social/audience/2",
}
```

Note the following properties:

* `actor` is the user actor carrying out the action; typically a moderator (see [Security Considerations](#security))
* `cc` contains the follower collections of both the outgoing and incoming audiences
* `object` is the resolvable context
* `origin` is the outgoing audience
* `target` is the incoming audience
* Additional recipients can and should be added as necessary (e.g. originating author, announcers, etc.)


## Removal

When a publisher removes a context from an audience, a `Remove` activity is published to the audience's followers.

This is identical in shape to relocation, except for the change in `type` and the lack of an `origin`.


``` json
{
    @context: "https://www.w3.org/ns/activitystreams",
    id: "https://example.social/context/123#activity/remove/<timestamp>",
    type: "Remove",
    actor: "https://example.social/uid/1",
    to: ["https://www.w3.org/ns/activitystreams#Public"],
    cc: ["https://example.social/audience/1/followers"],
    object: "https://example.social/context/1",
    target: "https://example.social/audience/1",
}
```

### Backwards compatibility

_This section is non-normative_

Implementations may also handle the federated removal of objects by federating out a `Delete` referencing the root-level object. This activity is further wrapped in an `Announce` activity per [FEP 1b12][1b12].

Implementors are encouraged to support this method for compatibility with existing implementations and/or older versions.

``` json
{
    "actor": "http://ds9.lemmy.ml/u/lemmy_alpha",
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    "object": "http://ds9.lemmy.ml/post/1",
    "cc": ["http://enterprise.lemmy.ml/c/main"],
    "audience": "http://enterprise.lemmy.ml/u/main",
    "type": "Delete",
    "id": "http://ds9.lemmy.ml/activities/delete/f2abee48-c7bb-41d5-9e27-8775ff32db12"
}
```

_Example from [Join Lemmy: Section 30 "Federation" — "Delete Post or Comment"][LemmyDelete]_
<a id="security"></a>


## Security Considerations

### Same-Origin Check

As per [FEP fe34][OriginBasedSecurityModel], the `Remove` and `Move` events outlined in this FEP are assumed to be authentic if the actor and the audience(s) in question (`target` and if applicable, `origin`) are same-origin.

### Moderator Collection Check

[FEP-1b12: Group federation][1b12] describes the use of an `OrderedCollection` referenced in an audience's `attributedTo` [to represent an audience's moderators](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md#group-moderation).

If the actor of the `Move` or `Remove` activities is not same-origin to the audience(s) in question, this collection SHOULD be cross-referenced for authorization.


## Implementors

* NodeBB


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary), 2017
- a, [FEP 7888: Demystifying the context property][7888], 2023
- Julian Lam, [ForumWG Nomenclature][Nomenclature], 2024
- Felix Ableitner, [FEP-1b12: Group federation][1b12], 2022
- Join Lemmy: Section 30 "Federation" — ["Delete Post or Comment"][LemmyDelete]
- silverpill, [FEP fe34][OriginBasedSecurityModel]: Origin-based security model

[ActivityPub]: https://www.w3.org/TR/activitypub/
[7888]: https://w3id.org/fep/7888
[1b12]: https://w3id.org/fep/1b12
[Nomenclature]: https://github.com/swicg/forums/issues/4
[LemmyDelete]: https://join-lemmy.org/docs/contributors/05-federation.html#delete-post-or-comment
[OriginBasedSecurityModel]: https://w3id.org/fep/fe34
[GroupActor]: https://www.w3.org/TR/activitystreams-vocabulary/#dfn-group

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
