# Aqueous design tool — P0 + P1 + B′ graph-layer UI

Document: implements **AQS-UI-001** Rev D phases **P0**, **P1**, and **B′**  
Licence: **CERN-OHL-S-2.0**  
Path (this repo): `design_tool/`

## WP-Ap1 — graph sole authority (unify_then_reshape)

| Item | Authority | Notes |
|---|---|---|
| Topology + rates | `../flow_graph/plant_flow_graph.json` `nodes`/`edges` | Placeholders keep `rate: null` |
| Sector enables | graph `mvs.sectors[]` | includes `required_for_mvs_closure` |
| Crew / `SITE_LAT` | graph `mvs.site` (`crew`, `site_lat_deg`) | `site_lat_deg` may be null |
| Surplus / self-copy flags | graph `mvs.mvs_criteria` | `loops_closed` stays false while incomplete |
| MVS `schema_version` | graph `mvs.schema_version` (`aqs-mvs-0.3`) | projected into candidate |
| Unit kw / params | graph `nodes[]` (`continuous_kw`, `modules`, `params`, `enabled`) | |
| Sandbox edits | `.sandbox_store/` only | never rewrite graph or projection silently |

**Single write path:** edit the plant flow graph, then regenerate projection:

```bash
cd ../flow_graph
python3 build_seed.py                 # optional topology rebuild (keeps mvs)
python3 export_candidate_mvs.py       # → aqs_design_tool/data/candidate_mvs.json
```

`candidate_mvs.json` is a **generated projection** for legacy consumers — **not**
a competing master. FastAPI `GET /api/v1/mvs` and sandbox create/solve load from
the graph via `flow_graph_adapter.mvs_from_graph()`. Never `mvs_equivalent=true`
while incomplete. `DOCK_EXPORT_TBD` stays TBD.

Pointer: `../flow_graph/README.md`.

## WP-Ap2 — contract tests + projection drift

```bash
cd ../flow_graph
python3 check_authority_contract.py
python3 -m pytest test_authority_contract.py -q
```

API (graph sole load; drift visible):

| Method | Path | Role |
|---|---|---|
| GET | `/health` | includes `projection_contract_ok` |
| GET | `/api/v1/mvs/projection-check` | **409** if on-disk `candidate_mvs` drifts |
| GET | `/api/v1/mvs` | always from graph |
| POST | `/api/v1/sandbox` + `/solve` | sandbox overlays graph base |

Smoke (API up on :8000):

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
curl -s http://127.0.0.1:8000/api/v1/flow-graph | python3 -m json.tool
curl -s http://127.0.0.1:8000/api/v1/mvs/projection-check | python3 -m json.tool
curl -s http://127.0.0.1:8000/api/v1/mvs | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['revision'], len(d['units']), len(d['streams']))"
SID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/sandbox -H 'Content-Type: application/json' -d '{"label":"ap2-smoke"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sandbox_id'])")
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/solve" -H 'Content-Type: application/json' -d '{}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status'), d.get('sandbox_id'))"
```

## WP-Ap3 — derived STREAM / MASS

```bash
cd ../flow_graph
python3 export_authority_md.py
python3 render_layer_views.py
```

See `../flow_graph/derived/SYNC_POINTER.md`. CAD `STREAM_REGISTER.md` /
`MASS_FLOW.md` remain sync targets (hybrid).

## Phase B′ — graph-layer UI (WP-Bp1…Bp4) — **done** 2026-10-01 CT

| WP | Deliverable | Evidence |
|---|---|---|
| **WP-Bp1** | React/SVG rebound to graph API | App loads `/flow-graph`, `/topology`; sandbox from graph MVS |
| **WP-Bp2** | Layer viewer | UI filters PFD/MFD/EFD-elec/thermal/ess; placeholders dashed; rates stay authority-sourced |
| **WP-Bp3** | Editor affordances | Sector toggles, cycles, gaps, crew/`SITE_LAT` on graph-backed sandbox |
| **WP-Bp4** | Export from graph | Pack includes `flow_graph_snapshot.json` + projection `mvs_snapshot.json`; MVS gold untouched |

### Web run path

```bash
# Terminal 1 — API
cd design_tool
uvicorn aqs_design_tool.api.app:app --host 127.0.0.1 --port 8000

# Terminal 2 — UI
cd web && npm install && npm run dev   # http://127.0.0.1:5173
npm run build                          # production build check
```

### B′ API smoke

```bash
curl -s http://127.0.0.1:8000/api/v1/flow-graph | python3 -m json.tool
for v in pfd mfd efd-elec efd-thermal efd-ess; do
  curl -s "http://127.0.0.1:8000/api/v1/flow-graph/views/$v" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d['view_mode'], d['node_count'], d['edge_count'])"
