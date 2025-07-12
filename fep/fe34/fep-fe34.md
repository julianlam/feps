---
slug: "fe34"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
dateReceived: 2024-11-15
discussionsTo: https://socialhub.activitypub.rocks/t/fep-fe34-origin-based-security-model/4292
trackingIssue: https://codeberg.org/fediverse/fep/issues/445
---
# FEP-fe34: Origin-based security model

## Summary

Developing a comprehensive [ActivityPub] security framework based on the concept of [web origin][RFC-6454].

## Rationale

[ActivityPub] standard does not specify authentication and authorization mechanisms. However, in some cases it hints at the importance of the web origin:

>**3. Objects**

>... Servers SHOULD validate the content they receive to avoid content spoofing attacks. (A server should do something at least as robust as checking that the object appears as received at its origin, but mechanisms such as checking signatures would be better if available).

>**7.3 Update Activity**

>... The receiving server MUST take care to be sure that the Update is authorized to modify its object. At minimum, this may be done by ensuring that the Update and its object are of same origin.

Implementations often rely on origin and ownership checks for determining the validity of activities and objects, but exact requirements are not documented and can be easily overlooked, leading to vulnerabilities such as [GHSA-3fjr-858r-92rw].

This proposal attempts to formalize existing practices and provide guidance for implementers.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Origin

Object identifiers can be grouped together into protection domains called "origins". This concept is similar to the "web origin" concept described in [RFC-6454], and origins of object IDs are computed by the same algorithm.

The same-origin policy determines when a relationship between objects can be trusted. Different origins are considered potentially hostile and are isolated from each other to varying degrees. Actors sharing an origin are assumed to trust each other because all their interactions are mediated by a single piece of software operated by a single person or an organization.

## Assumptions

Origin-based security model is supposed to be used when object identifiers are HTTP(S) URIs and actors are managed by servers. The model can also be used with other kinds of identifiers, but that is not covered in this document.

## Authentication

