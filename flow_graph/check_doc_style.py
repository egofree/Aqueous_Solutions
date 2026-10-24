"""Light documentation style check (docs-authority/DOC_STYLE.md, AQS-DOC-002).

Two rules, both driven by data in docs-authority/style_terms.json:

1. Every abbreviation written in capitals in a published page is defined in
   docs-authority/GLOSSARY.md (DOC_STYLE section 7). Identifiers from the plant
   graph (and unit folders under models/units/ and duty sheets), tokens containing a digit (formulas, stream ids, standard numbers),
   text in code spans or code blocks, link targets, revision and annex letters
   (Rev BH, Annex AA) and the words listed under
   "not_abbreviations" are not abbreviations.
2. No published page uses a term from the "banned" list: working jargon from
   the tools and sessions used to produce the design (DOC_STYLE section 4).

A published page is a tracked Markdown file outside the agent-only paths. Pages
listed under "exempt" are skipped for the reason given there. Pages listed under
"pending" have not yet been brought to the guide; they are reported but do not
fail, and an entry that has become clean must be removed (the test enforces it),
so the list only shrinks.

Usage: python3 -m flow_graph.check_doc_style [--all] [--shrink]
  --all     report findings in pending pages too
  --shrink  remove pending entries that no longer have findings
"""
from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs-authority" / "style_terms.json"
GLOSSARY = ROOT / "docs-authority" / "GLOSSARY.md"
GRAPH = ROOT / "flow_graph" / "plant_flow_graph.json"

_FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
_CODE = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^)]*\)|<https?://[^>]*>|https?://\S+")
_LETTER_LABEL = re.compile(r"\b(?:Rev|Revision|Revs|Annex|Appendix|Supplement|Class|Grade|Type|Zone|Level)\.?[ -]+[A-Z]{1,3}\b")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_ABBR = re.compile(r"(?<![\w/.\-])([A-Z][A-Z&]*[A-Z])(?:s|'s)?(?![\w\-/])")
_ROMAN = re.compile(r"^(?=[IVXLC]+$)C{0,3}(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")


def data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _tracked(pattern: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", pattern], cwd=ROOT, capture_output=True, text=True, check=True)
    return [p for p in out.stdout.splitlines() if p]


def _match(path: str, globs) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in globs)


def published_pages(d: dict | None = None) -> list[str]:
    d = d or data()
    return [p for p in _tracked("*.md") if not _match(p, d["agent_only"])]


@lru_cache(maxsize=1)
def glossary_abbreviations() -> frozenset[str]:
    text = GLOSSARY.read_text(encoding="utf-8")
    found: set[str] = set()
    for term, definition in re.findall(r"^\{(.*?)\s--\s(.*)", text, re.M):
        found.update(_ABBR.findall(term))
        found.update(re.findall(r"\(([A-Z][A-Z&]*[A-Z])s?\)", definition))
    return frozenset(found)


@lru_cache(maxsize=1)
def graph_identifiers() -> frozenset[str]:
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for n in g.get("nodes", []):
        ids.update(filter(None, (n.get("unit_id"), n.get("sector_id"))))
    for e in g.get("edges", []):
        ids.update(filter(None, (e.get("stream_id"), e.get("from_sector_id"), e.get("to_sector_id"))))
    # Units and building-block families that have a model folder or a duty sheet.
    for path in _tracked("models/units/*") + _tracked("docs-authority/duties/*.md"):
        parts = Path(path).parts
        ids.add(parts[2] if parts[0] == "models" else Path(path).stem)
    return frozenset(ids)


def prose(text: str) -> str:
    """The text a reader reads as prose: code, comments and link targets removed."""
    for rx in (_FENCE, _COMMENT, _CODE, _LINK_TARGET, _LETTER_LABEL):
        text = rx.sub(" ", text)
    return text


@lru_cache(maxsize=1)
def _glossary_words() -> frozenset[str]:
    return frozenset(re.findall(r"\b[a-z]+\b", GLOSSARY.read_text(encoding="utf-8")))


def undefined_abbreviations(text: str, d: dict) -> list[str]:
    """Capitalised tokens that are neither defined nor ordinary words.

    A token is taken as an ordinary word set in capitals (a drawing label such as
    ROOF TANK) when it has six or more letters and is not listed under
    "long_abbreviations", or when its lowercase form appears as a word in the
    same page or in the glossary."""
    body = prose(text)
    known = glossary_abbreviations() | graph_identifiers() | set(d["not_abbreviations"])
    words = set(re.findall(r"\b[a-z]+\b", body)) | _glossary_words()
    long_abbr = set(d["long_abbreviations"])
    out = []
    for tok in _ABBR.findall(body):
        if tok in known or _ROMAN.match(tok) or (tok.endswith("S") and tok[:-1] in known):
            continue
        if tok.lower() in words or (len(tok) >= 6 and tok not in long_abbr):
            continue
        out.append(tok)
    return sorted(set(out))


def banned_terms(text: str, d: dict) -> list[str]:
    body = prose(text)
    return [b["term"] for b in d["banned"] if re.search(b["pattern"], body, re.I)]


def findings(path: str, d: dict) -> list[tuple[str, str]]:
    text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
    return ([("undefined abbreviation", t) for t in undefined_abbreviations(text, d)]
            + [("banned term", t) for t in banned_terms(text, d)])


def scan(d: dict | None = None, include_pending: bool = False) -> dict[str, list[tuple[str, str]]]:
    d = d or data()
    exempt = {e["path"] for e in d["exempt"]}
    pending = set(d["pending"])
    out = {}
    for p in published_pages(d):
        if p in exempt or (p in pending and not include_pending):
            continue
        f = findings(p, d)
        if f:
            out[p] = f
    return out


def stale_pending(d: dict | None = None) -> list[str]:
    d = d or data()
    pages = set(published_pages(d))
    return [p for p in d["pending"] if p not in pages or not findings(p, d)]


def main(argv: list[str]) -> int:
    d = data()
    if "--shrink" in argv:
        stale = set(stale_pending(d))
        d["pending"] = [p for p in d["pending"] if p not in stale]
        DATA.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"removed {len(stale)} pending entries")
        return 0
    res = scan(d, include_pending="--all" in argv)
    for p, f in sorted(res.items()):
        for kind, t in f:
            print(f"{p} | {kind} | {t}")
    stale = stale_pending(d)
    for p in stale:
        print(f"{p} | pending entry is clean or gone | run --shrink")
    print(f"{sum(len(f) for f in res.values())} findings")
    return 1 if (res and "--all" not in argv) or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
