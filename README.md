# DSM Befragungs-App (Hotel) – v24.1 (Multipage, Fix)

Fix: ersetzt `st.experimental_rerun()` durch **`st.rerun()`** (verfügbar in aktuellen Streamlit-Versionen).
Damit verschwinden die AttributeError auf Start- und Absende-Seite.

Multi-Page sorgt weiterhin dafür, dass jede Seite auf dem Smartphone **oben startet**.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
