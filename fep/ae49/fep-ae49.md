---
slug: ae49
authors: Steve Bate <svc-fep@stevebate.net>
type: implementation
status: DRAFT
discussionsTo: https://codeberg.org/steve-bate/fep/issues
dateReceived: 2026-04-24
trackingIssue: https://codeberg.org/fediverse/fep/issues/836
---
# FEP-ae49: Semantic Routing for ActivityPub

## Summary

This proposal specifies *semantic* request routing for ActivityPub servers: an approach
to dispatching incoming activities by following
the relationships declared within ActivityStreams objects and dereferencing objects using
opaque URIs rather than parsing or
pattern-matching URL path segments. Semantic routing treats all
ActivityPub [URIs][RFC3986] as [opaque identifiers][URI-OPACITY] and
decouples implementation behavior from any particular URI path structure.

Most existing servers implement “path-based routing,” where the handler and
target actor are determined from path segments such as `/users/:username/inbox`.
This tight coupling makes it hard to migrate between software implementations
without breaking URIs and violates the [URI Opacity Axiom][URI-OPACITY], since semantics
are inferred from paths that are implementation-dependent.

Semantic routing instead relies on dereferencing ActivityStreams objects and
using relationships to identify and validate `inbox` and `outbox` endpoints. This allows URIs to remain
stable across implementations, simplifying migration scenarios where the domain does not change.

## Motivation

[ActivityPub][ACTIVITYPUB] federation works by looking up the target actor’s `inbox` and POSTing
activities to it. The Social API works by POSTing activities to an actor's `outbox`. ActivityPub documents are dereferenced (GET) using their `id` (URI).

Most ActivityPub servers route these requests based on a predefined URI path structure. This path-based approach has several drawbacks.

- URI lock-in: actor URIs minted by one implementation generally cannot be reused
  unchanged by another, because the new software expects different path
  shapes. Migrations either constrain software choice to preserve old paths
  or force new actor URIs, breaking links and federated state. Even when using a custom domain, it is generally not possible to migrate ActivityPub content from one implementation to another because of differing requirements for URI path shapes.

- Violation of URI opacity: "The only thing you can use an identifier for is to refer to an object. When you are not dereferencing, you should not look at the contents of the URI string to gain other information. -- Tim Berners-Lee, 1996 [[ref]][URI-AXIOMS]"

By shifting routing decisions from URI path analysis to graph traversal over
ActivityStreams objects, semantic routing eliminates these problems and allows
implementations to support flexible URI layouts.

## Scope

This proposal:

- Defines requirements for implementations that wish to employ semantic routing
  for ActivityPub.
- Provides non-normative examples illustrating correct behavior.
- Provides a list of known implementations.

The proposal does not modify [ActivityPub][ACTIVITYPUB] or [ActivityStreams][ACTIVITYSTREAMS]. It adds
constraints on implementation strategy while leaving the wire protocol unchanged.

This specification constrains only top-level request handling:

- `POST` to an actor *box* (`inbox`, `outbox`, `sharedInbox`)
- `GET` resolve an ActivityPub/ActivityStreams object ID

A `POST` to other URIs can use similar techniques, but since ActivityPub doesn't define
these kinds of posts, it is outside the scope of this document.

Internal subhandler selection (for example, by activity type, recipient conditions, or
local policy checks) is an implementation detail and is out of scope as long as it is
not dependent on a specific URI structure.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC2119].

**path-based routing**
: A request dispatch strategy in which an HTTP server parses the URI path of an incoming request and matches path segments against a static or parameterized route table to determine the handler responsible for the request. In the ActivityPub context, this typically means extracting an actor identifier (such as a username) from the path and using it to look up the corresponding actor record in a local database, without first dereferencing the request URURIL as an ActivityStreams object.

**semantic routing**
: A request dispatch strategy for ActivityPub servers in which the server processes a request based on the target URI rather than pattern matching on URI path segments. The dispatch uses ActivityPub objects and their relationships to determine how to process the request.

**resource**
: An [ActivityStreams][ACTIVITYSTREAMS] object retrieved by dereferencing a resource URI.

**opaque URI**
: A URI whose path, query, and fragment components carry no meaning to recipients beyond what is logically needed to dereference the URI or process POST requests to it [RFC3986].

**top-level handler**
: One of the three request classes in scope for this specification: inbox POST, outbox POST, or object dereference GET.

## Conformance

This specification defines requirements for one conformance class:

**Semantically Routing Server**
: An ActivityPub server (federated server or combined server) that dispatches
    incoming HTTP requests exclusively through
    *semantic routing* as defined in this document.

