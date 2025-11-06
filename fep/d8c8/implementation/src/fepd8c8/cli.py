from argparse import ArgumentParser
from pathlib import Path
import json

from fepd8c8.torrent import encode_torrent, decode_json


def parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="fepd8c8",
        description="Encoding and decoding torrents to ActivityStreams Torrent objects.",
    )
    parser.add_argument(
        "--encode", help="Encode a .torrent file to JSON", action="store_true"
    )
    parser.add_argument(
        "--decode", help="Decode a JSON torrent object to .torrent", action="store_true"
    )
    parser.add_argument(
        "--with-context",
        help="Include the JSON-LD Context in the json output",
        action="store_true",
    )
    parser.add_argument(
        "-i", "--input", help="path to input .torrent or JSON file", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="path to write output to. If not provided, print to stdout",
    )
    return parser


def main():
    args = parser().parse_args()
    in_path = Path(args.input)
    if args.encode:
        val = encode_torrent(in_path, with_context=args.with_context)
    elif args.decode:
        val = decode_json(in_path)
    else:
        raise ValueError("Must specify whether decoding or encoding")

    if args.output:
        out_path = Path(args.output)
        if args.encode:
            with open(out_path, "w") as f:
                json.dump(val, f, indent=2)
        else:
            out_path.write_bytes(val)
    else:
        print(val)
