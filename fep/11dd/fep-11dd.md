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

[FEP 7888] lays out some guidelines for use of the `context` as a common property between a set of objects when they can be grouped together through reply association (e.g. a reply-tree).

This proposal aims to extend these guidelines further by codifying:

1. That a context declares an owner via `context.attributedTo`.
1. The situations where a context may be inherited by new objects.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].


## Context Ownership

A context MUST have an owner. Actions carried out pertaining to the context itself MUST be carried out (via `actor`) by the context owner . These actions are out of scope of this FEP.

The following are upgrades to FEP 7888 that pertain to ownership:

1. A `context` MUST be resolvable.
1. When resolved the `context` MUST contain:
    * `attributedTo` denoting the authority/owner of that context.
    * `attributedTo` MUST resolve to an actor.

e.g. A resolvable context collection (see [FEP f228]) declares an owner by setting `context.attributedTo` to a resolvable URI.

```
{
    "id": "https://cats.example.org/1/context",
    "type": "OrderedCollection",
    "attributedTo": "https://cats.example.org/users/cat",
    "items": [...]
}
```

## Context Inheritance

### As a publisher

The object SHOULD inherit a `context` other than its own. It is RECOMMENDED that the object inherit the `context` of the object it is in reply to. Doing so will allow for all members of a `context` collection (per [FEP f228]) to refer to the same `context`.

The object MAY inherit `context` further up the chain.

When publishing an object with a `context` property _outside the local domain_, the context owner SHOULD be addressed (`to`, `cc`, `bto`, `bcc`).

### As a consumer

When consuming an object declaring a `context`  _outside the local domain_, the object's membership MAY be verified by resolving the context directly.

>[!NOTE]
> The remote `context`'s server may not immediately reflect the object's membership due to delays in processing.


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
