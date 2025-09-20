
from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# ----------------- Styles -----------------
st.markdown(
    '''
    <style>
    /* Echter horizontaler Trennstrich pro Kriterium */
    .crit-block{
        border-top: 3px solid #0f766e;
        padding: 10px 0 12px 0;
        margin: 12px 0 12px 0;
        background: transparent;
        border-radius: 0;
    }
    .crit-title{ font-size:1.12rem; font-weight:600; margin-bottom:2px; color:#0f172a; }
    .crit-help{ font-size:0.9rem; color:#6b7280; margin-bottom:6px; }
    </style>
    ''', unsafe_allow_html=True
)

st.title("Befragung Lastflexibilität – Hotel")

# ----------------- Helpers -----------------
def labeled_divider(label: str):
    st.markdown(f"---\n###### {label}")

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
            ws = sh.add_worksheet(title="responses", rows="100", cols="20")
            ws.append_row(list(df.columns), value_input_option="USER_ENTERED")
        rows = rows_for_gsheets(df)
        ws.append_rows(rows, value_input_option="USER_ENTERED")
        return f"✅ Übertragung erfolgreich: {sh.title} → Tab 'responses'"
    except Exception as e:
        return f"⚠️ Fehler bei Google Sheets Übertragung: {e}"

def criterion_block(title: str, helptext: str | None, options: list, key: str, disabled: bool):
    st.markdown('<div class="crit-block">', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-title">{title}</div>', unsafe_allow_html=True)
    if helptext:
        st.markdown(f'<div class="crit-help">{helptext}</div>', unsafe_allow_html=True)
    value = st.radio("", options, key=key, disabled=disabled, horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    return value

def choice_to_int(txt: str) -> int:
    return int(str(txt).split("–")[0].strip()) if txt else None

def sget(key: str, default: str = ""):
    return st.session_state.get(key, default)

# ----------------- Kriterien-Optionen -----------------
K1_OPTS = ["1 – kaum anpassbar","2 – etwas anpassbar","3 – gut anpassbar","4 – sehr gut anpassbar"]
K2_OPTS = ["1 – <15 min","2 – 15–45 min","3 – 45–120 min","4 – ≥2 h"]
K3_OPTS = ["1 – sehr viel Extraenergie","2 – viel Extraenergie","3 – wenig Extraenergie","4 – kaum Extraenergie"]
K4_OPTS = ["1 – feste Zeiten","2 – eingeschränkt flexibel","3 – eher flexibel","4 – völlig flexibel"]

# ----------------- Katalog -----------------
CATALOG = {
    "A) Küche": [
        "Kühlhaus",
        "Tiefkühlhaus",
        "Kombidämpfer",
        "Fritteuse",
        "Induktionsherd",
        "Geschirrspülmaschine",
    ],
    "B) Wellness / Spa / Pool": [
        "Sauna",
        "Dampfbad",
        "Pool-Umwälzpumpe",
        "Schwimmbad-Lüftung/Entfeuchtung",
    ],
    "C) Zimmer & Allgemeinbereiche": [
        "Zimmerbeleuchtung",
        "Aufzüge",
        "Waschmaschine",
        "Trockner",
        "Wallbox (E-Ladepunkte)",
    ],
}

# ----------------- Session -----------------
if "index" not in st.session_state: st.session_state.index = 0
if "started" not in st.session_state: st.session_state.started = False
if "flat_catalog" not in st.session_state:
    st.session_state.flat_catalog = [(sec, dev) for sec, devices in CATALOG.items() for dev in devices]
if "records" not in st.session_state: st.session_state.records = []
if "submitted" not in st.session_state: st.session_state.submitted = False

# Optionaler Reset in der Sidebar
with st.sidebar:
    if st.button("🔄 Befragung zurücksetzen"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

# ----------------- Intro & Stammdaten -----------------
if not st.session_state.started:
    st.markdown(
        '''
        **Einleitung**  
        Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
        Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
        **Geschätzte Dauer:** ~15 Minuten.
        '''
    )

    st.markdown(
        '''
        ### Einverständniserklärung
        Mit der Teilnahme an dieser Befragung erklären Sie sich einverstanden, dass:

        - Ihre Teilnahme freiwillig erfolgt und Sie den Fragebogen jederzeit abbrechen können, ohne dass Ihnen dadurch Nachteile entstehen.  
        - Ihre Angaben ausschließlich zu wissenschaftlichen Zwecken im Rahmen einer Masterarbeit an der FH Burgenland verwendet werden.  
        - Ihre Daten anonymisiert erhoben und ausgewertet werden, sodass keine Rückschlüsse auf einzelne Personen oder Betriebe möglich sind.  
        - Die Ergebnisse ausschließlich von berechtigten Personen (z. B. Betreuerinnen, Gutachterinnen) eingesehen werden.  

        **Mit dem Ausfüllen und Absenden des Fragebogens geben Sie Ihre Zustimmung zur Teilnahme.**
        '''
    )

    consent = st.checkbox("Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.", value=False, key="consent")
    labeled_divider("Stammdaten")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Hotel", placeholder="Hotel Mustermann", key="hotel")
    with col2:
        st.text_input("Bereich/Abteilung", placeholder="Küche, Haustechnik, ...", key="bereich")
    with col3:
        st.text_input("Position", placeholder="Leitung Küche, Haustechnik, ...", key="position")
    st.date_input("Datum", value=datetime.today(), key="datum")
    st.text_input("Name (optional)", key="teilnehmername")
    st.checkbox("Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.", key="confirm")

    start = st.button("Start – zur ersten Frage →", type="primary", use_container_width=True)
    if start:
        missing = []
        if not st.session_state.get("consent"): missing.append("Einverständniserklärung")
        if not st.session_state.get("confirm"): missing.append("Bestätigung")
        if not st.session_state.get("hotel"): missing.append("Hotel")
        if missing:
            st.warning("Bitte folgende Punkte noch erledigen: " + ", ".join(missing))
        else:
            st.session_state.meta = {
                "hotel": sget("hotel"),
                "bereich": sget("bereich"),
                "position": sget("position"),
                "datum": sget("datum"),
                "teilnehmername": sget("teilnehmername"),
            }
            # Sicherheitsnetz
            if not st.session_state.get("flat_catalog"):
                st.session_state.flat_catalog = [(sec, dev) for sec, devs in CATALOG.items() for dev in devs]
            st.session_state.index = 0
            st.session_state.started = True
            st.rerun()

# ----------------- Formular pro Gerät -----------------
def device_form(section: str, device_name: str):
    st.header(section)
    st.subheader(device_name)

    colA, colB = st.columns([1,1])
    with colA:
        vorhanden = st.checkbox("Vorhanden", key=f"vh_{device_name}")
    with colB:
        leistung = st.number_input("Leistung (kW, optional)", min_value=0.0, step=0.1, key=f"kw_{device_name}", disabled=not vorhanden)

    k1 = criterion_block("Leistung anpassen", None, K1_OPTS, key=f"k1_{device_name}", disabled=not vorhanden)
    k2 = criterion_block("Nutzungsdauer anpassbar", "wie lange drosselbar?", K2_OPTS, key=f"k2_{device_name}", disabled=not vorhanden)
    k3 = criterion_block("Energie-Nachholen", "braucht viel Extraenergie nach Drosselung?", K3_OPTS, key=f"k3_{device_name}", disabled=not vorhanden)
    k4 = criterion_block("Zeitliche Flexibilität", "fixe Zeiten oder frei?", K4_OPTS, key=f"k4_{device_name}", disabled=not vorhanden)

    cols_btn = st.columns([1,1,1])
    with cols_btn[0]:
        back = st.button("← Zurück", use_container_width=True, disabled=st.session_state.index == 0)
    with cols_btn[1]:
        skip = st.button("Überspringen", use_container_width=True)
    with cols_btn[2]:
        next_btn = st.button("Speichern & Weiter →", type="primary", use_container_width=True)

    saved = False
    if next_btn:
        rec = {
            "section": section,
            "geraet": device_name,
            "vorhanden": bool(vorhanden),
            "leistung_kw": float(leistung) if vorhanden else 0.0,
            "modulation": choice_to_int(k1) if vorhanden else None,
            "dauer": choice_to_int(k2) if vorhanden else None,
            "rebound": choice_to_int(k3) if vorhanden else None,
            "betriebsfenster": choice_to_int(k4) if vorhanden else None,
        }
        st.session_state.records = [r for r in st.session_state.records if not (r.get("section")==section and r["geraet"]==device_name)]
        st.session_state.records.append(rec)
        saved = True
        st.success("Antwort gespeichert.")

    if skip:
        st.session_state.records = [r for r in st.session_state.records if not (r.get("section")==section and r["geraet"]==device_name)]
        saved = True

    if back:
        st.session_state.index = max(0, st.session_state.index - 1)
        st.rerun()

    if saved:
        st.session_state.index = min(len(st.session_state.flat_catalog), st.session_state.index + 1)
        st.rerun()

# ----------------- Flow -----------------
if st.session_state.started:
    total = len(st.session_state.flat_catalog)
    if st.session_state.index < total:
        section, device = st.session_state.flat_catalog[st.session_state.index]
        device_form(section, device)
    else:
        labeled_divider("Abschluss")
        st.success("🎉 Vielen Dank für Ihre Teilnahme!")
        st.markdown("Die Umfrage ist abgeschlossen. Antworten wurden gespeichert und übermittelt.")
        if not st.session_state.submitted:
            if len(st.session_state.records) == 0:
                st.session_state.records.append({
                    "section": "(keine)",
                    "geraet": "(keine Angaben)",
                    "vorhanden": None,
                    "leistung_kw": None,
                    "modulation": None,
                    "dauer": None,
                    "rebound": None,
                    "betriebsfenster": None,
                })
            df = pd.DataFrame(st.session_state.records)
            meta_from_start = st.session_state.get("meta", {})
            meta = {
                "timestamp": datetime.utcnow().isoformat(),
                "hotel": meta_from_start.get("hotel", sget("hotel")),
                "bereich": meta_from_start.get("bereich", sget("bereich")),
                "position": meta_from_start.get("position", sget("position")),
                "datum": str(meta_from_start.get("datum", sget("datum"))),
                "teilnehmername": meta_from_start.get("teilnehmername", sget("teilnehmername")),
                "survey_version": "2025-09-py313-full",
            }
            for k, v in meta.items():
                df[k] = v
            cols = ["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version",
                    "section","geraet","vorhanden","leistung_kw","modulation","dauer","rebound","betriebsfenster"]
            df = df[cols]
            if "gcp_service_account" in st.secrets and get_gsheet_id():
                st.info(submit_to_gsheets(df))
            else:
                st.warning("Google Sheets ist nicht vollständig konfiguriert.")
            st.session_state.submitted = True

st.caption("© Masterarbeit – Intelligente Energiesysteme")
