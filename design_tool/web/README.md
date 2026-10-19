# Aqueous design tool — web UI (P1 / B′ / U6)

Document: `design_tool/web/` — React + Vite + TypeScript front-end for the
Aqueous design tool API (AQS-UI-001). Licence: **CERN-OHL-S-2.0**.

## Run

```bash
# Terminal 1 — API (from design_tool/)
uvicorn aqs_design_tool.api.app:app --host 127.0.0.1 --port 8000

# Terminal 2 — UI
cd web && npm install && npm run dev   # http://127.0.0.1:5173 (proxies /api → :8000)

npm run build                          # gate: tsc -b && vite build
```

## Components (`src/`)

| Component | Role |
|---|---|
| `App.tsx` | Boot: graph meta + topology, system tree, drivers, MVS projection, sandbox create + first solve |
| `SchematicCanvas` | SVG schematic over graph layer views (PFD/MFD/EFD-*) |
| `LayerFilters` | Layer view switch (pfd / mfd / efd-elec / efd-thermal / efd-ess) |
| `SectorToggles` | Sector-row enables (PATCH `sector_enabled`) |
| `TreeTogglePanel` | **U6** — AQS-SYS-TREE-001 4-level tree with checkboxes (indeterminate parents); root → `sector_enabled`, train → `system_enabled`, subsystem → `subsystem_enabled`, leaf → `unit_enabled`. Most-specific wins is resolved **server-side** (`store.apply_overrides`); the graph stays authority. Verified over HTTP at issue: a train off flags exactly that train's units; a unit flag beats the train flag |
| `SiteInputs` | Crew / SITE_LAT sandbox inputs |
| `GapPanel` | Solve status, **electrical envelope** (gen/storage/load/need/target + status badge), gaps, unclosed streams |
| `ParamsPanel` | **U6** — drivers.json table (key/value/units/ref badge/nv badge), searchable + filterable, **read-only** |
| `RegenStatusBadge` | **U6** — green/red derived-artefact staleness indicator; auto re-checks after every solve |
| `ExportButton` | Modular export pack writer |

## Endpoints consumed (U6 additions, all read-only)

| Method | Path | Role |
|---|---|---|
| GET | `/api/v1/system-tree` | Tree nodes with resolved unit sets + kW/presence aggregates from `flow_graph/system_tree.yaml` + graph |
| GET | `/api/v1/params` | `flow_graph/param/drivers.json` listing (key/value/units/ref/register/needs_verification) |
| GET | `/api/v1/regen-status` | Subprocess staleness check (`docs-authority/_rev_stamp.py --check-only` — the same evaluator `python3 -m flow_graph.param.regen --check` runs, minus its `DERIVED_REVISIONS.md` rewrite, so the GET stays side-effect free) + last regen receipt (graph sha / passes / vouched) |
| PATCH | `/api/v1/sandbox/{id}` | Sandbox-only mutations (sector/system/subsystem/unit overrides) |

Nothing in this UI writes the graph, drivers, tree, or authority docs: the
write path is edit → `python3 -m flow_graph.param.regen`.
