from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# =================== Theme / Farbauswahl ===================
st.sidebar.header("Darstellung")
accent_choice = st.sidebar.selectbox(
    "Akzentfarbe",
    ["Blau", "Smaragd", "Violett", "Orange", "Teal"],
    index=0,
    help="Wähle die Akzentfarbe für Trennstreifen und Gerätekopfzeilen."
)

ACCENTS_RGB = {
    "Blau":    "37, 99, 235",   # #2563eb
    "Smaragd": "5, 150, 105",   # #059669
    "Violett": "124, 58, 237",  # #7c3aed
    "Orange":  "234, 88, 12",   # #ea580c
    "Teal":    "15, 118, 110",  # #0f766e
}
accent_rgb = ACCENTS_RGB[accent_choice]
primary_rgb = "14, 165, 233"   # #0ea5e9 (Kasten)

# =================== Styles ===================
STYLE = f"""
<style>
:root {{ --accent-rgb: {accent_rgb}; --primary-rgb: {primary_rgb}; }}
html, body, [class^='css'] {{ color: #0f172a; }}

/* ---- Consent/Confirm: transparenter Kasten ---- */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border: none !important;
  background: rgba(var(--primary-rgb), .18) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {{
  padding: 14px 16px 16px 16px !important;
  background: transparent !important;
}}

/* ---- Globale Trennlinien entfernen ---- */
hr, [data-testid="stMarkdownContainer"] hr {{ display: none !important; }}
.block-container hr {{ display: none !important; }}

/* ---- Kriterienblöcke: ohne Linie ---- */
.crit-block {{ border-top: none !important; padding-top: 6px; margin-top: 8px; }}
.crit-title {{ font-weight: 700; margin-bottom: 2px; }}
.crit-help {{ font-size: .95rem; margin-bottom: 6px; color:#111827; }}

/* ---- Einziger Trennstreifen ---- */
.separator {{
  height: 4px;
  width: 100%;
  background: rgba(var(--accent-rgb), .28);
  border-radius: 2px;
  margin: 18px 0 12px 0;
}}

/* ==== Gerätekopf ==== */
.device-title {{
  font-size: 1.2rem;          /* größer */
  font-weight: 800;
  margin: 6px 0 2px;
  color: rgb(var(--accent-rgb)); /* Akzentfarbe */
}}
.device-section {{
  font-size: .94rem;
  color: #475569;
  margin-bottom: 8px;
}}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

# =================== Helpers ===================
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

def criterion_radio_inline(title: str, short_desc: str, labels_map: dict[int,str], key: str, disabled: bool):
    st.markdown('<div class="crit-block">', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-help">{short_desc}</div>', unsafe_allow_html=True)
    options = [1,2,3,4]
    def fmt(v: int): return f"{v} – {labels_map.get(v, '')}"
    value = st.radio("", options, key=key, disabled=disabled, horizontal=True, format_func=fmt, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    return value

# =================== Kriterien ===================
K1_TITLE, K1_SHORT = "Leistung anpassen", "Wie stark kann die Leistung kurzfristig reduziert/verändert werden?"
K1_LABELS = {1:"kaum anpassbar",2:"etwas anpassbar",3:"gut anpassbar",4:"sehr gut anpassbar"}
K2_TITLE, K2_SHORT = "Nutzungsdauer anpassbar", "Wie lange kann die Nutzung/Funktion gedrosselt oder verschoben werden?"
K2_LABELS = {1:"nicht anpassbar",2:"< 15 min",3:"15–45 min",4:"> 45 min"}
K4_TITLE, K4_SHORT = "Zeitliche Flexibilität", "Ist der Einsatz an feste Zeiten gebunden oder frei planbar?"
K4_LABELS = {1:"feste Zeiten",2:"eingeschränkt flexibel",3:"eher flexibel",4:"völlig flexibel"}

# =================== Katalog ===================
CATALOG = {
    "A) Küche": ["Kühlhaus","Tiefkühlhaus","Kombidämpfer","Fritteuse","Induktionsherd","Geschirrspülmaschine"],
    "B) Wellness / Spa / Pool": ["Sauna","Dampfbad","Pool-Umwälzpumpe","Schwimmbad-Lüftung/Entfeuchtung"],
    "C) Zimmer & Allgemeinbereiche": ["Zimmerbeleuchtung","Aufzüge","Waschmaschine","Trockner","Wallbox (E-Ladepunkte)"],
}

if "started" not in st.session_state: st.session_state.started = False

# =================== Intro-Seite ===================
if not st.session_state.started:
    st.markdown("""**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.""")

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

# =================== Hauptseite (Liste) ===================
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
        metas={"timestamp":datetime.utcnow().isoformat(),"hotel":meta.get("hotel",""),"bereich":meta.get("bereich",""),"position":meta.get("position",""),"datum":meta.get("datum",""),"teilnehmername":meta.get("teilnehmername",""),"survey_version":"2025-09-listlayout-v15"}
        for k,v in metas.items(): df[k]=v
        cols=["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version","section","geraet","vorhanden","modulation","dauer","betriebsfenster"]
        df=df[cols]
        if "gcp_service_account" in st.secrets and get_gsheet_id():
            st.success("Erfassung abgeschlossen. "+submit_to_gsheets(df))
        else:
            st.warning("Google Sheets ist noch nicht konfiguriert.")

st.caption("© Masterarbeit – Intelligente Energiesysteme")
