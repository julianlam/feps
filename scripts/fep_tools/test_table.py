from .fep_file import FepFile

from .table import table_for_feps, TableTitle


def test_table_for_feps():
    fep = FepFile("a4ed")
    result = table_for_feps([fep])

    assert len(result) == 1
    line = result[0]

    assert (
        line
        == "| [FEP-a4ed: The Fediverse Enhancement Proposal Process](./fep/a4ed/fep-a4ed.md) | `FINAL` | [#201](https://codeberg.org/fediverse/fep/issues/201) | 2020-10-16 | 2021-01-18 |\n"
    )


def test_table_title():
    columns = [
        "title",
        "tracking_issue",
        "discussions",
        "date_received",
        "date_final",
    ]

    result = TableTitle(columns).result

    assert result == [
        "| Title | Tracking issue | Discussions | Received | Finalized / Withdrawn |\n",
        "| --- | --- | --- | --- | --- |\n",
    ]
