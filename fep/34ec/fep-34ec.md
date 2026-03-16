---
slug: "34ec"
authors: Fred Hauschel <@naturzukunft2026@mastodon.social>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-34ec-notification-collection-endpoint/8568
dateReceived: 2026-03-15
trackingIssue: https://codeberg.org/fediverse/fep/issues/782
---
# FEP-34ec: Notification Collection Endpoint

## Summary

This FEP defines a standardized notification collection for ActivityPub actors. A new `notifications` property under `endpoints` ([ActivityPub] §5.7) provides an `OrderedCollection` containing `Notification` objects that inform the actor about relevant activities. Unlike the inbox, which receives raw activities, the notification collection holds server-generated notification objects. Notifications only exist within the collection — read notifications are removed. Batch removal is supported via [FEP-db70] (`RemoveAll`) with optional [FEP-34c1] filtering.

## Motivation

ActivityPub defines an inbox as the primary collection for incoming activities. However, clients need to distinguish between content-oriented activities (home feed) and engagement-oriented events (notifications) — a separation that [SWICG #21] has long called for.

Today, every Fediverse software (Mastodon, Pleroma, GoToSocial, Misskey) implements notifications as a proprietary REST API without interoperability. There is no standardized ActivityPub endpoint for notifications and no vocabulary for notification objects.

This FEP closes this gap by defining:
- A standardized endpoint under `endpoints.notifications`
- A new type `Notification` as a notification *about* an activity
- C2S operations for managing notifications (Remove, Add, [FEP-db70] RemoveAll)
- Integration with [FEP-34c1] for filtering and filtered batch operations

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

The `notifications` property points to an `OrderedCollection` sorted by `published` in descending order (newest first).

### 2. The `Notification` Type

A notification is a distinct object that informs the actor about an activity. It is **not** the activity itself — a `Like` is an activity, the notification about it is a notification.

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "Notification",
  "object": "https://alice.example/activities/like-123",
  "actor": "https://alice.example/actors/alice",
  "notificationType": "as:Like",
  "published": "2026-02-24T10:00:00Z"
}
```

#### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | String | MUST | `Notification` |
| `object` | IRI or Object | MUST | The activity being notified about |
| `actor` | IRI | MUST | The actor who triggered the activity |
| `notificationType` | IRI | MUST | An [Activity Streams 2.0 Activity Type][AS2-Vocab]. The value MUST be a subclass of `as:Activity`. |
| `published` | xsd:dateTime | MUST | Timestamp of the notification |

The `notificationType` property is defined with `@type: @id` in the [JSON-LD context](fep-34ec.jsonld), so string values like `"as:Like"` are automatically resolved to IRIs.

#### Notification Types

The value of `notificationType` MUST be an [Activity Streams 2.0 Activity Type][AS2-Vocab]. The following types are recommended as core vocabulary (SHOULD). Since `notificationType` can reference any AS2 Activity Type, the vocabulary is inherently extensible.

| notificationType | Triggering Activity | Description |
|------------------|---------------------|-------------|
| `as:Create` | `Create` addressed to the actor | New content (Note, Article, etc.) |
| `as:Like` | `Like` on an object owned by the actor | Like |
| `as:Announce` | `Announce` of an object owned by the actor | Boost/reshare |
| `as:Update` | `Update` of an object the actor is observing | Update |

### 3. Collection Semantics

The notification collection contains exclusively unread notifications:

- **Presence in the collection = unread** — there is no separate read/unread flag
- **Removal from the collection = read/dismissed** — the notification is deleted
- Notifications only exist within the collection — after removal, the object does not persist
- The server MUST create notifications when relevant activities arrive in the inbox

### 4. Pagination

The collection SHOULD support `OrderedCollectionPage` pagination. Since the collection only contains unread notifications, it typically remains small. Pagination becomes relevant only with larger volumes.

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
    {
      "type": "Notification",
      "object": "https://alice.example/activities/like-123",
      "actor": "https://alice.example/actors/alice",
      "notificationType": "as:Like",
      "published": "2026-02-24T10:00:00Z"
    },
    {
      "type": "Notification",
      "object": "https://carol.example/activities/create-456",
      "actor": "https://carol.example/actors/carol",
      "notificationType": "as:Create",
      "published": "2026-02-24T09:30:00Z"
    },
    {
      "type": "Notification",
      "object": "https://dave.example/activities/announce-789",
      "actor": "https://dave.example/actors/dave",
      "notificationType": "as:Announce",
      "published": "2026-02-24T09:00:00Z"
    }
  ]
}
```

For larger volumes, the server SHOULD switch to pagination:

```json
{
  "type": "OrderedCollection",
  "id": "https://example.com/actors/bob/notifications",
  "totalItems": 150,
  "first": "https://example.com/actors/bob/notifications?page=1"
}
```

### 5. C2S Operations

#### 5.1 Remove a Single Notification (Remove)

