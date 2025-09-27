from __future__ import annotations
from datetime import datetime
import re
import pandas as pd
import streamlit as st

ACCENT_RGB = "234, 88, 12"
VISUAL_SCALES = True

STYLE = f"""
<style>
:root {{ --accent-rgb: {ACCENT_RGB}; --muted-light:#334155; }}
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
[data-testid="stCheckbox"] label {{ font-weight:700 !important; background: rgba(var(--accent-rgb), .08); border:1px solid rgba(var(--accent-rgb), .35); padding:8px 12px; border-radius:12px; }}
[data-testid="stCheckbox"] input[type="checkbox"] {{ transform: scale(1.2); margin-right:8px; }}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

def clean_section_label(section: str) -> str:
    return re.sub(r'^[A-Z]\)\s*', '', section).strip()

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

# Inhalte
K1_TITLE, K1_SHORT = "Leistung anpassen", "Wie stark kann die Leistung kurzfristig reduziert/verändert werden?"
K1_LABELS = {1:"kaum anpassbar",2:"etwas anpassbar",3:"gut anpassbar",4:"sehr gut anpassbar"}
K2_TITLE, K2_SHORT = "Nutzungsdauer anpassbar", "Wie lange kann die Nutzung/Funktion gedrosselt oder verschoben werden?"
K2_LABELS = {1:"nicht anpassbar",2:"< 15 min",3:"15–45 min",4:"> 45 min"}
K4_TITLE, K4_SHORT = "Zeitliche Flexibilität", "Ist der Einsatz an feste Zeiten gebunden oder frei planbar?"
K4_LABELS = {1:"feste Zeiten",2:"eingeschränkt flexibel",3:"eher flexibel",4:"völlig flexibel"}

CATALOG = {
    "A) Küche": ["Kühlhaus","Tiefkühlhaus","Kombidämpfer","Fritteuse","Induktionsherd","Geschirrspülmaschine"],
    "B) Wellness / Spa / Pool": ["Sauna","Dampfbad","Pool-Umwälzpumpe","Schwimmbad-Lüftung/Entfeuchtung"],
    "C) Zimmer & Allgemeinbereiche": ["Zimmerbeleuchtung","Aufzüge","Waschmaschine","Trockner","Wallbox (E-Ladepunkte)"],
}

def collect_records():
    data=[]
    for section,devices in CATALOG.items():
        for dev in devices:
            vorhanden = st.session_state.get(f"vh_{section}_{dev}", False)
            k1 = st.session_state.get(f"k1_{section}_{dev}")
            k2 = st.session_state.get(f"k2_{section}_{dev}")
            k4 = st.session_state.get(f"k4_{section}_{dev}")
            data.append({
                "section":section, "geraet":dev, "vorhanden":bool(vorhanden),
                "modulation":int(k1) if vorhanden and k1 is not None else "",
                "dauer":int(k2) if vorhanden and k2 is not None else "",
                "betriebsfenster":int(k4) if vorhanden and k4 is not None else ""
            })
    return data

for section,devices in CATALOG.items():
    st.markdown(f"## {section}")
    for idx, dev in enumerate(devices):
        if idx > 0:
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="device-title">{dev}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="device-section">{clean_section_label(section)}</div>', unsafe_allow_html=True)

        vorhanden = st.checkbox("Vorhanden", key=f"vh_{section}_{dev}")
        k1 = criterion_radio_inline(K1_TITLE, K1_SHORT, K1_LABELS, key=f"k1_{section}_{dev}", disabled=not vorhanden)
        k2 = criterion_radio_inline(K2_TITLE, K2_SHORT, K2_LABELS, key=f"k2_{section}_{dev}", disabled=not vorhanden)
        k4 = criterion_radio_inline(K4_TITLE, K4_SHORT, K4_LABELS, key=f"k4_{section}_{dev}", disabled=not vorhanden)

all_records = collect_records()

# Pop-up bei fehlenden Häkchen (hier als einfache Warnkarte + Buttons)
missing = [f"{clean_section_label(r['section'])} – {r['geraet']}" for r in all_records if not r["vorhanden"]]

if st.button("Jetzt absenden und speichern", type="primary", use_container_width=True):
    if len(missing) > 0:
        st.session_state.missing_list = missing
        st.session_state.pending_records = all_records
        st.session_state.show_missing = True
        st.experimental_rerun()
    else:
        st.session_state.missing_list = []
        st.session_state.pending_records = all_records
        st.switch_page("pages/99_Speichern.py")

if st.session_state.get("show_missing"):
    st.warning(f"Es sind **{len(st.session_state.missing_list)} Geräte** nicht als „Vorhanden“ markiert:\n\n" + ", ".join(st.session_state.missing_list))
    colA, colB = st.columns(2)
    with colA:
        if st.button("Weiter bearbeiten", use_container_width=True):
            st.session_state.show_missing = False
            st.experimental_rerun()
    with colB:
        if st.button("Trotzdem absenden", type="primary", use_container_width=True):
            st.switch_page("pages/99_Speichern.py")
