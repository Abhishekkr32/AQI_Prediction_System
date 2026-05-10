import joblib
import os

def load_model():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base, "model_saved", "aqi_model.pkl")
    return joblib.load(model_path)
