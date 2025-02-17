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

Object observer can be specified using the `observer` property.

It MUST be a followable actor and SHOULD have an `Application` type. Observer doesn't perform any activities on its own, but [forwards][InboxForwarding] to its followers all activities that affect the observed object.

It SHOULD have a WebFinger address (consumers should be able to follow it even if they don't understand `observer` property).

## Use case: subscribing to a conversation

When conversation is represented by a [collection][FEP-f228], a collection observer can be created to support conversation subscriptions.

This actor can be attached to a collection via `observer` property, and can forward `Add` and `Remove` activities that modify it.

## Non-forwarding observers

If forwarding is not desirable, object observers can use `Announce` activity to distribute observed activities.

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
