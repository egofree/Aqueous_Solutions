"""Documentation style check (docs-authority/DOC_STYLE.md, flow_graph/check_doc_style.py)."""
import re

from flow_graph import check_doc_style as c


def test_no_style_findings_outside_pending():
    res = c.scan()
    assert res == {}, {p: f[:5] for p, f in list(res.items())[:10]}


def test_pending_list_only_shrinks():
    stale = c.stale_pending()
    assert stale == [], f"remove clean pages with python3 -m flow_graph.check_doc_style --shrink: {stale[:10]}"


def test_style_data_valid():
    d = c.data()
    for b in d["banned"]:
        re.compile(b["pattern"])
        assert b["why"] and b["instead"], b["term"]
    for e in d["exempt"]:
        assert e["reason"], e["path"]
    assert d["pending"] == sorted(set(d["pending"]))
    pages = set(c.published_pages(d))
    assert all(e["path"] in pages for e in d["exempt"])


def test_checker_catches_examples():
    d = c.data()
    assert c.banned_terms("The change landed in wave 3.", d)
    assert "QZX" in c.undefined_abbreviations("The QZX valve.", d)
    assert c.undefined_abbreviations("The `QZX` valve at Rev BH uses PTFE.", d) == []
