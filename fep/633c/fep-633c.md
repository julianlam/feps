---
slug: "633c"
authors: Bart Overkamp <bart@bedrijfzondernaam.nl>, Robin Genis <roboburr@gmail.com>
status: DRAFT
dateReceived: 2026-07-21
discussionsTo: https://socialhub.activitypub.rocks/t/fep-633c-guardians/8816
relatedFeps: FEP-e232, FEP-5624, FEP-5feb, FEP-5e53, FEP-8b32, FEP-521a, FEP-7888, FEP-171b, FEP-7458, FEP-11dd
---
# FEP-633c: Guardians

## In plain words (non-normative)

Imagine a child on the Fediverse. A stranger says something nasty. The child can't do much, and the parent feels helpless too: it came from someone far away on the internet, so there is "nothing I can do."

This proposal fixes that. An account can have **guardians** attached to it, the way a child has parents. The guardians decide who is allowed to follow the account, and the child can **call them in** whenever something feels wrong or confusing. Because everyone speaks the same rules, the guardians can then actually reach the person who did it and sort it out, adult to adult, instead of anyone shouting at the child.

Guardians are added carefully (both sides and any existing guardians have to agree), and leaving works too: as a child grows up, the guardians can loosen the rules or step away entirely. The rest of this document writes all of that down precisely, so any Fediverse software can build it the same way.

## Summary

This FEP defines a lightweight vocabulary and a set of activities that let one `Actor` (a **ward**) be watched over by one or more other `Actor`s (its **guardians**). Guardians co-approve who may follow or subscribe to the ward, and receive moderation escalations concerning the ward through in-protocol *and* out-of-band channels.

The goal is a concrete, minimal mechanism that makes the Fediverse a safe, promotable alternative to Big Tech for people who need a recourse structure around them: primarily children, but also any account that a trusted party has agreed to look after. The FEP provides the *mechanism*; it deliberately does not define *policy* (age verification, what counts as harmful, jurisdiction). Those remain with implementers.

The vocabulary originates in a guardian-gated Fediverse implementation and is namespaced accordingly (§2); it is intended for adoption by any implementation. The reasoning behind the design decisions in this document is recorded separately, in the namespace document at `https://ns.klonkt.com/shaer`.

## Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC2119].

This FEP builds on [ActivityPub] and [ActivityStreams2].

## 1. Model

There are three, and only three, states an `Actor` may occupy with respect to guardianship:

1. **Free**: the default. No `shaer:guardians`, no `shaer:isGuardian`.
2. **Ward**: has a non-empty `shaer:guardians`. Its follows/subscriptions are gated and its moderation escalations are routed to its guardians.
3. **Guardian**: has `shaer:isGuardian: true`. It watches over one or more wards.

The states are mutually exclusive:

- A **guardian MUST be free of guardians.** `shaer:isGuardian` and `shaer:guardians` MUST NOT both appear on the same `Actor`. Setting `shaer:guardians` on an actor that is a guardian is a configuration error.
- An `Actor` that is **free** or already a **Guardian** MAY become a (further) `Guardian`; a guardian may watch over more than one ward. Equivalently: only a **ward** is barred from becoming a guardian.

The structure is therefore **flat and non-recursive**: there are wards and there are guardians, and a guardian is never itself a ward. There is no "grand-guardian" (see §4).

## 2. Vocabulary

All terms are defined in the namespace:

```
https://ns.klonkt.com/shaer#
```

with the RECOMMENDED prefix `shaer`. A JSON-LD context that binds that prefix and carries the type information of the terms below is served at:

```
https://ns.klonkt.com/shaer
```

Implementations SHOULD reference that context document in their JSON-LD `@context`, as the examples in §9 do. Binding the prefix inline instead resolves the term *names* but carries no type information, and `shaer:guardians` then expands to string literals rather than to actor references — which defeats the resolvability §2.1 depends on. Consumers that do not understand the terms MUST ignore them (per [ActivityStreams2] extensibility) and MUST continue to operate normally.

The same URI serves a human-readable namespace document, which indexes these terms and records the reasoning behind the design decisions in this FEP. That document is non-normative; where it and this FEP disagree, this FEP governs.

### 2.1 On `Actor` objects

- **`shaer:guardians`** — a `Collection`, or an array of actor URIs. The guardian actors watching over this ward. Presence (non-empty) marks the actor as a **ward**.
- **`shaer:isGuardian`** — `xsd:boolean`. `true` marks the actor as a **guardian**. Mutually exclusive with `shaer:guardians`.

`shaer:guardians` is a **public** property of the actor, resolvable like any other actor property. Publishing it is what lets anyone with a concern reach the responsible adults rather than the ward (§5, §7). A deployment MAY deliver the list as bare references rather than embedded objects; the membership is not confidential.

### 2.2 On `Object`s (e.g. `Note`)

- **`shaer:hasGuardians`** — `xsd:boolean`. Advisory hint that the `Actor` responsible for this object is a ward (has guardians).
- **`shaer:helpRequest`** — `xsd:boolean`. Marks a direct `Note` as a ward's call for help to its guardians (see 5.2.1). Guardian-side clients MAY render it as an alert; everyone else safely ignores it.

`shaer:hasGuardians` is a routing hint for observing implementations: it tells a remote server "interactions with this object should be treated as involving a guarded actor, so route reports/approvals to the author's guardians." It MUST NOT affect regular delivery, rendering, or storage, and MUST be safely ignorable by non-observing implementations.

> **Resolved (A).** Because `shaer:guardians` is public on the actor (§2.1), no separate boolean is needed there: the guardian list itself is the ward-signal. `shaer:hasGuardians` therefore lives **only on objects**, as a per-object routing marker a remote server can act on without fetching the actor, and as the anchor for the legacy/rectification rules in §3.4.1.

### 2.3 The gated-setting proposal (§5.6)

