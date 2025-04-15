---
slug: "4f05"
authors: Julian Lam <julian@nodebb.org>, Angus McLeod <angus@pavilion.tech>
status: DRAFT
dateReceived: 2025-04-15
discussionsTo: https://socialhub.activitypub.rocks/t/fep-4f05-soft-deletion
---
# FEP-4f05: Soft Deletion


## Summary

The standard CRUD (Create, Read, Update, Delete) behaviours specified in [ActivityPub] specify a single `Delete` activity for use in all cases. This is insufficient to describe two-stage deletion, often referred to as "soft" and "hard" deletion.

Not all software implements two-stage deletion, and so the behaviours described here progressively enhance the functionality for those supporting it, while retaining backward compatibility otherwise.

### Assumptions

[A blog post by kaniini][DeleteSocialHub] advocates for the treatment of copies remote data _as a cache_. From there we derive the following assumptions:

* data living on the remote server is considered canonical.
* an incoming `Delete` activity should be treated as a request to refresh the locally cached copy or delete it otherwise.

The Forums and Threaded Discussions Task Force (ForumWG) has [identified a common nomenclature][Nomenclature] when referring to organized objects in a threaded discussion model.

* this FEP assumes the items in question are objects, although the concept described can apply to contexts as well.

## Publishers

### Soft deletion

When an object is **soft deleted**, the object's ActivityPub representation MUST be updated to `Tombstone`. Servers SHOULD continue to respond to requests for the object with a 200-level response code; the object continues to exist in-place.

A `Delete` activity SHOULD be published in order to propagate the soft deletion to other servers.

### Hard deletion

When an object is **hard deleted**, the object MUST no longer have an ActivityPub representation. Servers MUST respond to requests for the object with a 400-level response code. A [`404 Not Found`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/404) is acceptable, although a [`410  Gone`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/410) sends a more explicit signal that the object was explicitly removed. Security or privacy considerations may affect your decision to send anything more than a 404.

A `Delete` activity MUST be published in order to propagate the hard deletion to other servers.

## Receivers

When a `Delete` activity is encountered, the `actor` may not match the `attributedTo` of the targeted object. Follow the [origin-based security model][fe34] for verifying authenticity of the received activity.

Request the object (via its `id`) from the origin server directly, and handle appropriately based on the received response code or object `type`.

### `Tombstone`

The local object SHOULD be soft deleted as per the local implementor's standard behaviour.

### Not a `Tombstone`

Update the object's local representation if applicable.

### HTTP 404 or 410

The local object SHOULD be hard deleted as per the local implementor's standard behaviour.

## Additional Considerations

An earlier implementation of two-stage object deletion published an `Update(Tombstone)`, but this approach was deemed superfluous as it signified the same effect as a `Delete`—to proceed with a cache invalidation and update.

It is safe to assume the majority of ActivityPub-enabled software does not support two-stage object deletion. Publishing a `Delete` ensures that the intended behaviour of a soft deletion—that the object's content is no longer visible—is carried through to other servers.

Implementors are free to handle a soft deletion in the way they prefer (e.g. NodeBB will continue to associate the post (object) with the original actor, and simply blank out the content for non-privileged users.) This FEP explicitly does not specify how individual implementors should handle local representations of remote data.

The recipients list of the published `Delete` activity is outside the scope of this document.

## Implementors

* NodeBB
* Discourse

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- kaniini, [_The Delete Activity And It's Misconceptions_][DeleteSocialHub], 2019
- Julian Lam, [ForumWG Nomenclature][Nomenclature], 2024
- silverpill, [FEP-fe34: Origin-based security model][fe34], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[DeleteSocialHub]: https://socialhub.activitypub.rocks/t/the-delete-activity-and-its-misconceptions/137
[Nomenclature]: https://github.com/swicg/forums/issues/4
[fe34]: https://codeberg.org/fediverse/fep/src/branch/main/fep/fe34/fep-fe34.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
