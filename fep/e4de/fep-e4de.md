---
slug: "e4de"
authors: Dmitry Skavish <skavish@gmail.com>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-e4de-closing-registration-on-unattended-servers/8854
relatedFeps: FEP-f1d5, FEP-baf5, FEP-d556, FEP-2677
dateReceived: 2026-08-10
---
# FEP-e4de: Closing Registration on Unattended Servers

## Summary

A server that hands out accounts needs somebody watching the door. When nobody with instance-wide moderation
authority has been present for a long time, signups, reports and the moderation queue go unattended, and the
server becomes cheap infrastructure for spam and abuse aimed at everyone else.

This FEP defines:

- **Operator presence**: what counts as evidence that a human with moderation authority is still there.
- **The unattended state**: entered when no such evidence has been recorded for a configured period.
- **Fail-closed onboarding**: every path to a new local account closes together, and nothing else changes.
- **A published signal**: `unattendedSince`, carried in NodeInfo metadata and on the application actor.
- **Peer behaviour**: what other servers should and should not conclude from that signal.

This FEP is about liveness, not authorization. It does not define moderation policy, does not describe how
accounts are suspended, and does not address moderation scoped to a single group or community.

## Motivation

An abandoned server externalizes its costs. The junk accounts accumulate locally; the spam, the harassment and
the unanswered reports arrive somewhere else. The remedy available to the receiving side is a domain-level block,
which lands on every account on that domain, including the ordinary users who were there first, and is rarely
revisited once applied. Closing the door before the abuse starts is cheaper for everyone than a blocklist entry
afterwards.

Only the origin can close that door. Peers cannot stop signups on a server they do not run, and they infer
abandonment by hand today, from unanswered reports and bouncing contact addresses. A server that knows it is
unattended can act on it before anything happens, and say so in a form other servers can read.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY",
and "OPTIONAL" in this document are to be interpreted as described in [RFC-2119].

## Terminology

**Responsible operator**: a local account holding instance-wide authority to review signups, act on reports, or
moderate accounts other than its own. This covers the administrator described in [FEP-baf5] and any narrower
instance-wide moderation role a server defines. An account whose authority is confined to one group or community
(see [FEP-1b12]) is not a responsible operator here.

**Presence event**: a recorded moment at which a responsible operator demonstrably attended to the server.

**Absence threshold**: a configured duration, referred to below as *N*.

**Unattended state**: the state a server enters when no presence event has been recorded within the last *N*.

**Onboarding path**: any mechanism by which a person without a local account can obtain one without a responsible
operator deciding on that particular request. This includes, and is not limited to:

- an open registration form;
- invitation links or codes issued before the absence began;
- a signup queue that approves automatically, on a timer, or by any rule not involving an operator;
- account provisioning from an external identity provider;
- account creation through an API using a long-lived credential;
- inbound account migration that creates a new local account.

## Detecting Absence

### What counts as presence

A presence event is evidence that a human holding operator authority interacted with the server. What they did
with it does not matter; that they were there does.

A server MUST record a presence event when a responsible operator completes an interactive authentication, and
SHOULD record one for any other request it can attribute to that operator acting at that moment: opening the
report queue, reading their own timeline, posting, acting on an account.

The following MUST NOT be recorded as presence events:

- renewal of a session, refresh token or access token without re-authentication;
- requests from automated clients holding long-lived credentials (backup jobs, monitoring, deployment tooling,
  bridges, bots);
- receipt or delivery of mail or other notifications;
- passive traffic such as health checks and uptime probes;
- any activity by an account that is not a responsible operator.

The test is whether a human caused the request, not which part of the server it reached. An operator who reads
their own timeline every day is present, and on a server that alerts operators when the moderation queue needs
attention they are also reachable, since they never have to open the queue to learn that it is empty. An operator
whose client refreshes a token every hour from a phone in a drawer is not present. Many implementations track a
"last active" timestamp that cannot tell those two apart, because it advances on token refresh or background
polling; such a timestamp records that a credential exists, not that a person was there.