All of Section [requirements](#requirements-for-semantic-routing) are normative. All examples, notes, and sections explicitly labelled "non-normative" are informative.

Note: Implementations that satisfy the requirements in this document remain
fully conformant with [ActivityPub][ACTIVITYPUB]. The requirements here constrain
*how* routing is performed, not what is placed on the wire.

## Path-Based Routing: Characteristics and Problems

### How Path-Based Routing Works

In a typical fediverse server using path-based routing, a web framework
(such as Rails, Django, Express, or Flask) is configured with a route table
mapping URI path patterns to controller functions. When an ActivityPub activity
arrives addressed to a local actor, the server:

1. Receives an HTTP POST to a URI such as `https://social.example/users/alice/inbox`.
2. Matches the path `/users/alice/inbox` against the route pattern `/users/:username/inbox`.
3. Extracts the string `alice` as the username.
4. Looks up actor `alice` in the local database.
5. Passes the request body to the inbox handler with `alice`'s database record.

A representative path-based route table from a pseudocode web framework:

```text
POST /users/:username/inbox          → inbox_controller(username)
GET  /users/:username/outbox         → outbox_controller(username)
GET  /users/:username                → actor_controller(username)
GET  /users/:username/followers      → followers_controller(username)
GET  /users/:username/following      → following_controller(username)
```

The critical characteristic is that the `username` portion of the path is
authoritative for dispatch.

### Problems Introduced by Path-Based Routing

#### URI Lock-In and Migration Failure

Because the routing table defines the valid URI patterns for actor endpoints,
changing software means either:

- **Preserving the identical URI patterns**: The new software must implement
  the same path convention as the old software. This constrains software
  selection and prevents adoption of implementations that use different path
  structures such as `/ap/actors/:id/inbox`, `/:username/inbox`, or
  `/inbox/:uuid`.

- **Minting new URIs**: The actor gets a new `id`, breaking all federated
  relationships. Every remote server that cached the old actor document now
  holds a stale record. Followers are lost unless a manual re-follow campaign
  is conducted.

Neither option is satisfactory. The ActivityPub specification provides no
URI migration mechanism precisely because URIs are supposed to be stable,
opaque identifiers.

Example: migration failure with path-based request routing:

A community server running *SoftwareA* uses actor URIs of the form
`https://community.example/users/alice`, with inbox at
`/users/alice/inbox`.

The community migrates to *SoftwareB*, which uses actor URIs of the
form `https://community.example/alice`, with inbox at
`/inboxes/alice`.

All existing actor URIs are now invalid. Remote servers that delivered
activities to `/users/alice/inbox` receive HTTP 404 responses.
The actor's followers on remote servers reference the old actor `id`,
which no longer resolves.

If both *SoftwareA* and *SoftwareB* implemented semantic request routing, the
migration would be a simple transfer of content with not changes to URIs.

## Requirements for Semantic Routing

### [URI Opacity][URI-OPACITY]

URI opacity is the foundation of semantic routing. Routing
decisions MUST NOT depend on the syntactic structure of a URI's path, query,
or fragment components.

A Semantically Routing Server MUST NOT parse the path, query string,
or fragment of an incoming request URI to determine the identity of the
target actor or the type of endpoint being accessed (inbox, outbox, etc.).

### HTTP Request Handling

When a Semantically Routing Server receives an HTTP request, 
it MUST NOT depend on the syntactic structure of a URI's path, 
query, or fragment components to handle it.

## Semantic Routing Algorithms

This section is non-normative.

Although it may be possible to implement semantic routing using other algorithms,
this section shows pseudo-code for a possible implementation. This proposal does not include details like authorization or other security considerations that are not uniquely related to semantic request routing.

### HTTP GET

* Dereference the resource using opaque URI
* Return the serialized resource

### HTTP POST

* Dereference the resource using opaque URI
* Identify the owning actor
   * Using `attributedTo`, if present, or
   * Search for actor `inbox` or `outbox` reference to resource (conceptually, a graph search)
* After identifying `inbox` or `outbox`, dispatch to related handler
* Further Activity processing uses posted resource properties like `type` and `object`.

Example:

```
POST /x/9f3c1 HTTP/1.1
Host: social.example
Content-Type: application/activity+json

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://remote.example/activities/abcd",
  "type": "Follow",
  "actor": "https://remote.example/users/bob",
  "object": "https://social.example/actors/alice"
}
```

Where `https://social.example/x/9f3c1` is an opaque URI that happens to be Alice's inbox,
the server can process the request semantically as follows:

1. Treat the request target URI as an opaque identifier and do not parse path segments.
2. Dereference `https://social.example/x/9f3c1` to obtain the local inbox resource.
3. Identify the owning actor by reading resource relations (for example, `attributedTo`),
  or by resolving reverse links from actor resources that reference this inbox.
4. Confirm the resolved actor document contains an `inbox` equal to
  `https://social.example/x/9f3c1`.
5. Dispatch to the inbox handler for that actor and continue normal ActivityPub
  processing of the posted activity (`type: Follow`, authorization checks, policy checks,
  delivery side-effects, and response status).

This algorithm works regardless of whether the inbox URI looks like
`/users/alice/inbox`, `/inbox/42`, or `/x/9f3c1`. 

The same procedure is used for POST requests to `outbox` URIs. 

### Shared Inbox

For `sharedInbox` POST, the algorithm is similar but applied to each local inbox URI targeted for delivery.

For `sharedInbox` GET, the opaque URI is used to identify the request target. The dereferencing or construction of the resulting `OrderedCollectio`n is implementation-dependent.

## Security Considerations

TODO

## Related Work

### Solid

This section is non-normative.

The [Solid Protocol][SOLID] similarly treats
resource URIs as opaque and uses link relations to discover associated
resources. Solid's approach to data pods, where access control and resource
discovery are driven by linked metadata rather than URI structure parallels
the motivation for semantic routing in ActivityPub.

## Implementations

- [**FIRM ActivityPub Server**][FIRM] implements semantic routing as described
  in this document.
- [**Vocata**][VOCATA] implements semantic routing as described
  in this document and was the inspiration for the FIRM implementation.
- [**Mitra**][MITRA] implements semantic routing for [portable object][PORTABLE-OBJECTS] GET requests.

[URI-OPACITY]: https://www.w3.org/DesignIssues/Axioms.html#opaque


## References
- @caesar@indieweb.social, [Switching AP server software on the same domain][SWITCHING], SocialHub, 2024
- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub][ACTIVITYPUB], World Wide Web Consortium (W3C), 2018
- Dominik George, [Vocata][VOCATA] \[Software\], Codeberg
- Sarven Capadisli, Tim Berners-Lee, Dmitri Zagidulin, [Solid Protocol][SOLID], World Wide Web Consortium (W3C), 2024
- Scott O. Bradner, [Key words for use in RFCs to Indicate Requirement Levels][RFC2119], Internet Engineering Task Force, IETF, 1997
- Snell James M., Evan Prodromou, [Activity Streams 2.0][ACTIVITYSTREAMS], World Wide Web Consortium (W3C), 2017
- Snell James M., Evan Prodromou, [Activity Vocabulary][ACTIVITYSTREAMS-VOCAB], World Wide Web Consortium (W3C), 2017
- Steve Bate, [FIRM][FIRM] \[Software\], GitHub
- Steve Bate, [Flexible URI structure in AP Server Implementations][FLEXIBLE-URI], SocialHub, 2024
- Tim Berners-Lee, Roy T. Fielding, Larry M. Masinter, [Uniform Resource Identifier (URI): Generic Syntax][RFC3986], Internet Engineering Task Force, IETF, 2005
- Tim Berners-Lee, [Univeral Resource Identifiers -- Axioms of Web architecture][URI-AXIOMS], World Wide Web Consortium (W3C), W3C, 1996
- silverpill, [FEP-EF61 Portable Objects][PORTABLE-OBJECTS], GitHub, 2023
- silverpill, [Mitra][MITRA] \[Software\], Codeberg

