from dataclasses import dataclass

from .fep_file import FepFile


repo_base = "https://codeberg.org/fediverse/fep/src/branch/main/"


@dataclass
class TableLineBuilder:
    fep: FepFile
    columns: list[str]
    format: str = "readme"

    @property
    def parsed(self):
        return self.fep.parsed_frontmatter

    @property
    def title(self):
        if self.format == "readme":
            return f"[FEP-{self.fep.fep}: {self.fep.title}](./{self.fep.filename})"

        return f"[FEP-{self.fep.fep}: {self.fep.title}](fep/{self.fep.fep}/index.md)"

    @property
    def repo_link_image(self):
        return f"[<img src='../assets/codeberg.png' width=20 height=20 alt='codeberg'>]({repo_base}{self.fep.filename})"

    @property
    def tracking_issue(self):
        url = self.parsed.get("trackingIssue")
        if url is None:
            return "-"
        url_number = url.split("/")[-1]
        return f"[#{url_number}]({url})"

    @property
    def status(self):
        status = self.parsed["status"]
        return f"`{status}`"

    @property
    def date_received(self):
        return self.parsed.get("dateReceived", "-")

    @property
    def date_finalized(self):
        return self.parsed.get("dateFinalized", "-")

    @property
    def date_withdrawn(self):
        return self.parsed.get("dateWithdrawn", "-")

    @property
    def date_final(self):
        if "dateFinalized" in self.parsed:
            return self.parsed["dateFinalized"]
        if "dateWithdrawn" in self.parsed:
            return self.parsed["dateWithdrawn"]
        return "-"

    @property
    def discussions(self):
        discussions = self.parsed["discussionsTo"]

        if discussions == self.parsed.get("trackingIssue"):
            return "-"

        return f"[Discussions]({discussions})"

    @property
    def repository(self) -> str:
        url = f"{repo_base}fep/{self.fep.fep}/fep-{self.fep.fep}.md"
        return f"[codeberg]({url})"

    def get_attribute(self, column: str):
        try:
            return self.__getattribute__(column)
        except AttributeError:
            return self.parsed.get(column, "-")

    @property
    def line(self) -> str:
        values = [self.get_attribute(column) for column in self.columns]
        middle = " | ".join(values)
        return f"| {middle} |\n"


@dataclass
class TableTitle:
    columns: list[str]

    column_to_title = {
        "title": "Title",
        "status": "Status",
        "tracking_issue": "Tracking issue",
        "discussions": "Discussions",
        "date_received": "Received",
        "date_final": "Finalized / Withdrawn",
        "date_finalized": "Finalized",
        "date_withdrawn": "Withdrawn",
    }

    @property
    def title_line(self):
        center = " | ".join(
            [self.column_to_title.get(column, "") for column in self.columns]
        )

        return f"| {center} |\n"

    @property
    def second_line(self):
        center = " | ".join(["---"] * len(self.columns))
        return f"| {center} |\n"

    @property
    def result(self) -> list[str]:
        return [self.title_line, self.second_line]


def table_for_feps(
    feps: list[FepFile],
    columns: list[str] = [
        "title",
        "status",
        "tracking_issue",
        "date_received",
        # Finalized / Withdrawn
        "date_final",
    ],
    generate_title: bool = False,
    format: str = "readme",
):
    lines = [TableLineBuilder(fep, columns, format=format).line for fep in feps]
    if generate_title:
        return TableTitle(columns).result + lines

    return lines
