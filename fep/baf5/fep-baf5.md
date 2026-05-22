---
slug: "baf5"
authors: Julian Lam <julian@nodebb.org>
status: DRAFT
discussionsTo: https://activitypub.space/topic/178/fep-baf5-administrator-collection
dateReceived: 2026-05-22
trackingIssue:
---
# FEP-baf5: Administrator Collection


## Summary

This FEP introduces a mechanism for discovering the administrators of an ActivityPub instance. It extends the "Group Moderator" pattern from [FEP 1b12][1b12] and the "Application Actor" concept from [FEP d556][d556] by defining an `OrderedCollection` of administrators referenced from the instance's application actor.

### What is an administrator?

An **administrator** is a user who has carte blanche access and permission to federate moderation-style actions (object updates, deletion, etc.) on behalf of other users *on the same domain*. This aligns with the origin-based security model described in [FEP fe34][fe34], where such actions are considered authentic when the actor and the affected parties share the same origin.

This is distinct from a **moderator**, whose privileges are scoped to a specific group or community (see [FEP 1b12][1b12]). Administrators have instance-wide authority; moderators do not.

>[!NOTE]
> ActivityPub implementations may not have the concept of groups at all. In such cases, administrators are the only mechanism for delegated moderation authority. Examples of hierarchical structures across implementations:
>
> 1. NodeBB: Post &rarr; Topic &rarr; Category
> 1. Lemmy/Piefed: Comment &rarr; Post &rarr; Community

### Why is this needed?

[FEP fe34][fe34] implicitly infers moderator privilege for any same-origin actor carrying out destructive actions (update, delete, etc.) against another user on the same instance. In effect, it delegates the responsibility of determining boundaries between users to the sending instance.

This is not necessarily insecure, but without a standardized mechanism to declare those boundaries, receivers have no way to inspect or verify the authorization hierarchy on the sending side. This FEP (in conjunction with the "Group Moderation" pattern in [FEP 1b12][1b12]) makes these boundaries explicit and discoverable.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].


## Instance Actor and Application Actor

An ActivityPub server MUST publish an [Application Actor][ActivityPubActor] representing the instance itself.

The instance's application actor MUST include an `attributedTo` property referencing an `OrderedCollection` containing the instance's administrators.

``` json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": "https://example.social/actor",
    "type": "Application",
    "name": "Example Instance",
    "attributedTo": "https://example.social/administrators"
}
```


## Administrators Collection

The `attributedTo` property MUST reference an `Collection` (or `CollectionPage` for paginated collections). Each item in the collection MUST be either:

1. A URI reference to a User Actor (e.g., `https://example.social/users/admin`), or
1. A [User Actor object][ActivityPubUser] representing an administrator.

Both forms are acceptable and receivers MAY support both.

``` json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": "https://example.social/administrators",
    "type": "Collection",
    "items": [
        "https://example.social/users/alice",
        "https://example.social/users/bob"
    ]
}
```

### Collection Management

The administrators collection MAY be modified with `Add` and `Remove` activities, following the same pattern described in [FEP 1b12][1b12].

``` json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Announce",
    "actor": "https://example.social/actor",
    "id": "https://example.social/activities/announce/1",
    "object": {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Add",
        "actor": "https://example.social/users/alice",
        "id": "https://example.social/activities/add/1",
        "object": "https://example.social/users/bob",
        "target": "https://example.social/administrators"
    }
}
```

Either activity MAY be treated as a cache invalidation forcing the re-fetch of the Administrator Collection.

## Discovery

Support for this FEP is indicated by the implementation of [FEP 844e][844e], where the `implements` array of the instance's Application Actor includes:

```
{
    "href": "https://w3id.org/fep/baf5",
    "name": "FEP-baf5: Administrator Collection"
}
```


## Security and Authorization

This FEP supersedes the same-origin assumption described in [FEP fe34][fe34]. The administrators collection (in conjunction with the [FEP 1b12][1b12] moderator collection if applicable) determines whether a same-origin or cross-origin actor has administrative privilege.

When verifying the authenticity of a moderation action (such as `Update`, `Delete`, or other object mutations), a receiver SHOULD:

1. Resolve the actor of the activity.
1. Verify that the sending instance supports the Administrator Collection (this FEP), as indicated by [FEP 844e][844e]. If the FEP is not advertised, fall back to the standard origin-based security model as defined in [FEP fe34][fe34].
1. Resolve the `attributedTo` of the instance's Application Actor to obtain the administrators collection.
1. Check whether the actor is listed as an item in the administrators collection.
1. If the actor is present, the action is authentic and MAY be processed.

>[!NOTE]
> Receivers MAY cache the administrators collection to reduce network demand.

### Fallback Behavior

If the sending instance does not support the Administrator Collection (this FEP), the receiver SHOULD fall back to the standard origin-based security model as defined in [FEP fe34][fe34].


## Implementors

* NodeBB


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- Julian Lam, [FEP-1b12: Group federation][1b12], 2022
- Steve Bate, [FEP-d556: Server-Level Actor Discovery Using WebFinger][d556], 2024
- silverpill, [FEP-844e: Capability discovery][844e], 2025
- silverpill, [FEP fe34: Origin-based security model][fe34], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityPubActor]: https://www.w3.org/TR/activitypub/#actor-objects
[ActivityPubUser]: https://www.w3.org/TR/activitystreams-vocabulary/#dfn-person
[1b12]: https://w3id.org/fep/1b12
[d556]: https://w3id.org/fep/d556
[844e]: https://w3id.org/fep/844e
[fe34]: https://w3id.org/fep/fe34

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.