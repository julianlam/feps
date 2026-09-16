---
slug: "22cd"
authors: Hong Minhee <hong@minhee.org>
type: implementation
status: DRAFT
dateReceived: 2026-09-16
discussionsTo: https://socialhub.activitypub.rocks/t/fep-22cd-attributing-translations/8897
---

# FEP-22cd: Attributing translations

## Summary

This proposal adds structured translation metadata to Activity Streams objects
that already carry language-tagged content through `contentMap` (and
`nameMap`/`summaryMap`). It defines a `translations` property holding one
`Translation` entry per translated language, distinct from the object's own
`attributedTo`. Each entry credits one or more translators with the existing
`schema:translator` property, identifies its language with `schema:inLanguage`,
and links to the source with `schema:translationOfWork`. A new `sourceUpdated`
timestamp lets consumers distinguish translations reflecting the current source
from those predating its latest edit, without a server exposing its private
revision history. The combination of multiple `translator` actors and their
types (`Person` versus `Application`) distinguishes unaided human translation,
raw machine translation, and human-reviewed machine translation. Translations
share the containing object's identity, `replies` collection, and reactions; no
separate content object is introduced.


## Motivation

Activity Streams objects can already carry language-tagged text, through the
`contentMap`, `nameMap`, and `summaryMap` properties defined in [Activity
Streams 2.0]. An object with several language versions has one
identity, one `replies` collection, and one set of reactions, as most
implementations and users already expect.

What is missing is a way to identify responsibility for each language version,
beyond the object's `attributedTo`. Several fediverse projects let authors
publish translations of their own posts, or let other members of an organization
each translate specific languages. Existing vocabulary does not distinguish the
author of the original text from the translator of one language version, does
not tie a translator to one language rather than to the whole object, and does
not indicate whether a translation reflects the original's current or earlier
text.

[Schema.org] already defines `translator` (its declared range is `Person` or
`Organization`), `translationOfWork`/`workTranslation` (`CreativeWork` to
`CreativeWork`), and `inLanguage` (a [BCP 47] tag) for exactly this
relationship. This proposal reuses those terms, extends the actors
`translator` accepts to include `Application` and `Service` beyond Schema.org's
declared range (see "Distinguishing human and machine translation"), and adds
a container for per-language entries on an Activity Streams object plus a
timestamp recording translation freshness relative to the source.


## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119].


## The `translations` property

An object that uses `contentMap` (or `nameMap`/`summaryMap`) to carry more than
one language version MAY have a `translations`
(`https://w3id.org/fep/22cd#translations`) property. Its value is a set of
`Translation` (`https://w3id.org/fep/22cd#Translation`) objects, one for each
language version that is a translation rather than text directly authored by
whoever is named in the object's `attributedTo`.

A language present in `contentMap` with no corresponding entry in `translations`
is directly authored, not translated.

A `Translation` object has the following properties:

- `inLanguage` (`schema:inLanguage`, required): the [BCP 47] language tag
  this entry describes. It MUST match a key present in whichever of the
  containing object's `contentMap`, `nameMap`, or `summaryMap` properties
  are present.
- `translator` (`schema:translator`, required): one or more actors credited for
  this language version. See "Separating authorship from translation credit"
  below.
- `translationOfWork` (`schema:translationOfWork`, required): the `id` of the
  containing object.
- `sourceUpdated` (`https://w3id.org/fep/22cd#sourceUpdated`, recommended): an
  `xsd:dateTime` copied from the source object's `updated` property (or its
  `published` property, if `updated` is absent) as of the last human review
  of this translation against the source. See "Freshness" below.
- `isBasedOn` (`schema:isBasedOn`, optional): the `id` of a specific revision
  resource this translation was reviewed against, for implementations that
  publish such resources.
- `url` (optional): [Activity Vocabulary]'s own `url`
  property, reused unchanged, as a permalink to a rendering of this specific
  language version, distinct from the containing object's own `id` or `url`.