done
SID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/sandbox -H 'Content-Type: application/json' \
  -d '{"label":"bp-smoke"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sandbox_id'])")
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/export" -H 'Content-Type: application/json' \
  -d '{"export_modules":["params","streams","gaps","compliance_flags"]}' | python3 -c \
  "import sys,json; d=json.load(sys.stdin); assert 'flow_graph_snapshot.json' in d['files']; print('OK', d['pack_dir'])"
```

**B' exit:** Yes.

## WP-C1 — Export packs from graph (done 2026-10-01 CT)

Modular export modules emit **from the graph** when requested. Unused modules stay off.
Matplotlib is an **optional** exporter only (copy bridged hub PNGs; not authority).
MVS gold / `plant_flow_graph.json` are never overwritten. **WP-C2 GitHub publish not started**
(blocked pending publish authorize).

| Module key | Artefacts | Source |
|---|---|---|
| (always) | `flow_graph_snapshot.json`, `mvs_snapshot.json`, `design.json`, `gaps.md`, `README.md` | graph + sandbox |
| `params` | `params.json` | sandbox overlay |
| `streams` | `streams.csv` | sandbox streams (graph-backed) |
| `compliance_flags` | `compliance_flags.md` | last solve |
| `pfd` | `pfd/{pfd,mfd}.{svg,json}` + `BRIDGE.md` | `flow_graph/views/` |
| `sld` | `sld.svg` / `sld.json` + `sld/` (efd-thermal/ess) | `views/efd-elec` (+ peers) |
| `bom` | `bom.csv`, `bom_self_copy.json` | graph nodes + AQS-BOM-SC-001 flags |
| `matplotlib` | `matplotlib/*.png` | optional hub bridged PNGs (copy-only) |
| `3d` | `3d/recipe.json`, `3d/README.md` | bridge + name map + presence filter |

### C1 smoke

```bash
cd design_tool
python3 -c "
from aqs_design_tool.api.store import SandboxStore
from aqs_design_tool.models import ExportRequest
from aqs_design_tool.export.pack import export_pack
rec = SandboxStore().create(label='c1-smoke')
resp = export_pack(rec, ExportRequest(export_modules=[
    'params','streams','gaps','compliance_flags','pfd','sld','bom','matplotlib']))
assert 'pfd/pfd.svg' in resp.files and 'sld.svg' in resp.files and 'bom.csv' in resp.files
print('OK', resp.pack_dir)
"
```

**C1 exit:** Yes (local). **C2/C3:** blocked pending GitHub publish authorize — not started.


## Pack module `3d/` + presence filter (done 2026-10-01 CT)

Module `3d` emits `3d/recipe.json` (`aqs-3d-recipe-1.0`) and `3d/README.md` rebuild
pointer from `graph_geometry_bridge` + `unit_freecad_map.json`. Presence policy
skips `enabled=false` / `presence=placeholder` (unless map `massing_only`) and
keeps logical `unmapped` as skip. No deferred-only warning when `3d` is requested.
Geometry and rates are not invented from the graph. CERN-OHL-S-2.0.

### D3 smoke

```bash
cd design_tool
python3 -c "
from aqs_design_tool.api.store import SandboxStore
from aqs_design_tool.models import ExportRequest
from aqs_design_tool.export.pack import export_pack
rec = SandboxStore().create(label='d3-smoke')
resp = export_pack(rec, ExportRequest(export_modules=['params','3d']))
assert '3d/recipe.json' in resp.files
assert not any('deferred' in n.lower() for n in resp.notes if '3d' in n.lower() or 'Module' in n)
print('OK', resp.pack_dir)
"
# Presence filter tests (hub/share freecad):
python3 ../models/freecad/graph_geometry_bridge.py --self-test
```

**D3/D4 exit:** Yes (local). Pack `3d/` ships; baseline FCStd object count unchanged under gold presence; T6 disable removes mapped Feature.


## U6 — working design UI on the unified engine (2026-10-19)

The UI runs on the unified parametric system (graph + `flow_graph/system_tree.yaml` +
`flow_graph/param/drivers.json` + regen). Three read-only endpoints were added
(`design_tool/aqs_design_tool/api/app.py`; commit 5024743):

| Method | Path | Role |
|---|---|---|
| GET | `/api/v1/system-tree` | Tree nodes with resolved unit sets and kW/presence aggregates, from `flow_graph/system_tree.yaml` + graph (structure break returns 409) |
| GET | `/api/v1/params` | `drivers.json` listing (key / value / units / ref / register / needs_verification) with the drivers sha |
| GET | `/api/v1/regen-status` | Derived-artefact staleness via `docs-authority/_rev_stamp.py --check-only` plus the last regen receipt (graph sha, passes, vouched). Uses `--check-only` so a GET never mutates authority docs — documented deviation from the brief |

Web panels (`web/src/components/`): **ParamsPanel** (searchable, needs-verification-filtered
drivers table with citation badges, read-only), **TreeTogglePanel** (four-level AQS-SYS-TREE
render with indeterminate parents), **RegenStatusBadge** (staleness indicator, re-checks after
every solve). Component details: `web/README.md`.

**Toggle precedence.** Sandbox overrides exist at four levels — `sector_enabled` (root),
`system_enabled` (train), `subsystem_enabled`, `unit_enabled` (leaf) — and resolve
**most-specific-wins**, server-side in `store.apply_overrides`; the graph stays the authority.
Verified over HTTP: a train toggle flags exactly that train's units; a unit flag beats the
train flag. Nothing in the UI writes the graph, drivers, tree, or authority docs — the write
path is edit → `python3 -m flow_graph.param.regen`.

## What this is

Typed MVS JSON (`schema_version` **aqs-mvs-0.3**) plus a Python **FastAPI**
solver stub that understands Sector Definitions, gaps, unclosed streams,
surplus reporting, and electrical match hooks.

- Candidate MVS is **read-only** (`GET /api/v1/mvs`).
- All edits go through **sandboxes**; export writes a **new pack** under
  `exports/` — never overwrites locked / candidate MVS.
- Solver may return `status: partial` with gaps/surplus keys; it **does
  not claim false loop closure**.

## Relation to authority docs

| Doc | Role |
|---|---|
| `docs-authority/DESIGN_TOOL_ARCHITECTURE.md` (**AQS-UI-001** Rev C) | Architecture lock — colony MVS §3.2, schema §6, API §7, Sector Definitions §3.1 |
| `docs-authority/SECTOR_DEFINITIONS.md` (**AQS-SEC-001** Rev D) | Authoritative `sector_id` map — reconciled into `sector_definitions.py` / seed |
| `docs-authority/STREAM_REGISTER.md` (**AQS-STR-001**) | `stream_id` / `S##` seed |
| `docs-authority/CONTINUOUS_KW_REQUIREMENTS.md` (**AQS-REQ-KW-001**) | Electrical continuous-kW study inputs |
| `models/freecad/params.py` | `SCALE_M = 1.0` electrical module counts |
| `docs-authority/AUTHORITY.md` (**AQS-AUTH-001**) | Hub pointer to this package |
| Local planning artefacts (`MVS_GAP_AUDIT.md`, `SECTOR_CAPACITY_AUDIT.md`, `LEGACY_PROFILE_GAP.md`) | Planning/audit evidence; not CAD authority and not published |

No Odysseus runtime dependency.

**Phase A (2026-10-01):** `null_rate_kind` on null streams; upper-band food `pass_study`; unit-level unreclaimed map (`unit_enabled`); residual polish. **WP-Ap1 (2026-10-01):** graph sole authority; `candidate_mvs` = generated projection; still never sets `mvs_equivalent=true` while incomplete.
**WP-Ap2/Ap3 (2026-10-01):** authority contract tests + projection-check; derived STREAM/MASS sync documented.
**WP-Bp1…Bp4 (2026-10-01):** graph-layer UI rebound; layer filters; export includes flow_graph_snapshot; B′ exit Yes.
**WP-C1 (2026-10-01):** pfd/sld/bom from graph; matplotlib optional; C2 not started.

## Layout

```
design_tool/
  README.md                 ← this file
  requirements.txt
  web/                      ← P1 Vite+React+TS SVG schematic (CERN-OHL-S)
  aqs_design_tool/
    models.py               ← Pydantic MVS + solve/export models
    sector_definitions.py   ← Rev B enum + placeholder sector list
    solver/stub.py          ← gaps / unclosed / surplus / electrical hooks
    api/app.py              ← FastAPI /api/v1/*
    api/store.py            ← sandbox store (`.sandbox_store/`)
    export/pack.py          ← modular pack writer
    data/candidate_mvs.json ← GENERATED projection of plant_flow_graph (do not hand-edit)
    flow_graph_adapter.py  ← plant_flow_graph → full MvsModel (sole load path)
    schema/mvs.schema.json  ← JSON Schema from Pydantic
  exports/                  ← gitignored pack dirs (see exports/README.md)
```

Package location: **`design_tool/`** (this repository)
(hub sibling to `cad/`), not `cad/design_tool/`, so CAD rebuild scripts
stay separate from the API package.

## Install / run

From this directory (or with `PYTHONPATH` including it):

```bash
cd design_tool
pip install -r requirements.txt

# Import check
python -c "from aqs_design_tool.models import MvsModel; print(MvsModel.__name__)"

# API
uvicorn aqs_design_tool.api.app:app --host 127.0.0.1 --port 8000
# or: python -m aqs_design_tool
```

OpenAPI: `http://127.0.0.1:8000/docs`

### Endpoints (`/api/v1`)

| Method | Path | Role |
|---|---|---|
| GET | `/mvs` | MVS from plant_flow_graph (sole authority; read-only) |
| GET | `/mvs/from-graph` | Alias of `/mvs` (WP-Ap1) |
| GET | `/mvs/projection-check` | WP-Ap2 drift check (409 on diverge) |
| GET | `/flow-graph` | Flow-graph meta (AQS-FLOW-GRAPH-001) |
| GET | `/flow-graph/topology` | Units/streams mapped from graph |
| GET | `/flow-graph/views/{name}` | Layer view JSON |
| POST | `/sandbox` | Create sandbox (graph topology merge + overrides) |
| GET/PATCH | `/sandbox/{id}` | Fetch / mutate sandbox only |
| POST | `/sandbox/{id}/solve` | Residuals, gaps, surplus, electrical match |
| GET | `/sandbox/{id}/flags` | Gap / unclosed / bottleneck / code flags |
| POST | `/sandbox/{id}/export` | Write pack under `exports/` |
| GET | `/sector-definitions` | Placeholder catalogue (+ AQS-SEC-001 TODO) |
| GET | `/system-tree` | **U6** — system tree + aggregates (read-only) |
| GET | `/params` | **U6** — drivers listing with sha (read-only) |
| GET | `/regen-status` | **U6** — staleness + last regen receipt (read-only, `--check-only`) |


**2026-10-01:** Candidate stream rates filled where authority exists (`study`/`authority`); scale-down unreclaimed map **AQS-SCALE-UR-001** encoded in solver; WTR surplus-key fix.

**2026-10-01 Rev C wave:** AQS-SUR-001 surplus study thresholds wired into seed + solver (`pass_study`); AQS-BOM-SC-001 self-copy flags; study units VCD/REMIN/ORC/LITHO/SOLAR; AQS-ESS-001 duties; AQS-SEC-001 Rev E A4–A9 locks; schema **aqs-mvs-0.3**.

## Project locks (sectors)

For goods surplus, **FAB** and **MFG** are both
`required_for_mvs_closure: true` in the seed and catalogue module (A2 closed).

**ESS — all three required in MVS (A3 Rev D):** ZNBR2 / MEOH / PUMPED_HYDRO
each have `required_for_mvs_closure: true` and are **enabled** in the
candidate seed. Redundancy is a core tenet; MeOH also feeds other process
streams. Sandbox may disable any peer; the solver then emits gap reason
`unreclaimed_resource` **for each** missing required ESS — framed as
**incomplete closure / unreclaimed resource** (problems to solve), **not**
accepted pollution or emissions. Storage closure is not claimed without evidence.

**MVS framing (AQS-UI-001 Rev C):** smallest self-sustaining human colony
(Moon/Mars class) — full manufacturing + habitation; can make its own
parts; can copy itself (RepRap-class); can scale up (GVCS-class) or down.
Scaled-down omissions are modelled as unreclaimed / incompletely closed
streams. Surplus-export goal retained.

## AQS-SEC-001 reconcile (mid-P0)

- ``WATER`` → ``WTR``; added ``ELEC`` (hub) distinct from ``ELEC_PV``.
- ``GLASS`` ``required_for_mvs_closure=true`` per catalogue.
- 21 mapped ``sector_id`` rows; aliases ``POWER``/``FRM``/… rejected
  (see ``NON_SECTOR_ALIASES``). Do **not** add Sector Definition classes without a catalogue revision.
- GEO remains optional in seed (catalogue ``study``; ORC TBD).
- Rev D / A3: all three ESS peers ``required_for_mvs_closure=true``;
  missing → ``unreclaimed_resource`` (replaces Rev C ≥1 /
  ``ess_peer_set_all_disabled`` set-level rule).

## Known incompletenesses

- Mass / energy balances are **stub**: residuals mark `incomplete`.
- Remaining stream rates still `null` (life gas, inventory cycle, events,
  TBD duties) → `rate_incomplete_study`; filled rates cite authority docs
  as `study`/`authority` (not treated as closed balances).
- Surplus values now study-computed vs **AQS-SUR-001** thresholds; `pass_study` may be true while freeze of AQS-MVS-001 remains open.
- Self-copy checklist flags on `mvs_criteria.self_copy` (Partial).
- Sector catalogue is **AQS-SEC-001** Rev E (`docs-authority/SECTOR_DEFINITIONS.md`).
- Candidate MVS ≠ frozen `AQS-MVS-001` gold file.
- PFD/SLD/BOM export modules done (graph-driven); pack `3d/` + presence filter done; GitHub pack publish not started.

## P1 / deferred export backlog (explicit)

| Module | Status | Notes |
|---|---|---|
| params / streams / compliance_flags / gaps | Present | `export/pack.py` |
| **sld** | Done | Graph `views/efd-elec` → `sld.svg`/`sld.json` |
| **pfd** | Done | Graph `views/pfd`+`mfd` → pack `pfd/`; matplotlib optional separate |
| **bom** | Partial (RepRap) | `bom.csv` from graph nodes; flags from AQS-BOM-SC-001; `reprap_bom_complete` still false |
| **matplotlib** | Optional exporter | Copy bridged hub PNGs only; not authority |
| **3d** | Done | `3d/recipe.json` + rebuild pointer; presence decisions in recipe |
| Schematic UI | **P1 + B′** | `web/` graph-layer; AQS-UI-001 §11 |

PFD/SLD/BOM/`3d` export does not close GitHub pack publish. Phase D exit still needs a dry-run checklist in BUILD_3D_FROM_FLOW.


## P1 schematic UI (`web/`)

```bash
# Terminal 1 — API (this directory)
uvicorn aqs_design_tool.api.app:app --host 127.0.0.1 --port 8000

# Terminal 2 — UI
cd web && npm install && npm run dev
# → http://127.0.0.1:5173  (proxies /api → :8000)
```

CORS: FastAPI allows `http://127.0.0.1:5173` and `http://localhost:5173`.

### P1 smoke (curl + build)

```bash
# with API up:
curl -s http://127.0.0.1:8000/health
SID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/sandbox -H 'Content-Type: application/json' -d '{"label":"smoke"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sandbox_id'])")
curl -s -X PATCH "http://127.0.0.1:8000/api/v1/sandbox/$SID" -H 'Content-Type: application/json' -d '{"overrides":{"sector_enabled":{"FAB":false}}}'
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/solve" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "http://127.0.0.1:8000/api/v1/sandbox/$SID/export" -H 'Content-Type: application/json' -d '{"export_modules":["params","streams","gaps","compliance_flags"]}'
cd web && npm run build
```

## Licence header

New source files carry:

```
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
```

See repo `LICENSE` (CERN-OHL-S-2.0).

## Typed flow graph adapter (WP-A10 / AQS-FLOW-GRAPH-001)

**Sole topology authority:** `../flow_graph/plant_flow_graph.json` (locks: layered_views,
full_depth_now, efd_three_layers, typed_graph_sole, present_plus_placeholders).

**Wired (2026-10-01):** `aqs_design_tool/flow_graph_adapter.py`

| Endpoint | Role |
|---|---|
| `GET /api/v1/mvs` | Candidate MVS fields only (read-only seed) |
| `GET /api/v1/mvs/from-graph` | Candidate fields + graph units/streams |
| `GET /api/v1/flow-graph` | Graph meta (counts, path, locks) |
| `GET /api/v1/flow-graph/topology` | Mapped units/streams/gaps |
| `GET /api/v1/flow-graph/views/{pfd\|mfd\|efd-*}` | Layer view JSON |
| `POST /api/v1/sandbox` | Defaults to **graph topology merge** for solve |

Rules: placeholders keep null rates; `DOCK_EXPORT_TBD` stays TBD (no fake S##);
solver may return `partial` with gaps; **never** sets `mvs_equivalent=true` from
topology alone.

Layer SVG/DOT/JSON: `../flow_graph/views/`. Legacy matplotlib PFD/SLD:
`../flow_graph/LEGACY_PFD_SCRIPTS.md`.

```bash
cd ../flow_graph && python3 render_layer_views.py && python3 export_authority_md.py
# API smoke (from design_tool/):
# curl -s http://127.0.0.1:8000/api/v1/flow-graph
# curl -s http://127.0.0.1:8000/api/v1/mvs/from-graph | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['units']), len(d['streams']))"
```

