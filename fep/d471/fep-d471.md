---
slug: "d471"
authors: Ben Pate \<@benpate@mastodon.social\>
status: DRAFT
discussionsTo: https://activitypub.space/topic/439/fep-3447-endorsements/26
dateReceived: 2026-08-03
trackingIssue: https://codeberg.org/fediverse/fep/issues/900
---

# FEP-d471: Endorsements

This is a very early draft that is meant as a starting point for a conversation, not a final document. Please help develop this draft by [adding issues](https://github.com/EmissarySocial/fep-endorsements/issues) to this repository or joining the discussion on [ActivityPub.space](https://activitypub.space/topic/439/fep-3447-endorsements/26).

While we work, everything is going in this document. However, there are many points at the end that will likely go into separate design documents once we have a clearer picture of what we're creating.

This is the last update to this document on GitHub before we publish a draft to the official FEP repository on Codeberg.

If you're interested in the technical aspects of this FEP, look at §3 Vocabulary, and §4 Workflow.  If you're more interested in the usability and human factors, please look at §5 Security and §6 User Interface.

## Summary
`Endorsement` objects give us a counterpoint to blocks and mutes — a way to send a positive signal about other actors online that is more definitive than a `Follow` or a `Like`.

These records create the opportunity for a privacy-preserving, opt-in network similar to webs of trust, enabling third parties to know who they're dealing with before beginning an online interaction.

## 1. Requirements
The key words "MUST", "SHOULD", and "MAY" are to be interpreted as described in [RFC2119](https://tools.ietf.org/html/rfc2119.html).

## 2. History
In our ever-expanding online communities, individual behavior is often disconnected from the social norms that govern in-person relationships — factors like reputation and trust. This lack of accountability and long-term thinking often powers the worst abuses in online spaces.

Blocks (and block-lists) form an important part of this equation by censoring out those identified as most harmful to the community. But there is space for a counterpart, a "yes" endorsement that is the opposite of the block's "no."

This document defines an `Endorsement` object, which allows people to make positive statements about others on the Fediverse that are more definitive than a `Follow` or a `Like`.

`Endorsement` objects are opt-in and digitally signed to preserve privacy and prevent abuse. This data facilitates a web of trust, and builds the foundations for an online reputation system that helps reinforce social bonds and helps others to know the reputation of the people they interact with online.

## 3. Vocabulary Definitions
This document adds three vocabulary definitions and the workflows required to establish a new endorsement. In broad terms, actor A sends an `Offer(Endorsement)` to B which is `Accept`ed or `Reject`ed by B. If accepted, both actors publish the activity in their respective `endorses` or `endorsedBy` collections.

### 3.1 The `Endorsement` Object
The `Endorsement` object is defined with the URI:
`https://w3id.org/fep/d471#Endorsement`

An `Endorsement` object indicates that the `subject` actor has endorsed the `object` actor. Endorsing is defined as making a positive statement about another actor, and establishing some level of trust as defined by the additional properties included within this activity.

Endorsements are immutable and MUST NOT be changed after they have been `Offer`ed or `Accept`ed. To guarantee this, an [Object Integrity Proof](https://w3id.org/fep/8b32) MUST be included for any endorsement to be considered valid.

#### 3.1.1 ID Property (required)
Endorsements MUST have an [`id`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-id) property, which contains a permanent URI for the endorsement. This is required because external systems may need to verify the validity of the endorsement, or confirm that it has not been revoked by its creator.

#### 3.1.2 Subject Property (required)
Endorsements MUST have a [`subject`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-subject) property, which contains a [Link](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link) to the actor making the endorsement.

#### 3.1.3 Object Property (required)
Endorsements MUST have an [`object`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-object) property, which contains a [Link](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link) to the actor receiving the endorsement.

#### 3.1.4 Context Property (required)
Endorsements MUST have a [`context`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-context) property, which contains a context URI that identifies the nature of the endorsement. Context URIs are defined in §3.2.

#### 3.1.5 Proof Property (required)
Endorsements MUST have a [`proof`](https://w3id.org/fep/8b32) property, which contains an Object Integrity Proof as defined in FEP-8b32. This is required to prevent someone from changing an endorsement maliciously after it has already been accepted.

#### 3.1.6 Content Property
Endorsements MAY have a [`content`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-content) property, which contains HTML-formatted text which is a statement from the `subject` actor making the endorsement.

#### 3.1.7 Image Property
Endorsements MAY have an [`image`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-image) property, which contains a [Link](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-link) to an image associated with this endorsement.

#### 3.1.8 Tag Property
Endorsements MAY have a [`tag`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-tag) property, which contains one or more [Hashtags](https://www.w3.org/TR/activitystreams-vocabulary/#h-microsyntaxes) that help focus the nature of the endorsement. Hashtag definitions are left up to the actor making the endorsement.

#### 3.1.9 StartTime Property
Endorsements MAY have a [`startTime`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-starttime) property, which contains the date and time that an Endorsement becomes valid.

Endorsements without a startTime property are considered to have started at the beginning of time.

Endorsements are considered "inactive" if the current time is before the value of the `startTime` property.

#### 3.1.10 EndTime Property
Endorsements MAY have an [`endTime`](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-endtime) property, which contains the date and time that an Endorsement stops being valid.

Endorsements without an endTime property are considered to be valid in perpetuity, or until revoked.

Endorsements are considered "inactive" if the current time is after the value of the `endTime` property.

#### 3.1.11 URL Property
Endorsements MAY have a `url` property, which contains a URL that displays the endorsement in a human-friendly way (i.e. NOT in raw JSON-LD).

If this value is not present, systems SHOULD assume that the `id` property uses HTTP content negotiation to display the endorsement in either an HTML or JSON-LD format.

#### 3.1.12 Endorsement Example
```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "type": "Endorsement",
  "id": "https://alice.social/endorsements/1234",
  "subject": "https://alice.social/@alice",
  "object": "https://bob.social/@bob",
  "context": "https://w3id.org/fep/d471#humanity",
  "content": "Bob is swell",
  "proof": {/* fep-8b32 cryptographic proof */},
  "to": "https://www.w3.org/ns/activitystreams#Public"
}
```

### 3.2 Endorsement Contexts
This section is a work in progress. Please help us update and correct the concepts here.

#### 3.2.1 Humanity
https://w3id.org/fep/d471#humanity

This identifies the "endorsee" as a real human, instead of being a bot or AI account.

#### 3.2.2 Identity
https://w3id.org/fep/d471#identity

This identifies the identity of the "endorsee" as being accurate, and not an impersonator account.

#### 3.2.3 Character
https://w3id.org/fep/d471#character

This identifies the "endorsee" as having certain character qualities, identified in hashtags. Example uses might be: #honesty, #kindness, or #bravery

#### 3.2.4 Ability
https://w3id.org/fep/d471#ability

This identifies the "endorsee" as having certain abilities, identified in hashtags. Example uses might be: #musician, #acrobat, #pirate

### 3.3 The `endorses` Collection
Actors who publish endorsements MUST publish an `endorses` collection at the root of their JSON-LD profile. This is an [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) that contains all of their currently active endorsements.

The `endorses` collection is defined with the URI:
`https://w3id.org/fep/d471#endorses`

Endorsements are considered "inactive" when the current time is either before their `startTime` property, or after their `endTime` property. Inactive endorsements MUST NOT be included in this collection.

Endorsements are considered "revoked" after the originating actor publishes a `Delete` activity for it (§4.5). Revoked endorsements MUST NOT be included in this collection.

Actors MUST NOT publish endorsements in this collection if they have not been accepted by the actor in the `object` property.

### 3.4 The `endorsedBy` Collection
Actors who have received and accepted endorsements MUST publish an `endorsedBy` collection at the root of their JSON-LD profile. This is an [OrderedCollection](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection) that contains all of the endorsements that this actor has accepted from other actors.

The `endorsedBy` collection is defined with the URI:
`https://w3id.org/fep/d471#endorsedBy`

Endorsements are considered "inactive" when the current time is either before their `startTime` property, or after their `endTime` property. Inactive endorsements MUST NOT be included in this collection.

Endorsements are considered "revoked" after the originating actor publishes a `Delete` activity for it (§4.5). Revoked endorsements MUST NOT be included in this collection.

## 4. Workflow
This section walks through all of the scenarios in which "Alice" initiates an endorsement of "Bob". In high-level terms, she sends an Offer that he either Accepts or Rejects.

Endorsements use the common ActivityPub `Offer`/`Accept`/`Reject` workflow to prevent actors from using endorsements in abusive or malicious ways.

### 4.1 Offer an Endorsement
Alice begins the workflow by creating an endorsement record. This record MUST NOT be published publicly until after Bob accepts the endorsement (§4.2).

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "type": "Endorsement",
  "id": "https://alice.social/@alice/endorsements/1234",
  "subject": "https://alice.social/@alice",
  "object": "https://bob.social/@bob",
  "context": "https://w3id.org/fep/d471#identity",
  "content": "Bob is swell",
  "proof": {/* fep-8b32 cryptographic proof */}
}
```

After the endorsement has a publicly resolvable URL, Alice sends an `Offer(Endorsement)` to Bob.

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "actor": "https://alice.social/@alice",
  "to": "https://bob.social/@bob",
  "type": "Offer",
  "object": "https://alice.social/@alice/endorsements/1234"
}
```

Alice MUST wait for a reply from Bob before publishing the endorsement (§4.4).

### 4.2 Accept an Endorsement
If Bob wants to accept this endorsement, he MUST send an `Accept(Endorsement)` response to Alice.

After receiving this activity, Alice MUST add the `Endorsement` into her `endorses` collection. This fulfills the contract she offered to Bob.

After successfully delivering this message, Bob SHOULD add the `Endorsement` into his `endorsedBy` collection, although there are certain situations where a person may accept an endorsement but not publish it.

#### 4.2.1 Accept Example
```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "id": "https://bob.social/@bob/activities/5678",
  "actor": "https://bob.social/@bob",
  "to": "https://alice.social/@alice",
  "type": "Accept",
  "object": "https://alice.social/@alice/endorsements/1234"
}
```

### 4.3 Reject an Endorsement
Bob may not want Alice's endorsement, or may not want to be associated with her. In this case, Bob MUST send a `Reject(Endorsement)` response to Alice.

After receiving this activity, Alice MUST remove the `Endorsement` from her profile.

Bob may `Reject` Alice's endorsement at any time after she `Offer`s it. This could even be after having previously `Accept`ed her endorsement.

Rejecting an endorsement is final and cannot be undone. If Bob changes his mind after sending the `Reject` message, then he will have to ask Alice to generate a new endorsement instead.

#### 4.3.1 Reject Example
```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "actor": "https://bob.social/@bob",
  "to": "https://alice.social/@alice",
  "type": "Reject",
  "object": "https://alice.social/@alice/endorsements/1234"
}
```

### 4.4 Publish an Endorsement
When Alice receives an `Accept(Endorsement)` activity from Bob, she SHOULD publish an activity that adds this endorsement to her `endorses` collection.

This Add activity SHOULD be addressed to her followers, and MAY be addressed to "Public".

#### 4.4.1 Publish Example
```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "actor": "https://alice.social/@alice",
  "type": "Add",
  "object": "https://alice.social/@alice/endorsements/1234",
  "target": "https://alice.social/@alice/endorsements",
  "to": [
    "https://alice.social/@alice/followers",
    "https://www.w3.org/ns/activitystreams#Public"
  ]
}
```

### 4.5 Delete an Endorsement
If Alice decides to withdraw her endorsement of Bob, she MUST send a `Delete(Endorsement)` activity to Bob.

Alice may send this activity at any time after sending the `Offer(Endorsement)` activity from §4.1. Specifically, this may occur either _before_ or _after_ Bob accepts her endorsement.

After Alice publishes this `Delete(Endorsement)` activity, the endorsement is considered **revoked** and is no longer valid.

After receiving this message, if Bob has accepted the endorsement, then he MUST remove the activity from his `endorsedBy` collection.

After receiving this message, if Bob has not accepted the endorsement, then his server software SHOULD remove it from his user interface and no longer display it as an option to `Accept` or `Reject`.

After delivering this message, Alice's server MUST respond to requests for this `Endorsement` URL with a 404 Not Found error, or a [Tombstone](https://www.w3.org/TR/activitystreams-vocabulary/#dfn-tombstone) record.

`Delete`ing an endorsement is final, and cannot be undone. If Alice decides to endorse Bob anyway, then she will need to issue a new endorsement.

#### 4.5.1 Delete Example
```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/d471"
  ],
  "actor": "https://alice.social/@alice",
  "type": "Delete",
  "object": "https://alice.social/@alice/endorsements/1234",
  "to": [
    "https://alice.social/@alice/followers",
    "https://www.w3.org/ns/activitystreams#Public"
  ]
}
```

## 5. Security Considerations
Without safeguards, endorsements may be used in many malicious ways to deceive, harm, or harass others. Applications implementing endorsements SHOULD implement these security limitations.

### 5.1 Endorsements Must Be Opt-In
Endorsements use the standard ActivityPub `Offer`/`Accept`/`Reject` workflow to guarantee that a malicious user cannot publish a misleading or harmful endorsement. The target actor MUST accept the endorsement for it to be valid, and [Object Integrity Proofs](https://w3id.org/fep/8b32) ensure that endorsements are not maliciously changed after being accepted.

### 5.2 Verifying Endorsement Authenticity
Any third party that relies on an endorsement MUST verify it with both parties to the endorsement. This means:

1. Receivers MUST verify the Object Integrity Proof attached to the endorsement.
2. If an endorsement is received from the subject actor, then it MUST be confirmed to be present in the target actor's `endorsedBy` collection. This prevents the "subject actor" from publishing an endorsement that has not been `Accept`ed by the target actor.
3. If an endorsement is received from the target actor, then it MUST be confirmed to be present in the subject actor's `endorses` collection. This prevents the "target actor" from publishing a false endorsement, or continuing to publish an endorsement after it has been revoked.

### 5.3 Maximum Number of Endorsements
Servers that rely on endorsements SHOULD establish a maximum number of endorsements that they will trust from any one actor. This prevents botnets and sock-puppet accounts from gaming the system with enormous numbers of fraudulent endorsements.

A maximum of 100 endorsements per person is recommended for most cases, though certain uses may require exceptions. For instance, a university may issue endorsements for graduates, or for those who attend a seminar.

Servers MAY also consider applying a rate limit to endorsements, so that bots do not endorse an enormous number of people in a very short period of time.

MORE WORK IS REQUIRED

## 6. User Interface Considerations

This section is non-normative and will probably end up in separate documents in the future.

The sections above define a simple protocol for offering, accepting, rejecting, publishing, and deleting endorsements. But _how we actually use endorsements_ is the driving issue. This is also open to the widest interpretation by application developers.

**The fundamental principle is this: anyone can publish anything they want; it is up to each receiver to decide which statements they will believe and which ones they will reject.**

The above principle is already at work in the way that we use blocks and mutes to ignore certain actors on the Fediverse. Below is an example that uses this principle for endorsements as well.

### 6.1 Web of Trust
Endorsements form a personalized [web of trust](https://en.wikipedia.org/wiki/Web_of_trust) that spreads outward from each individual user in their own relative center.

* A person's first-degree network consists of all people that they currently endorse, i.e. everyone in their `endorses` collection.
* A person's second-degree network consists of all people endorsed by the people in their first-degree network.
* A person's third-degree network consists of all people endorsed by the people in their second-degree network. And so on.

People outside one's web of trust may be perfectly fine individuals, but this is simply not proven by the existing network.

Applications that rely on endorsements SHOULD have safeguards to identify fraudulent endorsements. This is easiest to do by reading _but not trusting_ the endorsements made by unknown actors. For example, if someone wants to "game the system" by endorsing themselves from 100 sock-puppet accounts, servers would simply disregard the sock-puppet endorsements because they come from untrusted actors.

MORE WORK IS REQUIRED

### 6.2 Trust Scores
User-facing systems could crawl their users' webs of trust to calculate a "trust score" for every actor they encounter online. Since there is no single "root node" to the web of trust, all trust scores MUST be relative to each individual user.

As a simple example, systems might simply display "1st", "2nd", and "3rd" badges next to people in various degrees of a user's web of trust.

As a more complicated example, a trust score might be calculated by giving each actor a certain number of points for each endorsement within the user's web of trust. The table below includes some example weights to illustrate this idea, but it is not a specific recommendation for implementors.

| Connection | Points    |
| ---------- | --------- |
| 1st degree | 50 points |
| 2nd degree | 25 points |
| 3rd degree | 5 points  |

A system then might identify various levels, such as low, medium, and high trust levels:

| Trust Level | Points     |
| ----------- | ---------- |
| Low         | 20+ points |
| Medium      | 40+ points |
| High        | 50+ points |

Using these two tables, we can compute Alice's trust score for Bob. If she has endorsed him directly (or if she endorses two others who have endorsed Bob) then she has a high trust score for him. If she has several 3rd-degree endorsements who trust Bob, then perhaps he would earn a medium trust score with Alice.

### 6.3 Server-Level Endorsements
Servers MAY endorse other servers. Server admins MAY make server-level endorsements on behalf of the server's [Application actor](https://w3id.org/fep/2677). And, application actors MAY endorse other application actors. This achieves the same things at the server level that individual endorsements do on an individual level.

The algorithms that determine trust scores (and other uses of the endorsements web of trust) may consider an implicit endorsement from each actor on a server to their server's application actor.

In the examples above, Alice (@alice@alice.social) has a profile hosted on the domain "alice.social" so Alice's server may assume an implicit endorsement from @alice@alice.social -\> @application@alice.social.

If the admins of alice.social endorse Bob (@bob@bob.social) then Bob would implicitly be a 2nd-degree endorsement of Alice's. (@alice@alice.social -\> @application@alice.social -\> @bob@bob.social)

If the admins of alice.social endorse the entire bob.social server, then Bob (and everyone on his server) would implicitly be a 3rd-degree endorsement of Alice's. (@alice@alice.social -\> @application@alice.social -\> @application@bob.social -\> @bob@bob.social)

### 6.4 Displaying Endorsements
People may choose to display links to other people they have endorsed directly on their profile page HTML. Similarly, people may wish to display the others who have endorsed them on their profile page HTML. These decisions, and the specific formats to be used, are left up to individual application developers.

Applications may also display endorsements and trust scores in each user's timeline. For example, trust scores could be displayed in a post or comments next to each actor's name or avatar image. From there, additional information might be available.

When displaying endorsements and trust scores, there are many factors that may be difficult for a machine to calculate. So, it is important to provide a clear, complete view of that person. The simplest solution is to only display endorsements within the user's own web of trust. However, sophisticated users may also benefit from seeing _all_ of an actor's endorsements and judging for themselves if they are legitimate or scammy.

### 6.5 Endorsements as Discovery
Trust levels could be used algorithmically to suggest people to follow, or to sort posts based on various trust levels. Applications that do this should make it clear when endorsements are being used to boost particular actors or content, and should provide a way for actors to opt out of or disable this algorithmic feature.

### 6.6 Endorsements as Permission
Trust levels could be a permission setting on posts: in addition to limiting posts to "Followers Only", you could make posts only for "People I Endorse" or "People within my Trust Network" (with a depth of 1, 2, or 3).

This goes a long way to facilitating small communities on the Fediverse.

## 7. Additional Discussion

This section is non-normative and will probably end up in separate documents in the future. It discusses specific issues that affect how endorsements may be used. MORE WORK IS NEEDED

### 7.1 How Endorsements Preserve Privacy
Endorsements are privacy-preserving for two main reasons: 1) they are opt-in, so nobody can publish an endorsement without your consent, and 2) they only address the _actor profile_, and not the individual. If a person has multiple personas, each of these accounts generates their own reputation and trust score. Endorsements provide no linking from the actor back to the individual person without their consent.

### 7.2 Why Not Reuse Follows and Likes?
There are several reasons why Endorsements are different from `Follow` and `Like` activities. The primary reason is stated above: the opt-in nature of Endorsements means that both parties have agreed to publish this object, which is not always the case for a `Follow` and is never the case for a `Like`.

In addition, there are many reasons why you might want to `Follow` someone's content even if you would not endorse them or their work to others.

And last, Endorsements are built to carry additional metadata that is not present in `Follow` and `Like` activities. Properties like `content`, `context`, and `tag` allow Endorsements to tell a much richer story than is possible with default activities.

## References

- [ActivityStreams Vocabulary](https://www.w3.org/TR/activitystreams-vocabulary/)
- [FEP-8b32: Object Integrity Proofs](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md)
- [FEP-2677: Identifying the Application Actor](https://w3id.org/fep/2677)

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
