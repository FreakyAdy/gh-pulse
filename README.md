<h1 align="center">gh-pulse</h1>

<p align="center">
  <strong>A terminal dashboard for GitHub PRs, CI status, and review requests — across all your repos.</strong>
</p>

<p align="center">
  <a href="https://github.com/FreakyAdy/gh-pulse/actions"><img src="https://img.shields.io/github/actions/workflow/status/FreakyAdy/gh-pulse/ci.yml?branch=main&style=flat-square" alt="Build Status"></a>
  <a href="https://github.com/FreakyAdy/gh-pulse/blob/main/LICENSE"><img src="https://img.shields.io/github/license/FreakyAdy/gh-pulse?style=flat-square" alt="License"></a>
  <a href="https://pypi.org/project/gh-pulse/"><img src="https://img.shields.io/pypi/v/gh-pulse?style=flat-square" alt="PyPI"></a>
  <a href="https://pypi.org/project/gh-pulse/"><img src="https://img.shields.io/pypi/pyversions/gh-pulse?style=flat-square" alt="Python"></a>
</p>

<p align="center">
  <!-- TODO: Replace with actual recording. See "Hero Image" section below. -->
  <em>[ hero GIF / screenshot goes here ]</em>
</p>

---

## Why gh-pulse?

If you work across multiple GitHub repos, checking PR status means clicking through tabs or running `gh pr list` per repo. **gh-pulse** puts everything in one terminal screen:

- PRs from every repo you care about, in a single view
- CI status (green ✅ / red ❌ / pending ⏳) at a glance
- Keyboard-driven: open PRs in browser, toggle drafts, refresh — no mouse needed
- Works anywhere you have a terminal and `gh` auth

### How it compares to `gh dash`

[`gh dash`](https://github.com/dlvhdr/gh-dash) is the established tool in this space (~7k stars, Go, feature-rich with issues/notifications/custom sections). gh-pulse is smaller and Python-native — if your team already works in Python and wants something they can read and extend, this is a simpler starting point. If you need a battle-tested, full-featured dashboard, use `gh dash`.

## Quickstart

**Prerequisites:** [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated (`gh auth login`).

```bash
# Install from source (PyPI coming soon)
pip install git+https://github.com/FreakyAdy/gh-pulse.git

# Launch the dashboard
gh-pulse
```

That's it. gh-pulse will auto-discover your repositories and show open PRs.

### Configure specific repos

```bash
# Create a config file
gh-pulse init

# Edit ~/.config/gh-pulse/config.yaml
```

```yaml
repos:
  - FreakyAdy/gh-pulse
  - torvalds/linux
refresh_interval: 30    # seconds (0 to disable)
show_drafts: false
show_closed: false
max_prs_per_repo: 20
```

You can also pass repos directly:

```bash
gh-pulse run --repos FreakyAdy/gh-pulse torvalds/linux
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `r` | Refresh all repos |
| `o` | Open selected PR in browser |
| `d` | Toggle draft PRs |
| `c` | Toggle closed/merged PRs |
| `q` | Quit |

## How It Works

gh-pulse wraps the [`gh` CLI](https://cli.github.com/) to fetch PR data via `gh pr list --json`, parses CI status from `statusCheckRollup`, and renders everything in a [Textual](https://github.com/Textualize/textual) TUI. No GitHub tokens to manage — it uses your existing `gh auth` session.

```
gh-pulse → gh CLI (subprocess) → GitHub API → Textual TUI
```

Each repo gets its own panel with a sortable table. Auto-refresh runs on a configurable interval. Everything stays in your terminal.

## Development

```bash
git clone https://github.com/FreakyAdy/gh-pulse.git
cd gh-pulse
uv sync                              # install deps
uv run gh-pulse                      # run locally
uv run pytest                        # run tests
uv run ruff check src/ tests/        # lint
uv run ruff format --check src/ tests/  # format check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development guide.

## Roadmap

- [ ] PyPI release (`pip install gh-pulse`)
- [ ] TUI tests via Textual pilot
- [ ] Notification badge for PRs requesting your review
- [ ] Custom column configuration
- [ ] Color theme support

## License

MIT — see [LICENSE](LICENSE).

---

## Hero Image Instructions

> **For the maintainer:** Record a ~15-second terminal session showing:
> 1. Run `gh-pulse run --repos <your-repo> <another-repo>` in a terminal with a dark theme
> 2. Show the dashboard loading with 2-3 repos, PRs with mixed CI status (green/red/yellow)
> 3. Press `r` to refresh, then `o` to open a PR in the browser
> 4. Convert to GIF (e.g., with [vhs](https://github.com/charmbracelet/vhs) or [asciinema](https://asciinema.org/) + [agg](https://github.com/asciinema/agg))
> 5. Replace the placeholder in the README above

### Demo GIF Ideas

Here are 5-7 moments that would make good short demo GIFs:

1. **First launch**: `gh-pulse` auto-discovers repos and shows the dashboard
2. **Multi-repo view**: Dashboard with 3+ repos, each showing PRs with different CI states
3. **Open in browser**: Select a PR with arrow keys, press `o` → browser opens
4. **Toggle drafts**: Press `d` to show/hide draft PRs, table updates instantly
5. **Config workflow**: `gh-pulse init` → edit YAML → `gh-pulse run` showing configured repos
6. **Auto-refresh**: Dashboard updating in real-time as CI status changes
7. **Repo discovery**: `gh-pulse repos --discover` listing all accessible repos