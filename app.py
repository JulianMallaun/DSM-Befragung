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
    help="Wähle die Akzentfarbe für Kartenstreifen, Trennlinien und wichtige Boxen."
)

ACCENTS = {
    "Blau":   {"600": "#2563eb", "100": "#dbeafe"},
    "Smaragd":{"600": "#059669", "100": "#d1fae5"},
    "Violett":{"600": "#7c3aed", "100": "#ede9fe"},
    "Orange": {"600": "#ea580c", "100": "#ffedd5"},
    "Teal":   {"600": "#0f766e", "100": "#ccfbf1"},
}

accent_600 = ACCENTS[accent_choice]["600"]
accent_100 = ACCENTS[accent_choice]["100"]
primary_600 = "#0ea5e9"  # Hinweis-Boxen bleiben blau
primary_100 = "#f0f9ff"

# =================== Styles ===================
STYLE = f"""
<style>
:root {{
  --accent-600: {accent_600};
  --accent-100: {accent_100};
  --primary-600: {primary_600};
  --primary-100: {primary_100};
  --surface: #f8fafc;
  --card: #ffffff;
  --text: #0f172a;
  --subtle: #475569;
  --border: #e2e8f0;
}}

html, body, [class^="css"] {{ color: var(--text); }}

/* Style den CONTAINER selbst via :has(), damit Checkbox + Text zusammen eingerahmt sind */
div:has(> .consent-anchor), div:has(> .confirm-anchor) {{
  border: 2px solid var(--primary-600);
  background: var(--primary-100);
  padding: 16px;
  border-radius: 14px;
  margin: 12px 0 16px 0;
  box-shadow: 0 1px 0 rgba(0,0,0,.02), 0 1px 2px rgba(0,0,0,.04);
}}
.consent-anchor, .confirm-anchor {{ display:none; }}
/* Listen im Kasten */
div:has(> .consent-anchor) ul {{ margin: 0 0 10px 1rem; }}
div:has(> .consent-anchor) li {{ margin: 2px 0; }}

/* Gerätekarte – deutliche Abgrenzung, moderner Look */
.device-card {{
  position: relative;
  background: var(--card);
  padding: 18px;
  border-radius: 16px;
  margin: 20px 0;
  border: 2px solid color-mix(in oklab, var(--accent-600) 40%, var(--border));
  box-shadow: 0 3px 6px rgba(0,0,0,.06), 0 10px 22px rgba(0,0,0,.06);
}}
.device-card::before {{
  content: "";
  position: absolute; left: 0; top: 0; bottom: 0; width: 10px;
  background: var(--accent-600);
  border-top-left-radius: 16px; border-bottom-left-radius: 16px;
}}

.device-title {{ font-size: 1.12rem; font-weight: 800; margin-bottom: 4px; }}
.device-section {{ font-size: .95rem; color: var(--subtle); margin-bottom: 10px; }}

/* Kriterienblock */
.crit-block {{ border-top: 1px solid var(--border); padding-top: 10px; margin-top: 12px; }}
.crit-title {{ font-weight: 700; margin-bottom: 2px; }}
.crit-help {{ font-size: .95rem; margin-bottom: 6px; }}
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
    with st.container():
        # ANCHOR -> Container wird zum blauen Kasten (Text + Checkbox drin)
        st.markdown('<span class="consent-anchor"></span>', unsafe_allow_html=True)
        st.markdown(
            """
<ul>
  <li>Teilnahme ist freiwillig, Abbruch jederzeit ohne Nachteile.</li>
  <li>Verwendung ausschließlich zu wissenschaftlichen Zwecken.</li>
  <li>Anonymisierte Erhebung.</li>
  <li>Einsicht nur für berechtigte Personen.</li>
</ul>
""",
            unsafe_allow_html=True,
        )
        st.checkbox("✅ Ich habe die Informationen gelesen und bin einverstanden.", key="consent")

    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("Hotel (Pflicht)", key="hotel")
    with col2: st.text_input("Bereich/Abteilung (Pflicht)", key="bereich")
    with col3: st.text_input("Position (Pflicht)", key="position")
    st.date_input("Datum", value=datetime.today(), key="datum")
    st.text_input("Name (optional)", key="teilnehmername")

    with st.container():
        # ANCHOR -> zweiter Kasten
        st.markdown('<span class="confirm-anchor"></span>', unsafe_allow_html=True)
        st.checkbox("✅ Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.", key="confirm")

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
        for dev in devices:
            st.markdown('<div class="device-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="device-title">{dev}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="device-section">{section}</div>', unsafe_allow_html=True)

            vorhanden = st.checkbox("Vorhanden", key=f"vh_{section}_{dev}")

            # Kriterien mit Inline-Beschriftung
            k1 = criterion_radio_inline(K1_TITLE, K1_SHORT, K1_LABELS, key=f"k1_{section}_{dev}", disabled=not vorhanden)
            k2 = criterion_radio_inline(K2_TITLE, K2_SHORT, K2_LABELS, key=f"k2_{section}_{dev}", disabled=not vorhanden)
            k4 = criterion_radio_inline(K4_TITLE, K4_SHORT, K4_LABELS, key=f"k4_{section}_{dev}", disabled=not vorhanden)

            all_records.append({"section":section,"geraet":dev,"vorhanden":bool(vorhanden),
                                "modulation":int(k1) if vorhanden else None,
                                "dauer":int(k2) if vorhanden else None,
                                "betriebsfenster":int(k4) if vorhanden else None})
            st.markdown('</div>', unsafe_allow_html=True)  # end device-card

    st.markdown("---")
    if st.button("Jetzt absenden und speichern",type="primary",use_container_width=True):
        if len(all_records)==0:
            all_records.append({"section":"(keine)","geraet":"(keine)","vorhanden":None,"modulation":None,"dauer":None,"betriebsfenster":None})
        df=pd.DataFrame(all_records)
        meta=st.session_state.get("meta",{})
        metas={"timestamp":datetime.utcnow().isoformat(),"hotel":meta.get("hotel",""),"bereich":meta.get("bereich",""),"position":meta.get("position",""),"datum":meta.get("datum",""),"teilnehmername":meta.get("teilnehmername",""),"survey_version":"2025-09-listlayout-v8"}
        for k,v in metas.items(): df[k]=v
        cols=["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version","section","geraet","vorhanden","modulation","dauer","betriebsfenster"]
        df=df[cols]
        if "gcp_service_account" in st.secrets and get_gsheet_id():
            st.success("Erfassung abgeschlossen. "+submit_to_gsheets(df))
        else:
            st.warning("Google Sheets ist noch nicht konfiguriert.")

st.caption("© Masterarbeit – Intelligente Energiesysteme")
