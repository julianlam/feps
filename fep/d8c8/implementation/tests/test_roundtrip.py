from pathlib import Path
import pytest
import json

from fepd8c8 import encode_torrent, decode_json

TMP_DIR = Path(__file__).parent / "__tmp__"


@pytest.mark.parametrize("context", [True, False])
def test_roundtrip(
    torrent_path: Path, context: bool, request: pytest.FixtureRequest, tmp_path: Path
):
    """We can roundtrip a torrent to and from JSON"""
    data = torrent_path.read_bytes()
    as_dict = encode_torrent(data, with_context=context)
    # ensure valid json
    as_json_str = json.dumps(as_dict, indent=2)
    # dump to path
    tmp_json = (tmp_path / torrent_path.name).with_suffix(".json")
    tmp_json.write_text(as_json_str)

    # write output to an inspectable directory if requested
    if request.config.getoption("--keep-output"):
        out_dir = TMP_DIR / "with_context" if context else TMP_DIR / "without_context"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = (out_dir / torrent_path.name).with_suffix(".json")
        out_path.write_text(as_json_str, encoding="utf-8")

    # invert back to bencoded form
    re_bencoded = decode_json(tmp_json)
    assert re_bencoded == data
