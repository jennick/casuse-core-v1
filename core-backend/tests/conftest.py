"""
Pytest bootstrap: zorg dat 'core-backend' op sys.path staat wanneer we
pytest vanaf de repo-root draaien, zodat 'app.main' importeerbaar is.
"""
from pathlib import Path
import sys

# .../core-backend/tests -> parent is .../core-backend
CORE_BACKEND_DIR = Path(__file__).resolve().parent.parent

# Voeg toe aan sys.path als nog niet aanwezig
core_str = str(CORE_BACKEND_DIR)
if core_str not in sys.path:
    sys.path.insert(0, core_str)
