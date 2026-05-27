---
slug: "fc48"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2026-02-27
trackingIssue: https://codeberg.org/fediverse/fep/issues/769
---
# FEP-fc48: Generic ActivityPub server

## Summary

Generic ActivityPub server is a server that implements standard ActivityPub client API or [FEP-ae97] client API, and can process any activity (including activities those behavior is not defined in the ActivityPub specification).

## Motivation

Most of existing ActivityPub servers are designed for a specific type of application: a micro-blog, a forum, a video sharing service. This leads to a situation where users are expected to have separate accounts for each application type.

Even a server that implements the entirety of [ActivityPub] specification is limited because it doesn't support custom activities.

A truly generic server does not have these limitations and can work with any type of client application.

## Object classification

A generic server MUST determine the class of an object before processing it. The classification of ActivityPub objects is covered in [FEP-2277: ActivityPub core types][FEP-2277].

## Activities and side effects

A generic server MUST support the following basic activities:

- `Create`
- `Update`
- `Delete`
- `Add`
- `Remove`

The side effects of these activities are implicit and are defined in the [ActivityPub] specification.

A generic server can only carry out the side effects of basic activities. Therefore, clients MUST specify the side effects of all other activities as additional activities. Clients can embed them into an activity using the `result` property, or send them separately.

A generic server MAY support other activity types defined in the [ActivityPub] specification.

## Authentication and authorization

A generic server MUST verify all objects according to the universal authentication and authorization procedures described in [FEP-fe34: Origin-based security model][FEP-fe34].

When processing activities submitted by a client, the server can only check permissions for basic activities. Therefore, recipients SHOULD NOT use the same-origin policy to verify permissions.

## Managing collections

A generic server MUST automatically create `inbox`, `outbox` and other actor collections defined in the ActivityPub specification after registering an actor.

Other collections MUST be created by clients using `Create` activities where `object` is an empty collection.

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
