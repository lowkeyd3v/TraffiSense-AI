import os
from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_ml_folder_exists():
    assert os.path.exists(PROJECT_ROOT / "ml")

def test_model_loads():
    model_paths = [
        PROJECT_ROOT / "ml" / "model.joblib",
        PROJECT_ROOT / "backend" / "model.joblib",
    ]
    # At least one model artifact must exist and load successfully
    loaded = False
    for path in model_paths:
        if path.exists():
            model = joblib.load(path)
            assert model is not None
            loaded = True
    assert loaded, "Neither ml/model.joblib nor backend/model.joblib could be found."