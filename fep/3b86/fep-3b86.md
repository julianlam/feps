---
slug: "3b86"
authors: Ben Pate \<@benpate@mastodon.social\>
status: DRAFT
dateReceived: 2024-04-19
relatedFeps: FEP-4adb, FEP-888d
---

# FEP-3b86: Activity Intents

## Summary
Activity Intents extend the capabilities of an ActivityPub server beyond a user's inbox, and simplify the process of interacting with content on the wider social web. They do this by publishing a machine-readable list of public URLs where users can perform key activities (such as `Follow`, `Like`, or `Announce`)  allowing other websites to easily initiate remote social interactions.

## Requirements
The key words "MUST", "SHOULD", and "MAY" are to be interpreted as described in [RFC2119](https://tools.ietf.org/html/rfc2119.html).

For the purposes of this document, a "Server" is the application that is publishing an Actor's Activity Intents via WebFinger, and a "Client" is the application requesting/receiving those intents.  This should not be confused with the fact that "Clients" will likely be Fediverse servers in their own right, in other interactions on the web.

## History
Most centralized social media services have widgets that allow users on the wider Internet to interact with their social services.  These include "like" and "share" buttons that third-party websites embed into their content, and link users back to their corresponding social media account.

There have been several attempts to make a "Share on Mastodon" button that performs a similar action on the Fediverse.  Some require an intermediate host, while others are run entirely on the user's web browser.  These buttons then forward the user back to the appropriate page on their home server with parameters that pre-populate some data about the original site.

But different server applications have different URL endpoints.  So Mastodon uses `/share` while Hubzilla uses `/rpost`.  Parameters to each application are often different, using variations of `text`, `title`, `url`, and others.

The lack of a unified standard has led developers to hard code lists of applications and the endpoints they support.  This solution is brittle and vulnerable to changes by server authors.  It also pins those URL endpoints, making them difficult to change in the future without breaking an unknown number of "share" buttons out in the wild.

What is needed is a way for each server to announce their supported endpoints in a systematic way.

## Activity Intents
In the most basic terms, Activity Intents expand on the common Fediverse use of [WebFinger](https://webfinger.net) in FEP-4adb to include mappings between any [Activity Type](https://www.w3.org/TR/activitystreams-vocabulary/#activity-types) and the URL endpoint where that user can perform it.

When performing an `acct:` (user account) query to the WebFinger endpoint, servers supporting Activity Intents SHOULD respond with one or more intent links in the ["links" property](https://datatracker.ietf.org/doc/html/rfc7033#section-4.4.4). Activity Intent links MUST have `rel` and `href` properties.  All others are ignored.

**rel**: Activity Intents use the `intent:*` relation format to designate the kind of activity intent, where `*` represents the particular Activity the user intends to perform.  Common examples are `intent:Follow`, `intent:Create` and `intent:Like` although any ActivityPub activity is valid.

**href**: Links also use the standard WebFinger `href` property,  but also include wrapped replace values (as in `{uri}` or `{name}`) to designate parameters to be injected by the caller.  (note: this is in contrast to the non-standard `template` property that was used by oStatus)

Parameter names are chosen to correspond with [Activity Vocabulary properties](https://www.w3.org/TR/activitystreams-vocabulary/#properties) and may differ from parameters used by pre-existing implementations.

**Example WebFinger Response:**
```json
{
  "subject": "acct:benpate@mastodon.social",
  "aliases": [
    "https://mastodon.social/@benpate",
    "https://mastodon.social/users/benpate"
  ],
  "links": [
    {
      "rel": "http://webfinger.net/rel/profile-page",
      "type": "text/html",
      "href": "https://mastodon.social/@benpate"
    },
    {
      "rel": "self",
      "type": "application/activity+json",
      "href": "https://mastodon.social/users/benpate"
    },
    {
      "rel": "intent:Follow",
      "href": "https://mastodon.social/authorize_interaction?uri={id}"
    },
    {
      "rel": "intent:Create",
      "href": "https://mastodon.social/share?uri={id}"
    },
    {
      "rel": "intent:Like",
      "template": "https://mastodon.social/intents/like?id={id}"
    },
    {
      "rel": "http://ostatus.org/schema/1.0/subscribe",
      "template": "https://mastodon.social/authorize_interaction?uri={uri}"
    }
  ]
}
```

This expands and standardizes the "remote follow" workflow that was used by oStatus protocol in the past, but has been only partially implemented by newer Fediverse applications.

### Announce Intent
This corresponds to the ActivityStreams [Announce activity](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-announce).  When included in an account's WebFinger results, `intent:Announce` publishes the API endpoint where the current user can announce, or boost the current document in their own outbox.

#### Parameters
* `{id}` - The ID of the ActivityStreams Document that the user will boost when they use this workflow. (required)

#### Example
```json
{
"rel": "intent:Announce",
	"href": "https://server.org/intents/announce?id={id}"
}
```

### Create Intent
This corresponds to the ActivityStreams [Create activity](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-create). When included in an account's WebFinger results, `intent:Create` publishes the API endpoint where the current user can create a new post in their own outbox.  This is similar to the existing "share" endpoints supported by several Fediverse apps, where the user can create a new post in their inbox starting with some pre-populated content.

#### Parameters
* `{content}` - Text content to pre-populate into the user's post.
* `{inReplyTo}` - The ID of the ActivityStreams Document that the user is replying to (if any)

#### Example
```json
{
	"rel": "intent:Create",
	"href": "https://mastodon.social/share?text={content}"
}
```

### Follow Intent
This corresponds to the ActivityStreams [Follow activity](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-follow).   When included in an account's WebFinger result, `intent:Follow` publishes the API endpoint where the current user can initiate a "follow" request.  This is similar to the existing [remote follow](https://www.hughrundle.net/how-to-implement-remote-following-for-your-activitypub-project/) workflow that is supported at various levels by several Fediverse apps, but is no longer formally documented.

#### Parameters
* `{id}` - The ID of the ActivityStreams Actor that the user will follow when they use this workflow. (required)

#### Example

```json
{
	"rel": "intent:Follow",
	"href": "https://mastodon.social/authorize_interaction?uri={id}"
}
```

**Note:** to maintain consistency with the rest of the Activity Vocabulary, this 

### Like Intent
This corresponds to the ActivityStreams [Like activity](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-like).  When included in an account's WebFinger result, `intent:Like` publishes the API endpoint where the current user can like the current document.

#### Parameters
* `{id}` - The ID of the ActivityStreams Document that the user will like when they use this workflow. (required)

#### Example

```json
{
	"rel": "intent:Like",
	"href": "https://server.com/intents/like?id={id}"
}
```

### Other Intents
This convention should be flexible enough that *any* [Activity Type](https://www.w3.org/TR/activitystreams-vocabulary/#activity-types) should be supported.  Parameters in each transaction should correspond to the valid [properties](https://www.w3.org/TR/activitystreams-vocabulary/#properties) for each activity type.  To prevent unrecognized properties from corrupting a workflow, Clients MUST be able to replace all recognized values with the appropriate string.  And, Clients MUST replace unrecognized values with an empty string.

### Security Considerations and CSRF issues
This FEP does not expose any additional attack vectors, but only documents the endpoints that already exist within the server.  Still, it is important to reiterate some key security practices to prevent to [Cross Site Request Forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) vulnerabilities.

* Activity Intents Clients MUST only send `GET` requests to Servers.
* Servers MUST NOT change data based on GET requests.
* Servers SHOULD protect these published endpoints by generating CSRF tokens and including them with every POST request.  This validates that the request originated on the user's home server, and was initiated by the user. See [OWASP Related Controls](https://owasp.org/www-community/attacks/csrf#related-controls) for in-depth discussion.

### TBD: What Namespace To Use for Link Relations?
The `intent:*` namespace is a placeholder for a discussion about what's best, here.  I believe it should be something as simple as possible. Some options are:

1. Continue using the non-standard `intent:*` relation in this initial draft.  It's concise and readable, but non-standard.  Using this model, Activity Intent relations would look like `intent:Announce` and `intent:Create`.

2. Lobby the [WebFinger](https://webfinger.net) project to include intents in their list of defined link relations.  Using this model, Activity Intent relations would look like: `https://webfinger.net/rel/intent#Create` and `https://webfinger.net/rel/intent#Like`

3. Use the https://w3id.org/fep/3b86 namespace, as suggested in [FEP-888d](https://codeberg.org/fediverse/fep/src/branch/main/fep/888d/fep-888d.md).  This has the benefit of following an established convention, but it requires a namespace with a bunch of seemingly random numbers.  Using this model, Activity Intent relations would look like: `https://w3id.org/fep/3b86#Create`.

4. Register a new domain for this effort.  Not out of the question, but it raises the issue of ongoing maintenance, and the possibility of repeating the tragedy of ostatus.org.  Using this model, Activity Intent relations would look like: `https://new-intents-domain.org/rel/Announce`

Right now, I'm in favor of option 1 because it is the most concise and requires the least amount of up-front work.  However, I want to have a discussion about this and will follow the consensus from the Fediverse developer community.

## Clients: The Other Half of the Equation
This FEP provides the prerequisite information required for a **Server** publish Activity Intents for its Actors.  The **Client** portion (where developers add "share" and "like" buttons to their content) is out of this scope.

But briefly, Developers will need to create the workflows on their own sites that:

1. Prompt users for their account.
2. Use WebFinger to look up their supported intents.
3. Fill in available template values.
4. Forward users to their home servers to complete the interaction.

Clients MAY also account for applications that do not publish Activity Intents, but whose endpoints are still well known.  In this case, Clients SHOULD use Activity Intents links if they are present, then fall back to older links (such as the oStatus `/authorize_interaction` endpoint) if they are present, then fall back to hard-coded values (such as the Mastodon `/share` endpoint) if no other values exist.

## Implementations
* [Emissary](https://emissary.dev) will support this FEP once its syntax is finalized.
* Add your name to this list and win a cookie 🍪

## References
* [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#activity-types)
* [RFC 7033: WebFinger](https://datatracker.ietf.org/doc/html/rfc7033)
* [Twitter: Web Intents](https://developer.twitter.com/en/docs/twitter-for-websites/web-intents/overview)
* [Facebook: Share Button](https://developers.facebook.com/docs/plugins/share-button/)
* [Share2Fedi](https://github.com/kytta/share2fedi)
* [Share to Mastodon Button](https://palant.info/2023/10/19/implementing-a-share-on-mastodon-button-for-a-blog/)
* [Remote Follows: Tutorial](https://www.hughrundle.net/how-to-implement-remote-following-for-your-activitypub-project/)
* [Remote Follows: Q&A](https://socialhub.activitypub.rocks/t/what-is-the-current-spec-for-remote-follow/2020)
* [Cross Site Request Forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) - Wikipedia
* [Cross Site Request Forgery](https://owasp.org/www-community/attacks/csrf) - OWASP


## Copyright
CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
