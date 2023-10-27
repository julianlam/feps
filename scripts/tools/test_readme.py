import pytest

from scripts.tools import Readme


@pytest.mark.skip("Only is correct for main branch and not pull requests")
def test_readme():
    with open("README.md") as f:
        lines = f.readlines()

    expected = Readme().content

    assert lines == expected
