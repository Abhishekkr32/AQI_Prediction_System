import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "aqi_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "model_saved")
os.makedirs(MODEL_DIR, exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)

X = df[['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']]
y = df['AQI']

# Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Models
rf = RandomForestRegressor(n_estimators=150, random_state=42)
lr = LinearRegression()

# Train
rf.fit(X_train, y_train)
lr.fit(X_train, y_train)

# Evaluate
models = {
    "Random Forest": rf,
    "Linear Regression": lr
}

for name, model in models.items():
    preds = model.predict(X_test)
    print(f"\n{name}")
    print("MAE:", mean_absolute_error(y_test, preds))
    print("R2 :", r2_score(y_test, preds))

# Save models
joblib.dump(rf, os.path.join(MODEL_DIR, "rf_model.pkl"))
joblib.dump(lr, os.path.join(MODEL_DIR, "lr_model.pkl"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

print("\n✅ Models and scaler saved successfully")
