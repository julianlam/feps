# isBannerImage

URI
: `https://w3id.org/fep/8a8e/isBannerImage`

rdfs:label
: Image is a banner image

rdfs:comment
: Whether an image is an (events) banner image.

rdfs:domain
: [as:Image](https://www.w3.org/ns/activitystreams#Image)

rdfs:range
: Boolean

rdfs:isDefinedBy
: [FEP‑8a8e](https://w3id.org/fep/8a8e)


## Examples

Example usage of isBannerImage

```json{
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
```
