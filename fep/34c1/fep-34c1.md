---
slug: "34c1"
authors: Fred Hauschel <@naturzukunft2026@mastodon.social>
status: DRAFT
dateReceived: 2026-02-19
discussionsTo: https://socialhub.activitypub.rocks/t/fep-34c1-collection-filtering-using-tree-hypermedia-vocabulary/8494
---

# FEP-34c1: Collection Filtering using TREE Hypermedia Vocabulary

## Summary

This FEP proposes using the [TREE Hypermedia Vocabulary][TREE] for client-initiated filter requests on ActivityPub Collections (especially Inbox). Clients can send a filter as a JSON-LD object via HTTP POST to retrieve a filtered subset of the collection.

This enables use cases such as:
- **Home Timeline**: Content lifecycle activities (`Create`, `Update`, `Delete`, `Announce`) from followed actors, visible to public or followers
- **Mentions**: Activities addressed to the actor via `as:to` or `as:cc`
- **Private Messages**: Activities not addressed to `as:Public` (DMs, followers-only, group messages)
- **Media Filter**: Only activities with images or videos

---

## Context

The context document for this ActivityPub extension is at `https://w3id.org/fep/34c1/context`. Its contents are as follows:

```json
{
  "@context": {
    "fep34c1": "https://w3id.org/fep/34c1#",
    "FilterRequest": "fep34c1:FilterRequest",
    "pageSize": {
      "@id": "fep34c1:pageSize",
      "@type": "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"
    }
  }
}
```

## Defined Terms

### `fep34c1:FilterRequest`

| | |
|---|---|
| URI | `https://w3id.org/fep/34c1#FilterRequest` |
| Notes | A container object for a filter query. It holds one or more `tree:relation` entries that define the filter criteria, and an optional `fep34c1:pageSize` to control pagination. |
| Domain | (none) |
| Range | (none) |

### `fep34c1:pageSize`

| | |
|---|---|
| URI | `https://w3id.org/fep/34c1#pageSize` |
| Notes | The maximum number of items per page in the filtered response. |
| Domain | `fep34c1:FilterRequest` |
| Range | `xsd:nonNegativeInteger` |
| Functional | Yes |

---

## Motivation

### Problem

ActivityPub defines Collections (Inbox, Outbox, Followers, etc.) but no mechanism for clients to request **filtered views**. Clients must:

1. Fetch all items with pagination
2. Filter and sort locally
3. Transfer unnecessarily large amounts of data

For a "Home Timeline" (activities from followees), this is particularly inefficient since the inbox also contains follow requests, likes, and other irrelevant activities.

### Existing Approaches

| Approach | Problem |
|----------|---------|
| **FEP-5bf0** | WITHDRAWN (June 2025); focused on server-side views, not client queries |
| **Hydra** | GET-oriented (URL templates), not for POST queries |
| **SPARQL** | Too complex for simple filters, security risks |
| **Proprietary** | Mastodon's `/api/v1/timelines/home` is not standardized |

### Why TREE?

The [TREE Hypermedia Vocabulary][TREE] offers:

- Established vocabulary (W3C Community Group, EU Government Adoption)
- Clear semantics for filter operations (`tree:path`, `tree:value`, `tree:Relation`)
- SPARQL-compatible comparison operators
- JSON-LD compatible
- Extensible for additional relation types

---

## Specification

### 1. Filter Endpoint

Servers MAY provide a filter endpoint for collections:

```
POST /ap/actors/{username}/inbox/filter
Content-Type: application/ld+json
```

