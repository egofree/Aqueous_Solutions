# aqueous-solutions (share / publish tree)

CERN-OHL-S-2.0 publish layout for the Aqueous closed-loop recycling plant
CAD, PFDs, ISO sheets, and authority docs.

**Working CAD home (Mike opens this daily):**  
`/home/user/dev/Aqueous/Diagrams/aqueous_diagrams/`

This directory (`share/aqueous-solutions/`) is the **clean publish tree**.
It is a copy of share-worthy content, reorganized. Do not treat it as the
only copy of live CAD — edit in `aqueous_diagrams`, then refresh share when
ready to publish.

Offline / non-git bulk lives in `/home/user/dev/Aqueous/archive/` (not
tracked).

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

## 3D from flow graphs (honest)

Outsiders: see **`docs-authority/BUILD_3D_FROM_FLOW.md`** (end-to-end) and
**`docs-authority/STACK_3D_DECISION.md`** (FreeCAD bias; Three.js gated).
Pipeline protocol: **`docs-authority/AGENT_CAD_PROTOCOL.md`**.

- **Present path:** rebuild baseline plant from `models/freecad/params.py` via `models/REBUILD.sh` (FreeCAD 1.0 only; `SCALE_M=1.0`).
- **Not wired:** export-pack `flow_graph_snapshot.json` does **not** drive FreeCAD placement. Stub: `models/freecad/graph_geometry_bridge.py`.
- **2D primary:** `flow_graph/views/*.svg` (matplotlib PNGs optional, not authority, not shipped).
- Phase D bias remains FreeCAD rebuild; Three.js only with a **later written decision** revising `STACK_3D_DECISION.md`.

```bash
cd models && bash REBUILD.sh
cd freecad && python3 graph_geometry_bridge.py --graph ../../flow_graph/plant_flow_graph.json
```

## How to rebuild

**Master menu (hub):** `python3 /home/user/dev/Aqueous/Diagrams/aqueous_diagrams/rebuild.py`  
Doc: `docs-authority/REBUILD.md` (AQS-REB-001).  
`SCALE_M` in `models/freecad/params.py` = **actual building size** (not plot zoom). Manufacturing `1.0`; `2.0` review-only. Set via menu 8 / `--scale`.

**From this share tree** (outsiders):

```bash
cd models
bash REBUILD.sh            # path shims + freecadcmd build_plant.py
bash REBUILD.sh --stls     # optional OpenSCAD first
```

**From the working hub** (Mike / operators — paths match existing scripts):

```bash
cd /home/user/dev/Aqueous/Diagrams/aqueous_diagrams
# OpenSCAD STLs + FreeCAD plant (needs openscad on PATH, /usr/bin/freecadcmd 1.0)
bash cad/REBUILD.sh
# or plant only:
cd cad/freecad && /usr/bin/freecadcmd build_plant.py
```

Primary diagrams in share are **`flow_graph/views/*.svg`** (graph-driven).
Matplotlib PFD/SLD generators are optional under
`flow_graph/exporters/matplotlib/` — **PNGs are not shipped** in this tree
(Mike: `demote_drop_pngs`). Hub still holds working `pfd_scripts/` + PNGs.

```bash
# Hub (working CAD — leave untouched when refreshing share):
cd /home/user/dev/Aqueous/Diagrams/aqueous_diagrams/pfd_scripts
# e.g. python wet_line_factory_pfd.py
```

After a hub rebuild, refresh this share tree by re-copying changed
`*.FCStd` / STLs / docs / flow_graph views into the matching folders above.
Do **not** re-copy hub PFD PNGs into share.

Share-tree local paths (if you adapt scripts here):

| Hub path | Share path |
|---|---|
| `cad/freecad/` | `models/freecad/` |
| `cad/*.scad`, `cad/detail/`, `cad/foam_ew/` | `models/openscad/` |
| `cad/export/`, `cad/detail/stl/` | `models/export/` |
| `cad/iso/` | `iso/` |
| `pfd_scripts/` | `flow_graph/exporters/matplotlib/` (scripts only; PNGs not shipped) |
| hub `*_pfd.png` / SLD | **not copied** — stay on hub only |
| `cad/*.md` | `docs-authority/` |
| `cad/animation/`, `cad/freecad/animation/` | `media/` |
| `flow_graph/` | `flow_graph/` |
| `design_tool/` (src only) | `design_tool/` |

`docs-authority/REBUILD.sh` still assumes hub layout (`ROOT/cad/...`); use
the hub copy for operator rebuilds.

## flow_graph + design_tool (v1 source)

Ship **source only** in this share tree. Odysseus planning is **not** published
(hub `cad/ODYSSEUS_PLANNING.md` stays local). Repo-level `planning/` audits stay
on the Aqueous machine and are never copied here.

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

Local repo only until Mike asks to push.

- `*.FCStd` and `*.stl` → Git LFS (see `.gitattributes`)
- Ignored: `__pycache__`, `*.log`, `*.FCBak`, `.omo`, `node_modules`, `dist`, `.sandbox_store`, `exports/sbx_*`, `ODYSSEUS*`, `planning/`, `archive/`, `*.zip`

## External open-source dependencies

Aqueous links to two external open-source projects: [Precious Plastic](https://preciousplastic.com/) for the MFG plastic-recycling reference, and [SEM-Tech / the open-sourced off-the-shelf ion-exchange membrane](https://github.com/egofree/Open-sourced-off-the-shelf-ion-exchange-membrane) for wet-line and BMED membrane work. See [`DEPENDENCIES.md`](DEPENDENCIES.md) for roles, licenses, upstream provenance, and the explicit **not bundled — link only** boundary.

## Licence

CERN-OHL-S-2.0 — see `LICENSE`.
