import sys
from pathlib import Path
PROJECT_PATH = Path(__file__).parents[1].resolve()
sys.path.insert(0, str(PROJECT_PATH))

from astroapiserver.app import app

if __name__ == "__main__":
    app.run(port=8080, debug=True)