Authentication is the process of verifying the origin of an ActivityPub object. It is performed in order to protect an application from [spoofing](https://en.wikipedia.org/wiki/Spoofing_attack) attacks.

Objects can be authenticated using the following methods:

- Fetching from an origin
- Verification of a signature
- Authentication through embedding

If an object can't be authenticated, it MUST be discarded.

Fetching from an origin is the primary authentication method, and other authentication methods described in this document depend on it. Consumers SHOULD attempt to fetch the object from its origin if other authentication methods are not available.

### Fetching from an origin

Non-anonymous ActivityPub objects can be authenticated by making an HTTP GET request with object's ID as the target.

The last URI in the chain of redirects is object's location. The location SHOULD match the ID of the retrieved object. If object's location and ID are different, they MUST have the same origin.

Servers MUST validate all objects received from clients. Any activity representing an action that actor is not [authorized](#authorization) to perform MUST be rejected. Special attention needs to be paid to media uploads, because malicious actors might attempt to bypass validation by uploading ActivityPub documents as media (see [GHSA-jhrq-qvrm-qr36] for more information).

Servers MUST NOT serve objects until they are validated.

### Signatures

Signature-based authentication can be used when:

- An object is delivered to inbox and the request contained a valid [HTTP signature][HttpSig].
- An object contains a valid [FEP-8b32] integrity proof.

The ID of the public key (or the verification method) MUST have the same origin as the object's ID.

Servers MUST NOT share secret keys with clients.

Servers MUST NOT allow clients to create objects representing public keys, including such objects embedded within actors and other objects. Embedded public keys with a different origin are permitted.

### Embedding

In some cases, an embedded object can be trusted when its wrapping object is trusted:

- An object is the `object` of a `Create` activity, and it has the same origin and the same [owner](#ownership) as the activity.
- An embedded object is identified as a [fragment][Fragment] of the wrapping object.
- An embedded object is anonymous (doesn't have an ID).

## Authorization

Authorization is the process of verifying permission to [create, read, update or delete](https://en.wikipedia.org/wiki/Create%2C_read%2C_update_and_delete) an object.

### Ownership

Ownership is indicated by a property of an ActivityPub object. The name of this property differs depending on the object class:

- The owner of an actor is indicated by its `id` property.
- Activities have an `actor` property, which describes the actor that performed the activity. This actor is considered to be the owner of the activity.
- Public keys and verification methods have `owner` and `controller` properties.
- Other kinds of objects might have an `attributedTo` property, which describes the actor to which the object is attributed. This actor is considered to be the owner of the object.

The owner of an object MUST be an actor.

Identifier of an object and identifier of its owner MUST have the same origin.

>[!NOTE]
>This document uses terms such as "actor" and "activity" in accordance with the object classification given in [FEP-2277].

>[!WARNING]
>According to [Activity Vocabulary][ActivityVocabulary], `actor` and `attributedTo` properties can contain references to multiple actors. These scenarios are not covered by this document and implementers are expected to determine the appropriate authorization procedures on a case-by-case basis.

### Create, update and delete

The actor that creates an object MUST be its owner.

If activity modifies or deletes an object, its owner SHOULD match the object's owner. If owners are different, their IDs MUST have the same origin.

Examples:

- `Update` and `Delete` activities, and objects indicated by their `object` property SHOULD have the same owner.
- `Undo` activity and object indicated by its `object` property SHOULD have the same owner.
- `Add` and `Remove` activities, and objects indicated by their `target` property SHOULD have the same owner.
- `Announce` and `Like` activities don't modify objects indicated by their `object` property, therefore their owners can be different.

### Ownership transfer

When ownership changes, the new owner ID MUST have the same origin as the old owner ID.

### Access control

When a protected object is retrieved, the `GET` request MUST contain a [HTTP signature][HttpSig] created using a key whose owner MUST belong to object's intended audience. The same-origin policy is not sufficient in this case because clients might use the [proxyUrl] endpoint to make requests signed with a key controlled by the server.

### Implicit ownership

In some cases ownership can be implicit. Examples:

- Inbox and outbox collections are expected to be owned by the actor to which they are attached.
- All pages of a collection are expected to be owned by the same actor.

Authorization recommendations provided in this document still apply in such cases.

## Reciprocal claims

When the same-origin policy can not be used, a trusted relationship between objects can be established with reciprocal claims. Claims are considered reciprocal when one object specifies a claim that is accompanied by a reverse claim specified in another object.

Example:

- Any activity performed by an actor can be verified by retrieving it from the actor's outbox.

## Cross-origin relationships

Relationships between objects with different origins are possible, but they MUST be confirmed with reciprocal claims made by both origins. In that case, the same-origin policy can be bypassed.

Examples:

- An activity can be signed with a key of different origin if that key is referenced from the actor document.
- An object can be deleted by an actor of different origin if that actor is specified as a moderator for the context to which the object belongs.
- An actor can migrate from one server to another by performing the `Move` activity if the migrating actor is included in the target actor's `alsoKnownAs`.

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Vocabulary][ActivityVocabulary], 2017
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- A. Barth, [The Web Origin Concept][RFC-6454], 2011
- silverpill, [FEP-8b32: Object Integrity Proofs][FEP-8b32], 2022
- Ryan Barrett, nightpool, [ActivityPub and HTTP Signatures][HttpSig], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityVocabulary]: https://www.w3.org/TR/activitystreams-vocabulary/
[GHSA-3fjr-858r-92rw]: https://github.com/mastodon/mastodon/security/advisories/GHSA-3fjr-858r-92rw
[GHSA-jhrq-qvrm-qr36]: https://github.com/mastodon/mastodon/security/advisories/GHSA-jhrq-qvrm-qr36
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[RFC-6454]: https://www.rfc-editor.org/rfc/rfc6454.html
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md
[FEP-2277]: https://codeberg.org/fediverse/fep/src/branch/main/fep/2277/fep-2277.md
[HttpSig]: https://swicg.github.io/activitypub-http-signature/
[proxyUrl]: https://www.w3.org/TR/activitypub/#actor-objects
[Fragment]: https://en.wikipedia.org/wiki/URI_fragment

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