[ACTIVITYPUB]: https://www.w3.org/TR/activitypub/ "ActivityPub"
[RFC2119]: https://datatracker.ietf.org/doc/rfc2119 "Key words for use in RFCs to Indicate Requirement Levels"
[ACTIVITYSTREAMS-VOCAB]: https://www.w3.org/TR/activitystreams-vocabulary/ "Activity Vocabulary"
[ACTIVITYSTREAMS]: https://www.w3.org/TR/activitystreams-core/ "Activity Streams 2.0"
[RFC3986]: https://datatracker.ietf.org/doc/rfc3986 "Uniform Resource Identifier (URI): Generic Syntax"
[VOCATA]: https://codeberg.org/Vocata/vocata "Vocata"
[FIRM]: https://github.com/steve-bate/firm "FIRM"
[FLEXIBLE-URI]: https://socialhub.activitypub.rocks/t/flexible-uri-structure-in-ap-server-implementations/4767 "Flexible URI structure in AP Server Implementations"
[SWITCHING]: https://socialhub.activitypub.rocks/t/switching-ap-server-software-on-the-same-domain/4508 "Switching AP server software on the same domain"
[SOLID]: https://solidproject.org/TR/protocol "Solid Protocol"
[URI-AXIOMS]: https://www.w3.org/DesignIssues/Axioms.html "Univeral Resource Identifiers -- Axioms of Web architecture"
[MITRA]: https://codeberg.org/silverpill/mitra "Mitra"
[PORTABLE-OBJECTS]: https://codeberg.org/fediverse/fep/src/branch/main/fep/ef61/fep-ef61.md "FEP-EF61 Portable Objects"

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
