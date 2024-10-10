# exampleC

URI
: `https://w3id.org/fep/888d/exampleC`

Label
: has an exampleC value of

Comment
: A property that is an ordered list of literal values that are specifically non-negative integers

Domain
: [SomeType](https://w3id.org/fep/888d/SomeType)

Range
:  A list of non-negative integers (@list)

Required
: No

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
