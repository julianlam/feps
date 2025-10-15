---
slug: "8b32"
authors: silverpill <@silverpill@mitra.social>
type: implementation
status: DRAFT
dateReceived: 2022-11-12
trackingIssue: https://codeberg.org/fediverse/fep/issues/29
discussionsTo: https://socialhub.activitypub.rocks/t/fep-8b32-object-integrity-proofs/2725
---
# FEP-8b32: Object Integrity Proofs

## Summary

This proposal describes how [ActivityPub][ActivityPub] servers and clients could create self-authenticating activities and objects.

HTTP signatures are often used for authentication during server-to-server interactions. However, this ties authentication to activity delivery, and limits the flexibility of the protocol.

Integrity proofs are sets of attributes that represent digital signatures and parameters required to verify them. These proofs can be added to any activity or object, allowing recipients to verify the identity of the actor and integrity of the data. That decouples authentication from the transport, and enables various protocol improvements such as activity relaying, embedded objects and client-side signing.

## History

Mastodon supports Linked Data signatures [since 2017](https://github.com/mastodon/mastodon/pull/4687), and a number of other platforms added support for them later. These signatures are similar to integrity proofs, but are based on outdated [Linked Data Signatures 1.0](https://github.com/w3c-ccg/ld-signatures/) specification, which has been superseded by other standards.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119][RFC-2119].

## Integrity proofs

The proposed authentication mechanism is based on [Data Integrity][DataIntegrity] specification.

### Proof generation

The proof MUST be created according to the *Data Integrity* specification, section [4.2 Add Proof][DI-AddProof].

The process of proof generation consists of the following steps:

- **Canonicalization** is a transformation of a JSON object into the form suitable for hashing, according to some deterministic algorithm.
- **Hashing** is a process that calculates an identifier for the transformed data using a cryptographic hash function.
- **Signature generation** is a process that calculates a value that protects the integrity of the input data from modification.

The resulting proof is added to the original JSON object under the key `proof`. Objects SHOULD NOT contain more than one integrity proof.

The list of attributes used in integrity proof is defined in *Data Integrity* specification, section [2.1 Proofs][DI-Proofs]. The proof type SHOULD be `DataIntegrityProof`, as specified in section [3.1 DataIntegrityProof][DI-DataIntegrityProof]. The value of `proofPurpose` attribute MUST be `assertionMethod`.

The value of the `verificationMethod` attribute of the proof can be an HTTP(S) URI or a [DID URL][DID-URL].

The [controlled identifier document][ControlledIdentifiers] where the verification method is expressed MUST be an actor object or a [DID][DIDs] document that is provably associated with an [ActivityPub] actor (e.g. using a mechanism described in [FEP-c390] or [FEP-ef61]). The verification method MUST be associated with the `assertionMethod` property of the controlled identifier document. If controlled identifier document is an actor object, implementers SHOULD use `assertionMethod` property as described in [FEP-521a].

### Proof verification

Recipients of an object SHOULD perform proof verification if it contains integrity proofs. Verification process MUST follow the *Data Integrity* specification, section [4.4 Verify Proof][DI-VerifyProof]. It starts with the removal of the `proof` value from the JSON object. Then verification method is retrieved from the controlled identifier document as described in *Controlled Identifiers* specification, section [3.3 Retrieve Verification Method][CI-RetrieveMethod]. Then the object is canonicalized, hashed and signature verification is performed according to the parameters specified in the proof.

The subject of the controlled identifier document where the verification method is expressed MUST be the [owner][FEP-fe34-Owner] of the signed object, or a [DID][DIDs] that is provably associated with that actor (e.g. using a mechanism described in [FEP-c390] or [FEP-ef61]).

If both HTTP signature and integrity proof are used, the integrity proof MUST be given precedence over HTTP signature. The HTTP signature MAY be dismissed.

### Algorithms

Implementers are expected to pursue broad interoperability when choosing algorithms for integrity proofs.

[eddsa-jcs-2022][eddsa-jcs-2022] cryptosuite is RECOMMENDED:

- Canonicalization: [JCS][JCS]
- Hashing: SHA-256
- Signatures: EdDSA

### Backward compatibility

Integrity proofs and linked data signatures can be used together, as they rely on different properties (`proof` and `signature`, respectively).

If compatiblity with legacy systems is desired, the integrity proof MUST be created and inserted before the generation of the linked data signature.

If both `proof` and `signature` are present in a received object, the linked data signature MUST be removed before the verification of the integrity proof.

### Security considerations

Implementers using integrity proofs as an authentication mechanism are advised to follow the recommendations given in [FEP-fe34: Origin-based security model][FEP-fe34].

### Privacy considerations

If a private object is signed, its authenticity can be proven if it is distributed beyond the intended recipients. This risk can be mitigated by encrypting private content.

## Examples

### Signed object

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v2"
  ],
  "id": "https://server.example/objects/1",
  "type": "Note",
  "attributedTo": "https://server.example/users/alice",
  "content": "Hello world",
  "proof": {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/data-integrity/v2"
    ],
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "verificationMethod": "https://server.example/users/alice#ed25519-key",
    "proofPurpose": "assertionMethod",
    "proofValue": "...",
    "created": "2023-02-24T23:36:38Z"
  }
}
```

### Signed activity

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v2"
  ],
  "id": "https://server.example/activities/1",
  "type": "Create",
  "actor": "https://server.example/users/alice",
  "object": {
    "id": "https://server.example/objects/1",
    "type": "Note",
    "attributedTo": "https://server.example/users/alice",
    "content": "Hello world"
  },
  "proof": {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/data-integrity/v2"
    ],
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "verificationMethod": "https://server.example/users/alice#ed25519-key",
    "proofPurpose": "assertionMethod",
    "proofValue": "...",
    "created": "2023-02-24T23:36:38Z"
  }
}
```

