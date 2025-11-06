---
slug: "d8c8"
authors: Jonny Saunders <j@nny.fyi>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-d8c8-bittorrent-torrent-objects/8309
dateReceived: 2025-11-03
trackingIssue: https://codeberg.org/fediverse/fep/issues/722
---

# FEP-d8c8: BitTorrent `Torrent` Objects

## Summary

The BitTorrent protocol is a p2p protocol for distributing data described as a series of hashes and file metadata contained in `.torrent` files. This FEP describes a JSON-LD representation of `.torrent` files as an extension of an ActivityStreams `Object`.

## Background

A torrent file[^torrentterminology] is an abbreviated, verifiable description of a file or directory that, at minimum, contains 

- A series of "piece hashes" that summarize pieces of the data (see [BEP 0003](https://www.bittorrent.org/beps/bep_0003.html), [BEP 0052](https://www.bittorrent.org/beps/bep_0052.html))
- A description of how the data is laid out in files and directories
- Metadata like the `piece length` that allow downloaded data to be validated against the hashes

A torrent consists of one outer "metainfo" dictionary, and an inner "info" dictionary (or, informally an "infodict"). A SHA1 (in the case of v1 torrents) or SHA256 (for v2 torrents) digest of the bencoded infodict serves as the content address for the data summarized by the torrent, or the "infohash".

Torrents are an *open world* specification: the specification sets the minimum required keys and their use, but any additional keys are allowed, ignored if the consuming client doesn't understand them. Torrents are encoded in a bittorrent-specific ASCII-based encoding, "[`bencoding`](https://en.wikipedia.org/wiki/Bencode)," whose strings, integers, lists, and dictionaries can be represented as a subset of JSON. Together, this means that with minimal adaptation, torrents can be represented as JSON-LD, with protocol extensions annotated with vocabularies imported by the `@context`.

## Spec

MUST, MAY, and SHOULD used in the [RFC-2119](https://tools.ietf.org/html/rfc2119.html) sense where they appear in CAPITAL LETTERS.

[CURIE](https://www.w3.org/TR/2010/NOTE-curie-20101216/) prefixes used in this document:
- `bt`: `https://w3id.org/fep/d8c8#` - the namespace created by this FEP (see [FEP-888d](https://codeberg.org/fediverse/fep/src/branch/main/fep/888d/fep-888d.md)), referring to the attached JSON-LD context [`fep-d8c8.jsonld`](./fep-d8c8.jsonld)
- `as`: `https://www.w3.org/ns/activitystreams` - the ActivityStreams vocabulary

A `Torrent` object is an extension of an ActivityStreams `Object` whose `"type"` is `"Torrent"` and whose `uri` is `bt:Torrent` (or, expanded, `https://w3id.org/fep/d8c8#Torrent`).

The contents of a `Torrent` object are, at minimum, those specified by [BEP 0003](https://www.bittorrent.org/beps/bep_0003.html) (bittorrent v1) or [BEP 0052](https://www.bittorrent.org/beps/bep_0052.html) (bittorrent v2)[^v1v2].

### JSON Encoding

`Torrent` objects MUST be JSON encoded, mapping bencoded strings, integers, lists, and dictionaries to their counterparts in JSON. 

- Strings that are not explicitly intended to be interpreted as binary data SHOULD be encoded as utf-8. 
- Strings that are to be interpreted as binary data SHOULD be encoded as [RFC 4648](https://datatracker.ietf.org/doc/html/rfc4648#section-4) base64, EXCEPT
- Strings that always represent *individual* hashes SHOULD be encoded as hexadecimal strings.
- The encoding used for the value of `pieces root` in v2 `file tree`s MUST be the same as the encoding used for keys in the `piece layers` dict.

Examples of strings that should be encoded as base64:
- the value of the `pieces` string in the v1 info dict, even when there is only one piece hash.
- the value of of the piece hashes within a v2 `piece layers` dictionary, even when there is only one piece hash.

Examples of strings that should be encoded as hexadecimal:
- v1 and v2 infohashes (below)
- keys in the v2 `piece layers` dict, and values of `pieces root` within `file tree`

### Bencoding

Additional terms may be added to the metainfo and info dictionaries, and when returning to the `bencoded` form these terms MUST be kept in their unexpanded form (i.e. not expanded to full URIs if they are terms from the JSON-LD Context) EXCEPT for the terms specified in this FEP, which MUST be removed from the `bencoded` form.

When bencoding a `Torrent` object, the inverse encoding to that described above MUST be applied to strings: hexadecimal, base64, and unicode strings MUST all be decoded to binary.

### Additional Keys

`Torrent` objects MUST contain their infohashes using the following keys, depending on whether they are v1, v2, or hybrid torrents:

- `bt:infohash_v1`: v1-only and hybrid torrents MUST have a hexadecimal SHA1 hash of the bencoded `info` dict
- `bt:infohash_v2`: v2-only and hybrid torrents MUST have a hexadecimal SHA256 hash of the bencoded `info` dict

Software that consumes `Torrent` objects SHOULD verify that the infohashes provided in the `Torrent` object match those computed by the bencoded form of the `Torrent`'s `info` dict, and MAY choose to not process `Torrent` objects with incorrect infohashes.

`Torrent` objects MAY contain the following keys:

- `bt:bencoded`: a URI to the bencoded form of the torrent.
- `bt:magnet`: A [magnet URI](https://en.wikipedia.org/wiki/Magnet_URI_scheme) that MUST contain the same information as the `Torrent` object, subset to the fields that have corresponding keys in the magnet URI scheme.

### Abbreviated Representation

In Collections or other circumstances where presenting the full, materialized `Torrent` object might be expensive, implementing software MAY present the object in an abbreviated form consisting of 

Required:
- the object's `id` uri
- its infohash(es): `bt:infohash_v1`, `bt:infohash_v2`, if applicable.

Optional:
- `bt:bencoded`: a URI to the bencoded form of the torrent. The linked bencoded torrent MUST be equivalent to a bencoded version of the JSON `Torrent` object (see [Bencoding](#Bencoding), above)
- `bt:magnet`: a [magnet URI](https://en.wikipedia.org/wiki/Magnet_URI_scheme) for the torrent.

In circumstances where other ActivityStreams Objects might be presented as a bare URI, `Torrent` objects SHOULD be presented as this abbreviated form, allowing the possibility of using the infohash to dereference the torrent contents via DHT or other means.

## Examples

### Torrent Objects

For some example torrent with arbitrary contents, we might expect the JSON `Torrent` to look like this (assuming the `@context` is supplied in some outer scope):

#### v1

<details>
<summary>Expand/collapse v1 Example</summary>

```json
{
  "announce": "udp://tracker.example.com:6969",
  "announce-list": [
    [
      "https://example.com/announce.php"
    ]
  ],
  "created by": "Example Torrent Creator",
  "creation date": 1724037213,
  "id": "https://example.com/torrents/torrent123",
  "info": {
    "files": [
      {
        "length": 5261174,
        "path": [
          "tentacoli-15-Tentacles (Versione 2).mp3"
        ]
      },
      {
        "length": 2778997,
        "path": [
          "tentacoli-02-She'll Never Come Back.mp3"
        ]
      },
      {
        "length": 2333412,
        "path": [
          "tentacoli-03-My Son's Friend Is A Champion Pisser.mp3"
        ]
      },
      {
        "length": 2562622,
        "path": [
          "tentacoli-04-Summer And Winter.mp3"
        ]
      },
      {
        "length": 2796486,
        "path": [
          "tentacoli-05-San Diego, Yellow Cab.mp3"
        ]
      },
      {
        "length": 3863849,
        "path": [
          "tentacoli-06-Happiness Is Having Two Killer Whales As Friends.mp3"
        ]
      },
      {
        "length": 3696387,
        "path": [
          "tentacoli-07-Too Risky A Day For A Regatta.mp3"
        ]
      },
      {
        "length": 2583746,
        "path": [
          "tentacoli-08-Sorry, I Have To Go.mp3"
        ]
      },
      {
        "length": 1924024,
        "path": [
          "tentacoli-09-Scotch For Two.mp3"
        ]
      },
      {
        "length": 2463949,
        "path": [
          "tentacoli-10-The Killer Whales' Games.mp3"
        ]
      },
      {
        "length": 1783901,
        "path": [
          "tentacoli-11-The Capture Of The Giant Octopus.mp3"
        ]
      },
      {
        "length": 2965602,
        "path": [
          "tentacoli-12-Two Old Kids.mp3"
        ]
      },
      {
        "length": 4319196,
        "path": [
          "tentacoli-13-Tentacles.mp3"
        ]
      },
      {
        "length": 1555839,
        "path": [
          "tentacoli-14-My Son's Friend Is A Champion Pisser (Versione 2).mp3"
        ]
      },
      {
        "length": 3177585,
        "path": [
          "tentacoli-01-Small Town Pleasures.mp3"
        ]
      },
      {
        "length": 2877921,
        "path": [
          "tentacoli-16-San Diego, Yellow Cab (Versione 2).mp3"
        ]
      },
      {
        "length": 1079679,
        "path": [
          "tentacoli-17-My Son's Friend Is A Champion Pisser (Versione 3).mp3"
        ]
      },
      {
        "length": 874993,
        "path": [
          "tentacoli-18-Too Risky A Day For A Regatta (Versione 2).mp3"
        ]
      },
      {
        "length": 3951350,
        "path": [
          "tentacoli-19-Tentacles (Versione 3).mp3"
        ]
      },
      {
        "length": 4358356,
        "path": [
          "tentacoli-20-Sails.mp3"
        ]
      },
      {
        "length": 2870766,
        "path": [
          "tentacoli-21-Sails (Versione 2).mp3"
        ]
      }
    ],
    "name": "tentacles-tentacoli-1977-ost-soundtrack",
    "piece length": 131072,
    "pieces": "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"
  },
  "infohash_v1": "1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083",
  "type": "Torrent"
}
```

</details>

#### v2

<details>
<summary>Expand/collapse v2 example</summary>

```json
{
  "announce": "udp://tracker.example.com:6969",
  "announce-list": [
    [
      "https://example.com/announce.php"
    ]
  ],
  "created by": "Example Torrent Creator",
  "id": "https://example.com/torrents/torrent123",
  "info": {
    "file tree": {
      "tentacoli-01-Small Town Pleasures.mp3": {
        "": {
          "length": 3177585,
          "pieces root": "e755700c5bcea4905a1a3f900351d8a5564098bc081e6754e379f805728d190a"
        }
      },
      "tentacoli-02-She'll Never Come Back.mp3": {
        "": {
          "length": 2778997,
          "pieces root": "d1c3d80bf13fd42b3e8582a15a21172d23b80247f3b6ca85ffa97f018db4dfcb"
        }
      },
      "tentacoli-03-My Son's Friend Is A Champion Pisser.mp3": {
        "": {
          "length": 2333412,
          "pieces root": "3b458ec67b680d056b9f48d2920242bd812249cebd1939880340e7d2e136fe0f"
        }
      },
      "tentacoli-04-Summer And Winter.mp3": {
        "": {
          "length": 2562622,
          "pieces root": "3ff20c6f038c048f27e428499498e1d19488f8f934df6632d5d4d827ccf3f3f2"
        }
      },
      "tentacoli-05-San Diego, Yellow Cab.mp3": {
        "": {
          "length": 2796486,
          "pieces root": "7ad85e1400e68597e006040d4d9373d2a05d9b2ae13f14dd9939317d33ea2c8b"
        }
      },
      "tentacoli-06-Happiness Is Having Two Killer Whales As Friends.mp3": {
        "": {
          "length": 3863849,
          "pieces root": "d0063c2d1f1c5e3b5e163383d5f5a63ac983be59708e0d695870442cebbe37d9"
        }
      },
      "tentacoli-07-Too Risky A Day For A Regatta.mp3": {
        "": {
          "length": 3696387,
          "pieces root": "4767dc7f1b8d2f6aaae276034cb2e2c6c656af56683e148f0e54c15382273245"
        }
      },
      "tentacoli-08-Sorry, I Have To Go.mp3": {
        "": {
          "length": 2583746,
          "pieces root": "661b7dc0bb901d026370be0b73e87fb6a95479dc85bcdefe61711d8fc5b236f3"
        }
      },
      "tentacoli-09-Scotch For Two.mp3": {
        "": {
          "length": 1924024,
          "pieces root": "6bdfbd145a64cabfc9b0971f87ae69c93bd1847b0c48351ed971c1fa4e9db97f"
        }
      },
      "tentacoli-10-The Killer Whales' Games.mp3": {
        "": {
          "length": 2463949,
          "pieces root": "e5273e3a62dee1a16328471a471f3a361eee0de07de68a11b6695c8483a4eb88"
        }
      },
      "tentacoli-11-The Capture Of The Giant Octopus.mp3": {
        "": {
          "length": 1783901,
          "pieces root": "91b3f6f33d7c2cc4752c3b6e79bafe7ec2d3e03c31ae3790a5c132d1a9b93f84"
        }
      },
      "tentacoli-12-Two Old Kids.mp3": {
        "": {
          "length": 2965602,
          "pieces root": "0b09f31a4206b8c42530dc7fb489ea52f4db6992b1de8c9e56dd1bf711d64af4"
        }
      },
      "tentacoli-13-Tentacles.mp3": {
        "": {
          "length": 4319196,
          "pieces root": "26c6744b0b3245ed23691732c22f95a9bf074f32a49ba5c9feece809347e889e"
        }
      },
      "tentacoli-14-My Son's Friend Is A Champion Pisser (Versione 2).mp3": {
        "": {
          "length": 1555839,
          "pieces root": "736490ac9a57251d5feb02bb8e17d0f29e761993bd604ebece2f66e8cfc24a76"
        }
      },
      "tentacoli-15-Tentacles (Versione 2).mp3": {
        "": {
          "length": 5261174,
          "pieces root": "4c94d4d2d20631afa6fa4d4287af4cf5c262c00f834c027c9df3f711adedb2db"
        }
      },
      "tentacoli-16-San Diego, Yellow Cab (Versione 2).mp3": {
        "": {
          "length": 2877921,
          "pieces root": "b9f50e8baac6b38dc2f84e93387b8c5e21c334f54f8772cd5dc819e88c671c6b"
        }
      },
      "tentacoli-17-My Son's Friend Is A Champion Pisser (Versione 3).mp3": {
        "": {
          "length": 1079679,
          "pieces root": "a2781d81c2dc33dac179bce14390485e47f2129ba98ed4efbd4690daf7229d95"
        }
      },
      "tentacoli-18-Too Risky A Day For A Regatta (Versione 2).mp3": {
        "": {
          "length": 874993,
          "pieces root": "c67de66bc0c2c41fce411d351d82dff8afe809e5206df6b14d536d4ff4c00dbe"
        }
      },
      "tentacoli-19-Tentacles (Versione 3).mp3": {
        "": {
          "length": 3951350,
          "pieces root": "b6145263d70c69c630d59dfa07856663b33e5621a62a33d7cd706c3aafdfe2ed"
        }
      },
      "tentacoli-20-Sails.mp3": {
        "": {
          "length": 4358356,
          "pieces root": "72436d6a0686a9a83d782445224036c71dde61e1824ef5ea230462ad95daa11d"
        }
      },
      "tentacoli-21-Sails (Versione 2).mp3": {
        "": {
          "length": 2870766,
          "pieces root": "b27df2732173f94fb73fece8d7ca2864d2c027d5186f078d30c01e4310d700e0"
        }
      }
    },
    "meta version": 2,
    "name": "tentacles-tentacoli-1977-ost-soundtrack",
    "piece length": 524288,
    "similar": []
  },
  "piece layers": {
    "0b09f31a4206b8c42530dc7fb489ea52f4db6992b1de8c9e56dd1bf711d64af4": "VPZdDK988MyI5L2JUEvc3RNizYDkWZBhaxZGOqqjJO6N5c5QVL/+NUNQvc6AyZtNFfD2A/APiNK/AVNMjhT2WjgTQeqMBtmnoLKBs3+F+e94T7NQk5uygqd89lOk+eFSW3zIxeoCgjnxq3QlX3i8ABOK3RDVvzFPnegQvpgYoBH+3TlsWxinQ+JtwGFyTMAFwe52fIRscF5UgcqdlgRyrJu6EzKob+25Ngq/Slv0Y/Ij1mSHLRcx6BRy960JjT8J",
    "26c6744b0b3245ed23691732c22f95a9bf074f32a49ba5c9feece809347e889e": "nIooZfqJg9f3Wa+Kko4aSSlqdLkymMqh+qvpz640fLgJHa+hFhvvQkGCETr/xzUT2YIBwtWr+/8jGUCpE7dWHoSL8ihQXdoNoOXHYcwy/fPygSMJl+r5IgatqWJOAKSX8zyncD6096iCsazYOgp1ya2CkdxNJPpCAyXVXCl7AoPV/ULP7gKn0G3WcqAE+eXPEmLkdzEBI7KWNXsFfhyl5uPDY0RgzfirDwOeC7e34jPxBqxHcfsLQJ1ORDpnhOO1F/Hh3L4hFfiiFifXwqu/tjs7yOUkmKwhpzvr6O5wvA26p/Igw5ztlqj6wlVGVN/ay5anFZB6wmLCmGNt3M7+W5afOyAk1tvRUpNoOMTAabxT0YMPUDiuP6bJHZPsOnG4",
    "3b458ec67b680d056b9f48d2920242bd812249cebd1939880340e7d2e136fe0f": "hmopzDsPaqQY8kB0fSAE9korQ/EYlhMNNKYh+Stip0nQeIednxVIigWz7SdHjEAxtrISO8Q7oPicQBePe6P5yH70mQLp20KAj82QuAtpEUXP582Ix5A/QTAlv/ZOCCV9bUeY63aSacDLrVzjyx0cu3O0I18d5lMa7GL8TszAeziVxSJDStgC/mSgsEw2lyjyzchw2XHI39o7x+1GlXHhZA==",
    "3ff20c6f038c048f27e428499498e1d19488f8f934df6632d5d4d827ccf3f3f2": "V8LPZiW6dYEhkVpy50NA8NQobcjCG7BiwqPR0TzNXe+rfk+pF/p7QCzF+tpKReBi5EPurqWGjO4+dbJ73YOO53yCOoLILCo9iji8YyvkB6RQ9nM4Xn71hPiU1+oJwAQb3cgM6dxz5+ida8bDGLpB7CroBXzQniNAbNUungzhJy2T6O5BwEHBoLJmpTrkcLurMqLmHRmGJN2SMqfcMDhg3g==",
    "4767dc7f1b8d2f6aaae276034cb2e2c6c656af56683e148f0e54c15382273245": "gAhlHM85lyfo/VNx1txeTrZogY4hwv1y2GQ9PrXIA6zqco3cpn6IIttXkb6GgIkz4PiVmEmC4vlKt/rV+mCr6/hj9o7tmCjolGiDw471NFblaxYcYKu+XfM/coV8GJGtAV+bWjotIAccxZUq+JpcMfVD33C9H0PKjX14NLJwAG02ZRMcu5gU1FEjypDUXi/uGmeb9LquiwDv7c9ZJ+tTqH7/K+w8w45GI3gt8B+ZRa4pPUlDAsS9o3efdLbpwNrwvbIgc/PNpmSwoSkDHtik6bclpq+IKm0oB0eK12ic6/NdOTH7eMZ0+FZ5rtn9ThJ028cHkSAeqHs8v1e+UOjx4w==",
    "4c94d4d2d20631afa6fa4d4287af4cf5c262c00f834c027c9df3f711adedb2db": "AFW7D3V3l7kOP+FoujXugKWb4HH2pXMOc53bQaUj5m3r7xXsXQSTox1chHUlK8ps+O1qxckSydl7e9pPXWN+j84nVqScDN6uF+LJp58SxqOmi/g7nBBJugwxPaf5HrEOAXynbi+CnHFBQPYnZ7/AlSFhpII4j9/Nnv9WT079YgFCc162lViJR860+Rbf3OaATtVAI5oGFJUAVCV636zAsTXoTMj0lnJne+Hb/KgxlROiWKLBDAL1jQ/0Cz3n3D/Vyw4eAQ0AaP0REXemD/wBFDyDE+5ixFS9+cI1uam4bTqGN4UPily/WRC49VpyAwyT6rpMFjTXc7xGTkMEZpNIgbENH8rZxBWFDoNSzJVRL/XjdOZaDFKe5ALRxeQAzbYh7tKeqdi4OXE0p4jzBd8pC+hNM3yDu8LgHDE1qjOM4egkt9gBtsmnSi2Urif1/Q8maaiy3sEHoph4VdA9D8N8nw==",
    "661b7dc0bb901d026370be0b73e87fb6a95479dc85bcdefe61711d8fc5b236f3": "aZRzmN/dmNjg+FsfKWMZl0l2siifCKnrMYFM2PA5lOOB8DclDu0sXUM55se9HRMVjOcnfNXxY3+mRIrtTdaT8sDbpzHXp9iGqsYZBGEAj07ZaeJM3jHvOky1o4x2Qro5JHtefe2GFDgq2lJS0ha+JUsWG9a6MdH3c3faaj/X4IVoJCDtF/V8WpvVY8eMmVoEA5L9Zfpc9eiTlCJNP7HwIw==",
    "6bdfbd145a64cabfc9b0971f87ae69c93bd1847b0c48351ed971c1fa4e9db97f": "sysPGOfDZ8wAr39CdfFK3MzWxiPexd7SkLqWvIySoYD/Gr+n3xJTMyxIZR5LwAjaQwAlCqRpgDx14e0kyWWKQBUPlj3EgcMR2/1vCW6mBHFTqfO2Y/IECE/iSUaFJ3i+zWEQcAklqVfqBloKbLGtfHMAVIRgwY8yoAKB23+gmFk=",
    "72436d6a0686a9a83d782445224036c71dde61e1824ef5ea230462ad95daa11d": "QiFoWXevBNl/jPCnBtGEtE4VfW9k31yMrX8MrTtJs+2DpNXJXQIWYPGaXA5S1iOnhQ1wBXlKt+m7M6TChTE/5/q2qPpe4hp5iVl28bkvb2pYgVZSgYiqGqistUewLisrhTygHutf8Rm2ChDp4cfJAJ0hRc2hHQpMo9syRwpVUYI2HpVjsS6t6Ymokojaxfdxk+88mJ1bJZcNNoFmK5EaqsQVRvjTenxaklYKPZROeDeiUb64FGCTvv8hF0T1/cNFCOV3kdUjgM4mrnw+gDfJIm5JdID5bsC4DVF7WrOWaAH251lWksPzDyIFcSxV0C7l+FihtXM4U/BhsxlnnfWEVfWZBP7tFb4vMU3WsMRCCbbXCsKpuNa/NYCwro+h1MO/",
    "736490ac9a57251d5feb02bb8e17d0f29e761993bd604ebece2f66e8cfc24a76": "VwRUXEzJHC3pz7uEnEowpwFHA/6Q4WYdUmMEoA1Fvog09IALuR6E3bAuo6FP9pTrn2bvxPvJSKHVhGyWwbGaJn5arMAK4ChGGuZyoAQwOOdQPwx/A90v92qo5SuqhxFF",
    "7ad85e1400e68597e006040d4d9373d2a05d9b2ae13f14dd9939317d33ea2c8b": "SCiEVcZOjE1GM0aMNWiBTiS7LMV2iIAVX4puj77Dhz+dsqG/hthLs+d6GD3oB29I0wCBYIPUCSDJmcj0ppAvABDDhc0H1bIpQzhqHQmwtK80T122VAQ2MPKCU9vg+k8wkJSzgWKib8AQJEpdpBpEiyO9DPCzSfzLtqPucgTUNvlatKYAh5c8+o0Nf1ewEkZumL58vocsENGianJDe+kSzUJMwJKxT6BvFlE9ujsZ7fSWDV95sVxqOQMFCVwxuNOD",
    "91b3f6f33d7c2cc4752c3b6e79bafe7ec2d3e03c31ae3790a5c132d1a9b93f84": "vj2xl+bqofTamS/TSAcwBbsf/E5jBX9C6lgZdswP+/7WNv4Vp15ny5mxi14YqCFG+M1+5NOfUzJw6RiwMLWY9R82q7yrrW4ccnBJMcvhP7f39D6BKMx4mcd/ATr0aEV5KbzkuW6io+4uahSt53fk53UMkGAwS1kGivE17ueD1ng=",
    "a2781d81c2dc33dac179bce14390485e47f2129ba98ed4efbd4690daf7229d95": "TpFZZj49ysDTd5yoplRz0DfoipqsWnG4ZNeNbZA+8M9rTS1ItmqZnol7sDqbMXZ+qrsXiYEr2pWCeaks/cqPI+1ae1ecX8rtsWyA3ej5aGRNt9zUmpYhDazGrqfok2v2",
    "b27df2732173f94fb73fece8d7ca2864d2c027d5186f078d30c01e4310d700e0": "jnrUt1kqrGZ1gPKtCYyDocTIoOxB0RtsWA3xEocJiyxaUaWv8jWumQAjW6ZMboJ10JODGebBV7HQssjlElEVdmR6HnePf6Ov+Fu/ZfplQHILfLi63PQYO3Dc8ohdwEz3o+FgJ+JOhQwbynrSItQOT+azQLJ8o41yWOGY72SUdhtNEjhytqWwGQIHFKMJfQeVlvLpVCryU6p84sgxIiYRJ8cUZbHPhz4Y0m3xPbR1tJMaIlqcfjOw0I9sHYCA4suZ",
    "b6145263d70c69c630d59dfa07856663b33e5621a62a33d7cd706c3aafdfe2ed": "GQLFRpTn3AVBJS/ojGtr9lhfSI/8ewYR0xLlkqg3Cnqx2AVlwr9RwBjKMajHSgcmVvpQpoZ0AejThvZz2JygF5kkjVy1Pe7zJ65GfmIMU0CCKkiAyCWuQt1PdDTd2xWNReKv7MH7rVRse7H6YrIAZSdEnziGr6eUVt9+fxULQm62g4rihawxEW6dZvMh8QL9D+PUFVjrgRBUKvYWqRXgRY0vObRxqCQj1AJDSwvUdMv33b7o95rNOsVEdBu+n+Lt3JA7CxwAXsQrgZt9AmGXQTvyu+uONt+2ihaqtspuGAkBf6/D8RN/sybcWtWCI0lgSyqu2g8cYBEMaxnjgKGSaw==",
    "b9f50e8baac6b38dc2f84e93387b8c5e21c334f54f8772cd5dc819e88c671c6b": "snFE/oMWtUu01QzaJnhsMG+D5D97pbKW287lAAMvMSwp0FK1aOBcV19dvQte9qvXmws494090AGQ3xxAOntIFQjzJlYhbp8JQC+2r32oFf7lyaowwreV535RdH6/TNcd39O9UI0dAndQ9uDWP9mRpBFfLksTvYFktKnlwqqCiYRAGbdsO5FC1qlJxi/X1CZHG9gjk1FxdhH0WLUehsdQwwxuoXxdQ12HLuowXNBr1JeAAWNcLVAqSezuUkulc/Or",
    "c67de66bc0c2c41fce411d351d82dff8afe809e5206df6b14d536d4ff4c00dbe": "GaAYwCiYeDqYOop50ZEV4TcybE87ULDDE3Nv1ZG4geIF6cRyFsjN+IAOqiXe6wjRkdReNo3NLKskpp61Ca2rBw==",
    "d0063c2d1f1c5e3b5e163383d5f5a63ac983be59708e0d695870442cebbe37d9": "fi5NJSOcrOVs57ny3dnPOhs/bIbTzJOYgLEGbq+cPwOkBPtHyY+BbAoVmFzgGyjVo+htFC81LKvLtgOMRk/TcrS8wdrRgB4NvawjS5Mk2+0LNGitxFrWZym3KhKNa4oTM6d+UE0wrGWAsOcm/fTxxGRETf4OR+gHpjz/4ED95uAboFk9h317NMudz9etX0IjX25HrBDVRH/cBJ4Kw2G0iwIVXFWQOfyBGIvQ3OUWLVd6pq7cKnYEv9V98EfpVuJquGsoDb08lJZdK72qzsxlIAXMSqhYjvEsXZD5w8wiqUeMs5XuN/DnzgDl8OdPGAUnaf8f5T0NEPvQjNMN4z+aiw==",
    "d1c3d80bf13fd42b3e8582a15a21172d23b80247f3b6ca85ffa97f018db4dfcb": "nZ0lMxZNxcUhIGdtCyi9FXVtv9WF43rLL6S5nCcQD5ufOCkq1YNu0PqtK7c6g89TZlysL0dZ/xqWIeIvsn927cVF+ugd6jvoFFcpmr33scLhCbT2PqN6A1oSYA75CgBrzlJpDzZiV5uwZzBWnlu2/menX26DPBbV67Qz2Fbn71+XwW1aBn9DR1i6MilHdyVMLpZn0C1gpgE1TG41//OZWg2N2QdACzAYK3UMoauKVDnDr4x3+cgPj8cuvjgMV3xk",
    "e5273e3a62dee1a16328471a471f3a361eee0de07de68a11b6695c8483a4eb88": "+mHCqf0cQomJkl6nWynCwp6sCWdbMlZvd78BdV3SkFJcwwolpXPAf2kZZYeUXs8X6HL3xOzFvgJLiCyS2gQ+TrG4iZThREyKwgw5eZVWv6AvxzFU5UntjCP/8R4uVWjaRNf4fupVWANkqYFZmcL0mxGk+b2y0ZH8e6kECzHCT6ZQDXvQMtUtFcg6UfuWNNmf3ha+A/M65Hs/m0q4ccp4Ww==",
    "e755700c5bcea4905a1a3f900351d8a5564098bc081e6754e379f805728d190a": "+aMdZEEaKoLp6RGQeKcp6QbjVdiqEsRghVOLxndG1+abKpoajctleyvXwAk5IszYUYyQoLt6Aj62v4256vygQ/mITuOkN3OQ6l3EaYlUwi79fu5jZvhpzgTLIXWglogaCZEft8aQ12G8m8DO6+GhLI/KqLLGGOayeB4vIq9aMjcnWIEYq5o/vrtTpVGnJFKNgAP9FbiLQka3RvJiEHWw2bMgpKspS8ai+fLNR5NqHEfzQRlxYVcK6ieySks/AcQ4m9X0olJYa0Hh6Cj4Md7pHaYvkMioFshhs+z4HFwnP0Y="
  },
  "url-list": [],
  "infohash_v2": "d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a",
  "type": "Torrent"
}
```

</details>

#### Hybrid

<details>
	<summary>Expand/collapse Hybrid example</summary>

```json
{
  "announce": "udp://tracker.example.com:6969",
  "announce-list": [
    [
      "https://example.com/announce.php"
    ]
  ],
  "created by": "Example Torrent Creator",
  "creation date": 1762216376,
  "id": "https://example.com/torrents/torrent123",
  "info": {
    "file tree": {
      "tentacoli-01-Small Town Pleasures.mp3": {
        "": {
          "length": 3177585,
          "pieces root": "e755700c5bcea4905a1a3f900351d8a5564098bc081e6754e379f805728d190a"
        }
      },
      "tentacoli-02-She'll Never Come Back.mp3": {
        "": {
          "length": 2778997,
          "pieces root": "d1c3d80bf13fd42b3e8582a15a21172d23b80247f3b6ca85ffa97f018db4dfcb"
        }
      },
      "tentacoli-03-My Son's Friend Is A Champion Pisser.mp3": {
        "": {
          "length": 2333412,
          "pieces root": "3b458ec67b680d056b9f48d2920242bd812249cebd1939880340e7d2e136fe0f"
        }
      },
      "tentacoli-04-Summer And Winter.mp3": {
        "": {
          "length": 2562622,
          "pieces root": "3ff20c6f038c048f27e428499498e1d19488f8f934df6632d5d4d827ccf3f3f2"
        }
      },
      "tentacoli-05-San Diego, Yellow Cab.mp3": {
        "": {
          "length": 2796486,
          "pieces root": "7ad85e1400e68597e006040d4d9373d2a05d9b2ae13f14dd9939317d33ea2c8b"
        }
      },
      "tentacoli-06-Happiness Is Having Two Killer Whales As Friends.mp3": {
        "": {
          "length": 3863849,
          "pieces root": "d0063c2d1f1c5e3b5e163383d5f5a63ac983be59708e0d695870442cebbe37d9"
        }
      },
      "tentacoli-07-Too Risky A Day For A Regatta.mp3": {
        "": {
          "length": 3696387,
          "pieces root": "4767dc7f1b8d2f6aaae276034cb2e2c6c656af56683e148f0e54c15382273245"
        }
      },
      "tentacoli-08-Sorry, I Have To Go.mp3": {
        "": {
          "length": 2583746,
          "pieces root": "661b7dc0bb901d026370be0b73e87fb6a95479dc85bcdefe61711d8fc5b236f3"
        }
      },
      "tentacoli-09-Scotch For Two.mp3": {
        "": {
          "length": 1924024,
          "pieces root": "6bdfbd145a64cabfc9b0971f87ae69c93bd1847b0c48351ed971c1fa4e9db97f"
        }
      },
      "tentacoli-10-The Killer Whales' Games.mp3": {
        "": {
          "length": 2463949,
          "pieces root": "e5273e3a62dee1a16328471a471f3a361eee0de07de68a11b6695c8483a4eb88"
        }
      },
      "tentacoli-11-The Capture Of The Giant Octopus.mp3": {
        "": {
          "length": 1783901,
          "pieces root": "91b3f6f33d7c2cc4752c3b6e79bafe7ec2d3e03c31ae3790a5c132d1a9b93f84"
        }
      },
      "tentacoli-12-Two Old Kids.mp3": {
        "": {
          "length": 2965602,
          "pieces root": "0b09f31a4206b8c42530dc7fb489ea52f4db6992b1de8c9e56dd1bf711d64af4"
        }
      },
      "tentacoli-13-Tentacles.mp3": {
        "": {
          "length": 4319196,
          "pieces root": "26c6744b0b3245ed23691732c22f95a9bf074f32a49ba5c9feece809347e889e"
        }
      },
      "tentacoli-14-My Son's Friend Is A Champion Pisser (Versione 2).mp3": {
        "": {
          "length": 1555839,
          "pieces root": "736490ac9a57251d5feb02bb8e17d0f29e761993bd604ebece2f66e8cfc24a76"
        }
      },
      "tentacoli-15-Tentacles (Versione 2).mp3": {
        "": {
          "length": 5261174,
          "pieces root": "4c94d4d2d20631afa6fa4d4287af4cf5c262c00f834c027c9df3f711adedb2db"
        }
      },
      "tentacoli-16-San Diego, Yellow Cab (Versione 2).mp3": {
        "": {
          "length": 2877921,
          "pieces root": "b9f50e8baac6b38dc2f84e93387b8c5e21c334f54f8772cd5dc819e88c671c6b"
        }
      },
      "tentacoli-17-My Son's Friend Is A Champion Pisser (Versione 3).mp3": {
        "": {
          "length": 1079679,
          "pieces root": "a2781d81c2dc33dac179bce14390485e47f2129ba98ed4efbd4690daf7229d95"
        }
      },
      "tentacoli-18-Too Risky A Day For A Regatta (Versione 2).mp3": {
        "": {
          "length": 874993,
          "pieces root": "c67de66bc0c2c41fce411d351d82dff8afe809e5206df6b14d536d4ff4c00dbe"
        }
      },
      "tentacoli-19-Tentacles (Versione 3).mp3": {
        "": {
          "length": 3951350,
          "pieces root": "b6145263d70c69c630d59dfa07856663b33e5621a62a33d7cd706c3aafdfe2ed"
        }
      },
      "tentacoli-20-Sails.mp3": {
        "": {
          "length": 4358356,
          "pieces root": "72436d6a0686a9a83d782445224036c71dde61e1824ef5ea230462ad95daa11d"
        }
      },
      "tentacoli-21-Sails (Versione 2).mp3": {
        "": {
          "length": 2870766,
          "pieces root": "b27df2732173f94fb73fece8d7ca2864d2c027d5186f078d30c01e4310d700e0"
        }
      }
    },
    "files": [
      {
        "length": 3177585,
        "path": [
          "tentacoli-01-Small Town Pleasures.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 230287,
        "path": [
          ".pad",
          "230287"
        ]
      },
      {
        "length": 2778997,
        "path": [
          "tentacoli-02-She'll Never Come Back.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 104587,
        "path": [
          ".pad",
          "104587"
        ]
      },
      {
        "length": 2333412,
        "path": [
          "tentacoli-03-My Son's Friend Is A Champion Pisser.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 25884,
        "path": [
          ".pad",
          "25884"
        ]
      },
      {
        "length": 2562622,
        "path": [
          "tentacoli-04-Summer And Winter.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 58818,
        "path": [
          ".pad",
          "58818"
        ]
      },
      {
        "length": 2796486,
        "path": [
          "tentacoli-05-San Diego, Yellow Cab.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 87098,
        "path": [
          ".pad",
          "87098"
        ]
      },
      {
        "length": 3863849,
        "path": [
          "tentacoli-06-Happiness Is Having Two Killer Whales As Friends.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 68311,
        "path": [
          ".pad",
          "68311"
        ]
      },
      {
        "length": 3696387,
        "path": [
          "tentacoli-07-Too Risky A Day For A Regatta.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 235773,
        "path": [
          ".pad",
          "235773"
        ]
      },
      {
        "length": 2583746,
        "path": [
          "tentacoli-08-Sorry, I Have To Go.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 37694,
        "path": [
          ".pad",
          "37694"
        ]
      },
      {
        "length": 1924024,
        "path": [
          "tentacoli-09-Scotch For Two.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 173128,
        "path": [
          ".pad",
          "173128"
        ]
      },
      {
        "length": 2463949,
        "path": [
          "tentacoli-10-The Killer Whales' Games.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 157491,
        "path": [
          ".pad",
          "157491"
        ]
      },
      {
        "length": 1783901,
        "path": [
          "tentacoli-11-The Capture Of The Giant Octopus.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 51107,
        "path": [
          ".pad",
          "51107"
        ]
      },
      {
        "length": 2965602,
        "path": [
          "tentacoli-12-Two Old Kids.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 180126,
        "path": [
          ".pad",
          "180126"
        ]
      },
      {
        "length": 4319196,
        "path": [
          "tentacoli-13-Tentacles.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 137252,
        "path": [
          ".pad",
          "137252"
        ]
      },
      {
        "length": 1555839,
        "path": [
          "tentacoli-14-My Son's Friend Is A Champion Pisser (Versione 2).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 17025,
        "path": [
          ".pad",
          "17025"
        ]
      },
      {
        "length": 5261174,
        "path": [
          "tentacoli-15-Tentacles (Versione 2).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 243850,
        "path": [
          ".pad",
          "243850"
        ]
      },
      {
        "length": 2877921,
        "path": [
          "tentacoli-16-San Diego, Yellow Cab (Versione 2).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 5663,
        "path": [
          ".pad",
          "5663"
        ]
      },
      {
        "length": 1079679,
        "path": [
          "tentacoli-17-My Son's Friend Is A Champion Pisser (Versione 3).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 231041,
        "path": [
          ".pad",
          "231041"
        ]
      },
      {
        "length": 874993,
        "path": [
          "tentacoli-18-Too Risky A Day For A Regatta (Versione 2).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 173583,
        "path": [
          ".pad",
          "173583"
        ]
      },
      {
        "length": 3951350,
        "path": [
          "tentacoli-19-Tentacles (Versione 3).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 242954,
        "path": [
          ".pad",
          "242954"
        ]
      },
      {
        "length": 4358356,
        "path": [
          "tentacoli-20-Sails.mp3"
        ]
      },
      {
        "attr": "p",
        "length": 98092,
        "path": [
          ".pad",
          "98092"
        ]
      },
      {
        "length": 2870766,
        "path": [
          "tentacoli-21-Sails (Versione 2).mp3"
        ]
      },
      {
        "attr": "p",
        "length": 12818,
        "path": [
          ".pad",
          "12818"
        ]
      }
    ],
    "meta version": 2,
    "name": "tentacles-tentacoli-1977-ost-soundtrack",
    "piece length": 262144,
    "pieces": "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"
  },
  "piece layers": {
    "0b09f31a4206b8c42530dc7fb489ea52f4db6992b1de8c9e56dd1bf711d64af4": "OrmkL+1wt5DMFYBPxOPA5cH8hsrAtlIhJviOqd41/UovO12SSlbrFchvhvi5DVrS8CkjguZZ3kfha8mRcGGY8RAc/RPjlPTggnO/aWvkFfCtGWsLa8ABT3MQETa+aH2iYfah6XNpDHw5heTQBas94o4noUMRWj2vf4XeSUUYmCdIld3ZUv5EC/lkauDqKi+iYE86H58RLKSoqbGkns+IkwDJQfh9GBY2FRLtitEbukJqsBxwnHY4QWWoGlkas0FrcooYDBSak+2fcYFoipVLbi7fPZHKR+sJLxFjE8Sc7/hVXfb8usqNYn3EPPHB8jlMsL/sC8ZD5YUIj6iXgFWVR0hIvwMLLJ9f7fGRSmO/R6Z15aF+0YLzNyS9DhAxrxJv6VVbT5VKC6l1/QOSSKr2UvW9C78Sidm7/f+4K1yY0XiPWlQyGODUMrvbBlGZTPb0SVi/828r+YrofHkSv5Tz868yv7R2QdvJ7ldV+RrM5604W0MAN1Tip6BNQndW1CWt",
    "26c6744b0b3245ed23691732c22f95a9bf074f32a49ba5c9feece809347e889e": "93cms33PbZZTwmgqv5mck+k2grLln6vNXYm1D0H9sr626dMzmAdfQif4o5BAAMScWvQhvRYscGWk1tjplEPvLU5U3OMyqu7tVPITvQ1w1lw7kcozYN4t8ePhlcR/nrE75oHF9Qm9xJAMts3GWvYxUROFkFilCLZd82NQ7Q0c6RKBNy5+y67rQ2VD/+AJFUuSBKUZSD70v12TdSRCL6T2xXsf/3G5jRxwaOVPsfnwinyHHz6FShzXytspL6XSAvXOoxH54BB8RmUgqyE+f5ocs1I+jpnx62UGPhIeU9por+UdwIjtjCFBbAYCXnMXBPfsVPR0HcsDgzcKwoWzvap7gJOJWhRRcB15OZiHQL9KJ6GRE1/ugcoEq2EJbw1Nje5Pzm8TXIEsNZyPVa5cN92E19hFFaOM1ZDKgq4lZgMLu1hrfvaeisk2TyI2TF8znoVw9CJCA0XXYI2e2XIH/3zXyqAYBn2h1un8MFpgBDkU+JblBiAp2L8smM7BBb6IQVKQpd86WXtrpWv5rSld2R94H7AUhc8xkaTZAa2vD8sEackjZBC9S02hWDEpGNl0ohQTVikghfqiW+zrOn7n7CIfcTHOp4SVJq7Qpi9ttuyILC9e+QI+MV888XrNcB29b7Gbd3M2/29mflYtJ7wBneZZdtlQGxgFXD+Z/pNktW5znVu7MzTvUhiitUbq42r0+4aXIa7TprFx3vsnO2IHMvKi7A==",
    "3b458ec67b680d056b9f48d2920242bd812249cebd1939880340e7d2e136fe0f": "nTFIf0LPwCPoNT78+kgBFHGy5XDvp5NA2p61K/z22PXj9kdCi7wPdvqK8jL2fVqwde66RhXHGbT/Wlutw0isomSetuJEWZ9A3F/TKw1rSjKPGz9hOGa+UfxjjUMX84QfVscP7GVGfcegWQTM87L2o/Q9VKMaQyNPUldSCebK5fSoggX+7LT+5d1U+Z1gaEI/GiCm/D0tfLh6ddXQhybKgZTzoP+zvDor7Mqu+4pGKE1eJHU5h0Iw6DdgGup6vfoOcTFY0flI4DUHi5JMR67XXadcpa5sslf8nZ0AyQC+PEe9+jI5yB3Y2Lj5V3Ah9xW3NJXruPOIZjeqCDXnZ+/Il6VuBvzhB/16jX+N1PFWNDfTP5dPGBaZJz15IYLzPUCC",
    "3ff20c6f038c048f27e428499498e1d19488f8f934df6632d5d4d827ccf3f3f2": "pUy003/UkvEJDvQzN5jXhX2B5truw0pqVsMHdPYMdqepwWcqZEBrtQvOptgzTBmxBmpyVUPoGed4G1ls5CuQOl4xV3fww7zU6tA/jUAZ2ufWbAfeIayiO+LdgX290qihHmni5a1MiGgL7vHrINB+BBnYJ75BSOFJ+Kcb0J1hBgPCleZZSHUe3y4LBo8Ten/ocrGbCwPAKzOr+g3sb3gt8QI9jKvB3e0VKGBTF58QrjoihLIdPiV/F1W55CkQXidVijh9FocJLESmWdf2CFm4mNOxRWSrOXAEOLuNwgs80pg7uL0qnAqr55gJbZLyktaWpP+cVNh5DaW1I6WwjCsEMWLJKvyGyWN74ibh3taHnGD5FFcw8ytSiFBcTeWDZl0pAuZZaxZgq11l8GuiFJjaMHzWhTixWoqOI3lZ8TUx9Yg=",
    "4767dc7f1b8d2f6aaae276034cb2e2c6c656af56683e148f0e54c15382273245": "X5RLsarlc9pADwVgp2d7PP3hZN3ZmYlep0pA2FuskDlbKIx3Rm0aNQJO3I0WeALY06cjog7jS9JXMMPGOZjSwfTPnvqPlOrpBmaR0/0k4UsHeV7Ma4D6Bs8TRdGgGIpmL4mhG19GMmNATTaCSTleOdkxLWg8/ikCEbk87hrqjMDTK570+4Z/37L075ZbJTZ9PiBv0d9otlcPwFwcAG0n99SCx7awBNSolAofK4aduCt+p8TffXnfeG72Ng2hZVCDIIKliAoguzDaGly0iyRkD9yxD7LcM6FTtcCpXYEfQBiBcVkQkZ5TclFCE7XPNpMdtu1ft1BPuisUcqDp7OYdGtvnHkjTPwuuYBp6XIbHYeIDIWfatuSmlzP/abATYrkxDSIHJTBSdOnTkY/9kK60QZ6wtbd10RpAdMcFs1QeMaP4fAvN1GrHwfaT+FBuu31S7MICgv6JzSkpRak9DhD9xoyG6H2fTwWPBY4s+1eLYYCwcwf7n6ChO4VHxZI9Yqk+aGjO/PYTlohOGDg3VeHxgGvVEmoDt+VA1nFtqvi4UPg0P7C914o4FzQrZjpqelSMKFCRlW5uWZnNH1eIe0XA7kSr6POILRwTYofx5Pl23MuDjsg+YTWcTukUj1pKqwuo",
    "4c94d4d2d20631afa6fa4d4287af4cf5c262c00f834c027c9df3f711adedb2db": "DyuboUHYom86yA33liC6obKdfKiCuOiyTlNTt5ACMtZF6TRLlaolBIUHNuLUnUPbfTTyz1cKtR/jFWwl563V8JhmXwSx9EvlfbCwIFulQBWcy9/35DHrRoIcwsUvB2Duu2Kfcd4ICOKqVvzOMsIR2+A1C6Ar+UCCADt5hna2ewVAFlQ/TM5rrxNioKAtWgmowt2dVrmng1dOX5cq6b9R1gQOB2byxyBbQf6oAK1royKWOyLMgVjjnGxLbpkgAAQhyhp+ja7MzGYF+mYo/ohSpjok0tfm0cEbG0k4s0Wgqlr3TMLdjyLTHzVGsPywKTwz/kUtrB3JKMWoxIqBjqWjTf+judP0abSv0/R6C8DhLk6x6oKuFeClww1cjoHfaP+OnSMHjZDPTw7gy+9oKVT5J5ByCWrXkUi760FhEQRXeEG2QAZkJTSgnNfVEEU6n7oU2Toslqh3SpMGjgjbZDveCxw6VhEP6mhZe6QyZ0fSHbaTnlIEt53jrUk4UNzEljVqqb08/csCA06T6mmBaAy82VBj8gRLSzfsWc6mQM2K6cG/UGd4NxdFPJgHMReLgU/xYiAiWhurTbjNhW0wwS86+6fbCPehWnvQq5rLDjtt44yohRMlhOIuPNgQeoQ5YUrtB/cQHki6Wg8bc4OyKMt8mrRBqR0ef5SS8aVt8Lt2TzT+AEp1IYwau6BEO59JkwqhF5F1uZO2+jBB449Az/B+O6JG2vjOhfnAw7aJgkJrUZICgzPkIzMfXEGTGmDzBI5acKeGeVt2Husv7794wjbdw5Lnz5k2vTogv34wNhYoSsUiYpFkHw5iiYERu+XfznAs8Zu2iD1oVRv4MWF8fnYJP8nwjOhSwrjBSx9HRaTicrF+sr9wRZfehlk14qN9E1Oq",
    "661b7dc0bb901d026370be0b73e87fb6a95479dc85bcdefe61711d8fc5b236f3": "gATN5ZHot0T6R5YneYJPrP76oSoC9fI49GtMgK2kJq0ya+06/wZZ5+RgBQoqFOv+5uio41M0wZoPyz6NsYrKFu/91+XGXzDoJQMsTj0PJFL/uXRyzfCtfNk7tfAGrEvN1Jstv3MVyPogT9zowv4U3zDpcPY8zjpfu46LkHI1XZyu6Uh2t/vrc55UO0QgSmAwr9z+mcX/up0n0ZaaTGNOESyHATjBon7HMt2ejPQ1MCBEtjLRPbhcdhEyJRW+A85aqFeqUNOLqTspBvqiio5peWQyQd0lIw/M3+Fi4WNJax+fR+DB+VPjKlaWscyje05QtNu42RT2iqB4L11jn0pdvw/Xfk3ooI+RBJ00u1AeSSQqZiY65sP3G6pTXbxDb6EnTgj48g6avUnyKMJCqHEY1/RhvDakG0n41l1NAT7vh7Y=",
    "6bdfbd145a64cabfc9b0971f87ae69c93bd1847b0c48351ed971c1fa4e9db97f": "SVct+bzPEHObJKHC3ZuofpIzlBylCSOFU8qsaGF2y7RrKZrjhlbOZdu8sE4rXUDn1csYAKCKwJ3cV1y3Ylg/el3ZO7d8syTwukJfpMfJE2yybMbQBlT/+AY4KncrT/IOD+3C6t88jOjaJW/VLiKY/RzeGmfyw3vZzVvFArsSLCxAbcrNIeATbLp0MJ57YOpgxiFgPU9+JUdMcN5PZtG86aTC8t+1Ky7MOcb2HzNdteqfVG58Hkl51l/xPFCHYZRTl3SkoOVy1+B8nEj0W8IS+1E8s9RemS4qyN2p2NZE9JBQKGiOTo8zTcyuhZPB9yxhB2xnfyCQenl8FwpfkQLCAA==",
    "72436d6a0686a9a83d782445224036c71dde61e1824ef5ea230462ad95daa11d": "slBceVoM9U+QRS9g3QIT+z/C08OGn3aAuwBuSSKGAzfCsDfRGCkY9IhFtQUG9wSjyrUU0Mh5oW6awq6aICOe/KQJCQ+7mM59RUBCkMbuME9Cr0ut2LlqAs1se4NtKgcMFwGnTtmy78Qu/q08tIAFQB60Y/buuHOaCtsxpWhoB3phA3eQRykDaWLmphUlXoYELeJP2T/C/5ZXENVQz79F8uyXTfTZj98iLqOT+8SxOKA7PsZsnIDRLWGWfgOic/nAZh1wJMIBRw90qFUmoYdQKaWRwB1hcQTObEtZAF+n8qxkRfHCbUnoNJTswB87QtG/hxaYclaVRZaCwgoLvoqYx85e+XGZEI83+HHxwto4xN/Bzj/JVtk2HFbx/QLCdV5rOtUKlJhsYIuOK2juRKCaOLSq5NghVf5alfy9qIjWWseQDHdPDiQB1mck2lrpZDJ+Das9f3b+ce4pLwxtQRW1JLOBjgBi7HXelPyu5lMRlqZcwRhNFZ4DxrprmPYmw0KeScndn5LHJXsDC1JA238+wIWP29ZF4QwLWvMPkn4Wfe4QYmBpeNINhPJjCwkhQx90Y20VBaJGKYK8/Le1J3VduaJ3ciYxDYcd7WW0ngaZiVKZ0y7pjfqC+tLT5zq+GQSGNPNXogL+OEaFKYVd7Lz0PfG88uaIkYVq0H7CDAjZwJZSnlCaT85L0Kv44jouiIKmfO9QX8zDS+QxLAh/Xy7VAw==",
    "736490ac9a57251d5feb02bb8e17d0f29e761993bd604ebece2f66e8cfc24a76": "KyDTfIYZYSJe7qMcrgvE5sUiV+0eus85j2/q76tIC8603rr7bx1er5UDI/7srDKX0/ah0ZdGtzleHKkkAuVwCE73C6iDxwEI5OESBF10mHRzD2ShejpsUNGx2wGKSNBl3m4XFs6Ta84bpxA9FvbbeBPsMvH8k1+fjxee4LqYxghlBHAOyMk0zMmvVGHN59cG7jnDon0o172flEf+UYrOnom8ZDi431XQ7wu5KVpfR8YqCjrAfLfPMhymEv2K17Kf",
    "7ad85e1400e68597e006040d4d9373d2a05d9b2ae13f14dd9939317d33ea2c8b": "/5ZiHJz/da3YhNv57jfG+6W5p++ZnjCPsy2QOJlC8m1iN2bmH3ygJtADgZZjbBq9lMg6qbCwEVfHzVNSgh6E62zNiPrHkguznFha+8orialK0xQe9TVnoMAS1fdMtFPkWFa8zKVXlLrmEiXa6MMDt7LmTGDOw4AFmIgTZ9+cQyJh+UvZYdYyO5xl9yVhDIK/HNSkhIe/E/gkMTBm/q+mXfER+uPLq1xc4eqykA+FVvJnBd4rzuDABEFUJP+sVqxqFFY28Ue+SSrcmHjnf8IL6bXem9lUcLoS176lXBOF73OIY9s1E+2vOM02HSXYiPXbsi+QE+cKrvs/PQ1gas5/EqGXDrW2ioYqebIX+Dw5re8xLvP67w3xrQh6N/UwyUb05FoKrgLFxisYn/NELkWiNV66PFccfCh4K0RYZUW8SMsHcwAEfQRst5ICX6H9HI6HUqkk++FQFWw1xmdPbcBKCw==",
    "91b3f6f33d7c2cc4752c3b6e79bafe7ec2d3e03c31ae3790a5c132d1a9b93f84": "n2cabuVybK3NWw3P3/XguQcIwT/JKcvTwjfIWqfqHQ8Sd1QeMY4bVjOol1ubEWU7BfhXaI9TS80wWoj7MKXCUdn+XkJXNh09vj1BoksVyiPjPT4powprR0MHolp1jxh+fN5uppVJMEtHYEMy1EcpU9zVAALQ5fwXL2XJ00+VhFsnoL+5NybXXGXB08Ihiy41rTkL/eDf9wS/xnDAooYsO+cC+ZZZJ+v7Pom/3pRU9soMFNJOKct1bsb7uuT9prOnKF4ppNEFZE/GwMezOYK+71WkMqjJHexFaEWiYLGM8mU=",
    "a2781d81c2dc33dac179bce14390485e47f2129ba98ed4efbd4690daf7229d95": "cy1UGgsHtzk1YlCUOzYxU5TTrIeXX7A6KiSlLj0ng+HzCKmJRaDGi0oqbkHJJTxA2UPrluSUJ4+CAhOYw7XZwHPVW8jh2ywDtSABmQvXEulGVJ/knxQCMCbnZEs5Sp+2J/Wk0hp6kJp0lu4Zsqts/pk1n/GiWxfN/1XZA1URfMu0GO4oWPDIPgpqFTKtUR0KL+AICQIo/7iKceDKl4EQLw==",
    "b27df2732173f94fb73fece8d7ca2864d2c027d5186f078d30c01e4310d700e0": "AwIURStzYR9k0OBxqnDmX1TL+6LU6aS9QO3blOLQuVh8MU/2F1KcBDskSVtkrJwfROiHpe9E8WCDMD0qbFRb4AMFBZhF7HeToUj175XtVeLU5WVWK8vB/gumLvQDTZqWb9tBwvcs8dGwzdVJfTNiIyIUl8eAVXtDEoICFgGyt1N85uGsl1BXTsY75p8pcKwAm/3wBVqZHPWUxYyjry1AKeCMCi09CIAn3HSD+65ewi9vwgNuhx3MZJQ6+3YZcHLWonWu2aGTHCPRHy7ERJ3EMgk3l7BDLoXLpTqe+/vRYXm7q7VwHyc0xEo6VeHLtWyeeUGUt23zWfxt9l5hHFCJ2ZvQVbJxYP49QCkvUbOmeYv7HAuWzl5f217lD+tnhOJ6AxBhMVZjWoy+IMg1y2C7mJ25nEd2J2yFfHf+WSy1h4d9IcPbYm64MSWR5TCnHKb1MSt4xdCjjTi2HP/8Zxhb9A==",
    "b6145263d70c69c630d59dfa07856663b33e5621a62a33d7cd706c3aafdfe2ed": "wfe1c3oZL51D35knRIf54tu+pUgpVC+Pitr0bOoSKXSKeKRvqfGE2aB8VbQLoEB5DjmEYteWfKtJBqN3i01k8aZiKfFLM0jpad/3LAH0ULeyMLRGPT0QTfuCzh46QjiSMa93Fnhf61OzQxqmt1A23pxwXeqwivAsehtrCthNeWncGiRl/8O/pMmyu6h6SF7LtfE7w+MaxB8m1MfQBvauhoTDOdRFAAlKm4wFkAHxZZlAixiUvKOchdvG31viM+OCyibWkTmkSlXVFWCp4ju1ndjS5jjzlPAz4lRd/D8YYoGEbUlK0WF7GNR8B+grTRE7m3CTLQBkLvtxsfPfR+TLEL/iPc7AQ4ZNZ+4ixzkWPISuvu7vZb0xByx5fgoWCPJDiRMprGx+GG8FjcMAI8Q5zpOCBVr5S+tQZpF6gUQJPtLXcHaWfXGy+AWGPWzEQQB4QzutKPTkZT/GteT9I7To+tKSsTv7bnWcfZrtBbOhpBUHBAl02W9vcPCwwgRpDLiWpGJfoziX4bmmqq3PlAdSf6D7pvOd5NJ5gsXFayZJHrwgZ8fO1zO+CvBlVEsTSEfOYxn6k4h6igW5Cjo+hPXRlF6tUi+opqd3oJK+AvER8exB4V3K4pa0eUO7ICA9PViKrX4eeKwRSurxzthIxR1SZyRIu+u80l3Qp0Vjn7Rs9ZY=",
    "b9f50e8baac6b38dc2f84e93387b8c5e21c334f54f8772cd5dc819e88c671c6b": "mlA7x/hs+LOUdTamHzEJZQZelGfXHa0EIXd8VZDLe1tnCTQgWmwYXfhSeJ6Sfsvz2J0t6jcLHuYM1JenXbNCnWA1sblB+D4aHQs/GWbP15cOKSwp3Vzr4m4VdrbPMRXdHFVn8cE/QRa8akYhme/uel68R1RyhgqvDZOsD1Ml7EigGtsKa0wzu9+kodzCCtCI+qruIUa64BxQDLTcW21fGpLeQZeaDJAIr/DrzSs9s/z0OjI1XP7Eo8VGGLFn7zO8dMT69LLyD5XPRbYIz50+/AV/2+Bn0DaBYy+f6AZJVAiCVEj7++2CuDIyAzNltb4SZSRH6fjyrmqDIo7v9PfIy7iXvTHwuJweyfEuDF/l7iKZsWjMlLT77vseIiaDqCBsXuMPg4cZCF35MXmfmDObco0zvUBxszujKyrGdKxx58bRnTgPPFh4h3lsDwKzJu23F60vsG4V0WNQ9tY2tiePfA==",
    "c67de66bc0c2c41fce411d351d82dff8afe809e5206df6b14d536d4ff4c00dbe": "+yKBmhJqkSsy3at/jXFIFvjZbUPT6ayJHsBtWeIP3mzHHflO6MUtioZiVQ2VnnA/PnR3JelkcwKwMRXmfm7i1zhBM2Awl0WlrqImvM2TBvmfMVPdpyWwejTwa/+qI79szw9waLwWYOdmu+jAwXk2hpE5naPvsm2lRuz1x1ehpyA=",
    "d0063c2d1f1c5e3b5e163383d5f5a63ac983be59708e0d695870442cebbe37d9": "Ngl7rHoMejoI0eGHLHI9mb0ELNrRc7h4EZCiaaiO1TQSgBX//vPdlS6pptsB62ocxGacCH+GrIhH75QNhwxAEWwBWFGDFofCVii4EctiGgBt3CpQgF7Jx0ce5AGxvD2/PKuV5MribIC893ftswL+NQFsT8Vp3N4O+nvWr2Q1/5avfGwkblyHAhWXIV5w3R9uYht94HxH0EjYZrDKCzkVr2ZypdlMVeStnJPBuJG5g+YcZMJBGFJvMxzYs95AeluXmh/dIIEh1WzPzVhaseC6q2z+SiIV5ZJtrH8deVNI4gOd6dOG5VCVjEtjwf1ewCzoYoma14wCm5gf8/4mT7FxNZ5zuB4QjBz0rJ6d/iQ2slugGU0syxnXKBLIFh2+Hx7WRA092URN/32owNkFVaj9OAg7pGKP97gdmKcqChaRoRLjgwJXQ5dr1YbLyG0qzhIUA3Vu1PtPb5qWBOykTxh3lO1ylt4Mlo2M9q7QjqONPfwXXOmttB792hOfERKzgniofrq0kwKEl/Yd/QhktOkrbrKUs1Xco0R3365y4kmuIdes3lws17nmWbu6fRZvjGrC6Zu3ZN7QRgxIpRWd1R7g6MkHnOBfz4Ws4yCheJorn5XgmbamnABpo6t1mwZEk7/6",
    "d1c3d80bf13fd42b3e8582a15a21172d23b80247f3b6ca85ffa97f018db4dfcb": "XldIzkVQ/K0VVG2P0RElCMdWn9S8BZSDOC5aiNVoz6GRXffE8J1looO+ZKsmT2oV8KkcUmbaHnxaWNixFC4Q3LozSkrcAjdnMq0MZxRFk/WVQmsDLTuUFEfKT6s6j9ERT/cTcH7Qw0bzDRzY8H3Q91qdw02RK9C2JWHqWdgxn6G0u8gIPFom7atyZb6eF6wpbPu2y+hYtV+KQ+WKbajiji3RYxBUEmnlsIA7TwaKBNRbL8IbmP0iX8o21yI6BRpPLQ3dfHz1J0FWdnvucbZaN63DLkZVyy0RnJ4jKULGiYXTCkKCFri3kNib799tEsU9JVUq46V5hKdP8SOxarWv7BCYhmvxbH3O53OVEpjmCALaVHtrD/S7R4R7qsPiTk290vk7edzbbj5NyoPsXJPXGDX41OwipCoIL6TMulboWVWU/ZjTSh/bH5WfqPdLJDhKx61AnZSpUPJgJroNdzojjw==",
    "e5273e3a62dee1a16328471a471f3a361eee0de07de68a11b6695c8483a4eb88": "JlcL/yfbL/d+1bjsMMpNkCN9AoNtQSHiecicfzxrpep2Vzthoooyk3zGGyrStrhmxHU1DgfoyW176op+3stFf4InqNCBBU2dciGuJrfEcmj7GuWi7eWVZWOcsZOrbOc07dz4BkaSxjPfCkxShE123IBOdz3t4Lot1CD0BsE8smVFF3qp6x0SFYxfofNSIU5T2gwIRE3HzJPzN1tnsV98lhaAUU/a3YUofqrgVNPAIrqZSH+bAmdGhxPsAJNzW+cq199LRjHVpIY3n41WoujCzZK3bF3hbRtU5hxQK+zqMQnSskDlk/34arHlTPRW+0z8hIIMcZjq+wzxxLBdcIim9hi/HsQjIrQjS4kdFwHuRZ7Mnjv0c2KLCui36pYqjAaMYhhIh5HOeyorUJY0T9ux08f5jE5caofU2GZu9pHZZjk=",
    "e755700c5bcea4905a1a3f900351d8a5564098bc081e6754e379f805728d190a": "O51c+F+qBXvwiodQC7gu1Rr+OfdGN4VI8gsLkqaiiGDyS3znAOXh0/0NF4+CVA98s896hwo9fgRMnLqOh47dkQdpFJVqA8GZS7ye9tf9kQIG46IfkhrKYJNoeilTs0rJC9MI9qK23EtTiDEYPjK2nuEvnCx67Wvj8uyUZvJM152LC9Qy/YdXw0uTP0jD/5hLDjOHWgNGEt4lalejai4yPR4xh4aHAZi8J7KNCdr9WnfQeTv9r0g7XVacs7+lOHc83LzyU2TUdgqlCULob6toS6yWMuoCF1Hpva+OTUyNYIHA1tywiItg4/frDOfdx+wS7SmUfTPxwrDgwfYKRZLT8AnBgScna9JdcDGOF3Vx4mM4H7E2RXM8b9hc+hs0XjsJmtmUueCm96U8Yt9Jj0O9eWVB5Huj47cF4HfJA/gBoOESUMGqURVMjvWL/XiX6+epAdNvySvRTtnOZpEfTvQHBDu1l8JzF7mVqCOOmIqWnS8IDVuQlZhcgtCKn00SWDal1i2RbbqeJbYoEQtCWHkwOWi2Uy37gj8mKZBNxMURazE="
  },
  "infohash_v1": "59c586143f057d74f28f0c423b0b6e5d39317838",
  "infohash_v2": "84c40568b01503d8d4baed762ae8aa3c096ce6bdfdc7ede39fe9c6ef531f2de3",
  "type": "Torrent"
}
```


</details>

### Abbreviated Representations

#### V1

Minimal

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v1": "1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083"
}
```

Expanded

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v1": "1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083",
	"bencoded": "https://example.com/torrents/mytorrent123.torrent",
	"magnet": "magnet:?xt=urn:btih:1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083&tr=http%3A%2F%2Fexample.com%2Fannounce"
}
```

#### V2

Minimal

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v2": "d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a"
}
```

Expanded

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v2": "d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a",
	"bencoded": "https://example.com/torrents/mytorrent123.torrent",
	"magnet": "magnet:?xt=urn:btmh:d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a&tr=http%3A%2F%2Fexample.com%2Fannounce"
}
```

#### Hybrid

Minimal

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v1": "1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083",
	"infohash_v2": "d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a"
}
```

Expanded

```json
{
	"id": "https://example.com/torrents/mytorrent123",
	"infohash_v1": "1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083",
	"infohash_v2": "d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a",
	"bencoded": "https://example.com/torrents/mytorrent123.torrent",
	"magnet": "magnet:?xt=urn:btih:1ad02871c78eb1c2934f46de0c7ffd9ef9ee4083&xt=urn:btmh:d655cc657b0b56975c2596ef1c493055565daccaf2ae29cafdea22bd7cc80e6a&tr=http%3A%2F%2Fexample.com%2Fannounce"
}
```

### Reference Implementation

A python package with [PEP 751](https://packaging.python.org/en/latest/specifications/pylock-toml/#pylock-toml-spec) lockfile is included with this FEP, see [`./implementation`](./implementation). The package implements encoding and decoding `Torrent` objects to and from bencoded torrents. 

Install the package with `python -m pip install .` from the FEP directory, and then call `fepd8c8 --help` to see usage documentation

```
usage: fepd8c8 [-h] [--encode] [--decode] [--with-context] -i INPUT [-o OUTPUT]

Encoding and decoding torrents to ActivityStreams Torrent objects.

options:
  -h, --help           show this help message and exit
  --encode             Encode a .torrent file to JSON
  --decode             Decode a JSON torrent object to .torrent
  --with-context       Include the JSON-LD Context in the json output
  -i, --input INPUT    path to input .torrent or JSON file
  -o, --output OUTPUT  path to write output to. If not provided, print to stdout
```


Additionally, the [`torrent-models`](https://pypi.org/project/torrent-models/) package will implement export to the specified format following this FEP's drafting (and this FEP will be updated with the version of `torrent-models` that implements it, when it is released)


## Discussion

### String Encoding

Two string encodings (base64 and hexadecimal) are specified for binary data. This choice was made to balance space efficiency with matching conventions that are common in bittorrent clients: bittorrent clients and trackers typically represent infohashes and other hashes as hexadecimal strings, however base64 is a more efficient encoding for the much larger concatenated `pieces` and `piece layers` strings. 

The handling of strings in the bittorrent specifications is vague, and that vagueness is matched here.

### Out Of Scope

This FEP only provides a means of representing `.torrent` files in ActivityPub/ActivityStreams clients. The following is thus out of scope:

- How to produce `Torrent` objects from files and directories
- How consuming instances should process `Torrent` objects
- The rest of the bittorrent specification (e.g. using ActivityPub instances as trackers, which will be the subject of a future FEP)
- Improvements to the bittorrent specification: this attempts to be a 1:1 representation of existing `.torrent` files, though the nature of RDF and JSON-LD allowing for future extensions is part of the motivation of this FEP.


## References

- Christine Lemmer-Webber, Jessica Tallon, Erin Shepherd, Amy Guy, Evan Prodromou, [ActivityPub], 2018
- Bram Cohen, [BEP 0003](https://www.bittorrent.org/beps/bep_0003.html): The BitTorrent Protocol Specification
- Bram Cohen, [BEP 0052](https://www.bittorrent.org/beps/bep_0052.html): The BitTorrent Protocol Specification v2

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.

## Footnotes

[^torrentterminology]: A `.torrent` file is often just called "a torrent," as it is in this document.
[^v1v2]: Bittorrent v2 is a backwards compatible extension of bittorrent v1, so torrents may be v1-only, v2-only, or so-called "hybrid" torrents that have both v1 and v2 fields.
