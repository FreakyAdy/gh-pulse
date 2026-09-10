"""gh CLI wrapper for fetching PR data."""

import json
import subprocess
from typing import Any

from gh_pulse.models import PR, CIStatus, Repo, ReviewRequest


class GHWrapper:
    """Wrapper around `gh` CLI for fetching PR and review data."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def _run(self, args: list[str]) -> dict[str, Any] | list[Any]:
        """Run gh command and return parsed JSON."""
        cmd = ['gh'] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
        if result.returncode != 0:
            raise RuntimeError(f'gh command failed: {result.stderr.strip()}')
        if not result.stdout.strip():
            return []
        return json.loads(result.stdout)

    def get_repos(self, limit: int = 100) -> list[Repo]:
        """Get list of repositories the user has access to."""
        data = self._run([
            'repo',
            'list',
            '--limit',
            str(limit),
            '--json',
            'nameWithOwner,owner,isPrivate,visibility',
        ])
        return [
            Repo(name=item['nameWithOwner'], private=item.get('isPrivate', False)) for item in data
        ]

    def get_prs(self, repo: str, state: str = 'open') -> list[PR]:
        """Get PRs for a repository."""
        data = self._run([
            'pr',
            'list',
            '--repo',
            repo,
            '--state',
            state,
            '--json',
            'number,title,author,state,url,createdAt,updatedAt,headRefName,baseRefName,isDraft,mergeable,reviewDecision,statusCheckRollup',
        ])
        return [self._parse_pr(item, repo) for item in data]

    def get_review_requests(self, repo: str | None = None) -> list[ReviewRequest]:
        """Get PRs where the current user is requested for review."""
        args = [
            'search',
            'prs',
            '--review-requested=@me',
            '--state=open',
            '--json',
            'number,title,author,state,url,createdAt,updatedAt,headRefName,baseRefName,isDraft,mergeable,reviewDecision,statusCheckRollup,repository',
        ]
        if repo:
            args.extend(['--repo', repo])
        data = self._run(args)
        review_requests = []
        for item in data:
            repo_name = item.get('repository', {}).get('nameWithOwner', repo or 'unknown')
            pr = self._parse_pr(item, repo_name)
            pr.review_requested = True
            review_requests.append(ReviewRequest(pr=pr))
        return review_requests

    def get_pr_details(self, repo: str, number: int) -> PR | None:
        """Get detailed PR information including CI status."""
        data = self._run([
            'pr',
            'view',
            str(number),
            '--repo',
            repo,
            '--json',
            'number,title,author,state,url,createdAt,updatedAt,headRefName,baseRefName,isDraft,mergeable,reviewDecision,statusCheckRollup,reviews,reviewRequests',
        ])
        if not data:
            return None
        return self._parse_pr(data, repo)

    def _parse_pr(self, data: dict[str, Any], repo: str) -> PR:
        """Parse PR data from gh output."""
        # Parse CI status
        ci_status = CIStatus.PENDING
        status_rollup = data.get('statusCheckRollup', [])
        if status_rollup:
            conclusions = [c.get('conclusion') for c in status_rollup if c.get('conclusion')]
            if all(c == 'SUCCESS' for c in conclusions):
                ci_status = CIStatus.SUCCESS
            elif any(c in ('FAILURE', 'ERROR', 'TIMED_OUT', 'CANCELLED') for c in conclusions):
                ci_status = CIStatus.FAILURE
            elif any(c in ('PENDING', 'IN_PROGRESS', 'QUEUED', 'REQUESTED') for c in conclusions):
                ci_status = CIStatus.PENDING
            else:
                ci_status = CIStatus.PENDING

        # Check if current user is requested for review
        review_requested = False
        review_requests = data.get('reviewRequests', [])
        # This is simplified - in reality we'd check current user
        # For now, we'll just note if there are review requests
        review_requested = len(review_requests) > 0

        return PR(
            number=data['number'],
            title=data['title'],
            author=data['author']['login'] if data.get('author') else 'unknown',
            state=data['state'],
            url=data['url'],
            repo=repo,
            created_at=data['createdAt'],
            updated_at=data['updatedAt'],
            head_ref=data.get('headRefName', ''),
            base_ref=data.get('baseRefName', ''),
            is_draft=data.get('isDraft', False),
            mergeable=data.get('mergeable'),
            review_decision=data.get('reviewDecision'),
            ci_status=ci_status,
            review_requested=review_requested,
        )
