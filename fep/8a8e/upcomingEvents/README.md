# upcomingEvents

URI
: `https://w3id.org/fep/8a8e/upcomingEvents`

Label
: Ordered collection of upcoming Events

Comment
: An ActivityStreams OrderedCollection of Event objects that have a startTime property in the future, sorted by startTime with the earliest first.

Range
: An OrderedCollection (@id)

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example usage of upcomingEvents

```json
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams"
      ],
      "type": "Organization",
      "upcomingEvents": {
        "type": "OrderedCollection",
        "items": [
          { "type": "Event", "startTime": "2025-06-01T12:00:00Z" },
          { "type": "Event", "startTime": "2025-07-15T15:30:00Z" }
        ]
      }
    }
    ```