- **`shaer:GatedSetting`** — an `Object` type. The object of an `Offer`: a proposed value for one guardian-controlled setting of one ward.
- **`shaer:ward`** — actor URI. Which ward the proposal is about.
- **`shaer:feature`** — IRI. Which setting. Deployments SHOULD use an IRI they control; this FEP names `shaer:externalEmbeds` (may non-fediverse link previews and embeds be shown) as the worked example.
- **`shaer:value`** — `xsd:boolean`, or a string. The proposed value.

These exist because nothing in [ActivityStreams2] expresses "a group of named adults jointly decides a setting on someone else's account". Where AS2 or another FEP already covers a need, use that instead: this FEP adds vocabulary only where it must.

### 2.4 Availability and lapse (§3.6)

- **`shaer:away`** — `xsd:boolean`. On a direct object from a guardian to its ward: declared absence, lasting until the object's `endTime` (§3.6.1).
- **`shaer:dormant`** — `xsd:boolean`. On a direct object from a ward's server to a guardian: notice that the guardian has been observed dormant (§3.6.2).
- **`shaer:Lapse`** — an `Object` type. The object of an `Offer`: a proposal to release one dormant guardian from one ward (§3.6.3). Names the ward in `shaer:ward` and the guardian in `object`.

The same restraint as §2.3 applies: `endTime` is plain [ActivityStreams2], and both markers ride ordinary direct notes exactly as `shaer:helpRequest` does, so a party on a non-observing server still receives a readable human message.

### 2.5 On the guardianship `Relationship`

- **`shaer:Guardian`** — a relationship type. The `relationship` value of the [ActivityStreams2] `Relationship` that models one guardianship (§3): the ward in `subject`, the guardian in `object`.

This is the only term that names the bond itself rather than a property of one of the parties, which is why it appears in the `Offer` of §3.1 and in every `Undo` that ends a guardianship (§3.2). The compact form `shaer:Guardian` and the full IRI `https://ns.klonkt.com/shaer#Guardian` are the same term: §3 writes it out, §9.3 uses the prefix.

## 3. Establishing guardianship (the handshake)

Guardianship is created by an explicit, multi-party, two-phase handshake. **No single party may create a guardianship alone.** This is the core safety property: a lone actor can neither insert itself as guardian over a child, nor (if the ward already has a guardian) can a new guardian be added without the existing guardian's consent.

Guardianship is modelled as an [ActivityStreams2] `Relationship`:

```json
{
  "type": "Relationship",
  "subject":      "https://ward.example/actor",
  "relationship": "https://ns.klonkt.com/shaer#Guardian",
  "object":       "https://guardian.example/actor"
}
```

### 3.1 Steps

1. **Offer.** The **guardian-candidate**, and only the guardian-candidate, sends an `Offer` whose `object` is the guardianship `Relationship` above. Fixing the initiator is deliberate: by offering to guard someone you publicly take on responsibility for that ward and open yourself to criticism of the ward *and* of your role as guardian. Much can and should be arranged out-of-band before this on-protocol offer is made. The `Offer` MUST be addressed to the ward, and to **all existing guardians of the ward** (if any).

2. **Party acceptance.** The guardianship is only valid once **all** of the following have `Accept`ed the `Offer`:
   - the **guardian-candidate** (agrees to serve), and
   - the **ward** (agrees to be guarded), and
   - **every existing guardian of the ward**, whenever they are reachable. If the ward has existing guardians, at least one existing guardian MUST co-accept; where possible all SHOULD.

3. **Final handle return (commit).** As the final step, the guardian-candidate returns a **handle**: a reference (e.g. an inbox URL or a capability endpoint, see §6) through which this guardian can be reached for escalations. Returning the handle is the atomic commit of the relationship.

   > An acceptor MUST NOT assume that, because it accepted, the offer still stands. The relationship is committed only when the handle is returned. An implementation MAY realise the handle return as the guardian-candidate's own `Accept` being the *last* accept in the sequence, carrying the handle in its `result`.

4. **Write.** Only upon receiving the handle does the ward add the guardian to its `shaer:guardians`, and the guardian set `shaer:isGuardian: true` (if not already set).

> **Note (first guardian, free ward).** When the ward is still **free** (has no existing guardians), the `Offer` itself constitutes the candidate's consent to serve, and the candidate's handle (§6) is its own inbox. The relationship then commits on the ward's single `Accept`: the first-guardian step is two-party (candidate offers, ward accepts), which preserves the core property that no single party acts alone while sparing a free actor a redundant round-trip. The moment the actor is a ward, the full multi-party handshake applies again: every further guardian requires the co-`Accept` of at least one existing guardian (§3.1.2), and a candidate that is itself a ward is barred (§1, enforced at commit per §4.2). This is the RECOMMENDED behaviour for a free actor; a deployment MAY instead require a distinct final handle-return from the candidate even for the first guardian.

### 3.2 Rejection and withdrawal

- Any addressed party MAY `Reject` the `Offer` before commit; a single `Reject` from a required party voids the handshake.
- After commit, either side MAY end the relationship with `Undo` of the `Relationship`. An `Undo` from a guardian, or from the ward *co-signed by an existing guardian*, removes the guardian from `shaer:guardians`.

> **Resolved (B).** The initiator is fixed: the aspirant guardian always makes the `Offer` (§3.1). Whoever offers to guard thereby exposes themselves to scrutiny over the ward and over the role, which is the intended accountability.

### 3.3 Removing a single guardian

While more than one guardian remains, a single guardian relationship MAY be ended (§3.2): an `Undo` of the `Relationship` from the guardian itself, or from the ward co-signed by an existing guardian, removes that guardian from `shaer:guardians`. The ward stays a ward as long as at least one guardian remains.

### 3.4 Emancipation (removing the `shaer:guardians` key)

Removing the **last** guardian, and thereby the whole `shaer:guardians` key so the actor becomes **free** again, is *emancipation*. Whether and how a ward may emancipate is ultimately a software/deployment choice, but this FEP gives two RECOMMENDED methods:

