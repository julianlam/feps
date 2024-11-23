---
slug: "171b"
authors: silverpill <@silverpill@mitra.social>
status: DRAFT
dateReceived: 2024-11-23
discussionsTo: https://socialhub.activitypub.rocks/t/fep-171b-conversation-containers/4766
---

# FEP-171b: Conversation Containers

## Summary

This document specifies a model for managing conversations in [ActivityPub] network as collections. It is based on the implementation of [Conversation Containers][Containers] in [Streams](https://codeberg.org/streams/streams).

In this model conversations are managed by the actor that created the initial post of a conversation thread. Such conversations take place within a specific audience and may be moderated.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Containers

A conversation container is implemented as a collection. Every item in that collection is an `Add` activity where `object` is another activity (such as `Create`, `Update`, `Delete`, `Like`, `Dislike`, `EmojiReact` or `Announce`). The conversation owner distributes `Add` activities to other participants, thus keeping their views of the conversation synchronized.

### Container collection

- Collection type MUST be `OrderedCollection`.
- Collection items MUST be in chronological order.
- Collection MUST have an `attributedTo` property containing the `id` of the conversation owner.
- Collection SHOULD have `collectionOf` property with value `Activity`.

>[!NOTE]
>The required collection type might be changed to a more descriptive one (such as `Context`) in a future version of this document. That will allow identification of `Add` activities belonging to a conversation container by the value of `Add.target.type`.

>[!NOTE]
>In addition to the conversation container collection, implementers MAY provide collection that represents the conversation tree and contains posts.

### Adding activities to a conversation

Conversation owner can add any activity to the conversation. However, if a `context` property is present on the activity, its value SHOULD be identical to the ID of a conversation container.

When activity is added to the conversation, its owner sends an `Add` activity to the conversation audience (usually defined by a top-level post).

`Add` activities published by the conversation owner MUST have a `target` property containing a partial object:

- `type`: `OrderedCollection`
- `id`: the `id` of the conversation container.
- `attributedTo`: the `id` of the collection owner.

`Add` activities published by the conversation owner MUST be added to the conversation container collection.

>[!NOTE]
>The "conversation outbox" model where the `target` of `Add` activity is a collection of `Add` activities is not compatible with ActivityStreams definition of [Add](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-add) activity, according to which *Add activity indicates that the actor has added the object to the target*.

### Top-level post

The top-level post MUST have a `context` property indicating a conversation container.

>[!NOTE]
>The usage of a `context` property in conversation containers differs from recommendations provided in [FEP-7888].

### Interactions

All activities in a conversation SHOULD only be delivered to the conversation owner.

Conversation participants SHOULD reject conversation activities that have not been added to the conversation by its owner.

The audience of a reply MUST be copied from a conversation root.

Reply with a different audience can be created by starting a new conversation and including a [FEP-e232] link to the post instead of specifying it in `inReplyTo`.

### Moderation

To remove a post from a conversation, its owner publishes a `Delete` activity where `object` is the post that must be removed. This activity is then wrapped in `Add` activity and distributed to the conversation audience.

>[!NOTE]
>Actor shouldn't be able to delete objects it didn't create. In a future version of this document `Delete` might be replaced with `Remove(target: Thread)`.

### Backfilling

Conversation participants can retrieve missing activities by reading the conversation container collection.

## Authentication

When an ActivityPub server receives an `Add` activity in its inbox, it MUST perform the authentication procedure according to [FEP-fe34]:

- If `Add.object` is not embedded, fetch it. If location of the fetched activity has the same origin as `Add.object`, add it to the conversation.
- If `Add.object` is embedded, check whether `Add.actor` and `Add.object.actor` have the same origin.
- If origins are equal, add `Add.object` to the conversation.
- If origins are different and [FEP-8b32] integrity proof is present, verify the proof. If the proof is valid, add `Add.object` to the conversation.
- If integrity proof is not present, fetch `Add.object` by its `id`. If location of the fetched activity has the same origin as `Add.object.id`, add fetched activity to the conversation.

>[!WARNING]
>Sometimes activities have non-dereferenceable identifiers. That may prevent their authentication.

## Examples

Example of an `Add` activity for a reply to a followers-only post:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Add",
  "id": "https://alice.example/activities/add/1",
  "actor": "https://alice.example/actors/1",
  "object": {
    "@context": [
      "https://www.w3.org/ns/activitystreams"
    ],
    "type": "Create",
    "id": "https://bob.example/activities/create/1",
    "actor": "https://bob.example/actors/1",
    "context": "https://alice.example/contexts/1",
    "object": {
      "@context": [
        "https://www.w3.org/ns/activitystreams"
      ],
      "type": "Note",
      "id": "https://bob.example/posts/1",
      "inReplyTo": "https://alice.example/posts/1",
      "content": "This is a reply",
      "to": [
        "https://alice.example/actors/1",
        "https://alice.example/actors/1/followers"
      ]
    },
    "to": [
      "https://alice.example/actors/1",
      "https://alice.example/actors/1/followers"
    ]
  },
  "target": {
    "type": "OrderedCollection",
    "id": "https://alice.example/contexts/1",
    "attributedTo": "https://alice.example/actors/1"
  },
  "to": [
    "https://bob.example/actors/1",
    "https://alice.example/actors/1/followers"
  ]
}
```

Example of a container of a followers-only conversation:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "OrderedCollection",
  "id": "https://alice.example/contexts/1",
  "attributedTo": "https://alice.example/actors/1",
  "orderedItems": [
    "https://alice.example/activities/add/1"
  ]
}
```

## Comparison with other proposals

- [FEP-400e]: The `object` of `Add` is an object, not an activity, and conversation collection contains added objects. `Reject(Create)` activity is generated for rejected posts. Conversation participants are expected to add a `target` property to posts.
- [FEP-1b12](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md): `Announce` activity is used instead of `Add`. Conversation and related activities are synchronized between participants, but conversation backfilling mechanism is not specified.
- [GoToSocial Interaction Policy](https://docs.gotosocial.org/en/latest/federation/posts/#interaction-policy): conversation is managed separately for each post (in a conversation container the owner has authority over the entire thread). `Accept` or `Reject` activity is generated for every interaction (in a conversation container `Add` activity is generated when activity is approved, and rejected activities are ignored). Conversation is not synchronized between participants, but can be backfilled by recursively fetching `replies` collections.

## Implementations

- [Streams](https://codeberg.org/streams/streams)

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub], 2018
- Mike Macgirvin, [Containers], 2024
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- Gregory Klyushnikov, [FEP-400e: Publicly-appendable ActivityPub collections][FEP-400e], 2021
- a, [FEP-7888: Demystifying the context property][FEP-7888], 2023
- silverpill, [FEP-e232: Object Links][FEP-e232], 2022
- silverpill, [FEP-fe34: Origin-based security model][FEP-fe34], 2024
- silverpill, [FEP-8b32: Object Integrity Proofs][FEP-8b32], 2022

[ActivityPub]: https://www.w3.org/TR/activitypub/
[Containers]: https://fediversity.site/help/develop/en/Containers
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[FEP-400e]: https://codeberg.org/fediverse/fep/src/branch/main/fep/400e/fep-400e.md
[FEP-7888]: https://codeberg.org/fediverse/fep/src/branch/main/fep/7888/fep-7888.md
[FEP-e232]: https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md
[FEP-fe34]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
