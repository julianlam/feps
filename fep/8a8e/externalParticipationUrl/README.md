# externalParticipationUrl

URI
: `https://w3id.org/fep/8a8e/externalParticipationUrl`

rdfs:label
: External participation URL

rdfs:comment
: A URL that points to an external platform where people can join the event or where they can buy tickets for the event. Required if [`joinMode`](https://w3id.org/fep/8a8e/) is set to `external`.

rdfs:domain
: [as:Event](https://www.w3.org/ns/activitystreams#Event)

rdfs:range
: xsd:anyURI

rdfs:isDefinedBy
: [FEP‑8a8e](https://w3id.org/fep/8a8e)


## Examples

Example usage of externalParticipationUrl

```json{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "external",
  "externalParticipationUrl": "https://www.meetup.com/somegroup/events/00000/"
}
```
