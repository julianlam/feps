---
slug: "521a"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
dateReceived: 2023-07-08
trackingIssue: https://codeberg.org/fediverse/fep/issues/130
discussionsTo: https://socialhub.activitypub.rocks/t/fep-521a-representing-actors-public-keys/3380
---
# FEP-521a: Representing actor's public keys

## Summary

This proposal describes how to represent public keys associated with [ActivityPub] actors.

## Rationale

Historically, Fediverse services used [publicKey](https://w3c-ccg.github.io/security-vocab/#publicKey) property to represent actor's public key. Implementations usually allow only one key per actor, therefore a new approach is needed to support use cases where additional keys are required.

Furthermore, `publicKey` property was removed from the latest version of [Security Vocabulary][SecurityVocabulary].

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Multikey

Each public key MUST be represented as an object with `Multikey` type, as defined in section *2.2.2 Multikey* of [Controlled Identifiers][Multikey] specification. This object MUST have the following properties:

- `id`: the unique global identifier of the public key.
- `type`: the value of this property MUST be the string `Multikey`.
- `controller`: the value of this property MUST match actor ID.
- `publicKeyMultibase`: a [Multibase] encoded value of a [Multicodec] prefix and the key. Implementations MUST use the `base-58-btc` alphabet.

Key identifier and actor identifier SHOULD have the same [origin][FEP-fe34].

The `Multikey` object MAY contain the `expires` property indicating the expiration date of the key. Implementations MUST NOT not accept a signature created with a key that has been expired.

### Key IDs

Identifiers SHOULD be generated by appending a fragment identifier to the actor ID. Different public keys of the same actor MUST be identified using different fragment IDs.

Resolution of a URI containing a fragment identifier is performed using the algorithm specified in section *3.4 Fragment Resolution* of [Controlled Identifiers][FragmentResolution] specification.

### Key types

Implementers can use cryptographic keys of any type for which [Multicodec] prefix is registered.

## Controlled identifier document

`Multikey` objects MUST be added to the actor object, which is considered a controlled identifier document, as described in [Controlled Identifiers][ControlledIdentifiers] specification.

If the key is intended to be used for signing ActivityPub objects, it MUST be added to the [`assertionMethod`][Assertion] array in the actor object.

Other use cases are currently out of scope of this proposal.

Implementations are discouraged from adding any objects to the `assertionMethod` array that does not conform to this specification. Implementations encountering non-conformant entries in the `assertionMethod` array SHOULD ignore them.

### Example

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://www.w3.org/ns/cid/v1"
    ],
    "type": "Person",
    "id": "https://server.example/users/alice",
    "inbox": "https://server.example/users/alice/inbox",
    "outbox": "https://server.example/users/alice/outbox",
    "assertionMethod": [
        {
            "id": "https://server.example/users/alice#ed25519-key",
            "type": "Multikey",
            "controller": "https://server.example/users/alice",
            "publicKeyMultibase": "z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2"
        }
    ]
}
```

## Difference between this proposal and FEP-c390

[FEP-c390](https://codeberg.org/fediverse/fep/src/branch/main/fep/c390/fep-c390.md) describes how to link external identities to ActivityPub actor. Valid identity proof implies that actor and proof's subject are controlled by the same entity.

This proposal describes how to represent actor's public keys. The corresponding secret keys are controlled by the server.

## Test vectors

See [fep-521a.feature](./fep-521a.feature)

## Implementations

- Mitra
- streams
- Hubzilla
- Fedify

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- Ivan Herman, Manu Sporny, Dave Longley, [Security Vocabulary][SecurityVocabulary], 2023
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- Dave Longley, Manu Sporny, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Controlled Identifiers (CIDs) v1.0][ControlledIdentifiers], 2025
- Protocol Labs, [Multicodec][Multicodec]
- silverpill, [FEP-fe34: Origin-based security model][FEP-fe34], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[SecurityVocabulary]: https://w3c.github.io/vc-data-integrity/vocab/security/vocabulary.html
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[ControlledIdentifiers]: https://w3c.github.io/cid/
[Multikey]: https://w3c.github.io/cid/#Multikey
[Multibase]: https://w3c.github.io/cid/#multibase-0
[Assertion]: https://w3c.github.io/cid/#assertion
[FragmentResolution]: https://w3c.github.io/cid/#fragment-resolution
[Multicodec]: https://github.com/multiformats/multicodec/
[FEP-fe34]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
