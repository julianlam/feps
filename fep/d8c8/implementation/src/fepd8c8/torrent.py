"""
Convert a .torrent file to a FEP-d8c8 JSON representation
"""

import base64
import hashlib
from pathlib import Path
import json
from typing import Literal, overload

from bencode_rs import bencode, bdecode

CONTEXT = ["https://www.w3.org/ns/activitystreams", "https://w3id.org/fep/d8c8"]

B64_KEYS = ("pieces",)
"""Keys whose values should be encoded as base64"""
HEX_KEYS = (
    "infohash_v1",
    "infohash_v2",
    "pieces root",
)
"""Keys whose values should be encoded as hex"""
EXTRA_KEYS = (
    "@context",
    "infohash_v1",
    "infohash_v2",
    "type",
)
"""Extra keys in the JSON form that should be stripped out of the bencoded form"""


@overload
def _handle_piece_layers(
    value: dict[bytes, bytes], mode: Literal["encode"] = "encode"
) -> dict[str, str]: ...


@overload
def _handle_piece_layers(
    value: dict[str, str], mode: Literal["decode"] = "decode"
) -> dict[bytes, bytes]: ...


def _handle_piece_layers(
    value: dict[bytes, bytes] | dict[str, str],
    mode: Literal["encode", "decode"] = "encode",
) -> dict[str, str] | dict[bytes, bytes]:
    """Encode keys as hex, values as b64"""
    if mode == "encode":
        return {k.hex(): base64.b64encode(v).decode("utf-8") for k, v in value.items()}
    elif mode == "decode":
        return {bytes.fromhex(k): base64.b64decode(v) for k, v in value.items()}
    else:
        raise ValueError("Unknown piece layers mode")


SPECIAL_KEYS = {"piece layers": _handle_piece_layers}
"""Map of keys whose values should be handled with some special handler"""


def encode_strings(value: dict | list) -> dict | list:
    """
    Encode strings as unicode, hex, or base64 strings according to the FEP.
    """
    if isinstance(value, dict):
        new_value = {}
        for k, v in value.items():
            if isinstance(k, bytes):
                k = k.decode("utf-8")

            if k in SPECIAL_KEYS:
                new_value[k] = SPECIAL_KEYS[k](v, mode="encode")
            elif isinstance(v, bytes):
                if k in B64_KEYS:
                    new_value[k] = base64.b64encode(v).decode("utf-8")
                elif k in HEX_KEYS:
                    new_value[k] = v.hex()
                else:
                    new_value[k] = v.decode("utf-8")
            elif isinstance(v, list | dict):
                new_value[k] = encode_strings(v)
            else:
                new_value[k] = v

    elif isinstance(value, list):
        new_value = [encode_strings(item) for item in value]
    elif isinstance(value, bytes):
        # should only encounter this while iterating over a list really
        new_value = value.decode("utf-8")
    else:
        new_value = value
    return new_value


def decode_strings(value: dict | list) -> dict | list:
    """
    Decode strings back into bencodable binary
    """
    if isinstance(value, dict):
        new_value = {}
        for k, v in value.items():
            if isinstance(k, bytes):
                k_bytes = k
                k = k.decode("utf-8")
            else:
                k_bytes = k.encode("utf-8")

            if k in SPECIAL_KEYS:
                new_value[k_bytes] = SPECIAL_KEYS[k](v, mode="decode")
            elif isinstance(v, str):
                if k in B64_KEYS:
                    new_value[k_bytes] = base64.b64decode(v)
                elif k in HEX_KEYS:
                    new_value[k_bytes] = bytes.fromhex(v)
                else:
                    new_value[k_bytes] = v.encode("utf-8")
            elif isinstance(v, list | dict):
                new_value[k] = decode_strings(v)
            else:
                new_value[k] = v

    elif isinstance(value, list):
        new_value = [decode_strings(item) for item in value]
    elif isinstance(value, str):
        new_value = value.encode("utf-8")
    else:
        new_value = value
    return new_value


def make_infohashes(info: dict) -> dict[str, str]:
    encoded_infodict = bencode(info)
    ret = {}
    if b"pieces" in info:
        ret["infohash_v1"] = hashlib.sha1(encoded_infodict).hexdigest()
    if b"file tree" in info:
        ret["infohash_v2"] = hashlib.sha256(encoded_infodict).hexdigest()
    return ret


def encode_torrent(torrent: Path | bytes, with_context: bool = False) -> dict:
    """Encode a bencoded torrent to json"""
    data = torrent.read_bytes() if isinstance(torrent, Path) else torrent
    bdecoded = bdecode(data)
    encoded = encode_strings(bdecoded)
    encoded.update(make_infohashes(bdecoded[b"info"]))
    encoded["type"] = "Torrent"
    if with_context:
        encoded["@context"] = CONTEXT
    return encoded


def decode_json(value: Path | dict) -> bytes:
    """Decode json to bencoded binary"""
    data = json.loads(value.read_text()) if isinstance(value, Path) else value
    # remove infohashes
    data = {k: v for k, v in data.items() if k not in EXTRA_KEYS}
    decoded = decode_strings(data)
    return bencode(decoded)
