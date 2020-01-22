from pathlib import Path
import json
import yaml

PROJECT_PATH = Path.cwd()

try:
    with open(PROJECT_PATH / "config.yml") as f:
        CONFIG = yaml.safe_load(f)
except FileNotFoundError:
    CONFIG = {}

try:
    with open(PROJECT_PATH / "env.json") as f:
        ENV = json.load(f)
except FileNotFoundError:
    print("`env.json` not found, ENV will not be set")
    print("ENV PATH", PROJECT_PATH / "env.json")
    ENV = {}
