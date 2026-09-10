# Changelog

All notable changes to gh-pulse will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-10

### Added

- Terminal dashboard (TUI) for viewing GitHub PRs across multiple repositories
- CI status indicators (green/red/yellow) for each PR
- Review request detection via `gh search prs --review-requested=@me`
- Keyboard bindings: `r` refresh, `o` open in browser, `d` toggle drafts, `c` toggle closed, `q` quit
- YAML configuration file (`~/.config/gh-pulse/config.yaml`)
- Auto-discovery of repositories from `gh repo list`
- CLI subcommands: `run` (TUI), `init` (create config), `repos` (list/discover repos)
- Friendly error message when `gh` CLI is not installed
- Unit tests for models, config, and gh CLI wrapper (18 tests)
- CI pipeline: ruff lint + format, mypy type check, pytest (Python 3.10–3.13)

[0.1.0]: https://github.com/FreakyAdy/gh-pulse/releases/tag/v0.1.0
