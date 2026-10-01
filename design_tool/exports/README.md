# Design-pack exports

Sandbox `POST /api/v1/sandbox/{id}/export` writes modular packs here
(e.g. `sbx_…_YYYYMMDD_HHMMSS/`). Packs never overwrite the candidate
MVS under `aqs_design_tool/data/` or `flow_graph/plant_flow_graph.json`.

Licence: CERN-OHL-S-2.0. Per-pack contents follow AQS-UI-001 §8.

## Modules (request via `export_modules`)

| Key | Emitted when requested | Source |
|---|---|---|
| (always) | `flow_graph_snapshot.json`, `mvs_snapshot.json`, `design.json`, `gaps.md`, `README.md` | graph + sandbox |
| `params` | `params.json` | sandbox overlay |
| `streams` | `streams.csv` | sandbox streams |
| `compliance_flags` | `compliance_flags.md` | last solve |
| `pfd` | `pfd/{pfd,mfd}.{svg,json}` | `flow_graph/views/` (graph) |
| `sld` | `sld.svg`, `sld.json`, `sld/*` | `views/efd-elec` (+ thermal/ess) |
| `bom` | `bom.csv`, `bom_self_copy.json` | graph nodes + AQS-BOM-SC-001 flags |
| `matplotlib` | `matplotlib/*.png` | optional bridged hub PNGs (copy-only) |
| `3d` | `3d/recipe.json`, `3d/README.md` | bridge + name map + presence filter |

Unused modules stay off. Matplotlib is optional and **not** topology authority.
Rates, streams, and nameplates are not invented to fill gaps. GitHub pack publish
is separate and blocked until explicitly authorized.
