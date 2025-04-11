def interpreta_ai(domanda, previsioni):
    import re
    from datetime import datetime as dt

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

# Blocco AI integrato
st.subheader("🧠 AI Meteo Assistant")
user_input = st.text_input("Scrivi la tua domanda meteo:", placeholder="Domani piove? Sab afa? Ombrello lun?")
if user_input:
    try:
        previsioni_ai = get_forecast()
        risposta = interpreta_ai(user_input, previsioni_ai)
        st.success("🤖 " + risposta)
    except Exception as e:
        st.error("Errore AI: " + str(e))