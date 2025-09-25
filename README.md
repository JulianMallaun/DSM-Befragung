# DSM Befragungs-App (Hotel) – v16 (Mobile + Dark Mode)

Fix: Erklärtexte der Kriterien waren auf Smartphones im Dark Mode schlecht lesbar.
- **Dark-Mode gezielte Farben**: `crit-title`, `crit-help`, Radiolabels werden in dunklen Umgebungen hell dargestellt (≈82% Weiß).
- **Mobile Tweaks**: Größere Schrift und mehr Zeilenhöhe auf kleinen Displays.
- Weiterhin: nur der farbige **Separator** zwischen Geräten; Consent-/Confirm-Boxen mit transparentem Blau (hell & dunkel).

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
