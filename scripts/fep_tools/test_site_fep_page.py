import pytest
from . import fep_file
from .site_fep_page import format_metatable, clean_markdown, transform_content


def skip_due_to_no_nh3_markdown():
    try:
        import nh3  # type: ignore  # noqa
        import markdown  # type: ignore  # noqa
    except Exception:
        return True
    return False


def test_format_metatable():
    file = fep_file.FepFile("a4ed")

    table = format_metatable(file)

    assert (
        table
        == """
| Authors | Status | Date received | Date final | Tracking issue | Discussions | Repository |
| --- | --- | --- | --- | --- | --- | --- |
| pukkamustard <pukkamustard@posteo.net> | `FINAL` | 2020-10-16 | 2021-01-18 | [#201](https://codeberg.org/fediverse/fep/issues/201) | - | [codeberg](https://codeberg.org/fediverse/fep/src/branch/main/fep/a4ed/fep-a4ed.md) |

"""
    )


@pytest.mark.skipif(
    skip_due_to_no_nh3_markdown(), reason="nh3 and markdown not installed"
)
@pytest.mark.parametrize(
    "text,expected",
    [
        ("[link](http://test.example)", "link"),
        ("[link][link]", "link"),
        ("[a][a] [b][b]", "a b"),
        ("a:b", "a b"),
    ],
)
def test_clean_markdown(text: str, expected: str):
    result = clean_markdown(text)
    assert result == expected


@pytest.mark.skipif(
    skip_due_to_no_nh3_markdown(), reason="nh3 and markdown not installed"
)
@pytest.mark.parametrize(
    "unchanged",
    [
        "[link](http://remote.tests)",
        "[fep-f1d5](https://codeberg.org/fediverse/fep/src/branch/main/fep/f1d5/fep-f1d5.md)",
        "[fep-f1d5]: https://codeberg.org/fediverse/fep/src/branch/main/fep/f1d5/fep-f1d5.md",
    ],
)
def test_content_unchanged(unchanged: str):
    assert transform_content(unchanged) == unchanged


@pytest.mark.skipif(
    skip_due_to_no_nh3_markdown(), reason="nh3 and markdown not installed"
)
def test_content():
    changed = "[link](../4adb/fep-4adb.md)"
    assert transform_content(changed) == "[link](../4adb/index.md)"

    changed = "[FEP-4adb]: ../4adb/fep-4adb.md"
    assert transform_content(changed) == "[FEP-4adb]: ../4adb/index.md"
