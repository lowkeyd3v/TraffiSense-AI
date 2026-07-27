import os
import joblib

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model.joblib"
)

model = joblib.load(MODEL_PATH)