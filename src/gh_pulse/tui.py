"""TUI dashboard for gh-pulse."""

from datetime import datetime
from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header, Label, Static

from gh_pulse.config import Config
from gh_pulse.gh_wrapper import GHWrapper
from gh_pulse.models import PR, CIStatus


class PRTable(DataTable):
    """Data table for displaying PRs."""

    def __init__(self, repo_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.repo_name = repo_name
        self.cursor_type = 'row'

    def on_mount(self) -> None:
        self.add_columns('#', 'Title', 'Author', 'Status', 'CI', 'Age', 'Draft')
        self.zebra_stripes = True

    def update_prs(self, prs: list[PR]) -> None:
        self.clear()
        for pr in prs:
            ci_color = self._ci_color(pr.ci_status)
            status_text = Text(pr.state, style=self._status_style(pr.state))
            ci_text = Text(pr.ci_status.value.upper(), style=ci_color)
            draft_text = '✓' if pr.is_draft else ''

            self.add_row(
                str(pr.number),
                pr.short_title(45),
                pr.author,
                status_text,
                ci_text,
                f'{pr.age_days()}d',
                draft_text,
                key=str(pr.number),
            )

    def _ci_color(self, status: CIStatus) -> str:
        return {
            CIStatus.SUCCESS: 'green',
            CIStatus.FAILURE: 'red',
            CIStatus.PENDING: 'yellow',
            CIStatus.UNKNOWN: 'dim',
        }.get(status, 'white')

    def _status_style(self, state: str) -> str:
        return {'OPEN': 'cyan', 'CLOSED': 'red', 'MERGED': 'magenta'}.get(state, 'white')


class RepoPanel(Static):
    """Panel for a single repository."""

    def __init__(self, repo_name: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.repo_name = repo_name
        self.prs: list[PR] = []

    def compose(self) -> ComposeResult:
        yield Label(self.repo_name, classes='repo-title')
        yield PRTable(self.repo_name, id=f'table-{self.repo_name.replace("/", "-")}')

    def update_prs(self, prs: list[PR]) -> None:
        self.prs = prs
        table = self.query_one(PRTable)
        table.update_prs(prs)


class GHPulseApp(App):
    """Main TUI application."""

    CSS = """
    Screen {
        layout: vertical;
    }
    Header {
        height: 3;
        background: $surface;
    }
    .repo-title {
        height: 1;
        background: $primary;
        color: $text;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    PRTable {
        height: 1fr;
    }
    RepoPanel {
        border: solid $primary;
        margin: 1;
        padding: 0 1;
        min-height: 10;
    }
    .status-bar {
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    Footer {
        height: 1;
    }
    """

    BINDINGS = [
        Binding('r', 'refresh', 'Refresh'),
        Binding('o', 'open_pr', 'Open PR'),
        Binding('q', 'quit', 'Quit'),
        Binding('d', 'toggle_drafts', 'Drafts'),
        Binding('c', 'toggle_closed', 'Closed'),
    ]

    repos: reactive[list[str]] = reactive([])
    config: Config = Config()
    gh_wrapper: GHWrapper = GHWrapper()
    last_refresh: datetime | None = None

    def __init__(self, config: Config | None = None, repos: list[str] | None = None):
        super().__init__()
        if config:
            self.config = config
        if repos:
            self.config.repos = repos

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(id='panels-container')
        yield Static('', classes='status-bar', id='status-bar')
        yield Footer()

    async def on_mount(self) -> None:
        if not self.config.repos:
            # Auto-discover repos
            self.config.repos = self.config.auto_discover_repos(self.gh_wrapper)

        await self.create_panels()
        await self.refresh_data()
        # Set up auto-refresh if configured
        if self.config.refresh_interval > 0:
            self.set_interval(self.config.refresh_interval, self.refresh_data)

    async def create_panels(self) -> None:
        container = self.query_one('#panels-container', Container)
        await container.remove_children()
        for repo_name in self.config.repos:
            panel = RepoPanel(repo_name)
            await container.mount(panel)

    async def refresh_data(self) -> None:
        """Fetch and update PR data for all repos."""
        self.last_refresh = datetime.now()
        self.update_status(f'Refreshing... ({self.last_refresh.strftime("%H:%M:%S")})')

        for repo_name in self.config.repos:
            try:
                prs = self.gh_wrapper.get_prs(repo_name)
                # Filter based on config
                if not self.config.show_drafts:
                    prs = [p for p in prs if not p.is_draft]
                if not self.config.show_closed:
                    prs = [p for p in prs if p.state == 'OPEN']
                prs = prs[: self.config.max_prs_per_repo]

                for panel in self.query(RepoPanel):
                    if panel.repo_name == repo_name:
                        panel.update_prs(prs)
                        break
            except Exception as e:
                self.update_status(f'Error fetching {repo_name}: {e}')

        self.update_status(f'Last refresh: {self.last_refresh.strftime("%H:%M:%S")}')

    def update_status(self, message: str) -> None:
        status_bar = self.query_one('#status-bar', Static)
        status_bar.update(message)

    def action_refresh(self) -> None:
        """Manual refresh."""
        self.app.run_worker(self.refresh_data())

    def action_open_pr(self) -> None:
        """Open selected PR in browser."""
        focused = self.focused
        if isinstance(focused, PRTable):
            row_key = focused.cursor_row
            if row_key is not None:
                # Get PR number from row key
                pr_number = focused.get_row_at(row_key)[0]
                repo_name = focused.repo_name
                import webbrowser

                url = f'https://github.com/{repo_name}/pull/{pr_number}'
                webbrowser.open(url)

    def action_toggle_drafts(self) -> None:
        self.config.show_drafts = not self.config.show_drafts
        self.app.run_worker(self.refresh_data())

    def action_toggle_closed(self) -> None:
        self.config.show_closed = not self.config.show_closed
        self.app.run_worker(self.refresh_data())

    async def action_quit(self) -> None:
        self.exit()


def main() -> None:
    """Entry point."""
    app = GHPulseApp()
    app.run()


if __name__ == '__main__':
    main()
