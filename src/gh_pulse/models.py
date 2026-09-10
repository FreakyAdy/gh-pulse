"""Data models for gh-pulse."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CIStatus(str, Enum):
    """CI status enum."""

    SUCCESS = 'success'
    FAILURE = 'failure'
    PENDING = 'pending'
    UNKNOWN = 'unknown'


@dataclass
class Repo:
    """Repository model."""

    name: str  # e.g., "owner/repo"
    private: bool = False

    @property
    def owner(self) -> str:
        return self.name.split('/')[0]

    @property
    def repo_name(self) -> str:
        return self.name.split('/')[1] if '/' in self.name else self.name


@dataclass
class PR:
    """Pull request model."""

    number: int
    title: str
    author: str
    state: str  # "OPEN", "CLOSED", "MERGED"
    url: str
    repo: str  # e.g., "owner/repo"
    created_at: str
    updated_at: str
    head_ref: str
    base_ref: str
    is_draft: bool = False
    mergeable: str | None = None  # "MERGEABLE", "CONFLICTING", "UNKNOWN"
    review_decision: str | None = None  # "APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED"
    ci_status: CIStatus = CIStatus.UNKNOWN
    review_requested: bool = False

    def short_title(self, max_len: int = 50) -> str:
        if len(self.title) <= max_len:
            return self.title
        return self.title[: max_len - 3] + '...'

    def age_days(self) -> int:
        created = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
        now = datetime.now(created.tzinfo)
        return (now - created).days


@dataclass
class ReviewRequest:
    """Review request model."""

    pr: PR
