#!/usr/bin/python

from tools import Readme

with open("README.md", "w") as f1:
    f1.writelines(Readme().content)
