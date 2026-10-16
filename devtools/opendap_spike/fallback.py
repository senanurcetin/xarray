"""Exploratory OPeNDAP endpoint selection, not an upstream integration.

Each provider has an explicit DAP2/DAP4 path. Unexpected HTTP responses
remain failures rather than being converted to skipped tests.
"""

from __future__ import annotations

from socket import gaierror
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

DAP_ENDPOINTS = {
    "dap2": (
        ("https://test.opendap.org/opendap/hyrax/data/nc/", ".dds"),
        ("https://thredds-test.unidata.ucar.edu/thredds/dodsC/testdods/", ".dds"),
    ),
    "dap4": (
        ("https://test.opendap.org/opendap/hyrax/data/nc/", ".dmr"),
        ("https://thredds-test.unidata.ucar.edu/thredds/dap4/testdods/", ".dmr.xml"),
    ),
}


def choose_dataset_url(protocol: str, filename: str, *, opener=urlopen) -> str:
    """Probe metadata before returning a PyDAP-compatible URL.

    Only 502/503/504 or connection/timeout failures trigger the next
    server; 401/404, TLS certificate errors and other unexpected failures
    remain hard errors.
    """
    if protocol not in DAP_ENDPOINTS:
        raise ValueError(f"Unsupported DAP protocol: {protocol}")
    if not filename or filename in {".", ".."} or any(
        ch in filename for ch in "/\\"
    ) or ".." in filename:
        raise ValueError("filename must be a plain dataset filename")

    last_error: Exception | None = None
    for base_url, suffix in DAP_ENDPOINTS[protocol]:
        dataset_url = base_url + filename
        try:
            with opener(dataset_url + suffix, timeout=6) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"Unexpected metadata HTTP {response.status}: {dataset_url}"
                    )
            parsed = urlsplit(dataset_url)
            return f"{protocol}://{parsed.netloc}{parsed.path}"
        except HTTPError as exc:
            exc.close()
            if exc.code not in {502, 503, 504}:
                raise
            last_error = exc
        except URLError as exc:
            if not isinstance(exc.reason, (ConnectionError, TimeoutError, gaierror)):
                raise
            last_error = exc
        except TimeoutError as exc:
            last_error = exc
    raise ConnectionError(f"No reachable {protocol.upper()} metadata endpoint") from last_error
