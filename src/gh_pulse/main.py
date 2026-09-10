"""Main entry point for gh-pulse."""

import argparse
import shutil
import sys
from pathlib import Path

from gh_pulse.config import DEFAULT_CONFIG, Config
from gh_pulse.tui import GHPulseApp


def _print(message: str) -> None:
    """Print to stdout (T20-compliant for CLI commands)."""
    sys.stdout.write(message + '\n')


def create_config(args: argparse.Namespace) -> Config:
    """Create config from args and file."""
    config = Config.load(args.config)

    if args.repos:
        config.repos = args.repos
    if args.refresh:
        config.refresh_interval = args.refresh
    if args.show_drafts:
        config.show_drafts = True
    if args.show_closed:
        config.show_closed = True

    return config


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize config file."""
    config_path = Path(args.config or str(Path.home() / '.config' / 'gh-pulse' / 'config.yaml'))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists() and not args.force:
        _print(f'Config already exists at {config_path}. Use --force to overwrite.')
        return 1
    config_path.write_text(DEFAULT_CONFIG)
    _print(f'Created config at {config_path}')
    return 0


def _check_gh_cli() -> None:
    """Check that the gh CLI is installed and authenticated."""
    if not shutil.which('gh'):
        _print(
            "Error: 'gh' CLI not found.\n"
            'gh-pulse requires the GitHub CLI to fetch data.\n'
            "Install it from https://cli.github.com/ and run 'gh auth login'."
        )
        sys.exit(1)


def cmd_run(args: argparse.Namespace) -> int:
    """Run the TUI dashboard."""
    _check_gh_cli()
    config = create_config(args)
    app = GHPulseApp(config=config)
    app.run()
    return 0


def cmd_repos(args: argparse.Namespace) -> int:
    """List tracked repos or auto-discover."""
    _check_gh_cli()
    config = Config.load(args.config)
    if args.discover:
        from gh_pulse.gh_wrapper import GHWrapper

        wrapper = GHWrapper()
        repos = wrapper.get_repos(limit=100)
        for repo in repos:
            _print(f'{repo.name} {"(private)" if repo.private else ""}')
    else:
        for repo in config.repos:
            _print(repo)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='gh-pulse',
        description='Terminal dashboard for GitHub PRs, CI status, and review requests',
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('--config', '-c', help='Path to config file')

    subparsers = parser.add_subparsers(dest='command')

    # run command
    run_parser = subparsers.add_parser('run', help='Run the TUI dashboard')
    run_parser.add_argument('--repos', '-r', nargs='+', help='Repositories to track (owner/repo)')
    run_parser.add_argument('--refresh', type=int, help='Refresh interval in seconds')
    run_parser.add_argument('--show-drafts', action='store_true', help='Show draft PRs')
    run_parser.add_argument('--show-closed', action='store_true', help='Show closed/merged PRs')
    run_parser.set_defaults(func=cmd_run)

    # init command
    init_parser = subparsers.add_parser('init', help='Create default config file')
    init_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing config')
    init_parser.set_defaults(func=cmd_init)

    # repos command
    repos_parser = subparsers.add_parser('repos', help='List or discover repositories')
    repos_parser.add_argument(
        '--discover', '-d', action='store_true', help='Auto-discover repos from gh'
    )
    repos_parser.set_defaults(func=cmd_repos)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        # Default to 'run' when no subcommand is given
        args = parser.parse_args(['run'])
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
