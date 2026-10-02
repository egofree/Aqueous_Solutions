# aqueous-solutions (share / publish tree)

CERN-OHL-S-2.0 publish layout for the Aqueous closed-loop recycling plant
CAD, PFDs, ISO sheets, and authority docs.

This repository is the **CERN-OHL-S publish tree**: CAD, flow graph,
design-tool source, ISO sheets, and authority docs intended for sharing.

Active day-to-day editing may happen in a separate local working hub; refresh
this tree from that hub before each publish. Absolute workstation paths and
offline archives are intentionally omitted here.

## Layout

```
README.md LICENSE .gitignore .gitattributes DEPENDENCIES.md
docs-authority/     # cad/*.md authority + hub process docs (no Odysseus)
models/freecad/     # *.py builders, *.FCStd, *.step
models/openscad/    # root + detail/ + foam_ew/ *.scad
models/export/      # *.stl (root + detail/; no *.log)
iso/                # AQS-ISO-*.png + iso_fab_drawings.pdf
flow_graph/         # plant flow graph schema, JSON, views/, derived/, tests
  exporters/matplotlib/  # optional legacy PFD/SLD generators (PNGs not shipped)
design_tool/        # aqs_design_tool + web source (no node_modules/dist/sandbox)
tables/             # BOM / materials / shopping lists
media/              # animation stills (D0–D6, F0) + plant_phase_d.mp4 + logo3.png
```

## Doc authority

In this tree, **only `docs-authority/` holds** `SIGN_SCHEDULE.md`,
`SYSTEM_MODEL_PLAN.md`, `FREECAD_PROTOCOL.md`, `AGENT_CAD_PROTOCOL.md`,
and other cad-authority markdown. Hub-root duplicates are not copied here;
cad/ wins.

See `docs-authority/AUTHORITY.md` and `docs-authority/SCALE_MODEL.md`.

## Scale: plant.FCStd is SCALE_M=1.0 (M1 baseline)

On-disk `models/freecad/plant.FCStd` is built and saved at **`SCALE_M = 1.0`**
(4×3 bays / M1 / one life plate / one basement). Driver:

```python
# models/freecad/params.py
SCALE_M = 1.0
```

`SCALE_M = 2.0` was a review-only pass; restore to 2 only for intentional
review rebuilds. Rules: `docs-authority/SCALE_MODEL.md` §7–§8.

## Building 3D models from the plant flow graph

See **`docs-authority/BUILD_3D_FROM_FLOW.md`** (end-to-end rebuild) and
**`docs-authority/STACK_3D_DECISION.md`** (FreeCAD default; Three.js gated).
Pipeline protocol: **`docs-authority/AGENT_CAD_PROTOCOL.md`**.

### Status and limitations

| Path | Behaviour |
|---|---|
| **Baseline rebuild** | FreeCAD builders read `models/freecad/params.py` via `models/REBUILD.sh` (FreeCAD 1.0; `SCALE_M=1.0`). |
| **Graph → placement** | Export-pack `flow_graph_snapshot.json` does **not** drive FreeCAD placement or vessel millimetres. Bridge: `models/freecad/graph_geometry_bridge.py` (inventory, name map, overlay fork, presence filter, pack recipe). |
| **2D primary** | `flow_graph/views/*.svg`. Matplotlib PNGs are optional exporters, not authority, and are not shipped. |
| **3D stack** | FreeCAD rebuild remains the default. Three.js only with a later written decision revising `STACK_3D_DECISION.md`. |

```bash
cd models && bash REBUILD.sh
cd freecad && python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json
```

## How to rebuild

Doc: `docs-authority/REBUILD.md` (AQS-REB-001).  
`SCALE_M` in `models/freecad/params.py` = **actual building size** (not plot zoom). Manufacturing `1.0`; `2.0` review-only.

**From this repository:**

```bash
cd models
bash REBUILD.sh            # path shims + freecadcmd build_plant.py
bash REBUILD.sh --stls     # optional OpenSCAD first (openscad on PATH)
```

Plant only (FreeCAD 1.0):

```bash
cd models/freecad && /usr/bin/freecadcmd build_plant.py
```

