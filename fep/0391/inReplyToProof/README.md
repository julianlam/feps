# inReplyToProof <https://w3id.org/fep/0391/inReplyToProof>

Provides proof that some object was added to the replies collection of some inReplyTo object

Domain
: Object with inReplyTo set to an Object that has a replies collection

Range
: Add

## Example

```json
{
	"@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/0391"],
	"id": "https://example.com/create-some-reply",
	"actor": "https://example.com/actors/2",
	"type": "Create",
	"object": {
		"id": "https://example.com/some-reply",
		"type": "Note",
		"attributedTo": "https://example.com/actors/2",
		"content": "This is a reply, and I can prove it was added to the replies collection.",
		"inReplyTo": {
			"id": "https://example.com/some-object",
			"type": "Note",
			"attributedTo": "https://example.com/actors/1",
			"content": "I am accepting replies to this object.",
			"replies": "https://example.com/some-object/replies"
		},
		"inReplyToProof": "https://example.com/some-proof"
	},
	"result": {
		"id": "https://example.com/some-proof",
		"actor": "https://example.com/actors/1",
		"type": "Add",
		"object": "https://example.com/some-reply",
		"target": "https://example.com/some-object/replies",
		"attributedTo": "https://example.com/create-some-reply"
	}
}
```