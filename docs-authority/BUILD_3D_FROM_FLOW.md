# Building 3D models from the plant flow graph

Document number: AQS-3D-BUILD-001  
Revision: H  
Date: 2026-10-24  
Licence: CERN-OHL-S-2.0  
Basis: `CAD_SCRIPTING_PROTOCOL.md` (AQS-CAD-001, the general pipeline) and `STACK_3D_DECISION.md` (FreeCAD as the default tool). This is not a document stamped by a professional engineer.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | First issue | Baseline rebuild path, limitations, and bridge stub | 2026-10-01 |
| B | Protocol align | End-to-end mapped to AGENT_CAD_PROTOCOL; stack pointer; share paths; flow_graph views primary 2D | 2026-10-01 |
| C | Plan pointer | Phase D impl plan is planning-local (AQS-PLAN-3D-001); not shipped here | 2026-10-01 |
| D | Name-map queue | Name-map coverage notes CAD massing for 18 present unmapped units; overlay next / parallel OK | 2026-10-01 |
| E | Overlay applicator | Allow-list applicator → `params_overlay.py` only; bridge `--apply-overlay`; gold `params.py` never rewritten | 2026-10-01 |
| F | Pack `3d/` + presence | Pack module `3d/` recipe + rebuild pointer; presence filter omit/tag; bridge `--self-test` / `--apply-presence` | 2026-10-01 |
| G | Placement study | Placement schema study done (hub planning-local); adopt schema draft / defer applicator / reject auto-router; no invented mm | 2026-10-01 |
| H | DOC_STYLE rewrite | Rewritten for a reader new to the project (AQS-DOC-002): purpose, terms, procedure and figure captions; commands and limits unchanged | 2026-10-24 |

## 1. Purpose and scope

This guide explains how to rebuild the three-dimensional (3D) plant model from this repository, and how much of the model the plant flow graph controls today. It is written for someone who has cloned the repository and wants to open, rebuild or adapt the model.

The short answer is that the graph does not yet place or size solids. The FreeCAD builders take every size and position from `models/freecad/params.py`. The graph decides which units are present: a post-processing step can omit or tag the solids of units that are switched off in a design. Vessel dimensions, rates and placements are never derived from the graph.

## 2. Terms

Plant flow graph: `flow_graph/plant_flow_graph.json`, the only authority for which units exist and how streams connect them (AQS-FLOW-GRAPH-001).

Baseline model: the M1 plant built from `params.py` at `SCALE_M = 1.0` (one metre in the model is one metre built). See `SCALE_MODEL.md`.

Export pack: a folder written by the design tool for one design. It holds a snapshot of the graph, a parameter overlay and, on request, drawings, tables and a 3D recipe.

Overlay: a set of parameter changes from an export pack. It is written only to `params_overlay.py` and only for keys on an allow-list. The master `params.py` is never rewritten.

Presence filter: the step that omits or tags the solids of units that a design marks `enabled=false` or `presence=placeholder`.

Bridge: `models/freecad/graph_geometry_bridge.py`, the script that compares the graph with the CAD model and applies the overlay and presence filter.

Feature: a named solid in a FreeCAD document.

## 3. What is connected today

Table 3.1 states what each path does at this revision.

Table 3.1. Status of the 3D paths

| Path | What it does |
|---|---|
| Baseline (connected) | The FreeCAD builders read `models/freecad/params.py` (and OpenSCAD `params.scad`) and write `plant.FCStd`. The flow graph does not drive the geometry |
| Study, Phase D | Design-tool export packs contain `flow_graph_snapshot.json`, `params.json` (the overlay) and, when module `3d` is requested, `3d/recipe.json`. The presence filter omits or tags Features of disabled and placeholder units; logical units with no CAD solid (`unmapped`) are skipped. The implementation plan AQS-PLAN-3D-001 Rev G is kept in the unpublished planning records; its name map, overlay, pack recipe, presence filter and placement-schema study are complete. A placement applicator is deferred, and an automatic router that would place solids from graph edges was rejected |
| Default tool | FreeCAD 1.0 console (`/usr/bin/freecadcmd`). Three.js or another live browser mesh only after a later written decision in `STACK_3D_DECISION.md` |

## 4. Pipeline

Figure 4.1 maps the general pipeline of `CAD_SCRIPTING_PROTOCOL.md` §5 onto the files of this repository. Each stage feeds the one below it.

Figure 4.1. From locked names to 3D detail, with the repository location of each stage

```
locked names (GLOSSARY / unit_id)          docs-authority/GLOSSARY.md
        ↓                                  flow_graph node names
2D PFD / typed graph                       flow_graph/plant_flow_graph.json
        ↓                                  flow_graph/views/*.svg  ← primary published 2D
shared parameters                          models/freecad/params.py
        ↓                                  models/openscad/params.scad
3D massing (FreeCAD Part)                  models/freecad/*.py → plant.FCStd
        ↓
detail parts (OpenSCAD) → STL              models/openscad/ → models/export/
        ↓
import meshes, hide massing                import_mfg / import_details
        ↓
(optional) shop renders                      media/  (the auto isometric sheets were retired 2026-10-27; the 3D presentation bias is this FreeCAD model)
```