### Signed activity with embedded signed object

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v2"
  ],
  "id": "https://server.example/activities/1",
  "type": "Create",
  "actor": "https://server.example/users/alice",
  "object": {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/data-integrity/v2"
    ],
    "id": "https://server.example/objects/1",
    "type": "Note",
    "attributedTo": "https://server.example/users/alice",
    "content": "Hello world",
    "proof": {
      "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/data-integrity/v2"
      ],
      "type": "DataIntegrityProof",
      "cryptosuite": "eddsa-jcs-2022",
      "verificationMethod": "https://server.example/users/alice#ed25519-key",
      "proofPurpose": "assertionMethod",
      "proofValue": "...",
      "created": "2023-02-24T23:36:38Z"
    }
  },
  "proof": {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/data-integrity/v2"
    ],
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "verificationMethod": "https://server.example/users/alice#ed25519-key",
    "proofPurpose": "assertionMethod",
    "proofValue": "...",
    "created": "2023-02-24T23:36:38Z"
  }
}
```

## Test vectors

- [fep-8b32.feature](./fep-8b32.feature)
- [eddsa-jcs-2022 test vectors][eddsa-jcs-2022-test]

## Implementations

- [Mitra](https://codeberg.org/silverpill/mitra/src/commit/f096ed54e350f4a0121289bcc0d1d5f83b5bbf8b/FEDERATION.md#object-integrity-proofs)
- Vervis
  ([generation](https://codeberg.org/ForgeFed/Vervis/commit/e8e587af26944d3ea8d91f5c47cc3058cf261387),
  [verification](https://codeberg.org/ForgeFed/Vervis/commit/621275e25762a1c1e5860d07a6ff87b147deed4f))
- Streams
- [Hubzilla](https://hub.somaton.com/channel/mario?mid=4214a375-3a18-4acb-b546-75c6c4818e2f)
- [Fedify](https://todon.eu/users/hongminhee/statuses/112638238338153870)
- [apsig](https://github.com/AmaseCocoa/apsig/blob/af7af0e106132a51356fc92ed034b1152a1caea8/docs/proof.md)
- [tootik](https://github.com/dimkr/tootik/blob/v0.19.0/FEDERATION.md#data-portability)
- Gush! ([commit](https://codeberg.org/gush/gush/commit/98c04c8d5cb3528b01eaf6949ec76584c9798ccb))

## Use cases

- [Forwarding from inbox](https://www.w3.org/TR/activitypub/#inbox-forwarding)
- [Conversation Containers](https://codeberg.org/streams/streams/src/commit/e3c83c46376f446013cd95f97381e8a146a09810/doc/develop/en/Containers.mc)
- [FEP-ef61: Portable Objects](https://codeberg.org/fediverse/fep/src/branch/main/fep/ef61/fep-ef61.md)
- [FEP-ae97: Client-side activity signing](https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md)

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- Dave Longley, Manu Sporny, [Verifiable Credential Data Integrity 1.0][DataIntegrity], 2024
- Manu Sporny, Dave Longley, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Decentralized Identifiers (DIDs) v1.0][DIDs], 2022
- Dave Longley, Manu Sporny, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Controlled Identifiers v1.0][ControlledIdentifiers], 2025
- silverpill, [FEP-521a: Representing actor's public keys][FEP-521a], 2023
- silverpill, [FEP-c390: Identity Proofs][FEP-c390], 2022
- silverpill, [FEP-ef61: Portable Objects][FEP-ef61], 2023
- Dave Longley, Manu Sporny, [Data Integrity EdDSA Cryptosuites v1.0][eddsa-jcs-2022], 2025
- A. Rundgren, B. Jordan, S. Erdtman, [JSON Canonicalization Scheme (JCS)][JCS], 2020
- silverpill, [FEP-fe34: Origin-based security model][FEP-fe34], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[DataIntegrity]: https://www.w3.org/TR/vc-data-integrity/
[DI-Proofs]: https://www.w3.org/TR/vc-data-integrity/#proofs
[DI-AddProof]: https://www.w3.org/TR/vc-data-integrity/#add-proof
[DI-DataIntegrityProof]: https://www.w3.org/TR/vc-data-integrity/#dataintegrityproof
[DI-VerifyProof]: https://www.w3.org/TR/vc-data-integrity/#verify-proof
[DIDs]: https://www.w3.org/TR/did-core/
[DID-URL]: https://www.w3.org/TR/did-core/#did-url-syntax
[ControlledIdentifiers]: https://www.w3.org/TR/cid/
[CI-RetrieveMethod]: https://www.w3.org/TR/cid/#retrieve-verification-method
[FEP-521a]: https://codeberg.org/fediverse/fep/src/branch/main/fep/521a/fep-521a.md
[FEP-c390]: https://codeberg.org/fediverse/fep/src/branch/main/fep/c390/fep-c390.md
[FEP-ef61]: https://codeberg.org/fediverse/fep/src/branch/main/fep/ef61/fep-ef61.md
[eddsa-jcs-2022]: https://www.w3.org/TR/vc-di-eddsa/#eddsa-jcs-2022
[eddsa-jcs-2022-test]: https://www.w3.org/TR/vc-di-eddsa/#representation-eddsa-jcs-2022
[JCS]: https://www.rfc-editor.org/rfc/rfc8785
[FEP-fe34]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md
[FEP-fe34-Owner]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md#ownership

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
