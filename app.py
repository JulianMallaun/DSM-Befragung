
from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

st.title("Befragung Lastflexibilität – Hotel")
st.caption("Masterarbeit – Intelligente Energiesysteme | Online-Erhebung")

# --- Helper: robust gsheet_id getter ---
def get_gsheet_id():
    return (
        st.secrets.get("gsheet_id")
        or st.secrets.get("gcp_service_account", {}).get("gsheet_id")
        or st.secrets.get("gsheet", {}).get("id")
    )

# --- Intro ---
st.markdown("""
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
Geschätzte Dauer: 20–30 Minuten.
""")

consent = st.checkbox("Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.", value=False)
if not consent:
    st.info("Bitte Einverständniserklärung bestätigen, bevor Sie Angaben machen.")

hotel = st.text_input("Hotel")
bereich = st.text_input("Bereich/Abteilung")
position = st.text_input("Position")
survey_date = st.date_input("Datum", value=datetime.today())
name = st.text_input("Name (optional)")
confirmation = st.checkbox("Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.")

CATALOG = ["Walk-in Kühlraum", "Walk-in Tiefkühlraum"]  # gekürzt für Debug

if "index" not in st.session_state:
    st.session_state.index = 0
if "records" not in st.session_state:
    st.session_state.records = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False

def device_form(dev):
    st.subheader(dev)
    vorhanden = st.checkbox("Vorhanden", key=f"vh_{dev}")
    if st.button("Weiter", key=f"next_{dev}"):
        rec = {"geraet": dev, "vorhanden": vorhanden}
        st.session_state.records.append(rec)
        st.session_state.index += 1
        st.rerun()

def submit_to_gsheets(df: pd.DataFrame) -> str:
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        sh = client.open_by_key(get_gsheet_id())
        try:
            ws = sh.worksheet("responses")
        except Exception:
            ws = sh.add_worksheet(title="responses", rows="100", cols="20")
            ws.append_row(list(df.columns))
        ws.append_rows(df.values.tolist())
        return "✅ Erfolgreich an Google Sheets übertragen."
    except Exception as e:
        return f"⚠️ Fehler bei Google Sheets Übertragung: {e}"

if consent and confirmation and hotel:
    if st.session_state.index < len(CATALOG):
        device_form(CATALOG[st.session_state.index])
    else:
        st.success("🎉 Vielen Dank für Ihre Teilnahme! Die Umfrage ist nun abgeschlossen.")
        if not st.session_state.submitted:
            df = pd.DataFrame(st.session_state.records)
            meta = {
                "timestamp": datetime.utcnow().isoformat(),
                "hotel": hotel,
                "bereich": bereich,
                "position": position,
                "datum": str(survey_date),
                "teilnehmername": name,
            }
            for k, v in meta.items():
                df[k] = v
            if "gcp_service_account" in st.secrets and get_gsheet_id():
                st.info(submit_to_gsheets(df))
            else:
                st.warning("Google Sheets nicht konfiguriert (Service-Account oder gsheet_id fehlt).")
            st.session_state.submitted = True

# --- Diagnose-Block: Secrets ---
with st.expander("Diagnose: Secrets-Übersicht", expanded=False):
    import json
    st.write("Top-Level Keys:", list(st.secrets.keys()))
    if "gcp_service_account" in st.secrets:
        st.write("Keys in gcp_service_account:", list(st.secrets["gcp_service_account"].keys()))
    try:
        st.code(json.dumps(dict(st.secrets), indent=2))
    except Exception as e:
        st.write(f"(Secrets nicht serialisierbar: {e})")

with st.expander("Diagnose: Google-Anbindung testen", expanded=False):
    if st.button("Google-Anbindung testen"):
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
            ]
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
            client = gspread.authorize(creds)
            sh = client.open_by_key(get_gsheet_id())
            st.success(f"Verbunden mit Spreadsheet: {sh.title}")
        except Exception as e:
            st.error(f"Fehler: {e}")
