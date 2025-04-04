---
slug: "044f"
authors: Claire <claire.fep-1d7d@sitedethib.com>
status: DRAFT
dateReceived: 2025-04-03
discussionsTo: https://socialhub.activitypub.rocks/t/pre-fep-quote-posts-quote-policies-and-quote-controls/5031
---

# FEP-044f: Consent-respecting quote posts

## Summary

This is a work-in-progress document describing Mastodon's proposed way of representing quote posts, users' choices regarding whether their posts can be quoted and by whom (quote policies), and a mechanism for servers to verify compliance with such policies.

This document describes protocol considerations, which do not necessarily translate directly to User Experience considerations. For instance, the use of the approval mechanism described in this document does not imply that the user's approval is manual.

## Requirements

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this specification are to be interpreted as described in [RFC-2119].

In the remaining of this document, “quoted object” refers to the object being quoted, “original author” to its author, and “quote post” refers to the object quoting the “quoted object”.

## Acknowledgments

(This section is non-normative.)

This proposal has benefitted from significant discussions on SocialHub as well as discussions with _trwnh_ and [GoToSocial](https://gotosocial.org/) developers. In fact, the `interactionPolicy` vocabulary directly comes from [GoToSocial's interaction policies](https://docs.gotosocial.org/en/latest/federation/interaction_policy/) which have since evolved along the current proposal.

## Representation of a quote post

A “quote post” is represented as an object with an Object Link (FEP-e232) to a “quoted object” using `https://misskey-hub.net/ns#_misskey_quote` as a link relation.

### Example

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Note",
  "id": "https://example.com/users/bob/statuses/1",
  "attributedTo": "https://example.com/users/bob",
  "to": [
    "https://www.w3.org/ns/activitystreams#Public",
    "https://example.com/users/alice"
  ],
  "content": "I am quoting alice's post<span class=\"quote-inline\"><br/>RE: <a href=\"https://example.com/users/alice/statuses/1\">https://example.com/users/alice/statuses/1</a></span>",
  "tag": [
    {
      "type": "Link",
      "mediaType": "application/ld+json; profile=\"https://www.w3.org/ns/activitystreams\"",
      "href": "https://example.com/users/alice/statuses/1",
      "rel": "https://misskey-hub.net/ns#_misskey_quote",
    }
  ]
}
```

This example is non-normative, and the `<span class=\"quote-inline\"><br/>RE: <a href=\"https://example.com/users/alice/statuses/1\">https://example.com/users/alice/statuses/1</a></span>` part of the content is an example of textual fallback, but does not otherwise carry meaning. In particular, it does not influence where the embedded quote should be displayed.

## Advertising a quote policy

Users may not want their posts to be quoted, or not by everyone. To allow users to express that, we re-use GoToSocial's interaction policies and define a `canQuote` sub-policy.

Each quotable object advertises an `interactionPolicy` (`https://gotosocial.org/ns#interactionPolicy`) with a `canQuote` (`https://gotosocial.org/ns#canQuote`) sub-policy.

A sub-policy is defined by two attributes:
- `automaticApproval` (`https://gotosocial.org/ns#automaticApproval`): an array of `Actor` and `Collection` of `Actor` objects from whom interactions are expected to be automatically approved
- `manualApproval` (`https://gotosocial.org/ns#manualApproval`): an array of `Actor` and `Collection` of `Actor` objects from whom interactions are subject to manual review

Interactions from actors that are neither in `automaticApproval` nor `manualApproval` are expected to never be approved.

To advertise a policy of disallowing all quotes, `interactionPolicy.canQuote.automaticApproval` SHOULD contain the object author's identifier as its single value. This is because an empty array is equivalent to a missing property under JSON-LD canonicalization.

`automaticApproval` and `manualApproval` SHOULD be restricted to individual actors, the special public collection `https://www.w3.org/ns/activitystreams#Public`, the author's `followers` collection, and the author's `following` collection.

Note that the policy is entirely advisory. It SHOULD be used to provide user interface hints such as enabling a “Quote” button or explaining why an object cannot be quoted, but it MUST NOT be used to verify whether a quote post is valid.
See later sections for the actual verification mechanism.