A client removes a single notification using the AS2 `Remove` activity:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "Remove",
  "actor": "https://example.com/actors/bob",
  "object": {
    "type": "Notification",
    "object": "https://alice.example/activities/like-123"
  },
  "target": "https://example.com/actors/bob/notifications"
}
```

The server MUST remove the notification from the collection and delete the notification object.

#### 5.2 Mark as Unread (Add)

A client can mark a previously removed notification as unread by adding a new notification to the collection:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "Add",
  "actor": "https://example.com/actors/bob",
  "object": {
    "type": "Notification",
    "object": "https://alice.example/activities/like-123",
    "actor": "https://alice.example/actors/alice",
    "notificationType": "as:Like"
  },
  "target": "https://example.com/actors/bob/notifications"
}
```

The server creates a new notification and adds it to the collection. Since the original notification was deleted upon removal, this is a new object — not a restoration.

#### 5.3 Batch Remove (RemoveAll)

Batch removal of notifications is supported via [FEP-db70] (`RemoveAll`). An optional [FEP-34c1] filter can be provided to remove only matching notifications.

**Remove all notifications ("mark all as read"):**

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

**Remove all notifications of a specific type (with FEP-34c1 filter):**

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/db70",
    "https://w3id.org/fep/34ec",
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
        "path": { "@id": "notificationType" },
        "value": "as:Create"
      }
    ]
  }
}
```

**Remove all notifications older than a given date:**

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

The server MUST remove and delete all notifications matching the filter. Without a filter, the server MUST remove all notifications.

### 6. Collection Filtering (Read)

Conforming servers SHOULD support [FEP-34c1] filtering for the notification collection. Servers MUST accept `notificationType` as an additional allowed `tree:path`.

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

A client that wants to retrieve only Create notifications sends a POST to the filter endpoint:

**Request:** `POST https://example.com/actors/bob/notifications/filter`

```json
{
  "@context": [
    "https://w3id.org/fep/34ec",
    "https://w3id.org/fep/34c1",
    "https://w3id.org/tree"
  ],
  "type": "FilterRequest",
  "relation": [
    {
      "type": "EqualToRelation",
      "path": { "@id": "notificationType" },
      "value": "as:Create"
    }
  ],
  "pageSize": 20
}
```

**Response:**

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/34ec"
  ],
  "type": "OrderedCollectionPage",
  "partOf": "https://example.com/actors/bob/notifications",
  "totalItems": 5,
  "orderedItems": [
    {
      "type": "Notification",
      "object": "https://carol.example/activities/create-456",
      "actor": "https://carol.example/actors/carol",
      "notificationType": "as:Create",
      "published": "2026-02-24T09:30:00Z"
    }
  ]
}
```

### 7. Server Behavior

#### 7.1 Notification Generation

When the server receives an activity in the actor's inbox, it MUST check whether the activity triggers a notification:

| Incoming Activity | Condition | notificationType |
|-------------------|-----------|-----------------|
| `Create` | Addressed to the actor (to/cc) | `as:Create` |
| `Like` | Object is owned by the actor | `as:Like` |
| `Announce` | Object is owned by the actor | `as:Announce` |
| `Update` | Object is being observed by the actor | `as:Update` |

Servers MAY generate notifications for additional activity types.

#### 7.2 Authorization

The notification collection MUST only be accessible to the authenticated actor. Unauthenticated requests MUST be rejected with `401 Unauthorized`.

## Security Considerations

- The notification collection contains potentially sensitive information (who interacts with whom). Access MUST be strictly limited to the owner.
- Servers SHOULD implement rate limiting for C2S operations, especially for `Add` and `RemoveAll`.

## Conformance

A conforming server MUST:
- Provide `notifications` under `endpoints` in the actor object
- Generate `Notification` objects in the collection
- Process `Remove` activities targeting the notification collection
- Delete removed notifications (not retain them)

A conforming server SHOULD:
- Support `OrderedCollectionPage` pagination for larger volumes
- Support [FEP-34c1] filtering for the notification collection
- Accept `notificationType` as a `tree:path` in filters
- Support `Add` activities for "mark as unread"
- Support [FEP-db70] `RemoveAll` for batch removal

## Implementations

- [ChangingGraph](https://changinggraph.org) (reference implementation, in progress)

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Streams 2.0], 2017
- James M Snell, Evan Prodromou, [Activity Streams 2.0 Vocabulary][AS2-Vocab], 2017
- naturzukunft, [FEP-34c1: Collection Filtering using TREE Hypermedia], 2025
- naturzukunft, [FEP-db70: RemoveAll Collection Activity], 2026
- [SWICG #21: Separation of home feed vs. notifications][SWICG #21]
- [SWICG #60: Server-local metadata under endpoints][SWICG #60]
- Sarven Capadisli, Amy Guy, [Linked Data Notifications], 2017
- [TREE Hypermedia Vocabulary][TREE]

[ActivityPub]: https://www.w3.org/TR/activitypub/
[Activity Streams 2.0]: https://www.w3.org/TR/activitystreams-core/
[AS2-Vocab]: https://www.w3.org/TR/activitystreams-vocabulary/#activity-types
[FEP-34c1]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md
[FEP-34ec]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34ec/fep-34ec.md
[FEP-db70]: https://codeberg.org/fediverse/fep/src/branch/main/fep/db70/fep-db70.md
[SWICG #21]: https://github.com/swicg/activitypub-api/issues/21
[SWICG #60]: https://github.com/swicg/activitypub-api/issues/60
[Linked Data Notifications]: https://www.w3.org/TR/ldn/
[TREE]: https://treecg.github.io/specification/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
