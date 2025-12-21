import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import requests
import plotly.express as px
from folium import Map, CircleMarker
from streamlit_folium import st_folium


# ------------ CONFIG ------------
st.set_page_config("AQI Prediction System", "🌍", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_saved", "aqi_model.pkl")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATA_FILE = os.path.join(BASE_DIR, "data", "aqi_data.csv")

model = joblib.load(MODEL_PATH)

WAQI_TOKEN = "34680606302d3d4588d8ee4c856b2bd7669f04aa"


# ------------ USER AUTH ------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "map_obj" not in st.session_state:
    st.session_state.map_obj = None


# ------------ AUTH PAGE ------------
def auth_page():
    st.title("🔐 Login / Register")
    users = load_users()
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Wrong username/password")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Register"):
            if u in users:
                st.warning("User Exists")
            elif u and p:
                users[u] = p
                save_users(users)
                st.success("Registered! Login Now.")
            else:
                st.error("Fields Required")


# ------------ AQI CATEGORY ------------
def aqi_category(aqi):
    if aqi <= 50: return "Good 🟢"
    elif aqi <= 100: return "Moderate 🟡"
    elif aqi <= 200: return "Unhealthy 🟠"
    elif aqi <= 300: return "Very Unhealthy 🔴"
    return "Hazardous ⚫"


def get_color(aqi):
    if aqi <= 50: return "green"
    elif aqi <= 100: return "yellow"
    elif aqi <= 200: return "orange"
    elif aqi <= 300: return "red"
    return "purple"


# ------------ PREDICTION PAGE ------------
def aqi_predict_page():
    st.header("🔮 AQI Prediction")
    pm25 = st.number_input("PM2.5", 0.0)
    pm10 = st.number_input("PM10", 0.0)
    no2 = st.number_input("NO2", 0.0)
    so2 = st.number_input("SO2", 0.0)
    co = st.number_input("CO", 0.0)
    o3 = st.number_input("O3", 0.0)

    if st.button("Predict AQI"):
        data = np.array([[pm25, pm10, no2, so2, co, o3]])
        pred = model.predict(data)[0]
        st.metric("Predicted AQI", int(pred))
        st.success(aqi_category(pred))


# ------------ BULK PREDICTION ------------
def bulk_page():
    st.header("📂 Bulk AQI Prediction")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        df = pd.read_csv(file)
        df["Predicted_AQI"] = model.predict(df[['PM2.5','PM10','NO2','SO2','CO','O3']])
        st.dataframe(df)


# ------------ ANALYTICS ------------
def analytics_page():
    st.header("📊 AQI Analytics Dashboard")
    df = pd.read_csv(DATA_FILE)

    col1,col2 = st.columns(2)
    with col1:
        st.subheader("AQI Distribution")
        fig = px.histogram(df, x="AQI")
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        st.subheader("City Wise AQI Trend")
        if "City" in df.columns:
            fig = px.box(df, x="City", y="AQI")
            st.plotly_chart(fig,use_container_width=True)


# ------------ LIVE AQI (WAQI Accurate API) ------------
def live_aqi_page():
    st.header("🌍 Live AQI (Highly Accurate - WAQI)")
    city = st.text_input("Enter City", "Delhi")

    if st.button("Get Live AQI"):
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
        res = requests.get(url).json()

        if res["status"] != "ok":
            st.error("City not found / API Error")
            st.json(res)
            return

        aqi = res["data"]["aqi"]
        st.metric("Live AQI", aqi)
        st.success(aqi_category(aqi))

        st.subheader("API Response")
        st.json(res)


# ------------ MAP AQI ------------
def map_aqi_page():
    st.header("🗺️ AQI World Map")

    city = st.text_input("Enter City For Map", "Delhi")

    if st.button("Show AQI on Map"):
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
        res = requests.get(url).json()

        if res["status"] != "ok":
            st.error("City Not Found")
            return

        lat = res["data"]["city"]["geo"][0]
        lon = res["data"]["city"]["geo"][1]
        aqi = res["data"]["aqi"]

        m = Map(location=[lat, lon], zoom_start=8)

        CircleMarker(
            location=[lat, lon],
            radius=15,
            tooltip=f"{city} | AQI: {aqi}",
            color=get_color(aqi),
            fill=True,
            fill_color=get_color(aqi)
        ).add_to(m)

        st.session_state.map_obj = m

    if st.session_state.map_obj:
        st_folium(st.session_state.map_obj, width=900, height=500)


# ------------ MAIN APP ------------
def main_app():
    st.sidebar.title(f"👋 Welcome {st.session_state.username}")

    page = st.sidebar.radio("Navigation",
                            ["AQI Prediction","Live AQI","Bulk CSV","Analytics","Map AQI","Logout"])

    if page == "AQI Prediction": aqi_predict_page()
    elif page == "Live AQI": live_aqi_page()
    elif page == "Bulk CSV": bulk_page()
    elif page == "Analytics": analytics_page()
    elif page == "Map AQI": map_aqi_page()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()


# ------------ ROUTER ------------
if not st.session_state.logged_in:
    auth_page()
else:
    main_app()