### Example

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "gts": "https://gotosocial.org/ns#",
      "interactionPolicy": {
        "@id": "gts:interactionPolicy",
        "@type": "@id"
      },
      "canQuote": {
        "@id": "gts:canQuote",
        "@type": "@id"
      },
      "automaticApproval": {
        "@id": "gts:automaticApproval",
        "@type": "@id"
      }
    }
  ],
  "interactionPolicy": {
    "canQuote": {
      "automaticApproval": "https://example.com/users/alice/followers"
    }
  },
  "type": "Note",
  "id": "https://example.com/users/alice/statuses/1",
  "attributedTo": "https://example.com/users/alice",
  "to": "https://www.w3.org/ns/activitystreams#Public",
  "content": "I allow my followers to quote this post"
}
```

## Approval stamps

In order to enforce a policy, we rely on approval stamps, a mechanism used to tell third-party servers that a quote is approved, regardless of the current state of the policy.

Quote approval stamps are objects of the type `QuoteAuthorization` (`http://joinmastodon.org/ns#QuoteAuthorization`), with `interactingObject` (`https://gotosocial.org/ns#interactingObject`), `interactionTarget` (`https://gotosocial.org/ns#interactionTarget`) and `attributedTo` attributes.

The `interactingObject` attribute MUST reference the accepted quote post, the `interactionTarget` attribute MUST reference the quoted object, and the `attributedTo` attribute MUST correspond to the author of the quoted object.

A `QuoteAuthorization` object MUST be dereferenceable by all parties allowed to see the original post, and MAY be publicly dereferenceable. It MUST NOT embed its `interactingObject` as to avoid possible information leaks. For the same reason, it MUST NOT embed its `interactionTarget` object if the server is unable to verify that the party dereferencing the object has permission to see the quoted object.

When a third-party attempts to dereference the `QuoteAuthorization`, the `interactionTarget` MAY be inlined if the third-party has permission to access the quoted object. This is so that the third-party does not have to perform a second request to access the quoted object.

### Example of `QuoteAuthorization`

The following stamp can be used to prove that actor `https://example.com/users/alice` has accepted `https://example.org/users/bob/statuses/1` as a quote of her post `https://example.com/users/alice/statuses/1`:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "toot": "http://joinmastodon.org/ns#",
      "QuoteAuthorization": "toot:QuoteAuthorization",
      "gts": "https://gotosocial.org/ns#",
      "interactingObject": {
        "@id": "gts:interactingObject",
        "@type": "@id"
      },
      "interactionTarget": {
        "@id": "gts:interactionTarget",
        "@type": "@id"
      }
    }
  ],
  "type": "QuoteAuthorization",
  "id": "https://example.com/users/alice/stamps/1",
  "attributedTo": "https://example.com/users/alice",
  "interactingObject": "https://example.org/users/bob/statuses/1",
  "interactionTarget": "https://example.com/users/alice/statuses/1"
}
```

### Verifying a `QuoteAuthorization`

To be considered valid for a particular quote post, a `QuoteAuthorization` MUST satisfy the following properties:
- its `interactingObject` is the quote post under consideration
- its `interactionTarget` property is the quoted object
- its `attributedTo` property is the author of its `interactionTarget`
- the authenticity of the `QuoteAuthorization` object can be asserted

### Revoking a `QuoteAuthorization`

An approval stamp can be revoked by `Delete`ing the stamp.

## `QuoteRequest` request activity

The `QuoteRequest` (`http://joinmastodon.org/ns#QuoteRequest`) activity type is introduced to request approval for a quote post.

The `QuoteRequest` activity uses the `object` property to refer to the quoted object, and the `instrument` property to refer to the quote post.

