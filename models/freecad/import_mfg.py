#!/usr/bin/env python3
"""Replace massing boxes with manufacturing STLs from models/openscad/detail/stl/.

    bash ../detail/build_stls.sh
    /usr/bin/freecadcmd import_mfg.py

Hides (does not delete) the stand-in Part features when the STL exists.
Missing STL is a skip. Re-run after adding STLs.
"""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import oil_line
import glass_line
import electrical_yard

import FreeCAD as App

OUT = Path(__file__).resolve().parent
STL = OUT.parent / "detail" / "stl"

HIDE = {
    "mfg_hopper.stl": ("HOPPER_SHREDDER",),
    "mfg_shredder.stl": ("HOPPER_SHREDDER",),
    "mfg_vibratory_conveyor.stl": ("VIBRATORY_CONVEYOR",),
    "mfg_leach_cstr.stl": (
        "LEACH_CSTR_1", "CSTR3_AUGER", "CSTR3_LIFT_TUBE",
        "MIXER", "LEACHATE_PUMP",
    ),
    "mfg_dewater.stl": ("FLOAT_DEWATER", "SINK_DEWATER"),
    "mfg_vibratory_split.stl": ("VIBRATORY_SPLIT",),
    "mfg_induction_pyrolyzer.stl": ("INDUCTION_PYROLYZER",),
    "mfg_dryer.stl": ("DRYER",),
    "mfg_quench.stl": ("QUENCH",),
    "mfg_fractionator.stl": ("FRACTIONATOR",),
    "mfg_afterburner.stl": ("AFTERBURNER",),
    "mfg_rinse.stl": ("RINSE_DEWATER",),
    "mfg_burnout_rotary.stl": ("BURNOUT_ROTARY",),
    "mfg_mill.stl": ("MILL",),
    "mfg_digest.stl": ("NaOH_DIGEST",),
    "mfg_electrical.stl": (
        "RECTIFIER", "ATS", "SOL_ARK_60K", "ZNBR2",
        "ZNBR2_POS_TANK", "ZNBR2_NEG_TANK", "ZNBR2_BR2_SCRUBBER",
    ),
    "mfg_baghouse.stl": ("BAGHOUSE",),
    "mfg_h2_dryer.stl": ("H2_DRYER", "H2_STACK"),
    "mfg_scrubber_train.stl": ("DEMISTER", "ALK_SCRUBBER", "FAN_STACK"),
    "mfg_harvest_vdf.stl": ("HARVEST_VACUUM_DRUM_FILTER",),
    "mfg_cru.stl": ("CRU",),
    "mfg_ew_fitout.stl": (),
    "mfg_ew_bund.stl": ("EW_BUND",),
    "mfg_melt.stl": ("MELT",),
    "mfg_precip.stl": ("P_Al", "P_Mg", "P_Ca"),
    "mfg_pipe_rack.stl": ("RACK_WET", "RACK_BMED", "RACK_OIL"),
    "mfg_cable_tray.stl": ("TRAY_EW", "TRAY_YARD", "GND_RING"),
    "mfg_fish_tank.stl": ("FISH_TANK",),
    "mfg_biofilter.stl": ("BIOFILTER",),
    "mfg_grow_bed.stl": ("GROW_BED",),
    "mfg_farm_sump.stl": ("FARM_SUMP",),
    "mfg_nutrient_dose.stl": ("NUTRIENT_DOSE",),
    "mfg_wet_bench.stl": ("WET_BENCH",),
    "mfg_etch_return.stl": ("ETCH_RETURN",),
    "mfg_hab_water.stl": ("HAB_WATER",),
    "mfg_hab_waste.stl": ("HAB_WASTE",),
    "mfg_cold_box.stl": ("COLD_BOX",),
    "mfg_life_rack.stl": ("RACK_LIFE_N", "RACK_LIFE_S", "RACK_LIFE_W", "RACK_LIFE_E"),
}


def _hide(doc, names):
    for name in names:
        obj = doc.getObject(name)
        if obj is None:
            continue
        try:
            if obj.ViewObject is not None:
                obj.ViewObject.Visibility = False
        except Exception:
            pass
        if not obj.Label.startswith("MASSING_"):
            obj.Label = "MASSING_" + obj.Label


