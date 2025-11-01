#!/usr/bin/env python

from fep_tools import index
from fep_tools.site_fep_page import make_page_for_fep
from fep_tools.site_overview_page import write_overview_file

from fep_tools import Readme

path_prefix = "scripts/docs"

with open(f"{path_prefix}/index.md", "w") as fp:
    fp.write("""---
hide:
- navigation
---

# Fediverse Enhancement Proposals
 
<div class="grid cards" markdown>

- [:material-file-document: Final Proposals](./final.md)
- [:material-file-document-edit: Draft Proposals](./draft.md)

</div>
             
""")

    fp.writelines(Readme(include_fep_table=False).content)


for file, status in [
    ("index.html", "FINAL"),
    ("draft.html", "DRAFT"),
    ("withdrawn.html", "WITHDRAWN"),
]:
    filename = f"{path_prefix}/{status.lower()}.md"

    write_overview_file(filename, status)


for fep in index():
    make_page_for_fep(fep)
