# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Every document number cited in a tracked Markdown page is registered.

A number counts as registered when it appears in the document register
(docs-authority/DOC_REGISTER.md, which carries former numbers as aliases) or in
the drawing register (docs-authority/DRAWING_REGISTER.md). Numbers that were
already unregistered on 2026-10-29 are listed in
docs-authority/unregistered_doc_numbers.json and are allowed until they are
fixed; the list may only shrink. Change records under docs-authority/notes/
and the generated revision register are not checked.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs-authority" / "unregistered_doc_numbers.json"
NUM = re.compile(r"\bAQS-[A-Z][A-Za-z]*(?:-[A-Z0-9][A-Za-z0-9]*)*-\d{3}\b")
SKIP = ("docs-authority/notes/", "docs-authority/DERIVED_REVISIONS.md",
        "docs-authority/DOC_REGISTER.md", "docs-authority/DRAWING_REGISTER.md")


def unregistered() -> dict[str, list[str]]:
    known = (ROOT / "docs-authority/DOC_REGISTER.md").read_text(encoding="utf-8") + \
        (ROOT / "docs-authority/DRAWING_REGISTER.md").read_text(encoding="utf-8")
    files = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    out: dict[str, set[str]] = {}
    for f in files:
        if f.startswith(SKIP):
            continue
        text = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
        for m in set(NUM.findall(text)):
            if not re.search(re.escape(m) + r"\b", known):
                out.setdefault(m, set()).add(f)
    return {k: sorted(v) for k, v in sorted(out.items())}


def test_no_new_unregistered_numbers():
    allowed = set(json.loads(BASELINE.read_text(encoding="utf-8"))["numbers"])
    found = unregistered()
    new = sorted(set(found) - allowed)
    assert not new, f"unregistered document numbers cited: {[(k, found[k]) for k in new]}"


def test_baseline_only_shrinks():
    allowed = set(json.loads(BASELINE.read_text(encoding="utf-8"))["numbers"])
    fixed = sorted(allowed - set(unregistered()))
    assert not fixed, f"no longer cited or now registered; remove from {BASELINE.name}: {fixed}"
