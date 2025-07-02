# requiredJoinVisibility

Label
: Required Join Visibility

Comment
: Specifies the minimum audience that must be addressed in a valid `Join` activity related to the event. This can include individual actors, groups, the `as:Public` collection, or any other URI. The `Join` activity must be addressed accordingly (e.g., using `to`, `cc`, `bto`, or `audience`).

Domain
: [as:Event](https://www.w3.org/ns/activitystreams#Event)

Range
:  A list of any addressed targets, i.e. URIs (@list)

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example usage of requiredJoinVisibility

```json{
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
    "https://example.org/yoga-workshop/organizers"
  ]
}```
