---
slug: "ef61"
authors: silverpill <silverpill@firemail.cc>
status: DRAFT
dateReceived: 2023-12-06
---
# FEP-ef61: Portable Objects

## Summary

Portable [ActivityPub](https://www.w3.org/TR/activitypub/) objects with server-independent IDs.

## Motivation

Usage of HTTP(S) URLs as identifiers has a major drawback: when the server disappears, everyone who uses it loses their identities and data.

The proposed solution should satisfy the following constraints:

- User's identity and data should not be tied to a particular server.
- Users should have a choice between full control over their identity and data, and delegation of control to a trusted party.
- Implementing the solution in existing software should be as simple as possible. Changes to ActivityPub data model should be kept to a minimum.
- The solution should be compatible with existing and emerging decentralized identity and storage systems.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119](https://tools.ietf.org/html/rfc2119.html).

## DID URLs

ActivityPub objects can be made portable by using [DID URLs](https://www.w3.org/TR/did-core/#did-url-syntax) for IDs instead of HTTP(S) URLs.

## did:apkey

`did:apkey` method works in the same way as [did:key](https://w3c-ccg.github.io/did-method-key/) method, but supports [DID URL syntax](https://www.w3.org/TR/did-core/#did-url-syntax).

### Dereferencing DID URLs

To dereference `did:apkey` URL, implementations MUST use `/.well-known/apkey` endpoint.

Example of a request to `apkey` endpoint:

```
GET https://social.example/.well-known/apkey?id=did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/path/to/object
```

ActivityPub objects identified by `did:apkey` URLs can be stored on multiple servers simultaneously.

If object identified by `did:apkey` URL is stored on a server, it MUST return a response with status `200 OK` containing the requested object. The response MUST have a `Link` header with `rel` parameter set to `canonical` and containing an HTTP(S) URL corresponding to a requested DID URL.

If object identified by `did:apkey` URL is not stored on a server, it MUST return `404 Not Found`.

## Portable actors

An actor object identified by `did:apkey` URL MUST contain the `hosts` property containing an up-to-date list of servers where actor object can be retrieved and it MUST contain [FEP-8b32](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md) integrity proof.

Example:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Person",
  "id": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor",
  "inbox": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/inbox",
  "outbox": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/outbox",
  "hosts": [
    "server1.example",
    "server2.example"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

### Actor IDs

When constructing ActivityPub objects, implementations SHOULD provide a list of hosts where actor ID can be dereferenced using the `/.well-known/apkey` endpoint.

The list of hosts MUST be specified using the `hosts` query parameter:

```
did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?hosts=server1.example,server2.example
```

Implementations MUST discard query parameters when comparing `did:apkey` identifiers and treat identifiers with different `hosts` parameter values as equal.

### Inboxes and outboxes

Implementations obtain local address of inbox and outbox from a `Link` HTTP header.

ActivityPub clients MUST follow [FEP-ae97](https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md) to publish activities. A client MAY deliver signed activities to multiple outboxes, located on different servers. A server SHOULD forward signed activities to outboxes located on other servers where actor's data is stored.

Upon receiving an activity in actor's inbox, server SHOULD forward it to inboxes located on other servers where actor's data is stored.

## Portable objects

Objects identified by `did:apkey` URLs MUST contain [FEP-8b32](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md) integrity proof.

Example:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Note",
  "id": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/objects/dc505858-08ec-4a80-81dd-e6670fd8c55f",
  "attributedTo": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?hosts=server1.example,server2.example",
  "inReplyTo": "did:apkey:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/objects/f66a006b-fe66-4ca6-9a4c-b292e33712ec",
  "content": "Hello world!",
  "to": [
    "did:apkey:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/actor"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:apkey:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

### Access control

If object is not public, `/.well-known/apkey` MUST return `404 Not Found` unless the request has a HTTP signature and the signer is allowed to view the object.

## References

- [ActivityPub] Christine Lemmer Webber, Jessica Tallon, [ActivityPub](https://www.w3.org/TR/activitypub/), 2018
- [did:key] Dave Longley, Dmitri Zagidulin, Manu Sporny, [The did:key Method v0.7](https://w3c-ccg.github.io/did-method-key/), 2022
- [DID URLs] Manu Sporny, Dave Longley, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Decentralized Identifiers (DIDs) v1.0](https://www.w3.org/TR/did-core/), 2022
- [FEP-8b32] silverpill, [FEP-8b32: Object Integrity Proofs](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md), 2022
- [FEP-ae97] silverpill, [FEP-ae97: Client-side activity signing](https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md), 2023

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
