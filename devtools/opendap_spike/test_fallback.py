"""Deterministic offline tests for the exploratory endpoint selector."""

import unittest
from urllib.error import HTTPError, URLError

from fallback import choose_dataset_url


class Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class FallbackTests(unittest.TestCase):
    def test_primary_dap2(self):
        seen = []

        def opener(url, timeout):
            seen.append(url)
            return Response()

        url = choose_dataset_url("dap2", "coads_climatology.nc", opener=opener)
        self.assertTrue(url.startswith("dap2://test.opendap.org/"))
        self.assertTrue(seen[0].endswith(".dds"))

    def test_primary_dap4(self):
        seen = []
        url = choose_dataset_url(
            "dap4",
            "coads_climatology.nc",
            opener=lambda u, timeout: (seen.append(u), Response())[1],
        )
        self.assertTrue(url.startswith("dap4://test.opendap.org/"))
        self.assertTrue(seen[0].endswith(".dmr"))

    def test_dap2_connection_refusal_fallback(self):
        seen = []

        def opener(url, timeout):
            seen.append(url)
            if len(seen) == 1:
                raise URLError(ConnectionRefusedError("outage"))
            return Response()

        url = choose_dataset_url("dap2", "coads_climatology.nc", opener=opener)
        self.assertIn("thredds/dodsC/testdods", url)
        self.assertEqual(len(seen), 2)

    def test_dap4_503_fallback(self):
        seen = []

        def opener(url, timeout):
            seen.append(url)
            if len(seen) == 1:
                raise HTTPError(url, 503, "unavailable", {}, None)
            return Response()

        url = choose_dataset_url("dap4", "coads_climatology.nc", opener=opener)
        self.assertIn("thredds/dap4/testdods", url)
        self.assertTrue(seen[-1].endswith(".dmr.xml"))

    def test_404_remains_hard_error(self):
        def opener(url, timeout):
            raise HTTPError(url, 404, "not found", {}, None)

        with self.assertRaises(HTTPError):
            choose_dataset_url("dap4", "coads_climatology.nc", opener=opener)

    def test_tls_errors_are_not_silently_hidden(self):
        import ssl

        def opener(url, timeout):
            raise URLError(ssl.SSLCertVerificationError("bad certificate"))

        with self.assertRaises(URLError):
            choose_dataset_url("dap4", "coads_climatology.nc", opener=opener)

    def test_both_unavailable_raise(self):
        def opener(url, timeout):
            raise URLError(TimeoutError("outage"))

        with self.assertRaises(ConnectionError):
            choose_dataset_url("dap4", "coads_climatology.nc", opener=opener)

    def test_reject_invalid_filename_and_protocol(self):
        with self.assertRaises(ValueError):
            choose_dataset_url("unknown", "coads_climatology.nc")
        with self.assertRaises(ValueError):
            choose_dataset_url("dap2", "../etc/passwd")


if __name__ == "__main__":
    unittest.main()
