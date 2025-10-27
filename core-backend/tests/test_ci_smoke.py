# core-backend/tests/test_ci_smoke.py
import importlib

CANDIDATES = ["app.main", "core_backend.app.main", "main"]

def test_import_app_module():
    for name in CANDIDATES:
        try:
            mod = importlib.import_module(name)
            assert hasattr(mod, "app"), f"{name} imported but no 'app' attribute"
            return
        except ModuleNotFoundError:
            continue
    raise AssertionError(f"Geen app module gevonden. Geprobeerd: {CANDIDATES}")
