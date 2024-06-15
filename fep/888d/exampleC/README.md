# exampleC <https://w3id.org/fep/888d/exampleC>

A property that is an ordered list of literal values that are specifically non-negative integers

Domain
: SomeType <https://w3id.org/fep/888d/SomeType>

Range
: List of nonNegativeInteger <http://www.w3.org/2001/XMLSchema#nonNegativeInteger>

## Example

```json
{
  "@context": "https://w3id.org/fep/888d",
  "@type": "SomeType",
  "exampleA": true,
  "exampleB": "https://example.com/some-object",
  "exampleC": [1, 1]
}
```