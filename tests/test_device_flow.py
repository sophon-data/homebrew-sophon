import unittest
from unittest.mock import patch

import conftest  # noqa: F401

from sophon_login import device_flow, http
from sophon_login.errors import HTTPError, LoginDenied, LoginExpired


def _start_response() -> dict:
    return {
        "device_code": "dev-abc",
        "user_code": "WXYZ-1234",
        "verification_uri": "http://localhost:5173/device",
        "verification_uri_complete": "http://localhost:5173/device?user_code=WXYZ-1234",
        "expires_in": 600,
        "interval": 2,
    }


def _poll_success() -> dict:
    return {
        "access_token": "jwt.eyJ.signed",
        "token_type": "Bearer",
        "expires_in": 86400,
        "scope": "ingest:write",
    }


class StartDeviceFlowTests(unittest.TestCase):
    def test_posts_to_correct_endpoint(self) -> None:
        calls: list[tuple[str, dict]] = []

        def fake_post(url, body, timeout=10.0):
            calls.append((url, body))
            return _start_response()

        with patch.object(http, "post_json", fake_post):
            resp = device_flow.start_device_flow("http://api.example.com")

        self.assertEqual(calls[0][0], "http://api.example.com/api/auth/device/start")
        self.assertEqual(calls[0][1], {"client_name": "sophon-cli"})
        self.assertEqual(resp["user_code"], "WXYZ-1234")


class PollUntilApprovedTests(unittest.TestCase):
    def test_returns_token_on_first_success(self) -> None:
        def fake_post(url, body, timeout=10.0):
            return _poll_success()

        sleeps: list[float] = []
        with patch.object(http, "post_json", fake_post):
            result = device_flow.poll_until_approved(
                api_base_url="http://api",
                device_code="dev",
                interval=2,
                expires_in=60,
                sleep=sleeps.append,
                now=lambda: 0.0,
            )
        self.assertEqual(result["access_token"], "jwt.eyJ.signed")
        self.assertEqual(sleeps, [2])

    def test_authorization_pending_keeps_polling(self) -> None:
        responses: list = [
            HTTPError(status=400, body={"detail": {"error": "authorization_pending"}}),
            HTTPError(status=400, body={"detail": {"error": "authorization_pending"}}),
            _poll_success(),
        ]

        def fake_post(url, body, timeout=10.0):
            r = responses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        sleeps: list[float] = []
        with patch.object(http, "post_json", fake_post):
            result = device_flow.poll_until_approved(
                api_base_url="http://api",
                device_code="dev",
                interval=3,
                expires_in=60,
                sleep=sleeps.append,
                now=lambda: 0.0,
            )
        self.assertEqual(result["access_token"], "jwt.eyJ.signed")
        self.assertEqual(sleeps, [3, 3, 3])

    def test_slow_down_increases_interval(self) -> None:
        responses: list = [
            HTTPError(status=400, body={"detail": {"error": "authorization_pending"}}),
            HTTPError(status=400, body={"detail": {"error": "slow_down"}}),
            HTTPError(status=400, body={"detail": {"error": "authorization_pending"}}),
            _poll_success(),
        ]

        def fake_post(url, body, timeout=10.0):
            r = responses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        sleeps: list[float] = []
        with patch.object(http, "post_json", fake_post):
            device_flow.poll_until_approved(
                api_base_url="http://api",
                device_code="dev",
                interval=2,
                expires_in=60,
                sleep=sleeps.append,
                now=lambda: 0.0,
            )
        self.assertEqual(sleeps, [2, 2, 7, 7])

    def test_expired_token_raises_login_expired(self) -> None:
        def fake_post(url, body, timeout=10.0):
            raise HTTPError(status=400, body={"detail": {"error": "expired_token"}})

        with patch.object(http, "post_json", fake_post):
            with self.assertRaises(LoginExpired):
                device_flow.poll_until_approved(
                    api_base_url="http://api",
                    device_code="dev",
                    interval=1,
                    expires_in=60,
                    sleep=lambda _s: None,
                    now=lambda: 0.0,
                )

    def test_access_denied_raises_login_denied(self) -> None:
        def fake_post(url, body, timeout=10.0):
            raise HTTPError(status=400, body={"detail": {"error": "access_denied"}})

        with patch.object(http, "post_json", fake_post):
            with self.assertRaises(LoginDenied):
                device_flow.poll_until_approved(
                    api_base_url="http://api",
                    device_code="dev",
                    interval=1,
                    expires_in=60,
                    sleep=lambda _s: None,
                    now=lambda: 0.0,
                )

    def test_local_deadline_raises_when_clock_passes_expiry(self) -> None:
        def fake_post(url, body, timeout=10.0):
            raise HTTPError(status=400, body={"detail": {"error": "authorization_pending"}})

        clock = [0.0]
        with patch.object(http, "post_json", fake_post):
            with self.assertRaises(LoginExpired):
                device_flow.poll_until_approved(
                    api_base_url="http://api",
                    device_code="dev",
                    interval=5,
                    expires_in=10,
                    sleep=lambda s: clock.__setitem__(0, clock[0] + s),
                    now=lambda: clock[0],
                )

    def test_unknown_error_bubbles_up(self) -> None:
        def fake_post(url, body, timeout=10.0):
            raise HTTPError(status=500, body={"detail": {"error": "server_meltdown"}})

        with patch.object(http, "post_json", fake_post):
            with self.assertRaises(HTTPError):
                device_flow.poll_until_approved(
                    api_base_url="http://api",
                    device_code="dev",
                    interval=1,
                    expires_in=60,
                    sleep=lambda _s: None,
                    now=lambda: 0.0,
                )


if __name__ == "__main__":
    unittest.main()
