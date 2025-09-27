from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

VISUAL_SCALES = True
ACCENT_RGB = "234, 88, 12"   # Orange

STYLE = f"""
<style>
:root {{
  --accent-rgb: {ACCENT_RGB};
  --text-light: #0f172a;
  --muted-light: #334155;
  --text-dark: #e5e7eb;
}}
.device-title {{ font-size: 1.2rem; font-weight: 800; margin: 10px 0 4px; color: rgb(var(--accent-rgb)); }}
.device-section {{ font-size: .95rem; color: #475569; margin-bottom: 10px; }}
.separator {{ height: 4px; width: 100%; background: rgba(var(--accent-rgb), .28); border-radius: 2px; margin: 22px 0 16px 0; }}
.crit-title {{ font-weight: 700; margin-bottom: 4px; }}
.crit-help {{ font-size: 1rem; line-height: 1.5; margin-bottom: 10px; color: var(--muted-light); }}
.scale-wrap {{ margin: 6px 0 12px 0; }}
.scale-rail {{ position: relative; height: 8px; background: rgba(var(--accent-rgb), .2); border-radius: 999px; }}
.scale-fill {{ position: absolute; left:0; top:0; bottom:0; width: 0%; background: rgba(var(--accent-rgb), .85); border-radius: 999px; transition: width .15s ease; }}
.scale-ticks {{ display: flex; justify-content: space-between; margin-top: 6px; font-size: .9rem; color:#64748b; }}
.scale-ticks span:first-child, .scale-ticks span:last-child {{ color:#111827; font-weight:600; }}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

def sget(key: str, default=None):
    return st.session_state.get(key, default)

def visual_scale(current_value:int, max_value:int=4, left_label:str="", right_label:str=""):
    pct = int((current_value or 0) / max_value * 100)
    st.markdown(f"""
<div class="scale-wrap">
  <div class="scale-rail"><div class="scale-fill" style="width:{pct}%;"></div></div>
  <div class="scale-ticks"><span>{left_label}</span><span>{right_label}</span></div>
</div>
""", unsafe_allow_html=True)

def criterion_radio_inline(title: str, short_desc: str, labels_map: dict[int,str], key: str, disabled: bool):
    st.markdown('<div class="crit-block">', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-help">{short_desc}</div>', unsafe_allow_html=True)
    options = [1,2,3,4]
    def fmt(v: int): return f"{v} – {labels_map.get(v, "")}"
    value = st.radio("", options, key=key, disabled=disabled, horizontal=True, format_func=fmt, label_visibility="collapsed")
    if VISUAL_SCALES:
        left = labels_map[min(labels_map.keys())]
        right = labels_map[max(labels_map.keys())]
        visual_scale(int(value or 0), max_value=4, left_label=left, right_label=right)
    st.markdown('</div>', unsafe_allow_html=True)
    return value

# Kriterien
K1_TITLE, K1_SHORT = "Leistung anpassen", "Wie stark kann die Leistung kurzfristig reduziert/verändert werden?"
K1_LABELS = {1:"kaum anpassbar",2:"etwas anpassbar",3:"gut anpassbar",4:"sehr gut anpassbar"}
K2_TITLE, K2_SHORT = "Nutzungsdauer anpassbar", "Wie lange kann die Nutzung/Funktion gedrosselt oder verschoben werden?"
K2_LABELS = {1:"nicht anpassbar",2:"< 15 min",3:"15–45 min",4:"> 45 min"}
K4_TITLE, K4_SHORT = "Zeitliche Flexibilität", "Ist der Einsatz an feste Zeiten gebunden oder frei planbar?"
K4_LABELS = {1:"feste Zeiten",2:"eingeschränkt flexibel",3:"eher flexibel",4:"völlig flexibel"}

# Katalog
CATALOG = {
    "A) Küche": ["Kühlhaus","Tiefkühlhaus","Kombidämpfer","Fritteuse","Induktionsherd","Geschirrspülmaschine"],
    "B) Wellness / Spa / Pool": ["Sauna","Dampfbad","Pool-Umwälzpumpe","Schwimmbad-Lüftung/Entfeuchtung"],
    "C) Zimmer & Allgemeinbereiche": ["Zimmerbeleuchtung","Aufzüge","Waschmaschine","Trockner","Wallbox (E-Ladepunkte)"],
}

# Intro-Seite
if "intro_done" not in st.session_state:
    st.markdown("""
    ## Einleitung

    Im Rahmen meiner Masterarbeit untersuche ich, wie Hotels ihren **Stromverbrauch flexibler gestalten** können.  
    Da erneuerbare Energien wie **Sonne und Wind wetterabhängig** sind, kommt es zu **Schwankungen im Stromnetz**.  

    Mit Ihrer Einschätzung möchte ich herausfinden, welche **Geräte im Hotelbetrieb zeitlich flexibel** eingesetzt werden können,  
    um **Lastspitzen zu reduzieren**, **Kosten zu senken** und die **Netzstabilität zu unterstützen**.  

    Die Befragung ist **anonym**, dauert nur **5–7 Minuten** und dient ausschließlich **wissenschaftlichen Zwecken**.  
    Ihre Teilnahme trägt dazu bei, Hotels **nachhaltiger und zukunftsfähiger** zu gestalten.  
    """)

    if st.button("Weiter zur Befragung", type="primary", use_container_width=True):
        st.session_state.intro_done = True
        st.rerun()
    st.stop()

if "started" not in st.session_state:
    st.session_state.started = False

# Einverständnis-Seite
if not st.session_state.started:
    st.subheader("Einverständniserklärung")

    with st.container(border=True):
        st.markdown(
            """
