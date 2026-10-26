"""Verify rendered Xarray PR #11806 docs and Sphinx fragment references.

Run: python validate_links.py
Only reads public preview pages. Writes qa_result.json beside this script.
No external Python dependencies.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin
from urllib.request import Request, urlopen


PR_NUMBER = 11806
PR_HEAD = "d51b021f79918c50cde01b267dcceeaa07fc55cc"
ROOT = "https://xray--11806.org.readthedocs.build/en/11806/"
GUIDE = urljoin(ROOT, "internals/how-to-add-new-backend.html")
ENTRYPOINT = urljoin(ROOT, "generated/xarray.backends.BackendEntrypoint.html")
METHODS = ("open_datatree", "open_groups_as_dict")


class LinksAndIds(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "a" and attributes.get("href"):
            self.links.append(
                {"href": attributes["href"], "title": attributes.get("title") or ""}
            )


def fetch(url: str) -> tuple[dict[str, object], LinksAndIds]:
    request = Request(url, headers={"User-Agent": "NEXUS-OSS-QA/1.0"})
    with urlopen(request, timeout=20) as response:
        data = response.read()
        status = response.status
        final_url = response.url
    html = LinksAndIds()
    html.feed(data.decode("utf-8"))
    return {"url": url, "status": status, "final_url": final_url, "size": len(data)}, html


def main() -> int:
    results: dict[str, object] = {
        "pr": PR_NUMBER,
        "head_sha": PR_HEAD,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "pages": [],
    }
    checks: list[dict[str, object]] = results["checks"]  # type: ignore[assignment]
    pages: list[dict[str, object]] = results["pages"]  # type: ignore[assignment]

    def record(name: str, passed: bool, **details: object) -> None:
        checks.append({"name": name, "passed": bool(passed), **details})

    guide_info, guide_html = fetch(GUIDE)
    pages.append(guide_info)
    record("guide_http_200", guide_info["status"] == 200, url=GUIDE)
    record("guide_section_anchor", "rst-open-datatree" in guide_html.ids)

    for method in METHODS:
        suffix = "xarray.backends.BackendEntrypoint." + method
        desired = urljoin(ROOT, "generated/" + suffix + ".html") + "#" + suffix
        matches = [
            urljoin(GUIDE, a["href"])
            for a in guide_html.links
            if urljoin(GUIDE, a["href"]) == desired
        ]
        record(method + "_guide_link", len(matches) >= 1, target=desired, count=len(matches))
        target_url, fragment = urldefrag(desired)
        target_info, target_html = fetch(target_url)
        pages.append(target_info)
        record(method + "_http_200", target_info["status"] == 200, url=target_url)
        record(method + "_fragment_present", fragment in target_html.ids, fragment=fragment)

    entrypoint_info, entrypoint_html = fetch(ENTRYPOINT)
    pages.append(entrypoint_info)
    record("entrypoint_http_200", entrypoint_info["status"] == 200, url=ENTRYPOINT)
    required_backlink = GUIDE + "#rst-open-datatree"
    backlinks = [
        urljoin(ENTRYPOINT, a["href"])
        for a in entrypoint_html.links
        if urljoin(ENTRYPOINT, a["href"]) == required_backlink
    ]
    record(
        "entrypoint_docstring_backlink",
        len(backlinks) >= 1,
        target=required_backlink,
        count=len(backlinks),
    )

    results["passed"] = sum(1 for item in checks if item["passed"])
    results["failed"] = len(checks) - results["passed"]
    results["all_passed"] = results["failed"] == 0
    output = Path(__file__).with_name("qa_result.json")
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
