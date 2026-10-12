# Changelog

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