The endpoint MUST be announced in the Collection object via the `tree:search` property:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/tree"
  ],
  "type": "OrderedCollection",
  "id": "https://example.com/ap/actors/alice/inbox",
  "tree:search": {
    "@type": "fep34c1:FilterEndpoint",
    "tree:template": "https://example.com/ap/actors/alice/inbox/filter"
  }
}
```

### 2. Filter Request Format

A filter request is a JSON-LD object of type `fep34c1:FilterRequest`:

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "rdf:type" },
      "tree:value": [
        { "@id": "as:Create" },
        { "@id": "as:Update" },
        { "@id": "as:Delete" },
        { "@id": "as:Announce" }
      ]
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "as:actor" },
      "tree:value": { "@id": "as:following" }
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": [{ "@id": "as:to" }, { "@id": "as:cc" }],
      "tree:value": [
        { "@id": "https://www.w3.org/ns/activitystreams#Public" },
        { "@id": "as:followers" }
      ]
    }
  ],
  "fep34c1:pageSize": 20
}
```

### 3. Relation Types

#### 3.1 MUST be Supported (Core)

| Relation | Semantics | SPARQL Equivalent |
|----------|-----------|-------------------|
| `tree:EqualToRelation` | Value is equal to | `?x = ?value` |
| `tree:NotEqualToRelation` | Value is not equal to | `?x != ?value` |
| `tree:GreaterThanRelation` | Value is greater than | `?x > ?value` |
| `tree:LessThanRelation` | Value is less than | `?x < ?value` |
| `tree:GreaterThanOrEqualToRelation` | Value is greater than or equal to | `?x >= ?value` |
| `tree:LessThanOrEqualToRelation` | Value is less than or equal to | `?x <= ?value` |

#### 3.2 SHOULD be Supported (Recommended)

| Relation | Semantics | SPARQL Equivalent |
|----------|-----------|-------------------|
| `tree:PrefixRelation` | Value starts with | `STRSTARTS(?x, ?value)` |
| `tree:SubstringRelation` | Value contains | `CONTAINS(?x, ?value)` |
| `tree:SuffixRelation` | Value ends with | `STRENDS(?x, ?value)` |

### 4. Special Values

#### 4.1 `as:following` - Dynamic Followee List

The value `as:following` is a special placeholder that the server MUST resolve at query time. When used as `tree:value`, the server replaces it with the set of actor IRIs from the `following` collection of the **authenticated (requesting) actor**.

This means a relation like:

```json
{
  "@type": "tree:EqualToRelation",
  "tree:path": { "@id": "as:actor" },
  "tree:value": { "@id": "as:following" }
}
```

is equivalent to: "Return only activities where the `as:actor` property matches one of the actor IRIs in the requesting actor's `following` collection." In other words, only activities authored by actors that the requesting user follows will be included in the result.

#### 4.2 `as:followers` - Dynamic Followers Collection IRI

The value `as:followers` is a special placeholder that the server MUST resolve at query time. When used as `tree:value`, the server replaces it with the IRI of the `followers` collection of the **authenticated (requesting) actor**.

This is useful for audience filtering: Fediverse servers typically address followers-only posts with the actor's followers collection IRI in `as:to` or `as:cc`.

#### 4.3 Multiple Values (OR Conjunction)

If `tree:value` is an array, the values are combined with OR:

```json
{
  "tree:value": [
    { "@id": "as:Create" },
    { "@id": "as:Update" },
    { "@id": "as:Delete" },
    { "@id": "as:Announce" }
  ]
}
```

**Semantics:** `rdf:type = as:Create OR rdf:type = as:Update OR rdf:type = as:Delete OR rdf:type = as:Announce`

### 5. Multiple Paths (UNION)

If `tree:path` is an array, the filter matches if **any** of the specified paths contains a matching value. This is equivalent to a UNION in SPARQL.

```json
{
  "@type": "tree:EqualToRelation",
  "tree:path": [{ "@id": "as:to" }, { "@id": "as:cc" }],
  "tree:value": { "@id": "https://example.com/ap/actors/alice" }
}
```

**Semantics:** "Match if the value appears in `as:to` OR in `as:cc`."

This is particularly useful for audience filtering, since ActivityPub activities use both `as:to` and `as:cc` for addressing.

### 6. Combination of Relations (AND Conjunction)

Multiple `tree:relation` entries are combined with AND:

