# DSM Befragungs-App (Hotel) – v22-fix

Diese Version entspricht funktional der stabilen v22 (ohne Sticky-Header), repariert für Mobile:

- **Auto-Scroll-to-Top** nach jedem Schritt (Intro → Einverständnis → Fragebogen → Danke).
- **Pop-up vor dem Absenden** bei nicht markierten Geräten.
- **Google-Sheets-Header-Anpassung**: Spalten werden an vorhandene Header im Tab `responses` angepasst.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