This FEP detects abandonment, not negligence. An operator who shows up daily and ignores the queue is a problem
it cannot see and does not try to.

### Evaluating the threshold

A server MUST evaluate the condition at least once per day; hourly is RECOMMENDED. The evaluation MUST be
idempotent, and MUST depend only on the server's own records: no remote party may cause, delay or prevent the
transition.

*N* MUST be configurable by a responsible operator. A default between 7 and 30 days is RECOMMENDED, and the
mechanism SHOULD be enabled by default.

Before the threshold is reached, a server SHOULD warn every responsible operator out of band, early enough to
act; a warning at three quarters of *N* is RECOMMENDED.

## Entering the Unattended State

### Every onboarding path closes together

On entering the unattended state, a server MUST close every onboarding path it offers, in one transition.

A registration form that reports itself closed while invitation codes still work is not a closed door.
Invitations issued before an operator disappeared keep circulating, and the same holds for an identity provider
that provisions accounts on first login or a queue that approves on a timer.

A server MUST durably record the transition: when it happened, the threshold in force, and the most recent
presence event.

### What does not change

The unattended state closes the door; it is not a suspension of the server. A server in this state:

- MUST allow existing local users to authenticate, read, post and interact as before;
- MUST keep account export, migration to another server, and account deletion available, so that no user is
  trapped on a server whose operators have gone;
- MUST continue to federate in both directions.

Local users did not cause their operators' absence, and degrading their accounts adds a second harm to the first.

### Notifying the operators

A server MUST attempt to notify every responsible operator through a channel that reaches them without logging
in, such as email. A notice shown only after login is worthless to someone who is not logging in.

The notification MUST be sent once per transition into the unattended state, and MUST NOT be repeated while the
server remains in it. It SHOULD state that registration is closed, the threshold that was exceeded, the last
recorded presence event, and how to reopen.

## Leaving the Unattended State

A presence event does not reopen registration. A server MUST NOT leave the unattended state automatically.

Reopening MUST require an explicit action by a responsible operator, distinct from authenticating. Before that
action, the server SHOULD present what accumulated during the absence: pending reports, queued signup requests,
and the record of the transition, including the date and the reason.

On reopening, the server clears the published signal, records a fresh presence baseline, and restores the
onboarding paths the operator chooses; restoring all of them is not required.

Returning to service should be a decision rather than a side effect: a door that reopens by itself lets signups
resume before anyone has looked at the queue that built up.

## Advertising the State

An unattended server publishes one fact: the point in time from which it has been unattended. The property is
named `unattendedSince` and carries a timestamp in the format described by [RFC-3339], RECOMMENDED to be
truncated to midnight UTC of the day of the transition.

Absence of the property means the server is attended, or does not implement this FEP. A server MUST remove the
property when it leaves the unattended state. A server MUST publish the property in each of the two locations
below that it already serves, and the two MUST agree.

### NodeInfo

While unattended, a server MUST report `openRegistrations` as `false`. [FEP-f1d5] already requires the concept to
exist, so every existing consumer understands it. The timestamp goes in the `metadata` object:

```json
{
  "version": "2.1",
  "software": { "name": "example", "version": "1.4.0" },
  "openRegistrations": false,
  "usage": { "users": { "total": 214 } },
  "metadata": {
    "unattendedSince": "2026-08-01T00:00:00Z"
  }
}
```

### Application actor

A server that publishes an application actor, as described in [FEP-d556] and [FEP-2677], SHOULD carry the same
property there, so that a consumer already fetching the actor need not also fetch NodeInfo:

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/fep/e4de"
  ],
  "type": "Application",
  "id": "https://server.example/actor",
  "inbox": "https://server.example/actor/inbox",
  "unattendedSince": "2026-08-01T00:00:00Z"
}
```

The JSON-LD context at `https://w3id.org/fep/e4de` defines the term:

```json
{
  "@context": {
    "fep-e4de": "https://w3id.org/fep/e4de#",
    "unattendedSince": {
      "@id": "fep-e4de:unattendedSince",
      "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
    }
  }
}
```

### Reading the two signals together

