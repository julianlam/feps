# FEP d8c8 Reference Implementation

## Usage

Install the package with `python -m pip install .`

Use the CLI `fepd8c8`, call `fepd8c8 --help` for usage instructions

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

## Testing

To validate that we can roundtrip a torrent to/from the JSON representation, 

- install with the optional `test` dependency group: `python -m pip install '.[test]'`
- call pytest with a `--torrentdir ./some/directory` argument 
  that points to a directory with .torrent files to roundtrip
- Optionally: call with `--keep-output` to inspect the created json files


## See Also

[`torrent-models`](https://pypi.org/project/torrent-models/) - 
a more complete implementation of .torrent files in python