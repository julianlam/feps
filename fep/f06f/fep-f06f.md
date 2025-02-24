---
slug: "f06f"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2025-02-18
trackingIssue: https://codeberg.org/fediverse/fep/issues/503
---
# FEP-f06f: Object observers

## Summary

Object observer is an [ActivityPub] actor that can be followed to receive object updates.

This proposal is intended to complement [FEP-bad1: Object history collection][FEP-bad1].

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Observers

Object observer is a followable actor. It doesn't perform any activities on its own, but activities that affect the observed object are [forwarded][InboxForwarding] to its followers. Only objects and collections can be observed.

Object observer MUST have an `observerOf` property specifying the observed object, and it SHOULD have an `Application` type.

Objects can specify their observers using the `observer` property.

Object observer can be created with [ActivityPub] client by publishing a `Create` activity with user's actor as its `actor` and with observer actor as its `object`.

Implementers MAY use a single cryptographic key for signing all HTTP requests made by observers on a server.

## Use case: subscribing to a conversation

When conversation is represented by a [collection][FEP-f228], a collection observer can be created to support conversation subscriptions.

This actor can be attached to a collection via `observer` property, and can forward `Add` and `Remove` activities that modify it.

## Non-forwarding observers

If forwarding is not desirable, object observers can use `Announce` activity to distribute observed activities.

## Examples

Example of an observer actor:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Application",
  "id": "https://server.example/objects/123456/observer",
  "inbox": "https://server.example/objects/123456/observer/inbox",
  "outbox": "https://server.example/objects/123456/observer/outbox",
  "observerOf": "https://server.example/objects/123456"
}
```

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- a, [FEP-bad1: Object history collection][FEP-bad1], 2023
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997

[ActivityPub]: https://www.w3.org/TR/activitypub/
[FEP-bad1]: https://codeberg.org/fediverse/fep/src/branch/main/fep/bad1/fep-bad1.md
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[InboxForwarding]: https://www.w3.org/TR/activitypub/#inbox-forwarding
[FEP-f228]: https://codeberg.org/fediverse/fep/src/branch/main/fep/f228/fep-f228.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
