# DSM Hotel – Online-Befragung (Streamlit)

Erhebung zur Lastflexibilität in Hotels. Ergebnisse als Excel-Download und optional in Google Sheets.

## 1) Repository auf GitHub anlegen
- Neues Repo erstellen, z. B. `dsm-befragung-app`.
- Dateien dieses Ordners pushen: `app.py`, `requirements.txt`, `.streamlit/config.toml`, `README.md`, `.gitignore`.

## 2) Deploy auf Streamlit Community Cloud (ohne lokalen Test)
1. Öffne https://share.streamlit.io und melde dich an.
2. **New app** → GitHub-Repo wählen → Branch `main` → Pfad zu `app.py` bestätigen → Deploy.
3. Nach dem ersten Start ist die App über einen Link öffentlich erreichbar und mobil nutzbar.

## 3) Google Sheets anbinden (optional)
1. In Google Cloud einen **Service Account** anlegen und einen **JSON Key** erzeugen.
2. In Streamlit Cloud unter **App → Settings → Secrets** folgendes hinterlegen:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "service-account@project.iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"

gsheet_id = "SPREADSHEET_ID"
```

3. In Google Sheets ein leeres Spreadsheet anlegen, aus der URL die **SPREADSHEET_ID** kopieren.
4. Das Spreadsheet für die **client_email** des Service Accounts mit **Bearbeiten**-Recht freigeben.
5. In der App wird bei jedem Absenden zusätzlich in den Tab **responses** geschrieben.

## 4) Datenformat
Tall-Format, eine Zeile pro Gerät:
```
timestamp, datum, hotel, bereich, position, teilnehmername, survey_version,
geraet, vorhanden, leistung_kw, modulation, dauer, rebound, betriebsfenster
```

## 5) Anpassungen
- Gerätekatalog in `app.py` im Dictionary `catalog` ändern oder erweitern.
- Theme in `.streamlit/config.toml`.

## 6) Datenschutz
- Einwilligung am Beginn ist verpflichtend.
- Name optional.
- Die App bietet Excel-Export an; Google Sheets ist freiwillig.

---

**Support**: Bei Fragen bitte Issue im GitHub-Repo anlegen.
