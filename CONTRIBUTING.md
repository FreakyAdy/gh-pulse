# Contributing to gh-pulse

Thanks for your interest in contributing! Here's how to get started.

## Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager
- **[gh CLI](https://cli.github.com/)** — GitHub CLI, authenticated (`gh auth login`)

## Setup

```bash
# Clone the repo
git clone https://github.com/FreakyAdy/gh-pulse.git
cd gh-pulse

# Install dependencies (creates .venv automatically)
uv sync

# Verify everything works
uv run pytest
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

## Development Workflow

### Running locally

```bash
# Launch the TUI dashboard
uv run gh-pulse run

# Or with specific repos
uv run gh-pulse run --repos owner/repo1 owner/repo2

# Initialize a config file
uv run gh-pulse init
```

### Running tests

```bash
# All tests
uv run pytest

# Verbose with short tracebacks
uv run pytest -v --tb=short

# Single test file
uv run pytest tests/test_models.py
```

### Linting and formatting

```bash
# Check lint
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Auto-format
uv run ruff format src/ tests/
```

### Type checking

```bash
uv run mypy src/gh_pulse/
```

## Code Style

- **Formatter**: ruff (single quotes, spaces, no trailing commas)
- **Linter**: ruff (pycodestyle, pyflakes, isort, pyupgrade, bugbear, comprehensions)
- **Type checking**: mypy with strict settings
- All code must pass `ruff check`, `ruff format --check`, and `mypy` before merging

## Making Changes

1. Fork the repo and create a branch from `main`
2. Make your changes with clear, small commits
3. Add or update tests for any new functionality
4. Run the full check suite: `uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
5. Open a PR with a clear description of what changed and why

## Reporting Issues

- Use the **Bug Report** template for bugs
- Use the **Feature Request** template for new ideas
- Include your Python version, OS, and `gh --version` when reporting bugs

## Project Structure

```
src/gh_pulse/
├── __init__.py        # Package metadata
├── main.py            # CLI entry point (argparse)
├── config.py          # YAML config loading/saving
├── gh_wrapper.py      # gh CLI subprocess wrapper
├── models.py          # Data models (PR, Repo, CIStatus)
└── tui.py             # Textual TUI dashboard
tests/
├── test_config.py     # Config tests
├── test_gh_wrapper.py # GH wrapper tests (mocked subprocess)
└── test_models.py     # Data model tests
```
