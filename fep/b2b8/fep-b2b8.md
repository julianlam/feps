---
slug: "b2b8"
authors: Evan Prodromou <evan@socialwebfoundation.org>
status: DRAFT
dateReceived: 2024-11-07
discussionsTo: https://codeberg.org/evanp/fep/issues
---
# FEP-b2b8: Long-form Text


## Summary

Multi-paragraph text is an important content type on the Social Web. This FEP defines best practices for representing and using properties of a long-form text object in Activity Streams 2.0.

## Motivation

Blog posts, magazine articles, and forum posts are often made up of multiple paragraphs of text, sometimes with embedded images, video, audio or other media. This important content type is documented in the Activity Vocabulary, but this FEP provides additional guidance for publishers and consumers and collects the relevant properties in one place.

This FEP does not provide guidance for book-length or longer text.

This document provides information for multiple protocols that use Activity Streams 2.0 as a representation format. Where ActivityPub use is different than AS2, it is noted.

## Type

The [Article](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-article) type is used to represent multi-paragraph text.

Some consumers do not display `Article` objects with their full content. Some publishers work around this by using a `Note`-type object with much more content than expected for a note.

Publishers should avoid this workaround, and instead give consumers the full information they need to display the content correctly in their own interfaces.

Consumers that only display short text should show the `name`, `summary` and a link to the `url` property so that users can view the full content in a web browser.

## Properties

### `id`

A unique identifier for the text. For ActivityPub, this should be an HTTPS URL that resolves to the object. It should be a single string, unique for all objects.

This property provides the same functionality as the `guid` property in RSS 2.0.

### `name`

The title of the text should be in the `name` property. The property should be short enough to be displayed in a line or two on a browser interface; 75-150 characters is a good rule of thumb. Longer descriptions should be in the `summary` property.

The `name` property should be plain text, not HTML or other markup. In particular, no HTML entities like `&amp;` or `&lt;` should be used.

This property provides the same functionality as the `title` property in RSS 2.0.

### `url`

The location of the full text should be in the `url` property. This can be a single string, in which case it is the URL of the HTML representation of the text. It can also be a [Link](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link) object, which can include additional metadata about the link. If it is a `Link` object, the `mediaType` should be 'text/html' and `href` property should be the URL of the HTML representation of the text.

The `url` property can also be an array of strings or `Link` objects or both. Multiple `Link` objects can be used to represent different media types or provide different URL protocols. At least one of the `Link` objects should have a `mediaType` of 'text/html' and a `href` property with the protocol 'https'.

This property provides the same functionality as the `link` property in RSS 2.0.

### `summary`

This property provides a brief description, teaser, abstract or "lede" for the text. It should be a maximum of about 500 characters; a few sentences; or a short paragraph.

This property can include HTML markup. It should not include embedded media like images, video or audio.

This property provides the same functionality as the `description` property in RSS 2.0.


### `attributedTo`

This property provides the authors of the text, either as a string, an object, or an array.

