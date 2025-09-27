# DSM Befragungs-App (Hotel) – v24.2 (Multipage + Hinweis-Dialog)

- **Nicht markierte Geräte**: Vor dem Absenden erscheint ein **Dialog** mit Anzahl & Liste – mit Buttons **„Weiter bearbeiten“** oder **„Trotzdem absenden“** (nicht blockierend).
- Beibehaltung: Multi-Page (mobile-freundlich), Google-Sheets-Header-Anpassung, Orange-CI, visuelle Skalen.
- Kompatibel mit Streamlit ≥ 1.37 (nutzt `st.rerun` & `st.switch_page`, `@st.dialog`).

Start:
```bash
pip install -r requirements.txt
streamlit run app.py
```
