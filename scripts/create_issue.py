#!/usr/bin/env python

from argparse import ArgumentParser
from fep_tools.issue import create_issue

import json

parser = ArgumentParser("Create tracking issue for FEP")
parser.add_argument("fep", help="slug of the FEP")
args = parser.parse_args()

with open("scripts/config.json") as f:
    config = json.load(f)

create_issue(config["owner"], config["repo"], config["token"], args.fep)
