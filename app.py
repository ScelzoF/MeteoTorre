
import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="🌦️ Meteo Torre Annunziata", layout="wide")

latitude = 40.7581
longitude = 14.4492

def calcola_indice_thom(temp, umid):
    return round(0.8 * temp + ((umid / 100) * (temp - 14.4)) + 46.4, 1)

def get_meteo_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index,pressure_msl&timezone=auto"
    r = requests.get(url)
    data = r.json().get("current", {})
    return {
        "temperatura": data.get("temperature_2m"),
        "umidita": data.get("relative_humidity_2m"),
        "vento": data.get("wind_speed_10m"),
        "uv": data.get("uv_index"),
        "pressione": data.get("pressure_msl")
    }

def get_24h_data():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,pressure_msl&past_hours=24&forecast_hours=0&timezone=auto"
    r = requests.get(url)
    d = r.json().get("hourly", {})
    return pd.DataFrame({
        "time": d.get("time", []),
        "Temperatura (°C)": d.get("temperature_2m", []),
        "Umidità (%)": d.get("relative_humidity_2m", []),
        "Pressione (hPa)": d.get("pressure_msl", [])
    })

def get_previsioni():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    r = requests.get(url)
    d = r.json().get("daily", {})
    return pd.DataFrame({
        "data": d.get("time", []),
        "max": d.get("temperature_2m_max", []),
        "min": d.get("temperature_2m_min", []),
        "prec": d.get("precipitation_sum", [])
    })

# HEADER grafico
st.markdown("""
    <div style='background:linear-gradient(90deg,#0f2027,#203a43,#2c5364);padding:30px;border-radius:10px;text-align:center;margin-bottom:20px;'>
        <h1 style='color:white;margin:0;'>🌦️ Meteo Torre Annunziata</h1>
        <p style='color:white;font-size:16px;'>Dati aggiornati in tempo reale - Powered by Open-Meteo</p>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    pagina = st.radio("📋 Menu", ["Meteo Attuale", "Previsioni", "Radar & Satellite", "Webcam"])
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
            st.warning(f"{dati['vento']} km/h")

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

        st.subheader("📈 Andamento ultime 24 ore")
        df = get_24h_data()
        if not df.empty:
            st.line_chart(df.set_index("time"))
        else:
            st.warning("Nessun dato disponibile.")

# PAGINA PREVISIONI





elif pagina == "Previsioni":
    st.subheader("📆 Previsioni 7 Giorni")
    df = get_previsioni()
    if not df.empty:
        for i, row in df.iterrows():
            giorno = datetime.strptime(row["data"], "%Y-%m-%d").strftime("%A %d/%m")
            icona = "☀️" if row["prec"] < 2 else "🌧️"
            condizione = "Sereno e soleggiato" if row["prec"] < 2 else "Rovesci nel pomeriggio"
            colore_sfondo = "#e3f2fd" if row["prec"] < 2 else "#fce4ec"
            badge_colore = "#0288d1" if row["prec"] < 2 else "#c62828"
            st.markdown(f"""
                <div style='display:flex;flex-direction:row;align-items:center;justify-content:space-between;background-color:{colore_sfondo};padding:16px 20px;border-radius:14px;margin-bottom:14px;box-shadow:1px 1px 6px #bbb;'>
                    <div style='flex:1;font-size:40px;text-align:center;'>{icona}</div>
                    <div style='flex:5;padding-left:10px;'>
                        <div style='font-size:17px;font-weight:bold;margin-bottom:6px;'>{giorno}</div>
                        <div style='margin-bottom:4px;'>🌡️ <b>{row["max"]}°C</b> / <b>{row["min"]}°C</b> — ☔ {row["prec"]} mm</div>
                        <div style='margin-bottom:4px;'>💨 Vento: in aggiornamento &nbsp; 🔆 UV: in aggiornamento</div>
                        <div style='font-style:italic;color:#333;'>🧠 {"Porta l'ombrello" if row["prec"] > 5 else "Giornata tranquilla"}</div>
                    </div>
                    <div style='flex:2;text-align:center;'>
                        <div style='background:{badge_colore};color:white;padding:10px 12px;border-radius:8px;font-weight:bold;box-shadow:1px 1px 4px rgba(0,0,0,0.2);'>
                            {condizione}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Dati previsionali non disponibili.")

elif pagina == "Radar & Satellite":
    st.subheader("🌧️ Radar - Windy")
    st.components.v1.iframe("https://embed.windy.com/embed2.html?lat=40.75&lon=14.45&detailLat=40.75&detailLon=14.45&width=700&height=450&zoom=8&level=surface&overlay=rain&menu=true", height=450)
    st.subheader("🛰️ Satellite - Windy")
    st.components.v1.iframe("https://embed.windy.com/embed2.html?lat=40.75&lon=14.45&detailLat=40.75&detailLon=14.45&width=700&height=450&zoom=6&level=surface&overlay=satellite&menu=false", height=450)

# WEBCAM
elif pagina == "Webcam":
    st.subheader("📷 Webcam Torre Annunziata")
    st.markdown("🔗 [Clicca qui per visualizzare la webcam live su SkylineWebcams](https://www.skylinewebcams.com/it/webcam/italia/campania/napoli/torre-annunziata.html)")
