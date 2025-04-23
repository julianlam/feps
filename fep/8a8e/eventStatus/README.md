# eventStatus

URI
: `https://w3id.org/fep/8a8e/eventStatus`

Label
: The events status is

Comment
: An eventStatus of an event represents its status; particularly useful when an event is cancelled or rescheduled.

Domain
: [Event](https://www.w3.org/ns/activitystreams#Event)

Range
: [EventStatusType](https://w3id.org/fep/8a8e/EventStatusType) (@vocab)

Required
: No

Functional
: Yes

See also
: [EventCancelled](https://w3id.org/fep/8a8e/EventCancelled) | [EventScheduled](https://w3id.org/fep/8a8e/EventScheduled) | [EventTentative](https://w3id.org/fep/8a8e/EventTentative) | [EventMovedOnline](https://w3id.org/fep/8a8e/EventMovedOnline) | [EventPostponed](https://w3id.org/fep/8a8e/EventPostponed) | [EventRescheduled](https://w3id.org/fep/8a8e/EventRescheduled)

Is defined by
: [FEP-8a8e](https://w3id.org/fep/8a8e)


## Examples

Example of a forward chronological OrderedCollection with additional context

```None
{
  "@context": [
    "https://w3id.org/fep/8a8e"
    "https://www.w3.org/ns/activitystreams",
  ],
  "id": "https://domain.example/events/0",
  "type": "Event",
  "eventStatus": "eventScheduled",
}
```
