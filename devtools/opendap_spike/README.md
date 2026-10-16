# OPeNDAP provider fallback spike (issue #11718)

This is a **nonproduction exploratory spike**, not a replacement for Xarray's
backend tests and not a fix for PR #11717 yet.

- Explicit paths for Hyrax and Unidata TDS, separately for DAP2 and DAP4
- Probe metadata before choosing a PyDAP `dap2://` / `dap4://` URL
- Retry another server only on connection failures, timeouts, HTTP 502/503/504
- Propagate hard errors such as 401, 404 and TLS certificate failures
- Offline unit tests with deterministic fake HTTP openers

Run offline: `python -m unittest discover -s devtools/opendap_spike -p 'test_*.py' -v`.

Still needed: verify HDF5 DataTree fixture URLs and authentication, and test
request-cache behavior with pinned PyDAP/Xarray versions. Existing PyDAP 3.5.9
and Xarray 2026.9.0 probes observed DAP2 metadata cache count 5 but
DAP4 count 1 on a TDS COADS dataset; those numbers are not guaranteed to
match historical test assumptions. **Do not merge this as a CI fallback
until maintainers agree on fixture mappings and protocol coverage.**
