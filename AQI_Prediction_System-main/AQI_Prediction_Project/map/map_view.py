import folium
from streamlit_folium import st_folium

def show_map(lat, lon, aqi):
    m = folium.Map(location=[lat, lon], zoom_start=8)

    folium.Marker(
        [lat, lon],
        popup=f"AQI Level: {aqi}",
        tooltip="AQI Location",
    ).add_to(m)

    st_folium(m, width=700, height=500)
