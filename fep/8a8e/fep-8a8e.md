---
slug: "8a8e"
authors: André Menrath <andre.menrath@posteo.de>, les <lesion@autistici.org>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/events-interoperability-validation-minimum-requirements-common-extensions/3849/
dateReceived: 2025-04-23
trackingIssue: https://codeberg.org/fediverse/fep/issues/565
---
# FEP-8a8e: A common approach to using the Event object type

## Summary

ActivityStreams defines the [Object Type `Event`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-event). In real-world applications, the event object immediately showed the need for extension. Applications featuring `Event` objects have often chosen to add additional attributes and clarifications (i.e., interpretations) in order to implement their particular use case. This proposal clarifies and extends the ActivityPub standard to address the needs that have arisen in real-world implementations.

This includes guidelines for the minimal interoperable event, handling of RSVP ("répondez s'il vous plaît", i.e., attendee management, and side effects), attendee capacities, physical location addresses, virtual locations, timezone, and clarification of how to control the visibility of events in federation.

These differences in how the aforementioned features are implemented have led to fragmentation in how events are published, discovered, and managed across platforms.

## What is not covered

We do not cover recurrence, multiple-scheduled, and connected events.

For more information on that, check out for example: 
- [RFC 5545 Section 3.8.5.3](https://www.rfc-editor.org/rfc/rfc5545#section-3.8.5.3)
- [RFC 5545 Section 3.8.4.5](https://www.rfc-editor.org/rfc/rfc5545#section-3.8.4.5)

## History

Fediverse applications, such as Mobilizon, Friendica, Gancio, and Hubzilla, have adopted varying approaches for handling ActivityPub events. Their different aims and the varying use cases have led to fragmentation in how events are published, discovered, and managed across federation.

Friendica and Hubzilla, for instance, follow the example set by ActivityStreams 2.0, using `Invite` for events, which seems to be very suited for smaller, more private gatherings, such as a birthday party. `Invite` seems natural when visibility is intentionally limited. On the other hand, applications like Mobilizon or Gancio have a focus on announcing public events and therefore chose to make use of the `Create` activity. Maybe another reason was that using creates eases interoperability with applications that do not support the `Invite` activity (yet). Furthermore, this may be justified because public events should as well be discoverable by anonymous actors, even by people who do not have an account in the Fediverse. This is achieved through federated event calendars, which are assembled by the instance administrators, who can add various federated event sources by following federated ActivityPub actors.

Within Mobilizon, for historical and internal reasons, the federated visibility of events is currently still controlled by whether a `Group` has published the `Event` or not, and whether the `Event` has also been announced at least once, rather than using `to`/`cc` (e.g., like Mastodon's "public silent"). In federation with other applications, this and other discrepancies led to issues, which have proven to be huge blockers. That's why this FEP sets out to define a common ground.

## Requirements

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”, “SHOULD NOT”, “RECOMMENDED”, “MAY”, and “OPTIONAL” in this specification are to be interpreted as described in [RFC-2119](https://datatracker.ietf.org/doc/html/rfc2119.html).

**The context of attributes:** Attributes that have no context prefix are to be interpreted as being in the `https://www.w3.org/ns/activitystreams` context.

## Object Type Event

The ActivityStreams specification already defines an object type `Event` which is inheriting all properties from the base `Object`, so some properties useful for describing an event are already specified, but some others are missing, and an enhanced specification will help.

For an `Event` at least the following properties are *REQUIRED*:

- [`name`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-name): A simple, human-readable, plain-text title for the event. HTML markup *MUST NOT* be included. Values for the name *MUST NOT* be an empty string and the name *MAY* be expressed using multiple language-tagged values.

- [`startTime`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-startTime): The date and time describing the moment the event began or is scheduled to begin in the format as specified in the [Activity Stream 2.0 specification](https://www.w3.org/TR/activitystreams-core/#dates). The `startTime` is not *REQUIRED* in case an event is postponed and a `https://w3id.org/fep/8a8e/previousStartTime` is set instead.

- [`endTime`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-endTime): The date and time when the event ends or is scheduled to end in the format as specified in the [Activity Stream 2.0 specification](https://www.w3.org/TR/activitystreams-core/#dates). The `endTime` *MUST* be a later date than the `startTime`. If the event is open-ended, it must include an end time at which applications (not humans) can treat the event as having ended.

- [`organizers`](https://w3id.org/fep/8a8e/organizers)

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Event",
  "id": "https://example.org/foo",
  "name": "New years party",
  "startTime": "2014-12-31T23:00:00Z",
  "endTime": "2015-01-01T06:00:00Z",
  "organizers": null,
}
```

### Events with Open End

If the event is open-ended, or the `endTime` is not intended to be displayed to humans, the `https://w3id.org/fep/8a8e/displayEndTime` attribute *SHOULD* be used and set to `false`.

Receiving an `Event` with an `endTime` set and no `https://w3id.org/fep/8a8e/displayEndTime` set, it *MUST* be treated as if `https://w3id.org/fep/8a8e/displayEndTime` is set to `true`, requiring the `endTime` to be displayed.

If an `Event` is received with no `endTime` set, the `Event` *MUST* be treated as if `https://w3id.org/fep/8a8e/displayEndTime` were set to `false` to avoid misleading users. In such cases, the receiving application *MAY* infer an appropriate `endTime` based on its requirements.

### Time zone

_This section is non-normative._

The [`https://w3id.org/fep/8a8e/timezone](`https://w3id.org/fep/8a8e/timezone`) property is introduced to support time zone information for events, enabling consistent handling of local "wall times".

> It is important to note that the "time-offset" component in `startTime` and `endTime` property does not correlate to time-zones, and while times that include the "time-offset" component work well for timestamps, they cannot be reliably converted to and from local "wall times" without additional information and processing.  
> [https://www.w3.org/TR/activitystreams-core/#dates](https://www.w3.org/TR/activitystreams-core/#dates)

For this reason, if the `Event` is primarily conducted in a single specific time-zone, the application *SHOULD* set the `https://w3id.org/fep/8a8e/timezone`.

In case the `https://w3id.org/fep/8a8e/timezone` property is specified it *MUST* be a specific IANA time zone identifier included in the [IANA Time Zone Database](https://data.iana.org/time-zones/tz-link.html) (often called tz or zoneinfo, see [https://www.w3.org/TR/timezone/#time-zone-identifiers](https://www.w3.org/TR/timezone/#time-zone-identifiers)).

<!--
  Evaluated @id / @type for @context:
<!--
  Evaluated @id / @type for @context:
   https://iana.org/time-zones
   https://www.w3.org/2006/timezone
   https://www.w3.org/2006/time#timezone
   https://www.w3.org/2007/uwa/context/common.owl#tzName
   https://www.w3.org/2007/uwa/context/common.owl#TimeZone
   https://www.w3.org/TR/timezone/
   https://www.w3.org/TR/timezone/#tz-definition
   https://www.w3.org/TR/timezone/#time-zone-identifiers -->

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "timezone": "http://www.w3.org/2006/time#timezone"
    }
  ],
  "type": "Event",
  "id": "https://example.org/foo",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00+01:00",
  "endTime": "2015-01-01T04:00:00+01:00",
  "timezone": "Europe/Rome"
}
```


### Location

ActivityStreams provides a flexible framework for representing locations, as outlined in [this section of the specification](https://www.w3.org/TR/activitystreams-vocabulary/#places). However, its flexibility can sometimes lead to ambiguity.

This section aims to establish a clear and consistent format for representing the locations of events, whether they are physical, virtual, or mixed.

Rather than creating a new schema, this specification adopts the [`location` property from Schema.org](https://schema.org/location) with some adjustments to better suite federated event handling:

- Exclusion of `Text` as a valid type:
Unlike the original Schema.org definition, Text is not a permitted type for location and *MUST NOT* be used. If only a name is required to describe a location, the Place type can be used.

- Support for multiple locations:
To specify mixed-format events (e.g., hybrid online and offline events), the location property can contain an array of locations. Each entry in the array can represent either a physical `Place` or a `VirtualLocation`.

#### Physical

For adding information about a physical location of an `Event` the `Place` object within the events `location` property *SHOULD* be extended via the attribute `address` which is of type `https://schema.org/address` or `https://schema.org/Place` *MAY* be used directly.

This allows the address to be given as a simple text input as well as a structured `https://schema.org/PostalAddress`. Applications *MUST* be able to transmogrify both incoming address types to their internal representation.

It is *RECOMMENDED* to always provide geolocation data via `longitude` and `latitude`, as filtering by these properties is crucial in federation.

> **Note**
> Even if users do not provide this data directly, attempting to look up the geolocation of a physical location once on the source side can save a lot of resources caused by multiple lookups on the receivers in federation.

Example with pure text address:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "address": "https://schema.org/address"
    }
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00+01:00",
  "endTime": "2015-01-01T04:00:00+01:00",
  "location": {
    "type": "Place",
    "name": "Foo Bar",
    "address": "15 Fediverse Street, 8010 Fediverse Town, Austria",
    "latitude": 47.06829,
    "longitude": 15.45634
  }
```

Example with address of type `https://schema.org/PostalAddress`:

```json
{
  "@context": [
    "https://schema.org",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "location": {
    "id": "",
    "type": "Place",
    "name": "Foo Bar",
    "address": {
      "type": "PostalAddress",
      "addressCountry": "Austria",
      "addressLocality": "Fediverse Town",
      "addressRegion": "Steiermark",
      "postalCode": "8010",
      "streetAddress": "15 Fediverse Street"
    },
    "latitude": 47.077892,
    "longitude": 15.460744
  }
}
```

#### Virtual

An online Location *SHOULD* be represented by using a type `VirtualLocation` as specified in [https://schema.org/VirtualLocation](https://schema.org/VirtualLocation).

Applications *SHOULD* at least set and be able to make use of `name` and `url` properties.

```json
{
  "@context": [
    "https://schema.org",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "Fediverse Moderation Meeting",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "location": {
    "type": "VirtualLocation",
    "name":"Jitsi Meet Meeting Link",
    "url": "https://jitsi.example.org/fediverse-moderation-meeting"
  }
}
```

#### Hybrid

Using multiple entries in `location` makes it easy to define multiple virtual and physical locations.

When not supporting multiple entries in `location` applications *MUST* use the first supported item.

```json
{
  "@context": [
    "https://schema.org",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "Discussion about the Fediverse",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "location": [
    {
      "type": "Place",
      "name": "Fediverse University",
      "url": "https://university.example.com",
      "address": "15 Fediverse Street, 1337 Fediverse Town, Fediverse Country"
    },
    {
      "type": "VirtualLocation",
      "name": "Big Blue Button Participation Link",
      "url": "https://bbb.example.com/meeting-room-1"
    },
    {
      "type": "VirtualLocation",
      "name": "Live Stream",
      "url": "https://peertube.example.com/fediverse-discussion"
    }
  ]
}
```

### Event status

To indicate the status of an `Event`, the `https://w3id.org/fep/8a8e/eventStatus` property *MUST* be used. As a fallback, it is *RECOMMENDED* to also support the `status` property, especially for incoming remote events, which might contain a value from `https://www.w3.org/2002/12/cal/ical#status`.

The possible values for the `https://w3id.org/fep/8a8e/eventStatus` are:
- [EventCancelled](https://w3id.org/fep/8a8e/EventCancelled)
- [EventMovedOnline](https://w3id.org/fep/8a8e/EventMovedOnline)
- [EventPostponed](https://w3id.org/fep/8a8e/EventPostponed)
- [EventRescheduled](https://w3id.org/fep/8a8e/EventRescheduled)
- [EventScheduled](https://w3id.org/fep/8a8e/EventScheduled)
- [EventTentative](https://w3id.org/fep/8a8e/EventTentative)

> **Note**
> `https://w3id.org/fep/8a8e/eventStatus` is almost identical to `https://schema.org/eventStatus`, however it has an additional status type for the event being tentative, which is leaned on iCalendar's `TENTATIVE`.

### RSVP (Attendee Management)

#### Not handling RSVP

If the event creator or the event creator's application does not handle joins via ActivityPub it *MUST* always respond to `Join` activities with an `Ignore` response, where the attribute `object` *MUST* either contain the ID of the `Join` activity, or contain a `Join` object with the `target` being set to the event-objects ID, where the former is preferred.

This *SHOULD* be made clear beforehand by setting `https://w3id.org/fep/8a8e/joinMode` to `none`.

#### Signaling how joins are handled

If an application does not handle joins of an `Event` via ActivityPub, but knows of an external URL which handles the attendee management `https://w3id.org/fep/8a8e/joinMode` *SHOULD* be set to `external`. If `joinMode` is set to `external`, also `https://w3id.org/fep/8a8e/externalParticipationUrl` *SHOULD* be set.

> **Note**
> This is compatible with Mobilizon's definition of `joinMode`, but it is not identical.

```json
{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/foo",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "joinMode": "external",
  "externalParticipationUrl": "https://example.org/foo#register"
}
```

> **Note**
> `externalParticipationUrl` could also be a `mailto`-URI, which is a way of handling event participants that is still used quite frequently by many organizers.

```json
{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/fediverse-workshop",
  "organizers": null,
  "name": "Fediverse Workshop",
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2025-01-01T04:00:00-08:00",
  "joinMode": "external",
  "externalParticipationUrl": "mailto:fediverse-workshop@example.org"
}
```

#### Indicating visibility and target audience of RSVP requests

Who the participants of an event are should possibly not be public, but should, for example, only be visible to the organisers of the event, in other cases also to other confirmed participants, or, for example, completely anonymously. An Event *SHOULD* provide information about the visibility scope of valid `Join` requests targeting the event via utilizing `https://w3id.org/fep/8a8e/requiredJoinVisibility`.

#### Showing RSVP status via ActivityPub

To specify the maximum number of attendees for an `Event`, applications *SHOULD* use the `https://schema.org/maximumAttendeeCapacity`.

Remaining attendee capacity *SHOULD* be shown indirectly via using the Collection `https://w3id.org/fep/8a8e/attendees`. This is a list of all event attendees. Every `Actor` that has accepted an `Invite` containing the `Event` as an `object` or which `Join` targeting the `Event` has been accepted is added as a side effect. Note that also other object types other than `Actor` (and it's subclasses) might be part of that collection, e.g. when an application allows for attendees to register by e-mail. In that case using `https://schema.org/Person` or `https://schema.org/Organization` is **RECOMMENDED**. The `attendees` collection *MUST* be either an `OrderedCollection` or a `Collection` and *MAY* be filtered by the privileges of an authenticated user, or as appropriate if no authentication is given.

```json
{
  "@context": [
    "https://schema.org",
    "https://www.w3.org/ns/activitystreams",
    {
      "attendees": {
        "@id": "https://w3id.org/fep/8a8e/attendees",
        "@type": "https://www.w3.org/TR/activitystreams-vocabulary/#dfn-collection"
      }
    }
  ],
  "type": "Event",
  "id": "https://example.org/foo-bar-party",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "maximumAttendeeCapacity": 100,
  "attendees": {
     "type": "Collection",
     "id": "https://example.org/foo-bar-party/attendees",
     "totalItems": 84
  }
}
```

#### Attendees Collection

Every [`Event`](https://www.w3.org/ns/activitystreams#Event) *MAY* have an `attendees` collection. This is a list of all [`actor`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-actor)s that meet one or more of the following conditions, added as a [side effect](https://www.w3.org/TR/activitypub/#like-activity-inbox).

- The actor has sent a [`Join`](https://www.w3.org/ns/activitystreams#Join) activity with this object as the [`object`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-object) property that has been answered with an [`Accept`](https://www.w3.org/ns/activitystreams#Accept).
- The actor has responded to an [`Invite`](https://www.w3.org/ns/activitystreams#Invite) activity from the `Event`'s owner (where the Event is specified as the `object` property) with an [`Accept`](https://www.w3.org/ns/activitystreams#Accept) activity.

The `attendees` collection *MUST* be either an [`OrderedCollection`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) or a [`Collection`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-collection) and *MAY* be filtered on privileges of an authenticated user or as appropriate when no authentication is given. This collection *MAY* have the [`totalItems`](https://www.w3.org/ns/activitystreams#totalItems) set regardless of authentication. If `https://schema.org/maximumAttendeeCapacity` is used `totalItems` *SHOULD* be public to disclose remaining capacity.

### Event Banner and Poster Images

#### Flyer

If the event has an image in the style of a flyer or a share-pic which is representing the whole event (i.e., is also containing at least the name and start-date in the image) this image *SHOULD* be set using the `image` attribute.

#### Banner

If the `Event` has a particular banner image, this image *SHOULD* be set as the first `attachment` of type `Image` (type `Document` is also valid but not *RECOMMENDED*). To indicate that an image from within the `attachment` attribute of an `Event` should be preferred over the flyer/share-pic image(s) within `image` attribute, for the use of list pages and header images, the attribute `https://w3id.org/fep/8a8e/isBannerImage` *SHOULD* be set.

Federated event calendars usually have thumbnail images with fixed aspect ratios. Therefore, `https://docs.joinmastodon.org/spec/activitypub/#focalPoint` *SHOULD* be set.

> **Note**
> Providing multiple versions of banner images and specifying `width` and `height` gives receiving applications the most flexibility to choose the most appropriate one based on aspect ratio.

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "toot": "http://joinmastodon.org/ns#",
      "focalPoint": {
        "@container": "@list",
        "@id": "toot:focalPoint"
      }
    }
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "image": {
    "type": "Image",
    "mediaType": "image/jpeg",
    "url": "https://example.com/images/new-year-party-flyer.png",
    "focalPoint": [
      -0.55,
      0.43
    ]
  }
}
```
### Event Categories

Federated event platforms benefit from a shared understanding of general event categories. These categories serve a distinct purpose from user-generated tags or hashtags. While hashtags are typically entered freely and reflect a specific language, event categories are drawn from a limited, generalized set, making them more suitable for tasks like filtering events in aggregated or joined calendars.

To represent categories, this FEP introduces the property [https://w3id.org/fep/8a8e/category](`https://w3id.org/fep/8a8e/category`).

In most cases, a single category should be sufficient. However, multiple categories may be included when relevant.
Applications *SHOULD* utilize at least the following recommended set of event categories:

- ARTS
- AUTO_BOAT_AIR
- BOOK_CLUBS
- BUSINESS
- CAUSES
- CLIMATE_ENVIRONMENT
- COMMUNITY
- COMEDY
- CRAFTS
- CREATIVE_JAM
- DIY_MAKER_SPACES
- FAMILY_EDUCATION
- FASHION_BEAUTY
- FESTIVALS
- FILM_MEDIA
- FOOD_DRINK
- GAMES
- INCLUSIVE_SPACES
- LANGUAGE_CULTURE
- LEARNING
- LGBTQ
- MEETING
- MEDITATION_WELLBEING
- MOVEMENTS_POLITICS
- MUSIC
- NETWORKING
- OUTDOORS_ADVENTURE
- PARTY
- PERFORMING_VISUAL_ARTS
- PETS
- PHOTOGRAPHY
- SCIENCE_TECH
- SPIRITUALITY_RELIGION_BELIEFS
- SPORTS
- THEATRE
- WORKSHOPS_SKILL_SHARING

> **Note**
> Implementing applications may extend this list or allow user-generated categories. However, such additions may not be understood by all consuming platforms and could default to a generic or "unknown" category.

#### Example of an event with a single category

```json
{
  "@context": [
    "https://https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams",
  ],
  "type": "Event",
  "id": "https://example.org/event/1",
  "name": "Demonstration againt fascism",
  "startTime": "2014-05-01T12:00:00-08:00",
  "startTime": "2014-05-01T18:00:00-08:00",
  "organizer": null,
  "category": "MOVEMENTS_POLITICS"
}
```

#### Example of an event with multiple categories

```json
{
  "@context": [
    "https://https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams",
  ],
  "type": "Event",
  "id": "https://example.org/open-mic-jam",
  "name": "Open Mic Jam at Sunny's",
  "startTime": "2014-12-12T20:00:00-08:00",
  "endTime": "2014-12-12T23:00:00-08:00",
  "organizer": null,
  "category": [
    "MUSIC",
    "CREATIVE_JAM"
  ]
}
```


### Discoverability

Fediverse applications that feature `Event` objects *MAY* provide public calendars, search functions or grouped visualization pages (e.g., for tags or categories) that display events from multiple federated sources.
In both cases these *MUST* never include events from federation that do not have `https://www.w3.org/ns/activitystreams#Public` (also `as:Public` or `Public` is valid) set in `to`. However, they *MAY* appear within a local representation of a remote actor, if `Public` set in `cc`.

The discoverability of an incoming event from federation *MUST NOT* be controlled by the type of the actor set in `attributedTo` or by the `Activity` the event was received (e.g., `Announce`, `Create`).

### Organizers Collection

Events *SHOULD* indicate their organizers by using `https://w3id.org/fep/8a8e/organizers`.
The `organizers` collection helps provide clarity about the event's management, supports federated discovery, and improves interoperability across platforms.

The value of the `organizers` field *MUST* be either an `OrderedCollection` or a `Collection`.
The `items` within this collection *MAY* include [actors](https://www.w3.org/TR/activitystreams-core/#actors), or [links](https://www.w3.org/TR/activitystreams-core/#link).
If the organizer is not an ActivityPub entity (e.g., a website or organization without an actor), it is recommended to either use a `Link` or `https://schema.org/Person` or `https://schema.org/Organization`.

```json
{
  "@context": [
    "https://schema.org",
    "https://https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams",
  ],
  "type": "Event",
  "id": "https://example.org/foo-bar-party",
  "name": "New Year's Party",
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "organizers": {
    "type": "OrganizersCollection",
    "id": "https://example.org/foo-bar-party/organizers",
    "totalItems": 3,
    "first": {
      "type": "CollectionPage",
      "partOf": "https://example.org/foo-bar-party/organizers",
      "items": [
        "https://example.social/users/johnmastodon",
        "https://example.org/somewebsite",
        {
          "type": "Organization",
          "id": "https://example.events/actors/eventorganizer",
          "context": "https://example.events/actors/eventorganizer/accept/example.org-foo-bar-party-offer"
        }
      ]
    }
  }
}
```

#### Explicit Non-Disclosure

If the event’s organizers are intentionally not disclosed, the `organizers` field *MUST* be set to `null`, have `totalItems: 0`, or contain an empty `items` array. This explicitly indicates a deliberate choice to withhold organizer information and takes precedence over any assumptions about organizers based on other fields. In such a case, when receiving an event, clients *MUST NOT* infer organizers from other event data.

#### Fallback to `attributedTo`

If the `organizers` property is omitted, it *MAY* be inferred that the actors in the `attributedTo` property are the event's organizers. For events with multiple organizers, it is *RECOMMENDED* to provide an `organizers` collection to avoid and ensure compatibility with applications that do not support arrays in `attributedTo`.

## Upcoming Events Collection for Actors

Every `actor` that has published `Event`s *SHOULD* have a `https://w3id.org/fep/8a8e/upcomingEvents` collection to list their future or ongoing events. This collection *MUST* follow these rules:

- **Collection Type**:  
  The collection *MUST* be an `OrderedCollection` or one of its subtypes.

- **Ordering**:
  Events *MUST* be ordered in ascending order by their `startTime`, with the earliest events appearing first.

- **Items**:  
  Each item in the collection *MUST* meet the following criteria:  
  - **Type**: The item *MUST* be of type `Event` or one of its subtypes.  
  - **Time**: The `Event`'s `endTime` *MUST NOT* be earlier than the current time, i.e., the event is ongoing or scheduled in the future.  
  - **Actor Involvement**: At least one of the following conditions *MUST* apply:  
    - The `Actor` is included in the `Event`'s `organizers` collection.
    - The `Actor` owns the `Event`, i.e., is part of the `Event`'s `attributedTo`.
    - The `Event` is in the actor's `shares` collection, and the `Event` shares the same host with the `actor`. This use case is primarily intended to cover relay and group `Actor`s.

## Terms

Note that the terms `joinMode` and `externalParticipationUrl` are compatible with and also leaned on the extensions [defined by Mobilizon](https://docs.mobilizon.org/5.%20Interoperability/1.activity_pub/).

<section id="displayEndTime" resource="https://w3id.org/fep/8a8e/displayEndTime" typeof="owl:DatatypeProperty">
  <h3>displayEndTime</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/displayEndTime</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">Whether to display the endTime</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">A property that defines whether the end time of an event should be displayed.</dd>
    <dt>Domain</dt>
    <dd><a property="rdfs:domain" href="https://w3id.org/fep/8a8e/displayEndTime">displayEndTime</a></dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="xsd:boolean">Boolean</dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example usage of displayEndTime" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams"
      ],
      "type": "Event",
      "displayEndTime": false
    }
    </code>
  </pre>
</section>

<section id="upcomingEvents" resource="https://w3id.org/fep/8a8e/upcomingEvents" typeof="owl:ObjectProperty">
  <h3>upcomingEvents</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/upcomingEvents</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">Ordered collection of upcoming Events</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">An ActivityStreams OrderedCollection of Event objects that have a startTime property in the future, sorted by startTime with the earliest first.</dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="as:OrderedCollection">An OrderedCollection (@id)</dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example usage of upcomingEvents" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams"
      ],
      "@type": "Actor",
      "upcomingEvents": {
        "type": "Collection",
        "items": [
          { "type": "Event", "startTime": "2025-06-01T12:00:00Z" },
          { "type": "Event", "startTime": "2025-07-15T15:30:00Z" }
        ]
      }
    }
    </code>
  </pre>
</section>

<section id="OrganizersCollection" resource="https://w3id.org/fep/8a8e/OrganizersCollection" typeof="rdfs:Class">
  <h3>OrganizersCollection</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/OrganizersCollection</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">An Event's Organizer Collection</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">Inherits all properties from <code><a href="https://www.w3.org/ns/activitystreams#Collection">https://www.w3.org/ns/activitystreams#Collection</a></code> with the addition that the <code>items</code> may also include <code>https://schema.org/Person</code> or <code>https://schema.org/Organization</code>.</dd>
    <dt>Subclass of</dt>
    <dd><a property="rdfs:subClassOf" href="https://www.w3.org/ns/activitystreams#Collection">Object</dd>
    <dt>See also</dt>
    <dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/organizers">organizers</a></dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example of an OrganizersCollection with different items" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams",
        {
          "sc": "http://schema.org#",
        }
      ],
      "type": "OrganizersCollection",
      "items": [
        { "type": "Group", "name": "ActivityPub Group Actor", "id": "https://example.org/actors/group1"},
        { "type": "Link", "href": "https://organizer1.example.org"},
        { "type": "sc:Person", "name": "Alice" },
        { "type": "Organization", "name": "Event Co." }
      ]
    }
    </code>
  </pre>
</section>

<section id="organizers" resource="https://w3id.org/fep/8a8e/organizers" typeof="owl:ObjectProperty">
  <h3>organizers</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/organizers</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">Organizers Collection</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">An ActivityStreams Collection collection that lists the entities that are disclosed to as organizers of an event. If set to <code>null</code> this explicitly indicates a deliberate choice to withhold organizer information.</dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="https://w3id.org/fep/8a8e/OrganizersCollection"><a href="https://w3id.org/fep/8a8e/OrganizersCollection" target="_blank">OrganizersCollection</a> (SubType of of the Collection or OrderedCollection ActivityStreams Type) or <code>null</code></dd>
    <dt>Required</dt>
    <dd>Yes</dd>
    <dt>Functional</dt>
    <dd>No</dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example usage of organizers" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams",
        {
          "sc": "http://schema.org#",
        }
      ],
      "type": "Event",
      "organizers": {
        "type": "OrganizersCollection",
        "totalItems": 4,
        "items": [
          { "type": "Actor", "name": "ActivityPub Group Actor", "id": "https://example.org/actors/group1"},
          { "type": "Link", "href": "https://organizer1.example.org"},
          { "type": "sc:Person", "name": "Alice" },
          { "type": "sc:Organization", "name": "Event Co." }
        ]
      }
    }
    </code>
  </pre>
</section>

<section id="AttendeesCollection" resource="https://w3id.org/fep/8a8e/AttendeesCollection" typeof="rdfs:Class">
  <h3>AttendeesCollection</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/AttendeesCollection</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">A Collection of the Event's attendees</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">
      Inherits all properties from <code><a href="https://www.w3.org/ns/activitystreams#Collection">https://www.w3.org/ns/activitystreams#Collection</a></code> with the addition that the <code>items</code> may also include <code>https://schema.org/Person</code> or <code>https://schema.org/Organization</code>.
      The items of the <code>AttendeesCollection</code> are entities that are confirmed attendees by an Events organizer(s). It contains all ActivityPub actors that meet one or more of the following conditions, added as a side effect.
      <ul>
        <li>The actor has sent a Join activity with this object as the object property that has been answered with an Accept.</li>
        <li>The actor has responded to an Invite activity from the Event's owner (where the Event is specified as the object property) with an Accept activity.</li>
      </ul>
      The items MAY be filtered on privileges of an authenticated user or as appropriate when no authentication is given. This collection *SHOULD* have the totalItems set in any case.
    </dd>
    <dt>Subclass of</dt>
    <dd><a property="rdfs:subClassOf" href="https://www.w3.org/ns/activitystreams#OrderedCollection">Object</dd>
    <dt>See also</dt>
    <dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/attendees">attendees</a></dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example of an AttendeesCollection with different items" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams",
        {
          "sc": "https://schema.org#"
        }
      ]
      "type": "AttendeesCollection",
      "totalItems": 2,
      "context": "https://example.org/events/alice-birthday-party"
      "items": [
        { "type": "Person", "name": "Bob", "id": "https://example.org/actors/bob"},
        { "type": "sc:Person", "name": "Alice", "email": "alice@example.org"},
      ]
    }
    </code>
  </pre>
</section>

<section id="attendees" resource="https://w3id.org/fep/8a8e/attendees" typeof="owl:ObjectProperty">
  <h3>attendees</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/attendees</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">Attendees of an Event</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en"></dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="rdfs:Resource"><a href="https://w3id.org/fep/8a8e/AttendeesCollection" target="_blank">Collection</a> (ActivityStreams Type)</dd>
    <dt>Required</dt>
    <dd property="owl:minCardinality" content="0" datatype="xsd:nonNegativeInteger">No</dd>
    <dt>Functional</dt>
    <dd>No</dd>
  </dl>
  <pre title="Example usage of attendees" lang="json">
    <code>
    {
      "@context": [
        "https://schema.org",
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams",
        {
          "sc": "https://schema.org#"
        }
      ],
      "type": "Event",
      "attendees": {
        "type": "https://w3id.org/fep/8a8e/OrganizersCollection",
        "totalItems": 4,
        "items": [
          { "type": "Actor", "name": "ActivityPub Group Actor", "id": "https://example.org/actors/group1"},
          { "type": "Link", "href": "https://organizer1.example.org"},
          { "type": "Person", "name": "Alice" },
          { "type": "sc:Organization", "name": "Event Co." }
        ]
      }
    }
    </code>
  </pre>
</section>

<section id="timezone" resource="https://w3id.org/fep/8a8e/timezone" typeof="owl:ObjectProperty">
  <h3>timezone</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/timezone</code></dd>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">The timezone of an Event</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">Indicates the timezone for which the time(s) indicated in the event are given. The value provided should be among those listed in the IANA Time Zone Database.</dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="rdfs:Literal">IANA Time Zone identifier</a></dd>
    <dt>Required</dt>
    <dd>No</dd>
    <dt>Functional</dt>
    <dd>No</dd>
  </dl>
  <pre title="Example usage of timezone" lang="json">
    <code>
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams"
      ]
      "type": "Event",
      "id": "https://example.org/events/new-years-party",
      "name": "New years party",
      "startTime": "2014-12-31T23:00:00Z",
      "endTime": "2015-01-01T06:00:00Z",
      "timezone": "Europe/Vienna",
      "organizers": null,
    }
    </code>
  </pre>
</section>

<section id="joinMode" resource="https://w3id.org/fep/8a8e/joinMode" typeof="owl:ObjectProperty">
  <h3>joinMode</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/joinMode</code></dd>
    <dt>rdfs:label</dt>
    <dd property="rdfs:label" lang="en">Join mode</dd>
    <dt>rdfs:comment</dt>
    <dd property="rdfs:comment" lang="en">
      Indicator of how new members may be able to join an event.
      Accepted values: <code>free</code>, <code>restricted</code>, <code>external</code>, <code>none</code>, <code>invite</code>.
      If <code>external</code>, you must also set <a href="https://w3id.org/fep/8a8e/externalParticipationUrl"><code>externalParticipationUrl</code></a>.
    </dd>
    <dt>rdfs:domain</dt>
    <dd>
      <a property="rdfs:domain" href="https://www.w3.org/ns/activitystreams#Event">as:Event</a>
    </dd>
    <dt>rdfs:range</dt>
    <dd property="rdfs:range" resource="xsd:string">A string</a></dd>
    <dt>rdfs:isDefinedBy</dt>
    <dd>
      <a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e/">FEP‑8a8e</a>
    </dd>
  </dl>

  <pre title="Example: restricted" lang="json">
<code>{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "restricted"
}
</code>
  </pre>

  <pre title="Example: external" lang="json">
<code>{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "external",
  "externalParticipationUrl": "https://www.escample.org/events/1234/participate"
}
</code>
  </pre>
</section>

<section id="requiredJoinVisibility" resource="https://w3id.org/fep/8a8e/requiredJoinVisibility" typeof="owl:ObjectProperty">
  <h3>requiredJoinVisibility</h3>
  <dl>
    <dt>Label</dt>
    <dd property="rdfs:label" lang="en">Required Join Visibility</dd>
    <dt>Comment</dt>
    <dd property="rdfs:comment" lang="en">
      Specifies the minimum audience that must be addressed in a valid <code>Join</code> activity related to the event. This can include individual actors, groups, the <code>as:Public</code> collection, or any other URI. The <code>Join</code> activity must be addressed accordingly (e.g., using <code>to</code>, <code>cc</code>, <code>bto</code>, or <code>audience</code>).
    </dd>
    <dt>Domain</dt>
    <dd property="rdfs:domain"><a href="https://www.w3.org/ns/activitystreams#Event">as:Event</a></dd>
    <dt>Range</dt>
    <dd property="rdfs:range" resource="xsd:anyURI"> A list of any addressed targets, i.e. URIs (@list)</dd>
    <dt>Is defined by</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
  </dl>
  <pre title="Example usage of requiredJoinVisibility" lang="json">
<code>{
   "@context": [
    "https://schema.org",
    "https://https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/yoga-workshop",
  "name": "Yoga Workshop with Alice and Bob",
  "startTime": "2014-12-12T18:00:00-08:00",
  "endTime": "2014-12-12T19:30:00-08:00",
  "attributedTo": "https://example.org/groups/fediyoga",
  "organizers": {
    "type": "OrganizersCollection",
    "id": "https://example.org/yoga-workshop/organizers",
    "totalItems": 3,
    "first": {
      "type": "CollectionPage",
      "partOf": "https://example.org/yoga-workshop/organizers",
      "items": [
        "https://example.org/users/bob",
        "https://example.org/users/alice",
        "https://example.org/groups/fediyoga"
      ]
    },
  "joinMode": "restricted",
  "requiredJoinVisibility": [
    "https://example.org/yoga-with-alice/organizers"
  ]
}</code>
  </pre>
</section>

<section id="externalParticipationUrl" resource="https://w3id.org/fep/8a8e/externalParticipationUrl" typeof="owl:DatatypeProperty">
  <h3>externalParticipationUrl</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/externalParticipationUrl</code></dd>
    <dt>rdfs:label</dt>
    <dd property="rdfs:label" lang="en">External participation URL</dd>
    <dt>rdfs:comment</dt>
    <dd property="rdfs:comment" lang="en">
      A URL that points to an external platform where people can join the event or where they can buy tickets for the event. Required if <a href="https://w3id.org/fep/8a8e/"><code>joinMode</code></a> is set to <code>external</code>.
    </dd>
    <dt>rdfs:domain</dt>
    <dd><a property="rdfs:domain" href="https://www.w3.org/ns/activitystreams#Event">as:Event</a></dd>
    <dt>rdfs:range</dt>
    <dd property="rdfs:range" resource="xsd:anyURI">xsd:anyURI</dd>
    <dt>rdfs:isDefinedBy</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP‑8a8e</a></dd>
  </dl>

  <pre title="Example usage of externalParticipationUrl" lang="json">
<code>{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "external",
  "externalParticipationUrl": "https://www.meetup.com/somegroup/events/00000/"
}
</code>
  </pre>
</section>

<section id="isBannerImage" resource="https://w3id.org/fep/8a8e/isBannerImage" typeof="owl:DatatypeProperty">
  <h3>isBannerImage</h3>
  <dl>
    <dt>URI</dt>
    <dd><code>https://w3id.org/fep/8a8e/isBannerImage</code></dd>
    <dt>rdfs:label</dt>
    <dd property="rdfs:label" lang="en">Image is a banner image</dd>
    <dt>rdfs:comment</dt>
    <dd property="rdfs:comment" lang="en">
      Whether an image is an (events) banner image.
    </dd>
    <dt>rdfs:domain</dt>
    <dd><a property="rdfs:domain" href="https://www.w3.org/ns/activitystreams#Image">as:Image</a></dd>
    <dt>rdfs:range</dt>
    <dd property="rdfs:range" resource="xsd:boolean">Boolean</dd>
    <dt>rdfs:isDefinedBy</dt>
    <dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP‑8a8e</a></dd>
  </dl>

  <pre title="Example usage of isBannerImage" lang="json">
<code>{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "id": "https://example.org/new-year-party",
  "name": "New years party",
  "organizers": null,
  "startTime": "2014-12-31T23:00:00-08:00",
  "endTime": "2015-01-01T04:00:00-08:00",
  "image": {
    "type": "Image",
    "mediaType": "image/jpeg",
    "url": "https://example.com/images/new-year-party-flyer.png",
    "focalPoint": [
      -0.55,
      0.43
    ]
  },
  "attachment": [
    {
      "type": "Image",
      "mediaType": "image/jpeg",
      "url": "https://example.com/images/new-year-party-banner.png",
      "witdh": 1000,
      "height": 500,
      "isBannerImage": true
    }
  ]
}
</code>
  </pre>
</section>

<section id="eventStatus" resource="https://w3id.org/fep/8a8e/eventStatus" typeof="rdf:Property">
<h3>eventStatus</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/eventStatus</code></dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The events status is</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">An eventStatus of an event represents its status; particularly useful when an event is cancelled or rescheduled.</dd>
<dt>Domain</dt>
<dd><a property="rdfs:domain" resource="as:Event" href="https://www.w3.org/ns/activitystreams#Event">Event</a></dd>
<dt>Range</dt>
<dd><a property="rdfs:range" resource="https://w3id.org/fep/8a8e/EventStatusType" href="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</a> (@vocab)</dd>
<dt>Required</dt>
<dd property="owl:minCardinality" content="0" datatype="xsd:nonNegativeInteger">No</dd>
<dt>Functional</dt>
<dd property="owl:maxCardinality" content="1" datatype="xsd:nonNegativeInteger">Yes</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventCancelled">EventCancelled</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventScheduled">EventScheduled</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventTentative">EventTentative</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventMovedOnline">EventMovedOnline</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventPostponed">EventPostponed</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventRescheduled">EventRescheduled</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
<pre title="Example of a forward chronological OrderedCollection with additional context">
<code>
{
  "@context": [
    "https://w3id.org/fep/8a8e"
    "https://www.w3.org/ns/activitystreams",
  ],
  "id": "https://domain.example/events/0",
  "type": "Event",
  "eventStatus": "eventScheduled",
}
</code>
</pre>
</section>

<section id="EventStatusType" resource="https://w3id.org/fep/8a8e/EventStatusType" typeof="rdfs:Class">
<h3>EventStatusType</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/8a8e</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">8a8e</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">EventStatusType is an enumeration type whose instances represent several states that an Event may be in.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://schema.org/EventStatusType">https://schema.org/EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventPostponed" resource="https://w3id.org/fep/8a8e/EventPostponed" typeof="rdfs:Class">
<h3>EventCancelled</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/EventPostponed</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event has been postponed.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The event has been postponed and no new date has been set. The event's previousStartTime should be set.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventRescheduled" resource="https://w3id.org/fep/8a8e/EventRescheduled" typeof="rdfs:Class">
<h3>EventRescheduled</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/EventRescheduled</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event has been rescheduled.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The event's previousStartTime should be set to the old date and the startTime should be set to the event's new start date.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventCancelled" resource="https://w3id.org/fep/8a8e/EventCancelled" typeof="rdfs:Class">
<h3>EventCancelled</h3>
<dl>
<dt>URI</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventPostponed">EventPostponed</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventRescheduled">EventRescheduled</a></dd>
<dd><code>https://w3id.org/fep/8a8e/EventCancelled</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event has been cancelled.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The event has been cancelled.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventCancelled" resource="https://w3id.org/fep/8a8e/EventCancelled" typeof="rdfs:Class">
<h3>EventCancelled</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/EventCancelled</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event has been cancelled.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The event has been cancelled.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventTentative" resource="https://w3id.org/fep/8a8e/EventTentative" typeof="rdfs:Class">
<h3>EventTentative</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/EventTentative</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event is tentative</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The event is currently being planned but not confirmed.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="EventMovedOnline" resource="https://w3id.org/fep/8a8e/EventMovedOnline" typeof="rdfs:Class">
<h3>EventMovedOnline</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/EventMovedOnline</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event moved online.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">Indicates that the event was changed to allow online participation.</dd>
<dt>Subclass of</dt>
<dd property="rdfs:subClassOf" resource="https://w3id.org/fep/8a8e/EventStatusType">EventStatusType</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/eventStatus">eventStatus</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="previousStartTime" resource="https://w3id.org/fep/8a8e/previousStartTime" typeof="owl:DatatypeProperty">
<h3>previousStartTime</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/previousStartTime</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The event previous start time.</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">The events previous start time is the old start time before an event got postponed or rescheduled.</dd>
<dt>Domain</dt>
<dd><a property="rdfs:domain" resource="as:Event" href="https://www.w3.org/ns/activitystreams#Event">Event</a></dd>
<dt>Range</dt>
<dd><a property="rdfs:range" resource="xsd:dateTime" href="https://www.w3.org/TR/xmlschema-2/#dateTime">xsd:dateTime</a> (@vocab)</dd>
<dt>See also</dt>
<dd><a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventPostponed">EventPostponed</a> | <a property="rdfs:seeAlso" href="https://w3id.org/fep/8a8e/EventRescheduled">EventRescheduled</a></dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

<section id="category" resource="https://w3id.org/fep/8a8e/category" typeof="owl:DatatypeProperty">
<h3>category</h3>
<dl>
<dt>URI</dt>
<dd><code>https://w3id.org/fep/8a8e/category</code>
</dd>
<dt>Label</dt>
<dd property="rdfs:label" lang="en">The category of an Event</dd>
<dt>Comment</dt>
<dd property="rdfs:comment" lang="en">Recommended event categories include: <code>ARTS</code>, <code>AUTO_BOAT_AIR</code>, <code>BOOK_CLUBS</code>, <code>BUSINESS</code>, <code>CAUSES</code>, <code>CLIMATE_ENVIRONMENT</code>, <code>COMMUNITY</code>, <code>COMEDY</code>, <code>CRAFTS</code>, <code>CREATIVE_JAM</code>, <code>DIY_MAKER_SPACES</code>, <code>FAMILY_EDUCATION</code>, <code>FASHION_BEAUTY</code>, <code>FESTIVALS</code>, <code>FILM_MEDIA</code>, <code>FOOD_DRINK</code>, <code>GAMES</code>, <code>INCLUSIVE_SPACES</code>, <code>LANGUAGE_CULTURE</code>, <code>LEARNING</code>, <code>LGBTQ</code>, <code>MEETING</code>, <code>MEDITATION_WELLBEING</code>, <code>MOVEMENTS_POLITICS</code>, <code>MUSIC</code>, <code>NETWORKING</code>, <code>OUTDOORS_ADVENTURE</code>, <code>PARTY</code>, <code>PERFORMING_VISUAL_ARTS</code>, <code>PETS</code>, <code>PHOTOGRAPHY</code>, <code>SCIENCE_TECH</code>, <code>SPIRITUALITY_RELIGION_BELIEFS</code>, <code>SPORTS</code>, <code>THEATRE</code>, <code>WORKSHOPS_SKILL_SHARING</code>
</dd>
<dt>Domain</dt>
<dd><a property="rdfs:domain" resource="as:Event" href="https://www.w3.org/ns/activitystreams#Event">Event</a></dd>
<dt>Range</dt>
<dd><a property="rdfs:range" resource="xsd:string" href="https://www.w3.org/TR/xmlschema-2/#string">xsd:string</a> (@list)</dd>
<dt>Is defined by</dt>
<dd><a property="rdfs:isDefinedBy" href="https://w3id.org/fep/8a8e">FEP-8a8e</a></dd>
</dl>
</section>

## Credits

This work would not have been possible without the support of [NLnet foundation](https://nlnet.nl/) and [NGI Zero](https://nlnet.nl/NGI0/).

Thanks are also expressed to the people at OFFDEM who laid out [the beginnings of this document](https://event-federation.eu/2024/02/10/fediversity-at-o%e2%82%84ffdem/).

Special thanks go to Laurin Weger, who was available for many time-consuming discussions. Further thanks go to the Cloudfest Hackathon 2025 for providing space and a platform for further discussion of this FEP and especially to Andreas Heigl for his rich feedback and ideas.

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
