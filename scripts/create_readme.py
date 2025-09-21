#!/usr/bin/env python

import json

from tools import index, Readme

with open("README.md", "w") as f1:
    f1.writelines(Readme().content)

result = []
for fep in index():
    data = fep.parsed_frontmatter
    data["title"] = fep.title
    data["implementations"] = fep.implementations
    result.append(data)

with open("index.json", "w") as index_file:
    json.dump(result, index_file, indent=2)
