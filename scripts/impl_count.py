#!/usr/bin/env python

from tools import index

result = []
print("| Title | Status | Count |")
print("| ----- | ------ | ----- |")
for fep in index():
    slug = fep.parsed_frontmatter["slug"]
    status = fep.parsed_frontmatter["status"]
    typ = fep.parsed_frontmatter.get("type") or "-"
    if fep.implementations == 0:
        continue
    print(f"| [{fep.title}](https://codeberg.org/fediverse/fep/src/branch/main/fep/{slug}/fep-{slug}.md) | {status} | {fep.implementations} |")
