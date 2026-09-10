"""Tests for gh-pulse models."""

from datetime import datetime, timezone

from gh_pulse.models import PR, CIStatus, Repo, ReviewRequest


def test_repo_properties():
    repo = Repo(name='owner/repo', private=True)
    assert repo.owner == 'owner'
    assert repo.repo_name == 'repo'
    assert repo.private is True


def test_pr_short_title():
    pr = PR(
        number=1,
        title='Short title',
        author='user',
        state='OPEN',
        url='https://github.com/owner/repo/pull/1',
        repo='owner/repo',
        created_at='2024-01-01T00:00:00Z',
        updated_at='2024-01-01T00:00:00Z',
        head_ref='feature',
        base_ref='main',
    )
    assert pr.short_title() == 'Short title'

    long_title = 'a' * 60
    pr.title = long_title
    assert len(pr.short_title(50)) == 50
    assert pr.short_title(50).endswith('...')


def test_pr_age_days():
    past = datetime.now(timezone.utc).replace(day=1).isoformat().replace('+00:00', 'Z')
    pr = PR(
        number=1,
        title='Test',
        author='user',
        state='OPEN',
        url='https://github.com/owner/repo/pull/1',
        repo='owner/repo',
        created_at=past,
        updated_at=past,
        head_ref='feature',
        base_ref='main',
    )
    # Age should be >= 0
    assert pr.age_days() >= 0


def test_ci_status_enum():
    assert CIStatus.SUCCESS == 'success'
    assert CIStatus.FAILURE == 'failure'
    assert CIStatus.PENDING == 'pending'
    assert CIStatus.UNKNOWN == 'unknown'


def test_review_request():
    pr = PR(
        number=1,
        title='Test',
        author='user',
        state='OPEN',
        url='https://github.com/owner/repo/pull/1',
        repo='owner/repo',
        created_at='2024-01-01T00:00:00Z',
        updated_at='2024-01-01T00:00:00Z',
        head_ref='feature',
        base_ref='main',
    )
    rr = ReviewRequest(pr=pr)
    assert rr.pr == pr
