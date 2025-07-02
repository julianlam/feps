# attendees

URI
: `https://w3id.org/fep/8a8e/attendees`

Label
: Attendees of an Event

Comment
: 

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)

Range
: [Collection](https://w3id.org/fep/8a8e/AttendeesCollection) (ActivityStreams Type)

Required
: No

Functional
: No


## Examples

Example usage of attendees

```json
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
        "type": "OrganizersCollection",
        "totalItems": 4,
        "items": [
          { "type": "Person", "name": "ActivityPub Person", "id": "https://example.org/actors/1"},
          { "type": "Link", "href": "https://organizer1.example.org"},
          { "type": "sc:Person", "name": "Alice" },
          { "type": "sc:Organization", "name": "Event Co." }
        ]
      }
    }
    ```
