from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# =================== Styles ===================
st.markdown(
    """
    <style>
    .consent-box {
        border: 2px solid #0ea5e9;
        background: #f0f9ff;
        padding: 14px;
        border-radius: 10px;
        margin: 6px 0 12px 0;
    }
    .consent-title { font-weight: 700; margin-bottom: 6px; color: #0f172a; }
    .consent-note { color: #334155; font-size: 0.95rem; }

    .device-divider { border-top: 2px solid #0f766e22; margin: 16px 0; }

    .crit-block { border-top: 2px solid #0f766e33; padding-top: 6px; margin-top: 8px; }
    .crit-title{ font-size: 1.06rem; font-weight: 700; margin-bottom: 2px; color: #0f172a; }
    .crit-help{ font-size: 0.95rem; color: #111827; margin-bottom: 6px; }
    .crit-explain{ font-size: 0.9rem; color: #374151; margin: 6px 0 0 0; }

    .opt-legend { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 6px; }
    .opt-item  { display: flex; align-items: baseline; gap: 6px; }
    .crit-number { font-size: 1.15rem; font-weight: 800; color:#111827; }
    .crit-desc   { font-size: 0.9rem; color:#6b7280; }
    </style>
    """
    , unsafe_allow_html=True,
)

st.title("Befragung Lastflexibilität – Hotel")

# Helpers
def labeled_divider(label: str):
    st.markdown(f"""---
###### {label}""")

def get_gsheet_id():
    return (
        st.secrets.get("gsheet_id")
        or st.secrets.get("gcp_service_account", {}).get("gsheet_id")
        or st.secrets.get("gsheet", {}).get("id")
    )

def rows_for_gsheets(df: pd.DataFrame):
    records = df.to_dict(orient="records")
    rows = []
    for r in records:
        row = []
        for col in df.columns:
            v = r.get(col, None)
            if v is None or (isinstance(v, float) and v != v):
                row.append("")
            else:
                row.append(str(v))
        rows.append(row)
    return rows

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
        rows = rows_for_gsheets(df)
        ws.append_rows(rows, value_input_option="USER_ENTERED")
        return f"✅ Übertragung erfolgreich: {sh.title} → Tab 'responses'"
    except Exception as e:
        return f"⚠️ Fehler bei Google Sheets Übertragung: {e}"

def sget(key: str, default=None):
    return st.session_state.get(key, default)

