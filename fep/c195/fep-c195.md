---
slug: "c195"
type: implementation
authors: Steve Bate <svc-fep@stevebate.net>
status: DRAFT
discussionsTo: https://codeberg.org/steve-bate/fep/issues
dateReceived: 2026-03-17
trackingIssue: https://codeberg.org/fediverse/fep/issues/790
---
# FEP-c195: JSONPath Filtering for ActivityPub Collection Retrieval

## Summary

This proposal defines a filter syntax for ActivityPub collection retrieval.

The syntax supports:

- JSONPath expressions conforming to [RFC9535]
- Filtering collection item arrays (`items` and `orderedItems`)
- Used on [ActivityPub] collections and shared inbox pseudo-collections.

>[!Note]
This proposal is based on the standard RFC9535 JSONPath language. Some JSONPath libraries implement extended functionality beyond the scope of this FEP.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] and [RFC8174] when, and only when, they appear in all capitals, as shown here.

## Filter Syntax

### Grammar

Filter expressions MUST use JSONPath syntax defined by [RFC9535].

Implementations of this proposal MUST accept at least:

- Root selector (`$`)
- Child selectors (`.name`, `['name']`)
- Wildcard selectors (`*`)
- Filter selectors (`[?(<logical-expr>)]`)
- Comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`)
- Boolean operators (`&&`, `||`)

See also: [examples](#example-filters).

### Evaluation Model

A *viewable* object is defined as an ActivityPub entity:

* With `as:Public` in the audience.
* With the current authenticated actor in the audience.
* Attributed to the current authenticated actor

A server applying this proposal:

1. Retrieves the viewable items from the addressed collection or the shared inbox.
2. Applies the JSONPath filter expression to candidate activity/object items
3. Returns matched item values in collection order for `OrderedCollection` or subtypes.

The filter is applied to collection items, not to the outer collection object.

## HTTP Usage

This syntax is used for the `filter` parameter on collection retrieval endpoints. The filter is an item-level filter. Depending on the collection type it will be applied to `orderedItems` or `items`.

The item filter has two variations:

| Case | Description |
|----|-----|
| No leading `[` | The expression will be wrapped in `[` and `]` |
| Leading `[` | Used as-is for the item filter expresssion |

**Example**

`@.type == 'Create'` 

becomes 

`$[?@type == 'Create']`

(for an `OrderedCollection`, otherwise `items` will be used)

For filtering with additional features like projection, the query should start with "[".

**Example**

`[?@.object[*].attachment[?@.type == 'Video']].id` 

becomes 

`$[?@.object[*].attachment[?@.type == 'Video']].id]`


### Query Results

The results MUST be returned as ActivityPub collection objects (optionally paged). The result collection URI should be unique to that filtering operation rather than the original collection URI. For example, it could be original URI with the filter criteria query argument or a generated URI.

## Example Filters

```bash
# Get all CRUD activities
@.type == 'Create' || @.type == 'Update' || @.type == 'Delete'

# Get all notification (non-CRUD) activities
!(@.type == 'Create' || @.type == 'Update' || @.type == 'Delete')

# Get all activities where Alice is the actor
@.actor=='https://example.social/users/alice'

# Get all items published before a specified date
@.published<='2026-02-20T10:30:00Z'

# Get the URI of the objects of all activities having a Video attachment
# This also peforms "projection" of the "id" property
[?@.object[*].attachment[?@.type == 'Video']].id

# Get all activities related to the given object URI (handles refs or embedded)
# Uses "id" projection
[?@.object == 'https://example.social/objects/note-1' || \
  @..object[?@ == 'https://example.social/objects/note-1']].id

# Get all activities who have an actor with 'bob' or 'Bob' in the name
search(@.actor, '[Bb]ob')
```

**HTTP Example**

```
GET /actor/inbox?filter=%24.orderedItems%5B%3F%28%40.type%20%3D%3D%20%27Create%27%20%7C%7C%20%40.type%20%3D%3D%20%27Update%27%20%7C%7C%20%40.type%20%3D%3D%20%27Delete%27%29%5D
Accept: application/activity+json

HTTP/1.1 200 OK
Content-Type: application/activity+json

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://example.com/actor/inbox?filter=%24.orderedItems%5B%3F%28%40.type%20%3D%3D%20%27Create%27%20%7C%7C%20%40.type%20%3D%3D%20%27Update%27%20%7C%7C%20%40.type%20%3D%3D%20%27Delete%27%29%5D
Accept: application/activity+json",
  "type": "OrderedCollectionPage",
  "totalItems": 3,
  "partOf": "https://example.com/actor/inbox",
  "next": "https://example.com/actor/inbox?offset=2&filter=%24.orderedItems%5B%3F%28%40.type%20%3D%3D%20%27Create%27%20%7C%7C%20%40.type%20%3D%3D%20%27Update%27%20%7C%7C%20%40.type%20%3D%3D%20%27Delete%27%29%5D",
  "orderedItems": [
    {
      ...
    }
}
```

### Error Handling

Invalid filters MUST result in an HTTP client error status.
Examples include:

- JSONPath parse failure
- Unsupported JSONPath feature in an implementation
- Invalid URL encoding of the `filter` parameter

Implementations MAY include parser or feature details in a problem response body.

## Related FEPs

### [FEP-34c1](https://codeberg.org/fediverse/fep/src/branch/main/fep/34c1/fep-34c1.md): Collection Filtering using TREE Hypermedia Vocabulary

This FEP is similar in intent but more oriented to RDF and Linked Data use cases.

### [FEP-6606](https://codeberg.org/fediverse/fep/src/branch/main/fep/6606/fep-6606.md): ActivityPub client to server collections addressing conventions

A simpler, but less powerful, filtering language based on a URL query parameter-based language defined in the FEP. The "fuzzy" matching is not well-defined (seems to be substring match) and it appears to not be able to handle conjunctions.

### [FEP-bad1](https://codeberg.org/fediverse/fep/src/branch/main/fep/bad1/fep-bad1.md): Object history collection

Filtering some collections (e.g., inbox and outbox) can provide similar historical results for a given object without the need for explicit history collections.

## Implementations

- [FIRM](https://github.com/steve-bate/firm)


## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement
Proposal have waived all copyright and related or neighboring rights to this work.


[ActivityPub]: https://www.w3.org/TR/activitypub/ "ActivityPub is a decentralized social networking protocol based upon the ActivityStreams 2.0 data format."
[ActivityStreams]: https://www.w3.org/TR/activitystreams-vocabulary/
[RFC9535]: https://www.rfc-editor.org/rfc/rfc9535 "JSONPath: Query Expressions for JSON"
[URI]: https://datatracker.ietf.org/doc/html/rfc3986 "Uniform Resource Identifier (URI): Generic Syntax"
[RFC2119]: https://www.rfc-editor.org/info/rfc2119
[RFC8174]: https://www.rfc-editor.org/info/rfc8174
