# DSM Hotel – Online-Befragung (Step-by-Step, Streamlit)

Neu: Schrittweiser Flow (ein Gerät nach dem anderen). Kriterien mit **Bedeutung** in kleiner grauer Schrift 
und **Optionen** direkt daneben. Excel-Export + optional Google Sheets.

## Deployment (ohne lokalen Test)
1. Repo bei GitHub erstellen (z. B. `dsm-befragung-app`) und Ordner-Inhalt pushen.
2. Streamlit Community Cloud → **New app** → Repo/Branch → `app.py` → **Deploy**.
3. Optional: Google Sheets in **App → Settings → Secrets** hinterlegen (Service-Account JSON + `gsheet_id`) und Sheet freigeben.

## Datenformat (Tall)
timestamp, datum, hotel, bereich, position, teilnehmername, survey_version,
geraet, vorhanden, leistung_kw, modulation, dauer, rebound, betriebsfenster
