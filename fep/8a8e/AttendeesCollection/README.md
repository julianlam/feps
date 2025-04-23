# AttendeesCollection

URI
: `https://w3id.org/fep/8a8e/AttendeesCollection`

Label
: A Collection of the Event's attendees

Comment
: Inherits all properties from `https://www.w3.org/ns/activitystreams#Collection` with the addition that the `items` may also include `https://schema.org/Person` or `https://schema.org/Organization`.
The items of the `AttendeesCollection` are entities that are confirmed attendees by an Events organizer(s). It contains all ActivityPub actors that meet one or more of the following conditions, added as a side effect.

* The actor has sent a Join activity with this object as the object property that has been answered with an Accept.
* The actor has responded to an Invite activity from the Event's owner (where the Event is specified as the object property) with an Accept activity.

The items MAY be filtered on privileges of an authenticated user or as appropriate when no authentication is given. This collection \*SHOULD\* have the totalItems set in any case.

Subclass of
: [Object](https://www.w3.org/ns/activitystreams#OrderedCollection)

See also
: [attendees](https://w3id.org/fep/8a8e/attendees)

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example of an AttendeesCollection with different items

```json
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
    ```
