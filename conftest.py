"""Make the repo root importable for the test suite.

`python -m pytest` prepends the working directory to sys.path; the bare
`pytest` console script does not. Without this, `from app.schemas import ...`
resolves under one invocation and raises ModuleNotFoundError under the other —
which is exactly how CI failed while local runs passed.

pytest imports the rootdir conftest before collecting, so putting the path
fix here makes both invocations behave the same on every pytest version.
"""

import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