Primary diagrams are **`flow_graph/views/*.svg`** (graph-driven).
Matplotlib PFD/SLD generators are optional under
`flow_graph/exporters/matplotlib/` — **PNGs are not shipped** in this tree.
Optional local PNG regenerate writes next to those scripts; do not commit PNGs.

A separate local working hub (not in this repo) may hold day-to-day CAD edits
and bridged PNG working copies. Refresh this publish tree from that hub before
sharing; do **not** copy hub PFD PNGs into this tree.

Layout mapping when adapting scripts from a local hub:

| Hub-style path | This repo |
|---|---|
| `cad/freecad/` | `models/freecad/` |
| `cad/*.scad`, `cad/detail/`, `cad/foam_ew/` | `models/openscad/` |
| `cad/export/`, `cad/detail/stl/` | `models/export/` |
| `cad/iso/` | `iso/` |
| `pfd_scripts/` | `flow_graph/exporters/matplotlib/` (scripts only; PNGs not shipped) |
| hub `*_pfd.png` / SLD | **not published** |
| `cad/*.md` | `docs-authority/` |
| `cad/animation/`, `cad/freecad/animation/` | `media/` |
| `flow_graph/` | `flow_graph/` |
| `design_tool/` (src only) | `design_tool/` |

## flow_graph + design_tool (v1 source)

Ship **source only** in this share tree. Odysseus planning and local
`planning/` audits are **not** published here.

**flow_graph** (authority-adjacent plant graph):

```bash
cd flow_graph
# schema + plant_flow_graph.json + views/ + derived/
python3 -m pytest test_authority_contract.py   # or: python3 check_authority_contract.py
```

**design_tool** (MVS sandbox UI — contributors rebuild deps locally):

```bash
cd design_tool
python3 -m pip install -r requirements.txt
# API (from design_tool/; needs hub or local flow_graph paths per README)
python3 -m aqs_design_tool
cd web && npm ci && npm run dev
```

Do not commit `web/node_modules/`, `web/dist/`, `.sandbox_store/`, or `exports/sbx_*`
(ignored). Keep `exports/README.md` only.

## Git / LFS

- `*.FCStd` and `*.stl` → Git LFS (see `.gitattributes`)
- Ignored: `__pycache__`, `*.log`, `*.FCBak`, `.omo`, `node_modules`, `dist`, `.sandbox_store`, `exports/sbx_*`, `ODYSSEUS*`, `planning/`, `archive/`, `*.zip`

## External open-source dependencies

Aqueous links to external open-source projects for design reference only:
[Precious Plastic](https://preciousplastic.com/) (MFG polymer line),
[SEM-Tech / open-sourced off-the-shelf ion-exchange membrane](https://github.com/egofree/Open-sourced-off-the-shelf-ion-exchange-membrane)
(wet-line and BMED / MeOH IEM), and the
[Civilization Starter Kit](https://github.com/OpenSourceEcology/Civilization-Starter-Kit)
(OSE GVCS machine catalogue). See [`DEPENDENCIES.md`](DEPENDENCIES.md) for
roles, licenses, upstream provenance, and the explicit **not bundled — link
only** boundary. CSK → Aqueous sector/unit inventory:
[`docs-authority/OSE_CSK_ALIGNMENT.md`](docs-authority/OSE_CSK_ALIGNMENT.md).

## Related projects / Upstream references

| Project | Role |
|---|---|
| [Precious Plastic](https://preciousplastic.com/) | MFG plastic-recycling machine and workspace reference |
| [SEM-Tech / open IEM](https://github.com/egofree/Open-sourced-off-the-shelf-ion-exchange-membrane) | Wet-line and MeOH IEM fabrication reference |
| [Civilization Starter Kit](https://github.com/OpenSourceEcology/Civilization-Starter-Kit) | OSE Global Village Construction Set documentation: modular DIY blueprints for 50 industrial machines (code GPLv3; other content CC-BY-SA). Alignment map: [`OSE_CSK_ALIGNMENT.md`](docs-authority/OSE_CSK_ALIGNMENT.md). |

Full attribution and license notes: [`DEPENDENCIES.md`](DEPENDENCIES.md).

## Licence

CERN-OHL-S-2.0 — see `LICENSE`.
