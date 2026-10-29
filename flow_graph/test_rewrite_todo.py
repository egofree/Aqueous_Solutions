# SPDX-License-Identifier: CERN-OHL-S-2.0
"""The rewrite tracker (AQS-DOC-003) agrees with the pending list in style_terms.json.

A page on the pending list is listed in section 3 (in progress) or section 4
(pending) of docs-authority/REWRITE_TODO.md, and nowhere else in those
sections. A page in the done table of section 2 is not on the pending list.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODO = ROOT / "docs-authority" / "REWRITE_TODO.md"
TERMS = ROOT / "docs-authority" / "style_terms.json"


def _section(text: str, start: str, end: str) -> str:
    return text[text.index(start):text.index(end)]


def _pages(block: str) -> list[str]:
    return re.findall(r"^\| `([^`]+)` \|", block, flags=re.M)


def test_tracker_matches_pending_list():
    text = TODO.read_text(encoding="utf-8")
    pending = set(json.loads(TERMS.read_text(encoding="utf-8"))["pending"])
    done = _pages(_section(text, "## 2. Done", "## 3. In progress"))
    open_rows = _pages(_section(text, "## 3. In progress", "## 5. Removed"))
    assert len(open_rows) == len(set(open_rows)), "a page is listed twice in sections 3 and 4"
    assert set(open_rows) == pending, (
        f"on the pending list but not in sections 3 or 4: {sorted(pending - set(open_rows))}; "
        f"in sections 3 or 4 but not pending: {sorted(set(open_rows) - pending)}")
    assert not set(done) & pending, f"listed as done but still pending: {sorted(set(done) & pending)}"
