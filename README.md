# DSM Befragungs-App (Hotel) – v19

Neu in v19
- **Echte Google-Sheets-Übertragung** (wenn Secrets vorhanden): klare Statusmeldung nach dem Absenden.
- **Smartphone-taugliche Outro/Thank-you-Seite** nach Klick auf „Absenden“ mit ✅-Icon, Statuskarte, „Neue Antwort starten“ und Download einer Kurzbestätigung.
- Beibehaltung aller bisherigen Anpassungen (Intro, Orange, visuelle Skalen, Weißraum).

## Google Sheets einrichten
Füge in `.streamlit/secrets.toml` (oder Projekt-Secrets) Folgendes hinzu:
```
[gcp_service_account]
type="service_account"
project_id="..."
private_key_id="..."
private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email="...@...gserviceaccount.com"
client_id="..."
token_uri="https://oauth2.googleapis.com/token"
gsheet_id="DEIN_SHEET_ID"       # optional hier oder als top-level gsheet_id
```
Oder setze `gsheet_id` als Top-Level-Schlüssel.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
