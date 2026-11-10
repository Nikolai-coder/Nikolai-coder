"""Turn a snapshot and the registry into what the instruments display.

Everything the modules print is derived here, in one place, from two inputs:
``registry.json`` (what the operator declares) and ``data/snapshot.json``
(what the public record says). No module reads the network.
"""

from __future__ import annotations

import re

from .typeface import GLYPHS

DASH = "-"  # printed wherever a value does not exist


def lettering(string: str) -> str:
    """Reduce any string to what FACTORY CUT can set."""
    cleaned = re.sub(r"[_\s]+", " ", string.upper())
    return "".join(char for char in cleaned if char in GLYPHS).strip() or DASH


def _status(repo: dict) -> str:
    if repo["releases"]:
        return "SHIPPING"
    if repo["languages"]:
        return "SOURCE OPEN"
    return "IN ASSEMBLY"


def _readouts(repo: dict) -> list[tuple[str, str]]:
    """Four label/value pairs for a line card. Missing values print a dash."""
    latest = repo["releases"][0] if repo["releases"] else None
    cells = [("RELEASE", lettering(latest["tag"]) if latest else DASH)]
    cells.append(("SHIPPED", latest["published"][:10]) if latest else ("UPDATED", repo["pushed"] or DASH))
    extras: list[tuple[str, str]] = []
    if latest:
        extras.append(("DOWNLOADS", str(sum(release["downloads"] or 0 for release in repo["releases"]))))
    if repo["languages"]:
        extras.append(("LANGUAGE", lettering(repo["languages"][0])))
    if repo["licence"]:
        extras.append(("LICENCE", lettering(repo["licence"])))
    extras += [("STARS", str(repo["stars"])), ("FORKS", str(repo["forks"]))]
    return cells + extras[:2]


def _alt(index: int, entry: dict, repo: dict, status: str) -> str:
    """Plain-language description of a line plate, for people who cannot see it."""
    parts = [f"Line {index:02d}: {entry['name']}. {entry['claim']}. Status: {status.lower()}"]
    if repo["releases"]:
        latest = repo["releases"][0]
        downloads = sum(release["downloads"] or 0 for release in repo["releases"])
        parts.append(f"latest release {latest['tag']} on {latest['published'][:10]}")
        parts.append(f"{downloads} installer downloads")
    else:
        parts.append(f"no public release; last updated {repo['pushed']}")
    parts.append(f"{repo['stars']} stars")
    return "; ".join(parts) + "."


def _discovered(repos: dict[str, dict], registry: dict) -> list[dict]:
    """Public repositories that carry code or releases but are not in the registry yet.

    They get a plain card automatically, so a newly published project shows up
    on the profile before anyone writes copy for it.
    """
    declared = {line["repo"] for line in registry["lines"]} | set(registry.get("ignore", []))
    declared.add(registry["login"])
    entries = []
    for name, repo in repos.items():
        if name in declared or repo["fork"] or repo["archived"]:
            continue
        if not (repo["releases"] or repo["languages"]):
            continue
        entries.append({
            "repo": name, "name": lettering(name.replace("-", " ")), "field": "UNASSIGNED", "art": "crate",
            "claim": (repo["description"] or "New arrival, not yet documented")[:70],
            "summary": repo["description"] or "A new public repository. No description has been written yet.",
            "edge": "", "stack": repo["languages"][:4], "links": [],
        })
    return sorted(entries, key=lambda entry: repos[entry["repo"]]["pushed"] or "", reverse=True)


def view(snapshot: dict, registry: dict) -> dict:
    """The complete display model."""
    login = snapshot["login"]
    repos = {repo["name"]: repo for repo in snapshot["repos"]}
    lines = []
    for entry in registry["lines"] + _discovered(repos, registry):
        repo = repos.get(entry["repo"])
        if repo is None:  # no longer public: drop the line rather than link to nothing
            continue
        url = f"https://github.com/{login}/{repo['name']}"
        links = [("Repository", url)]
        if repo["releases"]:
            links.append(("Latest release", f"{url}/releases/latest"))
        links += [(link["label"], f"{url}/blob/{repo['branch']}/{link['path']}")
                  for link in entry.get("links", []) if link.get("path") in repo["paths"]]
        index, status = len(lines) + 1, _status(repo)
        lines.append({
            **entry, "index": index, "url": url, "links": links, "status": status,
            "readouts": _readouts(repo), "releases": repo["releases"], "stars": repo["stars"],
            "alt": _alt(index, entry, repo, status),
        })

    shipped = [(stamp[:10], tag, downloads, name) for stamp, tag, downloads, name in sorted(
        (release["published"], release["tag"], release["downloads"] or 0, line["name"])
        for line in lines for release in line["releases"])]
    own = [repo for repo in snapshot["repos"] if not repo["fork"]]
    weeks = snapshot["activity"]["weeks"]
    return {
        "login": login,
        "captured": snapshot["captured"],
        "seed": snapshot["seed"],
        "site": registry.get("site", ""),
        "output": registry.get("output", []),
        "lines": lines,
        "sealed": [lettering(name) for name in registry.get("sealed", [])],
        "components": [
            {**component, "lines": [line["index"] for line in lines if line["repo"] in component["lines"]]}
            for component in registry.get("components", [])
        ],
        "shipped": shipped,
        "totals": {
            "releases": len(shipped),
            "downloads": sum(item[2] for item in shipped),
            "stars": sum(repo["stars"] for repo in own),
            "lines": len(lines),
            "repositories": len(snapshot["repos"]),
        },
        "activity": {
            "source": snapshot["activity"]["source"],
            "weeks": weeks,
            "total": sum(count for _, count in weeks),
        },
    }
