from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

SURVEY_VERSION = "2025-09-multipage-v24.1"
ACCENT_RGB = "234, 88, 12"

STYLE = f"""
<style>
:root {{ --accent-rgb:{ACCENT_RGB}; }}
.outro {{ text-align:center; padding: 12vh 4vw; }}
.outro .check {{ font-size: 64px; line-height: 1; margin-bottom: 12px; }}
.outro h2 {{ margin: 0 0 8px 0; }}
.outro .card {{ background: rgba(var(--accent-rgb), .06); border-radius: 14px; padding: 12px; margin: 14px auto; max-width: 40rem; }}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

st.title("Befragung Lastflexibilität – Hotel")

def get_gsheet_id():
    return (
        st.secrets.get("gsheet_id")
        or st.secrets.get("gcp_service_account", {}).get("gsheet_id")
        or st.secrets.get("gsheet", {}).get("id")
    )

GS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

def submit_to_gsheets(df):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if "gcp_service_account" not in st.secrets:
            return "⚠️ Google Sheets: Service Account Secret fehlt."
        gsid = get_gsheet_id()
        if not gsid:
            return "⚠️ Google Sheets: gsheet_id fehlt."
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=GS_SCOPES)
        client = gspread.authorize(creds)
        sh = client.open_by_key(gsid)
        try:
            ws = sh.worksheet("responses")
        except Exception:
            ws = sh.add_worksheet(title="responses", rows="2000", cols="32")
            header = ["timestamp","datum","hotel","bereich","position","teilnehmername","survey_version",
                      "geraet","vorhanden","leistung_kw","modulation","dauer","rebound","betriebsfenster"]
            ws.append_row(header, value_input_option="USER_ENTERED")
        header = ws.row_values(1)
        for col in header:
            if col not in df.columns:
                df[col] = ""
        df = df.reindex(columns=header, fill_value="")
        values = [[str(r.get(c, "")) if pd.notna(r.get(c)) else "" for c in df.columns]
                  for r in df.to_dict(orient="records")]
        ws.append_rows(values, value_input_option="USER_ENTERED")
        return f"✅ Übertragen nach Google Sheet: {sh.title} – Tab 'responses'."
    except Exception as e:
        return f"⚠️ Google Sheets Fehler: {e}"

# Daten laden
all_records = st.session_state.get("pending_records", [])
meta = st.session_state.get("meta", {})
if not all_records or not meta:
    st.warning("Es liegen keine Daten zum Speichern vor.")
    st.stop()

import pandas as pd
df = pd.DataFrame(all_records)
metas = {
    "timestamp": datetime.utcnow().isoformat(),
    "datum": meta.get("datum",""),
    "hotel": meta.get("hotel",""),
    "bereich": meta.get("bereich",""),
    "position": meta.get("position",""),
    "teilnehmername": meta.get("teilnehmername",""),
    "survey_version": SURVEY_VERSION
}
for k,v in metas.items(): df[k]=v

msg = submit_to_gsheets(df)

st.markdown("""
<div class="outro">
  <div class="check">✅</div>
  <h2>Vielen Dank für Ihre Teilnahme!</h2>
  <p>Ihre Angaben wurden gespeichert und fließen in die Auswertung der Masterarbeit ein.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='outro card'><strong>Status:</strong> {msg}</div>", unsafe_allow_html=True)
