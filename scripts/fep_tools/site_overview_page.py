from . import index, table_for_feps

markdown_frontmatter = """---
hide:
- toc
- navigation
---
"""


def columns_for_status(status: str) -> list[str]:
    columns = [
        "title",
        "repo_link_image",
        "tracking_issue",
        "discussions",
        "date_received",
    ]
    if status == "FINAL":
        columns.append("date_finalized")
    elif status == "WITHDRAWN":
        columns.append("date_withdrawn")
    return columns


def write_overview_file(filename: str, status: str) -> None:
    columns = columns_for_status(status)
    feps = [x for x in index() if x.status == status]

    table = "".join(
        table_for_feps(feps, columns=columns, generate_title=True, format="static")
    )

    title = status[0] + status[1:].lower()

    with open(filename, "w") as f:
        f.write(markdown_frontmatter)
        f.write(f"\n# {title}\n")
        f.write(table)