- **Method 1: cooperative release.** Emancipation requires the explicit approval of **at least three guardians** (a hard floor). A consequence, accepted deliberately: a ward with fewer than three guardians must first *add* guardians up to the floor before it can release them all. Releasing oversight should take at least three consenting adults, never fewer.

- **Method 2: contested release (deadlock-breaker).** Where current guardians *prevent* release, a ward MUST NOT be trapped. Emancipation is then permitted when **a majority of the guardians AND two (2) witnesses** all consent. In boolean terms, removal is allowed when:

  ```
  majority(guardian_set) AND witness_1 AND witness_2   →  emancipate
  ```

  `guardian_set` is the snapshot taken when the flow opens (§3.5), so neither side can change the arithmetic once it is running. The two witnesses stand for a contested departure: they legitimise the release without letting the ward walk away from oversight entirely on its own say-so, and they break a single holdout among the guardians.

  A witness is **not** a guardian. It holds a temporary role, scoped to this one emancipation and ending with it whatever the outcome:

  - a witness MAY answer this emancipation decision, and nothing else. It MUST NOT approve follows or replies, MUST NOT gain a guardian's read access to the ward, and MUST NOT appear in `shaer:guardians`;
  - the role ends when the flow settles. A witness who wants to stay on as a guardian MUST go through the ordinary handshake of §3.1, with the ward's and the existing guardians' consent like anyone else.

  That scoping is load-bearing. If witnesses joined `shaer:guardians` permanently and the flow may be repeated, a ward could add two sympathetic adults per attempt and, after a few "failed" attempts, outvote its actual guardians on *every* decision, not just this one. The way out of guardianship must not double as a way to hollow it out from the inside.

- **Method 3: release by lapse of time (last resort).** Neither cooperative nor contested release helps when the guardians are simply not there any more: an instance gone, an account deleted, a guardian who has died. A threshold that can never be met would leave the ward a ward for good, which is exactly the trap §3.4 exists to prevent. A ward MUST therefore be able to open an emancipation that can settle on time alone:

  1. the ward opens the emancipation; its server notifies every guardian in the set, in-protocol *and* over the out-of-band `handle` of §6;
  2. a window of **thirty (30) days** runs. As an irreversible decision it always runs in full (§3.5); reaching a threshold early does not shorten it;
  3. any guardian in the set MAY **pause** the flow once, stating a reason, which restarts the window a single time. A pause is not a veto: the same guardian MUST NOT pause the same flow twice;
  4. when the window closes, emancipation completes unless a majority of the set has rejected it.

  Time is the instrument: it gives a guardian with a real objection ample room to raise it, and denies an absent or obstructive one a permanent hold.

> **Editor's note (open question E, resolved).** The circularity is removed by making the bundled flow a single decision (§3.5) and the witnesses a non-guardian role (Method 2). The ward's server opens **one** emancipation decision; naming the two witnesses is part of *opening* it and does not itself require the guardians' approval, because a witness is not being added to `shaer:guardians`. The holdouts therefore cannot deadlock the flow by refusing the witnesses; their consent is needed only for the final removal, where they hold their majority. The witnesses' `Accept` activities are answers to that same decision, addressed to the ward's server, which tallies set and witnesses together.

> **Note (before the flow starts).** Emancipation ends the ward's ability to call in guardians (§5.2). An implementation SHOULD state this plainly before the flow is opened, and again at completion, including that returning means a fresh handshake (§3.1) and not an undo.

#### 3.4.1 Legacy of prior objects

Emancipation changes the actor going forward; it does **not** automatically rewrite the past. Objects created while the actor was a ward retain their `shaer:hasGuardians` marker by default, which keeps historical moderation routing coherent.

Data-protection law (GDPR or the local equivalent) then cuts **both** ways, and implementations SHOULD support both:

- **Erasure:** an actor MAY request removal of all objects bearing `shaer:hasGuardians`, or removal of the marker from them.
- **Rectification:** the marker MAY also be *added* to past objects retroactively, for example when someone who posted while free is later found to have belonged under a guardian. Correcting the record toward the truth is as legitimate as erasing it.

Retention of the legacy marker is the default; both erasure and rectification are the user's (or their guardians') to demand.

### 3.5 How decisions settle: thresholds and windows

Several places in this FEP put a decision in the hands of the guardians: adding a guardian (§3.1), removing one (§3.3), emancipation (§3.4), approving a follow (§5.3) and approving a reply (§5.4). They share one mechanic, defined here once.

A **decision** has three parts:

- a **set**: the guardians listed in `shaer:guardians` at the moment the decision opens. The set is *snapshotted*. Guardians added while the decision is open do not count toward it, and guardians removed do not shrink it. Without the snapshot either side could stack the set mid-decision.
- a **threshold**: the number of approvals that settles it. Unless a section states otherwise, the threshold is a **strict majority** of the set (2 of 2, 2 of 3, 3 of 4). Thresholds remain policy the guardians MAY relax as a ward matures (§5.3); this FEP fixes only the default.
- a **window**: a deadline. A decision that nobody answers MUST NOT stay open forever.

Members of the set who are **away** or **dormant** (§3.6) at the moment the decision opens form no part of the arithmetic: the threshold is computed over the **available set**, the snapshot minus those members. Availability is snapshotted together with the set, so stepping away mid-window moves nothing. Without this, a majority of a set that contains absent members can be arithmetically unreachable, and decisions expire not because anyone objected but because nobody was there to count.

The decisions of §3.4 are the exception and run over the **full** set. Method 3 already prices absence in with time, and a dormant guardian's pause is exactly the one answer that restores it (§3.6); computing emancipation over a shrunken set would make the gravest decision the cheapest to reach.

How a decision settles depends on whether it can be undone.