### Example `QuoteRequest` activity

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "toot": "http://joinmastodon.org/ns#",
      "QuoteRequest": "toot:QuoteRequest"
    }
  ],
  "type": "QuoteRequest",
  "id": "https://example.com/users/bob/statuses/1/quote",
  "actor": "https://example.com/users/bob",
  "object": "https://example.com/users/alice/statuses/1",
  "instrument": {
    "type": "Note",
    "id": "https://example.com/users/bob/statuses/1",
    "attributedTo": "https://example.com/users/bob",
    "to": [
      "https://www.w3.org/ns/activitystreams#Public",
      "https://example.com/users/alice"
    ],
    "content": "I am quoting alice's post<br/>RE: https://example.com/users/alice/statuses/1",
    "tag": [
      {
        "type": "Link",
        "mediaType": "application/ld+json; profile=\"https://www.w3.org/ns/activitystreams\"",
        "href": "https://example.com/users/alice/statuses/1",
        "rel": "https://misskey-hub.net/ns#_misskey_quote",
      }
    ]
  }
}
```

## Receiving, accepting or rejecting quote posts

When receiving a `QuoteRequest` activity, the original author decides (either manually or automatically) whether the quote is acceptable. Software that automatically accepts quotes on the author's behalf should notify the author of such quotes according to their notification settings.

The receiving end MAY inspect the `instrument` of the `QuoteRequest` itself to decide whether it is acceptable.

If the quote post is considered acceptable, the original author MUST reply with an `Accept` activity with the `QuoteRequest` activity as its object, and a `QuoteAuthorization` as its `result`.

If the quote post is considered unacceptable, the authority SHOULD reply with a `Reject` activity with the `QuoteRequest` activity as its object.

### Example `Accept`

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "toot": "http://joinmastodon.org/ns#",
      "QuoteRequest": "toot:QuoteRequest"
    }
  ],
  "type": "Accept",
  "to": "https://example.com/users/bob",
  "id": "https://example.com/users/alice/activities/1234",
  "actor": "https://example.com/users/alice",
  "object": {
    "type": "QuoteRequest",
    "id": "https://example.com/users/bob/statuses/1/quote",
    "actor": "https://example.com/users/bob",
    "object": "https://example.com/users/alice/statuses/1",
    "instrument": "https://example.org/users/bob/statuses/1"
  },
  "result": "https://example.com/users/alice/stamps/1"
}
```

### Example `Reject`

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "toot": "http://joinmastodon.org/ns#",
      "Quote": "toot:QuoteRequest"
    }
  ],
  "type": "Reject",
  "to": "https://example.com/users/bob",
  "id": "https://example.com/users/alice/activities/1234",
  "actor": "https://example.com/users/alice",
  "object": {
    "type": "QuoteRequest",
    "id": "https://example.com/users/bob/statuses/1/quote",
    "actor": "https://example.com/users/bob",
    "object": "https://example.com/users/alice/statuses/1",
    "instrument": "https://example.org/users/bob/statuses/1"
  }
}
```

## Requesting, obtaining and validating approval

In order to get approval, the quote post author MUST send a `QuoteRequest` (`http://joinmastodon.org/ns#QuoteRequest`) activity to the author of the quoted object, with the quoted object as its `object` property and the quote post as its `instrument`.

The quote post SHOULD be inlined in the `instrument` property and, if not, it SHOULD dereferenceable by the recipient at this point, as the author of the quoted object may want to inspect it to decide whether to accept the quote.

The quote post author MAY wait until they receive an `Accept` or `Reject` activity before sending the post's `Create` activity to its intended audience.
Doing so is possible for ActivityPub servers that implement the current proposal, and avoids having to issue an `Update` soon afterwards the `Create` for the quote post.
It is however not possible to implement for ActivityPub clients, which will likely need to issue a `Create` before the `QuoteRequest` activity.

### Rejection

If the author of the quote post receives a `Reject` activity from the quoted object's author to their `QuoteRequest` activity, they MUST consider the quote post to be explicitly rejected.

If the implementation waits for the `Accept` before issuing a `Create`, this MAY translate as the inability to publish the quote post.

Otherwise, it MAY translate as a `Delete` to outright remove the quote post, or an `Update` to remove the quote part from the post.

### Acceptance

If the author of the quote receives an `Accept` activity, they MUST add a reference to its `result` in the `approvedBy` property of the relevant object link.

Depending on whether they already sent a `Create` activity to the quote post's intended audience, they SHOULD send a `Create` activity or an `Update` activity with the updated `approvedBy` property.

