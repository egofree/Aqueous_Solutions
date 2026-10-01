# Master rebuild tool

Document number: AQS-REB-001  
Revision: B  
Date: 2026-09-28

| Rev | Change | Description | Date |
|---|---|---|---|
| — | — | Basic issue — hub `rebuild.py` menu | 2026-09-28 |
| A | — | Menu options 1–7 + share sync | 2026-09-28 |
| B | SCALE_M | Menu 8 / `--scale` — actual building size | 2026-09-28 |

## 1. Purpose

One menu-driven entry point so the operator can regenerate PFDs, set
building scale, rebuild `plant.FCStd`, and refresh the publish tree.

Working hub:

```
/home/user/dev/Aqueous/Diagrams/aqueous_diagrams/
```

Publish tree:

```
/home/user/dev/Aqueous/share/aqueous-solutions/
```

## 2. SCALE_M — actual building size

**SCALE_M is not drawing/plot/PDF zoom.** It sizes the real building:
bay counts, plate L×W, cassette class, LIFE_LEVELS, BASEMENT_LEVELS
per `cad/SCALE_MODEL.md` (AQS-SCALE-001). Manufacturing baseline
`SCALE_M = 1.0` is **1 m : 1 m** (24 × 18 m plate).

| Value | Role |
|---|---|
| `1.0` | Manufacturing baseline (default on disk) |
| `2.0` | **Review-only** denser packing (more bays / life plates) — Mike |
| other `> 0` | Custom; see SCALE_MODEL derivation |

### Persistence (single source of truth)

```
/home/user/dev/Aqueous/Diagrams/aqueous_diagrams/cad/freecad/params.py
```

Assignment line:

```python
SCALE_M = 1.0
```

`build_plant.py` imports this module. Building / campus / mass-flow PFD
scripts reload the same file. Changing SCALE_M **writes that line**, then
optionally rebuilds FreeCAD plant geometry and scale-sensitive PFDs so
solids and sheets match the new footprints.

**WARNING**

`SCALE_M = 2.0` is review-only. Do not leave it as the manufacturing
default. The tool requires typing `YES` (menu) or `--force` (CLI).

## 3. How to run

```bash
cd /home/user/dev/Aqueous/Diagrams/aqueous_diagrams
python3 rebuild.py
```

```bash
python3 rebuild.py --list
python3 rebuild.py --all-pfds
python3 rebuild.py --sld
python3 rebuild.py --group power
python3 rebuild.py --plant
python3 rebuild.py --scale 1.0
python3 rebuild.py --scale 2.0 --force --apply   # review-only + rebuild
python3 rebuild.py --sync
python3 rebuild.py --everything --sync
```

Absolute path:

```
/home/user/dev/Aqueous/Diagrams/aqueous_diagrams/rebuild.py
```

`--apply` after `--scale` runs `/usr/bin/freecadcmd build_plant.py` and
regenerates group **scale** (building_stack, campus_life_hazard, mass_flow).

## 4. Menu

| # | Action |
|---|---|
| 1 | All PFDs |
| 2 | Electrical SLD only |
| 3 | FreeCAD plant — `/usr/bin/freecadcmd build_plant.py` |
| 4 | PFD groups: building, sector, water, power, cryo, mfg, fab, farm, core, scale |
| 5 | Sync `share/aqueous-solutions` |
| 6 | Everything safe — all PFDs + plant; optional share |
| 7 | List discovered scripts / groups |
| 8 | **Set SCALE_M** (1.0 / 2.0 review-only / custom) → write params.py → optional plant+PFDs |
| 0 | Quit |

## 5. FreeCAD binary

Use **only** `/usr/bin/freecadcmd` (apt 1.0). Not the 1.1.1 AppImage.
See `cad/FREECAD_PROTOCOL.md`.

Legacy OpenSCAD STL + plant: `bash cad/REBUILD.sh` (needs `openscad`).

## 6. Share sync

Option 5 copies hub → `share/aqueous-solutions/` and appends
`share/SHARE_BUILD_LOG.txt`. Includes the current `params.py` (hence
SCALE_M). No git.

## 7. Exit codes

Non-zero if any selected step fails. Each step prints the command used.

## 8. Related

| Doc | Role |
|---|---|
| `cad/SCALE_MODEL.md` | AQS-SCALE-001 — what SCALE_M drives |
| `cad/FREECAD_PROTOCOL.md` | FreeCAD 1.0 binary / template |
| `cad/STL_MANIFEST.md` | OpenSCAD STL contract |
| `cad/AUTHORITY.md` | CAD authority lock |

## OpenSCAD availability (Wave 2)

If `openscad` is missing from PATH, see `cad/STL_MANIFEST.md` operator
PATH note. Do not force an install from an unattended agent.

