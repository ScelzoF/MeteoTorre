import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# Configurazione della pagina Streamlit
st.set_page_config(page_title="🌦️ Meteo Torre Annunziata", layout="wide")

# Configurazione API OpenWeather
OPENWEATHER_API_KEY = "d23fb9868855e4bcb4dcf04404d14a78"
latitude = 40.7581
longitude = 14.4492

# Funzione per ottenere i dati meteo attuali
def get_meteo_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    return {
        "temperatura": data["main"]["temp"],
        "umidita": data["main"]["humidity"],
        "vento": data["wind"]["speed"],
        "pressione": data["main"]["pressure"],
        "descrizione": data["weather"][0]["description"].capitalize()
    }

# Funzione per ottenere i dati delle ultime 24 ore
def get_24h_data():
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&exclude=current,minutely,daily,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    hourly_data = data["hourly"][:24]  # Prendi solo le ultime 24 ore
    return pd.DataFrame({
        "time": [datetime.utcfromtimestamp(hour["dt"]).strftime('%H:%M') for hour in hourly_data],
        "Temperatura (°C)": [hour["temp"] for hour in hourly_data],
        "Umidità (%)": [hour["humidity"] for hour in hourly_data],
        "Pressione (hPa)": [hour["pressure"] for hour in hourly_data]
    })

# Funzione per ottenere le previsioni a 7 giorni
def get_previsioni():
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&exclude=current,minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    daily_data = data["daily"]
    return pd.DataFrame({
        "data": [datetime.utcfromtimestamp(day["dt"]).strftime('%Y-%m-%d') for day in daily_data],
        "max": [day["temp"]["max"] for day in daily_data],
        "min": [day["temp"]["min"] for day in daily_data],
        "prec": [day["rain"] if "rain" in day else 0 for day in daily_data]
    })

# HEADER grafico
st.markdown("""
    <div style='background:linear-gradient(90deg,#0f2027,#203a43,#2c5364);padding:30px;border-radius:10px;text-align:center;margin-bottom:20px;'>
        <h1 style='color:white;margin:0;'>🌦️ Meteo Torre Annunziata</h1>
        <p style='color:white;font-size:16px;'>Dati aggiornati in tempo reale - Powered by OpenWeather</p>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    pagina = st.radio("📋 Menu", ["Meteo Attuale", "Previsioni", "Andamento 24h"])
    st.markdown("---")
    st.caption("🕒 Ultimo aggiornamento: " + datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC'))

# PAGINA METEO ATTUALE
if pagina == "Meteo Attuale":
    st.subheader("📍 Condizioni Attuali")
    dati = get_meteo_data()
    if dati:
        st.markdown(f"### 🌡️ Temperatura: **{dati['temperatura']}°C**")
        st.markdown(f"### 💧 Umidità: **{dati['umidita']}%**")
        st.markdown(f"### 💨 Vento: **{dati['vento']} m/s**")
        st.markdown(f"### 🧭 Pressione: **{dati['pressione']} hPa**")
        st.markdown(f"### 🌥️ Condizioni: **{dati['descrizione']}**")

# PAGINA ANDAMENTO 24H
elif pagina == "Andamento 24h":
    st.subheader("📈 Andamento ultime 24 ore")
    df = get_24h_data()
    if not df.empty:
        st.line_chart(df.set_index("time"))

# PAGINA PREVISIONI
elif pagina == "Previsioni":
    st.subheader("📆 Previsioni 7 Giorni")
    df = get_previsioni()
    if not df.empty:
        st.dataframe(df)
