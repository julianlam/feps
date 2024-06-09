# contextProof <https://w3id.org/fep/0391/contextProof>

Provides proof that some object was added to some `context` collection

Domain
: Object with context set to a Collection that has attributedTo set
Range
: Add

## Example

```json
{
	"@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/0391"],
	"id": "https://example.com/create-some-object",
	"actor": "https://example.com/some-actor",
	"type": "Create",
	"object": {
		"id": "https://example.com/some-object",
		"type": "Note",
		"attributedTo": "https://example.com/some-actor",
		"content": "This object is part of some context, and I can prove it was added to the context collection.",
		"context": {
			"id": "https://example.com/some-context",
			"type": "Collection",
			"attributedTo": "https://example.com/some-context-moderator"
		},
		"contextProof": "https://example.com/some-proof"
	},
	"result": {
		"id": "https://example.com/some-proof",
		"actor": "https://example.com/some-context-moderator",
		"type": "Add",
		"object": "https://example.com/some-comment",
		"target": "https://example.com/some-context",
		"attributedTo": "https://example.com/create-some-object"
	}
}
```