def criterion_block(title: str, short_desc: str, legend_items: list[tuple[str, str]], key: str, disabled: bool):
    st.markdown('<div class="crit-block">', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-help">{short_desc}</div>', unsafe_allow_html=True)
    value = st.radio("", [1,2,3,4], key=key, disabled=disabled, horizontal=True, label_visibility="collapsed")
    legend_html = '<div class="opt-legend">'
    for num, txt in legend_items:
        legend_html += f'<div class="opt-item"><span class="crit-number">{num}</span><span class="crit-desc">– {txt}</span></div>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return value

# Kriterien
K1_TITLE, K1_SHORT = "Leistung anpassen", "Wie stark kann die Leistung kurzfristig reduziert/verändert werden?"
K1_LEGEND = [("1","kaum anpassbar"),("2","etwas anpassbar"),("3","gut anpassbar"),("4","sehr gut anpassbar")]

K2_TITLE, K2_SHORT = "Nutzungsdauer anpassbar", "Wie lange kann die Nutzung/Funktion gedrosselt oder verschoben werden?"
K2_LEGEND = [("1","nicht anpassbar"),("2","< 15 min"),("3","15–45 min"),("4","> 45 min")]

K4_TITLE, K4_SHORT = "Zeitliche Flexibilität", "Ist der Einsatz an feste Zeiten gebunden oder frei planbar?"
K4_LEGEND = [("1","feste Zeiten"),("2","eingeschränkt flexibel"),("3","eher flexibel"),("4","völlig flexibel")]

# Katalog
CATALOG = {
    "A) Küche": ["Kühlhaus","Tiefkühlhaus","Kombidämpfer","Fritteuse","Induktionsherd","Geschirrspülmaschine"],
    "B) Wellness / Spa / Pool": ["Sauna","Dampfbad","Pool-Umwälzpumpe","Schwimmbad-Lüftung/Entfeuchtung"],
    "C) Zimmer & Allgemeinbereiche": ["Zimmerbeleuchtung","Aufzüge","Waschmaschine","Trockner","Wallbox (E-Ladepunkte)"],
}

if "started" not in st.session_state: st.session_state.started = False

# Intro-Seite
if not st.session_state.started:
    st.markdown("""**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.""")
    st.subheader("Einverständniserklärung")
    st.markdown('<div class="consent-box"><div class="consent-title">Bitte bestätigen Sie folgende Punkte:</div>', unsafe_allow_html=True)
    st.markdown("• Teilnahme ist freiwillig, Abbruch jederzeit ohne Nachteile.<br/>• Verwendung ausschließlich zu wissenschaftlichen Zwecken.<br/>• Anonymisierte Erhebung.<br/>• Einsicht nur für berechtigte Personen.", unsafe_allow_html=True)
    st.checkbox("✅ Ich habe die Informationen gelesen und bin einverstanden.", key="consent")
    st.markdown('</div>', unsafe_allow_html=True)
    labeled_divider("Stammdaten")
    col1, col2, col3 = st.columns(3)
    with col1: st.text_input("Hotel (Pflicht)", key="hotel")
    with col2: st.text_input("Bereich/Abteilung (Pflicht)", key="bereich")
    with col3: st.text_input("Position (Pflicht)", key="position")
    st.date_input("Datum", value=datetime.today(), key="datum")
    st.text_input("Name (optional)", key="teilnehmername")
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
    st.subheader("Gerätekatalog – bitte alles der Reihe nach ausfüllen")
    all_records=[]
    for section,devices in CATALOG.items():
        st.markdown(f"### {section}")
        for dev in devices:
            st.markdown('<div class="device-divider"></div>', unsafe_allow_html=True)
            st.markdown(f"**{dev}**")
            c1,c2=st.columns([1,1])
            with c1: vorhanden=st.checkbox("Vorhanden",key=f"vh_{section}_{dev}")
            with c2: kw=st.number_input("Leistung (kW, optional)",min_value=0.0,step=0.1,key=f"kw_{section}_{dev}",disabled=not vorhanden)
            k1=criterion_block(K1_TITLE,K1_SHORT,K1_LEGEND,key=f"k1_{section}_{dev}",disabled=not vorhanden)
            k2=criterion_block(K2_TITLE,K2_SHORT,K2_LEGEND,key=f"k2_{section}_{dev}",disabled=not vorhanden)
            k4=criterion_block(K4_TITLE,K4_SHORT,K4_LEGEND,key=f"k4_{section}_{dev}",disabled=not vorhanden)
            all_records.append({"section":section,"geraet":dev,"vorhanden":bool(vorhanden),"leistung_kw":float(kw) if vorhanden else 0.0,"modulation":int(k1) if vorhanden else None,"dauer":int(k2) if vorhanden else None,"betriebsfenster":int(k4) if vorhanden else None})
    st.markdown("---")
    if st.button("Jetzt absenden und speichern",type="primary",use_container_width=True):
        if len(all_records)==0: all_records.append({"section":"(keine)","geraet":"(keine)","vorhanden":None,"leistung_kw":None,"modulation":None,"dauer":None,"betriebsfenster":None})
        df=pd.DataFrame(all_records)
        meta=st.session_state.get("meta",{})
        metas={"timestamp":datetime.utcnow().isoformat(),"hotel":meta.get("hotel",""),"bereich":meta.get("bereich",""),"position":meta.get("position",""),"datum":meta.get("datum",""),"teilnehmername":meta.get("teilnehmername",""),"survey_version":"2025-09-listlayout-v2"}
        for k,v in metas.items(): df[k]=v
        cols=["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version","section","geraet","vorhanden","leistung_kw","modulation","dauer","betriebsfenster"]
        df=df[cols]
        if "gcp_service_account" in st.secrets and get_gsheet_id(): st.success("Erfassung abgeschlossen. "+submit_to_gsheets(df))
        else: st.warning("Google Sheets ist noch nicht konfiguriert.")
st.caption("© Masterarbeit – Intelligente Energiesysteme")
