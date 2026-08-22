---
slug: "49eb"
authors: MaddyUnderStars <maddyunderstars@aus.social>
status: DRAFT
discussionsTo: https://activitypub.space/topic/71072c6d-55a6-4c3b-8aaf-1584d0e60955/fep-49eb-batched-inbox-delivery
dateReceived: 2026-08-22
trackingIssue: https://codeberg.org/fediverse/fep/issues/913
---
# FEP-49eb: Batched Inbox Delivery

## Summary

This document describes a method of delivering multiple activities to an inbox within a single POST request. It may be combined with FEP-0499 Multibox with minimal changes, but adherence to FEP-0499 is not required for this FEP.

## Prior Art

*This section is non-normative*

- The Matrix federation protocol sends EDUs and PDUs ('events') via ['transactions'](https://spec.matrix.org/v1.19/server-server-api/#transactions) which include up to 50 PDUs and 100 EDUs for batch processing.
- [FEP-0499: Delivering to multiple inboxes with a multibox endpoint](https://codeberg.org/fediverse/fep/src/branch/main/fep/0499/fep-0499.md) defines an optional endpoint 'multibox' for delivery of activities to multiple inboxes. It further notes "POST an Add activity where the object is **at least one** activity".
- [FEP-1a11: Send Announces Containing Many Activities](https://codeberg.org/fediverse/fep/src/branch/main/fep/1a11/fep-1a11.md) is batch processing for Like/Dislike/Undo activities within FEP-1b12 Groups. It [documents PieFed behaviour](https://socialhub.activitypub.rocks/t/fep-1a11-send-announces-containing-many-activities/8629/3), which warrants this FEP.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this specification are to be interpreted as described in [RFC-2119].

## Batches

A 'batch' is a Collection or OrderedCollection of activities.
It MUST include the following properties:

- `type`: `"Collection"` or `"OrderedCollection"`
- `items`/`orderedItems`: An array of activities to be delivered. As in Activitystreams, use orderedItems for OrderedCollections and items otherwise.
- `totalItems`: Total number of activities in this batch.

A batch SHOULD include the following properties:

- `startTime`: The creation time of the chronologically first activity in this batch.
- `endTime`: The creation time of the chronologically last activity in this batch.

The batch MAY include any additional properties.

Batches MUST NOT contain more than 50 activities.

When signing activities using [FEP-8b32: Object Integrity Proofs](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md), the activities within the batch MUST be signed individually. This is to allow the receiving server to forward/process the received activities with greater flexibility.

## Delivery

To deliver a batch to an inbox, POST an Add activity to the inbox with the batch embedded in the `object` property.

```json
{
	"type": "Add",
	"object": {
		"items": [
			// ... activities
		],
		"totalItems": 50,
		"startTime": "1970-01-01T00:00:00",
		"endTime": "1970-01-01T00:01:00"
	},
}
```

When delivering activities via FEP-0499: Multibox, the `target` property is added as described in FEP-0499.

When delivered to an actor's inbox, all activities within the batch MUST be addressed to at least that actor.
When delivered to a sharedInbox, the activities can be freely addressed to any actor.

## Processing

Activities within a batch of type OrderedCollection MUST be processed in the order they were defined.
Conversely, activities within a batch of type Collection MAY be processed in any order.

Batched activities are processed and addressed as if they were sent individually.
Receiving a `Create<Note>` individually and receiving a batch containing `Create<Note>` MUST have the same effect.

## Capability Discovery

As batched inbox support may be present on any inbox, there is no way to tell if an inbox supports it without first attempting it and falling back on failure.
However, doing so may be unreliable as servers may only do light processing of the Add activity and/or signatures before adding it to a queue and failing later, as the object of the Add is a Collection.

To solve this, [FEP-844e: Capability Discovery](https://codeberg.org/fediverse/fep/src/branch/main/fep/844e/fep-844e.md) MAY be used to determine if a server supports batched inboxes.

When doing so, the value of the `href` property MUST be `http://w3id.org/fep/49eb` and the value of the `name` property MUST be `FEP-49eb: Batched Inbox Delivery`. Additionally, the server MUST support batched inbox delivery for all inboxes it controls.

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub](https://www.w3.org/TR/activitypub/), 2018
- Matrix Foundation, [Matrix Specification v1.19: Server-Server API#transactions](https://spec.matrix.org/v1.19/server-server-api/#transactions), 2026
- a, [FEP-0499: Delivering to multiple inboxes with a multibox endpoint](https://fediverse.codeberg.page/fep/fep/0499/), 2024
- Rimu Atkinson, [FEP-1a11: Send Announces Containing Many Activities](https://fediverse.codeberg.page/fep/fep/1a11/), 2026
- Felix Ableitner [FEP-1b12: Group federation](https://fediverse.codeberg.page/fep/fep/1b12/), 2022
- silverpill [FEP-8b32: Object Integrity Proofs](https://fediverse.codeberg.page/fep/fep/8b32/), 2022
- silverpill, [FEP-844e: Capability discovery](https://codeberg.org/fediverse/fep/src/branch/main/fep/844e/fep-844e.md), 2025

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
