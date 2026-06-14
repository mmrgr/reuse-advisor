#!/usr/bin/env python3
"""Search GitHub, npm, and PyPI for candidate reusable projects.

This script is intentionally lightweight: it generates candidates and metadata,
then leaves semantic comparison and final judgment to the agent.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


USER_AGENT = "open-source-reuse-advisor/1.0"
CONFIG_DIR = Path(os.environ.get("OPEN_SOURCE_REUSE_ADVISOR_HOME", Path.home() / ".open-source-reuse-advisor"))
TOKEN_FILE = CONFIG_DIR / "github_token"


def request_json(url: str, headers: dict[str, str] | None = None, timeout: int = 20) -> Any:
    merged_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        merged_headers.update(headers)
    req = urllib.request.Request(url, headers=merged_headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, errors="replace"))


def load_github_token() -> tuple[str | None, str]:
    env_token = os.environ.get("GITHUB_TOKEN")
    if env_token:
        return env_token.strip(), "env"
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token, "file"
    return None, "missing"


def save_github_token(token: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token.strip() + "\n", encoding="utf-8")
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass


def validate_github_token(token: str | None) -> tuple[str, str]:
    if not token:
        return "missing", "No GITHUB_TOKEN environment variable or local token file was found."
    try:
        request_json(
            "https://api.github.com/rate_limit",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        return "valid", "GitHub accepted the token."
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            return "invalid", f"GitHub rejected the token with HTTP {exc.code}."
        return "unknown", f"GitHub token check failed with HTTP {exc.code}."
    except Exception as exc:  # noqa: BLE001 - status command should explain failures.
        return "unknown", str(exc)


def github_search(query: str, limit: int, include_lists: bool = False) -> list[dict[str, Any]]:
    github_query = f"{query} in:name,description,readme fork:false archived:false"
    if not include_lists:
        github_query += " -awesome -awesome-list"
    params = {
        "q": github_query,
        "sort": "stars",
        "order": "desc",
        "per_page": str(min(max(limit * 3, limit), 30)),
    }
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(params)
    headers: dict[str, str] = {}
    token, _token_source = load_github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = request_json(url, headers=headers)
    items = []
    for repo in data.get("items", []):
        if not include_lists and is_list_like_repo(repo):
            continue
        items.append(
            {
                "source": "github",
                "name": repo.get("full_name"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "language": repo.get("language"),
                "license": (repo.get("license") or {}).get("spdx_id"),
                "updated_at": repo.get("updated_at"),
                "archived": repo.get("archived"),
                "topics": repo.get("topics", []),
            }
        )
        if len(items) >= limit:
            break
    return items


def is_list_like_repo(repo: dict[str, Any]) -> bool:
    text = " ".join(
        str(part or "")
        for part in [
            repo.get("name"),
            repo.get("full_name"),
            repo.get("description"),
            " ".join(repo.get("topics") or []),
        ]
    ).lower()
    list_markers = ["awesome", "curated-list", "list of", "collection of", "alternatives to"]
    return any(marker in text for marker in list_markers)


def npm_search(query: str, limit: int) -> list[dict[str, Any]]:
    params = {"text": query, "size": str(min(limit, 20))}
    url = "https://registry.npmjs.org/-/v1/search?" + urllib.parse.urlencode(params)
    data = request_json(url)
    items = []
    for obj in data.get("objects", [])[:limit]:
        package = obj.get("package", {})
        links = package.get("links", {})
        items.append(
            {
                "source": "npm",
                "name": package.get("name"),
                "url": links.get("repository") or links.get("npm"),
                "package_url": links.get("npm"),
                "description": package.get("description"),
                "version": package.get("version"),
                "license": package.get("license"),
                "updated_at": package.get("date"),
                "score": obj.get("score", {}).get("final"),
            }
        )
    return items


def pypi_search(query: str, limit: int) -> list[dict[str, Any]]:
    # PyPI has no stable JSON search API. Use its simple search page shape
    # through the XML-RPC-compatible endpoint only when available is overkill,
    # so return a web search URL candidate for manual follow-up.
    encoded = urllib.parse.quote_plus(query)
    return [
        {
            "source": "pypi-search-url",
            "name": f"PyPI search: {query}",
            "url": f"https://pypi.org/search/?q={encoded}",
            "description": "Open this PyPI search result page and inspect matching packages manually.",
        }
    ][:limit]


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = (item.get("url") or item.get("name") or "").lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Search open-source sources for reusable project candidates.")
    parser.add_argument("requirement", nargs="?", help="User requirement or search query")
    parser.add_argument("--query", action="append", default=[], help="Additional query; can be repeated")
    parser.add_argument("--limit", type=int, default=8, help="Candidates per source/query")
    parser.add_argument("--github", action="store_true", help="Search GitHub repositories")
    parser.add_argument("--npm", action="store_true", help="Search npm packages")
    parser.add_argument("--pypi", action="store_true", help="Add PyPI search URLs")
    parser.add_argument("--all", action="store_true", help="Search all supported sources")
    parser.add_argument("--include-lists", action="store_true", help="Do not filter out awesome-list style repositories")
    parser.add_argument("--token-status", action="store_true", help="Check saved or environment GitHub token status")
    parser.add_argument("--save-token", action="store_true", help="Prompt for a GitHub token, validate it, and store it locally")
    args = parser.parse_args()

    if args.token_status:
        token, source = load_github_token()
        status, message = validate_github_token(token)
        json.dump(
            {
                "status": status,
                "source": source,
                "token_file": str(TOKEN_FILE),
                "message": message,
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0 if status == "valid" else 1

    if args.save_token:
        token = getpass.getpass("GitHub token: ").strip()
        status, message = validate_github_token(token)
        if status != "valid":
            print(json.dumps({"status": status, "message": message}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 1
        save_github_token(token)
        json.dump(
            {
                "status": "saved",
                "token_file": str(TOKEN_FILE),
                "message": "GitHub token was validated and saved locally.",
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0

    if not args.requirement:
        parser.error("requirement is required unless --token-status or --save-token is used")

    sources_selected = args.all or not (args.github or args.npm or args.pypi)
    use_github = args.github or sources_selected
    use_npm = args.npm or sources_selected
    use_pypi = args.pypi or sources_selected

    queries = [args.requirement, *args.query]
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for query in queries:
        for source_name, enabled, func in [
            ("github", use_github, lambda q, n: github_search(q, n, args.include_lists)),
            ("npm", use_npm, npm_search),
            ("pypi", use_pypi, pypi_search),
        ]:
            if not enabled:
                continue
            try:
                results.extend(func(query, args.limit))
            except Exception as exc:  # noqa: BLE001 - keep CLI resilient across APIs.
                errors.append({"source": source_name, "query": query, "error": str(exc)})
            time.sleep(0.3)

    payload = {
        "requirement": args.requirement,
        "queries": queries,
        "count": len(dedupe(results)),
        "results": dedupe(results),
        "errors": errors,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if results else 2


if __name__ == "__main__":
    raise SystemExit(main())
