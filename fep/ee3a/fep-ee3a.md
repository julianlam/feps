---
slug: "ee3a"
authors: Marcin Czachurski <mczachurski@icloud.com>
status: DRAFT
discussionsTo: https://socialhub.activitypub.rocks/t/fep-ee3a-exif-metadata-support/8439
dateReceived: 2026-01-13
trackingIssue: https://codeberg.org/fediverse/fep/issues/752
---
# FEP-ee3a: Exif metadata support


## Summary

The exchangeable image file format ([Exif]) family combines file formats such as JPEG, TIFF and WAV with structured metadata. [Exif] records camera (e.g., lens data, focal length, exposure time) and audio (e.g., channel count, sampling rate) recording parameters. The standard originally focused on photography but was expanded with version 2.1 to cover sound recordings. This proposal defines a Fediverse-wide mechanism for conveying [Exif] metadata using the [`exifData`] property from the [Schema.org] vocabulary.

## Motivation

To improve interoperability and promote consistent handling of attachment metadata across [ActivityPub] implementations, this FEP defines a vocabulary and processing rules for exposing Exif metadata associated with image (Image) and audio (Audio) attachments.

## Description

In this FEP, Exif metadata is represented as an array of [`PropertyValue`] items under the `exifData` property of an `Image` or `Audio` object. Each item MUST include an `@type` of `PropertyValue`, a name identifying the Exif tag and a value holding the tag's value. All Exif tags defined in the official Exif specification may be represented, but implementations are encouraged to support a recommended subset for interoperability.

## Privacy considerations

Exif metadata can reveal sensitive information such as a user's location, device details or recording environment. Geographic coordinates (latitude and longitude) can expose personal addresses or travel patterns. **Producers MUST obtain user consent** before including these fields and SHOULD clearly inform users about what information will be published. Consumers SHOULD treat geographic and device metadata as sensitive and avoid displaying it publicly without explicit permission.

## Definitions

### `exifData` property

`exifData` is an optional property attached to media objects of type `Image` or `Audio`. When present, its value MUST be an array of objects where each object:
- has `@type` equal to "PropertyValue";
- has a `name` property containing the Exif field name (e.g., "ExposureTime", "SamplesPerSec");
- has a `value` property containing the corresponding value.

Implementations MUST ignore unknown properties. Schema.org's definition of `exifData` permits the value to be a string, but this FEP standardizes on the structured array representation for interoperability.

### Property names

Property names MUST be strings corresponding to the Exif specification `Field name` (e.g., "FNumber", "PhotographicSensitivity", "FocalLength").

## Recommended fields

Implementations MAY expose any Exif tag via `exifData` when present in the file and permitted by user consent. For interoperability, the following tag names and descriptions are recommended. Fields that apply only to images or only to audio are indicated in the second column.

| Name (PropertyValue.name)   | Applies to   | Description                                                    |
| --------------------------- | ------------ | -------------------------------------------------------------- |
| `DateTime`                  | image, audio | Date and time when the media was created. Exif's `DateTime` tag uses the format "YYYY:MM:DD HH:MM:SS". The time is expressed in the photographer's local time zone. |
| `ExposureTime `             | image        | Exposure time (e.g., `"1/100"` or `"4"`).                      |
| `FNumber`                   | image        | Aperture value expressed as an f-number (e.g., `"f/1.8"`).     |
| `Flash`                     | image        | Description of flash usage (e.g., "Flash did not fire.").      |
| `FocalLength`               | image        | Focal length reported by the camera.                           |
| `FocalLengthIn35mmFilm`     | image        | 35 mm equivalent focal length.                                 |
| `GPSLatitude`               | image        | Exact latitude of the photo location.                          |
| `GPSLatitudeRef`            | image        | Indicates whether the latitude of shooting location is north or south latitude. 'N' indicates north latitude, and 'S' is south latitude. |
| `GPSLongitude`              | image        | Exact longitude of the photo location (requires user consent). |
| `GPSLongitudeRef`           | image        | Indicates whether the longitude of shooting location is east or west longitude. 'E' indicates east longitude, and 'W' is west longitude. |
| `LensMake`                  | image        | Lens manufacturer.                                             |
| `LensModel`                 | image        | Lens model name.                                               |
| `Make`                      | image, audio | Device manufacturer.                                           |
| `Model`                     | image, audio | Device model.                                                  |
| `PhotographicSensitivity`   | image        | ISO sensitivity.                                               |
| `Software`                  | image, audio | Editing software or firmware used.                             |
| `SamplesPerSec`             | audio        | Sampling frequency (e.g., `"44100 Hz"`).                       |
| `AvgBytesPerSec`            | audio        | Bit depth per sample (e.g., `"16 bit"`).                       |
| `Channels`                  | audio        | Channel configuration (e.g., `"mono"`, `"stereo"`).            |
| `Compression`               | audio        | Compression scheme (e.g., `"PCM"`, `"μ-Law"`, `"ADPCM"`).      |

