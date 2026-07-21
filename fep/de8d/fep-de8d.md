---
slug: "de8d"
authors: Reese Armstrong <me@reeseric.ci>
status: DRAFT
dateReceived: 2026-07-19
discussionsTo: https://socialhub.activitypub.rocks/t/fep-de8d-emoji-catalogs/8825
---

# FEP-de8d: Emoji Catalogs

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119].

## Summary

Emoji Catalogs provide a way for both clients and servers to publish and discover custom emoji.

## Motivation

[ActivityPub] implementations, including Mastodon, commonly support custom emoji. [FEP-9098] defines how an `Emoji` is embedded in an [Activity Streams] object, but it does not define how a client discovers the emoji available for use when composing new content.

This leads to [ActivityPub] clients relying on implementation-specific APIs such as the Mastodon custom emoji endpoint.

A standardized emoji catalog allows a C2S client to:

- Populate an emoji picker.
- Determine which emoji the authenticated actor may use.
- Retrieve emoji categories and static previews.
- Update its local cache when the catalog changes.

Additionally, a standardized emoji catalog allows servers to publish custom emoji that other ActivityPub implementations can discover reliably.

## Vocabulary

### `emojiCatalog`

- URI: `https://w3id.org/fep/de8d#emojiCatalog`
- Domain: [ActivityPub] actor `endpoints`
- Range: IRI

The `emojiCatalog` property identifies an [Activity Streams] collection containing the custom emoji catalog for an actor.

### `emojiCategory`

- URI: `https://w3id.org/fep/de8d#emojiCategory`
- Domain: `Emoji`
- Range: string

The optional `emojiCategory` property identifies the user-facing category in which a client may display an emoji.

## Discovery

An [ActivityPub] actor MAY advertise an emoji catalog using the `emojiCatalog` property under its `endpoints` property.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/de8d"],
  "id": "https://social.example.com/users/alice",
  "type": "Person",
  "inbox": "https://social.example.com/users/alice/inbox",
  "outbox": "https://social.example.com/users/alice/outbox",
  "endpoints": {
    "emojiCatalog": "https://social.example.com/users/alice/emojis"
  }
}
```

The value MUST be an IRI which identifies an [Activity Streams] `Collection`.

C2S clients MUST prefer the catalog advertised by the authenticated actor over a catalog advertised by a server-level actor.

### Server-Level Catalogs

An `Application` or `Service` actor MAY advertise an `emojiCatalog` containing emoji that the publisher makes publicly available for discovery and reference in newly created content.

Receiving implementations MAY apply their own policies when deciding whether actors may use emoji discovered through a server-level catalog.

Consumers SHOULD cache emoji objects and media in accordance with HTTP
caching semantics and any applicable usage rights.

## Catalog

The emoji catalog MUST be represented as an [Activity Streams]
`Collection`, which contains [FEP-9098] `Emoji` objects.

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/9098",
    "https://w3id.org/fep/de8d"
  ],
  "id": "https://social.example.com/users/alice/emojis",
  "type": "Collection",
  "attributedTo": "https://social.example.com/server",
  "updated": "2026-07-18T16:00:00Z",
  "totalItems": 2,
  "items": [
    {
      "id": "https://social.example.com/emojis/blobcat",
      "type": "Emoji",
      "name": ":blobcat:",
      "emojiCategory": "Animals",
      "icon": {
        "type": "Image",
        "mediaType": "image/png",
        "url": "https://social.example.com/media/blobcat.png"
      }
    },
    {
      "id": "https://social.example.com/emojis/party-parrot",
      "type": "Emoji",
      "name": ":party_parrot:",
      "emojiCategory": "Party",
      "icon": {
        "type": "Image",
        "mediaType": "image/gif",
        "url": "https://social.example.com/media/party-parrot.gif"
      },
      "preview": {
        "type": "Image",
        "mediaType": "image/png",
        "url": "https://social.example.com/media/party-parrot-static.png"
      }
    }
  ]
}
```

### Membership

An actor-specific catalog MUST exclusively contain emoji that the actor
is permitted to use in newly created content.

A server-level catalog MUST exclusively contain emoji that the
publisher makes publicly available for discovery and reference in newly
created content.

Receiving implementations MAY apply additional policies when deciding
whether their actors may use emoji from a server-level catalog.

Absence from a catalog does not imply that an emoji is invalid or must
not be rendered.

In particular, clients MUST continue to render an FEP-9098 `Emoji`
embedded in existing or incoming content even when that emoji is absent
from the authenticated actor's catalog.

Catalogs MAY include emoji whose object IDs have a different origin from
the catalog.

### Updates

Adding an emoji to an actor-specific catalog means that the emoji is
available for use by that actor in newly created content.

Removing an emoji from an actor-specific catalog means that the emoji
is no longer available for use by that actor in newly created content.

Adding an emoji to a server-level catalog means that the publisher
makes the emoji publicly available for discovery and reference in newly
created content.

Removing an emoji from a server-level catalog means that the publisher no longer makes the emoji publicly available for discovery and reference in newly created content.

Removing an emoji from a catalog MUST NOT invalidate existing content
containing that emoji.

### Filtering

_This section is non-normative._

In keeping with [FEP-34c1], a catalog may advertise a filtering endpoint, which may support the following properties as filtering targets:

- `https://www.w3.org/ns/activitystreams#name`
- `https://www.w3.org/ns/activitystreams#updated`
- `https://w3id.org/fep/de8d#emojiCategory`

## Items

### Names

Emoji included in a catalog MUST have a `name`, which MUST be unique within a catalog.

Name uniqueness MUST be determined using exact string comparison.

A client encountering duplicate names MAY retain one item and ignore
other items with the same name.

### Categories

An emoji MAY have an `emojiCategory` label. Category labels do not have global semantic meaning.

Clients MAY use `emojiCategory` to group emoji for presentation.

Clients MUST NOT discard emoji that do not have an `emojiCategory`.

### Static Previews

An emoji MAY use the [Activity Streams] `preview` property to identify a non-animated representation of its `icon`.

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- silverpill, [FEP-9098: Custom emojis](https://codeberg.org/fediverse/fep/src/branch/main/fep/9098/fep-9098.md), 2025
- James Snell, Evan Prodromou, [Activity Streams 2.0](https://www.w3.org/TR/activitystreams-core/), 2017
- Fred Hauschel, [FEP-34c1: Collection Filtering using TREE Hypermedia Vocabulary](https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md), 2026
- Scott Bradner, [Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119), 1997

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RFC 2119]: https://datatracker.ietf.org/doc/html/rfc2119
[FEP-9098]: https://codeberg.org/fediverse/fep/src/branch/main/fep/9098/fep-9098.md
[Activity Streams]: https://www.w3.org/TR/activitystreams-core/
[FEP-34c1]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
