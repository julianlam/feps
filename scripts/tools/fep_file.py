def unquote(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    else:
        return value


class FepFile:
    def __init__(self, fep):
        self.fep = fep
        with open(self.filename) as f:
            self.frontmatter, self.content = FepFile.parsefile(f)

    @property
    def filename(self):
        return f"fep/{self.fep}/fep-{self.fep}.md"

    @property
    def summary(self):
        result = []
        is_summary = False
        for x in self.content:
            if is_summary:
                if x.startswith("##"):
                    return "\n".join(result)
                result.append(x)
            elif x == "## Summary":
                is_summary = True

    def write(self):
        with open(self.filename, "w") as f:
            f.write("---\n")
            for x in self.frontmatter:
                f.write(x + "\n")
            f.write("---\n")
            for x in self.content:
                f.write(x + "\n")

    @property
    def parsed_frontmatter(self):
        split = [x.split(":", 1) for x in self.frontmatter]
        return {a: unquote(b.strip()) for a, b in split}

    @property
    def title(self):
        titles = [x for x in self.content if x.startswith("# ")]
        assert len(titles) > 0

        title = titles[0]

        begin_title = f"# FEP-{self.fep}: "

        assert title.startswith(begin_title)
        true_title = title.removeprefix(begin_title)

        return true_title

    @property
    def implementations(self):
        if self.parsed_frontmatter.get("type") != "implementation":
            return 0
        implementations = []
        in_section = False
        for line in self.content:
            if line.startswith('#') and "Implementations" in line:
                in_section = True
            elif in_section is True and line.startswith('#'):
                in_section = False
            elif (
                in_section is True
                and (line.startswith("-") or line.startswith("*"))
            ):
                implementations.append(line)
        return len(implementations)

    @staticmethod
    def parsefile(f):
        lines = f.readlines()

        status = 0
        frontmatter = []
        content = []

        for line in lines:
            if line == "---\n" and status <= 2:
                status += 1
            elif status == 1:
                frontmatter.append(line.removesuffix("\n"))
            elif status >= 2:
                content.append(line.removesuffix("\n"))

        return frontmatter, content
