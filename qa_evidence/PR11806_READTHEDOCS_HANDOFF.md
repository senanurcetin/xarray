# Xarray #11806 — independent rendered-documentation QA

Checked on 27 October 2026 (2026-10-26 22:00:18 UTC).

- Upstream PR: https://github.com/pydata/xarray/pull/11806
- PR head reviewed: `d51b021f79918c50cde01b267dcceeaa07fc55cc`
- Preview: https://xray--11806.org.readthedocs.build/en/11806/internals/how-to-add-new-backend.html
- Reviewer concern: the generated Sphinx links for `BackendEntrypoint.open_datatree`
  and `BackendEntrypoint.open_groups_as_dict` previously failed to resolve.
- Independent QA branch: `qa/xarray-11806-rendered-links-20261027`
  (created from PR head, **no edits to the active PR branch**).

## Actual verification

A PowerShell `Invoke-WebRequest` probe and a separately executed dependency-free
Python link validator both inspected the **rendered Read the Docs HTML**.

The Python validator reported **10/10 checks passed, 0 failed**. Four pages
returned HTTP 200: the backend guide, the two individual generated method API
pages, and the parent `BackendEntrypoint` API page.

Verified:
- The guide contains a correct `href` for `open_datatree`; the target page
  exists and contains the requested `xarray.backends.BackendEntrypoint.open_datatree` ID.
- The guide contains a correct `href` for `open_groups_as_dict`; its target
  page exists and contains the requested ID.
- The guide contains the `rst-open-datatree` section anchor.
- The parent `BackendEntrypoint` generated API page links back to the
  guide's `#rst-open-datatree` section.

Proof and reproduction:
- `qa_evidence/validate_pr11806_docs_links.py` — Python 3.11 standard library only.
- `qa_evidence/pr11806_docs_links_result.json` — UTC timestamp, individual
  assertions, tested URLs, and response codes.
- Run in any network-enabled environment:
  `python qa_evidence/validate_pr11806_docs_links.py`.
  The script writes `qa_result.json` alongside itself, and exits nonzero on failure.
- Ruff lint and format checks passed after formatting the script.

## Handoff to Notebook 1

The reviewer's specific *rendered cross-reference* concern is now independently
checked and appears resolved on the preview deployed at the checked time.
Maintainer `headtr1ck` had already responded "Thanks!" on 26 October; avoid
an unnecessary follow-up message while awaiting further maintainer action.

The public preview is a moving build and might expire; rerun the script if the
PR head/build changes. These checks do **not** cover all documentation links,
or claim a full docs build / application test suite. The preview HTML was
inspected directly; no upstream code or PR metadata was modified.
