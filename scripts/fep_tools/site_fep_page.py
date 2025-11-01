import re
import shutil
from pathlib import Path

try:
    import nh3
    from markdown import markdown
except Exception:
    ...

from .fep_file import FepFile
from .table import TableLineBuilder


def transform_key(x: str) -> str:
    if x in ["dateReceived", "dateWithdrawn", "trackingIssue"]:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", x).lower()
    if x == "dateFinalized":
        return "date_final"
    if x == "discussionsTo":
        return "discussions"
    return x


possible_matter_keys = [
    "authors",
    "status",
    "type",
    "date_received",
    "date_final",
    "date_withdrawn",
    "tracking_issue",
    "discussions",
    "repository",
]


def format_metatable(fep: FepFile) -> str:
    """Creates a markdown table containing FEP metadata"""
    matter_keys = [transform_key(x) for x in fep.parsed_frontmatter.keys()]
    matter_keys = [x for x in possible_matter_keys if x in matter_keys] + ["repository"]

    line_builder = TableLineBuilder(fep=fep, columns=list(matter_keys))
    keys = " | ".join(x.replace("_", " ").capitalize() for x in matter_keys)
    values = line_builder.line

    divider = " | ".join(["---"] * len(matter_keys))

    return f"""
| {keys} |
| {divider} |
{values}
"""


def clean_markdown(text: str) -> str:
    """Transforms markdown to a plain text string. To be used in the frontmatter"""
    transformed = nh3.clean(markdown(text), tags=set())
    transformed = re.sub(r"\[(.+?)\]\[(.+?)\]", r"\1", transformed)
    transformed = transformed.replace(
        ":", " "
    )  # See https://codeberg.org/fediverse/fep/pulls/673/files#issuecomment-7514311
    return transformed.replace("\n", " ")


def frontmatter_for_fep(fep: FepFile) -> str:
    summary = fep.summary
    if summary is None:
        return """---
hide:
  - navigation
---

"""
    description = clean_markdown(summary)

    return f"""---
hide:
  - navigation
description: {description}
---

"""


def transform_content(content: str) -> str:
    """Transforms links to other FEPs. These need to be adjusted due to
    the renaming of `fep-slug.md` to `index.md`."""
    content = re.sub(
        r"\[(.+?)\]\((\.\./.+)/fep-(.+).md\)", r"[\1](\2/index.md)", content
    )
    content = re.sub(r"\[(.+?)\]: (\.\./.+)/fep-(.+).md", r"[\1]: \2/index.md", content)
    return content


def fep_to_site_mkdocs(fep: FepFile) -> str:
    """Transforms the FEP to markdown suitable for publishing as a static website"""
    title, content = fep.content_and_title()

    file_content = (
        frontmatter_for_fep(fep)
        + title
        + "\n\n"
        + format_metatable(fep)
        + "\n\n"
        + transform_content(content)
    )

    return file_content


def make_page_for_fep(fep: FepFile):
    """Copies relevant files for the FEP and adjusts index.md"""
    slug = fep.fep

    base_path = f"scripts/docs/fep/{slug}/"
    Path(base_path).mkdir(exist_ok=True, parents=True)

    shutil.rmtree(base_path)
    shutil.copytree(f"fep/{slug}/", base_path)
    shutil.move(f"{base_path}/fep-{slug}.md", f"{base_path}/index.md")

    with open(f"{base_path}/index.md", "w") as fp:
        fp.write(fep_to_site_mkdocs(fep))
