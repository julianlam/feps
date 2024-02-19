---
slug: "ef61"
authors: silverpill <@silverpill@mitra.social>
status: DRAFT
dateReceived: 2023-12-06
discussionsTo: https://codeberg.org/fediverse/fep/issues/209
---
# FEP-ef61: Portable Objects

## Summary

Portable [ActivityPub][ActivityPub] objects with server-independent IDs.

## Motivation

Usage of HTTP(S) URLs as identifiers has a major drawback: when the server disappears, everyone who uses it loses their identities and data.

The proposed solution should satisfy the following constraints:

- User's identity and data should not be tied to a particular server.
- Users should have a choice between full control over their identity and data, and delegation of control to a trusted party.
- Implementing the solution in existing software should be as simple as possible. Changes to ActivityPub data model should be kept to a minimum.
- The solution should be compatible with existing and emerging decentralized identity and storage systems.
- The solution should be transport-agnostic.

## History

[Streams](https://codeberg.org/streams/streams) implements [Nomadic Identity](https://codeberg.org/streams/streams/src/commit/11f5174fdd3dfcd8714974f93d8b8fc50378a193/FEDERATION.md?display=source#L54-L59) mechanism, that makes identity independent from a server. Nomadic accounts are currently not supported by ActivityPub but are available via the [Nomad protocol](https://codeberg.org/streams/streams/src/commit/11f5174fdd3dfcd8714974f93d8b8fc50378a193/spec/Nomad/Home.md).

[Decentralized Identifiers (DIDs) v1.0][DID] specification suggests that DIDs might be assigned to web resources in section [B.8 Assigning DIDs to existing web resources](https://www.w3.org/TR/did-core/#assigning-dids-to-existing-web-resources).

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119][RFC-2119].

## DID URLs

ActivityPub objects can be made portable by using [DID URLs][DID URLs] for IDs instead of HTTP(S) URLs.

## did:ap

`did:ap` is a [DID][DID] method that can be used to add DID URL functionality to other types of DIDs.

### did:ap:key

`did:ap:key` method works in the same way as [did:key][did:key] method, but supports [DID URL syntax][DID URLs].

### Dereferencing DID URLs

To dereference `did:ap:key` URL, the client MUST make HTTP GET request to a resolver endpoint located at `/.well-known/apresolver` path. The client MUST specify an `Accept` header with the `application/ld+json; profile="https://www.w3.org/ns/activitystreams"` media type.

Example of a request to a resolver:

```
GET https://social.example/.well-known/apresolver/did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/path/to/object
```

ActivityPub objects identified by `did:ap:key` URLs can be stored on multiple servers simultaneously.

If object identified by `did:ap:key` URL is stored on the server, it MUST return a response with status `200 OK` containing the requested object. The response MUST have a `Link` header with `rel` parameter set to `alternate` and containing an HTTP(S) URL corresponding to a requested DID URL.

Example:

```
Link: <https://social.example/objects/did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/path/to/object>; rel="alternate"
```

If object identified by `did:ap:key` URL is not stored on a server, it MUST return `404 Not Found`.

If object is not public, `/.well-known/apresolver` MUST return `404 Not Found` unless the request has a HTTP signature and the signer is allowed to view the object.

After retrieving an object, the client MUST verify its [FEP-8b32][FEP-8b32] integrity proof. The value of `verificationMethod` property of the proof MUST match the DID component of the DID URL.

## Portable actors

An actor object identified by `did:ap:key` URL MUST contain the `aliases` property containing an up-to-date list of HTTP(S) URLs where actor object can be retrieved and it MUST contain [FEP-8b32][FEP-8b32] integrity proof.

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v1",
    {
      "fep": "https://w3id.org/fep/c390#",
      "aliases": "fep:aliases"
    }
  ],
  "type": "Person",
  "id": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor",
  "inbox": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/inbox",
  "outbox": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/outbox",
  "aliases": [
    "https://server1.example/actor",
    "https://server2.example/actor"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

### Actor IDs

When constructing ActivityPub objects, implementations SHOULD provide a list of HTTP(S) URLs where actor object can be retrieved.

The list of URLs MUST be specified using the `aliases` query parameter, URL-endcoded and separated by commas.

Example:

```
did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?aliases=https%3A%2F%2Fserver1.example%2Factor,https%3A%2F%2Fserver2.example%2Factor
```

This DID URL has two aliases:

- `https://server1.example/actor`
- `https://server2.example/actor`

Implementations MUST discard query parameters when comparing `did:ap:key` identifiers and treat identifiers with different query parameter values as equal.

### Inboxes and outboxes

Implementations obtain local addresses of inbox and outbox from a `Link` HTTP header after dereferencing corresponding DID URLs.

ActivityPub clients MUST follow [FEP-ae97][FEP-ae97] to publish activities. A client MAY deliver signed activities to multiple outboxes, located on different servers. A server SHOULD forward signed activities to outboxes located on other servers where actor's data is stored.

Upon receiving an activity in actor's inbox, server SHOULD forward it to inboxes located on other servers where actor's data is stored.

### Discovering locations

(This section is non-normative.)

This proposal makes use of the `aliases` property, but the following alternatives are being considered:

- `sameAs`
- `alsoKnownAs` (used for account migrations, so the usage of this property may cause issues)
- `url` (with `alternate` [relation type](https://html.spec.whatwg.org/multipage/links.html#linkTypes))

## Portable objects

Objects identified by `did:ap:key` URLs MUST contain [FEP-8b32][FEP-8b32] integrity proof.

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://www.w3.org/ns/credentials/v2"
  ],
  "type": "Note",
  "id": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/objects/dc505858-08ec-4a80-81dd-e6670fd8c55f",
  "attributedTo": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?aliases=https%3A%2F%2Fserver1.example%2Factor,https%3A%2F%2Fserver2.example%2Factor",
  "inReplyTo": "did:ap:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/objects/f66a006b-fe66-4ca6-9a4c-b292e33712ec",
  "content": "Hello!",
  "attachment": [
    {
      "type": "Image",
      "href": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/media/image123.png",
      "mediaType": "image/png",
      "digestMultibase": "zQmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n"
    }
  ],
  "to": [
    "did:ap:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/actor"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:ap:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

## Compatibility

(This section is non-normative.)

DID URLs are not compatible with existing [ActivityPub][ActivityPub] implementations. The following workarounds are being considered:

1. Use HTTP URL of a resolver query instead of an actual DID URL. Implementations that support DID URLs should be able to extract the DID URL from the HTTP URL and process the object accordingly.
2. Use regular HTTP URLs but include a link to a DID URL in the `url` (with `canonical` relation type, as proposed in [FEP-fffd][FEP-fffd]). For pointers to other objects such as `inReplyTo` property, an embedded object with `url` property can be used instead of a plain URL.
3. Alter object ID depending on the capabilities of the peer which can be reported by [NodeInfo][NodeInfo] or some other mechanism.

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- Dave Longley, Dmitri Zagidulin, Manu Sporny, [The did:key Method v0.7][did:key], 2022
- Manu Sporny, Dave Longley, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Decentralized Identifiers (DIDs) v1.0][DID], 2022
- silverpill, [FEP-8b32: Object Integrity Proofs][FEP-8b32], 2022
- silverpill, [FEP-ae97: Client-side activity signing][FEP-ae97], 2023
- Adam R. Nelson, [FEP-fffd: Proxy Objects][FEP-fffd], 2023
- Jonne Haß, [NodeInfo][NodeInfo], 2014

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[did:key]: https://w3c-ccg.github.io/did-method-key/
[DID]: https://www.w3.org/TR/did-core/
[DID URLs]: https://www.w3.org/TR/did-core/#did-url-syntax
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md
[FEP-ae97]: https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md
[FEP-fffd]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fffd/fep-fffd.md
[NodeInfo]: https://nodeinfo.diaspora.software/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
