"""Collect the public record from the GitHub API.

Only facts that anyone can read without logging in are used: public
repositories, their releases, download counters, stars and commit dates.
Nothing here is estimated. When a value does not exist it stays ``None`` and
the instruments print a dash.

Failure policy
    Every request is retried with a pause. If the record still cannot be
    read, ``Unavailable`` is raised and the caller keeps the last good
    snapshot: the profile is never rebuilt from partial data.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
WEEKS = 26  # length of the activity window
HEARTBEAT_DAYS = 30  # refresh the build date at least this often (see ``snapshot``)


class Unavailable(RuntimeError):
    """The public record could not be read right now."""


class Missing(RuntimeError):
    """The requested resource does not exist, or its repository holds nothing yet."""


# -- transport -------------------------------------------------------------

def _request(url: str, token: str | None, body: bytes | None = None) -> tuple[object, dict]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "diavlo-factory",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last = "no attempt made"
    for pause in (0, 2, 6):
        time.sleep(pause)
        try:
            request = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode("utf-8")), dict(response.headers)
        except urllib.error.HTTPError as error:
            if error.code in (404, 409):  # 409 is how the API answers for an empty repository
                raise Missing(url) from None
            last = f"HTTP {error.code}"
            if error.code in (401, 403, 422) and "rate limit" not in error.read().decode("utf-8", "replace").lower():
                break  # refused, not busy: retrying will not help
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            last = type(error).__name__
    raise Unavailable(f"{url.split('?')[0]}: {last}")


def _get(path: str, token: str | None, **params: object) -> object:
    query = "?" + urllib.parse.urlencode(params) if params else ""
    return _request(f"{API}{path}{query}", token)[0]


def _pages(path: str, token: str | None, limit: int = 10, **params: object) -> list:
    """Follow ``Link: rel=next`` for at most ``limit`` pages of 100 items."""
    url = f"{API}{path}?" + urllib.parse.urlencode({"per_page": 100, **params})
    items: list = []
    for _ in range(limit):
        page, headers = _request(url, token)
        items.extend(page)
        following = [part.split(";")[0].strip(" <>") for part in headers.get("Link", "").split(",")
                     if 'rel="next"' in part]
        if not following:
            break
        url = following[0]
    return items


# -- facts -----------------------------------------------------------------

def _day(stamp: str | None) -> str | None:
    return stamp[:10] if stamp else None


def _repo(raw: dict) -> dict:
    licence = (raw.get("license") or {}).get("spdx_id")
    return {
        "name": raw["name"],
        "description": raw.get("description"),
        "fork": bool(raw.get("fork")),
        "archived": bool(raw.get("archived")),
        "stars": raw.get("stargazers_count", 0),
        "forks": raw.get("forks_count", 0),
        "created": _day(raw.get("created_at")),
        "pushed": _day(raw.get("pushed_at")),
        "branch": raw.get("default_branch"),
        "licence": licence if licence and licence != "NOASSERTION" else None,
    }


def _list_repos(login: str, token: str | None, known: list[str]) -> list[dict]:
    """Every public repository the account owns.

    The listing endpoint is the source of truth. If it cannot be reached, the
    repositories already on record are refreshed one by one instead, so a
    single failing endpoint does not freeze the whole profile.
    """
    try:
        raw = _pages(f"/users/{login}/repos", token, type="owner", sort="full_name")
    except Unavailable:
        raw = []
        for name in known:
            try:
                raw.append(_get(f"/repos/{login}/{name}", token))
            except Missing:
                continue
        if not raw:
            raise
    return sorted((_repo(item) for item in raw if not item.get("private")), key=lambda repo: repo["name"].lower())


def _releases(login: str, name: str, token: str | None) -> list[dict]:
    """Published releases, newest first. Downloads are those of the largest asset."""
    found = []
    for raw in _pages(f"/repos/{login}/{name}/releases", token):
        if raw.get("draft") or not raw.get("published_at"):
            continue
        assets = raw.get("assets") or []
        largest = max(assets, key=lambda asset: asset.get("size", 0)) if assets else None
        found.append({
            "tag": raw["tag_name"],
            "published": raw["published_at"],
            "prerelease": bool(raw.get("prerelease")),
            "downloads": largest["download_count"] if largest else None,
        })
    return sorted(found, key=lambda release: release["published"], reverse=True)


def _languages(login: str, name: str, token: str | None) -> list[str]:
    """Languages by size, largest first."""
    sizes = _get(f"/repos/{login}/{name}/languages", token)
    return [language for language, _ in sorted(sizes.items(), key=lambda item: -item[1])]


def _paths(login: str, repo: dict, wanted: list[str], token: str | None) -> list[str]:
    """Which of the ``wanted`` file paths exist on the default branch."""
    if not wanted:
        return []
    try:
        tree = _get(f"/repos/{login}/{repo['name']}/git/trees/{repo['branch']}", token, recursive=1)
    except Missing:
        return []
    present = {entry["path"] for entry in tree.get("tree", [])}
    return [path for path in wanted if path in present]


def _monday(day: dt.date) -> dt.date:
    return day - dt.timedelta(days=day.weekday())


def _window(today: dt.date) -> list[dt.date]:
    """Mondays of the last ``WEEKS`` weeks, oldest first, ending with the current week."""
    last = _monday(today)
    return [last - dt.timedelta(weeks=WEEKS - 1 - index) for index in range(WEEKS)]


def _commit_weeks(login: str, repos: list[dict], token: str | None, today: dt.date) -> list[list]:
    """Commits attributed to the account in its public repositories, per week."""
    window = _window(today)
    counts = {week: 0 for week in window}
    since = f"{window[0].isoformat()}T00:00:00Z"
    for repo in repos:
        if repo["fork"]:
            continue
        try:
            commits = _pages(f"/repos/{login}/{repo['name']}/commits", token, author=login, since=since)
        except Missing:
            continue
        for commit in commits:
            week = _monday(dt.date.fromisoformat(commit["commit"]["author"]["date"][:10]))
            if week in counts:
                counts[week] += 1
    return [[week.isoformat(), counts[week]] for week in window]


_CALENDAR = """query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"""


def _calendar_weeks(login: str, token: str | None, today: dt.date) -> list[list] | None:
    """The contribution calendar, per week. Needs a token; ``None`` when unavailable."""
    if not token:
        return None
    body = json.dumps({"query": _CALENDAR, "variables": {"login": login}}).encode("utf-8")
    try:
        answer, _ = _request(f"{API}/graphql", token, body)
        weeks = answer["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (Unavailable, Missing, KeyError, TypeError):
        return None
    window = _window(today)
    counts = {week: 0 for week in window}
    for week in weeks:
        for day in week["contributionDays"]:
            monday = _monday(dt.date.fromisoformat(day["date"]))
            if monday in counts:
                counts[monday] += day["contributionCount"]
    return [[week.isoformat(), counts[week]] for week in window]


# -- snapshot ---------------------------------------------------------------

def _seed(facts: dict) -> str:
    canonical = json.dumps(facts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha1(canonical).hexdigest()[:6]


def snapshot(registry: dict, previous: dict | None, today: dt.date, token: str | None = None) -> dict:
    """Read the public record and return a new snapshot.

    ``captured`` only moves when a fact changed, or after ``HEARTBEAT_DAYS``
    without change. The heartbeat keeps the build date honest and gives the
    repository the activity GitHub requires to keep scheduled workflows on.
    ``seed`` is a short fingerprint of the repositories; the gate draws its
    skyline from it.
    """
    token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    login = registry["login"]
    known = sorted({line["repo"] for line in registry["lines"]} | set(registry.get("ignore", [])) | {login}
                   | {repo["name"] for repo in (previous or {}).get("repos", [])})
    repos = _list_repos(login, token, known)
    wanted = {line["repo"]: [link["path"] for link in line.get("links", []) if "path" in link]
              for line in registry["lines"]}
    for repo in repos:
        own = not repo["fork"]
        repo["releases"] = _releases(login, repo["name"], token) if own else []
        repo["languages"] = _languages(login, repo["name"], token) if own else []
        repo["paths"] = _paths(login, repo, wanted.get(repo["name"], []), token) if own else []

    calendar = _calendar_weeks(login, token, today)
    if calendar is not None:
        activity = {"source": "calendar", "weeks": calendar}
    elif previous and previous.get("activity", {}).get("source") == "calendar":
        activity = previous["activity"]  # keep one definition rather than flip between two
    else:
        activity = {"source": "commits", "weeks": _commit_weeks(login, repos, token, today)}

    facts = {"schema": 1, "login": login, "repos": repos, "activity": activity}
    captured = today.isoformat()
    if previous and all(previous.get(key) == value for key, value in facts.items()):
        age = (today - dt.date.fromisoformat(previous["captured"])).days
        if age < HEARTBEAT_DAYS:
            captured = previous["captured"]
    # The seed follows the repositories only: it moves when something ships, is
    # starred or is downloaded, not when the activity window slides by a week.
    return {**facts, "captured": captured, "seed": _seed({"login": login, "repos": repos})}
