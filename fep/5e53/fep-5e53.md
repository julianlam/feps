---
slug: "5e53"
authors: Don Marti <dmarti@zgp.org>
status: DRAFT
dateReceived: 2024-06-09
trackingIssue: https://codeberg.org/fediverse/fep/issues/327
discussionsTo: https://socialhub.activitypub.rocks/t/fep-5e53-opt-out-preference-signals/4323
---
# FEP-5e53: Opt-out Preference Signals


## Summary

Some users have concerns about how their content and/or personal information are
used. For example, some users do not want the content they created
to be used for training generative AI systems, and some users do
not want to have their personal information shared or sold.

Several opt-out preference signals (OOPSs) have been
standardized or proposed in the form of HTTP headers that can apply to a
connection between a user and a central server.
In some jurisdictions, companies that administer web sites are required to
process and act on OOPSs. 

This FEP extends [ActivityPub] to support passing OOPSs along with
the content and user information to which they may apply. This FEP
refers to existing OOPSs that have already been documented, and does not propose new ones.


## Declaring an OOPS

In order to apply an OOPS to an object, an author MAY set the JSON-LD properties `xRobotsTag` and/or
`secGPC`.  For example,


```
{
  "@context": ["https://www.w3.org/ns/activitystreams", "https://fep.example/ns/privacyHeaders"],
  "type": "Note",
  "content": "Don't surveil me bro",
  "xRobotsTag": "noai",
  "secGPC": 1
}
```

A recipient SHOULD process the content and metadata of the object as if the recipient had received it
over an HTTP connection with the corresponding header.

 * `secGPC`: process as if the object has been received with the `Sec-GPC` HTTP request header.

 * `xRobotsTag`: process as if the object had been received with an `X-Robots-Tag` HTTP response header
    with a value equal to this property.


## Deployment considerations

The [GPC] standard allows for individuals in an increasing number of
jurisdictions to pass a legally binding signal indicating a commonly
held privacy norm.  However, GPC as an HTTP header only works from
client to server, so can only function in centralized systems. A
federated system where a user's information may be passed from
one server to another is currently at a disadvantage in serving
GPC users, because the GPC does not travel with the information
to which it applies.  Adding GPC to ActivityPub would bring parity
with centralized social sites.

Content sharing platforms that operate in a centralized manner
are now frequently promoting their support for signaling opt-outs
to <q>generative AI</q> training, using the [noai] value for the X-Robots-Tag header. See [RobotsMeta] and [RobotExclusion].
In order for federated content sharing systems to provide an
attractive alternative to centralized ones, federated systems will
likely need to also offer an opt out signaling feature.


## Security considerations

This proposal depends on compliant processing of the OOPSs by all actors.


## Implementations

None so far.



## Related proposal

[FEP-c118](https://codeberg.org/fediverse/fep/src/branch/main/fep/c118/fep-c118.md) suggests establishing
a content licensing framework. This may be possible by adapting this FEP to include the license header
from [WebLinking].


## References

- Christine Lemmer Webber, Jessica Tallon, [ActivityPub][ActivityPub], 2018
- DeviantArt team, [UPDATE All Deviations Are Opted Out of AI Datasets][noai], 2022
- Google Search Central, [Robots meta tag, data-nosnippet, and X-Robots-Tag specifications][RobotsMeta], undated
- M. Nottingham, [Web Linking][WebLinking], 2010
- Martijn Koster, [A Standard for Robot Exclusion][RobotExclusion], 1994
- Sebastian Zimmeck, Peter Snyder, Justin Brookman, Aram Zucker-Scharff, [Global Privacy Control][GPC], 2024


[ActivityPub]: https://www.w3.org/TR/activitypub/
[GPC]: https://privacycg.github.io/gpc-spec/
[noai]: https://www.deviantart.com/team/journal/UPDATE-All-Deviations-Are-Opted-Out-of-AI-Datasets-934500371
[RobotExclusion]: http://www.robotstxt.org/robotstxt.html
[RobotsMeta]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
[WebLinking]: https://datatracker.ietf.org/doc/html/rfc5988

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
