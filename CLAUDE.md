# ppdm-capacity-planner

Claude Opus 4.7-powered storage capacity forecasting for Dell EMC PowerProtect Data Manager (PPDM).

## What it does

`planner.py` connects to a live PPDM instance via its REST API, retrieves storage system utilisation data, then sends the snapshot to Claude Opus 4.7 which produces:

- **80% capacity breach projections** per storage system
- **95% capacity breach projections** per storage system (critical threshold)
- **Top recommendations** — deduplication, data cleanup, tiering, expansion
- **Executive summary** suitable for management reporting

A `--demo` flag lets you run the full pipeline (including the Claude analysis) without any live PPDM instance.

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Demo mode (no PPDM needed, uses built-in fake data)
python planner.py --demo

# Live PPDM instance
python planner.py --host ppdm.corp.example.com --user admin --pass MyPassword
```

## Environment variables

| Variable           | Description                                | Default  |
|--------------------|--------------------------------------------|----------|
| `PPDM_HOST`        | PPDM hostname or IP                        | —        |
| `PPDM_USER`        | PPDM admin username                        | —        |
| `PPDM_PASS`        | PPDM admin password                        | —        |
| `PPDM_PORT`        | PPDM HTTPS port                            | `8443`   |
| `ANTHROPIC_API_KEY`| Anthropic API key for Claude Opus 4.7      | —        |

Copy `.env.example` to `.env` and fill in your values. The tool reads all CLI flags from the environment if not passed on the command line.

## CLI reference

```
usage: planner [-h] [--host HOST] [--user USER] [--pass PASS] [--port PORT] [--demo]

options:
  --host HOST   PPDM hostname or IP (env: PPDM_HOST)
  --user USER   PPDM username (env: PPDM_USER)
  --pass PASS   PPDM password (env: PPDM_PASS)
  --port PORT   PPDM port (env: PPDM_PORT, default: 8443)
  --demo        Use built-in demo data instead of connecting to PPDM
```

## Architecture

Single-file tool (`planner.py`). Key components:

| Component            | Purpose                                              |
|----------------------|------------------------------------------------------|
| `PPDMClient`         | REST client: login → Bearer token → GET storage-systems → logout |
| `parse_storage_systems()` | Normalises raw PPDM API records to `{name, total_gib, used_gib, used_pct}` |
| `build_prompt()`     | Constructs the Claude prompt from the storage snapshot |
| `generate_forecast()`| Calls `anthropic.Anthropic().messages.create(model="claude-opus-4-7", ...)` |
| `print_report()`     | Renders ASCII utilisation bars + Claude narrative to stdout |

## Running tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Notes

- TLS certificate verification is disabled for PPDM connections (self-signed certs are common). Do not disable this in production internet-facing environments.
- Claude Opus 4.7 generates estimates from a single snapshot. For accurate projections, feed historical data by scheduling the tool daily and storing trends.
