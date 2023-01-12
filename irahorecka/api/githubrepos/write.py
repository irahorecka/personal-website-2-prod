"""
/irahorecka/api/githubrepos/write.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module to write and update GitHub repositories database table.
"""

import concurrent.futures
import random
import time

from requests.exceptions import ConnectionError

from github import Github
from github.GithubException import GithubException, UnknownObjectException

from irahorecka.models import db, GitHubRepo, RepoLanguage

LANGUAGE_COLOR = {
    "python": "#3672a5",
    "css": "#563d7c",
    "html": "#e34c26",
    "javascript": "#f1e05a",
    "makefile": "#427819",
    "c++": "#f34b7d",
    "jupyter notebook": "#da5b0b",
    "r": "#198ce7",
    "ruby": "#701516",
    "swift": "#ffac44",
    "racket": "#3d5caa",
    "rich text format": "#f6f8fa",
    "shell": "#89e051",
    "batchfile": "#c1f12e",
}


def write_github_repos(github_token):
    """ENTRY POINT: Writes user's GitHub repos to database. The user is determined via GitHub's access
    token `github_token`."""
    # Fetch repos first to allow fastest write to db.
    repos = fetch_repos(github_token)
    # Drop content in tables - don't bother updating as hard reset for a small
    # table like this is preferable.
    RepoLanguage.query.delete()
    GitHubRepo.query.delete()
    if not repos:
        return
    for repo in repos:
        # Add random latency to prevent `github.GithubException.RateLimitExceededException`
        time.sleep(random.randint(1, 3))
        repo_entry = GitHubRepo(
            name=repo["name"],
            full_name=repo["full_name"],
            description=repo["description"],
            license=repo["license"],
            private=repo["private"],
            stars=repo["stars"],
            forks=repo["forks"],
            commits=repo["commits"],
            open_issues=repo["open_issues"],
            url=repo["url"],
        )
        db.session.add(repo_entry)
        for lang in repo["languages"]:
            # Back-reference programming language used in a repo to `repo_entry`.
            lang_session = RepoLanguage(name=lang["name"], color=lang["color"], repo=repo_entry)
            db.session.add(lang_session)
    db.session.commit()


def fetch_repos(access_token):
    """Fetches GitHub user's repos."""
    user = Github(access_token).get_user()
    # Attempt to query pycraigslist instances even if there's a connection error.
    repos = user.get_repos()
    for i in range(4):
        try:
            return [repo for repo in map_threads(build_repo_dict, repos) if repo is not None]
        except ConnectionError:
            if i == 3:
                # Raise error if error cannot be resolved in 3 attempts.
                raise ConnectionError from ConnectionError
            # Wait a minute before reattempting query.
            time.sleep(60)


def build_repo_dict(repo):
    """Isolates desired properties of a GitHub repository."""
    try:
        # Raises `GithubException` if the git repository is empty.
        commits = len(list(validate_gh_method(repo.get_commits)))
    except GithubException:
        commits = 0
    return {
        "name": repo.full_name.split("/")[-1],
        "full_name": repo.full_name,
        "description": repo.description,
        "license": validate_gh_method(repo.get_license).license.name
        if validate_gh_method(repo.get_license) != ""
        else "",
        "private": repo.private,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "commits": commits,
        "open_issues": repo.open_issues_count,
        "languages": validate_gh_method(get_languages, repo) if validate_gh_method(get_languages, repo) != "" else "",
        "url": f"https://github.com/{repo.full_name}",
    }


def validate_gh_method(method, *args, **kwargs):
    """Wrapper that returns an empty string if PyGithub method
    raises an exception."""
    try:
        return method(*args, **kwargs)
    except UnknownObjectException:
        return ""


def get_languages(repo):
    """Returns language color as seen on GitHub."""
    languages = repo.get_languages()
    return [{"name": lang, "color": LANGUAGE_COLOR.get(lang.lower(), "#ffffff")} for lang in languages]


def map_threads(func, _iterable):
    """Maps function with iterable object in using thread pools."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.map(func, _iterable)
    return result
