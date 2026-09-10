"""Configuration management for gh-pulse."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from gh_pulse.gh_wrapper import GHWrapper


@dataclass
class Config:
    """Application configuration."""

    repos: list[str] = field(default_factory=list)
    refresh_interval: int = 60  # seconds
    show_drafts: bool = False
    show_closed: bool = False
    max_prs_per_repo: int = 20
    colors: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | None = None) -> 'Config':
        """Load config from file."""
        config_paths = []
        if path:
            config_paths.append(Path(path))
        config_paths.extend([
            Path.home() / '.config' / 'gh-pulse' / 'config.yaml',
            Path.cwd() / 'gh-pulse.yaml',
        ])

        for config_path in config_paths:
            if config_path.exists():
                with open(config_path) as f:
                    data = yaml.safe_load(f) or {}
                return cls(**data)

        return cls()

    def save(self, path: str | None = None) -> None:
        """Save config to file."""
        if path is None:
            path = str(Path.home() / '.config' / 'gh-pulse' / 'config.yaml')
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.safe_dump(self.__dict__, f)

    def auto_discover_repos(self, gh_wrapper: 'GHWrapper') -> list[str]:
        """Auto-discover repos from gh CLI."""
        try:
            repos = gh_wrapper.get_repos(limit=100)
            return [r.name for r in repos]
        except Exception:
            return []


DEFAULT_CONFIG = """# gh-pulse configuration
# repos: list of repositories to track (owner/repo format)
repos: []
# refresh_interval: seconds between auto-refresh (0 to disable)
refresh_interval: 60
# show_drafts: include draft PRs
show_drafts: false
# show_closed: include closed/merged PRs
show_closed: false
# max_prs_per_repo: maximum PRs to show per repository
max_prs_per_repo: 20
# colors: custom color overrides (rich color names)
colors: {}
"""
