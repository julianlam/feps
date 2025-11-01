#!/usr/bin/env python

import json

from fep_tools import data_for_json_file, Readme

with open("README.md", "w") as f1:
    f1.writelines(Readme().content)


with open("index.json", "w") as index_file:
    json.dump(data_for_json_file(), index_file, indent=2)
