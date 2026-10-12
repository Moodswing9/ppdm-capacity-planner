---
name: plan-capacity
description: Forecast Dell EMC PowerProtect Data Manager (PPDM) storage capacity — 80% and 95% breach projections per storage system, recommendations and an executive summary, using ppdm-capacity-planner. Use when the user asks when PPDM or Data Domain storage will fill up, for a capacity forecast or plan, or to try the planner in demo mode.
---

# PPDM capacity forecast

`planner.py` lives at the plugin root, two directories above this skill's base directory. Run it from there with the Bash tool.

## Steps

1. **Install dependencies** if they aren't installed yet:
   ```bash
   pip install -r <plugin root>/requirements.txt
   ```
2. **Check `ANTHROPIC_API_KEY` is set.** The forecast always calls Claude, in demo mode too. If it's missing, ask the user to set it; never ask them to paste it into the chat.
3. **Choose a mode:**
   - **Demo** (no PPDM server needed, built-in sample data):
     ```bash
     python <plugin root>/planner.py --demo
     ```
   - **Live:** needs `PPDM_HOST`, `PPDM_USER` and `PPDM_PASS` set in the environment (`PPDM_PORT` defaults to 8443). Prefer environment variables over `--pass`, which can leave the password in shell history.
     ```bash
     python <plugin root>/planner.py
     ```
     The planner reads only real environment variables; it does not load `.env` files.
4. **Report back:** summarise which storage systems are closest to the 80% and 95% thresholds, the projected dates, and the top recommendations. Quote the executive summary if the user wants something to share.

## Exit codes

- `1` — missing `--host`, `--user` or `--pass` (or their environment variables)
- `2` — PPDM returned no storage systems

## Limits

- Forecasts come from a single snapshot of current usage, so treat dates as estimates.
- TLS certificate verification is disabled for the PPDM connection (self-signed certificates are common); use it on trusted networks only.
