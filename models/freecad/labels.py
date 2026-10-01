#!/usr/bin/env python3
"""Standing-height label plates and safety signs.

Face text comes from SIGN_LEGEND / LABEL_LEGEND (same strings as
SIGN_SCHEDULE.md). Safety-sign faces are four lines: ANSI/KSC signal
word, locked unit name, hazard short title, then short instruction.
Glyphs are cut with Part.makeWireString when Liberation Sans Bold is
installed. If no font is found the plate is blank and the schedule is
the readable source.

Font policy: Liberation Sans Bold only (OFL-1.1). See FONTS.md.
Do not fall back to DejaVu or FreeFont.

Glyph facing: plates have thickness in +Y (origin at the -Y corner).
  face="-Y" — readable standing on the -Y side (aisle / approach)
  face="+Y" — readable standing on the +Y side (north of tank)
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
    # (signal, unit_name, hazard, instruction) — four-line face layout
    "SIGN_OXIDIZER_LEACH": ("WARNING", "LEACH CSTR 1", "OXIDIZER", "SALRIA HCl + NaClO3"),
    "SIGN_ACID_GAS_LEACH": ("WARNING", "LEACH CSTR 1", "ACID GAS", "DO NOT OPEN LID"),
    "SIGN_H2_EW_AISLE": ("WARNING", "EW AISLE", "HYDROGEN", "NO IGNITION SOURCES"),
    "SIGN_H2_DRYER": ("WARNING", "DRYER", "HYDROGEN", "NO HOT WORK"),
    "SIGN_SPLASH_HARVEST": ("CAUTION", "EW HARVEST", "ACID SPLASH", "PAIL IN BUND ONLY"),
    "SIGN_CAUSTIC_BMED": ("WARNING", "NaOH PRODUCT", "CAUSTIC", "PP VESSEL ONLY"),
    "SIGN_CAUSTIC_DIGEST": ("WARNING", "NaOH DIGEST", "CAUSTIC", "80 C TO 90 C"),
    "SIGN_RAD_PK9": ("WARNING", "PK-9", "RADIOACTIVE", "SEALED LID ONLY"),
    "SIGN_HOT_PYRO": ("CAUTION", "INDUCTION PYROLYZER", "HOT SURFACE", "400 C TO 600 C"),
    "SIGN_NCG_AFTERBURNER": ("WARNING", "AFTERBURNER", "NCG / TAR", "FLUE TO ROTARY ONLY"),
    "SIGN_OIL_VAPOR": ("WARNING", "OIL LINE", "OIL VAPOR", "KEEP HEADERS APART"),
    "SIGN_HOT_ROTARY": ("CAUTION", "BURNOUT ROTARY", "HOT SURFACE", "450 C TO 550 C"),
    "SIGN_ARC_FLASH_RECTIFIER": ("WARNING", "RECTIFIER", "ARC FLASH", "DC BUS LIVE"),
    "SIGN_BR2_BATTERY": ("WARNING", "ZnBr2", "BROMINE", "BATTERY SCRUBBER ONLY"),
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


def _glyphs(text, size_mm, face="-Y"):
    """Extrude Liberation letter outlines for a plate face.

    makeWireString → wires in XY. Extrude +Z, rotate +90° about X so
    thickness lies in Y and letter height in Z.

    face="-Y": mirror in Y so the readable face looks toward -Y; thickness
    ends in [-2, 0]. Viewer standing in -Y looking +Y reads LTR in +X.
    face="+Y": also mirror in X so a viewer in +Y looking -Y reads LTR
    (their right is -X). Thickness stays in [0, 2].
    """
    font = font_path()
    if not font:
        return None
    try:
        raw = Part.makeWireString(str(text), font, float(size_mm), 0)
    except Exception as exc:
        print("makeWireString failed:", exc)
        return None
    chars = raw if isinstance(raw, (list, tuple)) else [raw]
    solids = []
    for char_wires in chars:
        try:
            wires = list(char_wires) if isinstance(char_wires, (list, tuple)) else [char_wires]
            if not wires:
                continue
            face_w = Part.Face(wires)
            ext = face_w.extrude(App.Vector(0, 0, 2))
            if ext is None or ext.isNull() or abs(ext.Volume) < 1e-6:
                continue
            ext.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
            # Thickness was -Y after rotate; shift to [0, 2] in +Y.
            ext.translate(App.Vector(0, 2, 0))
            solids.append(ext)
        except Exception as exc:
            print("glyph char failed:", exc)
            continue
    if not solids:
        return None
    out = solids[0]
    for s in solids[1:]:
        out = out.fuse(s)

    m = App.Matrix()
    if face == "-Y":
        # Flip to put readable face toward -Y; thickness → [-2, 0].
        m.scale(1, -1, 1)
        out = out.transformGeometry(m)
    else:
        # Viewer from +Y: flip X so text is not mirrored.
        m.scale(-1, 1, 1)
        out = out.transformGeometry(m)
        bb = out.BoundBox
        out.translate(App.Vector(-bb.XMin, 0, 0))
    return out


def _stamp(doc, parent_name, lines, x, y, z, width, height, size=28, face="-Y", thick=None):
    """Put lines on the ±Y face of a plate whose origin is (x,y,z).

    Four-line signs (signal, unit, hazard, instruction) scale as:
    signal = size, unit = 0.85*size, hazard/instruction = 0.65*size.
    Cursor steps by each line's own size so all four fit on SIGN_H.
    """
    font = font_path()
    if not font:
        print("no TTF; %s legend is in SIGN_SCHEDULE.md" % parent_name)
        return
    if thick is None:
        thick = P.SIGN_T
    cursor = height - size - 16
    for i, line in enumerate(lines):
        if i == 0:
            line_size = size
        elif i == 1:
            line_size = size * 0.85
        else:
            line_size = size * 0.65
        g = _glyphs(line, line_size, face=face)
        if g is None:
            continue
        if face == "-Y":
            # Glyph Y in [-2, 0]; sit just proud of plate -Y face at y.
            g.translate(App.Vector(x + 16, y - 0.5, z + cursor))
        else:
            # Glyph Y in [0, 2]; sit proud of plate +Y face at y+thick.
            g.translate(App.Vector(x + 16, y + thick + 0.5, z + cursor))
        add(doc, parent_name + "_L%d" % i, g)
        cursor -= line_size + 8


def label_plate(doc, unit, x, y, z=None, text=None, face="+Y"):
    z = P.LBL_Z if z is None else z
    plate = add(doc, "LBL_" + unit, box_at(x, y, z, P.LBL_L, P.LBL_T, P.LBL_H))
    legend = text or LABEL_LEGEND.get(unit, unit.replace("_", " "))
    _stamp(
        doc, "LBL_" + unit, (legend,), x, y, z, P.LBL_L, P.LBL_H,
        size=22, face=face, thick=P.LBL_T,
    )
    return plate


def leader(doc, name, from_xyz, to_xyz, shaft_d=16, cone_len=50, cone_d=36):
    """Shaft + arrowhead from sign toward equipment (Part only, no Draft).

    Shaft diameter ~12–20 mm, cone ~40–60 mm long — visible at plant scale.
    Tip of the cone sits at to_xyz.
    """
    start = App.Vector(float(from_xyz[0]), float(from_xyz[1]), float(from_xyz[2]))
    end = App.Vector(float(to_xyz[0]), float(to_xyz[1]), float(to_xyz[2]))
    vec = end.sub(start)
    length = vec.Length
    if length < 10:
        return None
    direction = App.Vector(vec)
    direction.normalize()
    shaft_len = max(length - cone_len, 1.0)
    shaft = Part.makeCylinder(shaft_d / 2.0, shaft_len, start, direction)
    cone_base = App.Vector(
        start.x + direction.x * shaft_len,
        start.y + direction.y * shaft_len,
        start.z + direction.z * shaft_len,
    )
    cone = Part.makeCone(cone_d / 2.0, 0.1, cone_len, cone_base, direction)
    return add(doc, name, shaft.fuse(cone))


def sign(doc, name, x, y, z=None, face="-Y", to=None):
    z = P.SIGN_Z if z is None else z
    plate = add(doc, name, box_at(x, y, z, P.SIGN_L, P.SIGN_T, P.SIGN_H))
    lines = SIGN_LEGEND.get(name, (name.replace("_", " "),))
    _stamp(
        doc, name, lines, x, y, z, P.SIGN_L, P.SIGN_H,
        size=32, face=face, thick=P.SIGN_T,
    )
    if to is not None:
        # Plate mid-face toward the unit; leader named SIGN_*_ARROW.
        from_pt = (x + P.SIGN_L / 2.0, y + P.SIGN_T / 2.0, z + P.SIGN_H / 2.0)
        leader(doc, name + "_ARROW", from_pt, to)
    return plate


def wet_signs(doc):
    t = P.WALL
    cstr_to = (t + P.CSTR_L / 2.0, t + P.CSTR_W / 2.0, P.CSTR_H / 2.0)
    # South of CSTR (−Y approach): readable from −Y.
    sign(doc, "SIGN_OXIDIZER_LEACH", t + P.CSTR_L / 2, -600, face="-Y", to=cstr_to)
    sign(doc, "SIGN_ACID_GAS_LEACH", t + P.CSTR_L * 0.75, -600, face="-Y", to=cstr_to)
    # EW / polish aisle: plates sit south of the path; aisle is +Y of plate → face="+Y".
    ew5_to = (
        P.AISLE_X0 + 4 * P.EW_PITCH + P.EW_L / 2.0,
        P.AISLE_Y + P.EW_W / 2.0,
        P.AISLE_Z + P.EW_H / 2.0,
    )
    sign(doc, "SIGN_H2_EW_AISLE", P.AISLE_X0 + 4 * P.EW_PITCH, P.AISLE_Y - 700,
         face="+Y", to=ew5_to)
    harvest_to = (
        P.AISLE_X0 + 8 * P.EW_PITCH + P.EW_L / 2.0,
        P.AISLE_Y + P.EW_W / 2.0,
        P.AISLE_Z + P.EW_FUNNEL_H,
    )
    sign(doc, "SIGN_SPLASH_HARVEST", P.AISLE_X0 + 9 * P.EW_PITCH + 200, P.AISLE_Y - 700,
         face="+Y", to=harvest_to)
    # PK-9 (authoritative — not wet_products.build): south of polish bank, aisle-readable.
    pk_x = P.AISLE_X0 + 9 * P.EW_PITCH + 400 + 8 * P.PK_PITCH
    pk_y = P.AISLE_Y - (P.EW_W + 2 * t) - 800
    pk9_to = (pk_x + P.EW_L / 2.0, pk_y + P.EW_W / 2.0, P.AISLE_Z + P.EW_H / 2.0)
    sign(doc, "SIGN_RAD_PK9", pk_x, pk_y - 400, face="+Y", to=pk9_to)
    # North of wet line (+Y): readable from +Y → NaOH PRODUCT / BMED.
    bx = 200
    by = P.CSTR_W + 2 * t + 500
    naoh_to = (bx + P.BMED_L + 100 + P.TOTE_L / 2.0, by + P.TOTE_W / 2.0, P.TOTE_H / 2.0)
    sign(doc, "SIGN_CAUSTIC_BMED", 200, P.CSTR_W + 2 * t + 200, face="+Y", to=naoh_to)


def wet_labels(doc):
    t = P.WALL
    # North of CSTR (+Y).
    label_plate(doc, "LEACH_CSTR_1", t + 80, t + P.CSTR_W + 80, face="+Y")
    label_plate(doc, "HOPPER_SHREDDER", -P.MEZZ_L + 80, t + P.CSTR_W + 80, face="+Y")
    label_plate(doc, "FLOAT_DEWATER", t + P.CSTR_L + 400, t + P.CSTR_W + 80, face="+Y")
    # South of split (−Y).
    label_plate(doc, "VIBRATORY_SPLIT", t + P.CSTR_L + 800, t - 400, face="-Y")
    for i, metal in enumerate(P.EW_METALS):
        label_plate(
            doc, "EW_%d_%s" % (i + 1, metal),
            P.AISLE_X0 + i * P.EW_PITCH,
            P.AISLE_Y - 200,
            text="EW-%d %s" % (i + 1, metal),
            face="-Y",
        )


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    doc = App.newDocument("LABELS")
    wet_labels(doc)
    wet_signs(doc)
    print("font:", font_path() or "NONE — install fonts-liberation")
    doc.saveAs(str(OUT / "labels.FCStd"))
    print("wrote", OUT / "labels.FCStd")