A `Translation` object MAY have an `id`. Consumers MUST NOT assume it is
dereferenceable, and publishers MUST NOT expect it to be the target of its own
`Create`, `Update`, or `Delete` activity: it is metadata carried inside its
containing object, not an independent one.

The JSON-LD context at `https://w3id.org/fep/22cd` defines `translations`,
`Translation`, and `sourceUpdated`, and binds `translator`, `inLanguage`,
`translationOfWork`, and `isBasedOn` to their Schema.org definitions:

```json
{
  "@context": {
    "fep-22cd": "https://w3id.org/fep/22cd#",
    "schema": "https://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "translations": { "@id": "fep-22cd:translations", "@container": "@set" },
    "Translation": "fep-22cd:Translation",
    "sourceUpdated": { "@id": "fep-22cd:sourceUpdated", "@type": "xsd:dateTime" },
    "translator": { "@id": "schema:translator", "@type": "@id", "@container": "@set" },
    "inLanguage": "schema:inLanguage",
    "translationOfWork": { "@id": "schema:translationOfWork", "@type": "@id" },
    "isBasedOn": { "@id": "schema:isBasedOn", "@type": "@id" }
  }
}
```

Every example in this document loads this context alongside the Activity
Streams 2.0 context:

```json
"@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"]
```

A personal author translating their own article:

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/1",
  "type": "Article",
  "attributedTo": "https://example.com/users/alice",
  "updated": "2026-09-01T00:00:00Z",
  "contentMap": {
    "en": "<p>Original text...</p>",
    "ko": "<p>번역 텍스트...</p>"
  },
  "translations": [
    {
      "type": "Translation",
      "inLanguage": "ko",
      "url": "https://example.com/articles/1/ko",
      "translator": ["https://example.com/users/alice"],
      "translationOfWork": "https://example.com/articles/1",
      "sourceUpdated": "2026-09-01T00:00:00Z"
    }
  ]
}
```

Two organization members translating different languages of the same article:

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/2",
  "type": "Article",
  "attributedTo": "https://example.com/orgs/acme",
  "updated": "2026-09-10T00:00:00Z",
  "contentMap": {
    "en": "<p>Original...</p>",
    "ja": "<p>日本語版...</p>",
    "ko": "<p>한국어판...</p>"
  },
  "translations": [
    {
      "type": "Translation",
      "inLanguage": "ja",
      "translator": ["https://example.com/users/bob"],
      "translationOfWork": "https://example.com/articles/2",
      "sourceUpdated": "2026-09-10T00:00:00Z"
    },
    {
      "type": "Translation",
      "inLanguage": "ko",
      "translator": ["https://example.com/users/carol"],
      "translationOfWork": "https://example.com/articles/2",
      "sourceUpdated": "2026-09-10T00:00:00Z"
    }
  ]
}
```

Consumers MUST NOT infer meaning from the order of bob's and carol's entries.


## Separating authorship from translation credit

The object's `attributedTo` identifies whoever is responsible for the original
text. A `Translation` entry's `translator` identifies only who translated that
language version. It grants no control over the original object or other
language versions.

Receiving servers determine which activities to accept the way they already do,
by which actor signed the `Create`, `Update`, or `Delete` activity delivered to
them. `attributedTo` and `translator` are content asserted by the publishing
server. A receiving server MUST NOT treat either as authorization to accept
activities from the actors it names.

A translator credit is only as trustworthy as its publishing server. This
proposal neither provides nor requires independent verification of the
credit.

`translator` accepts a set of actors rather than a single actor, and
consumers MUST NOT infer meaning from their order.


## Distinguishing human and machine translation

A `Translation` entry can credit both the software that produced an initial
translation and its human reviewer through the `translator` set and the actor
types defined in the [Activity Vocabulary], without a
dedicated provenance property:

- A `Translation` entry whose `translator` set contains only `Person`,
  `Organization`, or `Group` actors represents an unaided human translation.
- A `Translation` entry whose `translator` set contains only `Application` (or
  `Service`) actors represents machine output no human has reviewed.
