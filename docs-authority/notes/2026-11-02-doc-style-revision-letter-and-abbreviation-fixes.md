# 2026-11-02 Documentation style findings cleared (revision-letter emission, glossary entries, banned phrase)

`scripts/check_all.sh` failed at graph Rev AD on five documentation style findings
(`flow_graph/test_doc_style.py::test_no_style_findings_outside_pending` plus
`python3 -m flow_graph.check_doc_style`). All five are cleared in this change; no
graph, driver, or transfer-function value changed.

## Findings, causes, fixes

1. `docs-authority/OPEN_QUESTIONS.md` - banned term "per the owner" in the Q-037
   ruling. Cause: the ruling recorded that the owner asked, not why. Fix: the
   ruling now states the decision ("the return-to-lake service is the intended
   basis"); the reason (degas plus in-lake dilution) was already in the row.
   Page bumped to Rev E; no decision changed.
2. `docs-authority/PARAMETRIC_MODEL.md` - undefined abbreviation KFST. Cause: the
   climate-station identifier (Fort Stockton-Pecos County Airport, cited as
   NWS_FORT_STOCKTON in `flow_graph/param/refs.py`) had no glossary entry. Fix:
   entry added to `docs-authority/GLOSSARY.md` (DOC_STYLE section 7: add a
   missing abbreviation in the same change). The use site needed no edit.
3. `docs-authority/SITE_BASIS_LAKE_BOEHMER.md` - undefined abbreviation LB.
   Cause: the lake_boehmer site code (`flow_graph/param/sites/lake_boehmer.json`,
   `site_code: LB`) had no glossary entry; the bare token is not a graph
   identifier, so the checker counts it. Fix: entry added to the glossary; the
   page needed no edit.
4. `docs-authority/DERIVED_REVISIONS.md` and `docs-authority/MFG_MODEL_PLAN.md` -
   undefined abbreviation AD. Cause: both pages are generated, and their
   generators emit the graph revision in lowercase prose ("revision AD"). The
   style check reads a capitalised two-letter token in prose as an abbreviation
   unless it follows the capitalised revision label (Rev, Revision). The token
   itself is legitimate: the graph revision scheme runs A to Z then AA, AB, ...
   (glossary, Rev (graph) entry), and the graph is at Rev AD. At Rev AC the
   finding was masked because "AC" happens to be glossary-defined (alternating
   current). Fix at the source, then regeneration (no hand edit to generated
   output):
   - `docs-authority/_rev_stamp.py` emits "Revision AD" in the DERIVED_REVISIONS
     identity line; `python3 docs-authority/_rev_stamp.py` regenerated the page.
   - `models/mfg/tracker.py` emits "Revision AD" and "Revision O" in the
     MFG_MODEL_PLAN section 7 provenance line; `python3 models/mfg/tracker.py`
     regenerated the section (params.json outputs byte-identical).
5. Working-tree fallout folded in: `docs-authority/DERIVED_REVISIONS.md` (graph
   commit stamp moved to f0160a6 by regeneration) and `docs-authority/STANDARDS_LIST.md`
   (regenerated with `python3 docs-authority/_standards_list.py`; now carries the
   Lake Boehmer citations of IBC 2027 Table 1806.2 and ASCE/SEI 7-22).

## Related housekeeping

- `docs-authority/GLOSSARY.md` bumped to Rev D. The Rev (graph) entry no longer
  states the current revision letter in hand-written text; it names the
  `revision` field of `flow_graph/plant_flow_graph.json`, which the regeneration
  pipeline keeps true (parametric-documentation rule). The previous text said
  "Rev AC at the time of writing", stale since the Rev AD bump.

## Verification

- `python3 -m flow_graph.check_doc_style`: 0 findings.
- `bash scripts/check_all.sh`: tests, staleness, authority contract, citations,
  doc-style all pass.
