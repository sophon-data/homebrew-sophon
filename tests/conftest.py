"""Make the libexec package importable for tests."""

import sys
from pathlib import Path

LIBEXEC = Path(__file__).resolve().parent.parent / "libexec"
if str(LIBEXEC) not in sys.path:
    sys.path.insert(0, str(LIBEXEC))
