# timezone

URI
: `https://w3id.org/fep/8a8e/timezone`

Label
: The timezone of an Event

Comment
: Indicates the timezone for which the time(s) indicated in the event are given. The value provided should be among those listed in the IANA Time Zone Database.

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)

Range
: IANA Time Zone identifier

Required
: No

Functional
: No


## Examples

Example usage of timezone

```json
    {
      "@context": [
        "https://w3id.org/fep/8a8e",
        "https://www.w3.org/ns/activitystreams"
      ],
      "type": "Event",
      "id": "https://example.org/events/new-years-party",
      "name": "New years party",
      "startTime": "2014-12-31T23:00:00Z",
      "endTime": "2015-01-01T06:00:00Z",
      "timezone": "Europe/Vienna",
      "organizers": null
    }
    ```
