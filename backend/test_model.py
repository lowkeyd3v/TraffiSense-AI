from pathlib import Path
import joblib

# This must match main.py's MODEL_PATH ("model.joblib", loaded relative to
# the backend/ working directory). Training produces ../ml/model.joblib;
# both CI (see .github/workflows/*.yml) and the Render deploy build command
# (render.yaml) copy that file to backend/model.joblib before the app or
# this test runs, so this test exercises the exact file the running app
# loads rather than an intermediate training artifact.
MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"

def test_model_loads():
    model = joblib.load(MODEL_PATH)
    assert model is not None