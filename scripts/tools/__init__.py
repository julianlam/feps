import glob
import hashlib

from .fep_file import FepFile


def title_to_slug(title):
    return hashlib.sha256(title.encode("utf-8")).hexdigest()[:4]


def get_fep_ids():
    for fep in glob.glob("fep/*"):
        yield fep.removeprefix("fep/")


def build_url_link(url):
    url_number = url.split("/")[-1]
    return f"[#{url_number}]({url})"


def index():
    fep_files = [FepFile(fep) for fep in get_fep_ids()]
    fep_files = sorted(
        fep_files,
        key=lambda x: (x.parsed_frontmatter["dateReceived"], x.parsed_frontmatter["slug"]),
    )
    return fep_files


class Readme:
    @property
    def content(self):
        return self.frontmatter + self.table + self.backmatter

    @property
    def frontmatter(self):
        with open("scripts/frontmatter.md") as f:
            return f.readlines()

    @property
    def backmatter(self):
        with open("scripts/backmatter.md") as f:
            return f.readlines()

    @property
    def table(self):
        result = []

        for fep in index():
            link = f"[FEP-{fep.fep}: {fep.title}](./{fep.filename})"
            parsed = fep.parsed_frontmatter

            tracking_issue = build_url_link(parsed["trackingIssue"])

            if "dateFinalized" in parsed:
                date_final = parsed["dateFinalized"]
            elif "dateWithdrawn" in parsed:
                date_final = parsed["dateWithdrawn"]
            else:
                date_final = "-"
            result.append(
                f"""| {link} | `{parsed["status"]}` | {tracking_issue} | {parsed["dateReceived"]} | {date_final} |\n"""
            )
        return result
