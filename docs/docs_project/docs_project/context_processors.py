import json
import time
import urllib.request

# The two sides of the docs point at two repos / two PyPI packages.
REPOS = {
    "core": "wrabit/django-cotton",
    "ui": "wrabit/django-cotton-ui",
}
PACKAGES = {
    "core": "django-cotton",
    "ui": "django-cotton-ui",
}
CACHE_TTL = 60 * 60 * 6  # 6 hours
FAIL_TTL = 60 * 10  # retry sooner if a request was unreachable

# Simple in-process cache. The docs CACHES backend is Redis but the `redis`
# package isn't installed here, so we avoid Django's cache for this.
_cache = {"data": None, "ts": 0.0}


def _get_json(url):
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "cotton-docs"},
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.load(resp)


def _fetch_stars(repo):
    try:
        return _get_json(f"https://api.github.com/repos/{repo}").get("stargazers_count")
    except Exception:
        return None


def _fetch_version(package):
    try:
        return _get_json(f"https://pypi.org/pypi/{package}/json").get("info", {}).get("version")
    except Exception:
        return None


def _format(count):
    if count is None:
        return None
    if count >= 1000:
        return f"{count / 1000:.1f}k".replace(".0k", "k")
    return str(count)


def _data():
    data, ts = _cache["data"], _cache["ts"]
    if data is not None:
        complete = all(v is not None for v in data.values())
        ttl = CACHE_TTL if complete else FAIL_TTL
        if (time.time() - ts) < ttl:
            return data
    data = {}
    for key, repo in REPOS.items():
        data[f"{key}_stars"] = _format(_fetch_stars(repo))
    for key, package in PACKAGES.items():
        data[f"{key}_version"] = _fetch_version(package)
    _cache["data"], _cache["ts"] = data, time.time()
    return data


def github_stars(request=None):
    d = _data()
    return {
        "github_core_repo": "https://github.com/" + REPOS["core"],
        "github_ui_repo": "https://github.com/" + REPOS["ui"],
        "github_core_stars": d.get("core_stars"),
        "github_ui_stars": d.get("ui_stars"),
        "pypi_core_version": d.get("core_version"),
        "pypi_ui_version": d.get("ui_version"),
    }
