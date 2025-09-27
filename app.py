from __future__ import annotations
from datetime import datetime
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

SURVEY_VERSION = "2025-09-multipage-v24.2"
ACCENT_RGB = "234, 88, 12"
VISUAL_SCALES = True

STYLE = f"""
<style>
:root {{
  --accent-rgb: {ACCENT_RGB};
  --text-light: #0f172a;
  --muted-light: #334155;
}}
.device-title {{ font-size: 1.2rem; font-weight: 800; margin: 10px 0 4px; color: rgb(var(--accent-rgb)); }}
.separator {{ height: 4px; width: 100%; background: rgba(var(--accent-rgb), .28); border-radius: 2px; margin: 22px 0 16px 0; }}
[data-testid="stCheckbox"] label {{
  font-weight: 700 !important;
  background: rgba(var(--accent-rgb), .08);
  border: 1px solid rgba(var(--accent-rgb), .35);
  padding: 8px 12px;
  border-radius: 12px;
}}
[data-testid="stCheckbox"] input[type="checkbox"] {{ transform: scale(1.2); margin-right: 8px; }}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

# ---------------- Intro ----------------
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

# ---------------- Consent ----------------
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
    st.checkbox("Vor der Teilnahme gelesen und einverstanden.", key="consent")

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
            "hotel": st.session_state.get("hotel",""),
            "bereich": st.session_state.get("bereich",""),
            "position": st.session_state.get("position",""),
            "datum": str(st.session_state.get("datum","")),
            "teilnehmername": st.session_state.get("teilnehmername","")
        }
        st.switch_page("pages/01_Fragebogen.py")
