"""
/irahorecka/api/githubrepos/read.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to handle the delivery of GitHub repositories from a query.
"""

from irahorecka.models import GitHubRepo


def read_github_repos(repo_names):
    """ENTRY POINT: Yields GitHub repos information as dictionaries from database."""
    for repo_name in repo_names:
        repo = GitHubRepo.query.filter_by(name=repo_name).first()
        yield {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "license": repo.license,
            "private": repo.private,
            "stars": repo.stars,
            "forks": repo.forks,
            "commits": repo.commits,
            "open_issues": repo.open_issues,
            "languages": [{"name": lang.name, "color": lang.color} for lang in repo.languages],
            "url": repo.url,
        }
