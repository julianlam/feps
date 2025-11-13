---
slug: "f15d"
authors: Julian Lam <julian@nodebb.org>
status: DRAFT
dateReceived: 2025-11-10
discussionsTo: *TBD*
---
# FEP-f15d: Context Relocation and Removal


## Summary

Threaded applications often have the need to move and remove content between audiences due to miscategorization or curation purposes.

This is an extension of the [Resolvable Contexts](//w3id.org/fep/7888) tree of FEPs.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].


## Assumptions

### Jurisdiction

The FEP specifically outlines the federation requirements of relocating and removing contexts from **audiences local to the instance**. It is assumed that relocation/removal of contexts from audiences _remote_ to the instance do not federate out.

For more information, see [Security Considerations](#security).

### Nomenclature

The Forums and Threaded Discussions Task Force (ForumWG) has [identified a common nomenclature][Nomenclature] when referring to organized objects in a threaded discussion model.

### Context

ActivityPub implementations differ in how they represent the aggregated collection of threaded objects.
Some implementations represent these collections as a distinct abstraction (e.g. a topic/thread in a forum.)
Others make no such distinction and represent them via the root-level object (e.g. link aggregators.)

The resolvable contexts tree of FEPs _requires_ that abstraction in order to communicate actions pertaining to it in an explicit manner.

For more information, see [FEP 7888].


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

* `actor` is the user actor carrying out the action; typically a moderator
* `cc` contains the follower collections of both the outgoing and incoming audiences
* `object` is the resolvable context
* `origin` is the outgoing context
* `target` is the incoming context
* Additional recipients can and should be added as necessary (e.g. originating author, announcers, etc.)


## Removal

When a publisher removes a context from an audience, a `Remove` activity is published to the audience's followers.

This is identical in shape to relocation, except for the change in `type` and the lack of an `origin`.


``` json
{
    @context: "https://www.w3.org/ns/activitystreams",
    id: "https://example.social/context/123#activity/move/<timestamp>",
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

Existing implementations handle the federated removal of objects by federating out a `Remove` pertaining to the root-level object.

Implementors are encouraged to support this method for compatiblity with existing implementations and/or older versions.

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

In the future, this FEP may be amended with additional moderator collection checks in order to enable cross-origin activities.


## Implementors

* NodeBB


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- a, [FEP 7888]: Demystifying the context property, 2023
- Julian Lam, [ForumWG Nomenclature][Nomenclature], 2024
- Join Lemmy: Section 30 "Federation" — ["Delete Post or Comment"][LemmyDelete]
- silverpill, [FEP fe34][OriginBasedSecurityModel]: Origin-based security model

[ActivityPub]: https://www.w3.org/TR/activitypub/
[FEP 7888]: https://w3id.org/fep/7888
[Nomenclature]: https://github.com/swicg/forums/issues/4
[LemmyDelete]: https://join-lemmy.org/docs/contributors/05-federation.html#delete-post-or-comment
[OriginBasedSecurityModel]: https://w3id.org/fep/fe34

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
