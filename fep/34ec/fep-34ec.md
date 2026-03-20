---
slug: "34ec"
authors: Fred Hauschel <@naturzukunft2026@mastodon.social>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-34ec-notification-collection-endpoint/8568
dateReceived: 2026-03-15
trackingIssue: https://codeberg.org/fediverse/fep/issues/782
categories: ["Collections & Filtering", "Social Features"]
protocols: ["C2S"]
---
# FEP-34ec: Notification Collection Endpoint

## Summary

This FEP defines a standardized notification collection for ActivityPub actors. A new `notifications` property under `endpoints` ([ActivityPub] §5.7) provides an `OrderedCollection` containing references to activities that the server deems notification-worthy. Unlike the inbox, which serves as the delivery channel for all incoming activities, the notification collection is a curated subset — engagement-oriented events such as likes, mentions, and boosts. Dismissal of notifications uses the standard `Remove` activity ([ActivityPub] §7.5). Batch dismissal is supported via [FEP-db70] (`RemoveAll`) with optional [FEP-34c1] filtering.

## Motivation

ActivityPub defines an inbox as the primary collection for incoming activities. However, clients need to distinguish between content-oriented activities (home feed) and engagement-oriented events (notifications) — a separation that [SWICG #21] has long called for.

Today, every Fediverse software (Mastodon, Pleroma, GoToSocial, Misskey) implements notifications as a proprietary REST API without interoperability. There is no standardized ActivityPub endpoint for notifications.

This FEP closes this gap by defining:
- A standardized endpoint under `endpoints.notifications`
- A server-curated `OrderedCollection` of notification-worthy activities
- Dismissal via standard `Remove` ([ActivityPub] §7.5), batch dismissal via [FEP-db70]
- Optional filtering via [FEP-34c1]

No new types or vocabulary beyond the `notifications` endpoint property are introduced. The collection holds references to existing activities — the activity types themselves provide categorization.

## Specification

### 1. Notification Endpoint on the Actor

A conforming server MUST provide the `notifications` property under `endpoints` in the actor object:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "Person",
  "id": "https://example.com/actors/bob",
  "endpoints": {
    "sharedInbox": "https://example.com/inbox",
    "notifications": "https://example.com/actors/bob/notifications"
  }
}
```

The `notifications` property points to an `OrderedCollection` sorted by server receive time in descending order (newest first).

### 2. Collection Contents

The notification collection contains references to activities that the server considers notification-worthy for the actor. These are typically engagement-oriented events:

| Activity Type | Typical Condition |
|---------------|-------------------|
| `Like` | Object is owned by the actor |
| `Announce` | Object is owned by the actor |
| `Create` | Actor is mentioned (to/cc/tag) |
| `Follow` | Actor is the follow target |
| `Update` | Object is owned by or observed by the actor |

This table is non-normative. Servers MAY include any activity type and SHOULD apply their own criteria for what constitutes a notification.

The activities referenced in the notification collection also remain in the actor's inbox. The notification collection is a view, not a separate delivery mechanism.

### 3. Collection Semantics

- **Presence in the collection = pending notification** — there is no separate read/unread flag
- **Removal from the collection = dismissed** — the activity itself is not deleted, only the reference in the notification collection is removed
- The server MUST add activities to the notification collection when relevant activities arrive in the inbox

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "OrderedCollection",
  "id": "https://example.com/actors/bob/notifications",
  "totalItems": 3,
  "orderedItems": [
    "https://alice.example/activities/like-123",
    "https://carol.example/activities/create-456",
    "https://dave.example/activities/announce-789"
  ]
}
```

Servers MAY inline the full activity objects instead of providing only IRIs. When inlining, the standard Activity Streams representation is used — no wrapper type is needed:

```json
{
  "type": "OrderedCollection",
  "id": "https://example.com/actors/bob/notifications",
  "totalItems": 2,
  "orderedItems": [
    {
      "type": "Like",
      "id": "https://alice.example/activities/like-123",
      "actor": "https://alice.example/actors/alice",
      "object": "https://example.com/posts/post-1",
      "published": "2026-02-24T10:00:00Z"
    },
    {
      "type": "Create",
      "id": "https://carol.example/activities/create-456",
      "actor": "https://carol.example/actors/carol",
      "object": {
        "type": "Note",
        "content": "Hey @bob, check this out!"
      },
      "published": "2026-02-24T09:30:00Z"
    }
  ]
}
```

### 4. Pagination

The collection SHOULD support `OrderedCollectionPage` pagination. Since the collection only contains pending notifications, it typically remains small. Pagination becomes relevant only with larger volumes.

```json
{
  "type": "OrderedCollection",
  "id": "https://example.com/actors/bob/notifications",
  "totalItems": 150,
  "first": "https://example.com/actors/bob/notifications?page=1"
}
```

### 5. C2S Operations

#### 5.1 Dismiss a Single Notification (Remove)

