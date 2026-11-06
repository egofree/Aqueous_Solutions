# Build log - CRYO_ASU

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_ASU.md`; bed design from the node design block).
Run note (2026-11-05): rebuild against the Rev AD graph node. The builder now reads the graph node through `models/mfg/lib/graph_node.py`; the N17 power-terminal cable row (cable schedule X-ELS-06) is carried verbatim, not drawn; bed sizing follows the node design block (bed_D_mm 421.9, bed_L_mm 1265.8, sorbent 115.04 kg/bed), which grows the beds, shifts the bed axes one pitch and grows the sorbent charge; the M0 registry-box misfit hold is unchanged. Supersedes the 2026-11-01 run at Rev AC sizing.

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CRYO_ASU/cryo_asu.py`

## Checks

- Build bbox 2460.0 x 592.1 x 2000.1 mm against the node size_mm [300, 300, 2000]: the node box is the M0 study registry envelope (params size_note) and the beds at their design diameter cannot fit it - misfit reported on the tracker board, nothing resized (AQS-PLAN-006 rule 3)
- Solid source: build export `models/mfg/CRYO_ASU/export/cryo_asu.step`; export STL closed and manifold; `cad/stl/CRYO_ASU.stl` replaced from the build (ASCII, metres)
- Nozzles: all 17 schedule rows of `docs-authority/nozzles/CRYO_ASU.csv` accounted for - 16 drawn at face, height, bore and tag, and N17 the power terminal (cable schedule X-ELS-06, AQS-ELEC-010) carried verbatim, not drawn (electrical, not piped); vent to the 2000 datum; frame-level z 160 rows through the plinth
- A-COL: the 13X charges are solids between support grids (311.9 kg drawn against 345.1 kg booked); distributor and demister are not named on the node (hold, WORK_ORDER W12)
- BOM `models/mfg/CRYO_ASU/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_ASU/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CRYO_ASU/cryo_asu.py`
- `models/mfg/CRYO_ASU/draw_cryo_asu.py`
- `build export `models/mfg/CRYO_ASU/export/cryo_asu.step``
- `models/mfg/CRYO_ASU/bom.csv`
- `models/mfg/CRYO_ASU/fasteners.csv`
- `models/mfg/CRYO_ASU/check.json`
- `models/mfg/CRYO_ASU/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL with the reported envelope misfit; the machine-design detail (TSA valve row, interconnect piping) follows the unit WORK_ORDER.
