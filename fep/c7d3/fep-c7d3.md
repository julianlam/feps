---
slug: "c7d3"
authors: silverpill <@silverpill@mitra.social>
status: DRAFT
dateReceived: 2024-06-04
discussionsTo: https://socialhub.activitypub.rocks/t/fep-c7d3-ownership/4292
trackingIssue: https://codeberg.org/fediverse/fep/issues/323
---
# FEP-c7d3: Ownership

## Summary

In this document we discuss the concept of ownership, as applied to [ActivityPub] objects.

## Rationale

[ActivityPub] standard does not specify authentication and authorization mechanisms.

Many implementations use `actor` and `attributedTo` properties (defined in [Activity Vocabulary][ActivityVocabulary]) to determine the validity of activities and objects. This proposal attempts to formalize the current practices and provide guidance for implementers.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Ownership

Ownership is indicated by `actor` and `attributedTo` properties.

Every activity MUST have an `actor` property, which describes the actor that performed the activity. This actor is considered the owner of the activity.

Every object (that is, not an actor and not an activity) MUST have an `attributedTo` property, which describes the actor to which the object is attributed. This actor is considered the owner of the object.

Collections MAY have an `attributedTo` property. If this property is present, the actor indicated by it is considered the owner of the collection.

>[!NOTE]
> In subsequent sections, "objects" and "activities" will be referred to as simply "objects".

## Origin

Object identifiers are grouped together into protection domains called "origins". This concept is similar to the "web origin" concept described in [RFC-6454], and origins of object IDs are computed by the same algorithm.

## Authentication

The object is considered authentic if any of the following conditions are met:

- It was fetched from the location that has the same origin as its owner's ID.
- It was delivered to inbox and the request contained a valid [HTTP signature][HttpSig] created by the owner.
- It contains a valid [FEP-8b32] integrity proof created by its owner.

If none of these conditions are met, the object MUST be discarded.

### Delivered to inbox

If the object was delivered to inbox and its authentication fails, the recipient SHOULD fetch it and repeat the authentication procedure.

### Emdedded objects

If the object is embedded within another object, it MAY be considered authentic if its owner matches the owner of the containing object. If the embedded and the containing objects have different owners, the authenticity of the embedded object MUST be verified independently either by fetching it from the server of origin, or by verifying its [FEP-8b32] integrity proof.

### Unattributed collections

Collections without an `attributedTo` property are owned by the server. Unattributed collection is considered authentic if fetched from the location that matches its ID.

## Authorization

The actor that creates the object MUST be its owner. If activity modifies or deletes the object, its owner MUST match the object's owner.

Examples:

- `Create`, `Update` and `Delete` activities, and objects indicated by their `object` property MUST have the same owner.
- `Add` and `Remove` activities, and objects indicated by their `target` property MUST have the same owner.

## Implementation notes

According to [Activity Vocabulary][ActivityVocabulary], `actor` and `attributedTo` properties can contain references to multiple actors. These scenarios are not covered by this document and implementers are expected to determine the appropriate authentication and authorization procedures on a case-by-case basis.

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- James M Snell, Evan Prodromou, [Activity Vocabulary][ActivityVocabulary], 2017
- S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC-2119], 1997
- A. Barth, [The Web Origin Concept][RFC-6454], 2011
- silverpill, [FEP-8b32: Object Integrity Proofs][FEP-8b32], 2022
- Ryan Barrett, nightpool, [ActivityPub and HTTP Signatures][HttpSig], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityVocabulary]: https://www.w3.org/TR/activitystreams-vocabulary/
[RFC-2119]: https://tools.ietf.org/html/rfc2119.html
[RFC-6454]: https://www.rfc-editor.org/rfc/rfc6454.html
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md
[HttpSig]: https://swicg.github.io/activitypub-http-signature/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
