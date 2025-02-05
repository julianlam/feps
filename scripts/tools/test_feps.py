import datetime
import pytest

from urllib.parse import urlparse

from scripts.tools import get_fep_ids, FepFile, title_to_slug


@pytest.mark.parametrize("fep", get_fep_ids())
def test_fep_front_matter(fep):
    fep_file = FepFile(fep)
    parsed_frontmatter = fep_file.parsed_frontmatter

    assert "status" in parsed_frontmatter
    assert parsed_frontmatter["status"] in ["DRAFT", "FINAL", "WITHDRAWN"]
    assert parsed_frontmatter["slug"] == fep
    assert "authors" in parsed_frontmatter
    assert "dateReceived" in parsed_frontmatter
    assert "discussionsTo" in parsed_frontmatter

    discussions_to = parsed_frontmatter["discussionsTo"]

    assert not urlparse(discussions_to).netloc.endswith(
        ".example"
    ), "Update discussionsTo to a valid URL for a discussion topic"

    if parsed_frontmatter["status"] == "FINAL":
        assert "dateFinalized" in parsed_frontmatter
    if parsed_frontmatter["status"] == "WITHDRAWN":
        assert "dateWithdrawn" in parsed_frontmatter

    for field_name in ["dateReceived", "dateFinalized", "dateWithdrawn"]:
        if field_name in parsed_frontmatter:
            datetime.datetime.strptime(parsed_frontmatter[field_name], "%Y-%m-%d")

    if "type" in parsed_frontmatter:
        assert parsed_frontmatter["type"] in ["informational", "implementation"]

@pytest.mark.parametrize("fep", get_fep_ids())
def test_fep_content(fep):
    fep_file = FepFile(fep)

    content = fep_file.content

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
