"""Read-only GitHub release checks. No credentials, PDF data, or executable downloads."""

import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


APP_VERSION = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
REPOSITORY = "iyansanjaya/ExpCore"
RELEASES_URL = f"https://github.com/{REPOSITORY}/releases"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
CHECK_INTERVAL = 24 * 60 * 60
MANUAL_INTERVAL = 60
ERROR_INTERVAL = 15 * 60
MAX_RESPONSE_BYTES = 1024 * 1024


def version_tuple(value):
    """Stable vMAJOR.MINOR[.PATCH] tags; numeric comparison, never lexicographic."""
    if not isinstance(value, str) or not re.fullmatch(
        r"v?(0|[1-9][0-9]{0,4})\.(0|[1-9][0-9]{0,4})(?:\.(0|[1-9][0-9]{0,4}))?", value
    ):
        raise ValueError("Nomor versi rilis tidak valid.")
    parts = tuple(map(int, value.removeprefix("v").split(".")))
    return parts + (0,) * (3 - len(parts))


version_tuple(APP_VERSION)  # Fail early if the packaged VERSION file is invalid.


@dataclass(frozen=True)
class UpdateResult:
    status: str
    tag: str = ""
    error: str = ""
    retry_at: float = 0

    @property
    def version(self):
        return self.tag.removeprefix("v")

    @property
    def url(self):
        # Build the URL from a validated tag, never navigate to remote/cache URLs.
        version_tuple(self.tag)
        return f"{RELEASES_URL}/tag/{self.tag}"


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "Unexpected release API redirect", headers, fp)


def _retry_at(headers, now):
    """Honor GitHub's Retry-After / rate reset, bounded against malformed headers."""
    delay = ERROR_INTERVAL
    try:
        value = headers.get("Retry-After")
        if value:
            try:
                delay = float(value)
            except ValueError:
                delay = parsedate_to_datetime(value).timestamp() - now
        elif headers.get("X-RateLimit-Reset"):
            delay = float(headers["X-RateLimit-Reset"]) - now
        if not math.isfinite(delay):
            delay = ERROR_INTERVAL
    except (TypeError, ValueError, OverflowError):
        delay = ERROR_INTERVAL
    return now + max(MANUAL_INTERVAL, min(delay, CHECK_INTERVAL))


def _release_state(data):
    if not isinstance(data, dict) or data.get("draft") is not False or data.get("prerelease") is not False:
        raise ValueError("Expected a published stable release")
    tag = data.get("tag_name")
    version_tuple(tag)
    if data.get("html_url") != f"{RELEASES_URL}/tag/{tag}":
        raise ValueError("Unexpected release URL")
    assets = data.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Invalid assets")
    names = {"ExpCore.exe", f"ExpCore-Setup-{tag.removeprefix('v')}.exe"}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        if (name in names and asset.get("state") == "uploaded"
                and type(asset.get("size")) is int and asset["size"] > 0
                and asset.get("browser_download_url") == f"{RELEASES_URL}/download/{tag}/{name}"):
            return "release", tag
    return "pending", tag


class UpdateChecker:
    """One worker per UI instance; a small per-user cache also limits restart traffic."""

    def __init__(self, cache_path=None, current_version=APP_VERSION):
        self.current_version = version_tuple(current_version)
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        self.cache_path = Path(cache_path) if cache_path is not None else base / "ExpCore" / "update-check.json"
        self._cache = None

    def _load_cache(self, now):
        try:
            cache = self._cache
            if cache is None:
                with self.cache_path.open("rb") as stream:
                    raw = stream.read(8193)
                if len(raw) > 8192:
                    return None
                cache = json.loads(raw)
            checked = cache["checked_at"]
            retry = cache["retry_at"]
            if (type(checked) not in (int, float) or type(retry) not in (int, float)
                    or not math.isfinite(checked) or not math.isfinite(retry)
                    or not 0 <= checked <= now or not 0 <= retry <= checked + CHECK_INTERVAL):
                return None
            if cache["repository"] != REPOSITORY or cache["schema"] != 1:
                return None
            if cache["state"] in ("release", "pending"):
                version_tuple(cache["tag"])
            elif cache["state"] not in ("unpublished", "error"):
                return None
            if cache["error"] not in ("", "network", "rate_limit", "invalid", "server"):
                return None
            return cache
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _save_cache(self, cache):
        self._cache = cache  # Read-only user profiles still get session-level throttling.
        temporary = None
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.cache_path.parent,
                                             prefix="update-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(cache, stream)
            os.replace(temporary, self.cache_path)
        except OSError:
            pass  # Update notification must remain usable if cache storage is unavailable.
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def _result(self, cache):
        state = cache["state"]
        tag = cache.get("tag", "")
        if state in ("release", "pending"):
            state = ("available" if state == "release" else "pending") if version_tuple(tag) > self.current_version else "current"
        return UpdateResult(state, tag, cache["error"], cache["retry_at"])

    def check(self, force=False):
        now = time.time()
        cache = self._load_cache(now)
        interval = MANUAL_INTERVAL if force else (ERROR_INTERVAL if cache and cache["state"] == "error" else CHECK_INTERVAL)
        if cache and (now < cache["retry_at"] or now - cache["checked_at"] < interval):
            return self._result(cache)

        state, tag, error, retry = "error", "", "", 0
        request = Request(API_URL, headers={
            "Accept": "application/vnd.github+json", "User-Agent": f"ExpCore/{APP_VERSION}",
            "X-GitHub-Api-Version": "2026-03-10",
        })
        try:
            # Default HTTPS certificate verification remains enabled. No redirects or credentials.
            with build_opener(_NoRedirects()).open(request, timeout=10) as response:
                if response.status != 200:
                    raise ValueError("Unexpected response status")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("Release response too large")
                state, tag = _release_state(json.loads(raw))
        except HTTPError as exc:
            try:
                if exc.code == 404:
                    state = "unpublished"
                else:
                    error = "rate_limit" if exc.code in (403, 429) else "server"
                    retry = _retry_at(exc.headers, now)
            finally:
                exc.close()
        except (URLError, OSError, HTTPException):
            error, retry = "network", now + ERROR_INTERVAL
        except (ValueError, TypeError):
            error, retry = "invalid", now + ERROR_INTERVAL
        cache = {"schema": 1, "repository": REPOSITORY, "checked_at": now, "retry_at": retry,
                 "state": state, "tag": tag, "error": error}
        self._save_cache(cache)
        return self._result(cache)
