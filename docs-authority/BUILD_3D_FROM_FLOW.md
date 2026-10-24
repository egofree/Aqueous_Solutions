# Building 3D models from the plant flow graph

Document number: **AQS-3D-BUILD-001**  
Revision: **G**  
Date: 2026-10-01  
Licence: CERN-OHL-S-2.0  
Audience: Users of the published `aqueous-solutions` tree  
Authority: Aligns with `AGENT_CAD_PROTOCOL.md` (design-agnostic pipeline) and
`STACK_3D_DECISION.md` (FreeCAD default). Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | First issue | Baseline rebuild path, limitations, and bridge stub | 2026-10-01 |
| B | Protocol align | End-to-end mapped to AGENT_CAD_PROTOCOL; stack pointer; share paths; flow_graph views primary 2D | 2026-10-01 |
| C | Plan pointer | Phase D impl plan is planning-local (AQS-PLAN-3D-001); not shipped here | 2026-10-01 |
| D | Name-map queue | Name-map coverage notes CAD massing for 18 present unmapped units; overlay next / parallel OK | 2026-10-01 |
| E | Overlay applicator | Allow-list applicator → `params_overlay.py` only; bridge `--apply-overlay`; gold `params.py` never rewritten | 2026-10-01 |
| F | Pack `3d/` + presence | Pack module `3d/` recipe + rebuild pointer; presence filter omit/tag; bridge `--self-test` / `--apply-presence` | 2026-10-01 |
| G | Placement study | Placement schema study done (hub planning-local); adopt schema draft / defer applicator / reject auto-router; no invented mm | 2026-10-01 |

---

## 0. Status and limitations

| Path | What it does today |
|---|---|
| **Baseline (wired)** | FreeCAD builders read **`models/freecad/params.py`** (and OpenSCAD `params.scad`) and write **`plant.FCStd`**. Geometry is **not** driven by the flow graph. |
| **Study / Phase D** | Design-tool export packs include `flow_graph_snapshot.json` + `params.json` (overlay) + **`3d/recipe.json`** when module `3d` is requested. Presence filter omits/tags Features for `enabled=false` / placeholder (logical unmapped stay skip). Impl plan (hub planning-local): **AQS-PLAN-3D-001** Rev G — name map, overlay, pack recipe, presence, and placement-schema study complete (placement applicator deferred; edge auto-router rejected). Overlay still forks `params_overlay.py` only (never gold `params.py`). Vessel millimetres, rates, and placements are not invented from the graph. |
| **Stack default** | FreeCAD 1.0 rebuild (`/usr/bin/freecadcmd`). **Three.js** (or live browser mesh) only with a **later written decision** — see `STACK_3D_DECISION.md`. |

**Graph → place/size solids from edges is not wired** (no auto layout).
Presence filter + name map + overlay fork **are** wired: rebuild the
**baseline M1 plant**, then omit/tag Features for disabled/placeholder
units per pack `3d/recipe.json`. Vessel millimetres still come only from
`params.py` / allow-listed overlay — never from rates.

---

## 1. Pipeline (AGENT_CAD_PROTOCOL aligned)

