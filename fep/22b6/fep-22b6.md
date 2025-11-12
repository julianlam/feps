---
slug: "22b6"
authors: Helge <@helge@mymath.rocks>
status: DRAFT
dateReceived: 2025-11-12
discussionsTo: https://socialhub.activitypub.rocks/t/fep-22b6-linking-an-activitypub-object-to-a-html-page-and-back/8369
---
# FEP-22b6: Linking an ActivityPub Object to a HTML page and back

## Summary

Links are a fundamental part of the internet. This FEP describes how to use
links to link a HTML page to an ActivityPub object. The mechanisms described
in this document are not new and are used to link to RSS feeds (see [alternate][],
second example).

## Linking from a HTML page

The HTML living standard states about [alternate][]

> The keyword creates a hyperlink referencing an alternate representation of the current document.

In this sense, we can link from the HTML page to an ActivityPub object
using 

```html
<head>
    ...
    <link rel="alternate" type="application/activity+json" href="http://location.example/object.id">
    ...
</head>
```

which can be used for automatic discovery.
To provide a link for the user, one should use an anchor, e.g.

```html
<body>
    ...
    <a rel="alternate" type="application/activity+json" href="http://location.example/object.id">
        ActivityPub Object
    </a>
    ...
</body>
```

We recommend using both forms as they serve different purposes.

>[!WARNING]
> One might be tempted to use [canonical][] instead of [alternate][] if the HTML page
> just renders the content of the ActivityPub object. The author believes that sticking
> to the single format giving here has the highest chance of leading to widespread support.

### Discussions

As the [example](#example) below shows, there are use cases when the ActivityPub object
and the page are on different servers. One can however still check the relationship,
by verifying the ActivityPub object contains a link back to the page.

Similarly, the ActivityPub object might provide less content than the webpage.

### Example

The page [https://bovine.codeberg.page/comments/](https://bovine.codeberg.page/comments/) contains
the link element

```html
<link rel="alternate"
  href="https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8="
  type="application/activity+json">
```

and the linked object resolves to

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Page",
  "attributedTo": "https://comments.bovine.social/actor/rF4xnx1QraAIU3Krg-2Qzg",
  "to": [
    "https://www.w3.org/ns/activitystreams#Public"
  ],
  "published": "2025-10-20T17:45:11Z",
  "url": [
    {
      "type": "Link",
      "href": "https://bovine.codeberg.page/comments/",
      "mediaType": "text/html"
    }
  ],
  "name": "Comment Tracking System",
  "summary": null,
  "id": "https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8=",
  "context": "https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8=/context",
  "replies": "https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8=/replies",
  "likes": "https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8=/likes",
  "shares": "https://comments.bovine.social/pages/aHR0cHM6Ly9ib3ZpbmUuY29kZWJlcmcucGFnZS9jb21tZW50cy8=/shares"
}
``` 

The Page object can be understood as [Page in the ActivityVocabulary][as-page] here, i.e. "Represents a Web Page".

## Alternatives

As already said, we recommend using this suggested approach to link from
the HTML to an ActivityPub object.

However, there are other methods that are in use to provide the link,
and should be considered valid options.

* [Content Negotiation][contneg]
* [Link Headers][link-headers]

For the use case of [FEP-136c: Comment Tracking Services][FEP-136c], that motivates
this work, embedding the links in the HTML is the only viable option.
This is due to the HTML often being hosted on static sites that do
not provide the option to use Content Negotiation or Link Headers.

## References

- Helge, [FEP-136c: Comment Tracking Services][FEP-136c], in preparation
- HTML Living Standard, [4.6.7.1 Link type "alternate"][alternate]
- HTML Living Standard, [4.6.7.4 Link type "canonical"][canonical]
- James M Snell, Evan Prodromou, [Activity Vocabulary][as-page]


[alternate]: https://html.spec.whatwg.org/multipage/links.html#rel-alternate
[canonical]: https://html.spec.whatwg.org/multipage/links.html#link-type-canonical
[contneg]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Content_negotiation
[link-headers]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Link
[as-page]: https://www.w3.org/TR/activitystreams-vocabulary/#dfn-page
[FEP-136c]: https://bovine.codeberg.page/comments/136c/fep-136c/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