- A `Translation` entry whose `translator` set contains both represents a
  machine-produced translation a human has reviewed. The human actor's presence
  credits review, not unaided translation.

This classification depends on dereferencing each `translator` actor to learn
its type. A consumer that cannot dereference one, for instance because the
account has been deleted, MUST treat that entry's human-or-machine status as
unknown rather than guessing from the actors it could resolve.

Publishers MUST NOT list a human translator alone for unreviewed machine
output. Consumers rendering translator credit SHOULD reflect this distinction,
for instance by labeling a `Person`-and-`Application` pair as reviewed rather
than as translated from scratch.

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/3",
  "type": "Article",
  "attributedTo": "https://example.com/users/erin",
  "updated": "2026-09-10T00:00:00Z",
  "contentMap": {
    "en": "<p>Original...</p>",
    "fr": "<p>Traduction automatique...</p>",
    "de": "<p>Maschinelle Übersetzung, von Dave geprüft...</p>"
  },
  "translations": [
    {
      "type": "Translation",
      "inLanguage": "fr",
      "translator": ["https://example.com/actors/llm-translator"],
      "translationOfWork": "https://example.com/articles/3"
    },
    {
      "type": "Translation",
      "inLanguage": "de",
      "translator": [
        "https://example.com/actors/llm-translator",
        "https://example.com/users/dave"
      ],
      "translationOfWork": "https://example.com/articles/3",
      "sourceUpdated": "2026-09-10T00:00:00Z"
    }
  ]
}
```

`https://example.com/actors/llm-translator` is an `Application` actor. The
unreviewed `fr` translation has no `sourceUpdated`. The `de` entry credits
dave for reviewing the machine translation, not for translating it from
scratch; its `sourceUpdated` identifies the source version he reviewed.


## Freshness

Consumers need to distinguish translations that reflect the current source,
translations that predate its latest edit, and translations with no recorded
freshness claim, without requiring publishing servers to expose private revision
histories.

The reference value is the source object's `updated` property, or its
`published` property if `updated` is absent. `sourceUpdated` records that
reference value as of the last human review of the translation against the
source, whether or not the review changed the translated text. Consumers
compare `sourceUpdated` with the source object's current reference value:

- If `sourceUpdated` is earlier than the reference value, the translation
  predates the source's latest edit and MAY be presented as potentially
  stale.
- If `sourceUpdated` is absent, no freshness claim is made, and consumers
  MUST NOT infer freshness or staleness.
- If `sourceUpdated` is equal to or later than the reference value, the
  translation reflects the current source. A later value can occur when a
  publisher stamps the review time rather than copying the source's property
  exactly; consumers MUST treat it as an equal value, not an error.

Publishers SHOULD only move `sourceUpdated` forward, to the current reference
value at the time a human translator reviews the source, whether or not the
translated text changes.

Implementations that record revisions as separate resources MAY additionally set
`isBasedOn` to reference the specific revision reviewed. It supplements rather
than replaces `sourceUpdated`, since not every implementation exposes
revisions as dereferenceable resources.

These snapshots show only freshness-related fields. An `Update.object` for
this article carries the full current object, including the unchanged
`contentMap` and any other language's `Translation` entry (see "Withdrawal
and deleted accounts").

Before a source edit invalidates the Korean translation:

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/2",
  "updated": "2026-09-10T00:00:00Z",
  "translations": [{
    "type": "Translation",
    "inLanguage": "ko",
    "translator": ["https://example.com/users/carol"],
    "translationOfWork": "https://example.com/articles/2",
    "sourceUpdated": "2026-09-10T00:00:00Z"
  }]
}
```

After the source is edited (`updated` moves to 09-15), the translation is stale
until carol reviews it:

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/2",
  "updated": "2026-09-15T00:00:00Z",
  "translations": [{
    "type": "Translation",
    "inLanguage": "ko",
    "translator": ["https://example.com/users/carol"],
    "translationOfWork": "https://example.com/articles/2",
    "sourceUpdated": "2026-09-10T00:00:00Z"
  }]
}
```

