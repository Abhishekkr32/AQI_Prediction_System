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


# ------------ USER AUTH UTILS ------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ------------ SESSION STATES ------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "map_obj" not in st.session_state: st.session_state.map_obj = None


# ================= AUTH PAGE =================
def set_auth_background():
    image_url = "https://images.pexels.com/photos/16512021/pexels-photo-16512021.jpeg?cs=srgb&dl=pexels-akhil-gautam-16512021.jpg&fm=jpg"

    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .block-container {{
        background: rgba(0,0,0,0.55);
        padding: 2rem;
        border-radius: 12px;
    }}

    label, p, h1, h2, h3, span {{
        color: white !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def auth_page():
    set_auth_background()
    st.title("🔐 Login / Register")

    users = load_users()     # <<< FIXED (now users exists)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # -------- LOGIN --------
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Wrong username or password ❌")

    # -------- REGISTER --------
    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Register"):
            if u in users:
                st.warning("User already exists ⚠️")
            elif u and p:
                users[u] = p
                save_users(users)
                st.success("Registered successfully 🎉 Please login.")
            else:
                st.error("All fields are required")


# ------------ HELPERS ------------
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


# ------------ AQI PREDICTION ------------
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

    col1, col2 = st.columns(2)

    # ---------------- Histogram ----------------
    with col1:
        st.subheader("AQI Distribution Range")

        fig = px.histogram(
            df,
            x="AQI",
            nbins=40,
            color_discrete_sequence=["#636EFA"],
            title="AQI Frequency Distribution"
        )

        fig.update_layout(
            bargap=0.05,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=13)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Box Plot ----------------
    with col2:
        st.subheader("City Wise AQI Spread")

        if "City" in df.columns:
            fig2 = px.box(
                df,
                x="City",
                y="AQI",
                points="all",
                color_discrete_sequence=["#EF553B"],
                title="AQI Spread Across Cities"
            )

            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig2, use_container_width=True)

    # ---------------- Trend Line ----------------
    st.subheader("📈 AQI Line Trend (If Timestamp Available)")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        fig3 = px.line(
            df.sort_values("Date"),
            x="Date",
            y="AQI",
            title="AQI Over Time",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Date column not found — trend visualization skipped ❕")

# ------------ LIVE AQI ------------
def live_aqi_page():
    st.header("🌍 Live Real-Time AQI Dashboard")
    st.write("Get highly accurate air quality monitoring with live weather details.")

    if "live_data" not in st.session_state:
        st.session_state.live_data = None

    city = st.text_input("Enter City", "Delhi")

    if st.button("Fetch Live AQI"):
        try:
            url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
            res = requests.get(url).json()

            if res["status"] != "ok":
                st.error("❌ City not found or API problem")
                st.json(res)
                return

            st.session_state.live_data = res["data"]
            st.success("✅ Live AQI Fetched Successfully")

        except Exception as e:
            st.error("Unexpected Error")
            st.write(e)

    # ---------------- SHOW DATA (PERSISTENT) ----------------
    if st.session_state.live_data:

        data = st.session_state.live_data
        aqi = data["aqi"]

        # ---------- AQI Meaning ----------
        def aqi_status(aqi):
            if aqi <= 50: return "Good 🟢", "Air quality is excellent."
            elif aqi <= 100: return "Moderate 🟡", "Acceptable air quality."
            elif aqi <= 200: return "Unhealthy 🟠", "Unhealthy for sensitive groups."
            elif aqi <= 300: return "Very Unhealthy 🔴", "Everyone may feel health effects."
            return "Hazardous ⚫", "Serious health risk."

        status, desc = aqi_status(aqi)

        # ---------- TOP SUMMARY ----------
        st.subheader(f"📍 Location: {data['city']['name']}")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current AQI", aqi)

        with col2:
            st.metric("Status", status)

        with col3:
            st.warning(desc)

        st.markdown("---")

        # ---------- POLLUTANT DETAILS ----------
        st.subheader("💨 Pollutant Breakdown")
        iaqi = data.get("iaqi", {})

        pollutants = {
            "pm25": "PM2.5",
            "pm10": "PM10",
            "no2": "Nitrogen Dioxide",
            "so2": "Sulphur Dioxide",
            "o3": "Ozone",
            "co": "Carbon Monoxide"
        }

        poll_values = {}
        for key, label in pollutants.items():
            if key in iaqi:
                poll_values[label] = iaqi[key]["v"]

        if poll_values:
            df = pd.DataFrame({
                "Pollutant": list(poll_values.keys()),
                "Value": list(poll_values.values())
            })

            st.dataframe(df, use_container_width=True)

            fig = px.bar(
                df,
                x="Pollutant",
                y="Value",
                title="Pollution Levels",
                color="Value",
                color_continuous_scale="Turbo"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No detailed pollutant data available")

        # ---------- WEATHER INFO ----------
        st.markdown("---")
        st.subheader("🌦 Weather Information")

        if "iaqi" in data and "t" in data["iaqi"]:
            temp = data["iaqi"]["t"]["v"]
        else:
            temp = "N/A"

        if "h" in iaqi:
            humidity = iaqi["h"]["v"]
        else:
            humidity = "N/A"

        colw1, colw2 = st.columns(2)
        with colw1:
            st.metric("Temperature", f"{temp} °C")
        with colw2:
            st.metric("Humidity", f"{humidity}%")

        # ---------- EXTRA INFO ----------
        st.markdown("---")
        st.info("🔎 Data Source: World Air Quality Index (WAQI) — Highly Reliable API")


# ------------ MAP AQI ------------
def map_aqi_page():
    st.header("🗺️ Advanced Map Based AQI Monitoring")

    city = st.text_input("Enter City", "Delhi")

    if "map_data" not in st.session_state:
        st.session_state.map_data = None

    if st.button("Show AQI on Map"):
        try:
            url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
            res = requests.get(url).json()

            if res["status"] != "ok":
                st.error("City Not Found / API Error")
                return

            data = res["data"]
            aqi = data["aqi"]
            city_name = data["city"]["name"]
            lat = data["city"]["geo"][0]
            lon = data["city"]["geo"][1]

            # Weather + Pollutants
            iaqi = data.get("iaqi", {})
            pm25 = iaqi.get("pm25", {}).get("v", "N/A")
            pm10 = iaqi.get("pm10", {}).get("v", "N/A")
            no2 = iaqi.get("no2", {}).get("v", "N/A")
            so2 = iaqi.get("so2", {}).get("v", "N/A")
            o3 = iaqi.get("o3", {}).get("v", "N/A")
            temp = iaqi.get("t", {}).get("v", "N/A")
            humidity = iaqi.get("h", {}).get("v", "N/A")

            # Save everything
            st.session_state.map_data = {
                "city": city_name,
                "aqi": aqi,
                "lat": lat,
                "lon": lon,
                "pm25": pm25,
                "pm10": pm10,
                "no2": no2,
                "so2": so2,
                "o3": o3,
                "temp": temp,
                "humidity": humidity
            }

        except Exception as e:
            st.error("Something went wrong")
            st.write(e)

    # ---------- SHOW MAP + DETAILS (PERSIST) ----------
    if st.session_state.map_data:
        data = st.session_state.map_data

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🌍 Location Details")
            st.write(f"**City:** {data['city']}")
            st.write(f"**Latitude:** {data['lat']}")
            st.write(f"**Longitude:** {data['lon']}")

            st.subheader("💨 AQI Information")
            st.metric("AQI Value", data["aqi"])
            st.write(f"Status: **{aqi_category(data['aqi'])}**")

        with col2:
            st.subheader("🌡 Weather & Pollutants")
            st.write(f"PM2.5: **{data['pm25']}** µg/m³")
            st.write(f"PM10: **{data['pm10']}** µg/m³")
            st.write(f"NO₂: **{data['no2']}** µg/m³")
            st.write(f"SO₂: **{data['so2']}** µg/m³")
            st.write(f"O₃: **{data['o3']}** µg/m³")
            st.write(f"Temperature: **{data['temp']}°C**")
            st.write(f"Humidity: **{data['humidity']}%**")

        # ---------- MAP ----------
        m = Map(location=[data["lat"], data["lon"]], zoom_start=9)

        CircleMarker(
            location=[data["lat"], data["lon"]],
            radius=18,
            tooltip=f"{data['city']} | AQI: {data['aqi']}",
            color=get_color(data["aqi"]),
            fill=True,
            fill_color=get_color(data["aqi"])
        ).add_to(m)

        st_folium(m, width=950, height=520)


# ------------ MAIN APP ------------
def main_app():
    st.sidebar.title(f"👋 Welcome {st.session_state.username}")

    page = st.sidebar.radio("Navigation",
                            ["AQI Prediction", "Live AQI", "Bulk CSV", "Analytics", "Map AQI", "Logout"])

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
