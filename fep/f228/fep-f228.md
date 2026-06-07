---
slug: "f228"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2025-02-17
trackingIssue: https://codeberg.org/fediverse/fep/issues/500
---
# FEP-f228: Backfilling conversations

## Summary

The most common conversation backfill method is based on recursive retrieval of posts indicated by `inReplyTo` property and posts contained in `replies` collections. [This is inefficient and stops working if any node in the reply tree becomes inaccessible](https://community.nodebb.org/topic/18844/backfilling-conversations-two-major-approaches).

[FEP-7888: Demystifying the context property][FEP-7888] suggests using the `context` property for grouping related objects (such as posts in a conversation). This property can resolve to a collection, which can be used for efficient backfilling without recursion.

Two different implementations of `context` collection exist: collection of posts and collection of activities.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Collection of posts

The items of this collection are attributed objects, such as `Note` or `Article` objects. It represents a [thread], as seen from the perspective of the conversation owner.

It is an `OrderedCollection`, and the order of items is chronological. It MUST contain at least one item, the top-level post. This post MUST have a `context` property referring to the collection. Other posts might not have this property.

When `context` property is present on a post, it MUST resolve to a collection of posts.

There is a difference between contents of this collection and a reply tree defined by `inReplyTo` and `replies` relationships, because conversation owner might choose to not include certain replies. When a reply is deleted by its author, the sub-replies MAY remain in the thread collection.

> [!NOTE]
> ActivityPub [requires][ActivityPub-Collections] ordered collections to be presented in reverse chronological order. However, an [erratum][ActivityPub-Errata] was proposed to relax this requirement.

## Collection of activities

This collection contains all activities related to posts in a conversation, including but not limited to:

- `Create`
- `Update`
- `Delete`
- `Like`

It is an `OrderedCollection`, and the order of items is chronological. It MUST contain at least one item, the `Create` activity for the top-level post. This activity MUST have a `context` property referring to the collection. Other activities might not have this property.

When `context` property is present on an activity, it MUST resolve to a collection of activities.

`contextHistory` property is used to make a reference from a top-level post to related collection of activities.

> [!NOTE]
> The collection of conversation activities was originally a part of [Conversation Containers][FEP-171b] proposal.

## Reading collections

After top-level post of a conversation is discovered, the whole conversation can be retrieved using the following algorithm:

- If `contextHistory` property is present, retrieve collection of activities and stop.
- If `context` property is present, retrieve collection of posts and stop.
- If `replies` property is present, retrieve collection of replies, and repeat this step for every reply.

## Implementations

Collection of posts:

- NodeBB
- Iceshrimp.NET
- WordPress
- Discourse
- Mitra
- Decodon ([PR](https://github.com/jesseplusplus/decodon/pull/188))
- PieFed ([commit](https://codeberg.org/rimu/pyfedi/commit/8d2afe5acd6c260a9ca9a352a93730d5a7b6bcdd))
- [Mastodon](https://github.com/mastodon/mastodon/releases/tag/v4.5.4)
- [tootik](https://github.com/dimkr/tootik/releases/tag/v0.21.2)
- [Lemmy](https://github.com/LemmyNet/lemmy/pull/5856)

Collection of activities:

- Streams
- Hubzilla
- Forte

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- a, [FEP-7888: Demystifying the context property][FEP-7888], 2023
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- silverpill, [FEP-171b: Conversation Containers][FEP-171b], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityPub-Collections]: https://www.w3.org/TR/activitypub/#collections
[ActivityPub-Errata]: https://www.w3.org/wiki/ActivityPub_errata
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[thread]: https://en.wikipedia.org/wiki/Thread_(online_communication)
[FEP-7888]: https://codeberg.org/fediverse/fep/src/branch/main/fep/7888/fep-7888.md
[FEP-171b]: https://codeberg.org/fediverse/fep/src/branch/main/fep/171b/fep-171b.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
