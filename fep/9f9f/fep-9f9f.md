---
slug: "9f9f"
authors: silverpill <@silverpill@mitra.social>
type: informational
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2026-04-03
---
# FEP-9f9f: Collections

## Summary

This document describes the current best practices for implementing and using [ActivityPub] collections.

Some parts of it are based on the implementation of collections in [GoActivityPub](https://github.com/go-ap).

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## What is a collection?

### Activity Streams definition

[Activity Streams 2.0](https://www.w3.org/TR/activitystreams-core/#dfn-collectionpage): A collection is an object with `Collection` type or its subtype (e.g. `OrderedCollection`).

### Duck typing

[FEP-2277]: A collection is an object with `items`, `orderedItems`, `totalItems`, `partOf`, `first`, `last`, `next`, `prev` or `current` property.

## Ownership

A collection SHOULD have an `attributedTo` property indicating the actor that created it.

## Creating collections

Clients can create collections by publishing a `Create` activity where `object` is a collection. The server MUST ignore reserved collection properties such as `items`, `totalItems` and pagination properties.

Some special collections, such as `inbox` and `outbox` are created automatically by a server.

Servers MAY create collections automatically when the `object` of `Create` activity contains a property that points to a collection, such as `likes`, `shares` or `replies`. When the specified collection ID is local, the server MUST verify that the ID is valid, and MAY assign a different ID.

Clients MUST NOT embed non-anonymous collections in objects.

Collection IDs SHOULD NOT contain query parameters.

## Updating collections

The contents of a collection are modified either directly by `Add`, `Remove` and `Move` activities, or indirectly by side-effects of other activities.

A client can update other properties of a collection by generating an `Update` activity. The server MUST NOT overwrite reserved collection properties such as `items`, `totalItems` and pagination properties.

> [!NOTE]
> `Update` of a collection is not compatible with client-side signing (FEP-ae97) because partial updates are not supported there.

## Ordering

ActivityPub requires `OrderedCollection` to be presented in [reverse chronological order][AP-Collections], though in practice some ordered collections are presented in forward chronological order.

## Filtering

Collections can be filtered.

Filters are specified using query parameters that are appended to a collection ID. A set of guidelines for using these parameters has been proposed in [FEP-6606: ActivityPub client to server collections addressing conventions][FEP-6606].

## Pagination

Pagination of collections is described in [Activity Streams 2.0][AS-Paging].

Collection page IDs are usually created by appending query parameters to a collection ID:

- `page` (integer): the page number.
- `after` and `before` (percent-encoded URI): the item identifier for cursor based pagination.
- `maxItems` (integer): the maximum number of items in a page.

## Access control

Collections SHOULD be filtered based on the permissions of a user.

However, a collection itself usually doesn't have an audience and is treated as public by default.

## Addressing

An object can be addressed to a collection. When determining delivery targets and regulating access to an object, the server SHOULD expand collections by replacing them with actors they contain (if any).

### `Public` collection

`https://www.w3.org/ns/activitystreams#Public` is a special collection ID that is used for public addressing. It is described in [ActivityPub][AP-Public].

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Streams 2.0][ActivityStreams], 2017
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- silverpill, [FEP-2277: ActivityPub core types][FEP-2277], 2025
- Marius Orcsik, [FEP-6606: ActivityPub client to server collections addressing conventions][FEP-6606], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityStreams]: https://www.w3.org/TR/activitystreams-core/
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[FEP-2277]: https://codeberg.org/fediverse/fep/src/branch/main/fep/2277/fep-2277.md
[FEP-6606]: https://codeberg.org/fediverse/fep/src/branch/main/fep/6606/fep-6606.md
[AS-Paging]: https://www.w3.org/TR/activitystreams-core/#paging
[AP-Collections]: https://www.w3.org/TR/activitypub/#collections
[AP-Public]: https://www.w3.org/TR/activitypub/#public-addressing

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
