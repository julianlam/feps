---
slug: "c648"
authors: Evan Prodromou <evan@prodromou.name>
status: DRAFT
dateReceived: 2023-06-14
trackingIssue: https://codeberg.org/fediverse/fep/issues/123
discussionsTo: https://codeberg.org/fediverse/fep/issues/123
---
# FEP-c648: Blocked Collection

## Summary

Users need to review and revise the list of actors they have blocked. This FEP defines a new collection property, the Blocked Collection, which contains the actors that a user has blocked. It also defines a collection of `Block` activities, which can be used to undo blocks. Finally, it defines inverse properties for both collections, to aid in navigating between the collections and the actors that own them.

## Motivation

The [Activity Vocabulary][Vocab] defines a [`Block` activity type](https://www.w3.org/tr/activitystreams-vocabulary#dfn-block). The [ActivityPub][ActivityPub] specification defines [how to use a `Block` activity in the API](https://www.w3.org/TR/activitypub/#block-activity-outbox) to block another actor.

However, ActivityPub does not define an efficient way to retrieve the list of actors that a user has blocked. The only way to get this information is to scan the `outbox` collection for `Block` activities that were not the object of a later `Undo` activity. With a large `outbox`, this can be inefficient and slow.

The `followers` and `following` properties of an actor are collections of objects in the actor's social graph. By analogy, the new `blocked` property defined in this document is a collection of other actors that the actor has blocked.

One use case for the list of blocked actors is to allow the user to review and potentially undo the blocks. However, the ActivityPub specification requires the `id` of the `Block` activity to undo the block.

To make it easier to undo blocks, the `blocks` property of an actor is a collection of `Block` activities, which include the `id` of the activity, the `object` that was blocked. These activities can be used to undo the block.

Of the two properties, `blocks` is most useful for client applications, since the collection of blocked actors can be derived from the `object` property of each `Block` activity. Some implementers, however, may prefer the `blocked` property for parallelism with the `followers` and `following` properties. This specification defines both properties.

## User stories

- As an ActivityPub user, I want to see a list of actors that I have blocked, so I can confirm who I have and have not restricted.
- As an ActivityPub user, I want to undo a Block activity, so that I can interact with that actor again.

## Context

The context document for the `blocked` property is as follows:

```json
{
  "@context": {
    "bl": "https://purl.archive.org/socialweb/blocked#",
    "blocked": {
      "@id": "bl:blocked",
      "@type": "@id"
    },
    "blocks": {
      "@id": "bl:blocks",
      "@type": "@id"
    },
    "blockedOf": {
      "@id": "https://www.w3.org/ns/activitystreams#blockedOf",
      "@type": "@id"
    },
    "blocksOf": {
      "@id": "https://www.w3.org/ns/activitystreams#blocksOf",
      "@type": "@id"
    },
  }
}
```

The context document is available at the URL `https://purl.archive.org/socialweb/blocked`.

### Version-stamped context URLs

The main context URL will always have the latest version of the context document for this vocabulary. Additional context URLs are available with version numbers, to allow implementers to define their own level of tolerance to changes in the vocabulary. The version stamps use [semantic versioning][semver]. The version-stamped context URLs are:

| Context URL | Purpose |
| --- | --- |
| `https://purl.archive.org/socialweb/blocked/2.0.0` | The exact version of the context used in this document. This alias is useful for implementers that need an immutable document. |
| `https://purl.archive.org/socialweb/blocked/2.0` | The exact set of terms defined in this document, possibly with bug fixes or documentation changes. This alias is useful to get the latest version of the context document, without introducing any new terms that might conflict with other vocabularies. |
| `https://purl.archive.org/socialweb/blocked/2` | The set of terms defined in this document, plus possibly new terms, as well as bug fixes and documentation changes. This alias allows implementers to get backwards-compatible changes to the vocabulary, without having to change their code. |

## Properties

### `blocked`

|  |  |
| --- | --- |
| URI | `https://purl.archive.org/socialweb/blocked#blocked` |
| Notes | The `blocked` property of an actor is an ordered collection of ActivityPub actors. The `blocked` collection SHOULD include all actors blocked by the actor, except for those that have been unblocked by an `Undo` activity. Each actor in the `blocked` collection MUST be unique. The `blocked` collection MUST be sorted in reverse chronological order, with the most recently added actor first. (Users are most likely to want to see who they have blocked recently, so these actors should be ordered first.) As with other ActivityPub properties, the `blocked` property MAY be referenced in the actor by `id` or as an [embedded node object](https://www.w3.org/TR/json-ld11/#embedding). |
| Domain | Object (an [ActivityPub actor](https://www.w3.org/TR/activitypub/#actor)) |
| Range | [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) |
| Functional | true |

### `blocks`

|  |  |
| --- | --- |
| URI | `https://purl.archive.org/socialweb/blocked#blocks` |
| Notes | The `blocks` property of an actor is an ordered collection of `Block` activities. The `blocks` collection SHOULD include all `Block` activities by the actor, except for those that have been reverted by an `Undo` activity. Each activity in the `blocks` collection MUST be unique. The `blocks` collection MUST be sorted in reverse chronological order, with the most recent activity first.  (Users are most likely to want to see who they have blocked recently, and possibly unblock them, so these activities should be ordered first.) As with other ActivityPub properties, the `blocks` property MAY be referenced in the actor object by `id` or as an [embedded node object](https://www.w3.org/TR/json-ld11/#embedding). |
| Domain | Object (an [ActivityPub actor](https://www.w3.org/TR/activitypub/#actor)) |
| Range | [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) |
| Functional | true |

### `blockedOf`

|  |  |
| --- | --- |
| URI | `https://purl.archive.org/socialweb/blocked#blockedOf` |
| Notes | The value of the `blockedOf` property of a collection is the actor for whom the collection is the value of its `blocked` property. It is the inverse property of `blocked`. As with other ActivityPub properties, the `blockedOf` property MAY be referenced in the actor by `id` or as an [embedded node object](https://www.w3.org/TR/json-ld11/#embedding). |
| Domain | [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) |
| Range | Object (an [ActivityPub actor](https://www.w3.org/TR/activitypub/#actor)) |
| Functional | true |

### `blocksOf`

|  |  |
| --- | --- |
| URI | `https://purl.archive.org/socialweb/blocked#blocksOf` |
| Notes | The value of the `blocksOf` property of a collection is the actor for whom the collection is the value of its `blocks` property. It is the inverse property of `blocks`. As with other ActivityPub properties, the `blocksOf` property MAY be referenced in the actor by `id` or as an [embedded node object](https://www.w3.org/TR/json-ld11/#embedding). |
| Domain | [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) |
| Range | Object (an [ActivityPub actor](https://www.w3.org/TR/activitypub/#actor)) |
| Functional | true |

## Examples

### `blocked` property

A publisher can include the `blocked` collection in the properties of an actor.

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://purl.archive.org/socialweb/blocked"
    ],
    "id": "https://example.com/evanp",
    "type": "Person",
    "name": "Evan Prodromou",
    "inbox": "https://example.com/evanp/inbox",
    "outbox": "https://example.com/evanp/outbox",
    "following": "https://example.com/evanp/following",
    "followers": "https://example.com/evanp/followers",
    "liked": "https://example.com/evanp/liked",
    "blocked": "https://example.com/evanp/blocked",
    "to": "as:Public"
}
```

### A `blocked` collection

Retrieving the `blocked` collection would provide an ordered collection of ActivityPub actors that have been blocked.

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://purl.archive.org/socialweb/blocked",
        {"custom": "https://example.com/ns/custom"}
    ],
    "id": "https://example.com/evanp/blocked",
    "type": "OrderedCollection",
    "attributedTo": "https://example.com/evanp",
    "blockedOf": "https://example.com/evanp",
    "name": "Evan Prodromou's Blocked Collection",
    "orderedItems": [
        {
            "type": "Person",
            "id": "https://spam.example/spammer",
            "name": "Irritating Spammer"
        },
        {
            "type": "Application",
            "id": "https://alarmclock.example/alarmclock",
            "name": "Badly-Behaved Alarm Clock App"
        }
    ]
}
```

### `blocks` property

Similarly, a publisher can include the `blocks` collection in the properties of an actor. Note that here, the `blocks` collection is referenced as an embedded node object, rather than a URL. It includes useful metadata about the collection.

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://purl.archive.org/socialweb/blocked"
    ],
    "id": "https://example.com/evanp",
    "type": "Person",
    "name": "Evan Prodromou",
    "inbox": "https://example.com/evanp/inbox",
    "outbox": "https://example.com/evanp/outbox",
    "following": "https://example.com/evanp/following",
    "followers": "https://example.com/evanp/followers",
    "liked": "https://example.com/evanp/liked",
    "blocks": {
        "id": "https://example.com/evanp/blocks",
        "type": "OrderedCollection",
        "totalItems": 2,
    },
    "to": "as:Public"
}
```

### A `blocks` collection

Retrieving the `blocks` property value would provide an ordered collection of `Block` activities that the user has performed and not undone.

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://purl.archive.org/socialweb/blocked",
        {"custom": "https://example.com/ns/custom"}
    ],
    "id": "https://example.com/evanp/blocks",
    "type": "OrderedCollection",
    "attributedTo": "https://example.com/evanp",
    "blocksOf": "https://example.com/evanp",
    "name": "Evan Prodromou's Blocks Collection",
    "orderedItems": [
        {
            "type": "Block",
            "id": "https://example.com/evanp/block/2",
            "object": {
                "type": "Person",
                "id": "https://spam.example/spammer",
                "name": "Irritating Spammer"
            },
            "published": "2023-04-15T00:00:00Z"
        },
        {
            "type": ["custom:Disallow", "Block"],
            "id": "https://example.com/evanp/block/2",
            "object": {
                "type": "Application",
                "id": "https://alarmclock.example/alarmclock",
                "name": "Badly-Behaved Alarm Clock App"
            },
            "published": "2022-12-25T00:00:00Z"
        }
    ]
}
```

## Processing requirements

When a server receives a `Block` activity from a client through the ActivityPub API, it SHOULD add the activity to the `blocks` collection of the actor that performed the block. The server MAY also add the blocked actor to the `blocked` collection of the blocking actor.

When a server receives an `Undo` activity for a `Block` activity through the ActivityPub API, it SHOULD remove the `Block` activity from the `blocks` collection of the actor that undid the block. The server MAY also remove the blocked actor from the `blocked` collection of the blocking actor.

## Security considerations

The `blocked` and `blocks` collections are very sensitive. Actors on the blocked list may be harassing or abusive. If they find themselves on a user's blocklist, they may retaliate against the user. Consequently, the `blocked` and `blocks` collections SHOULD NOT be publicly readable.

By default, implementations SHOULD NOT allow read access to the `blocked` or `blocks` collections to any actor other than the user that owns the collection.

Some users may want to share their blocklist with other actors. Shared blocklists are an important tool for user safety on monolithic social networks and on the social web. Implementations MAY allow a user to share their `blocked` collection with other actors. Implementations SHOULD inform the user of the risks of sharing their blocklist with the wrong actors.

Sharing the `blocks` collection is less useful, since `Block` activities are usually not readable by anyone but the blocking actor.

## Implementations

The [onepage.pub] server implements the `blocked` collection.

## History

[activitypub-express][activitypub-express] implements
a `blocked` property in the `streams` collection of an actor, including the blocked objects only. The developers' experience was that storing objects only made it hard to `Undo` a block, since the full Activity object's `id` is needed. Metadata about the block activity, such as the date, is also lost.

## References

- James Snell, Evan Prodromou, [Activity Streams 2.0 Vocabulary][Vocab], 2017
- Christine Lemmer Webber, Jessica Tallon, Erin Shephard, Amy Guy, Evan Prodromou, [ActivityPub][ActivityPub], 2018
- Tom Preston-Werner, [Semantic Versioning 2.0.0][semver], 2017

[ActivityPub]: https://www.w3.org/TR/activitypub/
[onepage.pub]: https://github.com/evanp/onepage.pub/
[activitypub-express]: https://github.com/immers-space/activitypub-express
[Vocab]: https://www.w3.org/TR/activitystreams-vocabulary/
[semver]: https://semver.org/spec/v2.0.0.html

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
