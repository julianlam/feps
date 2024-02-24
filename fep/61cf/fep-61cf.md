---
slug: "61cf"
authors: FenTiger <@FenTiger@zotum.net>
status: DRAFT
dateReceived: 2024-02-06
discussionsTo: https://codeberg.org/fediverse/fep/issues/263
---
# FEP-61cf: The OpenWebAuth Protocol

## Summary

OpenWebAuth is the "single sign-on" mechanism used by Hubzilla, (streams) and other related projects. It allows a browser-based user to log in to services across the Fediverse using a single identity. Once logged in, they can be recognised by other OpenWebAuth-compatible services, without third-party cookies and often without any explicit user interaction.

This is not a specification, a proposal, or a "best practice" document. The aim is to describe the existing protocol in detail as an aid to implementers, evaluators, and anyone who wants to understand its operation. It is mostly based on reverse-engineering the existing implementations and focuses on the minimal requirements for basic interoperability.

In OpenWebAuth, each user is identified by a public/private key pair. The protocol relies on there being a mechanism for other nodes on the network to discover a user's public key. This document assumes that ActivityPub actor objects will be used for this purpose. OpenWebAuth can also work with other protocols such as Zot6 and Nomad but these are not considered here.

## Operation of the protocol

The protocol takes place between two participants:

 - The _home instance_, which hosts the user's identity, and is equivalent to the Identity Provider (IdP) in SAML and OpenID Connect.

 - The _target instance_, which allows remote users to log in to it using the provided identity. This is equivalent to the Relying Party (RP) in SAML and OpenID Connect.

The OpenWebAuth login flow can begin in one of two ways:

- The user visits the target instance and sees a login screen. They type their Fediverse ID into a form field and click "Login".

- The user follows a link to the target instance. This link has a query parameter, `zid=`, which specifies the user's Fediverse ID.

Either way, the protocol begins with the user's browser making a request to the target instance.

1. The target instance constructs a URL of the form

   `https://home-instance.example/magic?owa=1&bdest=<destination URL>`

The parts of this URL are:

  - Scheme: Must be HTTPS
  - Hostname: The same as the hostname portion of the user's ID
  - Path: Must be `/magic`
  - Query parameters:
      - `owa`: must be set to 1
      - `bdest`: The URL that the user is trying to visit. This is encoded as UTF-8 and then converted to a hexadecimal string.

The user's browser is redirected to this URL.

2. The `/magic` endpoint at the user's home instance first checks that the user is logged in.

If so, it decodes the `bdest` destination URL. It performs a webfinger lookup on the root URL of the destination site and looks for a link with `rel` set to `http://purl.org/openwebauth/v1`. This identifies the target instance's "token endpoint".

The home instance constructs and issues a signed HTTPS request to this endpoint. This request must have an `Authorization` header starting with the word `Signature` followed by the encoded HTTP signature. The `keyId` property of the signature points to the public key in the user's ActivityPub actor record. The request also contains an additional signed header, `X-Open-Web-Auth`, containing a random string. Target instances do not use this header; it is provided to add additional entropy to the signature calculation.

3. The target instance's token endpoint extracts the `keyId`, fetches the actor record, extracts the public key and verifies the signature.

On success, it generates an URL-safe random string to use as a token. This token is stored locally, associated with the actor who signed the message. The token is also encrypted using the actor's public key and the RSA PKCS #1 v1.5 encryption scheme. The encrypted result is encoded as URL-safe Base64 with no '=' padding bytes.

Next it constructs the following JSON object in response:

```
{
   "success": true,
   "encrypted_token": <the base64-encoded token>
}
```

On failure it can also return a result with `success` set to false.

4. The signed request issued in step 2 completes. The home instance decodes the JSON response and verifies that `success` is true. Next it decodes the Base64-encoded encrypted token and decrypts it using the actor's private key.

If successful, it takes the original `bdest` destination URL, adds the query parameter: `owt=<decrypted token>`, and redirects the user's browser to it.

5. The user arrives back at the target instance. The target instance sees the `owt=` query parameter and checks its local storage for the token which it saved in step 3.

If found, this token identifies the remote user, and the target instance logs them in, overriding any existing login they may have. The token is also deleted from local storage so that it cannot be redeemed more than once.

## Additional notes

### Target instance's login check

To support logged in users, the target instance needs some logic to identify their requests. Normally this is done by checking for a valid session cookie. To support OpenWebAuth this logic must be extended to also check for the `zid=` and `owt=` query parameters.

Some corner cases are possible here. For instance, the user could already be logged in to the target instance when the OWA login flow begins.

When the OpenWebAuth flow succeeds, the `owt=` query parameter will identify the user who is logged in to the home instance. This will be a user from the domain in the original `zid=` parameter, but may not be the exact same user.

### Target instance's token endpoint

This endpoint should accept both GET and POST requests. Some home instances will issue POSTs with random bodies.

### Home instance's `/magic` endpoint

The implementation of this endpoint needs to request a login token from the target instance. This requires it to prove possession of the user's private key, first to calculate a signature for the request and then to decrypt the returned token. These are the only places in the protocol where the private key is needed, implying that only the home instance needs to be a Fediverse instance. The target instance only needs access to public keys, meaning that OpenWebAuth can be used to allow users to log into things that are not instances.

## Implementations

OpenWebAuth was developed as part of the Hubzilla / Streams family of projects. More recently it has been added to Friendica and proposed for inclusion in Mastodon and PixelFed.

There is a [wiki page](https://hz.eenoog.org/wiki/pascal/Fediverse%2820%29OpenWebAuth%2820%29support/Home) which lists the current implementation status and links to the relevant pull requests.

## Security Considerations

The purpose of OpenWebAuth is to provide a strong guarantee of a user's identity to the web sites that they visit. This is often considered undesirable and consideration should be given to preventing this information from leaking to sites which may not be acting in the user's best interests.

This consideration may involve policies such as displaying a consent screen to the user or otherwise allowing them to choose which target instances they are willing to authenticate themselves to. The user's browser is redirected to their home instance at step 2, giving it an opportunity to implement policies such as these.

Unused `owt=` login tokens are deleted after a couple of minutes. This protects against a potential DoS attack which could fill up the target instance's storage with unused tokens.

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
