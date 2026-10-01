# Master rebuild tool

Document number: AQS-REB-001  
Revision: C  
Date: 2026-10-01

| Rev | Change | Description | Date |
|---|---|---|---|
| — | — | Basic issue — hub `rebuild.py` menu | 2026-09-28 |
| A | — | Menu options 1–7 + share sync | 2026-09-28 |
| B | SCALE_M | Menu 8 / `--scale` — actual building size | 2026-09-28 |
| C | Share scrub | Document rebuild from this publish-tree layout | 2026-10-01 |

## 1. Purpose

Regenerate FreeCAD plant geometry, optional OpenSCAD STLs, and (from a
local working hub, not this repo) PFD sheets — then refresh this publish
tree.

**This repository** is the CERN-OHL-S publish tree. Day-to-day CAD editing
may live in a separate **local working hub** (not published). Commands
below prefer paths that exist **in this repo**.

## 2. SCALE_M — actual building size

**SCALE_M is not drawing/plot/PDF zoom.** It sizes the real building:
bay counts, plate L×W, cassette class, LIFE_LEVELS, BASEMENT_LEVELS
per `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001). Manufacturing baseline
`SCALE_M = 1.0` is **1 m : 1 m** (24 × 18 m plate).

| Value | Role |
|---|---|
| `1.0` | Manufacturing baseline (default on disk) |
| `2.0` | **Review-only** denser packing (more bays / life plates) |
| other `> 0` | Custom; see SCALE_MODEL derivation |

### Persistence (single source of truth)

In this tree:

```
models/freecad/params.py
```

Assignment line:

```python
SCALE_M = 1.0
```

`build_plant.py` imports this module. Changing SCALE_M **writes that line**,
then rebuild FreeCAD plant geometry so solids match the new footprints.

**WARNING**

`SCALE_M = 2.0` is review-only. Do not leave it as the manufacturing
default.

## 3. How to run (this repository)

```bash
cd models
bash REBUILD.sh            # FreeCAD plant via freecadcmd
bash REBUILD.sh --stls     # optional OpenSCAD STLs first
```

Plant only:

```bash
cd models/freecad
/usr/bin/freecadcmd build_plant.py
```

Optional OpenSCAD (when `openscad` is on PATH):

```bash
cd models/openscad/detail   # or the detail/ layout shipped here
bash build_stls.sh          # if present; see docs-authority/STL_MANIFEST.md
```

Flow-graph views:

```bash
cd flow_graph
python3 render_layer_views.py
```

## 4. Local working hub (optional; not in this repo)

Operators with a separate hub checkout may use a menu-driven `rebuild.py`
there (PFD groups, SCALE_M write, plant rebuild, sync into this publish
tree). That hub is **not published**. Do not hard-code workstation absolute
paths in this tree.

Typical hub menu actions (when present locally):

| # | Action |
|---|---|
| 1 | All PFDs |
| 2 | Electrical SLD only |
| 3 | FreeCAD plant — `/usr/bin/freecadcmd build_plant.py` |
| 4 | PFD groups |
| 5 | Sync publish tree |
| 6 | Everything safe — all PFDs + plant; optional share sync |
| 7 | List discovered scripts / groups |
| 8 | **Set SCALE_M** → write params.py → optional plant+PFDs |
| 0 | Quit |

## 5. FreeCAD binary

Use **only** `/usr/bin/freecadcmd` (apt 1.0). Not a mismatched AppImage
named `freecad`. See `docs-authority/FREECAD_PROTOCOL.md`.

## 6. Share sync

When using a local hub, sync copies hub → this publish tree. Includes the
current `params.py` (hence SCALE_M). Do not copy hub PFD PNGs into share.
Git commit/push remains a separate operator step.

## 7. Exit codes

Non-zero if any selected step fails. Each step prints the command used.

## 8. Related

| Doc | Role |
|---|---|
| `docs-authority/SCALE_MODEL.md` | AQS-SCALE-001 — what SCALE_M drives |
| `docs-authority/FREECAD_PROTOCOL.md` | FreeCAD 1.0 binary / template |
| `docs-authority/STL_MANIFEST.md` | OpenSCAD STL contract |
| `docs-authority/AUTHORITY.md` | CAD authority lock |
| `docs-authority/BUILD_3D_FROM_FLOW.md` | Graph → 3D honest path |

## OpenSCAD availability

If `openscad` is missing from PATH, see `docs-authority/STL_MANIFEST.md`.
Do not force an install from an unattended agent.