`openRegistrations: false` on its own gives no reason: it covers a deliberately invite-only community, a server
at capacity, and an abandoned one alike. Accompanied by `unattendedSince`, it says the door is closed because
nobody is watching it. The first is a functioning server making a choice; the second is a server whose users have
nobody to report anything to.

## Behaviour of Other Servers

The signal is self-asserted: it attests to nothing beyond what the origin chooses to say about itself. Consumers
MUST NOT use it as an input to authorization or to any signature verification decision.

A remote server MUST NOT treat `unattendedSince` on its own as grounds to defederate, suspend or block the
origin. Closing registration on discovering that nobody is watching is the correct behaviour, and punishing the
disclosure teaches other implementations to stay quiet.

A remote server SHOULD:

- stop presenting the origin as a place to sign up. Directories, "pick a server" listings and signup referral
  flows such as [FEP-7b29] are how strangers arrive at a server, and sending them to an unattended one recreates
  the problem the origin just solved;
- continue delivering to and accepting from the origin normally, since its users are still there.

A remote server MAY:

- warn a local user who is about to follow, or migrate an account to, the origin;
- apply heightened scrutiny (rate limits, spam scoring) to material originating there. The users are
  unsupervised, not presumed malicious;
- treat any `Flag` addressed to that origin as unlikely to be acted upon, and reach for local remedies rather
  than waiting for a reply. Silence from an unattended server SHOULD NOT be read as hostility.

## Security and Privacy Considerations

### Announcing that nobody is watching

The signal tells abusers exactly what it tells peers: this server has nobody minding it. That is a real cost, and
it is worth stating plainly rather than glossing over.

Three things keep it small:

- The most useful thing an abuser could do with an unattended server is open accounts on it, and that is already
  impossible by the time the signal appears.
- Abandonment is visible from the outside anyway. Reports go unanswered and contact addresses bounce, so anyone
  determined enough to look will find out with or without the signal.
- What gets published is one coarse date about the server, and nothing at all about the people running it.

A server MUST NOT publish, as part of this signal, the identity of its responsible operators, when each of them
was last present, or how many of them there are.

A server that still considers the risk too high MAY publish `openRegistrations: false` and omit
`unattendedSince`. All it gives up is the ability to distinguish itself from a server that is closed by choice.
Every protection in this FEP still applies.

### Closing a server that is not abandoned

The operator of a one-person server goes away for three weeks, and the server closes its registration while they
are gone.

This is the failure the design accepts, and it is deliberately a cheap one:

- the operator is warned before it happens;
- nothing is deleted, and no user is locked out;
- reopening takes a single action on their return;
- the only loss is the signups that would have arrived in the meantime.

The opposite failure is not cheap. A server that stays open too long collects a domain-level block that outlives
the incident and takes its innocent users with it. Operators of small servers should set *N* generously.

## References

- [FEP-f1d5: NodeInfo in Fediverse Software][FEP-f1d5]
- [FEP-baf5: Administrator Collection][FEP-baf5]
- [FEP-d556: Server-Level Actor Discovery Using WebFinger][FEP-d556]
- [FEP-2677: Identifying the Application Actor][FEP-2677]
- [FEP-1b12: Group federation][FEP-1b12]
- [FEP-7b29: Federated Signup Requests][FEP-7b29]

[FEP-f1d5]: https://codeberg.org/fediverse/fep/src/branch/main/fep/f1d5/fep-f1d5.md
[FEP-baf5]: https://codeberg.org/fediverse/fep/src/branch/main/fep/baf5/fep-baf5.md
[FEP-d556]: https://codeberg.org/fediverse/fep/src/branch/main/fep/d556/fep-d556.md
[FEP-2677]: https://codeberg.org/fediverse/fep/src/branch/main/fep/2677/fep-2677.md
[FEP-1b12]: https://codeberg.org/fediverse/fep/src/branch/main/fep/1b12/fep-1b12.md
[FEP-7b29]: https://codeberg.org/fediverse/fep/src/branch/main/fep/7b29/fep-7b29.md

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright
and related or neighboring rights to this work.