#### Example updated `Note` object

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "gts": "https://gotosocial.org/ns#",
      "approvedBy": {
        "@id": "gts:approvedBy",
        "@type": "@id"
      }
    }
  ],
  "type": "Note",
  "id": "https://example.com/users/bob/statuses/1",
  "attributedTo": "https://example.com/users/bob",
  "to": [
    "https://www.w3.org/ns/activitystreams#Public",
    "https://example.com/users/alice"
  ],
  "content": "I am quoting alice's post<br/>RE: https://example.com/users/alice/statuses/1",
  "tag": [
    {
      "type": "Link",
      "mediaType": "application/ld+json; profile=\"https://www.w3.org/ns/activitystreams\"",
      "href": "https://example.com/users/alice/statuses/1",
      "rel": "https://misskey-hub.net/ns#_misskey_quote",
      "approvedBy": "https://example.com/users/alice/stamps/1"
    }
  ]
}
```

## Verifying third-party quote posts

When processing a quote post from a remote actor, a recipient MUST consider them unapproved unless any of those conditions apply:
- the author of the quote post and that of the original post are the same (same `attributedTo`)
- the author of the quote post is mentioned in the original post
- `approvedBy` exists, can be dereferenced and is a valid `QuoteAuthorization` activity for this object

## Revocation of a quote post

### Revoking a previously-accepted quote post

The original author may want to perform /a posteriori/ moderation of the quote posts, or block a quote poster in particular.

To do this, the original actor MUST `Delete` the `QuoteAuthorization`. They SHOULD send the `Delete` activity to the quote post's author and any recipient it has reasons to think has accessed the quote post.

The original author MUST NOT embed the `object` nor the `target` of the `QuoteAuthorization`, so as to avoid potential information leakage.

### Handling a revocation

Upon receiving a `Delete` activity for a previously-verified `QuoteAuthorization`, third-parties MUST check that the `Delete` is valid and MUST subsequently consider the quote post unapproved.

Additionally, if the recipient owns the quote post, it MUST forward the `Delete` to the audience of the quote post.

## Opportunistic re-verification of quote approvals

Because getting revocation properly forwarded depends on the good will of the revoked post's author, it may be necessary to have other means of checking whether an approval has been revoked.

For this reason, recipients SHOULD re-check the `approvedBy` document when an already-known quote post is accessed for the first time in a given period of time.

## Server behavior considerations

This proposal has been made with great care to not require new server behavior, allowing ActivityPub clients to implement this proposal without requiring generic ActivityPub server software to implement additional logic.

In particular, this is the reason the approval stamp is a separate object rather than the `Accept` itself. Indeed, nothing in the ActivityPub specification would cause a `Reject` or `Undo` activity to invalidate the `Accept` activity itself, which means it would not be suitable as an approval stamp.
While ActivityPub does not technically forbid `Accept` activities to be the target of a `Delete` activity, we have found no precedent for that, and we anticipate that deleting activities might not be correctly handled across the fediverse.
For this reason, we opted to use a separate object that can be directly managed by an ActivityPub client, for instance by issuing a `Create` activity ahead of sending the `Accept` activity, and that can be deleted with the usual mechanism.

An alternative approach we considered is using a dedicated endpoint to check for approval of a quote. This would effectively allow externalizing approval verification to a separate mechanism, but while this would not require new server behavior, this would still require a new server component to be specified, which is why we opted for the mechanism described in this specification instead.

## Backward compatibility considerations

(This section is non-normative.)

To clients that do not implement this FEP, quote posts are seen as regular posts with no explicit relation with the quoted post. While this is preferable to having the quoted post relayed without the comment, this is still lacking significant semantic context.

Therefore, quote posts should be authored in such a way that their contents include a reference to the quoted post, e.g. by adding `<span class=\"quote-inline\"><br/>RE: <a href=\"https://example.com/users/alice/statuses/1\">https://example.com/users/alice/statuses/1</a></span>`.

Using a special class like `quote-inline` can be useful to hide redundant information information when the post is detected to have an attached quote.

## Security considerations

Servers not implementing this FEP will still be able to quote the post and provide no dogpiling-reducing friction. There is unfortunately nothing we can do about that.

Effectively revoking quote posts relies on the participation of the quote poster's server to effectively reach the audience of the quote post, so an ill-intentioned server could quote post then refuse to forward the revocation. Still, this can arise on well-intentioned servers too, so the feature remains useful. Opportunistic re-verification of quote approvals should also help.

By not adding a hash or copy of the reply in the `QuoteAuthorization` object, malicious actors could exploit this in a split horizon setting, sending different versions of the same activity to different actors. This is, however, already a concern in pretty much all contexts in ActivityPub, and enshrining that information in the `QuoteAuthorization` object would have many drawbacks:
- significantly more complex implementation
- inability to change the JSON-LD representation after the fact
- possibly leaking private information if the `QuoteAuthorization` object is publicly dereferenceable


## Implementations

None so far.

## References

- [RFC-2119] S. Bradner, [Key words for use in RFCs to Indicate Requirement Levels](https://tools.ietf.org/html/rfc2119.html)


## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication 

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
