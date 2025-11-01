from datetime import timedelta, date
from urllib.request import Request, urlopen
import json

from .fep_file import FepFile

DRAFT_FEP_LABEL = 149758


def create_body(filename: str, date_received: date):
    date1 = date_received.isoformat()
    date2 = (date_received + timedelta(days=365 * 2)).isoformat()

    body = f"""
The [proposal](https://codeberg.org/fediverse/fep/src/branch/main/{filename}) has been received. Thank you!

This issue tracks discussions and updates to the proposal during the `DRAFT` period.

Please post links to relevant discussions as comments to this issue.

`dateReceived`: {date1}

If no further actions are taken, the proposal will be set by the facilitators to `WITHDRAWN` on {date2} (in 2 years).
"""

    return body


def perform_post_request(url, token, body):
    request = Request(url)
    request.add_header("Content-Type", "application/json; charset=utf-8")

    request.add_header("authorization", f"Bearer {token}")
    request.add_header("Content-Length", str(len(body)))
    request.data = body

    response = urlopen(request)
    return json.loads(response.read())


def create_codeberg_issue(owner, repo, token, title, body):
    request_body = json.dumps(
        {"title": title, "body": body, "labels": [DRAFT_FEP_LABEL]}
    ).encode("utf-8")

    response = perform_post_request(
        f"https://codeberg.org/api/v1/repos/{owner}/{repo}/issues", token, request_body
    )

    issue_url = response["html_url"]
    issue_id = response["number"]

    return issue_url, issue_id


def parse_and_update_date_received(input_date: str) -> date:
    try:
        parsed = date.fromisoformat(input_date)

        if parsed < date.today() - timedelta(days=30):
            return date.today()

        return parsed
    except Exception:
        return date.today()


def update_fep_file_with_date_received(fep_file: FepFile, date_received: date):
    fep_file.frontmatter = [
        x for x in fep_file.frontmatter if not x.startswith("dateReceived")
    ]
    fep_file.frontmatter.append(f"dateReceived: {date_received.isoformat()}")


def create_issue(owner: str, repo: str, token: str, slug: str):
    fep_file = FepFile(slug)

    if "trackingIssue" in fep_file.parsed_frontmatter:
        print("File already has trackingIssue")
        exit(1)

    title = f"[TRACKING] FEP-{slug}: {fep_file.title}"

    date_received = parse_and_update_date_received(
        fep_file.parsed_frontmatter["dateReceived"]
    )
    update_fep_file_with_date_received(fep_file, date_received)
    discussions_to = fep_file.parsed_frontmatter["discussionsTo"]

    body = create_body(fep_file.filename, date_received)
    issue_url, issue_id = create_codeberg_issue(owner, repo, token, title, body)

    body_comment = f"Discussions: {discussions_to}"
    issue_body = json.dumps({"body": body_comment}).encode("utf-8")
    perform_post_request(
        f"https://codeberg.org/api/v1/repos/{owner}/{repo}/issues/{issue_id}/comments",
        token,
        issue_body,
    )

    fep_file.frontmatter.append(f"trackingIssue: {issue_url}")

    fep_file.write()

    print(f"Issue url: {issue_url} for {title}")
