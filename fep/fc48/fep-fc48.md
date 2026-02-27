---
slug: "fc48"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2026-02-27
---
# FEP-fc48: Generic ActivityPub server

## Summary

Generic ActivityPub server is a server that implements standard ActivityPub client API or [FEP-ae97] client API, and can process any activity (including activities those behavior is not defined in the ActivityPub specification).

## Classification

A generic server MUST determine the class of an object before processing it. The classification of ActivityPub objects is covered in [FEP-2277: ActivityPub core types][FEP-2277].

## Authentication and authorization

A generic server MUST verify all objects according to the universal authentication and authorization procedures described in [FEP-fe34: Origin-based security model][FEP-fe34].

## Activities and side effects

A generic server MUST support the following basic activities:

- `Create`
- `Update`
- `Delete`
- `Add`
- `Remove`
- `Offer`
- `Accept`
- `Reject`

A generic server SHOULD support other activity types defined in the [ActivityPub] specification.

Other activities MUST NOT have side-effects. Any additional operations, such as collection updates, MUST be specified using the `result` property or sent as separate activities.

## Managing collections

A generic server MUST automatically create `inbox`, `outbox` and other actor collections defined in the ActivityPub specification after registering an actor.

A generic server MUST create the collection specified in `target` property when a client publishes `Add` or `Move` activity. To create an empty collection, clients can publish an `Add` activity without `object`.

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- silverpill, [FEP-ae97: Client-side activity signing][FEP-ae97], 2023
- silverpill, [FEP-2277: ActivityPub core types][FEP-2277], 2025
- silverpill, [FEP-fe34: Origin-based security model][FEP-fe34], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[FEP-2277]: https://codeberg.org/fediverse/fep/src/branch/main/fep/2277/fep-2277.md
[FEP-fe34]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md
[FEP-ae97]: https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
