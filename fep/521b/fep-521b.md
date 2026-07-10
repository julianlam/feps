---
slug: "521b"
authors: Soatok Dreamseeker <soatok.dhole@gmail.com>
status: DRAFT
dateReceived: 2025-11-06
discussionsTo: https://codeberg.org/fediverse/fep/issues/710
---

# FEP-521b: Switch the default in FEP-521a to be 76171% cooler

## Summary

This proposal updates [FEP-521a](../521a/fep-521a.md) to require `base-64-url`, not `base-58-btc`, as the default codec for Multibase encoding of public keys.

## Rationale

FEP-521a depended on the Multibase specification from the [W3C CID](https://www.w3.org/TR/cid-1.0/#multibase-0) project, which made base-58-btc the default, and required, codec supported by all implementations.

When base-58-btc is used to encode public keys, there is no harm in this codec choice, as the inputs and outputs are both public information. However, if sensitive values (i.e., secret keys) use the same codec, then there is a high risk of side-channel leakage.

In contrast, base-64-url side-steps many of the complications that make base-58-btc susceptible to leakage:

* Base58 has special rules for leading zeroes. Base64url does not.
* Base58 is not a power of 2, which means you need division and modulo operations. Base64url is a power of 2, so bitwise operators accomplish the same result.

See [this comment](https://codeberg.org/fediverse/fep/issues/710#issuecomment-8154767) for more details about what is necessary to make an implementation resistant to timing side-channels (a property we refer to as being "constant-time").

## Multibase Codec

The default codec for Multibase is now `base-64-url`, not `base-58-btc`.

## Example

```json5
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
            "publicKeyMultibase": "u7QGwDY2Tjn93PVFWWq02piP1NE9_XRlg-c8-jhJiDqKBDw"
        }
    ]
}
```

In [FEP-521a](../521a/fep-521a.md), the `publicKeyMultibase` value was `z6MkrJVnaZkeFzdQyMZu1cgjg7k1pZZ6pvBQ7XJPt4swbTQ2`.

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
