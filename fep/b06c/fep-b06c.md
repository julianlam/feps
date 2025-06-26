---
slug: "b06c"
authors: Evan Prodromou <evan@socialwebfoundation.org>
status: DRAFT
dateReceived: 2025-06-25
discussionsTo: https://codeberg.org/evanp/fep/issues
---
# FEP-b06c: ActivityPoll

## Summary

 ActivityPoll is a proper subset of ActivityPub that excludes activity delivery, making it easier to implement for static Web sites or content management systems. It meets an equivalent need to RSS or Atom feeds.

## Introduction

In ActivityPub (AP), an **actor** is an ActivityPub object that produces activities. The actor's `outbox` is the collection of activities that the actor has produced.

[ActivityPub][ActivityPub] has optional features for real-time delivery of activities.
ActivityPub actors MAY deliver new activities to the actors addressed in the activity's `to`, `cc`, `bto`, `bcc` and `audience` properties using the ActivityPub federation protocol. The actor MAY also receive activities from other actors in its `inbox`, such as comments, likes, and other feedback.

Supporting the federation protocol adds significant complexity in the implementation of ActivityPub. Handling incoming and outgoing activities is a significant barrier to entry for AP implementation.

One alternative is to shift the burden of initiating delivery from the publisher to the consumer. Instead of pushing activities from the publishing server as they are generated, the activities can instead be pulled by the consumer at regular intervals.

There are three main downsides to a polling structure.

1. Activities are not delivered in near-real-time; there is a potential delay, up to the polling interval of the consumer (which may be variable).
2. The consumer can request updates when no new activities have been published, which takes both consumer and publisher resources.
3. Activities are not reliably delivered to the addressees. Unless the addressees' servers poll the feed, the addressees do not receive the activities in their `inbox`.

The primary upside is that polling opens up the social web to many more implementers. Any publisher that can publish an RSS feed can publish an ActivityPoll actor. Polling also opens up the network to simpler, power-constrained devices, as well as static web sites.

Having more content producers is better for all users, and thus better for more mature and full-featured social web platforms. Shifting this burden of delivery, if it results in more information on the network, can be good for the entire ecosystem.

This subset of ActivityPub, called **ActivityPoll**, describes the reduced responsibilities of the publisher, the increased responsibilities of the consumer, and methods for indicating use of polling.

## Publishers

ActivityPoll publishers host one or more ActivityPoll actors. ActivityPoll actors are valid ActivityPub actors and ActivityPub objects. They MUST have at least the following properties:

- `id`: A unique identifier for the actor, which MUST be a dereferenceable IRI.
- `type`: The type of the actor.
- `outbox`: An `OrderedCollection` of activities, with its own dereferenceable IRI.
- `inbox`: An `OrderedCollection` of activities, with its own dereferenceable IRI.

