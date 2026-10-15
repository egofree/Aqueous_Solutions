"""Shared object classes for clash_equip.py and resolve_overlaps.py."""
import re
SK = ("LBL", "LABEL", "SIGN", "TXT", "SLAB", "GROUND", "HA_", "FB_", "FR_", "ENV_", "CLEAR_", "KO_", "CORR_", "LOBBY", "HDR_", "RACK_",
      "STAIR", "ELEV", "SHAFT", "DOCK", "YARD_", "OVERFLOW", "TERRACE", "ROOF", "ARRAY_ROOF", "GRID", "LEVEL", "CAMPUS", "SITE", "PLATE",
      "CORE", "MASSING_", "GH_", "GROW_TRAY", "LED_", "UTIL_ROUGH", "VJ_", "CATCH_TANK", "MEZZANINE", "SERVICE_", "TOILET", "WETROOM", "RAIL",
      "GND_", "TRAY_", "PV_ARRAY", "C29_RECYCLE", "HX7_FLUE", "SCRUBBER_TO", "LEACHATE_TO", "FINES_TO", "RINSE_TO", "OIL_LINE_STUB", "CRYO_EGRESS")
ENV = ("HABITATION", "FARM", "MFG_SHOP", "WAFER_FAB", "FAB_PREP", "MFG_FLOOR", "PROCESS_B", "SLEEP", "MFG_CRIB")
OBST = ("CORR_", "STAIR", "ELEV", "SHAFT", "FB_", "PART_", "TOILET", "LOBBY", "YARD_FENCE", "CATCH_TANK", "CRYO_EGRESS")
def _part(o):
    return hasattr(o, "Shape") and o.TypeId.startswith("Part::") and not o.Shape.isNull() and o.Shape.Volume > 1e6
def is_equipment(o):
    return _part(o) and not o.Label.upper().startswith(SK) and o.Label not in ENV and not re.match(r"^CRYO(_B\d+)?$", o.Label) and not o.Label.startswith("PART_")
def is_obstacle(o):
    return _part(o) and o.Label.startswith(OBST)
def on_site(N, M, plate):
    L, W = plate
    if M[0] < 0 or M[1] < 0 or M[3] > L or M[4] > W:  # yard / outside units stay outside the plate
        return not (N[0] < L and N[3] > 0 and N[1] < W and N[4] > 0) or (N[0] >= 0 and N[3] <= L and N[1] >= 0 and N[4] <= W)
    return N[0] >= 100 and N[1] >= 100 and N[3] <= L - 100 and N[4] <= W - 100
