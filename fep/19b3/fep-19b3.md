---
slug: "19b3"
authors: Helge
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-19b3-specifying-properties-of-a-service/8311
dateReceived: 2025-11-04
trackingIssue: https://codeberg.org/fediverse/fep/issues/719
---

# FEP-19b3: Specifying Properties of a Service

## Summary

Actors of type `Service` are used in the Fediverse to
represent automated process. In this FEP, we suggest some property values
to use to convey further information about the
underlying automated process and the responsible
parties for the automated process.

## Property Values

Property values can be attached to an actor to specify additional
values. Using property values has two key advantage:

* It's a standardized approach
* They are visible to Fediverse users

The official definition of `PropertyValue` can be found
at [PropertyValue - Schema.org Type][schema]. 
The section [Examples of Property Value](#examples-of-property-value)
contains examples and further discussions on the usage of property
value.


## Suggested Property Values

The property values suggested here are meant to provide information
to the users of the Fediverse. They are not meant to influence the
behavior of Fediverse applications.

### Source

This property value should provide a link to the source code, e.g.

```json
{
  "type": "PropertyValue",
  "name": "Source",
  "value": "https://codeberg.org/helge/release_helper"
}
```

### Author

The Author field would specify the author of the source linked
in [Source](#source).  The exact format of the value can
be debated. Some possibilities 

* It could be a Fediverse handle, e.g. `@helge@mymath.rocks`,
* the corresponding acct-uri, e.g. `acct:helge@mymath.rocks`
* or even a webpage 
* or an email address (again with a discussion between `user@domain.example` or `mailto:user@domain.example`)

### Support

If the author of the service is not the one running it, one
needs to use an alternative field. We suggest using __Support__
in this case.

### Frequency

One can run services with a periodic trigger, e.g. cron. This indicates
their frequency. Example:

```json
{
  "type": "PropertyValue",
  "name": "Frequency",
  "value": "At 42 minutes past the hour"
}
```

### ServiceType

Indicates the type of the service, e.g. `Comment Tracking System`, see
[FEP-136c][]. This should be primarily used for services that do more
complicated processing, and link to documentation what the service
does.

```json
{
  "type": "PropertyValue",
  "name": "ServiceType",
  "value": "Comment Tracking System, https://bovine.codeberg.page/comments/136c/fep-136c/"
}
```

We imagine that specifying _Reacts To Mentions_ would be useful
to indicate that this is a bot the answers when mentioned.
Furthermore, for bots just as [@release](https://dev.bovine.social/@release),
once might specify something like _On Event_, as they are
triggered when continuous integration jobs are run.


## Examples of property value

The following example is taken from the actor [below](#example-of-actor-with-property-value)

```json
{
  "type": "PropertyValue",
  "name": "Source",
  "value": "https://codeberg.org/helge/release_helper"
}
```

In difference to the example provided by us, mastodon
uses HTML as the value of property values, e.g.

```json
{
  "type": "PropertyValue",
  "name": "🤖",
  "value": "<a href=\"https://botwiki.org\" target=\"_blank\" rel=\"nofollow noopener me\" translate=\"no\"><span class=\"invisible\">https://</span><span class=\"\">botwiki.org</span><span class=\"invisible\"></span></a>"
}
```

This example also shows another behavior, we recommend against:
_using emojis as name_. This has the disadvantage of being awkward
to parse (in particular for people using screen readers).

### Example of actor with property value

An example of an actor with property values looks like

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "PropertyValue": {
        "@id": "https://schema.org/PropertyValue",
        "@context": {
          "value": "https://schema.org/value",
          "name": "https://schema.org/name"
        }
      }
    }
  ],
  "id": "https://dev.bovine.social/actor/kH3y9kw8cqRUgzso3oM3_w",
  "type": "Service",
  "preferredUsername": "release",
  "name": "release",
  "attachment": [
    {
      "type": "PropertyValue",
      "name": "Author",
      "value": "acct:helge@mymath.rocks"
    },
    {
      "type": "PropertyValue",
      "name": "Source",
      "value": "https://codeberg.org/helge/release_helper"
    }
  ], 
  "...": "..."
}
```

> [!NOTE]
> There are variance with `@context` which change which URIs
> property values expand if one uses JSON-LD. As JSON-LD is
> unused for all practical purposes, this currently does not
> matter. See [the Appendix](#appendix-the-json-ld-problem) for
> details on what goes wrong.


## Appendix: The JSON-LD problem

The document

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    {
      "PropertyValue": {
        "@id": "https://schema.org/PropertyValue",
        "@context": {
          "value": "https://schema.org/value",
          "name": "https://schema.org/name"
        }
      }
    }
  ],
  "name": "release",
  "attachment": [
    {
      "type": "PropertyValue",
      "name": "Author",
      "value": "acct:helge@mymath.rocks"
    }
  ]
}
```

turns to 

```json
{
  "https://www.w3.org/ns/activitystreams#attachment": {
    "@type": "https://schema.org/PropertyValue",
    "https://schema.org/name": "Author",
    "https://schema.org/value": "acct:helge@mymath.rocks"
  },
  "https://www.w3.org/ns/activitystreams#name": "release"
}
```

when compacted against `"@context": {}`. Any variation of `@context` should
behave similarly. The obvious choices

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://schema.org"
  ],
  "name": "release",
  "attachment": [
    {
      "type": "PropertyValue",
      "name": "Author",
      "value": "acct:helge@mymath.rocks"
    }
  ]
}
```

and with the order of `"https://www.w3.org/ns/activitystreams"` and
`"https://schema.org"` reversed lead to incorrect results due to name
being overloaded.

## References

- Helge, [FEP-136c: Comment Tracking Services][FEP-136c], in preparation
- fediverse-ideas: [Botiquette][botiquette]
- schema.org [PropertyValue - Schema.org Type][schema]

[botiquette]: https://codeberg.org/fediverse/fediverse-ideas/issues/33
[FEP-136c]: https://bovine.codeberg.page/comments/136c/fep-136c/
[schema]: https://schema.org/PropertyValue

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
