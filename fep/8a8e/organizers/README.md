# organizers

URI
: `https://w3id.org/fep/8a8e/organizers`

Label
: Organizers Collection

Comment
: An ActivityStreams Collection collection that lists the entities that are disclosed to as organizers of an event. If set to `null` this explicitly indicates a deliberate choice to withhold organizer information.

Range
: [OrganizersCollection](https://w3id.org/fep/8a8e/OrganizersCollection) (SubType of of the Collection or OrderedCollection ActivityStreams Type) or `null`

Required
: Yes

Functional
: No

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example usage of organizers

```json
    {
      "@context": [
        "https://schema.org",
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams",
        {
          "sc": "http://schema.org/"
        }
      ],
      "type": "Event",
      "organizers": {
        "type": "OrganizersCollection",
        "totalItems": 4,
        "items": [
          { "type": "Person", "name": "ActivityPub Person Actor", "id": "https://example.org/actors/1"},
          { "type": "Link", "href": "https://organizer1.example.org"},
          { "type": "sc:Person", "name": "Alice" },
          { "type": "sc:Organization", "name": "Event Co." }
        ]
      }
    }
    ```