**Reversible decisions settle early: a race to the threshold.** The moment the threshold is met the decision fires, and the remaining guardians need not answer. Symmetrically, the moment enough rejections make the threshold arithmetically unreachable the decision fails at once, so nobody sits out a window whose outcome is already fixed. If the window closes undecided, the decision **fails closed** (it counts as a rejection) and the requester MAY try again. Follow approval (§5.3) works this way.

**Irreversible decisions run the full window.** An early threshold does NOT settle them; the clock runs out first, so every guardian in the set has had a genuine chance to speak. Emancipation (§3.4) works this way.

Which category a decision falls into is determined by the cost of a wrong approval: a follow accepted in error is undone with a block, whereas emancipation granted in error removes the recourse structure entirely and leaves the ward no standing to reverse it.

> **Note (non-normative).** Requiring every guardian to answer would hand each of them a silent veto: one unreachable or obstructive guardian could freeze a ward's social life indefinitely. A threshold with a deadline keeps the decision with the guardians while making non-response a choice with a consequence rather than a blocking move.

### 3.6 Availability

`shaer:guardians` is a public claim that these adults are watching. A guardian who no longer answers makes that claim untrue and renders the arithmetic of §3.5 unreachable. This section accounts for absence without treating it as misconduct.

A guardian stands, per ward, in one of three availability states, tracked by the ward's server:

- **active** — the default. Counts toward the available set of §3.5.
- **away** — declared by the guardian itself, with an end. Does not count toward the available set.
- **dormant** — observed by the ward's server, never declared. Does not count toward the available set.

One rule outranks everything else in this section: **one answer restores everything.** Any activity from the guardian addressed to the ward or its server returns the guardian to `active` at once, from either state, at any moment up to and including a running lapse (§3.6.3). Neither state is misconduct, and neither leaves a mark.

#### 3.6.1 Away: declared absence

A guardian declares itself away by sending its ward a direct object carrying `shaer:away: true` and an `endTime`. The `endTime` is REQUIRED: an absence without an end would let a nominal guardian hold a seat indefinitely. It rides an ordinary direct note (§2.4), so a ward on a plain-fediverse server still receives a readable message. When `endTime` passes, the guardian returns to `active` silently. Declaring away MUST NOT count as evidence toward dormancy.

Availability MUST NOT appear on the public actor document. An absence schedule is timing intelligence: it tells anyone watching exactly when the effective set is small. The ward and the co-guardians learn it through the owner-only queues (§2.1); the world keeps seeing `shaer:guardians` unchanged.

#### 3.6.2 Dormant: observed absence

Dormancy is a finding, and the evidence for it is deliberately narrow:

- it MAY follow **only from directly addressed requests that went unanswered**: a §3.5 decision the guardian was named in, or an explicit check-in. Calendar time alone MUST NOT make a guardian dormant. A guardian who was asked nothing can therefore never become dormant; implementations MAY send periodic check-ins, which count as directly addressed requests. How many misses over how long is a deployment choice, deliberately: any number written here would punish exactly the long-term ill this section exists to accommodate.
- marking a guardian dormant MUST be notified to that guardian, in protocol AND over the out-of-band handle of §6. The one-answer rule is worthless to someone who does not know an answer is wanted; the handle exists for precisely this moment.

Decisions settled while a guardian was away or dormant remain settled: restoration is never retroactive.

Delivery of a ward's call for help (§5.2) ignores availability entirely: a `shaer:helpRequest` goes to **all** guardians whatever their state. A call for help is not a decision.

When the available set is empty, every reversible decision expires and the ward cannot act at all. That is the entry condition of §3.4 Method 3 (release by lapse of time): a ward whose available set has been empty MUST be able to open it.

#### 3.6.3 Lapse: release in absentia

While a guardian is dormant, an available co-guardian MAY propose releasing it. The proposal mirrors §5.6:

```json
{
  "type": "Offer",
  "actor": "https://gran.example/actor",
  "to": ["https://kid.example/actor", "https://parent.example/actor"],
  "object": {
    "type": "shaer:Lapse",
    "shaer:ward": "https://kid.example/actor",
    "object": "https://uncle.example/actor"
  }
}
```

