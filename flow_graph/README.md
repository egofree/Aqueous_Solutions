# Plant flow graph — sole typed authority

Document: **AQS-FLOW-GRAPH-001** Rev C  
Licence: **CERN-OHL-S-2.0**  
Date: 2026-10-01

## Locks (must honor)

| # | Lock | Meaning here |
|---|---|---|
| 1 | `layered_views` | One graph; PFD / MFD / EFD are **view filters** |
| 2 | `full_depth_now` | Inter-block `S##` **and** intra-aisle `IA-*` |
| 3 | `efd_three_layers` | EFD = elec / thermal / ess |
| 4 | `typed_graph_sole` | This package is the **sole** topology + MVS-field authority |
| 5 | `present_plus_placeholders` | Present-path may carry rates; study stubs are **placeholders with `rate: null`** |

Stream routes, rates, and nameplates are not filled inventively; gaps stay flagged.

## Authority contract — single write path

| Concern | Lives on graph | Legacy projection |
|---|---|---|
| Units / streams (topology + rates) | `nodes[]` / `edges[]` | `candidate_mvs.json` units/streams |
| Sector enables + `required_for_mvs_closure` | `mvs.sectors[]` | same |
| Crew / `SITE_LAT` (`site_lat_deg`) | `mvs.site` | same |
| Surplus flags / thresholds / self-copy | `mvs.mvs_criteria` | same |
| Projected MVS `schema_version` | `mvs.schema_version` (`aqs-mvs-0.3`) | root `schema_version` |
| Graph schema | root `schema_version` (`aqs-flow-graph-0.1`) | — |
| Unit `continuous_kw` / `modules` / `params` / `enabled` | `nodes[]` fields | units[] |
| Sandbox overrides | `.sandbox_store/` only (never graph) | — |

**Write path (only):** edit / regenerate `plant_flow_graph.json`  
(`build_seed.py` preserves `mvs` + node enrichment).

**Projection (read-only for consumers):**  
`python3 export_candidate_mvs.py` → `design_tool/aqs_design_tool/data/candidate_mvs.json`

Do **not** hand-edit `candidate_mvs.json`. FastAPI loads/solves from the graph.
No silent dual writes. `mvs_equivalent` stays **false** while incomplete.
`DOCK_EXPORT_TBD` remains TBD (no placeholder DOCK stream numbers).


## Sole-authority contract

Topology identity: `unit_id` / `stream_id` sets (and stream endpoints) must
match between `plant_flow_graph.json` and the generated `candidate_mvs`
projection. Hand-edited or stale `candidate_mvs.json` fails the regen-check.

```bash
cd flow_graph
python3 check_authority_contract.py          # exit 0 = PASS
python3 -m pytest test_authority_contract.py -q
# or from design_tool/:
# PYTHONPATH=../flow_graph:. python3 -m pytest ../flow_graph/test_authority_contract.py -q
```

FastAPI: `GET /health` and `GET /api/v1/flow-graph` include `projection_contract`;
`GET /api/v1/mvs/projection-check` returns **409** on drift. Solve / mvs /
sandbox always load the **graph** (never a divergent on-disk master).

## Derived STREAM / MASS sync

```bash
python3 export_authority_md.py     # → derived/{STREAM_REGISTER,MASS_FLOW}_DERIVED.md + SYNC_POINTER.md + CENSUS.md
python3 render_layer_views.py      # layer stubs still graph-driven → views/
```

`cad/STREAM_REGISTER.md` and `cad/MASS_FLOW.md` are **sync targets** (human +
derived hybrid). Prefer `derived/` as generated; do not overwrite CAD wholesale.
Do not assign DOCK stream numbers or fill null placeholder rates without authority.

## Layout

