import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="🌦️ Meteo Torre Annunziata", layout="wide")

# Configurazione OpenWeather API
OPENWEATHER_API_KEY = "d23fb9868855e4bcb4dcf04404d14a78"
latitude = 40.7581
longitude = 14.4492

def calcola_indice_thom(temp, umid):
    return round(0.8 * temp + ((umid / 100) * (temp - 14.4)) + 46.4, 1)

# Funzione per ottenere i dati meteo attuali da OpenWeather
def get_meteo_data():
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    return {
        "temperatura": data["main"]["temp"],
        "umidita": data["main"]["humidity"],
        "vento": data["wind"]["speed"],
        "pressione": data["main"]["pressure"],
        "uv": data.get("uv", "N/D"),  # OpenWeather richiede una chiamata separata per l'UV Index
    }

# Funzione per ottenere i dati delle ultime 24 ore da OpenWeather
def get_24h_data():
    url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={latitude}&lon={longitude}&dt={(int(datetime.now().timestamp()) - 86400)}&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    hourly_data = data.get("hourly", [])
    return pd.DataFrame({
        "time": [datetime.utcfromtimestamp(hour["dt"]).strftime('%H:%M') for hour in hourly_data],
        "Temperatura (°C)": [hour["temp"] for hour in hourly_data],
        "Umidità (%)": [hour["humidity"] for hour in hourly_data],
        "Pressione (hPa)": [hour["pressure"] for hour in hourly_data]
    })

# Funzione per ottenere le previsioni a 7 giorni da OpenWeather
def get_previsioni():
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&exclude=current,minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    r = requests.get(url)
    data = r.json()
    daily_data = data.get("daily", [])
    return pd.DataFrame({
        "data": [datetime.utcfromtimestamp(day["dt"]).strftime('%Y-%m-%d') for day in daily_data],
        "max": [day["temp"]["max"] for day in daily_data],
        "min": [day["temp"]["min"] for day in daily_data],
        "prec": [day.get("rain", 0) for day in daily_data]
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
    pagina = st.radio("📋 Menu", ["Meteo Attuale", "Andamento 24 Ore", "Previsioni", "Radar & Satellite", "Webcam"])
    st.markdown("---")
    st.caption("🕒 Ultimo aggiornamento: " + datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC'))

# PAGINA METEO ATTUALE
if pagina == "Meteo Attuale":
    st.subheader("📍 Condizioni Attuali")
    dati = get_meteo_data()
    if dati:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🌡️ Temperatura")
            st.success(f"{dati['temperatura']} °C")
        with col2:
            st.markdown("### 💧 Umidità")
            st.info(f"{dati['umidita']} %")
        with col3:
            st.markdown("### 💨 Vento")
            st.warning(f"{dati['vento']} m/s")

        col4, col5 = st.columns(2)
        with col4:
            st.markdown("### 🌞 UV Index")
            st.success(f"{dati['uv']}")
        with col5:
            st.markdown("### 🧭 Pressione")
            st.info(f"{dati['pressione']} hPa")

        thom = calcola_indice_thom(dati['temperatura'], dati['umidita'])
        if thom < 70:
            colore, desc = "🟢", "Confort ideale"
        elif thom < 75:
            colore, desc = "🟡", "Leggero disagio"
        elif thom < 80:
            colore, desc = "🟠", "Disagio percepito"
        else:
            colore, desc = "🔴", "Pericoloso per la salute"
        st.markdown(f"### {colore} Indice di Thom: {thom}")
        st.info(f"**Interpretazione:** {desc} — misura il disagio da temperatura e umidità.")

# PAGINA ANDAMENTO 24 ORE
elif pagina == "Andamento 24 Ore":
    st.subheader("📈 Andamento ultime 24 ore")
    df = get_24h_data()
    if not df.empty:
        st.line_chart(df.set_index("time"))
    else:
        st.warning("Nessun dato disponibile per l'andamento delle ultime 24 ore.")

# PAGINA PREVISIONI
elif pagina == "Previsioni":
    st.subheader("📆 Previsioni 7 Giorni")
    df = get_previsioni()
    if not df.empty:
        for i, row in df.iterrows():
            giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
            data_obj = datetime.strptime(row["data"], "%Y-%m-%d")
            giorno = f"{giorni_it[data_obj.weekday()]} {data_obj.strftime('%d/%m')}"
            icona = "☀️" if row["prec"] < 2 else "🌧️"
            condizione = "Sereno e soleggiato" if row["prec"] < 2 else "Rovesci nel pomeriggio"
            colore_sfondo = "#e3f2fd" if row["prec"] < 2 else "#fce4ec"
            badge_colore = "#0288d1" if row["prec"] < 2 else "#c62828"
            st.markdown(f"""
                <div style='display:flex;flex-direction:row;align-items:center;justify-content:space-between;background-color:{colore_sfondo};padding:16px 20px;border-radius:14px;margin-bottom:14px;'>
                    <div style='flex:1;font-size:40px;text-align:center;'>{icona}</div>
                    <div style='flex:5;padding-left:10px;'>
                        <div style='font-size:17px;font-weight:bold;margin-bottom:6px;'>{giorno}</div>
                        <div style='margin-bottom:4px;'>🌡️ <b>{row["max"]}°C</b> / <b>{row["min"]}°C</b> — ☔ {row["prec"]} mm</div>
                        <div style='font-style:italic;color:#333;'>🧠 {"Porta l'ombrello" if row["prec"] > 5 else "Giornata tranquilla"}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# PAGINA RADAR & SATELLITE
elif pagina == "Radar & Satellite":
    st.subheader("🌧️ Radar - Windy")
    st.components.v1.iframe("https://embed.windy.com/embed2.html?lat=40.75&lon=14.45&detailLat=40.75&detailLon=14.45&width=700&height=450&zoom=8&level=surface&overlay=rain&menu=true", height=450)
    st.subheader("🛰️ Satellite - Windy")
    st.components.v1.iframe("https://embed.windy.com/embed2.html?lat=40.75&lon=14.45&detailLat=40.75&detailLon=14.45&width=700&height=450&zoom=6&level=surface&overlay=satellite&menu=false", height=450)

# PAGINA WEBCAM
elif pagina == "Webcam":
    st.subheader("📷 Webcam Torre Annunziata")
    st.markdown("🔗 [Clicca qui per visualizzare la webcam live su SkylineWebcams](https://www.skylinewebcams.com/it/webcam/italia/campania/napoli/torre-annunziata.html)")
