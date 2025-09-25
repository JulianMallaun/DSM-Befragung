# DSM Befragungs-App (Hotel) – v17

Änderungen (gemäß Wunsch):
- **Dauerhinweis**: „Die Befragung dauert ungefähr **5–7 Minuten**.“
- **Grafische Skalen** (Testbetrieb): ein farbiger Füllbalken spiegelt die Radio-Auswahl (abschaltbar via `VISUAL_SCALES = False`).
- **Orange** als feste CI-Farbe, Farbwähler entfernt.
- **Abstände & Weißraum** erhöht; Button unverändert.
- Dark-Mode-Optimierung weiter aktiv.

Rückbau auf die vorige Version (ohne grafische Skalen): Setze in `app.py` ganz oben `VISUAL_SCALES = False`.

## Start
```bash
pip install -r requirements.txt
streamlit run app.py
```