Other properties of an [Activity Streams 2.0][AS2] object MAY be included, including [extension properties](https://www.w3.org/TR/activitystreams-core/#extensibility).

Other properties of an [ActivityPub actor](https://www.w3.org/TR/activitypub/#actors) object MAY be included.

### Inbox

If an actor is poll-only, and does not support the ActivityPub federation protocol, the IRI of the `inbox` property of the actor MUST respond with a [405 Method Not Allowed](https://datatracker.ietf.org/doc/html/rfc9110#name-405-method-not-allowed) response to HTTP POST requests.

Publishers MAY also indicate that delivery is not supported using the `pollOnly` property defined in this specification, setting it to `true`. This does not override the requirement to have an `inbox` property that returns a 405 HTTP status on POST.

### Outbox

The actor's `outbox` property is an `OrderedCollection` in reverse chronological order. It MAY be [paginated](https://www.w3.org/TR/activitystreams-core/#paging).

The IRI for the `outbox` collection SHOULD support [HTTP Caching][CACHING], including the `If-Modified-Since` and `If-None-Match` request headers. The IRI for each page of a paginated `outbox` collection SHOULD support HTTP Caching.

The `outbox` collection object SHOULD include a `totalItems` property, so that changes in any page of the collection are reflected in the collection itself.

Activities in the `outbox`, and all the object properties of the activities, MUST be valid ActivityPub objects, with dereferenceable IRIs.

To make incremental polling manageable, ordering of activities in the `outbox` collection SHOULD be stable. New activities SHOULD be prepended to the collection. Deleted activities SHOULD be replaced by a [Tombstone](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-tombstone) object.

### Authentication

ActivityPoll servers MAY require authentication, such as [OAuth 2.0][OAuth2] or [HTTP Signatures](HTTPSignatures). Collections such as `outbox` MAY be filtered according to the access level of the authenticated client.

### Lack of activity side effects

Without an `inbox` that can receive incoming activities, an ActivityPoll publisher might not maintain many of the state changes that are typical side effects of such activities. A non-exhaustive list of collections affected by inbound activities:

- maintaining the `followers` collection for an actor
- maintaining the `replies` collection for an object
- maintaining the `shares` collection for an object
- maintaining the `likes` collection for an object

Publishers SHOULD omit these properties from objects and actors if they will not be maintained.

### Webfinger

ActivityPoll servers MAY implement [Webfinger][Webfinger] to allow `user@hostname` addressing for actors. Because Webfinger requires different content based on a query parameter, it is difficult to implement for static web sites, unless they only support a single actor.

## Consumers

ActivityPoll consumers read the `outbox` collection of an actor to retrieve activities and distribute them.

ActivityPoll consumers SHOULD support [HTTP Caching][CACHING] when fetching the `OrderedCollection`, its pages, and any activities and related objects in the collection.

Because the `outbox` property is ordered in reverse chronological order, consumers SHOULD use the results of their last poll to limit requests to the publishing server. Keeping a "last read" activity ID between polls can be used to limit the requests to only activities and pages published since that ID.

### Following

ActivityPoll consumers SHOULD include remote ActivityPoll actors in their actors' `following` collections.

### Polling frequency

Polling frequency in syndication systems is important. If polling is too infrequent, new activities aren't processed in a timely fashion. If polling is too frequent, it abuses publisher and consumer resources without any new activities being delivered.

The `updateInterval` property of an actor can indicate how often the actor generates activities. Consumers SHOULD use this information to schedule polling requests. Consumers MAY use heuristics to schedule polling requests, such as median time between activities previously seen. Consumers MAY set a minimum frequency for polling actors, such as daily or monthly.

### Local delivery

If the addressing properties of an activity by an ActivityPoll actor include actors on the consumer server, the consumer SHOULD deliver the activities to those actors' `inbox` collections. ActivityPoll consumers MAY deliver activities by ActivityPoll publisher actors to other servers, for example for [inbox forwarding](https://www.w3.org/TR/activitypub/#inbox-forwarding).

### Activity side effects

Some activities, or their objects, MAY be added to special collections on the consumer server. These include:

- Objects with an `inReplyTo` property with the value of an ActivityPub object on the consuming server MAY be added to the `replies` collection for that object.
- `Like` activities with an `object` value on the consumer server MAY be added to the `likes` collection of that object.
- `Announce` activities with an `object` value on the consumer server MAY be added to the `shares` collection of that object.
- `Follow` activities with an `object` value on the consumer server MAY result in the actor being added to the `object` value's `followers` collection.

Other side effects MAY be implemented by the consuming server.

## Context

This specification includes a context document that defines the optional properties of an ActivityPoll actor.

```json
{
  "@context": {
    "poll": "https://w3id.org/fep/b06c#",
    "pollOnly": "poll:pollOnly",
    "updateInterval": "poll:updateInterval"
  }
}
```

The context can be included using the context URL `https://w3id.org/fep/b06c`, as illustrated in the examples below.

### `pollOnly`

This is a boolean property that can be used to determine if an actor does not deliver activities remotely. Its default value is `false`.

### `updateInterval`

This property represents a typical interval between activities in the `outbox` of the actor. It is expressed as an [xsd:duration](https://www.w3.org/TR/xmlschema11-2/#duration) value. Some example values:

- `P15M` - new activities are added every 15 minutes
- `P4H` - new activities are added once every 4 hours
- `P1D` - updated daily
- `P3M` - updated quarterly
- `P1Y` - updated annually

This interval conveys a rough estimate of update frequency, not a commitment. Different types of actors often have different posting profiles. Automated actors often have regular intervals for activities. Real-world humans, on the other hand, tend to cluster into "sessions", when a human being makes a number of activities in only a few minutes or hours.

## Examples

### Minimal ActivityPoll Actor

This minimal actor provides just enough information to be a useful ActivityPoll object.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/b06c"],
  "id": "https://device.example/actor.jsonld",
  "type": "Application",
  "name": "Low-power device #69883",
  "to": "as:Public",
  "pollOnly": true,
  "inbox": "https://device.example/actor/inbox.jsonld",
  "outbox":  "https://device.example/actor/outbox.jsonld"
}
```

The inbox for this actor is an empty collection.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/5711"],
  "id": "https://device.example/inbox.jsonld",
  "type": "OrderedCollection",
  "summary": "Inbox of low-power device #69883",
  "attributedTo": "https://device.example/actor.jsonld",
  "to": "as:Public",
  "inboxOf": "https://device.example/actor.jsonld",
  "totalItems": 0
}
```

The outbox for this actor is not paginated.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/5711"],
  "id": "https://device.example/outbox.jsonld",
  "type": "OrderedCollection",
  "summary": "Outbox of low-power device #69883",
  "attributedTo": "https://device.example/actor.jsonld",
  "to": "as:Public",
  "outboxOf": "https://device.example/actor.jsonld",
  "totalItems": 5,
  "items": [
    "https://device.example/create-note-3.jsonld",
    "https://device.example/like-note-1.jsonld",
    "https://device.example/delete-note-2.jsonld",
    "https://device.example/create-note-2.jsonld",
    "https://device.example/create-note-1.jsonld"
  ]
}
```

### Publication

This example models a simple ActivityPoll actor for a Web magazine. By [embedding](https://www.w3.org/TR/json-ld11/#embedding) node objects into the document, the publisher can dramatically reduce the number of HTTP requests required to check for updates.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/b06c"],
  "id": "https://publisher.example/magazine/activitypoll.jsonld",
  "type": "Organization",
  "name": "ActivityPoll Magazine",
  "summary": "The premier magazine for the poll-oriented social web",
  "pollOnly": true,
  "updateInterval": "P1D",
  "inbox": "https://publisher.example/magazine/activitypoll/inbox.jsonld",
  "outbox": {
    "id": "https://publisher.example/magazine/activitypoll/outbox.jsonld",
    "totalItems": 4,
    "first": {
      "id": "https://publisher.example/magazine/activitypoll/outbox/1.jsonld",
      "orderedItems": [
        {
          "id": "https://publisher.example/magazine/activitypoll/create/article/3.jsonld",
          "type": "Create",
          "summary": "ActivityPoll Magazine created an article",
          "actor": "https://publisher.example/magazine/activitypoll.jsonld",
          "to": "as:Public",
          "object": {
            "id": "https://publisher.example/magazine/activitypoll/article/3.jsonld",
            "type": "Article",
            "name": "Polling strategies for ActivityPoll consumers",
            "summary": "<p>An overview of strategies for polling intervals</p>",
            "url": "https://publisher.example/magazine/activitypoll/article/3.html",
            "attributedTo":  "https://publisher.example/magazine/activitypoll.jsonld",
            "to": "as:Public"
          },
          "published": "20250621T00:00:00Z"
        },
        {
          "id": "https://publisher.example/magazine/activitypoll/delete/article/2.jsonld",
          "type": "Delete",
          "summary": "ActivityPoll Magazine deleted an article",
          "actor": "https://publisher.example/magazine/activitypoll.jsonld",
          "to": "as:Public",
          "object": {
            "id": "https://publisher.example/magazine/activitypoll/article/2.jsonld",
            "type": "Tombstone",
            "formerType": "Create",
            "published": "20250615T00:00:00Z",
            "deleted": "20250618T00:00:00Z",
            "attributedTo":  "https://publisher.example/magazine/activitypoll.jsonld",
            "to": "as:Public"
          },
          "published": "20250618T00:00:00Z"
        },
        {
          "id": "https://publisher.example/magazine/activitypoll/create/article/2.jsonld",
          "type": "Create",
          "summary": "ActivityPoll Magazine created an article",
          "actor": "https://publisher.example/magazine/activitypoll.jsonld",
          "to": "as:Public",
          "object": {
            "id": "https://publisher.example/magazine/activitypoll/article/2.jsonld",
            "type": "Tombstone",
            "formerType": "Create",
            "published": "20250615T00:00:00Z",
            "deleted": "20250618T00:00:00Z",
            "attributedTo":  "https://publisher.example/magazine/activitypoll.jsonld",
            "to": "as:Public"
          },
          "published": "20250615T00:00:00Z"
        },
        {
          "id": "https://publisher.example/magazine/activitypoll/create/article/1.jsonld",
          "type": "Create",
          "summary": "ActivityPoll Magazine created an article",
          "actor": "https://publisher.example/magazine/activitypoll.jsonld",
          "to": "as:Public",
          "object": {
            "id": "https://publisher.example/magazine/activitypoll/article/1.jsonld",
            "type": "Article",
            "name": "Announcing ActivityPoll Magazine",
            "summary": "<p>This is a new magazine for posts about the poll-oriented social web.</p>",
            "url": "https://publisher.example/magazine/activitypoll/article/1.html",
            "attributedTo":  "https://publisher.example/magazine/activitypoll.jsonld",
            "to": "as:Public"
          },
          "published": "20250609T00:00:00Z"
        }
      ]
    }
  }
}
```

### Social Network Interactions

This example models a simple social network user, with reaction activities to content published elsewhere.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/b06c"],
  "id": "https://social.example/user/activitypoll.jsonld",
  "type": "Person",
  "name": "Social Networkuser",
  "summary": "A typical social network user",
  "pollOnly": true,
  "updateInterval": "P8H",
  "inbox":  "https://social.example/user/activitypoll/inbox.jsonld",
  "outbox": {
    "id": "https://social.example/user/activitypoll/outbox.jsonld",
    "totalItems": 3,
    "first": {
      "id": "https://social.example/user/activitypoll/outbox/1.jsonld",
      "orderedItems": [
        {
          "id": "https://social.example/user/activitypoll/activity/3.jsonld",
          "type": "Like",
          "summary": "Social Networkuser liked this object",
          "object": "https://other.example/object/D6D11370-8BD1-4E52-849B-AF62121AB58E"
        },
        {
          "id": "https://social.example/user/activitypoll/activity/2.jsonld",
          "type": "Announce",
          "summary": "Social Networkuser shared this object",
          "object": "https://third.example/object/50D4C4E9-DEB4-4EC5-8353-F079A63533F0"
        },
        {
          "id": "https://social.example/user/activitypoll/activity/3.jsonld",
          "type": "Create",
          "summary": "Social Networkuser created a note",
          "object": {
            "id": "https://social.example/user/activitypoll/note/1.jsonld",
            "type": "Note",
            "inReplyTo": "https://other.example/object/0BDF12F8-1148-4BDF-B911-3B9CBEA95678",
            "content": "I agree!"
          }
        }
      ]
    }
  }
}
```

## Privacy considerations

This specification allows publishers to implement authentication for ActivityPub objects, actors, and collections. However, authentication is difficult to implement for static web sites. Features that depend on authentication, such as non-public objects or blocking users or domains, will be hard to implement or enforce with ActivityPoll.

## Implementation notes

The subset of ActivityPub outlined in this specification does not preclude the use of the ActivityPub API for publishing activities, even if they are not delivered to remote addressees.

## History

Read-only, poll-based syndication feeds are a common pattern on the Web. [RSS 1.0][RSS1], [RSS 2.0][RSS2], [Atom][Atom], and other syndication formats have been used for decades to provide a simple way to transfer content from one Web site to another. [Atom Activity Streams 1.0][AS1] enhanced Atom with richer data about social networking activities, such as comments, likes, and shares.

## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- Aaron Swartz, [RSS1], 2000
- Harvard Law School Berkman Klein Center for Internet & Society, [RSS2], 2002
- Mark Nottingham, R. Sayer, [Atom], 2005
- Martin Atkins, Will Norris, Chris Messina, Monica Wilkinson, Rob Dolin, [AS1], 2010
- James Snell, Evan Prodromou, [AS2], 2018
- Dick Hardt, [OAuth2], 2012
- Ryan Barrett, nightpool, [HTTPSignatures], 2024
- R. Fielding, M. Nottingham, J. Reschke, [CACHING], 2022
- a, Evan Prodromou, [Webfinger], 2024

[ActivityPub]: https://www.w3.org/TR/activitypub/
[RSS1]: https://web.resource.org/rss/1.0/
[RSS2]: https://cyber.harvard.edu/rss/
[Atom]: https://tools.ietf.org/html/rfc4287
[AS1]: https://activitystrea.ms/specs/atom/1.0/
[AS2]: https://www.w3.org/TR/activitystreams-core/
[OAuth2]: https://datatracker.ietf.org/doc/html/rfc6749
[HTTPSignatures]: https://swicg.github.io/activitypub-http-signature/
[CACHING]: https://datatracker.ietf.org/doc/html/rfc9111
[Webfinger]: https://www.w3.org/community/reports/socialcg/CG-FINAL-apwf-20240608/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
