from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model.joblib"

def test_model_loads():
    model = joblib.load(MODEL_PATH)
    assert model is not None