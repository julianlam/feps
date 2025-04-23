# joinMode

URI
: `https://w3id.org/fep/8a8e/joinMode`

rdfs:label
: Join mode

rdfs:comment
: Indicator of how new members may be able to join an event.
Accepted values: `free`, `restricted`, `external`, `none`, `invite`.
If `external`, you must also set [`externalParticipationUrl`](https://w3id.org/fep/8a8e/externalParticipationUrl).

rdfs:domain
: [as:Event](https://www.w3.org/ns/activitystreams#Event)

rdfs:range
: A string

rdfs:isDefinedBy
: [FEP‑8a8e](https://w3id.org/fep/8a8e/)


## Examples

Example: restricted

```json{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "restricted"
}
```

Example: external

```json{
  "@context": [
    "https://w3id.org/fep/8a8e",
    "https://www.w3.org/ns/activitystreams"
  ],
  "type": "Event",
  "url": "http://example.org/events/1234",
  "joinMode": "external",
  "externalParticipationUrl": "https://www.escample.org/events/1234/participate"
}
```
