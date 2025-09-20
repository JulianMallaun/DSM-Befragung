from __future__ import annotations
import io
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Befragung Lastflexibilität – Hotel", page_icon="🏨", layout="wide")
st.title("Befragung Lastflexibilität – Hotel")
st.caption("Masterarbeit im Bereich Intelligente Energiesysteme – Online-Erhebung")

with st.expander("Einleitung", expanded=True):
    st.markdown(
        """
        Vielen Dank, dass Sie an dieser Befragung teilnehmen. Ziel ist es, die Flexibilität des Energieverbrauchs in Hotels besser zu verstehen.
        Die Daten werden anonymisiert ausschließlich zu wissenschaftlichen Zwecken genutzt.
        Zeitaufwand: ca. 20–30 Minuten.
        """
    )

with st.expander("Einverständniserklärung", expanded=True):
    consent = st.checkbox(
        "Ich habe die Informationen gelesen und bin mit der Teilnahme einverstanden.",
        value=False,
    )
    if not consent:
        st.info("Bitte Einverständniserklärung bestätigen, bevor Sie Angaben machen.")

st.subheader("Stammdaten")
col1, col2, col3 = st.columns(3)
with col1:
    hotel = st.text_input("Hotel")
with col2:
    bereich = st.text_input("Bereich/Abteilung")
with col3:
    position = st.text_input("Position")

survey_date = st.date_input("Datum", value=datetime.today())

criteria_labels = [
    ("Modulation", "1=<10 %, 2=10–25 %, 3=25–40 %, 4=≥40 %"),
    ("Dauer", "1=<15 min, 2=15–45 min, 3=45–120 min, 4=≥2 h"),
    ("Rebound", "1=sehr stark, 2=stark, 3=gering, 4=kaum"),
    ("Betriebsfenster", "1=rigide, 2=begrenzt, 3=breit, 4=frei"),
]

def device_form(key_prefix: str, title: str):
    st.markdown(f"## {title}")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        vorhanden = st.checkbox("Vorhanden", key=f"{key_prefix}_vorhanden")
    with col_b:
        leistung = st.number_input(
            "Leistung (kW)", min_value=0.0, step=0.1, key=f"{key_prefix}_leistung"
        )

    ratings = {}
    for crit, helptext in criteria_labels:
        ratings[crit] = st.select_slider(
            f"{crit} ({helptext})",
            options=[1, 2, 3, 4],
            value=2,
            key=f"{key_prefix}_{crit}",
            disabled=not vorhanden,
        )

    return {
        "geraet": title,
        "vorhanden": vorhanden,
        "leistung_kw": leistung if vorhanden else 0.0,
        **{f"{c.lower()}": ratings[c] for c, _ in criteria_labels},
    }

# Gerätekatalog
catalog = {
    "A) Küche": {
        "A1) Kühlung / Kälte": [
            "Walk-in Kühlraum",
            "Walk-in Tiefkühlraum",
            "Kühltische / Unterbaukühler",
            "Getränke-/Flaschenkühler",
            "Eismaschine",
            "Kühlanlagenzentrale",
        ],
        "A2) Gargeräte / Wärme": [
            "Kombidämpfer",
            "Konvektomat / Backofen",
            "Fritteuse",
            "Induktionsherd",
            "Kippbratpfanne",
            "Bain-Marie / Warmhalten",
            "Salamander",
        ],
        "A3) Geschirr- und Spülbereich": [
            "Haubenspülmaschine",
            "Bandspülmaschine",
        ],
        "A4) Lüftung": [
            "Küchenabluft (Haubenlüftung)",
            "Küchenzuluft",
        ],
    },
    "B) Wellness / Spa / Pool": {
        "B1) Sauna / Wärme": [
            "Finnische Sauna",
            "Biosauna",
        ],
        "B2) Dampfbad": [
            "Dampfsauna",
        ],
        "B3) Pools / Wassertechnik": [
            "Pool- Umwälzpumpe",
        ],
        "B4) Lüftung / Entfeuchtung": [
            "Schwimmbad Abluft",
            "Schwimmbad Zuluft",
            "Schwimmbad Luftentfeuchtung",
        ],
    },
    "C) Zimmer & Allgemeinbereiche": {
        "C1) Beleuchtung": [
            "Zimmerbeleuchtung",
            "Reklame/ Aussenbeleuchtung",
        ],
        "C2) Vertikale Förderung / Garage": [
            "Aufzüge",
        ],
        "C3) Laundry / Sonstiges": [
            "Waschmaschinen",
            "Trockner",
            "Wallbox (EV- Ladepunkte)",
        ],
    },
}

all_records = []
for big_section, sub in catalog.items():
    st.header(big_section)
    for sub_section, items in sub.items():
        st.subheader(sub_section)
        for dev in items:
            with st.container():
                rec = device_form(key_prefix=f"{sub_section}_{dev}", title=dev)
                all_records.append(rec)
                st.divider()

st.subheader("Abschluss")
name = st.text_input("Name (optional)")
confirmation = st.checkbox("Ich bestätige, dass die Angaben nach bestem Wissen erfolgen.")

submit = st.button("Jetzt absenden und speichern", type="primary")

if submit:
    if not consent:
        st.error("Bitte Einverständniserklärung bestätigen.")
    elif not confirmation:
        st.error("Bitte die Bestätigung am Ende setzen.")
    elif not hotel:
        st.error("Bitte Hotel angeben (Pflichtfeld).")
    else:
        meta = {
            "timestamp": datetime.utcnow().isoformat(),
            "hotel": hotel,
            "bereich": bereich,
            "position": position,
            "datum": str(survey_date),
            "teilnehmername": name,
        }
        df = pd.DataFrame(all_records)
        for k, v in meta.items():
            df[k] = v

        cols = [
            "timestamp","datum","hotel","bereich","position","teilnehmername",
            "geraet","vorhanden","leistung_kw","modulation","dauer","rebound","betriebsfenster"
        ]
        df = df[cols]

        st.success("Erfassung erfolgreich. Daten werden unten bereitgestellt.")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="responses")
        st.download_button(
            label="Excel-Datei herunterladen",
            data=output.getvalue(),
            file_name="befragung_responses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

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
                ws.append_rows(df.values.tolist())
                st.success("Daten zusätzlich in Google Sheets gespeichert (Tab: responses).")
            except Exception as e:
                st.warning(f"Google Sheets Speicherung nicht möglich: {e}")
        else:
            st.info(
                "Google Sheets ist optional. Hinterlegen Sie st.secrets['gcp_service_account'] und st.secrets['gsheet_id'], wenn Sie Sheets nutzen möchten."
            )

st.caption(
    "© Masterarbeit – Intelligente Energiesysteme | Diese Anwendung sammelt keine personenbezogenen Daten über das technisch Notwendige hinaus."
)
