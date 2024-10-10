# orderType

URI
: `https://w3id.org/fep/1985/orderType`

Label
: is ordered in

Comment
: Indicates the type of ordering for an OrderedCollection.

Domain
: [OrderedCollection](https://www.w3.org/ns/activitystreams#OrderedCollection)

Range
: [OrderingClass](https://w3id.org/fep/1985/OrderingClass) (@vocab)

Required
: No

Functional
: Yes

See also
: [ForwardChronological](https://w3id.org/fep/1985/ForwardChronological) | [ReverseChronological](https://w3id.org/fep/1985/ReverseChronological)

Is defined by
: [FEP-1985](https://w3id.org/fep/1985)


## Examples

Example of a forward chronological OrderedCollection with additional context

```None
{
	"@context": [
		"https://www.w3.org/ns/activitystreams",
		"https://w3id.org/fep/1985"
	],
	"id": "https://domain.example/some-collection",
	"type": "OrderedCollection",
	"orderedItems": [
		"https://domain.example/objects/1",
		"https://domain.example/objects/2",
		"https://domain.example/objects/3"
	],
	"orderType": "ForwardChronological"
}
```

Example of a forward chronological OrderedCollection without additional context

```None
{
	"@context": "https://www.w3.org/ns/activitystreams",
	"id": "https://domain.example/some-collection",
	"type": "OrderedCollection",
	"orderedItems": [
		"https://domain.example/objects/1",
		"https://domain.example/objects/2",
		"https://domain.example/objects/3"
	],
	"https://w3id.org/fep/1985/orderType": {
		"id": "https://w3id.org/fep/1985/ForwardChronological"
	}
}
```
