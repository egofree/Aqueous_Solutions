# 2026-10-29 — BUILD_3D: the build-out units join the FreeCAD plant; the rebuild works again

## What changed

**The plant rebuild was broken**: `fire_barriers._rated_rooms` crashed with
`width of box too small` on every run since 2026-10-19 (the committed
`plant.FCStd` predates this fix and every rebuild since then silently died —
freecadcmd exits 0 on script exceptions, so `models/REBUILD.sh` reported
success). The cause: opposite-side boundary clips (a stair and its door) can
squeeze a fire room's rectangle inside out, and the wall builder then received
a negative width. The fix surfaces the conflict instead of crashing: the room
is skipped, named on the build log, and recorded in
`docs-authority/inventory/CAD_ROOM_FINDINGS.json` (one run's findings, never
accreted). Two pre-existing conflicts now show as GA findings:

- `FR_OIL_PYRO` — clipped to −20 mm between `STAIR_SERVICE` and
  `STAIR_SERVICE_DOOR_Lm1` on L-1;
- `FR_AFTERBURNER` — room band 250 mm deep, thinner than two 150 mm walls.

Both need a layout decision (move the room origin or the stair pair); that is
recorded, not silently redesigned.

**The X-FARM / X-POLY / X-UI-002 units join the CAD model** (dims read from
the graph at build time — flat `params.size_mm` or `params.envelope.size_mm` —
never re-typed in the builders):

| Units | Builder | Placement |
|---|---|---|
| FEED_PREP, AQUA_UV, CHICKEN_COOP, QUAIL_CAGE, RABBIT_HUTCH, BEE_HIVE, VERMI_BIN, BSFL_BIN, DUCK_PEN | `models/freecad/farm.py` | farm plate free floor: feed-formulation row west, animal rows, manure row; AQUA_UV sits in the BIOFILTER→grow-bed loop pocket (A-M-424) |
| DUCKWEED | `models/freecad/farm.py` | scale-guarded: the 30.1 × 10.1 m raceway does not fit the M1 plate; the builder emits it at the scale that fits it |
| MET_SYN, GW_INTAKE | `models/freecad/d1b_massing.py` | MET_SYN east of MEOH_TANK in the L0 yard row (bench envelope from the X-SPEC sizing, A-M-416 route A); GW_INTAKE wellhead pad south of the row (X-LOC-13) |
| POLY_FIBER | `models/freecad/mfg_shop.py` | MFG floor, first cassette (A-M-429); the CadQuery machine model follows at its unit task — no cadquery interpreter on this host (installed 2.8.0 for `flow_graph.param.envelopes`) |

`flow_graph/param/specialty_sizing.py` now writes MET_SYN's
`params.size_mm` (bench fume-hood train, 1500 × 1000 × 1800 mm; the 9 g/d
DL-Met duty sets nothing larger). `models/freecad/unit_freecad_map.json` is
Rev E with the 13 entries above.

## Verification

- `python3 -m flow_graph.param.regen` green; `pytest flow_graph/` 204 passed /
  1 skipped (including the X-PAR-04 envelope-bbox gate: `cad/stl/MET_SYN.stl`
  generated and matches the graph size within 1 mm).
- `bash models/REBUILD.sh`: plant builds and saves for the first time since
  2026-10-19 — 1179 objects, all 12 new units present by Name,
  `clash_equip` 0 clashes; `clash_check` reports 1 solid clash
  (`FR_H2O_ELYZ` room wall cuts its own unit — room-fitting artifact, now
  visible because the build works again; reported to GA_CHECK by
  `docs-authority/_cad_clash.py`).

## Open items

- FR_OIL_PYRO / FR_AFTERBURNER room squeeze: layout decision needed.
- FR_H2O_ELYZ self-clash: the room fit pass should keep the wall outside the
  unit it encloses.
- POLY_FIBER CadQuery machine model (mfg/polymers.py lane) at its unit task.
