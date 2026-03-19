---
slug: "a1d1"
type: implementation
authors: Steve Bate <svc-fep@stevebate.net>
status: DRAFT
discussionsTo: https://codeberg.org/steve-bate/fep/issues
dateReceived: 2026-03-19
trackingIssue: https://codeberg.org/fediverse/fep/issues/796
---
# FEP-a1d1: ActivityPub Patch

## Summary

[ActivityPub] Client-to-Server (C2S) Partial Update relies on shallow top-level replacement and uses JSON `null` to signal property removal, but in compacted JSON-LD `null` is elided, so deletions can be lost in transit. This FEP introduces a `Patch` activity (based on [JSON Patch][RFC6902]) that cleanly separates patch operations from the target object and supports nested property updates via JSON Pointer ([RFC6901](https://www.rfc-editor.org/rfc/rfc6901)).

## Motivation

ActivityPub client-to-server updates are currently defined as shallow partial replacements of top-level properties, with a special rule that a property set to JSON `null` is removed from the stored object. In practice, that removal rule is not compatible with ActivityPub's JSON-LD serialization model. 

In compacted JSON-LD, `null` values are removed and treated as if the property wasn't specified, so a server may never receive the signal that a property is meant to be deleted. This issue has been recorded in the [ActivityPub errata], and related discussion in the W3C ActivityPub issue tracker (Issues #[396](https://github.com/w3c/activitypub/issues/396) and #[477](https://github.com/w3c/activitypub/issues/477)).

The semantics of the C2S Partial Update is also incorrect. The update is specified in the `object` property with an `id`. However, the `id` is the URI of the target object rather than the update object. In other words, the `id` is not being used to specify the identity of the `Update` `object`, but rather a completely different target object. The `Patch` operation separates the patch operations from the `target` object that will be patched.

The C2S Partial Update can only modify top-level properties. The `Patch` activity can modify nested properties (using JSON Pointer [RFC6901](https://www.rfc-editor.org/rfc/rfc6901) ).

Ideally, the `Patch` activity will replace partial `Update` activities in the C2S specification. For complete object replacement, the C2S `Update` activity can continue to be used in a consistent manner as for the Server-to-Server (S2S) `Update`.

## Patch

Based on [JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902/), a `Patch` `object` refers to a `PatchOperations` object. This object has an `operations` property containing an ordered list of operations.

**Example**

```json
{
    "@context": [
        "https://w3id.org/fep/a1d1",
        "https://www.w3.org/ns/activitystreams"
    ],
    "id": "https://server.example/patch/1",
    "type": "Patch",
    "object": {
        "type": "PatchOperations",
        "operations": [
            {
                "op": "add",
                "path": "/name",
                "value": "Daily post"
            },
            {
                "op": "remove",
                "path": "/summary",
            },
            {
                "value": "Some new content...",
                "path": "/content",
                "op": "replace"
            },
            {
                "value": "Du nouveau contenu...",
                "path": "/contentMap/fr",
                "op": "replace"
            },
        ]
    },
    "target": "http://object-to-update"
}
```

The `operations` are standard JSON Patch operations so they will not be covered in detail in this FEP. The operations include:

* `add`
* `remove`
* `replace`
* `move`
* `copy`
* `test`

[RFC6902] contains numerous examples that describe the semantics of these operations. This FEP defines a JSON-LD context for the `Patch` activity and the JSON Patch language.

## Side-Effects

When a `Patch` activity is posted to the outbox, the server MUST apply authorized operations to the target object. After the update is complete, the server SHOULD send an `Update` notification (with the full, updated object) notification, on behalf of the `Patch` actor, to any specified recipients.

## JSON-LD Context

```json
{
    "@context": [
        {
            "@version": 1.1,
            "fep-a1d1": "https://w3id.org/fep/a1d1#",
            "Patch": "fep-a1d1:Patch",
            "PatchOperations": {
                "@id": "fep-a1d1:PatchOperations",
                "@context": {
                    "operations": {
                        "@id": "fep-a1d1:operations",
                        "@container": "@list",
                        "@context": {
                            "op": "fep-a1d1:op",
                            "path": "fep-a1d1:path",
                            "value": { 
                                "@id": "fep-a1d1:value", 
                                "@type": "@json"
                            },
                            "from": "fep-a1d1:from",
                            "add": "fep-a1d1:add",
                            "remove": "fep-a1d1:remove",
                            "replace": "fep-a1d1:replace",
                            "move": "fep-a1d1:move",
                            "copy": "fep-a1d1:copy",
                            "test": "fep-a1d1:test"
                        }
                    }
                }
            }
        }
    ]
}
```

> **NOTE:** The `fep-a1d1:value` term is defined as a JSON-LD `@json` type. For JSON consumers, this will not make a difference but it tells JSON-LD consumers
that the content is a serialized JSON string (which may itself be JSON-LD). Linked Data applications will typically need to parse this string to retrieve the original JSON content.

## Implementations

- [FIRM](https://github.com/steve-bate/firm)

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement
Proposal have waived all copyright and related or neighboring rights to this work.


[ActivityPub]: https://www.w3.org/TR/activitypub/ "ActivityPub is a decentralized social networking protocol based upon the ActivityStreams 2.0 data format."
[ActivityPub errata]: https://www.w3.org/wiki/ActivityPub_errata
[ActivityStreams]: https://www.w3.org/TR/activitystreams-vocabulary/
[RFC6902]: https://datatracker.ietf.org/doc/html/rfc6902/