```
flow_graph/
  plant_flow_graph.json     # sole authority (nodes/edges + mvs)
  models.py                 # Pydantic
  schema/plant_flow_graph.schema.json
  build_seed.py             # rebuild topology; preserves mvs enrichment
  export_candidate_mvs.py   # → design_tool/.../candidate_mvs.json (projection)
  export_authority_md.py    # → derived/ STREAM_REGISTER + MASS_FLOW + SYNC_POINTER
  authority_contract.py    # topology identity + drift helpers
  check_authority_contract.py
  test_authority_contract.py
  render_layer_views.py     # → views/*.{json,dot,svg} (Graphviz)
  pfd_bridge.py             # thin helper for matplotlib SLD/MF bridges
  LEGACY_PFD_SCRIPTS.md     # graph-bridged matplotlib sheets (optional)
  exporters/matplotlib/     # optional PFD/SLD generators (PNGs not shipped)
  derived/                  # generated excerpts (not competing CAD masters yet)
  views/                    # JSON + DOT + SVG layer renders (primary)
```

## Regenerate

```bash
cd flow_graph
python3 build_seed.py              # rebuild plant_flow_graph.json (keeps mvs)
python3 export_candidate_mvs.py    # refresh generated candidate_mvs projection
python3 export_authority_md.py     # derived markdown excerpts + SYNC_POINTER
python3 render_layer_views.py      # JSON + DOT + SVG (needs graphviz `dot`)
python3 check_authority_contract.py
python3 -c "from models import PlantFlowGraph; \
  g=PlantFlowGraph.model_validate_json(open('plant_flow_graph.json').read()); \
  print(g.doc_id, g.revision, 'mvs', g.mvs.schema_version if g.mvs else None)"
```

## Design-tool adapter (wired)

`design_tool/aqs_design_tool/flow_graph_adapter.py` → `mvs_from_graph()`.

| Endpoint | Role |
|---|---|
| `GET /api/v1/flow-graph` | Meta (path, counts, locks, mvs block) |
| `GET /api/v1/flow-graph/topology` | Units/streams from graph |
| `GET /api/v1/flow-graph/views/{name}` | Layer view JSON |
| `GET /api/v1/mvs` | Full MVS from graph (sole authority) |
| `GET /api/v1/mvs/from-graph` | Alias of `/mvs` |
| `POST /api/v1/sandbox` | Sandboxes default to graph load + overrides |

Pointer: `design_tool/README.md`.
Legacy PFD/SLD scripts: `LEGACY_PFD_SCRIPTS.md`.

## Known gaps represented

- **S17** included; labeled on graph-bridged `electrical_sld.png` (still sparse on line PFDs).
- **DOCK_EXPORT_TBD** placeholder edge (`namespace=TBD`) — no DOCK stream number assigned; TBD block on `mass_flow_pfd.png`.
- **MeOH S73–S82** on graph + bridged mass_flow claim sheet; S79 on electrical_sld; MF table claim rows still end S72.
- **PUMPED_HYDRO / DOCK** covered by dedicated `hydro_dock_pfd.png` (graph-bridged); HYDRO elec still rate null on SLD; DOCK_EXPORT_TBD remains TBD.
- **IA-*** for EW / continuous recycle / glass / BMED / polish — placeholder rates; **overlaid on corresponding line PFDs**.
- Study stubs (VCD, LITHO, ORC, BLOW, REMIN, ELECTRODE_COAT, SOLAR_PV_CELL, GEO_ORC):
  `presence=placeholder`, rates null.

## Matplotlib bridge

`pfd_bridge.py` — shared loader/filter for SLD/MF + IA line PFDs + `hydro_dock_pfd` + znbr2/meoh.
See `LEGACY_PFD_SCRIPTS.md` and `exporters/matplotlib/README.md`.
**Share:** views SVG primary; matplotlib optional; PNGs not shipped.


## Design-tool export modules (graph consumers)

`design_tool/aqs_design_tool/export/pack.py` may copy layer artefacts from
`views/` into an export pack when modules `pfd` / `sld` are requested, and
roll up `bom.csv` from `nodes[]`. Optional `matplotlib` module copies hub
bridged PNGs only. See `design_tool/README.md` (export modules). Does not rewrite
this graph. GitHub publish of packs is not started.

## Related

- Audit: AQS-FLOW-AUD-001 (local planning artefacts, not published)
- Legacy CAD sync targets: `docs-authority/` STREAM_REGISTER / MASS_FLOW (or derived/)
- Authority lock: `docs-authority/AUTHORITY.md`
- Plan notes: local planning artefacts (not published)
- Contract: `check_authority_contract.py` / `test_authority_contract.py`
- Derived sync: `derived/SYNC_POINTER.md`
