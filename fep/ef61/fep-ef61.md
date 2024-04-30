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

- User's identity and data should not be tied to a single server.
- Users should have a choice between full control over their identity and data, and delegation of control to a trusted party.
- Implementing the solution in existing software should be as simple as possible. Changes to ActivityPub data model should be kept to a minimum.
- The solution should be compatible with existing and emerging decentralized identity and storage systems.
- The solution should be transport-agnostic.

## History

[Streams](https://codeberg.org/streams/streams) implements [Nomadic Identity](https://codeberg.org/streams/streams/src/commit/5a20e0102b73a2c05e72bead13ddd712e4c2f885/FEDERATION.md#nomadic-identity) mechanism, that makes identity independent from a server. Nomadic accounts are currently not supported by ActivityPub but are available via the [Nomad protocol](https://codeberg.org/streams/streams/src/commit/11f5174fdd3dfcd8714974f93d8b8fc50378a193/spec/Nomad/Home.md).

[Decentralized Identifiers (DIDs) v1.0][DID] specification suggests that DIDs might be assigned to web resources in section [B.8 Assigning DIDs to existing web resources](https://www.w3.org/TR/did-core/#assigning-dids-to-existing-web-resources).

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119][RFC-2119].

## Identifiers

An [ActivityPub][ActivityPub] object can be made portable by using an identifier that is not tied to a single server. This proposal describes a new identifier type that has this property and is compatible with the [ActivityPub] specification.

### ap:// URLs

`ap://` URL is constructed according to the [URI][RFC-3986] specification, but with a [Decentralized Identifier][DID] in place of the authority:

```text
ap://did:example:123456/path/to/object?name=value#key-id
\_/  \________________/ \____________/ \________/ \____/
 |           |                |            |        |
scheme   authority           path        query   fragment
```

- The URI scheme MUST be `ap`.
- The authority component MUST be a valid [DID].
- The path is REQUIRED.
- The query and the fragment are OPTIONAL.

### DID methods

Implementers MUST support the [did:key] method and MAY support the [did:web] method.

Other DID methods SHOULD NOT be used. Any [DID URL][DID-URL] capabilities of a DID method MUST be ignored when working with `ap://` URLs.

### Dereferencing ap:// URLs

To dereference an `ap://` URL, the client MUST make HTTP GET request to a gateway endpoint at [well-known] location `/.well-known/apgateway`. The `ap://` prefix MUST be removed from the URL and the rest of it appened to a gateway URL. The client MUST specify an `Accept` header with the `application/ld+json; profile="https://www.w3.org/ns/activitystreams"` media type.

Example of a request to a gateway:

```
GET https://social.example/.well-known/apgateway/did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/path/to/object
```

ActivityPub objects identified by `ap://` URLs can be stored on multiple servers simultaneously.

If object identified by `ap://` URL is stored on the server, it MUST return a response with status `200 OK` containing the requested object.

If object identified by `ap://` URL is not stored on the server, it MUST return `404 Not Found`.

If object is not public, the server MUST return `404 Not Found` unless the request has a HTTP signature and the signer is allowed to view the object.

After retrieving an object, the client MUST verify its [FEP-8b32][FEP-8b32] integrity proof. The value of `verificationMethod` property of the proof MUST match the authority component of the `ap://` URL.

## Portable actors

An actor object identified by `ap://` URL MUST have the `gateways` property containing an ordered list of gateways where the latest version of that actor object can be retrieved. Each item in the list MUST be an HTTP(S) [origin](https://developer.mozilla.org/en-US/docs/Glossary/Origin), and the list MUST contain at least one item.

An actor object identified by `ap://` URL MUST contain an [FEP-8b32][FEP-8b32] integrity proof.

One identity (represented by [DID]) can control multiple actors (which are differentiated by the path component of an `ap://` URL).

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v1",
    {
      "gateways": {
        "@id": "https://w3id.org/fep/ef61/gateways",
        "@type": "@id",
        "@container": "@list"
      }
    }
  ],
  "type": "Person",
  "id": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor",
  "inbox": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/inbox",
  "outbox": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/outbox",
  "gateways": [
    "https://server1.example",
    "https://server2.example"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

### Location hints

When ActivityPub object containing a reference to another actor is being constructed, implementations SHOULD provide a list of gateways where specified actor object can be retrieved. This list MAY be provided using the `gateways` query parameter. Each gateway address MUST be URL-endcoded, and if multiple addresses are present they MUST be separated by commas.

Example:

```
ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?gateways=https%3A%2F%2Fserver1.example,https%3A%2F%2Fserver2.example
```

This URL indicates that object can be retrieved from two gateways:

- `https://server1.example`
- `https://server2.example`

Implementations MUST discard query parameters when comparing `ap://` identifiers and treat identifiers with different query parameter values as equal.

### Inboxes and outboxes

Servers and clients MUST use gateways to deliver activities to inboxes or outboxes. Servers specified in the `gateways` property of an actor object MUST accept POST requests to respective gateway URLs.

Example:

```
POST https://social.example/.well-known/apgateway/did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor/inbox
```

If a server does not accept deliveries on behalf of an actor, it MUST return `405 Method Not Allowed`.

ActivityPub clients MAY follow [FEP-ae97][FEP-ae97] to publish activities. In this case, the client MAY deliver signed activity to multiple outboxes, located on different servers.

Upon receiving an activity in actor's outbox, server SHOULD forward it to outboxes located on other servers where actor's data is stored.

Upon receiving an activity in actor's inbox, server SHOULD forward it to inboxes located on other servers where actor's data is stored.

## Portable objects

Objects identified by `ap://` URLs MUST contain [FEP-8b32][FEP-8b32] integrity proof.

Example:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/data-integrity/v1",
    {
      "digestMultibase": {
        "@id": "https://w3id.org/security#digestMultibase",
        "@type": "https://w3id.org/security#multibase"
      }
    }
  ],
  "type": "Note",
  "id": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/objects/dc505858-08ec-4a80-81dd-e6670fd8c55f",
  "attributedTo": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/actor?gateways=https%3A%2F%2Fserver1.example,https%3A%2F%2Fserver2.example",
  "inReplyTo": "ap://did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/objects/f66a006b-fe66-4ca6-9a4c-b292e33712ec",
  "content": "Hello!",
  "attachment": [
    {
      "type": "Image",
      "href": "ap://did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2/media/image123.png",
      "mediaType": "image/png",
      "digestMultibase": "zQmdfTbBqBPQ7VNxZEYEj14VmRuZBkqFbiwReogJgS1zR1n"
    }
  ],
  "to": [
    "ap://did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK/actor"
  ],
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "created": "2023-02-24T23:36:38Z",
    "verificationMethod": "did:key:z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2",
    "proofPurpose": "assertionMethod",
    "proofValue": "..."
  }
}
```

## Compatibility

`ap://` URLs might not be compatible with existing [ActivityPub][ActivityPub] implementations. To provide backward compatibility, gateway-based HTTP(S) URLs of objects can be used instead of their actual `ap://` identifiers.