Table 4.1 says which stages are connected.

Table 4.1. Pipeline stages

| Stage | Repository files | Connected? |
|---|---|---|
| Locked names | Graph `unit_id` and the glossary | Names exist; CAD Feature names follow the builders |
| 2D drawings and graph | `flow_graph/` and `flow_graph/views/*.svg` | Yes, for 2D drawings and the design tool |
| Parameters | `params.py` and `params.scad` | Yes; the only source of sizes |
| FreeCAD massing | `models/freecad/` and `REBUILD.sh` | Yes; builds the baseline catalogue, not filtered by the graph |
| OpenSCAD to STL | `models/openscad/`, `models/export/` | Optional detail |
| Mesh import | Builders under `models/freecad/` | Yes, when the STL files are present |
| Graph filter and overlay | Pack `3d/` and the bridge presence step | Yes (recipe and presence). Placement schema studied; applicator deferred; no edge router |

The primary published 2D drawings are `flow_graph/views/*.svg`. The matplotlib PFD and SLD exporters in `flow_graph/exporters/matplotlib/` are optional. They are not topology authority, and their PNG files are not kept in the repository.

## 5. Prerequisites

Table 5.1. Software needed

| Tool | Requirement |
|---|---|
| FreeCAD | `/usr/bin/freecadcmd` version 1.0, installed with apt. Do not use the 1.1 AppImage. See `FREECAD_PROTOCOL.md` |
| FreeCAD graphical program (optional) | `/usr/bin/freecad`, to open `.FCStd` and `.step` files |
| OpenSCAD (optional) | On `PATH`, to recompile the detail STL files |
| Python 3 | For the bridge and the design tool |

## 6. Rebuilding the baseline model

The repository keeps the CAD files under `models/` (the development tree used `cad/`). The wrapper script handles the paths.

```bash
cd models
bash REBUILD.sh            # links materials + STL paths, then freecadcmd build_plant.py
bash REBUILD.sh --stls     # also run OpenSCAD detail compile first
bash REBUILD.sh --plant-only
```

Table 6.1 lists where things are.

Table 6.1. Repository paths

| Need | Path |
|---|---|
| Rebuild entry point | `models/REBUILD.sh` |
| FreeCAD builders and `params.py` | `models/freecad/` |
| OpenSCAD sources | `models/openscad/` |
| Compiled STL files | `models/export/` (including `detail/`) |
| Materials table | `tables/materials.csv` (`REBUILD.sh` links it into `models/`) |
| Plant flow graph | `flow_graph/plant_flow_graph.json` |
| Primary 2D drawings | `flow_graph/views/*.svg` |
| Bridge | `models/freecad/graph_geometry_bridge.py` |

The same steps by hand:

```bash
# 1) Make stamp_materials / import_mfg paths resolve under models/
cd models
ln -sfn ../tables/materials.csv materials.csv
mkdir -p detail
ln -sfn ../export/detail detail/stl

# 2) FreeCAD plant (SCALE_M from params.py)
cd freecad
/usr/bin/freecadcmd build_plant.py
# → plant.FCStd
```

The wet line can be built alone; it also takes its sizes from the parameters:

```bash
cd models/freecad
/usr/bin/freecadcmd leach_cstr.py
/usr/bin/freecadcmd ew_cell.py
/usr/bin/freecadcmd build_wet.py
/usr/bin/freecad wet_line.FCStd   # GUI
```

To rebuild documents and models together, run `python3 -m flow_graph.param.regen --cad` from the repository root, as described in `docs-authority/REBUILD.md`.

## 7. From the flow graph to the model

### 7.1 The plant flow graph

```
flow_graph/plant_flow_graph.json   # sole topology authority (AQS-FLOW-GRAPH-001)
flow_graph/views/*.svg             # graph-layer diagrams (primary published 2D)
```

The graph drives the 2D layer drawings and the design-tool topology. It does not place FreeCAD solids, and will not until a placement applicator is released.

### 7.2 Design-tool export pack

Table 7.1 lists what a pack contains and what each file does for the 3D model.

Table 7.1. Export pack contents

| File | Role for the 3D model |
|---|---|
| `flow_graph_snapshot.json` | Frozen graph for the sandbox; input to the bridge, not to the builders |
| `params.json` | Study overlay (`scale_m`, electrical counts). Apply with `params_overlay_apply.py` or the bridge option `--apply-overlay`; writes `params_overlay.py` only, never the master `params.py` |
| `mvs_snapshot.json`, `design.json` | Projection of the minimum viable system (MVS) and sandbox state; no solids |
| `pfd/`, `sld`, `bom` (on request) | 2D drawings and tables |
| `3d/` | `recipe.json` (format `aqs-3d-recipe-1.0`), a README pointing to the rebuild, optional SHA-256 hashes of the FCStd and STEP files, and the presence decisions |