As a string, it is a single `id` for the author. For ActivityPub, the `id` should be a URL that resolves to an ActivityPub [actor](https://www.w3.org/TR/activitypub/#actor-objects).

As an object, it can be an AS2 object with a type like `Person`, `Application` or `Organization`. It should have an `id` and a `name` property and can also include an `icon` property for the author's avatar. A `summary` property can be used to provide a brief description of the author, including HTML. An `url` property can be used to provide a link to the author's profile page.

If the author does not have an AS2 representation, the `attributedTo` property can be an object with a `type` of `Link` and an `href` property with the URL of the author's profile page. The `name` property can be used to provide the author's name.

As an array, the `attributedTo` property can include multiple authors, either as strings or objects.

The `attributedTo` property provides the same functionality as the `author` property of an item in RSS 2.0, with additional features.

### `published`

The publication date of the text should be in the [published](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-published) property. This should be a [dateTime](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-datetime) string in the format `YYYY-MM-DDTHH:MM:SSZ`.

This property provides the same functionality as the `pubDate` property in RSS 2.0.

### `updated`

If the object has been updated, the date of the last update should be in the [updated](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-updated) property. This should be a [dateTime](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-datetime) string in the format `YYYY-MM-DDTHH:MM:SSZ`. If the property is not present, consumers can assume that the object has not been modified since the `published` date.

### `image`

The [image](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-image) property provides a notable or representative image for the text. It can be included by reference as an `id` or with an `Image` type object.

There can be multiple values for the `image` property, either as an array of `id` strings or `Image` objects. Publishers should provide these in order of importance, with the most important image first. Consumers can use as many or as few as needed.

### `content`

The full text of the article or blog post should be in the [content](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-content) property. This should be HTML. Using `mediaType` to set a different media type presumes that consumers will be able to display that type.

The HTML elements in the `content` property should include a sanitized subset of
the full HTML element set. It should not include any CSS or JavaScript. This subset should include:

- `<p>`
- `<span>` (class)
- `<br>`
- `<a>` (href, rel, class)
- `<del>`
- `<pre>`
- `<code>`
- `<em>`
- `<strong>`
- `<b>`
- `<i>`
- `<u>`
- `<ul>`
- `<ol>` (start, reversed)
- `<li>` (value)
- `<blockquote>`
- `<img>` (src, alt, title, width, height, class)
- `<video>` (src, poster, width, height, class)
- `<audio>` (src, controls, class)

The HTML should only include the content of the text. Additional navigation to other pages on the originating site, like category links or home page links, should not be included. Other affordances like "favourite", "like", "bookmark" or other buttons should not be included.

Any embedded media like images, video or audio in the `content` property should also be listed in the `attachment` property so that consumers can pre-fetch the media.

### `source`

If the text was originally created in a different format, the original source should be in the [source](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-source) property to allow editing the content. It should include the `mediaType` of the source format and the `content` property with the original content.

### `replies`

Comments on the text should be linked in the [replies](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-replies) property. This should be a URL that resolves to a collection of objects for the replies.

Comments are usually `Note` objects, but can be other types of objects like `Article` or `Question`.

This property provides the same functionality as the `comments` property in RSS 2.0.

### `attachment`

The [attachment](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-attachment) property provides additional media that is part of the text. This can include images, video, audio, or other media. Consumers can use this property to pre-fetch media for display without needing to load and parse the full `content` property.

If the text is a commentary on or review of a particular link on the Web, the `attachment` property can include a `Link` object with a `href` property that is the URL of the linked resource.

### `tag`

The [tag](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-tag) property provides additional metadata about the text. There are two important types of tags:

- [Hashtag](https://swicg.github.io/miscellany/#Hashtag) objects, which represent a topic or category that the text is about. These should have a `name` property with the tag text.
- [Mention](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-mention) objects, which represent a mention of an actor, such as an ActivityPub actor. These should have an `href` property with the URL of the actor's profile page.

### `context`

If the text is part of a larger collection, the [context](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-context) property can provide a link to the collection. An example might be an article in a series, a newspaper column, a blog category (although `tag` may be better here) or a section of a magazine.

There can be multiple `context` properties, either as an array of strings or objects or both.

### `generator`

The [generator](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-generator) property provides information about the software that generated the text. This is usually an `Application` or `Service` object with an `id` and a `name` property.

## Examples

This section includes examples of long-form text objects. Note that for brevity, the content is not actually multi-paragraph text.

### Long-form text with included content

```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text.jsonld",
  "name": "Long-form text with included content",
  "url": "https://example.com/2024/11/07/long-form-text.html",
  "attributedTo": "https://example.com/evan",
  "summary": "<p>This is a long-form text object with included content. It has a title, a summary, and a full text.</p>",
  "content": "<p>This is a long-form text object with included content. It has a title, a summary, and a full text.</p>",
  "published": "2024-11-07T12:00:00Z"
}
```

### Long-form text with external content

```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text-no-content.jsonld",
  "name": "Long-form text with included content",
  "url": "https://example.com/2024/11/07/long-form-text-no-content.html",
  "attributedTo": "https://example.com/evan",
  "summary": "<p>This is a long-form text object with external content. It has a title, a summary, and a link to the full text.</p>"
  "published": "2024-11-07T12:00:00Z"
}
```

### Long-form text with full author information

```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text-author.jsonld",
  "name": "Long-form text with full author information",
  "url": "https://example.com/2024/11/07/long-form-text-author.html",
  "attributedTo": {
    "type": "Person",
    "id": "https://example.com/evan",
    "name": "Evan Prodromou",
    "summary": "<p>Founder of Social Web Foundation</p>",
    "url": "https://example.com/evan",
    "icon": {
      "type": "Image",
      "mediaType": "image/png",
      "url": "https://example.com/evan.png"
    }
  },
  "summary": "<p>This is a long-form text object with full author information. It has a title, a summary, and an URL to the full text.</p>"
  "published": "2024-11-07T12:00:00Z"
}
```

### Long-form text with embedded images


```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text-images.jsonld",
  "name": "Long-form text with embedded images",
  "url": "https://example.com/2024/11/07/long-form-text-images.html",
  "attributedTo": "https://example.com/evan",
  "summary": "<p>This is a long-form text object with embedded images.</p>",
  "content": "<p>This is a long-form text object with embedded images.</p><img src=\"https://example.com/image1.jpg\" alt=\"Image 1\"><img src=\"https://example.com/image2.jpg\" alt=\"Image 2\">",
  "attachment": [
    {
      "type": "Image",
      "id": "https://example.com/image1.jpg",
      "mediaType": "image/jpeg"
    },
    {
      "type": "Image",
      "id": "https://example.com/image2.jpg",
      "mediaType": "image/jpeg"
    }
  ],
  "published": "2024-11-07T12:00:00Z"
}
```

### Long-form text with tags

```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text-tags.jsonld",
  "name": "Long-form text with tags",
  "url": "https://example.com/2024/11/07/long-form-text-tags.html",
  "attributedTo": "https://example.com/evan",
  "summary": "<p>This is a long-form text object with tags.</p>",
  "content": "<p>@<a href='https://example.com/evan'>evan</a> made this #<a href='https://example.com/tag/example'>example</a>.</p>",
  "tag": [
    {
      "type": "Hashtag",
      "name": "example",
      "href": "https://example.com/tag/example"
    },
    {
      "type": "Mention",
      "href": "https://example.com/evan"
    }
  ],
  "published": "2024-11-07T12:00:00Z"
}
```

### Long-form text with context

```
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "id": "https://example.com/2024/11/07/long-form-text-context.jsonld",
  "name": "Long-form text with context",
  "url": "https://example.com/2024/11/07/long-form-text-context.html",
  "attributedTo": "https://example.com/evan",
  "summary": "<p>This is a long-form text object with context.</p>",
  "content": "<p>This is a long-form text object with context.</p>",
  "context": [
    "https://example.com/2024/11/07/series",
    "https://example.com/2024/11/07/category"
  ],
  "published": "2024-11-07T12:00:00Z"
}
```

## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018

[ActivityPub]: https://www.w3.org/TR/activitypub/

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
