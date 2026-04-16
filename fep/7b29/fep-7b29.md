---
slug: "7b29"
authors: Ben Pate \<@benpate@mastodon.social\>, Dan Supernault \<@dansup@mastodon.social\>
status: DRAFT
dateReceived: 2026-03-26
relatedFeps: FEP-3b86
discussionsTo: https://socialhub.activitypub.rocks/t/fep-7b29-federated-signup-requests/8649
---

# FEP-7b29: Federated Signup Requests

## Summary
People don't sign up for a new social website in a vacuum. Instead, this is one step in a larger goal that they are trying to accomplish -- such as following a new account, or liking or replying to a particular post.

But this process is often disjointed and filled with "dead ends" in the user experience.

"Federated Signups" give websites the tools to create a smooth signup process even when the user is bounced between several websites.  It accomplishes this by including standardized query parameters in signup referral links to the user's new Fediverse server.  This prevents "dead ends" and allows the user's new server to complete the original task that started their signup.

## 1. Requirements
The key words "MUST", "SHOULD", and "MAY" are to be interpreted as described in [RFC2119](https://tools.ietf.org/html/rfc2119.html).

For the purposes of this document, a "remote server" is any website on the Internet where this workflow begins, such as a news or informational website. A "website visitor" is a person who is consuming the content on a remote server.

Remote servers refer their website visitors to "potential home servers", where they may choose to sign up.  When a person creates an account on a potential home server, they become a "user" and that potential home server simply becomes their "home server."

## 2. The Problem
Currently, most remote servers methods for their website visitors to stay connected with them after their initial visit. For example, visitors who read an article on Substack and Patreon have the opportunity to "Follow" the author of the article and be notified when new articles are published.

This workflow is difficult to achieve for new users of a distributed environment.

For instance, a Fediverse news website (such as WeDistribute.org) hosts its own ActivityPub actors, but does not allow website visitors to create accounts on their website. Instead, publishers like this depend on their visitors following from their own "home server" - a Fediverse account on an entirely separate domain.

If the visitor already has a home server, then [FEP-3b86 Activity Intents](https://w3id.org/fep/3b86) provides a smooth workflow for existing Fediverse users to follow.

But this process breaks down if the website visitor does not already have a Fediverse account. At best, publishers can recommend a Fediverse server for visitors to join, but even still, the visitor's original goal is lost. There is no way for them to connect the new account signup back to their original goal, in order to continue following, liking, or replying to the web page on the remote server.

And from the remote server's point of view, that website visitor goes into a black hole.  It never finds out if that visitor actually joined and completed their task or not.  If the website visitor was half-way into a task -- such as purchasing access to private content -- they may have to start over once they have created an account on their new home server.

If websites are to be gateways for new people to find and join the Fediverse, then we must unify this workflow into a single seamless process, both before and after new users join.

## 3. Federated Signups
Federated signups define a common way for remote servers to pass metadata to a potential home server when referring website visitors to sign up.

This state information takes the form of optional query parameters passed to the home server's signup page, which allows the home server to complete the user's original goal (for instance, following an author or replying to a post)

This document defines four standard query parameters: 

* `please.follow` 
* `please.view`
* `please.notify`
* `please.highlight`

Values for each of these parameters MUST be URL encoded values consistent with URL query parameter standards.

These parameters are merely workflow requests from the remote server to the potential home server.  Workflows defined on remote servers MUST NOT depend on receiving a response from potential home servers.

### 3.1. please.follow
If a website visitor wishes to `Follow` a particular actor on a remote website, but does not yet have a Fediverse identity, then the remote website SHOULD refer them to one or more Fediverse servers where they can establish an account. The link provided by the remote server MAY include a `please.follow` query parameter.

This parameter MUST be a comma separated list of one or more URLS.  The URLs MUST refer to one of these two values:

* The URL of an actor
* The URL of a collection of actors

Once the user has established a new account, the home server SHOULD inspect the list of actors and collections, then provide the new user with the option choose which of them to follow. 

Home servers MAY apply additional rules to this list, for instance adding additional recommended accounts to follow, or removing values from the provided list for other policy reasons.

Example referral URL using propose.follow:

```go
https://homeserver.social/signup?please.follow=https://remoteserver.social/@actor-to-follow,https://remoteserver.social/starter-pack-to-follow
```

### 3.2. please.view
If a website visitor wishes to interact with a particular piece of content on a remote website (i.e. to like, boost, or reply to a web page) but does not yet have a Fediverse identity, then the remote website SHOULD refer them to one or more Fediverse servers where they can establish an account. The link provided by the remote server MAY include a `please.view` query parameter.

This parameter MUST be a single URL that links to the original content.

Once the user has established a new account, the home server SHOULD look up the ActivityStreams representation of the URL and present it to the user.

Home servers MAY apply additional rules to requested URLs. For instance, if a provided URL belongs to a blocked or banned website or user, then the new home server MAY refuse to display it to the new user.

Example referral URL using please.view:

```go
https://homeserver.social/signup?please.view=https://remoteserver.social/my-latest-article
```

#### 3.2.1 please.highlight
As an additional option, when a remote server sends a `please.view` parameter, it MAY also send a `please.highlight` parameter.  This identifies a single activity (such as `Like`, `Announce`, `Arrive`, etc) for the new home server to feature on the page displayed to new users.

Home servers MAY or MAY NOT use this parameter.  It is provided as guidance to the new home server to help the new user complete their original task.

Consider the example of a website visitor who clicks a "Like" button on the remote server, and is then forwarded to a new home server and completes the signup process there. When their new home server displays the original resource where they clicked "Like", it MAY also highlight the "Like" button in some way on its corresponding page. This MAY be by color, size, positioning, or any other method determined by the home server.

### 3.3. please.notify
When a remote website refers a visitor to a new home server, it may have incomplete tasks in process that would benefit by knowing that the visitor has successfully created a new account. For example, if the visitor has purchased access to private content, then the remote website may want to link those privileges to the newly-created identity.

The `please.notify` parameter asks the new home server to send an out-of-band HTTP POST to a URL specified by the remote server.

The URL specified in the `please.notify` parameter MUST be[Percent Encoded](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1).  

The URL specified in the `please.notify` parameter MAY include a single template string value: `{id}`.

Home servers MAY take actions based on this parameter, or MAY simply disregard it.

To support this parameter, a home server MUST replace this `{id}` value with the actor id of the newly created actor. This is the requested notification URL. Then, the home server MUST send an HTTP `POST` request with no body to the notification URL. 

## 4.0. Same Server Signups
Federated Signups help improve the signup workflow even if the remote server and home server are the same.  If a Fediverse-enabled website allows anonymous user signups, it can still provide a smoother user experience by passing the four standard parameters to its own signup pages.

## 5.0. Instance Choosers
There are a growing number of "instance chooser" websites that help potential new users to navigate the wide number of Fediverse servers to choose from.

"Instance chooser" websites SHOULD accept the four standard parameters, and then forward these values on to the signup page for the instance that the user ultimately picks.

This allows remote servers to let their visitors pick a new instance according to the rules provided by the instance chooser, and still request these important signup actions from the selected home server.

## 6.0. Implementations

### 6.1 Home Servers
This is a list of "home servers" that publish Activity Intent endpoints.

* Add your name to this list and win a cookie 🍪

### 6.2 Clients
This is a list of client tools that allow end-users to use Activity Intents on remote websites.

* Add your name to this list and win a cookie 🍪

## References
* [Activity Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/#activity-types)
* [IETF RFC 3896](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1) - Uniform Resource Identifier Generic Syntax
* [IEFT RFC 2119](https://tools.ietf.org/html/rfc2119.html) - Key words for use in RFCs to Indicate Requirement Levels
* [IEFT RFC-6570](https://datatracker.ietf.org/doc/html/rfc6570) - URI Template

## Copyright
CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