```json
{
  "tree:relation": [
    { "@type": "tree:EqualToRelation", "tree:path": {"@id": "rdf:type"}, "tree:value": {"@id": "as:Create"} },
    { "@type": "tree:EqualToRelation", "tree:path": {"@id": "as:actor"}, "tree:value": {"@id": "as:following"} },
    { "@type": "tree:EqualToRelation", "tree:path": [{"@id": "as:to"}, {"@id": "as:cc"}], "tree:value": {"@id": "https://www.w3.org/ns/activitystreams#Public"} }
  ]
}
```

**Semantics:** `rdf:type = as:Create AND as:actor IN following AND (as:to = as:Public OR as:cc = as:Public)`

### 7. Response Format

The response is an `OrderedCollectionPage` with the filtered items:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/tree",
    { "fep34c1": "https://w3id.org/fep/34c1#" }
  ],
  "@type": "OrderedCollectionPage",
  "partOf": "https://example.com/ap/actors/alice/inbox",
  "orderedItems": [
    { /* Activity 1 */ },
    { /* Activity 2 */ }
  ],
  "tree:relation": [
    {
      "@type": "tree:GreaterThanRelation",
      "tree:path": { "@id": "as:published" },
      "tree:value": "2026-01-28T10:00:00Z",
      "tree:node": "https://example.com/ap/actors/alice/inbox/filter?cursor=abc123"
    }
  ],
  "totalItems": 42
}
```

### 8. Pagination

Cursor-based pagination is signaled via `tree:relation` in the response. Each pagination relation uses three properties from the TREE vocabulary:

- `tree:value` — the boundary value (e.g., a timestamp) that delimits the current page
- `tree:node` — the URL to fetch to retrieve the **next page** of results beyond that boundary
- `tree:path` — the property used for ordering (typically `as:published`)

For example, a `tree:GreaterThanRelation` with `tree:value` of `"2026-01-28T10:00:00Z"` and a `tree:node` URL means: "Fetching `tree:node` will return items with `as:published` greater than `2026-01-28T10:00:00Z`."

Pagination directions:

- `tree:GreaterThanRelation` on `as:published` → next page contains **older** items (published after the boundary, in reverse chronological order)
- `tree:LessThanRelation` on `as:published` → next page contains **newer** items (published before the boundary)

### 9. Authentication

The filter endpoint MUST require the same authentication as the collection itself:

- **Inbox**: Only the owner (JWT/OAuth2)
- **Outbox**: Public or owner-only (server-dependent)

---

## Security Considerations

### Query Injection

Servers MUST validate and sanitize filter requests. In particular:

- `tree:path` MUST be restricted to allowed properties
- `tree:value` MUST be restricted to allowed values/types
- Complex queries (e.g., deep property paths) MAY be rejected

**Recommended allowed `tree:path` values:**

- `rdf:type`
- `as:actor`
- `as:object`
- `as:to`
- `as:cc`
- `as:published`
- `as:tag`
- `as:inReplyTo`
- `as:attributedTo`

### Rate Limiting

Filter requests are potentially more expensive than regular GET requests. Servers SHOULD implement rate limiting.

### No Arbitrary SPARQL Queries

This FEP explicitly defines **no** SPARQL interface. The supported operations are limited to the defined `tree:Relation` types.

---

## Examples

### Example 1: Home Timeline

Shows content lifecycle activities from followed actors, visible to public or followers.

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "rdf:type" },
      "tree:value": [
        { "@id": "as:Create" },
        { "@id": "as:Update" },
        { "@id": "as:Delete" },
        { "@id": "as:Announce" }
      ]
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "as:actor" },
      "tree:value": { "@id": "as:following" }
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": [{ "@id": "as:to" }, { "@id": "as:cc" }],
      "tree:value": [
        { "@id": "https://www.w3.org/ns/activitystreams#Public" },
        { "@id": "as:followers" }
      ]
    }
  ],
  "fep34c1:pageSize": 20
}
```

### Example 2: Mentions

