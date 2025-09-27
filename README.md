# DSM Befragungs-App (Hotel) – v24 (Multipage)

**Warum v24?** Auf Smartphones behalten Browser beim „Rerun“ oft die Scrollposition. Die sicherste Lösung ist echtes
Seiten-Navigieren. In v24 ist die App in **mehrere Seiten** aufgeteilt – damit startet jede Seite garantiert **ganz oben**.

## Struktur
- `app.py` – Intro & Einverständnis. Button wechselt mit `st.switch_page()` zur nächsten Seite.
- `pages/01_Fragebogen.py` – Geräteabfrage inkl. Prüf-Hinweis bei nicht markierten Geräten.
- `pages/99_Speichern.py` – Speichern nach Google Sheets + Danke-Seite.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
