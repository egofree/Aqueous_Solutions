# Tier 5 headers to M3 — 2026-11-02

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7;
per-unit recipe pattern in `models/mfg/HX8/WORK_ORDER.md` and
`models/mfg/EW_1/WORK_ORDER.md`. Graph Rev AD. One commit per unit (plan rule 4);
this note gains a section per accepted unit. Units: HDR_CO2, HDR_H2, HDR_N2,
HDR_O2, HDR_UPW, NCG_HEADER, Q4_BUS (tier 5, class `header`, route F-PIPE,
acceptance A-core + A-PIPE: line list with tag, from, to, DN or "bore not
calculated", rating; spool drawing; no new edge).

## Lane tooling fixes — commit 1

- `docs-authority/_drawings.py` stamped every fabrication-drawing title with a
  hard-coded graph revision letter that had drifted (the register said a revision
  the graph had left). The generator now reads the live `revision` field of
  `flow_graph/plant_flow_graph.json`, and the title says "graph Rev <letter>" so
  the revision letter reads as a revision label on the page. Running the
  generator re-stamped the register rows; the SVG title blocks were already
  truncated above the revision letter and did not change.
- `models/mfg/lib/sheets.py` wrote a fixed date into every acceptance build log.
  It now writes the build date.

## HDR_CO2 (CO2 header, HAB, tier 5) — commit 2

Filled when accepted.