If carol reviews the current source and confirms that the Korean translation
needs no changes, the publishing server sends, on the article's behalf, an
`Update` that advances only `sourceUpdated`:

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/22cd"],
  "id": "https://example.com/articles/2",
  "updated": "2026-09-15T00:00:00Z",
  "translations": [{
    "type": "Translation",
    "inLanguage": "ko",
    "translator": ["https://example.com/users/carol"],
    "translationOfWork": "https://example.com/articles/2",
    "sourceUpdated": "2026-09-15T00:00:00Z"
  }]
}
```


## Withdrawal and deleted accounts

In server-to-server delivery, an `Update` replaces the object's full state, as
specified by [ActivityPub §7.3]. A previously present value
omitted from a subsequent `Update` is removed; this applies to `translations`
as to other properties. Withdrawing a translated language
means removing both its `contentMap` entry and its `Translation` entry in the
same federated `Update`. Consumers MUST treat a language that disappears this
way as withdrawn. Servers MUST NOT apply this removal rule to
client-to-server `Update` activities received from their own users: those
updates are partial, and absence does not indicate removal.

The `translator` value remains unchanged when an account is later deleted. The
actor IRI remains as published, and dereferencing it returns the actor server's
existing `Tombstone` or HTTP error response, as for other stale actor
references in Activity Streams. If the actor's type can no longer be resolved,
consumers MUST treat the entry's human-or-machine status as unknown (see
"Distinguishing human and machine translation").


## Compatibility

The object retains one `id`, a shared set of replies and reactions, and every
language version in `contentMap`. Implementations that do not recognize
`translations`, `Translation`, or `sourceUpdated` render it as they would
without these properties. This proposal adds metadata without changing the
meaning of `contentMap` or requiring compatible peers to render anything new.

Some communities and software publish translations as separate objects linked by
`translationOfWork` and `workTranslation`, without a shared `contentMap`. This
existing approach is unaffected. Each language version has separate replies and
reactions; this proposal uses a single object to keep them shared. Unifying
separately published objects' identities is outside its scope and relates more
closely to conversation- or context-grouping proposals such as [FEP-171b] and
[FEP-2931].


## Open questions

The following questions remain open; implementer feedback is sought before
this proposal advances beyond `DRAFT`.

Whether `sourceUpdated` alone is precise enough for real editorial workflows, or
whether `isBasedOn` should be required rather than optional for implementations
with revision resources.

Whether `nameMap` and `summaryMap` translations need treatment beyond that
specified for `contentMap`, since title and body translations could in
principle have different translators.

Whether a `Translation` entry should allow naming a translator who is not a
known actor, for data imported or migrated from a system that recorded
translator names as plain text rather than identities.


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan
  Prodromou, [ActivityPub], 2018
- James M. Snell, Evan Prodromou, [Activity Streams 2.0], 2017
- James M. Snell, Evan Prodromou, [Activity Vocabulary], 2017
- S. Bradner, [Key words for use in RFCs to Indicate Requirement
  Levels][RFC 2119], 1997
- A. Phillips, M. Davis, [Tags for Identifying Languages][BCP 47], 2009
- [Schema.org], `translator`, `translationOfWork`, `workTranslation`,
  `inLanguage`, `isBasedOn`
- silverpill, [FEP-171b: Conversation Containers][FEP-171b], 2024
- a, [FEP-2931: Representing context with a Collection][FEP-2931], 2025

[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityPub §7.3]: https://www.w3.org/TR/activitypub/#update-activity-inbox
[Activity Streams 2.0]: https://www.w3.org/TR/activitystreams-core/
[Activity Vocabulary]: https://www.w3.org/TR/activitystreams-vocabulary/
[RFC 2119]: https://datatracker.ietf.org/doc/html/rfc2119
[BCP 47]: https://www.rfc-editor.org/info/bcp47
[Schema.org]: https://schema.org/
[FEP-171b]: https://w3id.org/fep/171b
[FEP-2931]: https://w3id.org/fep/2931

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement
Proposal have waived all copyright and related or neighboring rights to this
work.
