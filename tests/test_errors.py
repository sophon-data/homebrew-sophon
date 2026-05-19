import unittest

import conftest  # noqa: F401 — installs sys.path

from sophon_login.errors import HTTPError


class HTTPErrorParsingTests(unittest.TestCase):
    def test_error_code_from_detail_dict(self) -> None:
        err = HTTPError(status=400, body={"detail": {"error": "authorization_pending"}})
        self.assertEqual(err.error_code(), "authorization_pending")

    def test_error_code_from_top_level_key(self) -> None:
        err = HTTPError(status=400, body={"error": "slow_down"})
        self.assertEqual(err.error_code(), "slow_down")

    def test_none_when_unstructured(self) -> None:
        err = HTTPError(status=500, body={"foo": "bar"})
        self.assertIsNone(err.error_code())

    def test_none_body_safe(self) -> None:
        err = HTTPError(status=500, body=None)
        self.assertIsNone(err.error_code())


if __name__ == "__main__":
    unittest.main()
