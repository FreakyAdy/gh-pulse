"""Tests for gh-pulse gh_wrapper with mocked gh output."""

import json
from unittest.mock import MagicMock, patch

import pytest

from gh_pulse.gh_wrapper import GHWrapper
from gh_pulse.models import CIStatus, Repo


@pytest.fixture
def mock_gh_output():
    """Sample gh pr list JSON output."""
    return [
        {
            'number': 42,
            'title': 'Add new feature',
            'author': {'login': 'contributor'},
            'state': 'OPEN',
            'url': 'https://github.com/owner/repo/pull/42',
            'createdAt': '2024-01-15T10:00:00Z',
            'updatedAt': '2024-01-15T12:00:00Z',
            'headRefName': 'feature/new-thing',
            'baseRefName': 'main',
            'isDraft': False,
            'mergeable': 'MERGEABLE',
            'reviewDecision': 'REVIEW_REQUIRED',
            'statusCheckRollup': [
                {'name': 'CI', 'conclusion': 'SUCCESS'},
                {'name': 'Tests', 'conclusion': 'SUCCESS'},
            ],
        },
        {
            'number': 43,
            'title': 'Fix critical bug',
            'author': {'login': 'maintainer'},
            'state': 'OPEN',
            'url': 'https://github.com/owner/repo/pull/43',
            'createdAt': '2024-01-16T08:00:00Z',
            'updatedAt': '2024-01-16T09:00:00Z',
            'headRefName': 'fix/critical',
            'baseRefName': 'main',
            'isDraft': True,
            'mergeable': 'CONFLICTING',
            'reviewDecision': 'CHANGES_REQUESTED',
            'statusCheckRollup': [{'name': 'CI', 'conclusion': 'FAILURE'}],
        },
    ]


@pytest.fixture
def mock_repo_output():
    """Sample gh repo list JSON output."""
    return [
        {
            'nameWithOwner': 'owner/repo1',
            'isPrivate': False,
            'owner': {'login': 'owner'},
            'visibility': 'PUBLIC',
        },
        {
            'nameWithOwner': 'owner/repo2',
            'isPrivate': True,
            'owner': {'login': 'owner'},
            'visibility': 'PRIVATE',
        },
    ]


def test_get_repos(mock_repo_output):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(mock_repo_output), stderr=''
        )
        wrapper = GHWrapper()
        repos = wrapper.get_repos(limit=10)
        assert len(repos) == 2
        assert isinstance(repos[0], Repo)
        assert repos[0].name == 'owner/repo1'
        assert repos[0].private is False
        assert repos[1].name == 'owner/repo2'
        assert repos[1].private is True


def test_parse_pr_success_ci(mock_gh_output):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(mock_gh_output), stderr=''
        )
        wrapper = GHWrapper()
        prs = wrapper.get_prs('owner/repo')
        assert len(prs) == 2
        # First PR has all SUCCESS checks
        assert prs[0].ci_status == CIStatus.SUCCESS
        assert prs[0].number == 42
        assert prs[0].title == 'Add new feature'
        assert prs[0].author == 'contributor'
        assert prs[0].is_draft is False
        # Second PR has FAILURE
        assert prs[1].ci_status == CIStatus.FAILURE
        assert prs[1].is_draft is True


def test_parse_pr_pending_ci():
    pending_output = [
        {
            'number': 1,
            'title': 'Pending PR',
            'author': {'login': 'user'},
            'state': 'OPEN',
            'url': 'https://github.com/owner/repo/pull/1',
            'createdAt': '2024-01-15T10:00:00Z',
            'updatedAt': '2024-01-15T12:00:00Z',
            'headRefName': 'feature',
            'baseRefName': 'main',
            'isDraft': False,
            'mergeable': 'MERGEABLE',
            'reviewDecision': 'REVIEW_REQUIRED',
            'statusCheckRollup': [{'name': 'CI', 'conclusion': 'PENDING'}],
        }
    ]
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0, stdout=json.dumps(pending_output), stderr=''
        )
        wrapper = GHWrapper()
        prs = wrapper.get_prs('owner/repo')
        assert prs[0].ci_status == CIStatus.PENDING


def test_parse_pr_no_ci():
    no_ci_output = [
        {
            'number': 1,
            'title': 'No CI PR',
            'author': {'login': 'user'},
            'state': 'OPEN',
            'url': 'https://github.com/owner/repo/pull/1',
            'createdAt': '2024-01-15T10:00:00Z',
            'updatedAt': '2024-01-15T12:00:00Z',
            'headRefName': 'feature',
            'baseRefName': 'main',
            'isDraft': False,
            'mergeable': 'MERGEABLE',
            'reviewDecision': 'REVIEW_REQUIRED',
            'statusCheckRollup': [],
        }
    ]
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(no_ci_output), stderr='')
        wrapper = GHWrapper()
        prs = wrapper.get_prs('owner/repo')
        assert prs[0].ci_status == CIStatus.PENDING  # Empty rollup -> PENDING


def test_get_prs_error():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='gh: repo not found')
        wrapper = GHWrapper()
        with pytest.raises(RuntimeError, match='gh command failed'):
            wrapper.get_prs('owner/nonexistent')


def test_get_repos_error():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='gh: auth required')
        wrapper = GHWrapper()
        with pytest.raises(RuntimeError, match='gh command failed'):
            wrapper.get_repos()


def test_empty_output():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
        wrapper = GHWrapper()
        repos = wrapper.get_repos()
        assert repos == []


def test_mixed_ci_status():
    """Test CI status when some checks pass and some fail."""
    mixed_output = [
        {
            'number': 1,
            'title': 'Mixed CI',
            'author': {'login': 'user'},
            'state': 'OPEN',
            'url': 'https://github.com/owner/repo/pull/1',
            'createdAt': '2024-01-15T10:00:00Z',
            'updatedAt': '2024-01-15T12:00:00Z',
            'headRefName': 'feature',
            'baseRefName': 'main',
            'isDraft': False,
            'mergeable': 'MERGEABLE',
            'reviewDecision': 'REVIEW_REQUIRED',
            'statusCheckRollup': [
                {'name': 'Lint', 'conclusion': 'SUCCESS'},
                {'name': 'Tests', 'conclusion': 'FAILURE'},
            ],
        }
    ]
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mixed_output), stderr='')
        wrapper = GHWrapper()
        prs = wrapper.get_prs('owner/repo')
        # Any failure -> FAILURE
        assert prs[0].ci_status == CIStatus.FAILURE
