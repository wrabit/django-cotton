import json
import time
import urllib.request

# The two sides of the docs point at two repos.
REPOS = {
    "core": "wrabit/django-cotton",
    "ui": "wrabit/django-cotton-ui",
}
CACHE_TTL = 60 * 60 * 6  # 6 hours
FAIL_TTL = 60 * 10  # retry sooner if GitHub was unreachable

# Simple in-process cache. The docs CACHES backend is Redis but the `redis`
# package isn't installed here, so we avoid Django's cache for this.
_cache = {"data": None, "ts": 0.0}


def _fetch_stars(repo):
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "cotton-docs",
            },
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.load(resp).get("stargazers_count")
    except Exception:
        return None


def _format(count):
    if count is None:
        return None
    if count >= 1000:
        return f"{count / 1000:.1f}k".replace(".0k", "k")
    return str(count)


def _counts():
    data, ts = _cache["data"], _cache["ts"]
    if data is not None:
        ttl = CACHE_TTL if all(data.values()) else FAIL_TTL
        if (time.time() - ts) < ttl:
            return data
    data = {key: _format(_fetch_stars(repo)) for key, repo in REPOS.items()}
    _cache["data"], _cache["ts"] = data, time.time()
    return data


def github_stars(request=None):
    counts = _counts()
    return {
        "github_core_repo": "https://github.com/" + REPOS["core"],
        "github_ui_repo": "https://github.com/" + REPOS["ui"],
        "github_core_stars": counts.get("core"),
        "github_ui_stars": counts.get("ui"),
    }
