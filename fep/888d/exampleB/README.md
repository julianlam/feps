# exampleB

URI
: `https://w3id.org/fep/888d/exampleB`

Label
: has example relation B with

Comment
: A property that links to another node on the graph (for example, another object)

Domain
: [SomeType](https://w3id.org/fep/888d/SomeType)

Range
: An object (@id)

Required
: No

Functional
: No

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