- it MAY be opened only against a guardian that is already dormant (§3.6.2), and only by a guardian in the available set. The ward does not open it (see the editor's note below);
- it is an **irreversible** decision in the sense of §3.5: strict majority of the available set, and the window always runs in full;
- the target is notified as for any dormancy marking (protocol AND handle), and **any** activity from the target cancels the lapse outright: one answer restores everything, up to the last moment;
- on completion the ward's server removes the guardian from `shaer:guardians` and notifies every party, the released guardian included;
- a lapse that would empty `shaer:guardians` MUST be refused: removing the last guardian is emancipation, and the road there is §3.4.

> **Note (non-normative).** A lapse can leave a single guardian in sole control, and can be wielded inside a failing relationship. This FEP deliberately does not arbitrate that case, and does not make the ward the tiebreaker between its adults. What the mechanism guarantees is narrower: a removal can be unjust, but it cannot be silent. See §10 (I); the full reasoning is in the namespace document.

## 4. No recursion ("Not a Teapot")

A valid guardian is free of guardians (§1). A malformed actor — one carrying both `shaer:isGuardian` and `shaer:guardians` — must therefore never be treated as a guardian, and an implementation **MUST NOT** recurse to such an actor's own guardians. There is no grand-guardian.

That condition has to be caught at two different moments, and the correct response differs between them: softly when delivering to several guardians (§4.1), and loudly when committing a relationship to one (§4.2).

### 4.1 At escalation delivery

When an implementation is about to deliver an escalation to a guardian and discovers that this "guardian" itself carries `shaer:guardians` (i.e. it is misconfigured as both), the implementation **MUST NOT** recurse to that actor's guardians.

Instead it MUST **fail softly**: drop the escalation to that malformed target, continue delivering to the remaining valid guardians, and SHOULD log the condition. Implementations MAY signal this with an out-of-band error; this FEP's convention is a `418`-flavoured "Not a Teapot" marker. A malformed target MUST NOT block delivery to the well-formed guardians.

### 4.2 At guardianship commit

§1 bars a ward from becoming a guardian. This section fixes when that bar is enforced, because §4.1 alone runs only once the relationship exists.

When an implementation is about to commit a guardianship (§3.1, step 3) and finds that the guardian-candidate carries `shaer:guardians`, it **MUST** refuse the commit and void the handshake. The guardianship **MUST NOT** be recorded, and the ward's `shaer:guardians` **MUST NOT** be written (§3.1, step 4).

The verification **MUST** be performed against a freshly dereferenced actor document at commit time. An actor's guardianship state MAY change between the `Offer` (§3.1, step 1) and the commit, so a check performed only on receipt of the `Offer` is NOT sufficient.

Where the actor document **cannot be dereferenced**, the implementation **MUST NOT** treat the failure as either outcome. It MUST NOT commit, because the candidate is then unverified. It MUST NOT void the handshake either: an unreachable server is not a malformed actor, and treating one as the other lets a transient failure destroy a multi-party agreement that can only be remade by repeating §3.1 in full.

The commit is therefore **deferred, not decided**. An implementation **SHOULD** retry the dereference on its own schedule rather than wait for a further activity from a party: the last `Accept` may already have arrived, in which case nothing further will trigger a retry and the handshake would stall until its window closed.

Adding a guardian is a §3.5 decision, so the hold is already bounded: if the window closes with the check still unresolved, the decision fails closed. Where that happens, the parties **MUST** be told that the handshake failed because the candidate could not be verified, and **MUST NOT** be told that it was refused. Those are different facts, and only one of them is about the candidate.

Unlike §4.1, this failure **MUST NOT be silent toward the ward**. The ward and its existing guardians **MUST** be informed, with the reason: they are parties to the handshake, the condition is derived from public data (§2.1), and a silent void would leave a ward believing an adoption completed that did not. This is the half of the refusal that is not a disclosure question.

Toward the **candidate**, the refusal SHOULD be expressed as a `Reject` of the `Offer` (§3.2), which voids the handshake by the mechanism §3 already defines and which an implementation unaware of §4 still handles correctly.

Whether that `Reject` states the reason is a deployment decision, and the trade-off is real in both directions:

- Stating it lets a candidate whose account is merely misconfigured discover and correct that. This is the common case by a wide margin.
- Commit is the **last** step of §3.1: reaching it means every other party has already accepted. A refusal that identifies itself as technical therefore discloses that the human parties consented and only the protocol objected. Where a guardianship is contested, that is precisely the fact a party may not be entitled to learn. A bare `Reject` is indistinguishable from any party's refusal under §3.2 and discloses nothing about who refused or why.

Implementations **SHOULD** therefore perform the same check when the `Offer` is received and refuse it there when the condition already holds. At that point no party has accepted, so nothing about anyone's consent can be inferred and the reason MAY be given freely. Refusing early is both the kinder path for a misconfigured candidate and the one that leaks nothing; the commit-time check remains REQUIRED as the backstop for a candidate whose state changed in between.

> **Note (non-normative).** §4.1 remains REQUIRED alongside §4.2: the two cover disjoint cases. §4.2 prevents a malformed guardianship being created; §4.1 contains one that became malformed afterwards, which no handshake-time check can detect.

## 5. Feedback and moderation

Guardianship exists to provide **recourse**: a ward must never be left without a route to act, and an adult with a complaint must have somewhere to take it other than the child.

### 5.1 Adult ↔ adult (unchanged)

Between free actors, nothing changes. Adults address adults as adults: flag a missing content warning, open a private conversation, use ordinary reporting. This FEP does not touch that path.

### 5.2 A ward can call in its guardians

This FEP does **not** ask implementations to scan for "hostile content." The mechanism is ward-driven: implementations SHOULD give a ward a simple way to **call in its own guardians** about any interaction it receives that it does not understand, finds unpleasant, or is simply unsure about. The ward is never left holding the problem alone.

When a ward invokes its guardians, software:

- **MUST** deliver the escalation in-protocol as a `Note` (or `Flag`) to each guardian's handle; **and**
- **SHOULD** additionally reach each guardian through at least one out-of-band channel where configured: e-mail, SMS, a bot relay, push, etc. (Guardians are not always watching an inbox; reliable reach is the point.)

The mechanism provides **contact, not surveillance**: it gives the guardian a defined route to reach and speak with the party concerned, so the exchange takes place between adults rather than being directed at the ward.

#### 5.2.1 The escalation note (`shaer:helpRequest`)

The in-protocol form of a call for help is a `Note` carrying `shaer:helpRequest: true`. Its shape follows the deployed private-mention (direct) model, so that a guardian on ANY ActivityPub server receives it as an ordinary readable direct message; the marker only adds meaning for guardian-side implementations.

- The note **MUST** be addressed to the ward's guardians and to no one else: their actor URIs in `to`, no `as:Public` anywhere, no followers collection. This makes it undeliverable to timelines and impossible to boost, by construction.
- Availability (§3.6) **MUST NOT** filter this delivery: the note goes to away and dormant guardians too. A cry for help is not a decision.
- The guardians **SHOULD** be tagged as `Mention` so ordinary servers notify them.
- The subject of the concern (the actor or object the ward needs help with) **MUST NOT** be addressed and **MUST NOT** be tagged as a `Mention`: in the deployed model a mention adds its target to the conversation. Reference the subject instead with an object link per [FEP-e232] (a `Link` in `tag` with the ActivityStreams media type) and/or a plain URL in the content.
- The note **SHOULD** carry evidence that survives deletion of the source: a short text quote of the object concerned, and/or an image of what the ward actually saw, as a regular `attachment`. A capture **SHOULD** render only the object concerned, never surrounding content: a screenshot of a whole screen leaks unrelated third-party material to the guardians.
- Client software **SHOULD** show the ward exactly what will be shared and ask for confirmation before sending: the ward learns what leaves the device, and accidental invocations stay harmless.
- Escalation is not reporting. Sending a `Flag` to the subject's origin server is a follow-up decision **by a guardian** (5.1); implementations **MUST NOT** auto-file a `Flag` as a side effect of a ward's call for help.
- Guardian-side implementations **MAY** render a `shaer:helpRequest` note distinctly (an alert with the evidence up front) and offer the follow-up actions of 5.1. Non-observing servers need nothing: the note reads as a normal direct message with an image.

### 5.3 Follows and subscriptions are gated

- A `Follow` targeting a ward MUST be forwarded to the ward's guardians for **approval**. The quorum is policy, and is for the guardians to set and relax as the ward's user matures: it MAY require **all** guardians, **any one** guardian, or (OPTIONAL) **no** approval at all once the guardians so decide. This FEP requires the forwarding and that the decision rests with the guardians; it does not fix the threshold.
- Where the guardians have not set a policy, the RECOMMENDED default is a **strict majority within twenty-four (24) hours**, settled as a reversible decision (§3.5): the follow is accepted the moment the majority is reached, rejected the moment a majority has become unreachable, and rejected (retryable) if the day passes undecided. A day is long enough for guardians in different time zones and short enough that someone asking to follow a child is not left hanging. Because it is a race to the threshold rather than a poll, the guardians who have answered decide, and the rest are not a bottleneck.
- A subscription request (a follow of the ward's feed / any mechanism granting ongoing access) MUST likewise be forwarded to the guardians for **co-approval**.
- A `Follow` **from a committed guardian of the ward** SHOULD be auto-accepted: the guardian is already an approved party for that ward (§3), so gating its own follow adds no safety and only delays a guardian's legitimate need to watch over its ward. Because `shaer:guardians` is public (§2.1), the ward's server can recognise the follower as a current guardian without extra coordination.

This aligns with `manuallyApprovesFollowers: true`: the difference is that the approval decision is delivered to the **guardian**, not the ward.

> **Note (implementation).** Watching over a ward is realised as an ordinary `Follow`: a guardian follows its ward, and the ward's posts (including followers-only) are then delivered to the guardian by the normal mechanism, cross-server and honouring visibility. No new fetch is required for the common case. An OPTIONAL refinement is an actor-authenticated (signed) `GET` of the ward's outbox by a guardian, which a ward's server MAY grant by checking the fetcher against the public `shaer:guardians` list; this lets a guardian read without appearing in the followers collection and lets it backfill history from before the follow. This FEP does not require the signed-fetch path.

> **Note (forwarding, modelled on §3).** When a ward's guardians are on other servers, the ward's server forwards the gated `Follow` to each guardian as an `Offer` whose `object` is that `Follow` (the same distributed shape as the adoption offer in §3, so each guardian keeps its own copy). A guardian answers with `Accept`/`Reject` addressed back to the ward's server, which tallies the quorum and, on approval, returns the standard `Accept`(`Follow`) to the original follower. Co-located guardians need no forwarding: they read and decide on the ward's own server. This keeps follow-approval and adoption on one mechanism.

### 5.4 Replies are gated

Guardianship gates follows (§5.3); replies are gated with the reply-control mechanism already deployed in the Mastodon namespace `http://joinmastodon.org/ns#`: `canReply` on an object (who may reply), the `ApproveReply` and `RejectReply` activities (the authority's decision), and an `approval` property on the reply pointing to the `ApproveReply`. This FEP builds on that deployed behaviour rather than reinventing it.

Note on provenance: these terms were originally specified in [FEP-5624] (per-object reply control), which was **WITHDRAWN** on 2025-06-24. The terms themselves remain in production use, so this FEP relies on the deployed mechanism, not on the withdrawn proposal, and treats 5624 as an informative predecessor. The live successor discussion on who owns a thread and who may join it has moved to the context and replies-collection proposals ([FEP-171b] conversation containers, [FEP-7458] replies collection, [FEP-11dd] context ownership); a future revision of this FEP SHOULD track whichever of those reaches FINAL and re-express reply-gating in its terms.

- A ward's objects SHOULD advertise a restricted `canReply` (for example the ward's `followers` and mentioned actors, not `as:Public`), so a stranger's reply arrives as pending rather than being distributed automatically. This is the reply-side counterpart of `manuallyApprovesFollowers`.
- For a ward, the approving authority is the ward's **guardians**. A reply pending approval MUST be forwarded to the guardians (reusing the `handle` and out-of-band reach of §5.2), and an `ApproveReply` or `RejectReply` MAY be issued by a guardian on the ward's behalf under the guardians' quorum policy (§5.3 leaves the threshold to the guardians). A pending reply is a reversible decision and settles like a follow (§3.5): first to the threshold, failing closed at the end of the window.
- The `shaer:hasGuardians` object hint (§2.2) is the signal a remote server needs to route a reply's approval decision to the author's guardians without first fetching the actor.

### 5.5 Discoverability is off by default (via [FEP-5feb])

A ward SHOULD set `indexable: false` ([FEP-5feb]), and a deployment MAY treat this as a default that only the ward's guardians can relax. This is stronger than FEP-5feb's own (contested) default, and reflects the stance that you reach people by connecting, not by search.

Note the deliberate asymmetry with §7: a ward's **guardians** are public (the village model), so a concerned adult can find the responsible adults, while the ward's **content** is not indexable, so strangers cannot discover the child in the first place. Reachability for recourse and discoverability to strangers are separated on purpose.

Deployments MAY additionally honour [FEP-5e53] (opt-out preference signals) on ward content for broader scraping and AI opt-out; this is OPTIONAL.

### 5.6 Gated settings: the guardians decide, across servers

§5.3–5.5 each name something a ward's guardians control. A deployment will grow more of these (external links and link previews, direct messages, who may reply, how loud "public" is). They share one shape, and it MUST work when the guardians are **not** on the ward's server, because that is the ordinary case: a child on the family instance, a grandparent on theirs.

A gated setting is a **decision** in the sense of §3.5: a snapshotted set, a threshold, a window. It is reversible (a permission granted can be withdrawn), so it settles as a race to the threshold and fails closed at the deadline.

- A guardian proposes a change by sending an `Offer` to the **ward's** server, whose `object` names the ward, the feature and the proposed value:

  ```json
  {
    "type": "Offer",
    "actor": "https://gran.example/actor",
    "to": ["https://kid.example/actor"],
    "object": {
      "type": "shaer:GatedSetting",
      "shaer:ward":    "https://kid.example/actor",
      "shaer:feature": "shaer:externalEmbeds",
      "shaer:value":   true
    }
  }
  ```

- Other guardians answer with `Accept` or `Reject` on that `Offer`, exactly as in §3.1. The **ward's server** is the one that tallies, because the ward's server is the one that enforces the setting.
- The proposing guardian's own `Offer` counts as its `Accept` (§3.1's one-step clause), so with two guardians one further `Accept` settles it.
- The ward's server MUST verify that every counted party is in `shaer:guardians` at the moment the decision opened, and MUST ignore answers from anyone else.
- A ward MAY *request* a change (the mirror of §5.2: the ward asks, the adults decide), but a ward's own answer never counts toward the threshold.

Enforcement belongs on the ward's server and MUST NOT be left to the client: a feature that a client merely hides has still been delivered to the device. Where a setting suppresses content, the content is left out of the response.

> **Note (non-normative).** A single guardian flipping a switch on another server is indistinguishable from a compromised or estranged guardian doing so. The threshold is what makes the change attributable to the guardians as a group rather than to whoever acted first, and the window is what prevents one silent guardian from blocking it indefinitely.

## 6. The handle and cross-server trust

The **handle** returned at commit (§3.1 step 3) is how a ward's server reaches a guardian for the lifetime of the relationship. At minimum it is the guardian's `inbox`. Implementations MAY make it a scoped capability (an unguessable, revocable endpoint) so that possession of the handle authorises escalation delivery without exposing the guardian's main inbox.

Escalation deliveries and handshake activities MUST be authenticated as ordinary authenticated ActivityPub server-to-server traffic: HTTP Signatures at minimum, and SHOULD prefer object integrity proofs ([FEP-8b32], built on the actor public keys of [FEP-521a]) for the security-sensitive §3 (handshake) and §5 (escalation) activities. A guardian relationship is security-sensitive: a forged `Accept` or `Undo` could detach a child from protection, so implementations SHOULD require the strongest authentication they support for those activities.

## 7. Privacy considerations

- **Guardians are public.** `shaer:guardians` is published openly, so that an outsider with a moderation concern can find the responsible adults rather than confronting the ward. Reaching an actor's guardians is therefore open not only to the guardians themselves and to authenticated parties, but to any **free** actor handling a moderation matter. The default is openness; deployments that need stricter confidentiality MAY narrow it, at the cost of that reachability.
- Escalation payloads concern minors and MUST be minimised: deliver enough for a guardian to act, not a full surveillance feed.
- Out-of-band channels (e-mail/SMS) carry the same data off the Fediverse; implementations MUST treat guardian contact details as sensitive personal data (GDPR / age-appropriate design).

## 8. Scope (what this FEP does NOT do)

- It does **not** verify age, identity, or minority. It provides the guardianship mechanism; who is a ward is a deployment decision.
- It does **not** define the moderation policy, the follow-approval quorum, or the out-of-band channel details beyond "at least one, where configured."
- It does **not** create a trust hierarchy deeper than one level (§4).
- It does **not** adopt portable or DID-bound actor identity (e.g. FEP-ef61). This is deliberate: a guardianship protects an account on a server, not a lifelong identity, and pinning it to a durable cryptographic anchor would outlive the relationship it describes.

## 9. Examples

### 9.1 A ward actor

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams",
               "https://ns.klonkt.com/shaer"],
  "type": "Person",
  "id": "https://kids.example/users/robin",
  "manuallyApprovesFollowers": true,
  "shaer:guardians": ["https://kids.example/users/parent"]
}
```

### 9.2 A guardian actor

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams",
               "https://ns.klonkt.com/shaer"],
  "type": "Person",
  "id": "https://kids.example/users/parent",
  "shaer:isGuardian": true
}
```