- Teilnahme ist freiwillig, Abbruch jederzeit ohne Nachteile.  
- Verwendung ausschließlich zu wissenschaftlichen Zwecken.  
- Anonymisierte Erhebung.  
- Einsicht nur für berechtigte Personen.
            """.strip()
        )
        st.checkbox("Ich habe die Informationen gelesen und bin einverstanden.", key="consent")

    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("Hotel (Pflicht)", key="hotel")
    with col2: st.text_input("Bereich/Abteilung (Pflicht)", key="bereich")
    with col3: st.text_input("Position (Pflicht)", key="position")
    st.date_input("Datum", value=datetime.today(), key="datum")
    st.text_input("Name (optional)", key="teilnehmername")

    with st.container(border=True):
        st.checkbox("Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.", key="confirm")

    if st.button("Start – zum Fragebogen", type="primary", use_container_width=True):
        if not (st.session_state.get("consent") and st.session_state.get("confirm") and st.session_state.get("hotel") and st.session_state.get("bereich") and st.session_state.get("position")):
            st.warning("Bitte alle Pflichtfelder und Häkchen ausfüllen.")
        else:
            st.session_state.meta = {
                "hotel":sget("hotel",""),
                "bereich":sget("bereich",""),
                "position":sget("position",""),
                "datum":str(sget("datum","")),
                "teilnehmername":sget("teilnehmername","")
            }
            st.session_state.started=True
            st.rerun()

# Hauptfragebogen
if st.session_state.started:
    all_records=[]
    for section,devices in CATALOG.items():
        st.markdown(f"## {section}")
        for idx, dev in enumerate(devices):
            if idx > 0:
                st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="device-title">{dev}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="device-section">{section}</div>', unsafe_allow_html=True)

            vorhanden = st.checkbox("Vorhanden", key=f"vh_{section}_{dev}")

            k1 = criterion_radio_inline(K1_TITLE, K1_SHORT, K1_LABELS, key=f"k1_{section}_{dev}", disabled=not vorhanden)
            k2 = criterion_radio_inline(K2_TITLE, K2_SHORT, K2_LABELS, key=f"k2_{section}_{dev}", disabled=not vorhanden)
            k4 = criterion_radio_inline(K4_TITLE, K4_SHORT, K4_LABELS, key=f"k4_{section}_{dev}", disabled=not vorhanden)

            all_records.append({
                "section":section,
                "geraet":dev,
                "vorhanden":bool(vorhanden),
                "modulation":int(k1) if vorhanden else None,
                "dauer":int(k2) if vorhanden else None,
                "betriebsfenster":int(k4) if vorhanden else None
            })

    if st.button("Jetzt absenden und speichern",type="primary",use_container_width=True):
        df=pd.DataFrame(all_records)
        meta=st.session_state.get("meta",{})
        metas={"timestamp":datetime.utcnow().isoformat(),"hotel":meta.get("hotel",""),"bereich":meta.get("bereich",""),"position":meta.get("position",""),"datum":meta.get("datum",""),"teilnehmername":meta.get("teilnehmername",""),"survey_version":"2025-09-listlayout-v18"}
        for k,v in metas.items(): df[k]=v
        st.success("Erfassung abgeschlossen (lokaler Test – Google Sheets nicht konfiguriert).")

st.caption("© Masterarbeit – Intelligente Energiesysteme")
