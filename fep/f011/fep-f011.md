---
slug: "f011"
authors: Steve Bate <svc-fep@stevebate.net>
status: DRAFT
dateReceived: 2026-03-17
discussionsTo: https://codeberg.org/steve-bate/fep/issues
---
# FEP-f011: Full-Text Search Query Syntax for ActivityPub

## Summary

This proposal defines a full-text search syntax for ActivityPub client support.

The syntax supports:

- Terms and quoted phrases
- Faceted search (`facet:value`)
- Boolean operators (`AND`, `OR`, `NOT`)
- Parenthesized groups
- Implicit `AND` between adjacent expressions
- Regex literals (`/.../`)
- Inclusive, exclusive, and mixed range bounds (`[a TO b]`, `{a TO b}`, `[a TO b}`)

## Terminology

The term *query string* means the value of the `q` query parameter in an HTTP request
against a search endpoint.

The term *faceted expression* means `<facet>:expr`, where `expr` may be a term,
phrase, regex, range, or parenthesized subexpression and the *facet* is typically a JSON property path.

The term *unfaceted expression* means a term, phrase, regex, or group that does not
have a facet prefix.

## Query Syntax

### Grammar

The (simplified) grammar proposed by this FEP is:

```ebnf
query      := or_expr
or_expr    := and_expr ("OR" and_expr)*
and_expr   := unary (("AND" unary) | (implicit_and unary))*
unary      := "NOT" unary | primary
primary    := term | phrase | regex | range | field_expr | "(" query ")"
field_expr := WORD ":" (primary | "(" query ")")
range      := ("[" | "{") bound TO bound ("]" | "}")
bound      := WORD | phrase
phrase     := '"' <any-char-except-quote>* '"'
regex      := "/" <regex-body> "/"
term       := WORD
```

An AND is implicit when two primaries are adjacent. The "regex-body" SHOULD conform to [RFC9485] (Interoperable Regular Expression Format).

A full ABNF grammar is [available](fep-f011.abnf). This can be used with parser generators like [ANTLR](https://www.antlr.org/).

### Token Rules

- `AND`, `OR`, `NOT`, and `TO` are recognized as operators only in uppercase.
- `WORD` excludes whitespace and these delimiters: `()[]{}":/`.
- Regex literals use slash delimiters and support escaped slash characters.

### Operator Precedence

The parser evaluates operators in this order:

1. Parenthesized expressions
2. Unary `NOT`
3. `AND` (explicit and implicit)
4. `OR`

`AND` and `OR` are left-associative.

### Faceted Expressions

A fielded expression has this form:

```text
<facet>:value
<facet>:"some phrase"
<facet>:/xy.*/
<facet>:[10 TO 20]
<facet>:(cats OR dogs)
```

`<facet>:(...)` applies the nested expression to the facet value.

### Range Expressions

Ranges support inclusive and exclusive delimiters independently:

- `[a TO b]` inclusive lower and upper bounds
- `{a TO b}` exclusive lower and upper bounds
- `[a TO b}` inclusive lower, exclusive upper
- `{a TO b]` exclusive lower, inclusive upper

Unbounded bounds may use `*` where supported by the evaluator implementation
(e.g., `rank:[4 TO *]`).


## Search Endpoint Discovery

The search endpoint is specified using the `search` property of the ActivityPub actor `endpoints` object. For example:

```json
{
  "@context": [
    "https://w3id.org/fep/f011"
    "https://www.w3.org/ns/activitystreams"
  ],
  ...
  "endpoints": {
    "search": "https://server.example/search"
  }
}
```
## HTTP Usage

This syntax is used as the `q` parameter on the search endpoint.

```text
GET https://server.example/search?q=<query>
```

### Responses

Responses MUST be an ActivityPub `Collection` or `OrderedCollection`. Paging is optional. If an `OrderedCollection` is returned, the results SHOULD be considered ranked although the ranking criteria will not be known by the client ( possibilities are relevance/[BM25](https://en.wikipedia.org/wiki/Okapi_BM25), recency, etc.).

### Example 1: Simple Primary Term

Request: `cats`

```http
GET /search?q=cats HTTP/1.1
Host: social.example
Accept: application/activity+json
```

### Example 2: Faceted + Unfaceted phrase

Request: `tag:fediverse language:en "ActivityPub client search"`

```http
GET /search?q=tag%3Afediverse%20language%3Aen%20%22ActivityPub%20client%20search%22 HTTP/1.1
Host: social.example
Accept: application/activity+json
```

Response:

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "OrderedCollection",
  "id": "https://social.example/search?q=tag:fediverse language:en \"ActivityPub client search\"",
  "totalItems": 1,
  "orderedItems": [
    {
      "id": "https://social.example/notes/1",
      "type": "Note"
    }
  ]
}
```

### Example 3: Boolean + Grouping

Request:v`(cats OR dogs) AND NOT testing`


```http
GET /search?q=%28cats%20OR%20dogs%29%20AND%20NOT%20testing HTTP/1.1
Host: social.example
Accept: application/activity+json
```

### Example 4: Regex

Request: `type:Person preferredUsername:/alic.*/`

```http
GET /search?q=type%3APerson%20preferredUsername%3A%2Ffedi.%2A%2F
Host: social.example
Accept: application/activity+json
```

This could be useful for auto completion. Using a `type:HashTag` search term could similarly be used for hashtag autocompletion.

### Example 5: Range

Request: `rank:[2 TO 4]`

```http
GET /search?q=rank%3A%5B2%20TO%204%5D HTTP/1.1
Host: social.example
Accept: application/activity+json
```

### Error Handling

Invalid syntax MUST result in an HTTP client error status.
Examples include:

- Missing closing `)`
- Missing value after `<facet>:`
- Unterminated regex literal
- Missing range delimiter

Implementations MAY include details in a problem response body.

## Interoperability Notes

- Operators are case-sensitive (`AND` is an operator, `and` is a term).
- Unfaceted regex and primary term evaluation depends on pre-configured text facets in the evaluation layer.
- Field capabilities are evaluator-specific
- This proposal standardizes syntax and parsing behavior, not ranking/scoring.

## Implementations

- [FIRM](https://github.com/steve-bate/firm)


## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement
Proposal have waived all copyright and related or neighboring rights to this work.

[ActivityPub]: https://www.w3.org/TR/activitypub/ "ActivityPub is a decentralized social networking protocol based upon the ActivityStreams 2.0 data format."
[RFC9485]: https://www.rfc-editor.org/rfc/rfc9485.html#name-pcre-re2-and-ruby-regexps "This document specifies I-Regexp, a flavor of regular expression that is limited in scope with the goal of interoperation across many different regular expression libraries."