Shows activities where the actor is directly addressed via `as:to` or `as:cc` (public mentions only, excluding DMs).

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "rdf:type" },
      "tree:value": [{ "@id": "as:Create" }]
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": [{ "@id": "as:to" }, { "@id": "as:cc" }],
      "tree:value": { "@id": "https://example.com/ap/actors/alice" }
    },
    {
      "@type": "tree:EqualToRelation",
      "tree:path": [{ "@id": "as:to" }, { "@id": "as:cc" }],
      "tree:value": { "@id": "https://www.w3.org/ns/activitystreams#Public" }
    }
  ]
}
```

### Example 3: Private Messages

Shows activities not addressed to `as:Public` (neither in `as:to` nor `as:cc`). This includes direct messages, followers-only posts, and group messages.

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:EqualToRelation",
      "tree:path": { "@id": "rdf:type" },
      "tree:value": [{ "@id": "as:Create" }]
    },
    {
      "@type": "tree:NotEqualToRelation",
      "tree:path": { "@id": "as:to" },
      "tree:value": { "@id": "https://www.w3.org/ns/activitystreams#Public" }
    },
    {
      "@type": "tree:NotEqualToRelation",
      "tree:path": { "@id": "as:cc" },
      "tree:value": { "@id": "https://www.w3.org/ns/activitystreams#Public" }
    }
  ]
}
```

### Example 4: Activities Since Timestamp

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:GreaterThanRelation",
      "tree:path": { "@id": "as:published" },
      "tree:value": {
        "@value": "2026-01-27T00:00:00Z",
        "@type": "xsd:dateTime"
      }
    }
  ]
}
```

### Example 5: Posts from a Specific Instance

```json
{
  "@context": {
    "tree": "https://w3id.org/tree#",
    "fep34c1": "https://w3id.org/fep/34c1#",
    "as": "https://www.w3.org/ns/activitystreams#"
  },
  "@type": "fep34c1:FilterRequest",
  "tree:relation": [
    {
      "@type": "tree:PrefixRelation",
      "tree:path": { "@id": "as:actor" },
      "tree:value": "https://mastodon.social/"
    }
  ]
}
```

---

## Implementation Notes

### For Servers

1. Special placeholder values (`as:following`, `as:followers`) MUST be resolved at query time before evaluating the filter (see Section 4).

2. Allowed `tree:path` values SHOULD be restricted to a known set of ActivityStreams properties (see Security Considerations).

3. For multi-path with `EqualToRelation`, the semantics are UNION (match if any path matches). For `NotEqualToRelation`, the semantics are ALL (none of the paths may match).

### For Clients

1. Clients SHOULD check if `tree:search` is present in the collection
2. If not present: fall back to client-side filtering
3. Filter requests SHOULD be cached (ETag/If-None-Match)
4. Clients SHOULD expect `405 Method Not Allowed` if the server does not support filters

---

## Backwards Compatibility

This FEP is fully backwards compatible:

- Servers without filter support return `405 Method Not Allowed` on POST requests
- Clients can fall back to client-side filtering
- Existing GET semantics for collections remain unchanged
- The `tree:search` property signals filter support

---

## Implementations

- [ChangingGraph](https://changinggraph.org/) is a federated social platform built with Spring Boot and RDF4J. It implements collection filtering on the inbox using TREE relations, translating filter requests to SPARQL queries. It uses multi-path filtering for audience-based views (Timeline, Mentions, Private Messages).

## References

- Pieter Colpaert et al., [TREE Hypermedia Specification][TREE], W3C Community Group, 2023
- Christine Lemmer-Webber et al., [ActivityPub][ActivityPub], W3C Recommendation, 2018
- James Snell, Evan Prodromou, [Activity Streams 2.0][AS2], W3C Recommendation, 2017
- mpuckett, [FEP-5bf0: Collection sorting and filtering][FEP-5bf0], 2023 (WITHDRAWN 2025)

[TREE]: https://treecg.github.io/specification/
[ActivityPub]: https://www.w3.org/TR/activitypub/
[AS2]: https://www.w3.org/TR/activitystreams-core/
[FEP-5bf0]: https://codeberg.org/fediverse/fep/src/branch/main/fep/5bf0/fep-5bf0.md

---

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
