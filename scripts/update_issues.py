#!/usr/bin/env python

from tools import get_fep_ids, FepFile
from tools.issue import create_issue
import os


owner = os.environ.get("CI_REPO_OWNER")
repo = os.environ.get("CI_REPO_NAME")
token = os.environ.get("CODEBERG_API_TOKEN")

for slug in get_fep_ids():
    fep_file = FepFile(slug)
    tracking_issue = fep_file.parsed_frontmatter.get("trackingIssue")
    if not tracking_issue:
        print(slug, tracking_issue)

        create_issue(owner, repo, token, slug)