Canonical agent pipeline (`AGENT_CAD_PROTOCOL.md` §3), mapped onto **this
share tree**:

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
(optional) shop / animation                media/, iso/
```

| Stage | Share artefact | Wired today? |
|---|---|---|
| Locked names | Graph `unit_id` / glossary | Names exist; CAD Feature names follow builders |
| 2D / graph | `flow_graph/` + **`views/*.svg`** | Yes for 2D / design_tool |
| Params | `params.py` / `params.scad` | Yes — sole size driver |
| FreeCAD massing | `models/freecad/` + `REBUILD.sh` | Yes — **baseline catalogue**, not graph filter |
| OpenSCAD → STL | `models/openscad/`, `models/export/` | Optional detail |
| Import | builders under `models/freecad/` | Yes when STLs present |
| Graph → filter/overlay solids | pack `3d/` + bridge presence | **Wired** (recipe + presence); placement schema studied, applicator deferred (no edge auto-router) |

Matplotlib PFD/SLD PNGs are **optional exporters only**
(`flow_graph/exporters/matplotlib/`). They are **not** topology authority
and **PNGs are not shipped** in this tree. Primary 2D drawings:
**`flow_graph/views/*.svg`**.

---

## 2. Prerequisites

| Tool | Requirement |
|---|---|
| FreeCAD | **`/usr/bin/freecadcmd` 1.0** (apt). Do **not** use the 1.1 AppImage. Details: `FREECAD_PROTOCOL.md`. |
| FreeCAD GUI (optional) | `/usr/bin/freecad` to open `.FCStd` / `.step` |
| OpenSCAD (optional) | On `PATH` if you want to recompile detail STLs |
| Python 3 | For the bridge and (on hub) design_tool |

On-disk plant baseline: **`SCALE_M = 1.0`** in `models/freecad/params.py`
(1 m : 1 m manufacturing). See `SCALE_MODEL.md`.

---

## 3. Present path — rebuild baseline 3D from this share tree

Share layout differs from the hub (`cad/` → `models/`). Prefer the share wrapper:

```bash
cd models
bash REBUILD.sh            # links materials + STL paths, then freecadcmd build_plant.py
bash REBUILD.sh --stls     # also run OpenSCAD detail compile first
bash REBUILD.sh --plant-only
```

### 3.1 Share path map

| Need | Share path |
|---|---|
| Rebuild entry | `models/REBUILD.sh` |
| FreeCAD builders + `params.py` | `models/freecad/` |
| OpenSCAD sources | `models/openscad/` |
| Compiled STLs | `models/export/` (incl. `detail/`) |
| Materials CSV | `tables/materials.csv` (REBUILD.sh links into `models/`) |
| Typed graph | `flow_graph/plant_flow_graph.json` |
| Primary 2D views | `flow_graph/views/*.svg` |
| Graph inventory bridge | `models/freecad/graph_geometry_bridge.py` |

Manual equivalent:

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

Wet-line-only sequence (also params-driven):

```bash
cd models/freecad
/usr/bin/freecadcmd leach_cstr.py
/usr/bin/freecadcmd ew_cell.py
/usr/bin/freecadcmd build_wet.py
/usr/bin/freecad wet_line.FCStd   # GUI
```

**Local hub operators** (not this repo) may use a hub `rebuild.py`
and `cad/REBUILD.sh` (absolute hub paths). `docs-authority/REBUILD.md`
documents that menu; it is not required for share-tree rebuild.

---

## 4. Flow diagrams → what you actually get

### 4.1 Typed plant graph (in this package)

```
flow_graph/plant_flow_graph.json   # sole topology authority (AQS-FLOW-GRAPH-001)
flow_graph/views/*.svg             # graph-layer diagrams (primary published 2D)
```

These drive **2D** layer views and design_tool topology — **not** FreeCAD
Part placement. That limitation remains until a placement applicator ships.

### 4.2 Design-tool export pack (from your design)

Typical pack always includes:

| File | Role for 3D |
|---|---|
| `flow_graph_snapshot.json` | Frozen graph for the sandbox — **input to bridge**, not to builders |
| `params.json` | Study overlay (`scale_m`, electrical counts). Apply via `params_overlay_apply.py` / bridge `--apply-overlay` → **`params_overlay.py` fork only** (never gold `params.py`) |
| `mvs_snapshot.json` / `design.json` | MVS projection / sandbox — not solids |
| `pfd/` / `sld` / `bom` (if requested) | 2D / tables |
| `3d/` | **Emitted:** `recipe.json` (`aqs-3d-recipe-1.0`) + README rebuild pointer; optional FCStd/STEP sha256; presence decisions |

### 4.3 Bridge: inventory, overlay, presence, pack recipe

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

What the bridge **does**:

- Lists units by `sector_id` / `enabled`
- Loads unit↔FreeCAD name-map coverage
- Notes pack `scale_m` vs on-disk `SCALE_M`
- Applies allow-listed overlay keys to **`params_overlay.py`** only
- Writes a **recipe JSON** (records `applied_keys` when overlay applied)
- Presence filter: skip `enabled=false` / `presence=placeholder` unless map `massing_only`; logical `unmapped` stay skip
- `--apply-presence` post-pass omits or tags mapped Feature Names on an FCStd **copy**
- Pack module `3d` writes `3d/recipe.json` + rebuild pointer

What it **does not** do:

- Resize tanks from rates or invent vessel millimetres
- Auto-layout from edges
- Call Three.js
- Rewrite gold `params.py` from pack overlay

Optional: rebuild baseline solids after inventory (still params-driven):

```bash
python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
  --rebuild-baseline
```

---

## 5. End-to-end checklist

1. **Read** this file + `AGENT_CAD_PROTOCOL.md` + `STACK_3D_DECISION.md` +
   `FREECAD_PROTOCOL.md` + `SCALE_MODEL.md`.
2. **Install** FreeCAD 1.0 apt console (`freecadcmd`).
3. **Open** primary 2D: `flow_graph/views/*.svg` (and optionally the graph JSON).
4. **Open** shipped `models/freecad/plant.FCStd` to see the M1 baseline massing.
5. **Rebuild** with `models/REBUILD.sh` if you change `params.py` or STLs
   (`SCALE_M=1.0` unless you knowingly fork).
6. **Export** a design pack from design_tool (graph snapshot + overlay).
7. **Run** `graph_geometry_bridge.py` on the snapshot to compare topology to
   the CAD catalogue.
8. **Optionally** apply pack overlay with `--apply-overlay` → `params_overlay.py`
   (allow-list only). Do **not** overwrite gold `params.py`. Rebuilds still
   import `params` unless you knowingly point a session at the fork.
9. **Export** with design_tool module `3d` → open pack `3d/recipe.json` +
   `3d/README.md`. Apply presence post-pass when the sandbox disables units.
   Placement schema study is complete (hub planning-local); applicator
   deferred; **no** edge auto-router or invented millimetres. Do **not** adopt
   Three.js without a written decision in `STACK_3D_DECISION.md`.

---

## 6. Related docs

| Doc | Role |
|---|---|
| `AGENT_CAD_PROTOCOL.md` | Design-agnostic PFD→CAD agent protocol (pipeline source) |
| `STACK_3D_DECISION.md` | FreeCAD default; Three.js / matplotlib disposition |
| `FREECAD_PROTOCOL.md` | Binary, script template, failure modes |
| `REBUILD.md` | Hub master menu (AQS-REB-001) |
| `SCALE_MODEL.md` | What `SCALE_M` changes |
| `STL_MANIFEST.md` | OpenSCAD STL contract |
| `DESIGN_TOOL_ARCHITECTURE.md` | Phase D FreeCAD default; pack layout (§3.3) |
| *(hub planning only)* | Phase D plan **AQS-PLAN-3D-001** Rev G + placement study `planning/PLACEMENT_SCHEMA_STUDY.md` — not shipped here |
| `../models/REBUILD.sh` | Share-tree rebuild |
| `../models/freecad/graph_geometry_bridge.py` | Bridge (inventory + name map + overlay + presence + recipe 1.0) |
| `../models/freecad/params_overlay_apply.py` | Allow-list overlay → `params_overlay.py` fork |
| `../flow_graph/views/` | Primary published 2D diagrams |
| `../tables/` | materials.csv and BOM tables |