### 7.3 Using the bridge

```bash
cd models/freecad
python3 graph_geometry_bridge.py \
  --graph ../../flow_graph/plant_flow_graph.json

# or against an export pack snapshot:
python3 graph_geometry_bridge.py \
  --graph /path/to/export/flow_graph_snapshot.json \
  --params /path/to/export/params.json \
  --out out/3d_recipe.json

# Safe overlay → params_overlay.py (allow-list only; gold untouched)
python3 graph_geometry_bridge.py \
  --params /path/to/export/params.json --apply-overlay
# equivalent:
python3 params_overlay_apply.py --params /path/to/export/params.json
python3 params_overlay_apply.py --self-test
python3 graph_geometry_bridge.py --allow-list

# Presence report / post-pass / tests
python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
  --presence-report
python3 graph_geometry_bridge.py --graph /path/to/export/flow_graph_snapshot.json \
  --apply-presence --fcstd plant.FCStd --fcstd-out out/plant_filtered.FCStd
python3 graph_geometry_bridge.py --self-test
```

The bridge does the following:

- lists units by `sector_id` and `enabled`;
- loads the coverage of the map from units to FreeCAD names;
- notes any difference between the pack's `scale_m` and `SCALE_M` on disk;
- applies allow-listed overlay keys to `params_overlay.py` only;
- writes a recipe JSON, recording `applied_keys` when an overlay was applied;
- skips units with `enabled=false` or `presence=placeholder` unless the map marks them `massing_only`, and skips logical units marked `unmapped`;
- with `--apply-presence`, omits or tags the mapped Feature names in a copy of an FCStd file;
- for pack module `3d`, writes `3d/recipe.json` and the rebuild pointer.

The bridge does not:

- resize tanks from rates or invent vessel dimensions;
- lay out solids from graph edges;
- call Three.js;
- rewrite the master `params.py` from a pack overlay.

After the inventory, the bridge can rebuild the baseline solids; this still uses the parameters only:

```bash
python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
  --rebuild-baseline
```

## 8. Procedure from start to finish

1. Read this guide, `CAD_SCRIPTING_PROTOCOL.md`, `STACK_3D_DECISION.md`, `FREECAD_PROTOCOL.md` and `SCALE_MODEL.md`.
2. Install the FreeCAD 1.0 console (`freecadcmd`) with apt.
3. Open the primary 2D drawings, `flow_graph/views/*.svg`, and if useful the graph JSON.
4. Open `models/freecad/plant.FCStd` to see the M1 baseline massing.
5. Rebuild with `models/REBUILD.sh` after changing `params.py` or the STL files. Keep `SCALE_M=1.0` unless you deliberately fork.
6. Export a design pack from the design tool (graph snapshot and overlay).
7. Run `graph_geometry_bridge.py` on the snapshot to compare the topology with the CAD catalogue.
8. Optionally apply the pack overlay with `--apply-overlay`, which writes `params_overlay.py` for allow-listed keys only. Do not overwrite the master `params.py`. Rebuilds still import `params` unless you deliberately point a session at the fork.
9. Export with design-tool module `3d`, then open `3d/recipe.json` and `3d/README.md`. Apply the presence step when the sandbox disables units. The placement-schema study is complete and its applicator is deferred; there is no edge router and no invented dimension. Do not adopt Three.js without a written decision in `STACK_3D_DECISION.md`.

## 9. Related documents

| Document | Role |
|---|---|
| `CAD_SCRIPTING_PROTOCOL.md` (AQS-CAD-001) | General pipeline from process flow diagram to CAD |
| `STACK_3D_DECISION.md` | FreeCAD as default; what happens to Three.js and matplotlib |
| `FREECAD_PROTOCOL.md` | FreeCAD binary, script template and failure modes |
| `REBUILD.md` (AQS-REB-001) | Regeneration pipeline |
| `SCALE_MODEL.md` | What `SCALE_M` changes |
| `STL_MANIFEST.md` | OpenSCAD STL contract |
| `DESIGN_TOOL_ARCHITECTURE.md` | Phase D FreeCAD default; pack layout (§3.3) |
| Unpublished planning records | Phase D plan AQS-PLAN-3D-001 Rev G and the placement study in the planning note PLACEMENT_SCHEMA_STUDY |
| `../models/REBUILD.sh` | Rebuild script |
| `../models/freecad/graph_geometry_bridge.py` | Bridge (inventory, name map, overlay, presence, recipe 1.0) |
| `../models/freecad/params_overlay_apply.py` | Allow-listed overlay into the `params_overlay.py` fork |
| `../flow_graph/views/` | Primary published 2D drawings |
| `../tables/` | `materials.csv` and BOM tables |
