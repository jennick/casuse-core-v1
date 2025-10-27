# core-backend/tests/conftest.py
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
CORE = ROOT / "core-backend"

for p in (str(ROOT), str(CORE)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Optioneel: assert dat het importpad werkt; zo niet, duidelijke fout
try:
    __import__("app.main")
except Exception as exc:
    raise RuntimeError(
        f"Kon 'app.main' niet importeren; sys.path={sys.path[:5]}"
    ) from exc
