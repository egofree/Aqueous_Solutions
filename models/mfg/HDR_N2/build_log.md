# Build log - HDR_N2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HDR_N2.md`; envelope per `models/mfg/HDR_N2/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HDR_N2/hdr_n2.py`

## Checks

- Build bbox 2000 x 60.3 x 60.3 mm against the 2000 x 60.3 x 60.3 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HDR_N2/export/hdr_n2.step`; export STL closed and manifold, 1 solid(s); `cad/stl/HDR_N2.stl` ; replaced from the build (ASCII, metres)
- Nozzles: all 14 rows of `docs-authority/nozzles/HDR_N2.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 9 rows (manifold spool + 8 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN32 OD 42.4 x wall 3.56 (Sch 40 table; the M1 class sheet carries the schedule at order), bore 35.3 mm inside the 17.2 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized
- Reservation adoption (2026-11-08): headers.py (AQS-DUTY-075) sizes the reservation cross-section to the largest issued branch hardware (60.3 mm, the EN-rounded OD series); the DN50 branch row N1 draws inside it at the manifold centreline, the build reads 2000 x 60.3 x 60.3 against the same reservation, no misfit carried
- Schedule datums clamped into the 60.3 mm cross-section: inlets 10 to 11.3 mm, the DN25 37 mm datums to 32.4 mm, the 160/600 mm placeholder datums down (holds, W12); N12 drawn DN15, bore not calculated (plan W4); N3/N4 carry services with no present edge and are drawn verbatim
- BOM `models/mfg/HDR_N2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HDR_N2/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HDR_N2/hdr_n2.py`
- `models/mfg/HDR_N2/draw_n2.py`
- `models/mfg/HDR_N2/bom.csv`
- `models/mfg/HDR_N2/fasteners.csv`
- `models/mfg/HDR_N2/line_list.csv`
- `models/mfg/HDR_N2/check.json`
- `models/mfg/HDR_N2/WORK_ORDER.md`
- `build export `models/mfg/HDR_N2/export/hdr_n2.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
