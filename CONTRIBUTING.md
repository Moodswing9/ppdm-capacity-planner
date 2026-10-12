# Contributing to ppdm-capacity-planner

Thanks for helping out. Bug reports, fixes and forecasting improvements are all welcome.

## Reporting a bug

Open an issue using the **Bug report** template. Include your PPDM version, and say whether you ran in live or `--demo` mode. Remove hostnames, storage system names and credentials before posting.

## Making a change

1. Fork the repo and create a branch from `main`.
2. Install and run the tests:
   ```bash
   pip install -r requirements.txt pytest
   pytest tests -v
   ```
3. Make your change and add tests for it in `tests/`. The tests don't call PPDM or the Anthropic API.
4. Make sure `pytest tests` passes. CI runs it on Python 3.11 and 3.12.
5. Add an entry under a new `[Unreleased]` heading in `CHANGELOG.md`, and update `README.md` if options or behaviour changed.
6. Open a pull request describing what changed and how you tested it.

## Guidelines

- Keep `--demo` working without a PPDM server, so anyone can try the tool.
- Never print or log credentials or API keys.

## Releases

Maintainers bump the version in `planner.py`, `.claude-plugin/plugin.json`, the README badge and the version test, then publish a GitHub release tagged `vX.Y.Z`.
