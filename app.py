from __future__ import annotations
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="centered")

# ----------------- Global Styles -----------------
st.markdown(
    """
    <style>
    .crit-block {padding: 14px 16px; border: 1px solid #e5e7eb; border-radius: 14px; margin-bottom: 12px; background: #fafafa;}
    .crit-title {font-size: 1.05rem; font-weight: 700; margin-bottom: 2px;}
    .crit-help {font-size: 0.9rem; color: #6b7280; margin-top: 0; margin-bottom: 8px;}
    .section-counter {font-size: 0.9rem; color: #6b7280;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Befragung Lastflexibilität – Hotel")
st.caption("Masterarbeit – Intelligente Energiesysteme | Online-Erhebung (mobil & Desktop) – Präzisierte Version")

# ----------------- Helpers -----------------
def labeled_divider(label: str):
    st.markdown(f"---\n###### {label}")

def get_gsheet_id():
    # robust: akzeptiert gsheet_id auf Top-Level ODER innerhalb gcp_service_account bzw. gsheet.id
    return (
        st.secrets.get("gsheet_id")
        or st.secrets.get("gcp_service_account", {}).get("gsheet_id")
        or st.secrets.get("gsheet", {}).get("id")
    )

def rows_for_gsheets(df: pd.DataFrame):
    """Alles als String senden (None/NaN -> ""), damit 100% JSON-kompatibel."""
    records = df.to_dict(orient="records")
    rows = []
    for r in records:
        row = []
        for col in df.columns:
            v = r.get(col, None)
            # NaN-Check ohne numpy: NaN != NaN ist True
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

# ----------------- Intro & Consent -----------------
st.markdown("""
**Einleitung**  
Vielen Dank für Ihre Teilnahme. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.  
Die Angaben werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.  
**Geschätzte Dauer:** ~15 Minuten.
""")

consent = st.checkbox("Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.", value=False)
if not consent:
    st.info("Bitte Einverständniserklärung bestätigen.")

# ----------------- Stammdaten -----------------
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

# ----------------- Kriterien (präzise Labels & Optionen) -----------------
# 1) Leistung anpassen – 1–4: kaum/etwas/gut/sehr gut
K1_OPTS = [
    "1 – kaum anpassbar",
    "2 – etwas anpassbar",
    "3 – gut anpassbar",
    "4 – sehr gut anpassbar",
]

# 2) Nutzungsdauer anpassbar – <15, 15–45, 45–120, ≥2h
K2_OPTS = [
    "1 – <15 min",
    "2 – 15–45 min",
    "3 – 45–120 min",
    "4 – ≥2 h",
]

# 3) Energie-Nachholen – sehr viel, viel, wenig, kaum
K3_OPTS = [
    "1 – sehr viel Extraenergie",
    "2 – viel Extraenergie",
    "3 – wenig Extraenergie",
    "4 – kaum Extraenergie",
]

# 4) Zeitliche Flexibilität – feste Zeiten, eingeschränkt, eher flexibel, völlig flexibel
K4_OPTS = [
    "1 – feste Zeiten",
    "2 – eingeschränkt flexibel",
    "3 – eher flexibel",
    "4 – völlig flexibel",
]

def choice_to_int(txt: str) -> int:
    return int(str(txt).split("–")[0].strip()) if txt else None

# ----------------- Gerätekatalog (präzisierte Version) -----------------
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

# ----------------- Session -----------------
if "index" not in st.session_state:
    st.session_state.index = 0
if "flat_catalog" not in st.session_state:
    st.session_state.flat_catalog = [dev for section in CATALOG.values() for dev in section]
if "records" not in st.session_state:
    st.session_state.records = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ----------------- Formular pro Gerät -----------------
def criterion_block(title: str, helptext: str, options: list, key: str, disabled: bool):
    st.markdown('<div class="crit-block">', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="crit-help">{helptext}</div>', unsafe_allow_html=True)
    # horizontal: klar sichtbar, zugehörig zum Titel
    value = st.radio("", options, key=key, disabled=disabled, horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    return value

def device_form(device_name: str):
    st.subheader(device_name)

    colA, colB = st.columns([1,1])
    with colA:
        vorhanden = st.checkbox("Vorhanden", key=f"vh_{device_name}")
    with colB:
        leistung = st.number_input("Leistung (kW, optional)", min_value=0.0, step=0.1, key=f"kw_{device_name}", disabled=not vorhanden)

    k1 = criterion_block("Leistung anpassen", "stufenlos oder nur ein/aus?", K1_OPTS, key=f"k1_{device_name}", disabled=not vorhanden)
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
            "geraet": device_name,
            "vorhanden": bool(vorhanden),
            "leistung_kw": float(leistung) if vorhanden else 0.0,
            # interne Spalten stabil halten
            "modulation": choice_to_int(k1) if vorhanden else None,
            "dauer": choice_to_int(k2) if vorhanden else None,
            "rebound": choice_to_int(k3) if vorhanden else None,
            "betriebsfenster": choice_to_int(k4) if vorhanden else None,
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

# ----------------- Flow -----------------
if consent and confirmation and hotel:
    total = len(st.session_state.flat_catalog)
    if st.session_state.index < total:
        st.markdown(f'<div class="section-counter">Frage {st.session_state.index + 1} von {total}</div>', unsafe_allow_html=True)
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
                "survey_version": "2025-09-precise",
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
