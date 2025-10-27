"""
Pytest bootstrap:
- Voeg 'core-backend' toe aan sys.path zodat 'app.main' importeerbaar is
  wanneer pytest vanaf de repo-root draait.
"""
from pathlib import Path
import sys

TESTS_DIR = Path(__file__).resolve().parent
CORE_BACKEND_DIR = TESTS_DIR.parent  # .../core-backend

core_str = str(CORE_BACKEND_DIR)
if core_str not in sys.path:
    sys.path.insert(0, core_str)
