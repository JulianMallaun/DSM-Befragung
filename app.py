from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# ============ Konfiguration (für schnellen Rückbau der grafischen Skalen) ============
VISUAL_SCALES = True   # ← auf False setzen, um zur alten (nur Radio) Version zurückzugehen

# ============ Feste CI-Farbe: ORANGE ============
ACCENT_RGB = "234, 88, 12"   # #ea580c
PRIMARY_LIGHT_RGB = "14, 165, 233"   # Info-Blau für Box in Light
PRIMARY_DARK_RGB  = "56, 189, 248"   # Info-Blau in Dark

# ============ Styles ============
STYLE = f"""
<style>
:root {{
  --accent-rgb: {ACCENT_RGB};
  --primary-light-rgb: {PRIMARY_LIGHT_RGB};
  --primary-dark-rgb:  {PRIMARY_DARK_RGB};
  --text-light: #0f172a;
  --muted-light: #334155;
  --text-dark: #e5e7eb;
}}

html, body, [class^='css'] {{ color: var(--text-light); }}

/* Consent/Confirm: transparenter Kasten */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border: none !important;
  background: rgba(var(--primary-light-rgb), .16) !important;
  border-radius: 16px !important;
  overflow: hidden !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
  padding: 16px 18px !important;
  background: transparent !important;
}}

/* Globale Trennlinien entfernen */
hr, [data-testid="stMarkdownContainer"] hr {{ display: none !important; }}
.block-container hr {{ display: none !important; }}

/* Abstand & Weißraum (mobile-first freundlicher) */
.block-container {{ padding-top: 1.2rem; }}
h1 {{ margin-bottom: .6rem; }}
h2 {{ margin-top: 1.6rem; margin-bottom: .6rem; }}
.device-title {{ font-size: 1.2rem; font-weight: 800; margin: 10px 0 4px; color: rgb(var(--accent-rgb)); }}
.device-section {{ font-size: .95rem; color: #475569; margin-bottom: 10px; }}

/* Einziger Trennstreifen */
.separator {{
  height: 4px;
  width: 100%;
  background: rgba(var(--accent-rgb), .28);
  border-radius: 2px;
  margin: 22px 0 16px 0;
}}

/* Kriterienblöcke */
.crit-block {{ border-top: none !important; padding-top: 8px; margin-top: 10px; }}
.crit-title {{ font-weight: 700; margin-bottom: 4px; }}
.crit-help {{ font-size: 1rem; line-height: 1.5; margin-bottom: 10px; color: var(--muted-light); }}

/* Grafische Skala (rein visuell, spiegelt die Auswahl) */
.scale-wrap {{ margin: 6px 0 12px 0; }}
.scale-rail {{ position: relative; height: 8px; background: rgba(var(--accent-rgb), .2); border-radius: 999px; }}
.scale-fill {{ position: absolute; left:0; top:0; bottom:0; width: 0%; background: rgba(var(--accent-rgb), .85); border-radius: 999px; transition: width .15s ease; }}
.scale-ticks {{ display: flex; justify-content: space-between; margin-top: 6px; font-size: .9rem; color:#64748b; }}
.scale-ticks span:first-child {{ color:#111827; font-weight:600; }}
.scale-ticks span:last-child  {{ color:#111827; font-weight:600; }}

/* Dark Mode Kontraste */
@media (prefers-color-scheme: dark) {{
  html, body, [class^='css'] {{ color: var(--text-dark); }}
  .crit-help {{ color: rgba(255,255,255,.85); }}
  .device-section {{ color: rgba(255,255,255,.7); }}
  [data-testid="stVerticalBlockBorderWrapper"] {{ background: rgba(var(--primary-dark-rgb), .20) !important; }}
  .scale-rail {{ background: rgba(var(--accent-rgb), .22); }}
  .scale-ticks span {{ color: rgba(255,255,255,.7); }}
  .scale-ticks span:first-child,
  .scale-ticks span:last-child {{ color: rgba(255,255,255,.95); }}
}}

/* Mobile Tweaks */
@media (max-width: 520px) {{
  .crit-help {{ font-size: 1.02rem; line-height: 1.55; }}
  .device-title {{ font-size: 1.24rem; }}
  .separator {{ margin: 20px 0 14px 0; }}
}}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

# Hilfsfunktionen
def get_gsheet_id():
    return (
        st.secrets.get("gsheet_id")
        or st.secrets.get("gcp_service_account", {}).get("gsheet_id")
        or st.secrets.get("gsheet", {}).get("id")
    )

def rows_for_gsheets(df: pd.DataFrame):
    return [[str(r.get(col, "")) if pd.notna(r.get(col)) else "" for col in df.columns] for r in df.to_dict(orient="records")]

GS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

def submit_to_gsheets(df: pd.DataFrame) -> str:
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=GS_SCOPES)
        client = gspread.authorize(creds)
        gsid = get_gsheet_id()
        if not gsid:
            return "⚠️ gsheet_id fehlt."
        sh = client.open_by_key(gsid)
        try:
            ws = sh.worksheet("responses")
        except Exception:
            ws = sh.add_worksheet(title="responses", rows="2000", cols="20")
            ws.append_row(list(df.columns), value_input_option="USER_ENTERED")
        ws.append_rows(rows_for_gsheets(df), value_input_option="USER_ENTERED")
        return f"✅ Übertragung erfolgreich: {sh.title} → Tab 'responses'"
    except Exception as e:
        return f"⚠️ Fehler bei Google Sheets Übertragung: {e}"

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

if "started" not in st.session_state: st.session_state.started = False

# Intro
if not st.session_state.started:
    st.markdown("""**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
**Dauer:** Die Befragung dauert ungefähr **5–7 Minuten**.
""")

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
            st.session_state.meta = {"hotel":sget("hotel",""),"bereich":sget("bereich",""),"position":sget("position",""),"datum":str(sget("datum","")),"teilnehmername":sget("teilnehmername","")}
            st.session_state.started=True
            st.rerun()

# Hauptseite
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

            all_records.append({"section":section,"geraet":dev,"vorhanden":bool(vorhanden),
                                "modulation":int(k1) if vorhanden else None,
                                "dauer":int(k2) if vorhanden else None,
                                "betriebsfenster":int(k4) if vorhanden else None})

    if st.button("Jetzt absenden und speichern",type="primary",use_container_width=True):
        if len(all_records)==0:
            all_records.append({"section":"(keine)","geraet":"(keine)","vorhanden":None,"modulation":None,"dauer":None,"betriebsfenster":None})
        df=pd.DataFrame(all_records)
        meta=st.session_state.get("meta",{})
        metas={"timestamp":datetime.utcnow().isoformat(),"hotel":meta.get("hotel",""),"bereich":meta.get("bereich",""),"position":meta.get("position",""),"datum":meta.get("datum",""),"teilnehmername":meta.get("teilnehmername",""),"survey_version":"2025-09-listlayout-v17"}
        for k,v in metas.items(): df[k]=v
        cols=["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version","section","geraet","vorhanden","modulation","dauer","betriebsfenster"]
        df=df[cols]
        if "gcp_service_account" in st.secrets and get_gsheet_id():
            st.success("Erfassung abgeschlossen. "+submit_to_gsheets(df))
        else:
            st.warning("Google Sheets ist noch nicht konfiguriert.")

st.caption("© Masterarbeit – Intelligente Energiesysteme")
