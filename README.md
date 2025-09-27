# DSM Befragungs-App (Hotel) – v21

Neu in v21
- **Vor Absenden Prüf-Dialog**: Wenn Geräte nicht als „Vorhanden“ markiert sind, erscheint ein Dialog mit der Anzahl und Liste der fehlenden Geräte. Nutzer:in kann *weiter bearbeiten* oder *trotzdem absenden*. Wenn alle Geräte markiert sind, kommt **kein** Dialog.
- **Sheets-Kompatibilität**: Beim Schreiben wird die **Spaltenreihenfolge an den vorhandenen Header** im Tab `responses` angepasst. Extra-Spalten (`leistung_kw`, `rebound`) werden automatisch als leer ergänzt, damit die Auswertung wieder passt.
- Bestehende Features bleiben (Intro-Seite, Orange-CI, visuelle Skalen, klare Outro-Seite).

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
