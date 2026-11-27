"""The `moriarty` command.

The `ship` and `holodeck` workspace members are virtual: they import from the repo root, which a
console script does not have on `sys.path`. The CLI is installed editable from the workspace, so
the repo root is two levels above this file; put it on the path before anything imports `ship`.
"""

import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
