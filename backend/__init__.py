import json

with open("package.json") as f:
    package = json.load(f)

__version__ = package["version"]
