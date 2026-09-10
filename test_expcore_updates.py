"""Offline release/check/cache regressions. Run with the standard library unittest runner."""

from copy import deepcopy
from email.message import Message
from io import BytesIO
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import expcore_updates as updates


def release(tag="v1.7.0"):
    return {
        "tag_name": tag, "draft": False, "prerelease": False,
        "html_url": f"{updates.RELEASES_URL}/tag/{tag}",
        "assets": [{"name": "ExpCore.exe", "state": "uploaded", "size": 1234,
                    "browser_download_url": f"{updates.RELEASES_URL}/download/{tag}/ExpCore.exe"}],
    }


class UpdateChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "updates.json"
        self.checker = updates.UpdateChecker(self.path, "1.6.0")
        clock = patch("expcore_updates.time.time", return_value=1000000)
        self.clock = clock.start()
        self.addCleanup(clock.stop)
        opener = patch("expcore_updates.build_opener")
        self.opener = opener.start().return_value
        self.addCleanup(opener.stop)
        self.respond(release())

    def respond(self, data):
        response = MagicMock()
        response.status = 200
        response.read.return_value = json.dumps(data).encode()
        self.opener.open.return_value.__enter__.return_value = response
        return response

    def test_version_order_and_rejected_tags(self):
        self.assertEqual(updates.version_tuple("v1.5"), updates.version_tuple("1.5.0"))
        self.assertGreater(updates.version_tuple("v1.10.0"), updates.version_tuple("1.9.9"))
        for tag in (None, 15, "", "v1.6.0-rc.1", "v1.6.0+build", "v01.6.0", "v1.6.0/evil",
                    "1.6.0\n", "https://evil.test", "999999.0.0"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                updates.version_tuple(tag)

    def test_live_request_contract_and_trusted_link(self):
        result = self.checker.check()
        self.assertEqual(result.status, "available")
        self.assertEqual(result.url, f"{updates.RELEASES_URL}/tag/v1.7.0")
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.full_url, updates.API_URL)
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertFalse(request.has_header("Authorization"))
        self.assertEqual(self.opener.open.call_args.kwargs["timeout"], 10)

    def test_current_older_and_pending_releases(self):
        for tag, expected in (("v1.5", "current"), ("v1.6.0", "current"), ("v1.10.0", "available")):
            with self.subTest(tag=tag):
                self.respond(release(tag))
                self.clock.return_value += updates.CHECK_INTERVAL + 1
                self.assertEqual(self.checker.check().status, expected)
        data = release()
        data["assets"] = []
        self.respond(data)
        self.clock.return_value += updates.CHECK_INTERVAL + 1
        self.assertEqual(self.checker.check().status, "pending")

    def test_release_validation_and_installer_readiness(self):
        good = release()
        for field, value in (("draft", True), ("prerelease", True), ("draft", "false"),
                             ("tag_name", "v1.7.0-rc.1"), ("html_url", "https://evil.test"),
                             ("html_url", f"{updates.RELEASES_URL}/tag/v1.8.0"), ("assets", {})):
            data = deepcopy(good)
            data[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                updates._release_state(data)
        for field, value in (("state", "new"), ("size", 0), ("size", True), ("name", "other.exe"),
                             ("browser_download_url", "https://evil.test/setup.exe")):
            data = deepcopy(good)
            data["assets"][0][field] = value
            self.assertEqual(updates._release_state(data)[0], "pending")
        name = "ExpCore-Setup-1.7.0.exe"
        good["assets"][0].update(name=name, browser_download_url=f"{updates.RELEASES_URL}/download/v1.7.0/{name}")
        self.assertEqual(updates._release_state(good), ("release", "v1.7.0"))

    def test_cache_across_restarts_manual_throttle_and_app_upgrade(self):
        self.checker.check()
        self.clock.return_value += 59
        restarted = updates.UpdateChecker(self.path, "1.6.0")
        self.assertEqual(restarted.check(force=True).status, "available")
        self.assertEqual(self.opener.open.call_count, 1)
        self.clock.return_value += 1
        restarted.check(force=True)
        self.assertEqual(self.opener.open.call_count, 2)
        self.clock.return_value += 100
        upgraded = updates.UpdateChecker(self.path, "1.7.0")
        self.assertEqual(upgraded.check().status, "current")
        self.assertEqual(self.opener.open.call_count, 2)
        self.clock.return_value += updates.CHECK_INTERVAL
        upgraded.check()
        self.assertEqual(self.opener.open.call_count, 3)

    def test_corrupt_future_and_wrong_repo_cache_are_ignored(self):
        self.checker.check()
        valid = json.loads(self.path.read_text())
        variants = [b"not json", b"x" * 8193, b"null", b"[]"]
        for key, value in (("checked_at", 1000001), ("retry_at", float("nan")),
                           ("schema", 2), ("repository", "another/repo"), ("tag", "bad")):
            cache = {**valid, key: value}
            variants.append(json.dumps(cache).encode())
        for raw in variants:
            self.path.write_bytes(raw)
            self.opener.open.reset_mock()
            self.assertEqual(updates.UpdateChecker(self.path).check().status, "available")
            self.opener.open.assert_called_once()

    def test_network_tls_and_invalid_responses_back_off(self):
        for error in (URLError("offline"), TimeoutError(), ssl.SSLCertVerificationError("untrusted certificate")):
            self.opener.open.side_effect = error
            self.clock.return_value += updates.CHECK_INTERVAL + 1
            result = self.checker.check()
            self.assertEqual((result.status, result.error), ("error", "network"))
            count = self.opener.open.call_count
            self.checker.check(force=True)
            self.assertEqual(self.opener.open.call_count, count)
            self.clock.return_value += updates.ERROR_INTERVAL
            self.checker.check()
            self.assertEqual(self.opener.open.call_count, count + 1)
        self.opener.open.side_effect = None
        for payload in (b"{broken", b"null", b"[]", b"x" * (updates.MAX_RESPONSE_BYTES + 1)):
            response = self.respond(release())
            response.read.return_value = payload
            self.clock.return_value += updates.CHECK_INTERVAL + 1
            self.assertEqual(self.checker.check().error, "invalid")

    def test_http_errors_and_retry_after(self):
        for code, status, error in ((404, "unpublished", ""), (403, "error", "rate_limit"),
                                    (429, "error", "rate_limit"), (503, "error", "server")):
            headers = Message()
            headers["Retry-After"] = "3600"
            self.opener.open.side_effect = HTTPError(updates.API_URL, code, "test", headers, BytesIO())
            self.clock.return_value += updates.CHECK_INTERVAL + 1
            result = self.checker.check()
            self.assertEqual((result.status, result.error), (status, error))
            if code != 404:
                self.assertEqual(result.retry_at, self.clock.return_value + 3600)
        self.assertEqual(updates._retry_at({"Retry-After": "nan"}, 1000), 1000 + updates.ERROR_INTERVAL)
        self.assertEqual(updates._retry_at({"X-RateLimit-Reset": "2000"}, 1000), 2000)
        self.assertEqual(updates._retry_at({"Retry-After": "Thu, 01 Jan 1970 01:00:00 GMT"}, 1000), 3600)

    def test_redirects_and_cache_write_failures(self):
        with self.assertRaises(HTTPError):
            updates._NoRedirects().redirect_request(updates.Request(updates.API_URL), None, 302, "test", {}, "http://evil.test")
        with patch("expcore_updates.os.replace", side_effect=PermissionError):
            self.assertEqual(self.checker.check().status, "available")
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])
        self.checker.check()
        self.opener.open.assert_called_once()


if __name__ == "__main__":
    unittest.main()
