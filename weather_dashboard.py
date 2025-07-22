import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import geocoder

# --- CONFIG ---
API_KEY = "a8564be1fd5ba533db286f1d9a2f533b"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

st.set_page_config(page_title="Weather Dashboard", layout="wide")

# --- TITLE ---
st.markdown("<h1 style='text-align: center;'>🌍 Live Weather Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# --- AUTO LOCATION ---
@st.cache_data
def get_location_city():
    g = geocoder.ip('me')
    return g.city if g.city else "New York"

# --- SEARCH BAR ---
search_city = st.text_input("🔍 Enter City Name", value=get_location_city(), placeholder="e.g. Tokyo, Paris")
st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# --- API REQUESTS ---
def get_weather_data(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    return requests.get(WEATHER_URL, params=params).json()

def get_forecast_data(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    return requests.get(FORECAST_URL, params=params).json()

def get_air_quality_data(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    return requests.get(AIR_QUALITY_URL, params=params).json()

# --- FETCH DATA ---
weather = get_weather_data(search_city)
forecast = get_forecast_data(search_city)

if "main" not in weather:
    st.error("❌ Could not fetch weather. Try another city.")
    st.stop()

lat, lon = weather['coord']['lat'], weather['coord']['lon']
aqi_data = get_air_quality_data(lat, lon)
aqi = aqi_data['list'][0]['main']['aqi']

# --- AQI LABEL ---
aqi_levels = {
    1: ("Good", "#009966"),
    2: ("Fair", "#ffde33"),
    3: ("Moderate", "#ff9933"),
    4: ("Poor", "#cc0033"),
    5: ("Very Poor", "#660099"),
}
aqi_label, aqi_color = aqi_levels.get(aqi, ("Unknown", "#888888"))

# --- LOCATION HEADER ---
st.markdown(f"""
<div style='font-size:24px; font-weight:bold; margin-bottom:10px;'>
📍 Location: {weather['name']}, {weather['sys']['country']}
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# --- WEATHER BLOCK COLUMNS (TRANSPARENT) ---
col1, col2 = st.columns(2)
block_style = """
    background-color: rgba(0, 0, 0, 0);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    font-size: 22px;
"""

with col1:
    st.markdown(f"<div style='{block_style}'>🌥 <b>Condition:</b> {weather['weather'][0]['description'].title()}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='{block_style}'>🌬 <b>Wind:</b> {weather['wind']['speed']} m/s</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='{block_style}'>🌅 <b>Sunrise:</b> {datetime.fromtimestamp(weather['sys']['sunrise']).strftime('%H:%M')}</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='{block_style}'>🌡 <b>Temperature:</b> {weather['main']['temp']} °C</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='{block_style}'>💧 <b>Humidity:</b> {weather['main']['humidity']}%</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='{block_style}'>🌇 <b>Sunset:</b> {datetime.fromtimestamp(weather['sys']['sunset']).strftime('%H:%M')}</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

# --- AQI CHART ---
st.markdown("### 🌫 Air Quality Index")
st.markdown(f"""
<div style='font-size: 22px; color: {aqi_color}; font-weight: bold; margin-bottom: 10px;'>
AQI Level: {aqi} - {aqi_label}
</div>
""", unsafe_allow_html=True)

aqi_bar = go.Figure()
aqi_bar.add_trace(go.Bar(
    x=["Good", "Fair", "Moderate", "Poor", "Very Poor"],
    y=[1, 2, 3, 4, 5],
    marker_color=["#009966", "#ffde33", "#ff9933", "#cc0033", "#660099"],
    text=["0–50", "51–100", "101–150", "151–200", "201+"],
    textposition="outside"
))
aqi_bar.update_layout(
    title="AQI Levels Overview",
    yaxis=dict(showticklabels=False),
    height=350,
    width=900,
    template="simple_white",
    margin=dict(t=50, b=40)
)
st.plotly_chart(aqi_bar, use_container_width=False)

st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

# --- 5-DAY FORECAST ---
st.markdown("### 📅 5-Day Temperature Forecast")

forecast_times = [entry['dt_txt'] for entry in forecast['list']]
forecast_temps = [entry['main']['temp'] for entry in forecast['list']]

forecast_fig = go.Figure()
forecast_fig.add_trace(go.Scatter(
    x=forecast_times,
    y=forecast_temps,
    mode='lines+markers',
    line=dict(color='royalblue'),
    name="Temperature"
))
forecast_fig.update_layout(
    height=400,
    width=1000,
    xaxis_title="Date & Time",
    yaxis_title="Temperature (°C)",
    template="simple_white",
    margin=dict(t=50, b=40)
)
st.plotly_chart(forecast_fig, use_container_width=False)

st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)

# -- Footer --
st.markdown("---")
st.caption("Weather data provided by OpenWeatherMap • Dashboard built with Streamlit")
