import datetime
import pytest

from scripts.tools import get_fep_ids, FepFile, title_to_slug


@pytest.mark.parametrize("fep", get_fep_ids())
def test_fep(fep):
    fep_file = FepFile(fep)

    content = fep_file.content
    parsed_frontmatter = fep_file.parsed_frontmatter

    assert "status" in parsed_frontmatter
    assert parsed_frontmatter["status"] in ["DRAFT", "FINAL", "WITHDRAWN"]
    assert parsed_frontmatter["slug"] == f'"{fep}"'
    assert "authors" in parsed_frontmatter

    if parsed_frontmatter["status"] == "FINAL":
        assert "dateFinalized" in parsed_frontmatter
    if parsed_frontmatter["status"] == "WITHDRAWN":
        assert "dateWithdrawn" in parsed_frontmatter

    for field_name in ["dateReceived", "dateFinalized", "dateWithdrawn"]:
        if field_name in parsed_frontmatter:
            datetime.datetime.strptime(parsed_frontmatter[field_name], "%Y-%m-%d")

    assert "## Summary" in content
    assert "## Copyright" in content

    titles = [x for x in content if x.startswith("# ")]
    assert len(titles) > 0

    title = titles[0]

    begin_title = f"# FEP-{fep}: "

    assert title.startswith(begin_title)
    true_title = title.removeprefix(begin_title)

    expected_slug = title_to_slug(true_title)

    assert expected_slug == fep
