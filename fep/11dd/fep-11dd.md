---
slug: "11dd"
authors: Julian Lam <julian@nodebb.org>
status: DRAFT
discussionsTo: https://activitypub.space/topic/22/fep-11dd-context-ownership-and-inheritance
dateReceived: 2025-09-11
trackingIssue: https://codeberg.org/fediverse/fep/issues/675
---
# FEP-11dd: Context Ownership and Inheritance


## Summary

### What is a context?

[FEP 7888] lays out some guidelines for use of the `context` as a common property between a set of objects when they can be grouped together through reply association (e.g. a reply-tree).

### What is this for?

This proposal aims to extend these guidelines further by codifying:

1. That a context must declare an owner via `context.attributedTo`.
1. Where and when a context may be inherited by new objects.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].


## Context Ownership

A context MUST have an owner. The following are upgrades to FEP 7888 that pertain to ownership:

1. A `context` MUST be resolvable.
1. When resolved the `context` MUST contain:
    * `attributedTo` denoting the authority/owner of that context.
1. `context.attributedTo` MUST resolve to an actor ([ActivityPub §4.1 Actor Objects](https://www.w3.org/TR/activitypub/#actor-objects)).

### Example

A resolvable context collection (see [FEP f228]) declares an owner by setting `context.attributedTo` to a resolvable URI.

```
{
    "id": "https://cats.example.org/1/context",
    "type": "OrderedCollection",
    "attributedTo": "https://cats.example.org/users/cat",
    "items": [...]
}
```

## Context Inheritance

Inheritance is considered only when a new object being published has a relation (typically via `inReplyTo`) to another object.

There are situations where a relation exists but context is explicitly *not* inherited (e.g. forked topic, quote post). These situations are out of scope of this FEP.

### As a publisher

The object MUST inherit `context` from the root node, if the property is present and resolvable. Otherwise the object MUST NOT publish a context.

Implementors SHOULD map that inherited context to a local identifier (if applicable) to support future use-cases/activities.

When publishing an object with a `context` property _outside the local domain_, the context owner SHOULD be addressed (`to`, `cc`, `audience`).

> [!NOTE]
> If an object is at the root/top-level, then there is nothing to inherit and a new context should be generated.

### As a consumer

When consuming an object declaring a `context`  _outside the local domain_, the object's membership MAY be verified by resolving the context directly.

>[!NOTE]
> The remote `context`'s server may not reflect the object's membership in a timely manner due to delays in processing (i.e. network congestion, approval queues, etc.)


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- a, [FEP 7888]: Demystifying the context property, 2023
- silverpill, [FEP f228]: Backfilling conversations, 2025

[ActivityPub]: https://www.w3.org/TR/activitypub/
[FEP 7888]: https://w3id.org/fep/7888
[FEP f228]: https://w3id.org/fep/f228

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