Implementations MAY include additional tags and MUST ignore tags they do not understand. Property names SHOULD be consistent across implementations to facilitate display and filtering.

## Examples

### Image example

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        {
            "schema": "https://schema.org/"
        }
    ],
    "type": "Note",
    "content": "Sunrise photo.",
    "attachment": [{
        "type": "Image",
        "url": "https://example.org/photos/123.jpg",
        "mediaType": "image/jpeg",
        "exifData": [
            {
                "@type": "PropertyValue",
                "name": "DateTime",
                "value": "2025:03:30 06:30:00"
            },
            {
                "@type": "PropertyValue",
                "name": "ExposureTime",
                "value": "1/250"
            },
            {
                "@type": "PropertyValue",
                "name": "FNumber",
                "value": "f/5.6"
            },
            {
                "@type": "PropertyValue",
                "name": "FocalLength",
                "value": "70 mm"
            },
            {
                "@type": "PropertyValue",
                "name": "LensModel",
                "value": "Canon EF 70-200mm"
            },
            {
                "@type": "PropertyValue",
                "name": "Make",
                "value": "Canon"
            },
            {
                "@type": "PropertyValue",
                "name": "Model",
                "value": "EOS R5"
            },
            {
                "@type": "PropertyValue",
                "name": "PhotographicSensitivity",
                "value": "400"
            },
            {
                "@type": "PropertyValue",
                "name": "Software",
                "value": "Darktable"
            }
        ]
    }]
}
```

### Audio example

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        {
            "schema": "https://schema.org/"
        }
    ],
    "type": "Note",
    "content": "Field recording.",
    "attachment": [{
        "type": "Audio",
        "url": "https://example.org/audio/field.wav",
        "mediaType": "audio/wav",
        "exifData": [
            {
                "@type": "PropertyValue",
                "name": "DateTime",
                "value": "2025-03-02T14:00:00Z"
            },
            {
                "@type": "PropertyValue",
                "name": "SamplesPerSec",
                "value": "48000 Hz"
            },
            {
                "@type": "PropertyValue",
                "name": "AvgBytesPerSec",
                "value": "24 bit"
            },
            {
                "@type": "PropertyValue",
                "name": "Channels",
                "value": "stereo"
            },
            {
                "@type": "PropertyValue",
                "name": "Compression",
                "value": "PCM"
            },
            {
                "@type": "PropertyValue",
                "name": "Make",
                "value": "Sony"
            },
            {
                "@type": "PropertyValue",
                "name": "Model",
                "value": "PCM-D10"
            },
            {
                "@type": "PropertyValue",
                "name": "Software",
                "value": "Audacity"
            }
        ]
    }]
}
```

## Implementations

### Servers

This list is not comprehensive:

* Vernissage

## References

- [ActivityPub] Christine Lemmer Webber, Jessica Tallon, [ActivityPub](https://www.w3.org/TR/activitypub/), 2018
- [exifDate] Schema.org, [exifData](https://schema.org/exifData), 2025
- [PropertyValue] Schema.org, [PropertyValue](https://schema.org/PropertyValue), 2025
- [Exif] Camera & Imaging Products Association (CIPA), [Exchangeable image file format for digital still cameras: Exif Version 3.0](https://www.cipa.jp/std/documents/download_e.html?CIPA_DC-008-2024-E), 2024.

## Copyright

CC0 1.0 Universal (CC0 1.0) Public Domain Dedication

To the extent possible under law, the authors of this Fediverse Enhancement Proposal have waived all copyright and related or neighboring rights to this work.