Publishers MUST use the first gateway from actor's `gateways` list when constructing compatible identifiers. Consuming implementations that support `ap://` URLs MUST remove the part of the URL preceding `did:` and re-construct the canonical `ap://` identifier.

Publishers MUST NOT add the `gateways` query parameter to object IDs if compatible identifiers are used.

## Discussion

### did:ap URLs

An alternative to the `ap://` URL scheme could be a new DID method providing [DID URL syntax][DID-URL]. Example: `did:ap:example:123456/path/to/object`.

### Discovering locations

This proposal makes use of the `gateways` property, but the following alternatives are being considered:

- `aliases` and [`sameAs`](https://schema.org/sameAs) (containing HTTP(S) URLs of objects)
- `alsoKnownAs` (used for account migrations, so the usage of this property may cause issues)
- `url` (with `alternate` [relation type](https://html.spec.whatwg.org/multipage/links.html#linkTypes))

### Media

Gateways can be used to retrieve media (by content hash):

```
https://social.example/.well-known/apgateway/urn:sha256:11a8c27212f7bbc47a952494581f3bc92e84883ac343cd11a1e4f8eaa1254f4b
```

### Compatibility

The following alternatives to gateway URLs are being considered:

1. Use regular HTTP(S) URLs but specify the canonical `ap://` URL using the `url` property (with `canonical` relation type, as proposed in [FEP-fffd][FEP-fffd]). For pointers to other objects such as `inReplyTo` property, an embedded object with `url` property can be used instead of a plain URL.
2. Alter object ID depending on the capabilities of the peer (which can be reported by [NodeInfo][NodeInfo] or some other mechanism).

## Implementations

TBD

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- T. Berners-Lee, R. Fielding, L. Masinter, [Uniform Resource Identifier (URI): Generic Syntax][RFC-3986], 2005
- Manu Sporny, Dave Longley, Markus Sabadello, Drummond Reed, Orie Steele, Christopher Allen, [Decentralized Identifiers (DIDs) v1.0][DID], 2022
- Dave Longley, Dmitri Zagidulin, Manu Sporny, [The did:key Method v0.7][did:key], 2022
- Christian Gribneau, Michael Prorock, Orie Steele, Oliver Terbu, Mike Xu, Dmitri Zagidulin, [did:web Method Specification][did:web], 2023
- M. Nottingham, [Well-Known Uniform Resource Identifiers (URIs)][well-known], 2019
- silverpill, [FEP-8b32: Object Integrity Proofs][FEP-8b32], 2022
- silverpill, [FEP-ae97: Client-side activity signing][FEP-ae97], 2023
- Adam R. Nelson, [FEP-fffd: Proxy Objects][FEP-fffd], 2023
- Jonne Haß, [NodeInfo][NodeInfo], 2014

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RFC-2119]: https://datatracker.ietf.org/doc/html/rfc2119.html
[RFC-3986]: https://datatracker.ietf.org/doc/html/rfc3986.html
[DID]: https://www.w3.org/TR/did-core/
[did:key]: https://w3c-ccg.github.io/did-method-key/
[did:web]: https://w3c-ccg.github.io/did-method-web/
[DID-URL]: https://www.w3.org/TR/did-core/#did-url-syntax
[well-known]: https://datatracker.ietf.org/doc/html/rfc8615
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md
[FEP-ae97]: https://codeberg.org/fediverse/fep/src/branch/main/fep/ae97/fep-ae97.md
[FEP-fffd]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fffd/fep-fffd.md
[NodeInfo]: https://nodeinfo.diaspora.software/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
