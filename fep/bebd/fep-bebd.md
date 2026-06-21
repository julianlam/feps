---
slug: "bebd"
authors: MaddyUnderStars <maddyunderstars@aus.social>
status: DRAFT
discussionsTo: https://activitypub.space/topic/28f8ab19-d074-4494-9e72-3aabdf1606ab/fep-bebd-follow-invites
dateReceived: 2026-06-05
trackingIssue: https://codeberg.org/fediverse/fep/issues/854
---

# FEP-bebd: Follow Invites

## Summary

This document describes an alternative method of accepting follow requests via an 'invite code' intended to be used with Private [FEP-1b12 Groups](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md), although it is applicable to any Actor. It further defines an extension of Webfinger to resolve an InviteCode to its corresponding Actor.

### Why is this needed?

It is useful to allow some mechanism of joining communities via a secret rather than knowing the Actor ID and having manually accepted requests.

Some use cases include:
- As an anti-spam measure
- To lift some burden of Accepting Follow requests manually
- The ability to Follow Actors via short identifiers rather than a full Actor ID or Webfinger mention.
- The ability to restrict certain InviteCodes
- The ability to provide a tentative inviteCode to a group without establishing a full Follow relationship

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this specification are to be interpreted as described in [RFC-2119].

## InviteCodes

InviteCode is an ActivityStreams Object that represents a short code used to automatically Approve Follow requests.

It MUST contain the following properties:
- `type` (REQUIRED): The value of the `type` property MUST be the string `InviteCode`
- `name` (REQUIRED): The instance-unique string used to reference this InviteCode
- `attributedTo` (REQUIRED): The Actor that this InviteCode can be used to Follow

The document MAY contain additional properties.

The InviteCode `name` MAY be user-defined. It is RECOMMENDED that the `name` is a short, alphanumeric string.
If InviteCodes are to be dereferenceable via Webfinger as described below, the `name` MUST be able to form a valid URL.

As InviteCodes can be dereferenced via Webfinger, they MUST be unique per instance.

### Follow Activities using an InviteCode

A Follow activity MAY include the ID of an InviteCode in the `instrument` field.

```json
{
	"id": "https://example.com/myFollowActivity",
	"type": "Follow",
	"actor": "https://example.com/myActor",
	"object": "https://remote.example/remoteActor",
	"instrument": "https://remote.example/remoteInvite",
}
```

When an Actor receives a Follow activity containing an InviteCode:
1. If the Actor does not manually approve follows, the InviteCode is ignored
2. The Actor MUST ensure that the InviteCode exists and was acknowledged by the Actor prior to its use
3. The Actor MAY impose any additional restrictions to the InviteCodes use
4. If the InviteCode has been deemed valid, an Accept activity is automatically sent for the Follow as would be normal for an Actor not gated by an InviteCode.

If the InviteCode is not valid, a Reject activity SHOULD be sent.

#### Example Restrictions

*This section is non-normative*

- The InviteCode may include an `endTime` as defined by ActivityStreams. After this timestamp the InviteCode may be deleted
- The Actor may only accept an InviteCode when used by some set of Actors
- The Actor may track the number of uses for an InviteCode and deny uses past some threshold
- The Actor may set the InviteCode to be an answer to some public question to create more friction for those outside some desired community

### Activities on InviteCodes

For the purposes of Group moderation by external Actors is it useful to allow modifications to InviteCodes via activities.

When an activity modifying the InviteCodes for an Actor is received, the Actor MUST ensure that the activity is being performed by an authorised Actor.

- To create a new InviteCode for an Actor, a standard `Add` activity is sent to the Actor the InviteCode is associated with.
- To update an InviteCode, a standard `Update` activity is sent to the Actor the InviteCode is associated with.
- To remove an InviteCode, a standard `Remove` activity is sent to the Actor the InviteCode is associated with.

When an Add, Update, or Remove activity is received by an Actor from an unauthorised Actor, the Actor MAY send a `Reject(InviteCode)`, refuse to add it to its `invites` Collection, and deem the InviteCode invalid for future Follow requests.

### `invites` Collection

Actors that accept InviteCodes SHOULD include an `invites` field that resolves to a Collection containing valid InviteCodes for this Actor.
If present, the `invites` Collection MUST be private and only accessible to authorised Actors.

## InviteCode Dereferencing via Webfinger

InviteCodes MAY be dereferenceable via Webfinger.

To prevent InviteCodes colliding with regular Webfinger `acct` lookups, a new URI scheme `invite` is defined.

To resolve an InviteCode `ABCDE` hosted on instance `example.com`, we can query:
```
GET https://example.com/.well-known/webfinger?resource=invite:ABCDE@example.com
```

This will resolve to an InviteCode object which can further be resolved via the `attributedTo` field to the target Actor.

## A note on Authorised Actors

*This section is non-normative*

For the purposes of viewing the `invites` collection, authorised actors may include only the 'invite-actor', or it may include anyone following them, or any other criteria.
For the purposes of updating, adding, or removing InviteCodes from Actors, authorised actors may be the same set as above but that is not required.

## References

- [ActivityPub] Christine Lemmer Webber, Jessica Tallon, [ActivityPub](https://www.w3.org/TR/activitypub/), 2018
- [ActivityStreams] J. Snell, E. Prodromou, [ActivityStreams](https://www.w3.org/TR/activitystreams-core/), 2017
- [Webfinger] P. Jones, G. Salgueiro, M. Jones, J. Smarr, [RFC 7033](https://datatracker.ietf.org/doc/html/rfc7033),2013
- [FEP-1b12 Groups] F. Ableitner, [FEP-1b12: Group federation](https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md)

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighbouring rights to this work.
