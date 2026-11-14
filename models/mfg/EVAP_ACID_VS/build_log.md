# Build log - EVAP_ACID_VS

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EVAP_ACID_VS.md`; sizing `docs-authority/sizing/EVAP_ACID_VS.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 400 x 400 x 1400 mm: inside the envelope with margin (envelope 400 x 400 x 1400 mm)
- 2026-11-14 rebuild through the current `vent_scrubber.py`: export STL closed and
  manifold, 318.3 x 318.3 x 1400.0 mm against size_mm 400 x 400 x 1400. The
  2026-11-01 build carried the off-gas outlet socket 80 mm above the stated height
  (misfit reported on the board, nothing resized); the socket now ends flush at the
  top cap face - the size_mm z claim is the column height (AQS-DUTY-061 section 2:
  bed 500 + sump, inlet and demister 900) and connection hardware stays inside the
  claim (A-core 2). The drawing set predates this rebuild and regenerates in a
  drawing round.
- Solid source: build export `models/mfg/EVAP_ACID_VS/export/evap_acid_vs.step`
- BOM `models/mfg/EVAP_ACID_VS/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EVAP_ACID_VS/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EVAP_ACID_VS/export/evap_acid_vs.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