A client dismisses a notification by posting a `Remove` activity to the actor's outbox, as defined in [ActivityPub] §6.11:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Remove",
  "actor": "https://example.com/actors/bob",
  "object": "https://alice.example/activities/like-123",
  "target": "https://example.com/actors/bob/notifications"
}
```

The server MUST remove the activity reference from the notification collection. The activity itself MUST NOT be deleted from the inbox.

#### 5.2 Batch Dismiss (RemoveAll)

Batch dismissal is supported via [FEP-db70] (`RemoveAll`). An optional [FEP-34c1] filter can be provided to dismiss only matching notifications.

**Dismiss all notifications ("mark all as read"):**

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/db70"
  ],
  "type": "RemoveAll",
  "actor": "https://example.com/actors/bob",
  "target": "https://example.com/actors/bob/notifications"
}
```

**Dismiss all notifications of a specific type (with FEP-34c1 filter):**

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/db70",
    "https://w3id.org/fep/34c1",
    "https://w3id.org/tree"
  ],
  "type": "RemoveAll",
  "actor": "https://example.com/actors/bob",
  "target": "https://example.com/actors/bob/notifications",
  "filter": {
    "type": "FilterRequest",
    "relation": [
      {
        "type": "EqualToRelation",
        "path": { "@id": "as:type" },
        "value": { "@id": "as:Like" }
      }
    ]
  }
}
```

**Dismiss all notifications older than a given date:**

```json
{
  "type": "RemoveAll",
  "actor": "https://example.com/actors/bob",
  "target": "https://example.com/actors/bob/notifications",
  "filter": {
    "type": "FilterRequest",
    "relation": [
      {
        "type": "LessThanRelation",
        "path": { "@id": "as:published" },
        "value": { "@value": "2026-02-17T00:00:00Z", "@type": "xsd:dateTime" }
      }
    ]
  }
}
```

The server MUST remove all activity references matching the filter from the notification collection. Without a filter, the server MUST remove all activity references.

### 6. Collection Filtering (Read)

Conforming servers SHOULD support [FEP-34c1] filtering for the notification collection. The activity `type` SHOULD be accepted as a `tree:path` for filtering.

The server signals filter support via `tree:search` in the collection:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec",
    "https://w3id.org/fep/34c1",
    "https://w3id.org/tree"
  ],
  "type": "OrderedCollection",
  "id": "https://example.com/actors/bob/notifications",
  "totalItems": 25,
  "tree:search": {
    "type": "FilterEndpoint",
    "template": "https://example.com/actors/bob/notifications/filter"
  }
}
```

A client retrieving only Like notifications sends a POST to the filter endpoint:

**Request:** `POST https://example.com/actors/bob/notifications/filter`

```json
{
  "@context": [
    "https://w3id.org/fep/34c1",
    "https://w3id.org/tree"
  ],
  "type": "FilterRequest",
  "relation": [
    {
      "type": "EqualToRelation",
      "path": { "@id": "as:type" },
      "value": { "@id": "as:Like" }
    }
  ],
  "pageSize": 20
}
```

**Response:**

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "OrderedCollectionPage",
  "partOf": "https://example.com/actors/bob/notifications",
  "totalItems": 5,
  "orderedItems": [
    {
      "type": "Like",
      "id": "https://alice.example/activities/like-123",
      "actor": "https://alice.example/actors/alice",
      "object": "https://example.com/posts/post-1",
      "published": "2026-02-24T10:00:00Z"
    }
  ]
}
```

### 7. Authorization

The notification collection MUST only be accessible to the authenticated actor. Unauthenticated requests MUST be rejected with `401 Unauthorized`.

## Security Considerations

- The notification collection contains potentially sensitive information (who interacts with whom). Access MUST be strictly limited to the owner.
- Servers SHOULD implement rate limiting for C2S operations, especially for `RemoveAll`.

## Conformance

A conforming server MUST:
- Provide `notifications` under `endpoints` in the actor object
- Populate the notification collection with references to notification-worthy activities
- Process `Remove` activities targeting the notification collection by removing the reference
- NOT delete the underlying activity from the inbox when removing from the notification collection

A conforming server SHOULD:
- Support `OrderedCollectionPage` pagination for larger volumes
- Support [FEP-34c1] filtering for the notification collection
- Accept activity `type` as a `tree:path` in filters
- Support [FEP-db70] `RemoveAll` for batch dismissal

## Implementations

- [ChangingGraph](https://changinggraph.org) (reference implementation, in progress)

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Streams 2.0], 2017
- James M Snell, Evan Prodromou, [Activity Streams 2.0 Vocabulary][AS2-Vocab], 2017
- naturzukunft, [FEP-34c1: Collection Filtering using TREE Hypermedia], 2025
- naturzukunft, [FEP-db70: RemoveAll Collection Activity], 2026
- [SWICG #21: Separation of home feed vs. notifications][SWICG #21]
- Sarven Capadisli, Amy Guy, [Linked Data Notifications], 2017
- [TREE Hypermedia Vocabulary][TREE]

[ActivityPub]: https://www.w3.org/TR/activitypub/
[Activity Streams 2.0]: https://www.w3.org/TR/activitystreams-core/
[AS2-Vocab]: https://www.w3.org/TR/activitystreams-vocabulary/#activity-types
[FEP-34c1]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md
[FEP-34ec]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34ec/fep-34ec.md
[FEP-db70]: https://codeberg.org/fediverse/fep/src/branch/main/fep/db70/fep-db70.md
[SWICG #21]: https://github.com/swicg/activitypub-api/issues/21
[Linked Data Notifications]: https://www.w3.org/TR/ldn/
[TREE]: https://treecg.github.io/specification/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
