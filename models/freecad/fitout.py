#!/usr/bin/env python3
"""Per-level fit-out massing — corridors, toilet rooms, lift lobbies, stair clearances.

    /usr/bin/freecadcmd fitout.py

IBC-accessible clear widths (ADA-minded): main corridor spine ≥ 1800 mm,
toilet room clear ≥ 1525 mm on the latch side approach, elevator lobby
clear ≥ 1500 × 1500 mm. Ratings between hab and process stay on FB_*/HA_*.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate

import FreeCAD as App

OUT = Path(__file__).resolve().parent

# Clear heights for fit-out solids (below next slab soffit).
H_Lm2 = 2800
H_Lm1 = 3200
H_L0 = 3200
H_L1 = 2800
H_L2 = 2400

CORR_W = 1800          # accessible corridor
TOILET_L, TOILET_W = 2200, 2000
LOBBY_L, LOBBY_W = 3200, 3000
STAIR_CLR = 200        # clearance pad beyond stair box


def _corr(doc, name, x, y, z, dx, dy, dz):
    add(doc, name, box_at(x, y, z, dx, dy, dz))
    label_plate(doc, name, x, y - 150, z=z + min(800, dz // 2))


def _level_spine(doc, tag, z, h):
    """E–W corridor south of CORE + N–S corridor west of CORE."""
    # E–W spine along Y = CORE_Y - CORR_W (south face of core bay)
    y_ew = P.CORE_Y - CORR_W
    _corr(doc, "CORR_%s_EW" % tag, 1000, y_ew, z, P.PLATE_L - 2000, CORR_W, h)
    # N–S spine along X = CORE_X - CORR_W (west face of core)
    x_ns = P.CORE_X - CORR_W
    _corr(doc, "CORR_%s_NS" % tag, x_ns, 1000, z, CORR_W, P.PLATE_W - 2000, h)


def _toilets(doc, tag, z, h):
    """Toilet rooms at NW (hab/secondary) and SE (farm/secondary) corners."""
    add(doc, "TOILET_%s_NW" % tag, box_at(
        400, P.PLATE_W - TOILET_W - 400, z, TOILET_L, TOILET_W, min(h, 2600)))
    label_plate(doc, "TOILET_%s_NW" % tag, 400, P.PLATE_W - TOILET_W - 550,
                z=z + 600)
    add(doc, "TOILET_%s_SE" % tag, box_at(
        P.PLATE_L - TOILET_L - 400, 400, z, TOILET_L, TOILET_W, min(h, 2600)))
    label_plate(doc, "TOILET_%s_SE" % tag, P.PLATE_L - TOILET_L - 400, 250,
                z=z + 600)


def _lift_lobby(doc, tag, z, h):
    """Freight elevator lobby on the west (life) side of ELEV_SVC."""
    # ELEV_SVC is at CORE_X+2600, CORE_Y+100 — lobby west of it toward CORE_LIFE
    lx = P.CORE_X + 200
    ly = P.CORE_Y + 100
    add(doc, "LOBBY_ELEV_%s" % tag, box_at(lx, ly, z, LOBBY_L, LOBBY_W, h))
    label_plate(doc, "LOBBY_ELEV_%s" % tag, lx, ly - 150, z=z + 600)


def _stair_clear(doc, tag, z, h):
    """Clearance pads at STAIR_S1 / STAIR_S2 landings (accessible approach)."""
    # STAIR_S1 NW at (200, PLATE_W-2600); pad to the south
    add(doc, "STAIR_CLR_%s_S1" % tag, box_at(
        200, P.PLATE_W - 2600 - STAIR_CLR - 1500, z,
        2400, 1500, min(h, 400)))
    # STAIR_S2 SE at (PLATE_L-2600, 200); pad to the north
    add(doc, "STAIR_CLR_%s_S2" % tag, box_at(
        P.PLATE_L - 2600, 200 + 2400, z,
        2400, 1500, min(h, 400)))


def _hab_partitions(doc):
    """Light internal partition stubs on L1 HAB (SLEEP / GALLEY / wet rooms)."""
    x, y, z = P.HAB_X, P.HAB_Y, P.Z_L1
    t = 100
    h = 2600
    # Corridor through hab (E–W at mid-Y of west half)
    _corr(doc, "CORR_L1_HAB", x + 200, y + 7000, z, P.HAB_L - 400, CORR_W, h)
    # Partition SLEEP | GALLEY
    add(doc, "PART_HAB_SLEEP_GALLEY", box_at(
        x + 3800, y + 200, z, t, 6000, h))
    label_plate(doc, "PART_HAB_SLEEP_GALLEY", x + 3800, y + 40, z=z + 600)
    # Wet-room bank (toilet + shower) near STAIR_S1 approach
    add(doc, "WETROOM_HAB_NW", box_at(
        x + 400, y + P.HAB_W - 4200, z, 3600, 2800, h))
    label_plate(doc, "WETROOM_HAB_NW", x + 400, y + P.HAB_W - 4350, z=z + 600)


def _farm_partitions(doc):
    """Light circulation stub on L1 FARM — service aisle west of grow beds."""
    x, y, z = P.FARM_X, P.FARM_Y, P.Z_L1
    h = 2800
    _corr(doc, "CORR_L1_FARM", x + 200, y + 7000, z, P.FARM_L - 400, CORR_W, h)
    add(doc, "PART_FARM_SERVICE", box_at(
        x + 5800, y + 200, z, 100, 6000, h))
    label_plate(doc, "PART_FARM_SERVICE", x + 5800, y + 40, z=z + 600)


def _process_corridor_lm1(doc):
    """L-1 process aisle corridor east of wet cassette toward CORE / CRYO."""
    z, h = P.Z_Lm1, H_Lm1
    # Spine between process (west) and CRYO (east), south of CORE
    _corr(doc, "CORR_Lm1_PROCESS", 2000, P.CORE_Y - CORR_W, z,
          P.CRYO_X - 2000 - 200, CORR_W, h)
    # Rated approach strip north of CRYO west wall (no process-air duct)
    add(doc, "CORR_Lm1_CRYO_APPROACH", box_at(
        P.CRYO_X - CORR_W - 200, P.CRYO_Y, z, CORR_W, P.CRYO_W, h))
    label_plate(doc, "CORR_Lm1_CRYO_APPROACH", P.CRYO_X - CORR_W - 200,
                P.CRYO_Y - 150, z=z + 600)


def attach(doc):
    # L-2 utility — corridor + maint stair clear only (no hab toilets)
    _level_spine(doc, "Lm2", P.Z_Lm2, H_Lm2)
    _lift_lobby(doc, "Lm2", P.Z_Lm2, H_Lm2)

    # L-1 basement process + CRYO
    _level_spine(doc, "Lm1", P.Z_Lm1, H_Lm1)
    _lift_lobby(doc, "Lm1", P.Z_Lm1, H_Lm1)
    _process_corridor_lm1(doc)
    # Operator toilet near STAIR_MAINT (not a hab exit)
    add(doc, "TOILET_Lm1_MAINT", box_at(
        P.CORE_X - TOILET_L - 200, P.CORE_Y + 5000, P.Z_Lm1,
        TOILET_L, TOILET_W, 2600))
    label_plate(doc, "TOILET_Lm1_MAINT", P.CORE_X - TOILET_L - 200,
                P.CORE_Y + 4850, z=P.Z_Lm1 + 600)

    # L0 grade — dock / shop / fab circulation
    _level_spine(doc, "L0", P.Z_L0, H_L0)
    _toilets(doc, "L0", P.Z_L0, H_L0)
    _lift_lobby(doc, "L0", P.Z_L0, H_L0)
    _stair_clear(doc, "L0", P.Z_L0, H_L0)

    # L1 life — hab + farm fit-out
    _toilets(doc, "L1", P.Z_L1, H_L1)
    _lift_lobby(doc, "L1", P.Z_L1, H_L1)
    _stair_clear(doc, "L1", P.Z_L1, H_L1)
    _hab_partitions(doc)
    _farm_partitions(doc)

    # L2 roof tank deck — maint corridor only
    _corr(doc, "CORR_L2_MAINT", 2000, P.CORE_Y - CORR_W, P.Z_L2,
          P.PLATE_L - 4000, CORR_W, H_L2)
    _lift_lobby(doc, "L2", P.Z_L2, H_L2)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("FITOUT")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "fitout.FCStd"))
    print("fit-out massing attached")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