def _mesh(doc, name, stl_name, x, y, z, rot_axis=None, rot_deg=0):
    path = STL / stl_name
    if not path.exists():
        print("skip (no stl)", path.name)
        return None
    import Mesh
    if doc.getObject(name):
        doc.removeObject(name)
    mobj = doc.addObject("Mesh::Feature", name)
    mobj.Mesh = Mesh.Mesh(str(path))
    if rot_axis and rot_deg:
        mobj.Placement.Rotation = App.Rotation(App.Vector(*rot_axis), rot_deg)
    mobj.Placement.Base = App.Vector(x, y, z)
    _hide(doc, HIDE.get(stl_name, ()))
    print("placed", name)
    return mobj


def attach(doc):
    """Process-aisle STLs in L-1 local coords (before cassette shift)."""
    t = P.WALL
    W = P.CSTR_W
    hx = -P.MEZZ_L + 80
    hy = t + (W - P.HOPPER_W) / 2
    hz = P.MEZZ_H + P.MEZZ_THK + P.SHRED_H
    sx = hx + (P.HOPPER_L - P.SHRED_L) / 2
    sy = t + (W - P.SHRED_W) / 2
    drop_y = t + (W - P.DROP_W) / 2
    drop_x = t + P.DROP_X
    conv_sx = sx + P.SHRED_L
    conv_sz = P.MEZZ_H + P.MEZZ_THK + 80

    _mesh(doc, "MFG_SHREDDER", "mfg_shredder.stl",
          sx, sy, P.MEZZ_H + P.MEZZ_THK)
    _mesh(doc, "MFG_HOPPER", "mfg_hopper.stl",
          sx + P.SHRED_L / 2, sy + P.SHRED_W / 2, hz)
    _mesh(doc, "MFG_CONVEYOR", "mfg_vibratory_conveyor.stl",
          conv_sx, drop_y + P.DROP_W / 2, conv_sz)
    _mesh(doc, "MFG_LID_COAMING", "mfg_lid_coaming.stl",
          drop_x, drop_y, P.FLOOR + P.CSTR_H + P.WALL)
    _mesh(doc, "MFG_LEACH_CSTR", "mfg_leach_cstr.stl", 0, 0, 0)
    _mesh(doc, "MFG_CSTR3_FLIGHT", "cstr3_flight.stl",
          t + 60, t + P.AUGER_OFFSET_Y, P.FLOOR + P.AUGER_TROUGH_H / 2,
          rot_axis=(0, 1, 0), rot_deg=90)

    weir_sx = t + P.CSTR_L + t + P.WEIR_LIP
    weir_sy = t + (W - P.WEIR_W) / 2
    weir_sz = P.FLOOR + P.WEIR_CREST - 20
    _mesh(doc, "MFG_FLOAT_DEWATER", "mfg_dewater.stl",
          weir_sx, weir_sy, weir_sz)

    ang = math.radians(P.AUGER_INCLINE)
    lift_ex = t + P.CSTR_L - 40 + P.AUGER_LIFT_L * math.cos(ang)
    lift_ez = P.FLOOR + P.AUGER_TROUGH_H / 2 + P.AUGER_LIFT_L * math.sin(ang)
    _mesh(doc, "MFG_SINK_DEWATER", "mfg_dewater.stl",
          lift_ex, t + P.AUGER_OFFSET_Y - P.SDEW_W / 2, lift_ez - 20)
    _mesh(doc, "MFG_SPLIT", "mfg_vibratory_split.stl",
          lift_ex + P.SDEW_L, t + P.AUGER_OFFSET_Y - P.SPLIT_W / 2, lift_ez - 20)

    _mesh(doc, "MFG_EW_BUND", "mfg_ew_bund.stl",
          P.AISLE_X0 - P.BUND_PAD, P.AISLE_Y - P.BUND_PAD,
          P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L - P.BUND_H)
    _mesh(doc, "MFG_VDF", "mfg_harvest_vdf.stl",
          P.AISLE_X0 + 9 * P.EW_PITCH + 200,
          P.AISLE_Y + (P.EW_W + 2 * t) / 2,
          P.AISLE_Z - P.EW_FUNNEL_H)
    _mesh(doc, "MFG_CEM_EW1", "cem_cassette.stl",
          P.AISLE_X0 + t + 8,
          P.AISLE_Y + t + P.EW_W / 2 - P.EW_SLOT / 2,
          P.AISLE_Z + t + 20)
    _mesh(doc, "MFG_VALVE_EW1", "funnel_valve.stl",
          P.AISLE_X0 + (P.EW_L + 2 * t) / 2,
          P.AISLE_Y + (P.EW_W + 2 * t) / 2,
          P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L)
    for i in range(9):
        _mesh(doc, "MFG_EW_FITOUT_%d" % (i + 1), "mfg_ew_fitout.stl",
              P.AISLE_X0 + t + i * P.EW_PITCH, P.AISLE_Y + t, P.AISLE_Z + t)
    pk_y = P.AISLE_Y - (P.EW_W + 2 * t) - 800
    pk_x0 = P.AISLE_X0 + 9 * P.EW_PITCH + 400
    for i, tag in enumerate(P.PK_TAGS):
        if tag in ("PK-4", "PK-5"):
            continue
        _mesh(doc, "MFG_%s_FITOUT" % tag.replace("-", "_"),
              "mfg_ew_fitout.stl",
              pk_x0 + i * P.PK_PITCH + t, pk_y + t, P.AISLE_Z + t)
    _mesh(doc, "MFG_CRU", "mfg_cru.stl",
          200 + P.BMED_L + 100, P.CSTR_W + 2 * t + 500 + P.BMED_W + 80, 0)

    px = P.AISLE_X0 + 9 * P.EW_PITCH + 400
    for i, tag in enumerate(("P_Al", "P_Mg", "P_Ca")):
        _mesh(doc, "MFG_" + tag, "mfg_precip.stl",
              px + i * P.P_PITCH, P.AISLE_Y, P.AISLE_Z)
    crib_x = P.AISLE_X0 + 9 * P.EW_PITCH + 1600
    _mesh(doc, "MFG_MELT", "mfg_melt.stl", crib_x + 1900, P.AISLE_Y, 0)
    _mesh(doc, "MFG_TOTES", "mfg_totes.stl",
          200 + P.BMED_L + 100, P.CSTR_W + 2 * t + 500, 0)
    _mesh(doc, "MFG_BMED_STACK", "mfg_bmed_stack.stl",
          220, P.CSTR_W + 2 * t + 520, 0)

    ox, oy, _ = oil_line.origin()
    _mesh(doc, "MFG_DRYER", "mfg_dryer.stl", ox, oy, 0)
    _mesh(doc, "MFG_PYRO", "mfg_induction_pyrolyzer.stl",
          ox + P.DRYER_L + 80, oy + P.DRYER_W / 2, 400)
    _mesh(doc, "MFG_QUENCH", "mfg_quench.stl",
          ox + P.DRYER_L + 80 + P.PYRO_L + 80, oy, 0)
    fx = ox + P.DRYER_L + 80 + P.PYRO_L + 80 + 900
    _mesh(doc, "MFG_FRACTIONATOR", "mfg_fractionator.stl",
          fx + P.FRAC_D / 2, oy + P.DRYER_W / 2, 0)
    _mesh(doc, "MFG_AFTERBURNER", "mfg_afterburner.stl",
          fx + 1200, oy + P.DRYER_W / 2, 0)

    gx, gy, _ = glass_line.origin()
    _mesh(doc, "MFG_RINSE", "mfg_rinse.stl", gx, gy, 0)
    _mesh(doc, "MFG_ROTARY", "mfg_burnout_rotary.stl",
          gx + P.RINSE_L + 80, gy + 300, 400)
    _mesh(doc, "MFG_MILL", "mfg_mill.stl",
          gx + P.RINSE_L + 80 + P.ROTARY_L + 80, gy, 0)
    _mesh(doc, "MFG_DIGEST", "mfg_digest.stl",
          gx + P.RINSE_L + 80 + P.ROTARY_L + 80 + P.MILL_L + 80, gy, 0)

    _mesh(doc, "MFG_SCRUBBER", "mfg_scrubber_train.stl",
          t + P.CSTR_L * 0.80, P.CSTR_W + 2 * t + 200, 0)
    _mesh(doc, "MFG_BAGHOUSE", "mfg_baghouse.stl",
          -P.MEZZ_L - 200, t + P.CSTR_W + 200, P.MEZZ_H)
    _mesh(doc, "MFG_H2_DRYER", "mfg_h2_dryer.stl",
          P.AISLE_X0 + 9 * P.EW_PITCH + 200,
          P.AISLE_Y + P.EW_W + 2 * t + 200, 400)

    _mesh(doc, "MFG_Q4", "mfg_q4_hvac.stl",
          200, P.CSTR_W + 2 * t + P.BMED_W + 700, 0)
    _mesh(doc, "MFG_GAS", "mfg_gas_handling.stl",
          t + P.CSTR_L * 0.80, P.CSTR_W + 2 * t + 2200, 0)
    _mesh(doc, "MFG_PIPE_RACK", "mfg_pipe_rack.stl",
          P.AISLE_X0, P.AISLE_Y + P.EW_W + 2 * t + 150, 0)
    _mesh(doc, "MFG_CABLE_TRAY", "mfg_cable_tray.stl",
          P.AISLE_X0, P.AISLE_Y + P.EW_W + 2 * t + 350, 0)



