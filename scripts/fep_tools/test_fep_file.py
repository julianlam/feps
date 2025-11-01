from . import fep_file


def test_fep_file():
    file = fep_file.FepFile("a4ed")

    assert file.status == "FINAL"


def test_implementation_count():
    file = fep_file.FepFile("8b32")

    assert file.implementation_count > 2
