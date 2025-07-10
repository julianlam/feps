---
slug: "844e"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/silverpill/feps/issues
dateReceived: 2025-06-14
trackingIssue: https://codeberg.org/fediverse/fep/issues/624
---
# FEP-844e: Capability discovery

## Summary

Capability discovery for [ActivityPub] applications.

This document is based on the idea described in [FEP-aaa3: Listing Implemented Specifications on the Application Actor][FEP-aaa3].

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Application object

An application can advertise its capabilities using the `implements` property on an `Application` object.

This object might not be an actor. The value of `implements` property MUST be an array of `Link` objects, each containing the following properties:

- `href` (REQUIRED): the unique identifier of the capability. The value MUST be an URI.
- `name` (RECOMMENDED): the short description of the capability.

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/844e"
  ],
  "type": "Application",
  "id": "https://social.example/server",
  "implements": [
    {
      "href": "https://datatracker.ietf.org/doc/html/rfc9421",
      "name": "RFC-9421: HTTP Message Signatures"
    }
  ]
}
```

## Discovery through an actor

An `Application` object can be linked to an actor using the [`generator`][generator] property. The value of this property SHOULD be a partial object containing the `implements` property. That object MAY be anonymous (without an identifier).

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/844e"
  ],
  "id": "https://social.example/actors/1",
  "type": "Person",
  "inbox": "https://social.example/actors/1/inbox",
  "outbox": "https://social.example/actors/1/outbox",
  "generator": {
    "type": "Application",
    "implements": [
      "href": "https://datatracker.ietf.org/doc/html/rfc9421",
      "name": "RFC-9421: HTTP Message Signatures"
    ]
  }
}
```

## Discovery through a well-known endpoint

The mechanism of discovering an `Application` object using WebFinger is described in [FEP-d556].

Capability discovery through NodeInfo endpoint is discouraged.

## Intended use

The reliance on the mechanism described in this document might increase implementation complexity and hinder interoperability.

Implementers MUST NOT use it in cases where capabilities can be inferred from properties and types of objects.

## Registry of software capabilities

(This section is non-normative.)

| Name | Identifier |
| ---  | ---        |
| RFC-9421: HTTP Message Signatures | https://datatracker.ietf.org/doc/html/rfc9421 |
| RFC-9421 signatures using the Ed25519 algorithm | https://datatracker.ietf.org/doc/html/rfc9421#name-eddsa-using-curve-edwards25 |

## Implementations

- Streams
- Forte
- Mitra
- [ActivityPub for WordPress](https://activitypub.blog/2025/07/09/7-0-0-i-will-follow-you/)

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- Helge, [FEP-aaa3: Listing Implemented Specifications on the Application Actor][FEP-aaa3], 2024
- Steve Bate, [FEP-d556: Server-Level Actor Discovery Using WebFinger][FEP-d556], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RFC-2119]: https://datatracker.ietf.org/doc/html/rfc2119.html
[FEP-aaa3]: https://codeberg.org/helge/fep/src/commit/e1b2a16707b542ea5ea0cfb390ac1abce89f05bb/fep/aaa3/fep-aaa3.md
[FEP-d556]: https://codeberg.org/fediverse/fep/src/branch/main/fep/d556/fep-d556.md
[generator]: https://www.w3.org/TR/activitystreams-vocabulary/#dfn-generator

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
