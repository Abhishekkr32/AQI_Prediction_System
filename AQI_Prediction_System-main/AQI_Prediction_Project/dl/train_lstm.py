import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("data/historical_aqi.csv")
aqi = df["AQI"].values.reshape(-1,1)

scaler = MinMaxScaler()
aqi_scaled = scaler.fit_transform(aqi)

X, y = [], []
for i in range(30, len(aqi_scaled)):
    X.append(aqi_scaled[i-30:i])
    y.append(aqi_scaled[i])

X, y = np.array(X), np.array(y)

model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X.shape[1],1)),
    LSTM(50),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=20)

model.save("dl/lstm_model.h5")