### 9.3 Offering guardianship

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams",
               "https://ns.klonkt.com/shaer"],
  "type": "Offer",
  "actor": "https://kids.example/users/parent",
  "to": ["https://kids.example/users/robin"],
  "object": {
    "type": "Relationship",
    "subject": "https://kids.example/users/robin",
    "relationship": "shaer:Guardian",
    "object": "https://kids.example/users/parent"
  }
}
```

### 9.4 A note that hints at guarded authorship

```json
{
  "@context": ["https://www.w3.org/ns/activitystreams",
               "https://ns.klonkt.com/shaer"],
  "type": "Note",
  "attributedTo": "https://kids.example/users/robin",
  "content": "hi fediverse!",
  "shaer:hasGuardians": true
}
```

## 10. Open questions (need author decisions before FINAL)

- **(A) Resolved.** `shaer:guardians` is a public property (village model); no separate `shaer:guarded` boolean. See §2.1, §2.2.
- **(B) Resolved.** Fixed initiator: the aspirant guardian makes the `Offer`. See §3.1.
- **(C) Resolved.** Follow-approval quorum stays policy (all, any-one, or optionally none) for the guardians to relax as the ward matures. See §5.3.
- **(D) Resolved.** Existing FEPs are cross-referenced: reply control via the deployed Mastodon terms (§5.4; originally [FEP-5624], now WITHDRAWN, with the live discussion in [FEP-171b] / [FEP-7458] / [FEP-11dd]), search consent [FEP-5feb] and [FEP-5e53] (§5.5), object integrity [FEP-8b32] and actor keys [FEP-521a] (§6), plus `Flag` (§5) and the context FEPs ([FEP-7888], [FEP-171b], [FEP-7458]) as related work. The full mapping and rationale are maintained separately from this proposal.
- **(E) Resolved.** The bundled emancipation flow is a single decision (§3.5) in which the two witnesses hold a temporary, non-guardian role (§3.4, Method 2). Naming them is part of opening the flow and needs no guardian approval, so holdouts cannot deadlock it; their majority is needed only for the removal itself.
- **(F) Resolved.** Hard floor of three for emancipation (§3.4): a ward with fewer than three guardians must add guardians before it can release them all.
- **(H) Resolved.** Gated settings (§5.6) travel as an `Offer` of a `shaer:GatedSetting` to the ward's server, answered with `Accept`/`Reject` by the other guardians and tallied there as a §3.5 decision. Co-located guardians are the special case of that, not the other way round.
- **(I) Resolved by leaving it unresolved.** A contested lapse (§3.6.3) is not arbitrated by this FEP. A protocol can record consensus; it cannot manufacture one, and threshold arithmetic applied to a family conflict does not settle it. The ward is not made the tiebreaker either. The guarantee is procedural rather than substantive: notice over the handle, the full window, cancellation by a single answer, and the resulting record. Contested removals are resolved outside the protocol; the protocol supplies evidence to that process.
- **(G) Resolved.** Decisions settle by threshold within a window (§3.5), not by waiting for everyone. Reversible decisions (follows, replies) settle early, in a race to the threshold, and fail closed at the deadline; irreversible ones (emancipation) always run the full window. Default follow window: 24 hours (§5.3). Default emancipation window: 30 days (§3.4, Method 3).

## Acknowledgements

The guardianship model in this document, including the emancipation design in §3.4 (the two-witness deadlock-breaker and the legacy/erasure treatment of prior objects), originates with Bart Overkamp and was developed through 'discussion' on SocialHub and in other places On- and Off-line. This draft renders that design into FEP form.

The prose of this document is largely written by Claude (Fable and Opus 5/4.8), working from the [forum post][discussion] and from FEP-67ff, which this repository was queried for. The initial draft was produced after discussion; the FEP repository was then cloned and a synced copy set up, and the document has been revised in the same way since.

The division of labour is worth stating plainly. Close to all of the text is model-written. None of the design is: the guardianship model, the emancipation flow, the decision mechanic, and the deliberate refusals to decide (§10) come from the authors and from operating a guarded instance. So does every correction of substance — the placement of the §4 check, the disclosure that a commit-time refusal carries, and the undefined behaviour of a failed dereference were all caught by the authors, several of them by implementing the text and finding it wanting.

The decision model of §3.5 came out of the same discussion: a threshold reached within a window rather than a poll everyone must answer, and the distinction between reversible decisions that settle early and irreversible ones that always run their full window. Bart Overkamp put it as "a race to the threshold rather than a vote".

## References

- [RFC2119] S. Bradner, Key words for use in RFCs to Indicate Requirement Levels, 1997
- [ActivityPub] C. Lemmer-Webber, J. Tallon, ActivityPub, W3C, 2018
- [ActivityStreams2] J. Snell, E. Prodromou, Activity Streams 2.0, W3C, 2017
- Informative: [FEP-4ccd] Pending Followers Collection (verified in index, DRAFT): complements §5.3 follow-gating; [FEP-8b32] Object Integrity Proofs (DRAFT) and [FEP-521a] Representing actor's public keys (FINAL): recommended signing for §3/§6 activities
- [FEP-e232] Object Links (FINAL)
- [FEP-5624] Per-object reply control policies (WITHDRAWN 2025-06-24; informative predecessor, its `canReply`/`ApproveReply`/`RejectReply` terms remain deployed in the Mastodon namespace)
- [FEP-5feb] Search indexing consent for actors
- [FEP-5e53] Opt-out Preference Signals
- [FEP-8b32] Object Integrity Proofs
- [FEP-521a] Representing actor public keys (Multikey)
- [FEP-7888] Demystifying the context property; [FEP-171b] Conversation Containers; [FEP-7458] Using the replies collection; [FEP-11dd] Context Ownership and Inheritance (all DRAFT): the live successor discussion to the withdrawn [FEP-5624] on who owns a thread and who may reply

## Copyright

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.

[RFC2119]: https://tools.ietf.org/html/rfc2119.html
[ActivityPub]: https://www.w3.org/TR/activitypub/
[ActivityStreams2]: https://www.w3.org/TR/activitystreams-core/
[discussion]: https://socialhub.activitypub.rocks/t/fep-633c-guardians/8816
[FEP-4ccd]: https://codeberg.org/fediverse/fep/src/branch/main/fep/4ccd/fep-4ccd.md
[FEP-11dd]: https://codeberg.org/fediverse/fep/src/branch/main/fep/11dd/fep-11dd.md
[FEP-171b]: https://codeberg.org/fediverse/fep/src/branch/main/fep/171b/fep-171b.md
[FEP-521a]: https://codeberg.org/fediverse/fep/src/branch/main/fep/521a/fep-521a.md
[FEP-5624]: https://codeberg.org/fediverse/fep/src/branch/main/fep/5624/fep-5624.md
[FEP-5e53]: https://codeberg.org/fediverse/fep/src/branch/main/fep/5e53/fep-5e53.md
[FEP-5feb]: https://codeberg.org/fediverse/fep/src/branch/main/fep/5feb/fep-5feb.md
[FEP-7458]: https://codeberg.org/fediverse/fep/src/branch/main/fep/7458/fep-7458.md
[FEP-7888]: https://codeberg.org/fediverse/fep/src/branch/main/fep/7888/fep-7888.md
[FEP-8b32]: https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md
[FEP-e232]: https://codeberg.org/fediverse/fep/src/branch/main/fep/e232/fep-e232.md
