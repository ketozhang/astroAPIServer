from pathlib import Path
import json
import yaml

PROJECT_PATH = Path.cwd()

with open(PROJECT_PATH / "config.yml") as f:
    CONFIG = yaml.safe_load(f)
    if not CONFIG:
        CONFIG = {}

with open(PROJECT_PATH / 'env.json') as f:
    ENV = json.load(f)
    if not ENV:
        ENV = {}

JWT_SECRET = ENV["JWT_SECRET"]
JWT_EXP = CONFIG.get("JWT_EXP", None)
JWT_ALGORITHM = CONFIG.get("JWT_ALGORITHM", "HS256")