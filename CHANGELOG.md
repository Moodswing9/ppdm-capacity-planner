# Changelog

## [1.1.0] — 2026-11-10
### Fixed
- Forecasts were cut off: Claude Opus 4.7 hit the 1024-token limit before the Executive Summary (section 4 of 4) on the demo data. `max_tokens` is now 8000, and a report that does hit the limit says so
- On Windows, printing a forecast that contains emoji or other non-ASCII text crashed with `UnicodeEncodeError` after the forecast had been generated (and paid for); output is now written as UTF-8

### Changed
- Forecasts run on **Claude Opus 5.5** (`claude-opus-5-5`) at `low` effort. Opus 5.5 always thinks; measured on the demo data, `low` produced the complete four-section report for about $0.06, about what a complete Opus 4.7 report would cost, while `medium` cost about 25% more for no visible gain
- The response is read by block type (it now starts with a thinking block); `content[0].text` would have returned the thinking block
- If Claude declines, the planner retries on a fallback model (`fallbacks: "default"`) and otherwise exits with code 3 and a clear message
- `anthropic` requirement → `>=2.7.0` (API version `2026-10-21`)

### Added
- Unit tests for the forecast request and response handling

## [1.0.2] — 2026-10-12
### Fixed
- Claude Code plugin manifest passes `claude plugin validate`: `repository` is a URL, `license` is MIT and the unsupported `components` field is gone; the invalid `skills` entry (a custom `run` field) is replaced by a real `plan-capacity` skill in `skills/plan-capacity/SKILL.md`
- Install docs: the plugin is now installed from the Moodswing9 marketplace (`claude plugin marketplace add Moodswing9/claude-plugins`, then `claude plugin install ppdm-capacity-planner@moodswing9`). The previously documented `npx skills add` installs only the skill, not the slash commands

### Added
- CI validates the plugin manifest on every push and pull request

## [1.0.1] — 2026-10-12
### Added
- CI runs the 13 tests on Python 3.11 and 3.12 for every push and pull request; they previously never ran on GitHub
- README, MIT LICENSE, CONTRIBUTING guide, bug-report issue template and this changelog

### Fixed
- CLAUDE.md said copying `.env.example` to `.env` configures the tool; the planner reads only environment variables, so the docs now say to export them

No code changes from 1.0.0.

## [1.0.0] — 2026-07-14
### Added
- Capacity forecasting for PPDM storage systems with Claude Opus 4.7: 80% and 95% breach projections, recommendations and an executive summary
- Live mode (PPDM REST API) and `--demo` mode with built-in sample data
- Utilisation bars in the terminal report
- Claude Code plugin manifest with a `plan-capacity` skill
- 13 unit tests