def attach_campus(doc):
    """Campus / life / cryo STLs in world coords (call AFTER cassette shift)."""
    _mesh(doc, "MFG_FISH_TANK", "mfg_fish_tank.stl",
          P.FARM_X + 200, P.FARM_Y + 200, P.FARM_Z)
    _mesh(doc, "MFG_BIOFILTER", "mfg_biofilter.stl",
          P.FARM_X + 3900, P.FARM_Y + 200, P.FARM_Z)
    _mesh(doc, "MFG_GROW_BED", "mfg_grow_bed.stl",
          P.FARM_X + 6100, P.FARM_Y + 200, P.FARM_Z)
    _mesh(doc, "MFG_FARM_SUMP", "mfg_farm_sump.stl",
          P.FARM_X + 200, P.FARM_Y + 3000, P.FARM_Z)
    _mesh(doc, "MFG_NUTRIENT_DOSE", "mfg_nutrient_dose.stl",
          P.FARM_X + 2900, P.FARM_Y + 3000, P.FARM_Z)
    _mesh(doc, "MFG_WET_BENCH", "mfg_wet_bench.stl",
          P.FAB_X + 2600, P.FAB_Y + 200, P.FAB_Z)
    _mesh(doc, "MFG_ETCH_RETURN", "mfg_etch_return.stl",
          P.FAB_X + 2600, P.FAB_Y + 3200, P.FAB_Z)
    _mesh(doc, "MFG_HAB_WATER", "mfg_hab_water.stl",
          P.HAB_X + 200, P.HAB_Y + 3200, P.HAB_Z)
    _mesh(doc, "MFG_HAB_WASTE", "mfg_hab_waste.stl",
          P.HAB_X + 2400, P.HAB_Y + 3200, P.HAB_Z)
    _mesh(doc, "MFG_COLD_BOX", "mfg_cold_box.stl",
          P.CRYO_X + 200, P.CRYO_Y + 200, P.CRYO_Z)
    _mesh(doc, "MFG_LIFE_RACK", "mfg_life_rack.stl",
          P.LIFE_RACK_X0, P.LIFE_RACK_N_Y, P.Z_L1)


def attach_electrical(doc):
    """Electrical / ZnBr2 STLs at grade outdoor yard (not cassette-shifted)."""
    ex, ey, ez = electrical_yard.origin()
    _mesh(doc, "MFG_ELECTRICAL", "mfg_electrical.stl", ex, ey, ez)
    _mesh(doc, "MFG_ZNBR2_IEM", "znbr2_iem.stl",
          ex + 40, ey + P.RECT_W + 220, ez + 400)
    _mesh(doc, "MFG_ZNBR2_SKID", "mfg_znbr2_skid.stl",
          ex, ey + P.RECT_W + 200, ez)


def build():
    plant = OUT / "plant.FCStd"
    if plant.exists():
        App.openDocument(str(plant))
    else:
        import build_plant as BP
        BP.build()
    doc = App.ActiveDocument
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "plant.FCStd"))
    print("wrote", OUT / "plant.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
