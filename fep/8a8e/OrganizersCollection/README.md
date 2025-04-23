# OrganizersCollection

URI
: `https://w3id.org/fep/8a8e/OrganizersCollection`

Label
: An Event's Organizer Collection

Comment
: Inherits all properties from `https://www.w3.org/ns/activitystreams#Collection` with the addition that the `items` may also include `https://schema.org/Person` or `https://schema.org/Organization`.

Subclass of
: [Object](https://www.w3.org/ns/activitystreams#Collection)

See also
: [organizers](https://w3id.org/fep/8a8e/organizers)

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example of an OrganizersCollection with different items

```json
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
    ```
