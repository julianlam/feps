---
slug: "db70"
authors: Fred Hauschel <@naturzukunft2026@mastodon.social>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-db70-removeall-collection-activity/8569
dateReceived: 2026-03-15
trackingIssue: https://codeberg.org/fediverse/fep/issues/784
---
# FEP-db70: RemoveAll Collection Activity

## Summary

This FEP defines a `RemoveAll` activity for batch-removing items from an ActivityPub collection. While the [ActivityPub] specification defines `Remove` for removing a single item from a collection, there is no mechanism for removing multiple or all items at once. `RemoveAll` fills this gap. It supports an optional [FEP-34c1] filter to selectively remove items matching specific criteria (e.g. by type, by date, or by actor). Without a filter, all items are removed. `RemoveAll` is a generic collection operation — it can be used with any collection type, not just inboxes or notification collections.

## Motivation

ActivityPub's `Remove` activity targets a single `object` within a `target` collection. For collections that can grow large, clients need a way to batch-remove items without sending individual `Remove` activities for each item. Common use cases include:

- "Mark all as read" in a notification collection ([FEP-34ec])
- Clearing old items from a collection
- Removing all items matching a specific filter (e.g. all items of a certain type)

Without a batch operation, a client must first fetch all items, then send individual `Remove` activities — which is both slow and prone to race conditions.

## Specification

### 1. The `RemoveAll` Activity

`RemoveAll` is a new activity type that removes multiple items from a target collection.

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

#### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `type` | String | MUST | `RemoveAll` |
| `actor` | IRI | MUST | The actor performing the operation |
| `target` | IRI | MUST | The collection to remove items from |
| `filter` | FilterRequest | MAY | A [FEP-34c1] filter to select which items to remove |

Without a `filter`, the server MUST remove all items from the target collection.

### 2. Filtered RemoveAll (with FEP-34c1)

When a `filter` property is present, only items matching the filter are removed. The filter uses the [FEP-34c1] `FilterRequest` format with [TREE] relations.

**Remove all items matching a specific property value:**

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
  "target": "https://example.com/actors/bob/some-collection",
  "filter": {
    "type": "FilterRequest",
    "relation": [
      {
        "type": "EqualToRelation",
        "path": { "@id": "rdf:type" },
        "value": { "@id": "as:Create" }
      }
    ]
  }
}
```

**Remove all items older than a given date:**

```json
{
  "type": "RemoveAll",
  "actor": "https://example.com/actors/bob",
  "target": "https://example.com/actors/bob/some-collection",
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

**Combine multiple filter criteria (AND):**

```json
{
  "type": "RemoveAll",
  "actor": "https://example.com/actors/bob",
  "target": "https://example.com/actors/bob/some-collection",
  "filter": {
    "type": "FilterRequest",
    "relation": [
      {
        "type": "EqualToRelation",
        "path": { "@id": "rdf:type" },
        "value": { "@id": "as:Create" }
      },
      {
        "type": "LessThanRelation",
        "path": { "@id": "as:published" },
        "value": { "@value": "2026-02-17T00:00:00Z", "@type": "xsd:dateTime" }
      }
    ]
  }
}
```

Multiple `relation` entries are combined with AND — all criteria must match for an item to be removed.

### 3. Server Behavior

- The server MUST remove all matching items from the target collection
- The server MUST verify that the `actor` is authorized to modify the target collection
- If the target collection does not exist, the server MUST respond with `404 Not Found`
- Unauthorized requests MUST be rejected with `401 Unauthorized`
- Whether removed items are deleted or archived is determined by the collection's semantics (e.g. [FEP-34ec] specifies that removed notifications MUST be deleted)

### 4. Response

The server SHOULD respond with `200 OK` and the number of removed items:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Removed 12 items from the collection"
}
```

## Security Considerations

- `RemoveAll` without a filter removes all items from a collection. Servers SHOULD ensure that the actor is authorized for the target collection.
- Servers SHOULD implement rate limiting for `RemoveAll` operations.

## Conformance

A conforming server MUST:
- Process `RemoveAll` activities targeting a collection owned by the actor
- Remove all items when no `filter` is present
- Remove only matching items when a [FEP-34c1] `filter` is present

A conforming server SHOULD:
- Support [FEP-34c1] `FilterRequest` in the `filter` property

## Implementations

- [ChangingGraph](https://changinggraph.org) (reference implementation, in progress)

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Streams 2.0], 2017
- naturzukunft, [FEP-34c1: Collection Filtering using TREE Hypermedia], 2025
- naturzukunft, [FEP-34ec: Notification Collection Endpoint], 2026
- [TREE Hypermedia Vocabulary][TREE]

[ActivityPub]: https://www.w3.org/TR/activitypub/
[Activity Streams 2.0]: https://www.w3.org/TR/activitystreams-core/
[FEP-34c1]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md
[FEP-34ec]: https://codeberg.org/fediverse/fep/src/branch/main/fep/34ec/fep-34ec.md
[TREE]: https://treecg.github.io/specification/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
