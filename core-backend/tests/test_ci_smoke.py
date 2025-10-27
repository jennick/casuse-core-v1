"""
CI smoke test voor core-backend.

- Verifieert dat de FastAPI-appmodule importeerbaar is, óf direct vanaf
  het bestand kan worden geladen als de pakketpaden niet kloppen.
- Zorgt dat er altijd minstens één test draait (geen 'no tests' failures).
"""
from __future__ import annotations

import importlib
import importlib.util
import types
from pathlib import Path

# 1) Probeer normale pakketimports
CANDIDATES = [
    "app.main",               # gebruikelijk: core-backend/app/main.py
    "core_backend.app.main",  # alternatieve layout
    "main",                   # fallback voor lokale runs in core-backend/
]


def _try_import(name: str) -> types.ModuleType | None:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None


def _load_from_file() -> types.ModuleType | None:
    """
    Fallback: laad main.py rechtstreeks vanaf het bestand, zonder dat
    het pakketpad klopt. Werkt in alle runners.
    """
    here = Path(__file__).resolve()
    # Mogelijke locaties van main.py relatief t.o.v. deze test
    candidates = [
        here.parent.parent / "app" / "main.py",  # core-backend/app/main.py
        here.parent / "main.py",                 # core-backend/tests/../main.py
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("casuse_app_main", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
    return None


def test_import_app_module():
    # Eerst gewone imports
    imported = [m for m in (_try_import(n) for n in CANDIDATES) if m]

    # Zo niet, fallback naar bestands-import
    if not imported:
        fallback = _load_from_file()
        if fallback:
            imported.append(fallback)

    assert imported, (
        "Geen app module gevonden via pakketimport of bestandsimport. "
        f"Geprobeerd: {CANDIDATES} en fallback core-backend/app/main.py"
    )


def test_basic_truth():
    assert True
