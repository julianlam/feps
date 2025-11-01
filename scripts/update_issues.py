#!/usr/bin/env python

from fep_tools import get_fep_ids, FepFile
from fep_tools.issue import create_issue
import os


owner = os.environ.get("CI_REPO_OWNER")
repo = os.environ.get("CI_REPO_NAME")
token = os.environ.get("CODEBERG_API_TOKEN")

if not isinstance(owner, str):
    print("Please set the owner of the repostory at CI_REPO_OWNER")
    exit(1)

if not isinstance(repo, str):
    print("Please set the repository at CI_REPO_NAME")
    exit(1)

if not isinstance(token, str):
    print("Please provide a codeberg api token")
    exit(1)


for slug in get_fep_ids():
    fep_file = FepFile(slug)
    tracking_issue = fep_file.parsed_frontmatter.get("trackingIssue")
    if not tracking_issue:
        print(slug, tracking_issue)

        create_issue(owner, repo, token, slug)
