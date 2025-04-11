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
            giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
            data_obj = datetime.strptime(row["data"], "%Y-%m-%d")
            giorno = f"{giorni_it[data_obj.weekday()]} {data_obj.strftime('%d/%m')}"
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

# === AI METEO ASSISTANT ===
def interpreta_ai(domanda, previsioni):
    from datetime import datetime as dt
    domanda = domanda.lower()
    giorni_alias = {
        "lun": 0, "mar": 1, "mer": 2, "gio": 3, "ven": 4, "sab": 5, "dom": 6,
        "luned": 0, "mart": 1, "merc": 2, "giov": 3, "vener": 4, "sabat": 5, "domen": 6
    }
    oggi = dt.now().date()
    if "oggi" in domanda:
        r = previsioni.iloc[0]
        return f"Oggi: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"
    if "domani" in domanda:
        r = previsioni.iloc[1]
        return f"Domani: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"
    for parola in domanda.split():
        for alias, idx in giorni_alias.items():
            if parola.startswith(alias):
                for _, r in previsioni.iterrows():
                    d = dt.strptime(r['data'], "%Y-%m-%d").date()
                    if d.weekday() == idx:
                        return f"{d.strftime('%A %d/%m')}: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"
    return "❓ Domanda non compresa. Es: 'piove sab?', 'caldo domani?', 'serve ombrello?'"

# === BLOCCO VISIVO AI ===
try:
    st.subheader("🧠 AI Meteo Assistant")
    domanda_ai = st.text_input("Scrivi la tua domanda meteo:", placeholder="Domani piove? Sab afa? Ombrello lun?")
    if domanda_ai:
        previsioni_ai = get_previsioni()
        risposta_ai = interpreta_ai(domanda_ai, previsioni_ai)
        st.success("🤖 " + risposta_ai)
except Exception as e:
    st.error("❌ Errore AI Assistant: " + str(e))



# === AI METEO ASSISTANT AVANZATO ===





def interpreta_ai_esteso(domanda, previsioni):
    from datetime import datetime as dt, timedelta

    giorni_alias = {
        "oggi": 0, "domani": 1, "dopodomani": 2,
        "lun": 0, "mar": 1, "mer": 2, "gio": 3, "ven": 4, "sab": 5, "dom": 6,
        "lunedì": 0, "martedì": 1, "mercoledì": 2, "giovedì": 3,
        "venerdì": 4, "sabato": 5, "domenica": 6
    }

    giorni_it = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    oggi = dt.now().date()
    domanda = domanda.lower()

    for parola in domanda.split():
        if parola in giorni_alias:
            idx = giorni_alias[parola]
            data_target = oggi + timedelta(days=idx) if parola in ["oggi", "domani", "dopodomani"] else None

            for _, r in previsioni.iterrows():
                try:
                    data_obj = dt.strptime(r["data"], "%Y-%m-%d").date()
                except:
                    continue

                if data_target and data_obj != data_target:
                    continue
                if not data_target and data_obj.weekday() != idx:
                    continue

                min_t = r.get("min", "?")
                max_t = r.get("max", "?")
                pioggia = r.get("prec", 0)
                vento = r.get("vento", 0)

                commento = ""
                if pioggia > 2:
                    commento += "🌧️ Possibile pioggia: meglio portare l’ombrello. "
                elif pioggia > 0:
                    commento += "🌥️ Qualche goccia possibile. "
                else:
                    commento += "☀️ Tempo stabile, nessuna pioggia prevista. "

                if isinstance(max_t, (int, float)) and max_t > 30:
                    commento += "🔥 Fa molto caldo!"
                elif isinstance(max_t, (int, float)) and max_t < 10:
                    commento += "🧥 Giornata fredda."

                if isinstance(vento, (int, float)) and vento > 30:
                    commento += "💨 Attenzione al vento forte."

                giorno_it = giorni_it[data_obj.weekday()]
                return f"{giorno_it} {data_obj.strftime('%d/%m')}: {min_t}°C / {max_t}°C – Pioggia {pioggia} mm – Vento {vento} km/h. {commento}"

    if "tendenza" in domanda or "settimana" in domanda:
        try:
            giorni_con_pioggia = sum(previsioni["prec"] > 2)
            if giorni_con_pioggia >= 4:
                return "📉 Settimana instabile, con diverse giornate piovose."
            elif giorni_con_pioggia == 0:
                return "📈 Settimana stabile e soleggiata."
            else:
                return "🌦️ Alternanza tra sole e pioggia nei prossimi giorni."
        except:
            return "❗ Dati insufficienti per calcolare la tendenza settimanale."

    return "❓ Domanda non compresa. Prova con: 'piove sabato?', 'caldo lunedì?', 'serve ombrello domani?', 'tendenza settimana'."
