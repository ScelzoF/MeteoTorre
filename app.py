import streamlit as st
import pandas as pd
import requests
from datetime import datetime as dt

st.set_page_config(page_title="Meteo Torre Annunziata", layout="wide")
st.title("🌦️ Meteo Torre Annunziata")

# Funzione per ottenere previsioni reali
def get_previsioni():
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=40.7633&longitude=14.4522"
        "&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,uv_index_max,windspeed_10m_max"
        "&timezone=Europe%2FRome"
    )
    r = requests.get(url)
    d = r.json()["daily"]

    return pd.DataFrame({
        "data": d["time"],
        "min": d["temperature_2m_min"],
        "max": d["temperature_2m_max"],
        "prec": d["precipitation_sum"],
        "uv": d["uv_index_max"],
        "vento": d["windspeed_10m_max"]
    })

# Funzione AI meteo avanzata
def interpreta_ai(domanda, previsioni):
    domanda = domanda.lower()
    giorni_alias = {
        "lun": 0, "mar": 1, "mer": 2, "gio": 3, "ven": 4, "sab": 5, "dom": 6,
        "luned": 0, "mart": 1, "merc": 2, "giov": 3, "vener": 4, "sabat": 5, "domen": 6
    }
    oggi = dt.now().date()

    def analizza(r):
        note = []
        if float(r['prec']) > 1:
            note.append("🌧️ Pioggia prevista")
        if float(r['uv']) > 6:
            note.append("🌞 UV elevato")
        if float(r['vento']) > 30:
            note.append("💨 Vento forte")
        if float(r['max']) >= 30:
            note.append("🥵 Giornata calda")
        if float(r['min']) <= 5:
            note.append("❄️ Freddo mattutino")
        if not note:
            note.append("☀️ Condizioni meteo stabili")
        return " – ".join(note)

    if "oggi" in domanda:
        r = previsioni.iloc[0]
        return f"Oggi: {r['min']}°C / {r['max']}°C – {analizza(r)}"
    elif "domani" in domanda:
        r = previsioni.iloc[1]
        return f"Domani: {r['min']}°C / {r['max']}°C – {analizza(r)}"
    else:
        for parola in domanda.split():
            for alias, idx in giorni_alias.items():
                if parola.startswith(alias):
                    for _, r in previsioni.iterrows():
                        d = dt.strptime(r['data'], "%Y-%m-%d").date()
                        if d.weekday() == idx:
                            return f"{d.strftime('%A %d/%m')}: {r['min']}°C / {r['max']}°C – {analizza(r)}"
    return "❓ Domanda non compresa. Es: 'piove sab?', 'caldo domani?', 'serve ombrello?'"

# Blocco visivo AI Assistant
st.subheader("🧠 AI Meteo Assistant")
user_input = st.text_input("Scrivi la tua domanda meteo (anche in modo informale):", placeholder="Domani piove? Sab afa? Ombrello lun?")
if user_input:
    try:
        previsioni_ai = get_previsioni()
        risposta_ai = interpreta_ai(user_input, previsioni_ai)
        st.success("🤖 " + risposta_ai)
    except Exception as e:
        st.error("❌ Errore AI Assistant: " + str(e))