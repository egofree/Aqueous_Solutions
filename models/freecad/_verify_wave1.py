import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import FreeCAD as App
import params as P

plant = Path(__file__).resolve().parent / "plant.FCStd"
doc = App.openDocument(str(plant))
names = sorted({o.Name for o in doc.Objects})
checks = [
    "DOCK", "YARD_PAD", "BACKUP_GEN", "FUEL_CELL", "ZNBR2_BR2_REGEN",
    "COLD_BOX", "STIRLING_COLD_HEAD", "CRYO_AHU_COND", "CRYO_H2", "FLUE_CAP",
    "MET_MELT", "MET_AHU", "MET_SCRUB", "ACID_POLISH_SCRUB",
    "TERRACE_BED_S_1", "GROW_TRAY_1", "CRYO", "WAFER_FAB", "MFG_SHOP",
    "SERVICE_ENTRY",
]
out = []
out.append("VERIFY_START")
for c in checks:
    sample = [n for n in names if n == c or n.startswith(c + "_") or n.startswith(c)][:8]
    # tighter: exact or startswith c
    sample = [n for n in names if n == c or n.startswith(c)][:8]
    out.append("%s: %s" % (c, sample if sample else "MISSING"))
out.append("SCALE_M=%.1f FAB=%dx%d MFG=%dx%d CRYO=%dx%d DOCK_Y=%d CRYO_X=%d" % (
    P.SCALE_M, P.FAB_L, P.FAB_W, P.MFG_L, P.MFG_W, P.CRYO_L, P.CRYO_W, P.DOCK_Y, P.CRYO_X))
out.append("object_count=%d" % len(names))
out.append("VERIFY_END")
Path("/tmp/wave1_verify.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
App.closeDocument(doc.Name)
