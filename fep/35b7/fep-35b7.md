---
slug: 35b7
authors: Steve Bate <svc-fep@stevebate.net>
type: informational
status: DRAFT
discussionsTo: https://codeberg.org/steve-bate/fep/issues
dateReceived: 2026-04-22
trackingIssue: https://codeberg.org/fediverse/fep/issues/832
---
# FEP-35b7: Fediverse Servers, Instances, and Tenants

## Summary

This proposal defines terminology related to servers, instances, and tenants in a [Fediverse][FEDIVERSE] context. The goal is to provide consistent vocabulary for specifications, implementations, and documentation across projects.

## Motivation

Fediverse discussions use overlapping but sometimes inconsistent terminology when describing software, deployments, and administrative boundaries. In particular, the words “server” and “instance” are often used interchangeably.

The terminology issue becomes even more clear for multi-tenant server implementations and instances. As more projects implement multi-tenant architectures, clear terminology becomes important for:

- Protocol specifications and FEPs
- Implementation documentation and configuration
- Operational guidance and security analysis
- Interoperability discussions between projects

This document proposes terminology that other FEPs and implementations may reference.

## Definitions

### Server implementation

A **server implementation** is a software codebase that implements one or more Fediverse-related protocols (such as ActivityPub). This software must be deployed on computational infrastructure to participate in the Fediverse.

Characteristics:

- Identified primarily by its source code and release artifacts (e.g. a repository, package, or container image).
- May support different deployment topologies, including single-tenant, multi-tenant, and clustered deployments.
- Multiple independently operated deployments of the same server implementation are still the same implementation but different [server instances](#server-instance).

Example Implementations:

- Mastodon ([repo](https://github.com/mastodon/mastodon))
- Pleroma ([repo](https://git.pleroma.social/pleroma/pleroma))
- Mitra ([repo](https://codeberg.org/silverpill/mitra))

The word *server* may also refer to computational infrastructure (physical or virtual hardware, containers, etc.) in some contexts. This is not how the word is used in this proposal, which only refers to server *software*.

### Server instance

A **server instance** is a specific deployment of a server implementation, including its running processes, configuration, and associated persistent storage, operated by a defined administrative authority.

Characteristics:

- Exists in a particular operational environment (e.g. a host, container cluster, or PaaS deployment) with its own lifecycle (provisioning, upgrade, backup, decommissioning).
- Is typically associated with one or more network endpoints (e.g. hostnames, IP addresses, ports) that other Fediverse participants use to communicate with it.
- May serve one or multiple tenants, depending on the implementation and configuration.
- Two deployments of the same software are considered different server instances.

Examples:

- [mastodon.social](https://mastodon.social) is a Mastodon instance.
- [hachyderm.io](https://hachyderm.io/) is a Mastodon instance.
- [udongein.xyz](https://udongein.xyz/about) is a Pleroma instance.

In common Fediverse usage, “instance” often implicitly refers to a server instance; this document uses the explicit term “server instance” for clarity.

### Tenant

A **tenant** in a Fediverse context is a logically and administratively distinct group of actors and related data that is served by a server instance and for which the server provides isolated configuration, policies, and data separation.

This definition adapts the general notion of [multitenancy][MULTITENANT] where a single software instance serves multiple tenants while isolating their data and configuration to the specific case of Fediverse services.

Characteristics:

- A tenant is typically associated with a set of human users, automated agents, or both, that share a common administrative or organizational boundary (such as a community, organization, or project).
- A tenant configuration may be constrained by instance-level administrative policies.
- The server instance enforces isolation of tenant-specific data and configuration from other tenants on the same instance, such that each tenant’s data is not visible or modifiable by other tenants, except via Fediverse protocol interactions.
- Tenants may have distinct policies (e.g. moderation rules, registration policies, content limits), branding, and domain names within the same server instance, depending on implementation.
- Tenants may be mapped to domains or subdomains, path prefixes, or other routing constructs at the protocol and deployment levels (e.g. `https://tenant-a.server.example/`, `https://tenant-b.server.example/`, `https://tenant-c.example/`).

Examples:

- A multi-tenant deployment where a single server instance hosts per-user domains (`https://alice.example/` and `https://bob.example/`).
- A deployment where multiple communities are modeled as separate tenants with separate administrative control.

Related concepts:

* "Bring your own domain" (BYOD): In general, this does not require a multi-tenant instance although multi-tenant support will typically provide the feature. A user-registered domain can also be used with a single-tenant self-hosted server, for example.

* Reverse-proxied cluster: An architecture with multiple single-tenant server instances with a reverse proxy is not considered a multi-tenant *instance* given the definitions in this proposal. However, more broadly, it could be considered a multi-tenant *cluster architecture*.

## Relationship Between Terms

- One server implementation can be deployed as many server instances.
- Each server instance runs exactly one version of a server implementation at a given point in time.
- A server instance may serve one tenant (single-tenant) or multiple tenants (multi-tenant). Current server implementations are predominately server a single tenant. Known multitenant-capable server implementations include [Takahē](https://jointakahe.org/), [Vocata](https://codeberg.org/Vocata/vocata), and [FIRM](https://github.com/steve-bate/firm).

```text
+-----------------------+
| Server implementation |
+-----------------------+
| software codebase     |
| release artifacts     |
+-----------------------+
	     |
	     | 0..*
	     v
+-----------------------+
|    Server instance    |
+-----------------------+
| running deployment    |
| config + storage      |
| admin boundary        |
+-----------------------+
	|                 \
	|                  \
	|                   \
	v                    v
+----------------+  +----------------+
| Single tenant  |  | Multi-tenant   |
| deployment     |  | deployment     |
+----------------+  +----------------+
	 \              /
	  \            /
	   \          /
	    \ 1      / 1..*
	     v      v
	   +----------------+
	   |     Tenant     |
	   +----------------+
	   | isolated data  |
	   | isolated policy|
	   | admin boundary |
	   +----------------+
```

## Scope and Non-Goals

This document:

- Defines terminology for use in FEPs, specifications, and implementation documentation.
- Does not prescribe any particular multitenancy model, request routing strategy, database layout, or deployment topology.
- Does not define how tenants are discovered, migrated, or addressed at the protocol level; those topics are expected to be covered by other FEPs.

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub][ACTIVITYPUB], World Wide Web Consortium (W3C), 2018
- [Multitenancy][MULTITENANT], Wikipedia Foundation, 2026
- [Fediverse][FEDIVERSE], Wikipedia Foundation, 2026

[ACTIVITYPUB]: https://www.w3.org/TR/activitypub/ "ActivityPub"
[MULTITENANT]: https://en.wikipedia.org/w/index.php?title=Multitenancy&oldid=1338248635 "Multitenancy"
[FEDIVERSE]: https://en.wikipedia.org/w/index.php?title=Fediverse&oldid=1349081668 "Fediverse"

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
