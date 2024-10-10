# exampleA

URI
: `https://w3id.org/fep/888d/exampleA`

Label
: has example relation A with the literal value

Comment
: A property with some literal value (string, boolean, number)

Domain
: [SomeType](https://w3id.org/fep/888d/SomeType)

Range
: A literal value

Required
: Yes

Functional
: Yes

Is defined by
: [FEP-888d](https://w3id.org/fep/888d)


## Examples

Example of a SomeType with properties exampleA, exampleB, exampleC

```None
{
  "@context": "https://w3id.org/fep/888d",
  "@type": "SomeType",
  "exampleA": true,
  "exampleB": "https://example.com/some-object",
  "exampleC": [1, 1]
}
```
