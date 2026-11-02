# Build log - HDR_H2

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HDR_H2.md`; envelope per `models/mfg/HDR_H2/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HDR_H2/hdr_h2.py`

## Checks

- Build bbox 2000 x 50 x 60.3 mm against the 2000 x 50 x 50 mm envelope: OVER - misfit reported (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HDR_H2/export/hdr_h2.step`; export STL closed and manifold, 1 solid(s); `cad/stl/HDR_H2.stl` ; kept as the envelope registry at the node size (the build carries the reported DN50 cross-section misfit; build mesh in export/) (ASCII, metres)
- Nozzles: all 16 rows of `docs-authority/nozzles/HDR_H2.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 15 rows (manifold spool + 14 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table; P1 class sheet carries Sch 80 at order), bore 26.9 mm inside the 6.6 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized
- Misfit reported (plan rule 3): the 3 DN50 branch rows (OD 60.3) are larger than the 50 mm cross-section; drawn at the manifold centreline, the mesh reads z 60.3 against the 50 mm envelope; nothing resized, the section 7 row carries the misfit
- Schedule datums clamped into the 50 mm cross-section: inlets 10 to 11.3 mm, the 160 mm placeholder datums down (holds, W12); N8 drawn DN15, bore not calculated (plan W4)
- BOM `models/mfg/HDR_H2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HDR_H2/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HDR_H2/hdr_h2.py`
- `models/mfg/HDR_H2/draw_h2.py`
- `models/mfg/HDR_H2/bom.csv`
- `models/mfg/HDR_H2/fasteners.csv`
- `models/mfg/HDR_H2/line_list.csv`
- `models/mfg/HDR_H2/check.json`
- `models/mfg/HDR_H2/WORK_ORDER.md`
- `build export `models/mfg/HDR_H2/export/hdr_h2.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
