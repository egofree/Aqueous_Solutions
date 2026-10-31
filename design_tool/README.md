# Aqueous design tool

The design tool lets you explore changes to the plant without editing the design itself. It reads the plant flow graph, lets you make a working copy, switch sectors or units off, change parameters, solve the copy and export the result as a pack of files.

Architecture: `docs-authority/DESIGN_TOOL_ARCHITECTURE.md` (AQS-UI-001). Licence: CERN-OHL-S-2.0.

## 1. What it does

- **Starts from a site.** `POST /api/v1/sandbox/from-site` applies a locale scaling profile (the same engine the regeneration pipeline uses): the eliminations, replacements and sizing of `flow_graph/param/sites/<site_id>.json` become the sandbox's starting state. `POST /api/v1/sandbox/{id}/solve-pipeline` then runs the real balance reconciliation on the fold and reports the true residuals - a closed subset is never called equivalent to the baseline.
- **Reads the design.** The minimum viable system (MVS) model is built from `flow_graph/plant_flow_graph.json` every time it is requested. The graph is the only source; `aqs_design_tool/data/candidate_mvs.json` is a generated projection of it, written by the regeneration pipeline, and must not be edited by hand.
- **Works on copies.** A sandbox is a working copy of the model with your overrides (sectors or units switched off, a scale factor, parameter changes). The design itself is never changed through the tool.
- **Solves a copy.** The solver reports residuals, gaps, streams left unclosed, surplus and the electrical match. It does not claim that a loop closes when it does not: a result can be `partial`.
- **Reports what a smaller or reduced plant loses.** When a sector or unit is off, or the scale factor is below a limit, the solver lists the unreclaimed streams defined in `docs-authority/SCALE_DOWN_UNRECLAIMED.md` (AQS-SCALE-UR-001).
- **Exports packs.** An export writes a new folder under `exports/` (ignored by Git) with the modules you ask for: parameters, streams, gaps, compliance flags, process flow diagram (PFD), single-line diagram (SLD), bill of materials (BOM) and a 3D folder.

## 2. Install and run

Python 3.11 or later. From the repository root:

```bash
cd design_tool
pip install -r requirements.txt
uvicorn aqs_design_tool.api.app:app --host 127.0.0.1 --port 8000   # or: python -m aqs_design_tool
```

The interactive API documentation is at <http://127.0.0.1:8000/docs>.

To run the web interface as well, start the API as above and, in a second terminal:

```bash
cd design_tool/web
npm install
npm run dev      # serves http://127.0.0.1:5173 and forwards /api to port 8000
npm run build    # production build
```

The API accepts browser requests from `http://127.0.0.1:5173` and `http://localhost:5173` only.

## 3. Try it

With the API running:

```bash
curl -s http://127.0.0.1:8000/health
SID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/sandbox -H 'Content-Type: application/json' \
      -d '{"label":"trial"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sandbox_id'])")
curl -s -X PATCH "http://127.0.0.1:8000/api/v1/sandbox/$SID" -H 'Content-Type: application/json' \
      -d '{"overrides":{"sector_enabled":{"FAB":false}}}'
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/solve" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/export" -H 'Content-Type: application/json' \
      -d '{"export_modules":["params","streams","gaps","compliance_flags"]}'
```

This switches off FAB (fabrication), solves the copy and exports a pack.

## 4. Interface

All paths are under `/api/v1` except `/health`.

Table 4.1. Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/health` | Service status |
| GET | `/mvs` | The MVS model built from the plant graph (read-only) |
| GET | `/mvs/from-graph` | The same as `/mvs` |
| GET | `/mvs/projection-check` | Whether the committed projection matches the graph; status 409 if it does not |
| GET | `/flow-graph` | Graph metadata |
| GET | `/flow-graph/topology` | Units and streams |
| GET | `/flow-graph/views/{name}` | One diagram layer view |
| POST | `/sandbox` | A new sandbox |
| GET, PATCH | `/sandbox/{id}` | Read or change a sandbox's overrides |
| POST | `/sandbox/{id}/solve` | Residuals, gaps, surplus and electrical match |
| GET | `/sandbox/{id}/flags` | Gap, unclosed-stream, bottleneck and code flags |
| POST | `/sandbox/{id}/export` | A pack written under `exports/` |
| GET | `/sector-definitions` | The sector list (AQS-SEC-001) |
| GET | `/system-tree` | The system tree with totals |
| GET | `/params` | The design drivers and their checksum |
| GET | `/regen-status` | Whether generated files are current, and the last regeneration receipt |

The request and response models are in `aqs_design_tool/models.py`; the JSON Schema generated from them is `aqs_design_tool/schema/mvs.schema.json`.

## 5. Layout

```
design_tool/
  requirements.txt
  web/                        browser interface (React, Vite, TypeScript)
  exports/                    export packs (ignored by Git)
  aqs_design_tool/
    flow_graph_adapter.py     plant graph to MVS model; the only load path
    models.py                 data models
    sector_definitions.py     sector ids and retired ids
    solver/                   solver and the scale-down map
    api/app.py                HTTP interface
    api/store.py              sandbox storage
    export/pack.py            pack writer
    data/                     generated data (candidate_mvs.json, scale_down.json)
    schema/mvs.schema.json    JSON Schema
```

## 6. Limitations

- Mass and energy balances in the solver are simplified. Residuals are marked incomplete where the graph has no rate.
- Streams without a rate in the graph are reported as `rate_incomplete_study`. Rates that are filled are study values with a cited basis, not closed balances.
- Surplus is compared with the study thresholds of `docs-authority/SURPLUS_PASS_THRESHOLDS.md`. Passing them does not freeze the MVS.
- The candidate MVS is a projection of the current graph, not a frozen design.
- Export packs are written locally only.

## 7. Checks

The design tool is covered by the repository checks in `CONTRIBUTING.md`. `flow_graph/test_authority_contract.py` checks that the projection matches the graph, and `python3 flow_graph/check_authority_contract.py` runs the same contract from the command line.

## 8. Licence header

New source files start with:

```python
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
```
