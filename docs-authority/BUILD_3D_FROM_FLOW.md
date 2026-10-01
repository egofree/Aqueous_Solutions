# Build 3D models from flow diagrams / design packs

Document number: **AQS-3D-BUILD-001**  
Revision: **B**  
Date: 2026-10-01  
Licence: CERN-OHL-S-2.0  
Audience: Outsiders using the published `aqueous-solutions` tree  
Authority: Aligns with `AGENT_CAD_PROTOCOL.md` (design-agnostic pipeline) and
`STACK_3D_DECISION.md` (FreeCAD bias). Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | First issue | Present path + honest gap + stub | 2026-10-01 |
| B | Protocol align | End-to-end mapped to AGENT_CAD_PROTOCOL; stack pointer; share paths; flow_graph views primary 2D | 2026-10-01 |

---

## 0. Honest status (read first)

| Path | What it does today |
|---|---|
| **Present (wired)** | FreeCAD builders read **`models/freecad/params.py`** (and OpenSCAD `params.scad`) and write **`plant.FCStd`**. Geometry is **not** driven by the flow graph. |
| **Study / Phase D** | Design-tool export packs include `flow_graph_snapshot.json` + `params.json` (overlay). Module **`3d` is deferred**. No script places FreeCAD solids from graph nodes/edges. |
| **Bias** | FreeCAD 1.0 rebuild (`/usr/bin/freecadcmd`). **Three.js** (or live browser mesh) only with a **later written decision** — see `STACK_3D_DECISION.md`. |

**Graph → geometry is not wired.** If you exported a custom design pack
expecting “press button → 3D of *my* topology,” that bridge is **not
implemented**. You can still rebuild the **baseline M1 plant** shipped
here, and use the stub bridge to inventory your graph against that
baseline.

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
| Graph → place/size solids | — | **Not wired** (Phase D) |

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
| Python 3 | For the stub bridge and (on hub) design_tool |

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

### 3.1 Share path map (important)

| Need | Share path |
|---|---|
| Rebuild entry | `models/REBUILD.sh` |
| FreeCAD builders + `params.py` | `models/freecad/` |
| OpenSCAD sources | `models/openscad/` |
| Compiled STLs | `models/export/` (incl. `detail/`) |
| Materials CSV | `tables/materials.csv` (REBUILD.sh links into `models/`) |
| Typed graph | `flow_graph/plant_flow_graph.json` |
| Primary 2D views | `flow_graph/views/*.svg` |
| Stub graph inventory | `models/freecad/graph_geometry_bridge.py` |

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

**Hub operators** continue to use `Diagrams/aqueous_diagrams/rebuild.py`
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
Part placement. That gap is intentional until Phase D ships.

### 4.2 Design-tool export pack (from your design)

Typical pack always includes:

| File | Role for 3D |
|---|---|
| `flow_graph_snapshot.json` | Frozen graph for the sandbox — **input to stub**, not to builders |
| `params.json` | Study overlay (`scale_m`, electrical counts). **Does not rewrite `params.py`** |
| `mvs_snapshot.json` / `design.json` | MVS projection / sandbox — not solids |
| `pfd/` / `sld` / `bom` (if requested) | 2D / tables — WP-C1 |
| `3d/` | **Not emitted** — Phase D deferred |

### 4.3 Stub: inventory your graph against the CAD baseline

```bash
cd models/freecad
python3 graph_geometry_bridge.py \
  --graph ../../flow_graph/plant_flow_graph.json

# or against an export pack snapshot:
python3 graph_geometry_bridge.py \
  --graph /path/to/export/flow_graph_snapshot.json \
  --params /path/to/export/params.json \
  --out /tmp/3d_recipe.json
```

What the stub **does**:

- Lists units by `sector_id` / `enabled`
- Notes pack `scale_m` vs on-disk `SCALE_M`
- Writes a **recipe JSON** describing the *future* bridge contract

What it **does not** do:

- Resize tanks from rates
- Hide units with `enabled=false` in FreeCAD
- Auto-layout from edges
- Call Three.js
- Rewrite `params.py` from pack overlay

Optional: rebuild baseline solids after inventory (still params-driven):

```bash
python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json \
  --rebuild-baseline
```

---

## 5. Outsider checklist (end-to-end)

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
8. **Manually** align `SCALE_M` / module counts in `params.py` only if you
   knowingly fork the baseline (keep a copy; do not pretend the overlay
   auto-applied).
9. Treat full **graph→geometry** as Phase D study until pack module `3d`
   ships. Do **not** adopt Three.js without a written decision in
   `STACK_3D_DECISION.md`.

---

## 6. Related docs

| Doc | Role |
|---|---|
| `AGENT_CAD_PROTOCOL.md` | Design-agnostic PFD→CAD agent protocol (pipeline source) |
| `STACK_3D_DECISION.md` | FreeCAD bias; Three.js / matplotlib disposition |
| `FREECAD_PROTOCOL.md` | Binary, script template, failure modes |
| `REBUILD.md` | Hub master menu (AQS-REB-001) |
| `SCALE_MODEL.md` | What `SCALE_M` changes |
| `STL_MANIFEST.md` | OpenSCAD STL contract |
| `DESIGN_TOOL_ARCHITECTURE.md` | Phase D FreeCAD bias; pack layout (§3.3) |
| `../models/REBUILD.sh` | Share-tree rebuild |
| `../models/freecad/graph_geometry_bridge.py` | Stub bridge (inventory only) |
| `../flow_graph/views/` | Primary published 2D diagrams |
| `../tables/` | materials.csv and BOM tables |
