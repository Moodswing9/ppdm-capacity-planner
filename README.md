<div align="center">

# 📈 ppdm-capacity-planner

**AI capacity forecasting for Dell PowerProtect Data Manager (PPDM) storage, powered by Claude Opus 4.7**

[![Version](https://img.shields.io/badge/version-1.0.1-6366f1?style=flat-square)](https://github.com/Moodswing9/ppdm-capacity-planner/releases)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/Moodswing9/ppdm-capacity-planner/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/Moodswing9/ppdm-capacity-planner/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-3b82f6?style=flat-square)](#requirements)
[![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude%20Opus%204.7-f59e0b?style=flat-square)](#how-it-works)

</div>

---

## Overview

`ppdm-capacity-planner` reads the current utilisation of every storage system attached to a PPDM server and asks Claude Opus 4.7 to turn that snapshot into a capacity plan:

- **80% breach projections** — when each storage system is expected to cross the warning threshold
- **95% breach projections** — the critical threshold, per storage system
- **Top recommendations** — deduplication, data cleanup, tiering or expansion
- **Executive summary** — a short narrative suitable for management reporting

The report prints to the terminal with a utilisation bar per storage system, followed by Claude's analysis.

A `--demo` mode runs the full pipeline, including the Claude analysis, against built-in sample data, so you can try it without a PPDM server.

---

## Requirements

- Python 3.11+ (CI runs on 3.11 and 3.12)
- An [Anthropic API key](https://console.anthropic.com/) in `ANTHROPIC_API_KEY` (needed in demo mode too)
- For live mode: network access to a PPDM server and an account that can read storage systems

---

## Quick start

```bash
git clone https://github.com/Moodswing9/ppdm-capacity-planner.git
cd ppdm-capacity-planner
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...

# Try it without a PPDM server
python planner.py --demo

# Run against a live PPDM server
python planner.py --host ppdm.corp.example.com --user admin --pass 'your-password'
```

On Windows PowerShell, set the key with `$env:ANTHROPIC_API_KEY = "sk-ant-..."`.

---

## Configuration

Every connection option can be passed as a flag or set as an environment variable. Flags take precedence.

| Flag | Environment variable | Description | Default |
|:---|:---|:---|:---|
| `--host` | `PPDM_HOST` | PPDM hostname or IP | — |
| `--user` | `PPDM_USER` | PPDM username | — |
| `--pass` | `PPDM_PASS` | PPDM password | — |
| `--port` | `PPDM_PORT` | PPDM HTTPS port | `8443` |
| `--demo` | — | Use built-in sample data instead of a live PPDM server | off |
| — | `ANTHROPIC_API_KEY` | Anthropic API key | — |

`.env.example` lists the variables, but the tool does not load `.env` files itself. Export the variables in your shell, or load the file with a tool of your choice before running.

Passing `--pass` on the command line can leave the password in your shell history; setting `PPDM_PASS` in the environment avoids that.

---

## How it works

1. **Collect** — logs in to the PPDM REST API, fetches all storage systems, then logs out.
2. **Normalise** — converts each record to name, total capacity, used capacity and percentage used.
3. **Forecast** — sends the snapshot to Claude Opus 4.7, which returns the breach projections, recommendations and summary.
4. **Report** — prints utilisation bars followed by the forecast.

Everything lives in a single file, `planner.py`.

---

## Claude Code plugin

The repo includes a Claude Code plugin manifest (`.claude-plugin/plugin.json`) with a `plan-capacity` skill that runs the planner from inside Claude Code.

---

## Running tests

```bash
pip install -r requirements.txt pytest
pytest tests -v
```

The tests don't call PPDM or the Anthropic API.

---

## Limitations

- **Single snapshot.** Forecasts are estimated from one point-in-time reading. For more reliable projections, run the planner on a schedule and keep the history.
- **TLS verification is disabled** for the PPDM connection, because PPDM servers commonly use self-signed certificates. Only use it on trusted internal networks.

---

See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute and [CHANGELOG.md](CHANGELOG.md) for release history.
