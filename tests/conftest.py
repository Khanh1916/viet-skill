import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for scripts in sorted((ROOT / "skills").glob("*/scripts")):
    sys.path.insert(0, str(scripts))
