from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

st.title("Befragung Lastflexibilität – Hotel")
st.caption("Masterarbeit – Intelligente Energiesysteme | Online-Erhebung (mobil & Desktop) – Vereinfachte Version")

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

st.markdown("""
**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
**Geschätzte Dauer:** ~15 Minuten.
""")

consent = st.checkbox("Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.", value=False)
if not consent:
    st.info("Bitte Einverständniserklärung bestätigen.")

labeled_divider("Stammdaten")
col1, col2, col3 = st.columns(3)
with col1:
    hotel = st.text_input("Hotel", placeholder="Hotel Mustermann")
with col2:
    bereich = st.text_input("Bereich/Abteilung", placeholder="Küche, Haustechnik, ...")
with col3:
    position = st.text_input("Position", placeholder="Leitung Küche, Haustechnik, ...")
survey_date = st.date_input("Datum", value=datetime.today())
name = st.text_input("Name (optional)")
confirmation = st.checkbox("Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.")

MOD_OPTS = ["1 – <10 %", "2 – 10–25 %", "3 – 25–40 %", "4 – ≥40 %"]
DAU_OPTS = ["1 – <15 min", "2 – 15–45 min", "3 – 45–120 min", "4 – ≥2 h"]
REB_OPTS = ["1 – sehr stark", "2 – stark", "3 – gering", "4 – kaum"]
BW_OPTS  = ["1 – rigide", "2 – begrenzt", "3 – breit", "4 – frei"]

def choice_to_int(txt: str) -> int:
    return int(str(txt).split("–")[0].strip()) if txt else None

CATALOG = {
    "A) Küche": [
        "Kühlhaus",
        "Tiefkühlhaus",
        "Kühlzentrale",
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

if "index" not in st.session_state:
    st.session_state.index = 0
if "flat_catalog" not in st.session_state:
    st.session_state.flat_catalog = [dev for section in CATALOG.values() for dev in section]
if "records" not in st.session_state:
    st.session_state.records = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False

def device_form(device_name: str):
    st.subheader(device_name)
    colA, colB = st.columns([1,1])
    with colA:
        vorhanden = st.checkbox("Vorhanden", key=f"vh_{device_name}")
    with colB:
        leistung = st.number_input("Leistung (kW, optional)", min_value=0.0, step=0.1, key=f"kw_{device_name}", disabled=not vorhanden)
    st.markdown("**Modulation**"); st.caption("Anpassungsgrad der Leistung")
    mod = st.radio(" ", MOD_OPTS, key=f"mod_{device_name}", disabled=not vorhanden, horizontal=True)
    st.markdown("**Dauer**"); st.caption("Länge der Anpassungsphase")
    dau = st.radio("  ", DAU_OPTS, key=f"dau_{device_name}", disabled=not vorhanden, horizontal=True)
    st.markdown("**Rebound**"); st.caption("Mehrverbrauch nach Anpassung")
    reb = st.radio("   ", REB_OPTS, key=f"reb_{device_name}", disabled=not vorhanden, horizontal=True)
    st.markdown("**Betriebsfenster**"); st.caption("Zeitliche Einsatzflexibilität")
    bw  = st.radio("    ", BW_OPTS, key=f"bw_{device_name}", disabled=not vorhanden, horizontal=True)

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
            "geraet": device_name,
            "vorhanden": bool(vorhanden),
            "leistung_kw": float(leistung) if vorhanden else 0.0,
            "modulation": choice_to_int(mod) if vorhanden else None,
            "dauer": choice_to_int(dau) if vorhanden else None,
            "rebound": choice_to_int(reb) if vorhanden else None,
            "betriebsfenster": choice_to_int(bw) if vorhanden else None,
        }
        st.session_state.records = [r for r in st.session_state.records if r["geraet"] != device_name]
        st.session_state.records.append(rec)
        saved = True
        st.success("Antwort gespeichert.")

    if skip:
        st.session_state.records = [r for r in st.session_state.records if r["geraet"] != device_name]
        saved = True

    if back:
        st.session_state.index = max(0, st.session_state.index - 1)
        st.rerun()

    if saved:
        st.session_state.index = min(len(st.session_state.flat_catalog), st.session_state.index + 1)
        st.rerun()

if consent and confirmation and hotel:
    if st.session_state.index < len(st.session_state.flat_catalog):
        total = len(st.session_state.flat_catalog)
        labeled_divider(f"Frage {st.session_state.index + 1} von {total}")
        device_form(st.session_state.flat_catalog[st.session_state.index])
    else:
        labeled_divider("Abschluss")
        st.success("🎉 Vielen Dank für Ihre Teilnahme!")
        st.markdown("Die Umfrage ist abgeschlossen. Antworten wurden gespeichert und übermittelt.")
        if not st.session_state.submitted:
            if len(st.session_state.records) == 0:
                st.session_state.records.append({
                    "geraet": "(keine Angaben)",
                    "vorhanden": None,
                    "leistung_kw": None,
                    "modulation": None,
                    "dauer": None,
                    "rebound": None,
                    "betriebsfenster": None,
                })
            df = pd.DataFrame(st.session_state.records)
            meta = {
                "timestamp": datetime.utcnow().isoformat(),
                "hotel": hotel,
                "bereich": bereich,
                "position": position,
                "datum": str(survey_date),
                "teilnehmername": name,
                "survey_version": "2025-09-simplified",
            }
            for k, v in meta.items():
                df[k] = v
            cols = [
                "timestamp","datum","hotel","bereich","position","teilnehmername","survey_version",
                "geraet","vorhanden","leistung_kw","modulation","dauer","rebound","betriebsfenster"
            ]
            df = df[cols]
            if "gcp_service_account" in st.secrets and get_gsheet_id():
                st.info(submit_to_gsheets(df))
            else:
                st.warning("Google Sheets ist nicht vollständig konfiguriert.")
            st.session_state.submitted = True
else:
    st.warning("Bitte Einwilligung, Stammdaten und Bestätigung setzen.")

st.caption("© Masterarbeit – Intelligente Energiesysteme")
