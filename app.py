import streamlit as st
import pandas as pd
from datetime import datetime as dt

# Mock funzione get_forecast() per evitare errori
def get_forecast():
    return pd.DataFrame([
        {'data': '2025-04-11', 'min': 12.5, 'max': 21.7, 'appa_max': 27, 'prec': 0.0, 'vento': 9.2, 'uv': 5.3},
        {'data': '2025-04-12', 'min': 14.0, 'max': 22.1, 'appa_max': 31, 'prec': 2.1, 'vento': 8.7, 'uv': 6.1},
        {'data': '2025-04-13', 'min': 13.2, 'max': 25.3, 'appa_max': 30.5, 'prec': 1.2, 'vento': 7.5, 'uv': 6.5},
    ])

def interpreta_ai(domanda, previsioni):
    domanda = domanda.lower()
    giorni_alias = {
        "lun": 0, "mar": 1, "mer": 2, "gio": 3, "ven": 4, "sab": 5, "dom": 6,
        "luned": 0, "mart": 1, "merc": 2, "giov": 3, "vener": 4, "sabat": 5, "domen": 6
    }
    oggi = dt.now().date()
    risposta = "Domanda non compresa. Es: 'pioggia sab?', 'domani caldo?', 'serve ombrello?'"

    if "oggi" in domanda:
        r = previsioni.iloc[0]
        return f"Oggi: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"
    elif "domani" in domanda:
        r = previsioni.iloc[1]
        return f"Domani: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"
    else:
        for parola in domanda.split():
            for alias, idx in giorni_alias.items():
                if parola.startswith(alias):
                    for _, r in previsioni.iterrows():
                        d = dt.strptime(r['data'], "%Y-%m-%d").date()
                        if d.weekday() == idx:
                            return f"{d.strftime('%A %d/%m')}: {r['min']}°C / {r['max']}°C – Pioggia {r['prec']} mm – Vento {r['vento']} km/h"

    if "piogg" in domanda or "ombrel" in domanda:
        piovosi = [f"{r['data']}: {r['prec']} mm" for _, r in previsioni.iterrows() if r['prec'] > 0.5]
        return "📅 Giorni con pioggia: " + ", ".join(piovosi) if piovosi else "☀️ Nessuna pioggia rilevante nei prossimi giorni."
    if "afa" in domanda or "caldo" in domanda:
        afosi = [f"{r['data']}: {r['appa_max']}°" for _, r in previsioni.iterrows() if r['appa_max'] >= 30]
        return "🥵 Giorni afosi: " + ", ".join(afosi) if afosi else "🌤️ Nessuna ondata di calore rilevata."
    return risposta

# INTERFACCIA VISUALE
st.set_page_config(page_title="Meteo Torre Annunziata", layout="centered")
st.title("🧠 AI Meteo Assistant")

try:
    previsioni_ai = get_forecast()
    domanda = st.text_input("Scrivi la tua domanda meteo:", placeholder="Domani piove? Sab afa? Ombrello lun?")
    if domanda:
        risposta = interpreta_ai(domanda, previsioni_ai)
        st.success("🤖 " + risposta)
except Exception as e:
    st.error("Errore AI: " + str(e))