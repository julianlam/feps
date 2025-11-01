from dataclasses import dataclass
import glob
import hashlib

from .fep_file import FepFile
from .table import table_for_feps


def title_to_slug(title: str):
    return hashlib.sha256(title.encode("utf-8")).hexdigest()[:4]


def get_fep_ids():
    for fep in glob.glob("fep/*"):
        yield fep.removeprefix("fep/")


def index():
    fep_files = [FepFile(fep) for fep in get_fep_ids()]
    fep_files = sorted(
        fep_files,
        key=lambda x: (
            x.parsed_frontmatter["dateReceived"],
            x.parsed_frontmatter["slug"],
        ),
    )
    return fep_files


@dataclass
class Readme:
    path_prefix: str = "./scripts/snippets"
    include_fep_table: bool = True

    @property
    def content(self):
        if self.include_fep_table:
            return (
                self.snippet("frontmatter_git")
                + self.snippet("frontmatter")
                + self.table
                + self.snippet("backmatter")
            )

        return self.snippet("frontmatter") + self.snippet("backmatter")

    def snippet(self, name: str):
        with open(f"{self.path_prefix}/{name}.md") as f:
            return f.readlines()

    @property
    def table(self):
        return self.snippet("fep_title") + table_for_feps(index())


def data_for_json_file() -> list[dict[str, str]]:
    result = []
    for fep in index():
        data = fep.parsed_frontmatter
        data["title"] = fep.title
        data["implementations"] = fep.implementation_count
        result.append(data)

    return result
