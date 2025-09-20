from __future__ import annotations
import io
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# --- Header ---
st.title("Befragung Lastflexibilität – Hotel")
st.caption("Masterarbeit – Intelligente Energiesysteme | Online-Erhebung (mobil & Desktop)")

def labeled_divider(label: str):
    st.markdown(f"---\n###### {label}")

# --- Intro & Consent ---
st.markdown("""
**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
Geschätzte Dauer: 20–30 Minuten.
""")

consent = st.checkbox(
    "Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.",
    value=False,
)
if not consent:
    st.info("Bitte Einverständniserklärung bestätigen, bevor Sie Angaben machen.")

# --- Stammdaten ---
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

# --- Kriterien-Optionen ---
MOD_OPTS = ["1 – <10 %", "2 – 10–25 %", "3 – 25–40 %", "4 – ≥40 %"]
DAU_OPTS = ["1 – <15 min", "2 – 15–45 min", "3 – 45–120 min", "4 – ≥2 h"]
REB_OPTS = ["1 – sehr stark", "2 – stark", "3 – gering", "4 – kaum"]
BW_OPTS  = ["1 – rigide", "2 – begrenzt", "3 – breit", "4 – frei"]

def choice_to_int(txt: str) -> int:
    return int(txt.split("–")[0].strip())

# --- Gerätekatalog ---
CATALOG = [
    "Walk-in Kühlraum",
    "Walk-in Tiefkühlraum",
    "Kühltische / Unterbaukühler",
    "Getränke-/Flaschenkühler",
    "Eismaschine",
    "Kühlanlagenzentrale",
    "Kombidämpfer",
    "Konvektomat / Backofen",
    "Fritteuse",
    "Induktionsherd",
    "Kippbratpfanne",
    "Bain-Marie / Warmhalten",
    "Salamander",
    "Haubenspülmaschine",
    "Bandspülmaschine",
    "Küchenabluft (Haubenlüftung)",
    "Finnische Sauna",
    "Biosauna",
    "Dampfsauna",
    "Pool- Umwälzpumpe",
    "Schwimmbad Abluft",
    "Schwimmbad Zuluft",
    "Schwimmbad Luftentfeuchtung",
    "Zimmerbeleuchtung",
    "Reklame/ Aussenbeleuchtung",
    "Aufzüge",
    "Waschmaschinen",
    "Trockner",
    "Wallbox (EV- Ladepunkte)",
]

# --- Session State ---
if "index" not in st.session_state:
    st.session_state.index = 0
if "records" not in st.session_state:
    st.session_state.records = []

def device_form(device_name: str):
    st.subheader(device_name)

    colA, colB = st.columns([1,1])
    with colA:
        vorhanden = st.checkbox("Vorhanden", key=f"vh_{device_name}")
    with colB:
        leistung = st.number_input("Leistung (kW)", min_value=0.0, step=0.1,
                                   key=f"kw_{device_name}", disabled=not vorhanden)

    # --- Kriterien mit Bedeutungen ---
    st.markdown("**Modulation**")
    st.caption("Anpassungsgrad der Leistung")
    mod = st.radio(" ", MOD_OPTS, key=f"mod_{device_name}", disabled=not vorhanden, horizontal=True)

    st.markdown("**Dauer**")
    st.caption("Länge der Anpassungsphase")
    dau = st.radio("  ", DAU_OPTS, key=f"dau_{device_name}", disabled=not vorhanden, horizontal=True)

    st.markdown("**Rebound**")
    st.caption("Mehrverbrauch nach Anpassung")
    reb = st.radio("   ", REB_OPTS, key=f"reb_{device_name}", disabled=not vorhanden, horizontal=True)

    st.markdown("**Betriebsfenster**")
    st.caption("Zeitliche Einsatzflexibilität")
    bw  = st.radio("    ", BW_OPTS, key=f"bw_{device_name}", disabled=not vorhanden, horizontal=True)

    # --- Navigation ---
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
        st.session_state.index = min(len(CATALOG) - 1, st.session_state.index + 1)
        st.rerun()

# --- Start ---
if consent and confirmation and hotel:
    labeled_divider(f"Frage {st.session_state.index + 1} von {len(CATALOG)}")
    device_form(CATALOG[st.session_state.index])
else:
    st.warning("Bitte Einwilligung, Stammdaten (Hotel) und Abschluss-Bestätigung setzen, um zu starten.")

# --- Export ---
labeled_divider("Export")
export_df = pd.DataFrame(st.session_state.records)
if not export_df.empty:
    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "hotel": hotel,
        "bereich": bereich,
        "position": position,
        "datum": str(survey_date),
        "teilnehmername": name,
        "survey_version": "2025-09",
    }
    for k, v in meta.items():
        export_df[k] = v
    cols = [
        "timestamp","datum","hotel","bereich","position","teilnehmername","survey_version",
        "geraet","vorhanden","leistung_kw","modulation","dauer","rebound","betriebsfenster"
    ]
    export_df = export_df[cols]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, index=False, sheet_name="responses")
    st.download_button(
        "Excel-Datei herunterladen",
        data=buf.getvalue(),
        file_name="befragung_responses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # --- Google Sheets optional ---
    if "gcp_service_account" in st.secrets and "gsheet_id" in st.secrets:
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file",
                ],
            )
            client = gspread.authorize(creds)
            sh = client.open_by_key(st.secrets["gsheet_id"])
            try:
                ws = sh.worksheet("responses")
            except Exception:
                ws = sh.add_worksheet(title="responses", rows="100", cols="20")
                ws.append_row(cols)
            ws.append_rows(export_df.values.tolist())
            st.success("Daten zusätzlich in Google Sheets gespeichert (Tab: responses).")
        except Exception as e:
            st.warning(f"Google Sheets Speicherung nicht möglich: {e}")
    else:
        st.caption("Google Sheets ist optional. Secrets setzen, um direkt ins Sheet zu schreiben.")

st.caption("© Masterarbeit – Intelligente Energiesysteme | Es werden nur für die Erhebung notwendige Daten gespeichert.")
