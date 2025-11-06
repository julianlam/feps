import pytest
import warnings
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption(
        "--torrentdir",
        help="directory of torrent files to roundtrip",
        action="store",
        default=None,
    )
    parser.addoption(
        "--keep-output", help="Keep temporary JSON files", action="store_true"
    )


def pytest_generate_tests(metafunc):
    if "torrent_path" in metafunc.fixturenames:
        torrent_dir = metafunc.config.getoption("torrentdir")
        if not torrent_dir:
            warnings.warn("No torrent-dir passed, no torrents will be tested!")
        else:
            torrents = list(Path(torrent_dir).rglob("**/*.torrent"))
            metafunc.parametrize("torrent_path", torrents)
