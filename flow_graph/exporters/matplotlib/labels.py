#!/usr/bin/env python3
"""Standing-height label plates and safety signs.

Face text comes from SIGN_LEGEND / LABEL_LEGEND (same strings as
docs-authority/SIGN_SCHEDULE.md). Glyphs are cut with Part.makeWireString when a
sans-bold TTF exists. If no font is found the plate is blank and the
schedule is the readable source.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent

# Liberation Sans Bold only — FONTS.md / CERN-OHL-S + OFL policy.
FONTS = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

LABEL_LEGEND = {
    "LEACH_CSTR_1": "LEACH CSTR 1",
    "HOPPER_SHREDDER": "HOPPER / SHREDDER",
    "FLOAT_DEWATER": "FLOAT DEWATER",
    "VIBRATORY_SPLIT": "VIBRATORY SPLIT",
}

SIGN_LEGEND = {
    "SIGN_OXIDIZER_LEACH": ("WARNING", "OXIDIZER", "SALRIA HCl + NaClO3"),
    "SIGN_ACID_GAS_LEACH": ("WARNING", "ACID GAS", "DO NOT OPEN LID"),
    "SIGN_H2_EW_AISLE": ("WARNING", "HYDROGEN", "NO IGNITION SOURCES"),
    "SIGN_H2_DRYER": ("WARNING", "HYDROGEN", "NO HOT WORK"),
    "SIGN_SPLASH_HARVEST": ("CAUTION", "ACID SPLASH", "PAIL IN BUND ONLY"),
    "SIGN_CAUSTIC_BMED": ("WARNING", "CAUSTIC", "NaOH PRODUCT"),
    "SIGN_CAUSTIC_DIGEST": ("WARNING", "CAUSTIC", "80 C TO 90 C"),
    "SIGN_RAD_PK9": ("WARNING", "RADIOACTIVE", "SEALED LID ONLY"),
    "SIGN_HOT_PYRO": ("CAUTION", "HOT SURFACE", "400 C TO 600 C"),
    "SIGN_NCG_AFTERBURNER": ("WARNING", "NCG / TAR", "FLUE TO ROTARY ONLY"),
    "SIGN_OIL_VAPOR": ("WARNING", "OIL VAPOR", "KEEP HEADERS APART"),
    "SIGN_HOT_ROTARY": ("CAUTION", "HOT SURFACE", "450 C TO 550 C"),
    "SIGN_ARC_FLASH_RECTIFIER": ("WARNING", "ARC FLASH", "DC BUS LIVE"),
    "SIGN_BR2_BATTERY": ("WARNING", "BROMINE", "BATTERY SCRUBBER ONLY"),
}


def font_path():
    for p in FONTS:
        if Path(p).exists():
            return p
    return None


def box_at(x, y, z, dx, dy, dz):
    s = Part.makeBox(dx, dy, dz)
    s.translate(App.Vector(x, y, z))
    return s


def add(doc, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def _glyphs(text, size_mm):
    font = font_path()
    if not font:
        return None
    try:
        raw = Part.makeWireString(str(text), font, float(size_mm), 0)
    except Exception as exc:
        print("makeWireString failed:", exc)
        return None
    wires = raw if isinstance(raw, (list, tuple)) else [raw]
    solids = []
    for w in wires:
        try:
            face = Part.Face(w) if hasattr(w, "Wires") or w.ShapeType == "Wire" else None
            if face is None:
                shp = w if hasattr(w, "extrude") else Part.Compound(w)
                ext = shp.extrude(App.Vector(0, 2, 0))
            else:
                ext = face.extrude(App.Vector(0, 2, 0))
            if ext and not ext.isNull():
                solids.append(ext)
        except Exception:
            continue
    if not solids:
        return None
    out = solids[0]
    for s in solids[1:]:
        out = out.fuse(s)
    return out


def _stamp(doc, parent_name, lines, x, y, z, width, height, size=28):
    """Put lines on the +Y face of a plate whose origin is (x,y,z)."""
    font = font_path()
    if not font:
        print("no TTF; %s legend is in SIGN_SCHEDULE.md" % parent_name)
        return
    cursor = height - size - 16
    for i, line in enumerate(lines):
        g = _glyphs(line, size if i == 0 else size * 0.7)
        if g is None:
            continue
        g.translate(App.Vector(x + 16, y + P.SIGN_T + 0.5, z + cursor))
        add(doc, parent_name + "_L%d" % i, g)
        cursor -= size + 10


def label_plate(doc, unit, x, y, z=None, text=None):
    z = P.LBL_Z if z is None else z
    plate = add(doc, "LBL_" + unit, box_at(x, y, z, P.LBL_L, P.LBL_T, P.LBL_H))
    legend = text or LABEL_LEGEND.get(unit, unit.replace("_", " "))
    _stamp(doc, "LBL_" + unit, (legend,), x, y, z, P.LBL_L, P.LBL_H, size=22)
    return plate


def sign(doc, name, x, y, z=None):
    z = P.SIGN_Z if z is None else z
    plate = add(doc, name, box_at(x, y, z, P.SIGN_L, P.SIGN_T, P.SIGN_H))
    lines = SIGN_LEGEND.get(name, (name.replace("_", " "),))
    _stamp(doc, name, lines, x, y, z, P.SIGN_L, P.SIGN_H, size=32)
    return plate


def wet_signs(doc):
    t = P.WALL
    sign(doc, "SIGN_OXIDIZER_LEACH", t + P.CSTR_L / 2, -600)
    sign(doc, "SIGN_ACID_GAS_LEACH", t + P.CSTR_L * 0.75, -600)
    sign(doc, "SIGN_H2_EW_AISLE", P.AISLE_X0 + 4 * P.EW_PITCH, P.AISLE_Y - 700)
    sign(doc, "SIGN_SPLASH_HARVEST", P.AISLE_X0 + 9 * P.EW_PITCH + 200, P.AISLE_Y - 700)
    sign(doc, "SIGN_CAUSTIC_BMED", 200, P.CSTR_W + 2 * t + 200)
    sign(doc, "SIGN_RAD_PK9", P.AISLE_X0 + 9 * P.EW_PITCH + 200, P.AISLE_Y - 1600)


def wet_labels(doc):
    t = P.WALL
    label_plate(doc, "LEACH_CSTR_1", t + 80, t + P.CSTR_W + 80)
    label_plate(doc, "HOPPER_SHREDDER", -P.MEZZ_L + 80, t + P.CSTR_W + 80)
    label_plate(doc, "FLOAT_DEWATER", t + P.CSTR_L + 400, t + P.CSTR_W + 80)
    label_plate(doc, "VIBRATORY_SPLIT", t + P.CSTR_L + 800, t - 400)
    for i, metal in enumerate(P.EW_METALS):
        label_plate(
            doc, "EW_%d_%s" % (i + 1, metal),
            P.AISLE_X0 + i * P.EW_PITCH,
            P.AISLE_Y - 200,
            text="EW-%d %s" % (i + 1, metal),
        )


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    doc = App.newDocument("LABELS")
    wet_labels(doc)
    wet_signs(doc)
    print("font:", font_path() or "NONE — install fonts-liberation")
    doc.saveAs(str(OUT / "labels.FCStd"))
    print("wrote", OUT / "labels.FCStd")
