"""BLOW_MOLD manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 800 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 800 x 1600 mm, node size_mm ("L x W x H mm, issued envelope").
  The duty section 2 envelope line agrees with the node. A four-post guard frame
  on the base plate pins the registry box so the X-PAR-04 envelope registry reads
  the build.
- Machine per the node design block ("continuous-extrusion blow molder",
  Precious Plastic class; AQS-EQP-MFG-001; A-M-285): the melt path - extruder
  barrel, extrusion head and die - is 316L per duty section 3 (the wax melt is
  the wet service; CA 0 mm); the three issued drive groups are purchased
  envelopes per plan rule 6 with the node ratings - extruder drive 2.2 kW
  (extruder_kW), clamp unit 0.75 kW (BLOW-CLAMP-01, clamp_kW), air supply 0.75
  kW (BLOW-AIR-01, air_kW); the mold tool (BLOW-MOLD-TOOL-01) is the clamp
  platens and the mold-halves envelope. The article geometry is not named on
  the node, so the mold set is an envelope and the mold detail is a named hold
  (W12). Barrel and platen sizes are the layout choice (W12); the process
  figures 2.8 kg/h at 3.0 h/d on 8.407 kg/d wax feed are node figures.
- Guard and anchors: the four-post guard frame; 8 slab anchors in
  fasteners.csv. Scrap goes to OIL_FRAC (node design line).
- Nozzles: all rows of docs-authority/nozzles/BLOW_MOLD.csv drawn at tag,
  face, height and bore: N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is a schedule placeholder under the
  1600 box); N3 (C11-C18 to the mold) and N4 (blown parts) are `solids`
  transfer rows drawn DN15, bore not calculated (plan W4). Duty section 4:
  atmospheric joints are hose.
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 800 x 1600
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
_mach = DS.get("machine")
if isinstance(_mach, dict):            # builder-owned nesting from a previous pass
    DS = _mach
assert DS.get("machine") == "continuous-extrusion blow molder", "node design block changed"

T_BASE = 20.0                                              # base plate (layout, W12)
POST = 40.0                                                # guard frame section
MAT_WET = "316L"                                           # duty section 3 (wax melt path)
CA = materials.ca_for(MAT_WET)                             # 0.0, AQS-STD-001
RHO_WET = materials.density(MAT_WET)
RHO_CS = materials.density("CS")

BARREL_OD, BARREL_LEN = 60.0, 700.0                        # melt-path envelope (layout, W12)
BX0, BX1 = 80.0, 80.0 + BARREL_LEN                         # barrel x 80..780
BY, BZ = 400.0, 900.0                                      # barrel axis (y, z)
DIE = (BX1 - 40.0, BY - 45.0, BZ - 260.0, 80.0, 90.0, 260.0)   # head + downward die (316L)
PLATEN = (BX1 + 20.0, BY - 150.0, 520.0, 40.0, 300.0, 300.0)   # clamp platens (BLOW-CLAMP-01 zone)
MOLD = (BX1 + 60.0, BY - 110.0, 640.0, 140.0, 220.0, 160.0)    # mold-halves envelope (BLOW-MOLD-TOOL-01)
AIR = (BX1 + 40.0, BY + 170.0, 520.0, 220.0, 160.0, 200.0)     # BLOW-AIR-01 envelope (0.75 kW)
DRIVE = (BX0, BY - 90.0, BZ - 100.0, 120.0, 180.0, 200.0)      # extruder drive (2.2 kW)

assert L == 1200.0 and W == 800.0 and H == 1600.0, "BLOW_MOLD node envelope changed"
for (x, y, z, dx, dy, dz) in (DIE, PLATEN, MOLD, AIR, DRIVE):
    assert x >= 44.0 and x + dx <= L - 44.0 and y >= 44.0 and y + dy <= W - 44.0, "inside the guard"
    assert z >= T_BASE and z + dz <= H - POST - 40.0, "on the base, under the top rails"
assert BX1 < L - 44.0, "barrel inside the guard"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_x(od, x0, length, y, z):
    return (cq.Workplane("XY").circle(od / 2).extrude(length)
            .rotate((0, 0, 0), (0, 1, 0), 90)
            .translate((x0, y, z)))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- base plate + guard frame
parts["base"] = box(0, 0, 0, L, W, T_BASE)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- melt path (316L, duty section 3)
parts["barrel"] = tube_x(BARREL_OD, BX0, BARREL_LEN, BY, BZ)
parts["head_die"] = box(*DIE)

# ---------------------------------------------------------------- purchased drive envelopes (rule 6)
parts["drive"] = box(*DRIVE)                               # extruder drive, 2.2 kW
parts["clamp_platens"] = (box(*PLATEN)
                          .union(box(PLATEN[0] + 100.0, PLATEN[1],
                                     PLATEN[2], *PLATEN[3:])))   # BLOW-CLAMP-01 (0.75 kW)
parts["mold"] = box(*MOLD)                                 # BLOW-MOLD-TOOL-01 envelope
parts["air"] = box(*AIR)                                   # BLOW-AIR-01 envelope (0.75 kW)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    x = 600.0
    for r in rows:
        layout_x[r["tag"]] = round(x, 1)
        x += 60.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    if dnl == "cable":                                    # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
    note = "atmospheric hose joint per duty section 4"
    if r["face"] == "bottom":                             # N1: drain flush at the envelope bottom
        s = tube_z("DN15", T_BASE + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder")
    elif r["face"] == "top":                              # N2: 800 datum predates the 1600 box
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (770.0, W / 2), (L, W, H))
        note = ("vent flush at the envelope top; the schedule datum 800 mm "
                "predates the 1600 box (hold, WORK_ORDER W12)")
    else:                                                 # N3/N4: solids transfer rows
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, FACE_OF.get(r["face"], r["face"]), h,
                                  (layout_x[tag], W / 2), (L, W, H))
        note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                 "not calculated (plan W4)")
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": FACE_OF.get(r["face"], r["face"]),
                  "height_mm": h,
                  "drawn_height_mm": h if r["face"] in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- exports
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
_m = {"base": RHO_CS, "frame": RHO_CS, "barrel": RHO_WET, "head_die": RHO_WET,
      "drive": RHO_CS, "clamp_platens": RHO_CS, "mold": RHO_CS, "air": RHO_CS,
      "nozzles": RHO_WET}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "continuous-extrusion blow molder per the node design block "
                "(Precious Plastic class; AQS-EQP-MFG-001; A-M-285): 316L "
                "melt path (extruder barrel, extrusion head, downward die) "
                "per duty section 3, the three drive groups as purchased "
                "envelopes per plan rule 6 with the node ratings (extruder "
                "2.2 kW, clamp 0.75 kW BLOW-CLAMP-01, air 0.75 kW "
                "BLOW-AIR-01), and the mold tool envelope (BLOW-MOLD-TOOL-01) "
                "between the platens",
        "process": "node figures: 2.8 kg/h at 3.0 h/d on the 8.407 kg/d wax "
                   "feed (C11-C18 to the mold); products to MFG_SHOP "
                   "(IA-BLOW-OUT); scrap to OIL_FRAC (node design lines)",
        "mold_hold": "the article geometry is not named on the node, so the "
                     "mold set is an envelope and the mold detail is a named "
                     "hold (WORK_ORDER W12)",
        "material": MAT_WET, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet (the "
                          "wax melt path); CA 0 mm (AQS-STD-001); frame and "
                          "dry groups carbon steel",
        "guard": "four-post guard frame (40 x 40 posts, top rails) on the "
                 "base plate pins the registry box (X-PAR-04); anchors in "
                 "fasteners.csv",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose joints per duty section 4; the N3/N4 "
                    "solids rows are non-piped transfers drawn DN15, bore not "
                    "calculated (plan W4); the N2 vent datum 800 predates the "
                    "1600 box (hold, W12); the schedule rating column (Class "
                    "150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Base plate {L:g} x {W:g} x {T_BASE:g} (BLOW-01 machine base)", 1,
     "carbon steel (ASTM A500)", mass["base"], "make (AQS-BOM-SC-001)",
     "issued envelope frame; anchors in fasteners.csv"],
    ["2", "Guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "machine guard practice (A-MACH hardware drawn); the frame pins the "
     "registry box (X-PAR-04)"],
    ["3", f"Extruder barrel OD {BARREL_OD:g} x {BARREL_LEN:g} with extrusion "
           "head and downward die (the melt path)", 1,
     "316L (duty section 3: the wax melt is the wet service)",
     mass["barrel"] + mass["head_die"], "make (AQS-BOM-SC-001)",
     "melt path per duty section 3; CA 0 mm (AQS-STD-001); barrel and die "
     "sizes are the layout choice (hold, W12)"],
    ["4", "Extruder drive envelope at the barrel tail", 1,
     "purchased drive (envelope)", mass["drive"], "buy",
     "node design extruder_kW 2.2; purchased per plan rule 6, rating from "
     "the node"],
    ["5", "Clamp platens and tie bars (BLOW-CLAMP-01)", 1,
     "carbon steel (ASTM A500)", mass["clamp_platens"], "make (AQS-BOM-SC-001)",
     "clamp drive is the purchased 0.75 kW group (BOM row 6); platens are "
     "shop work; sizes are the layout choice (hold, W12)"],
    ["6", "Purchased drive groups by node rating: clamp 0.75 kW (BLOW-CLAMP-01) "
           "and air supply 0.75 kW (BLOW-AIR-01)", 2,
     "purchased drive (envelope)", mass["air"], "buy",
     "node design clamp_kW 0.75 and air_kW 0.75; purchased per plan rule 6, "
     "ratings from the node (the air envelope is drawn beside the clamp)"],
    ["7", "Mold-halves envelope between the platens (BLOW-MOLD-TOOL-01)", 1,
     "carbon steel mold blank (envelope)", mass["mold"], "make (AQS-BOM-SC-001)",
     "AQS-BOM-SC-001 row: blow moulds and shoe moulds, shop-machinable; the "
     "article geometry is not named on the node - mold detail is a hold (W12)"],
    ["8", "Nozzle set per docs-authority/nozzles/BLOW_MOLD.csv: drain and vent "
           "flush at the envelope faces; the two solids transfer rows drawn "
           "DN15 bore not calculated", len(schedule), "316L (duty section 3)",
     mass["nozzles"], "make (AQS-BOM-SC-001)",
     "issued schedule verbatim; the cable schedule row is carried, never drawn; "
     "atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "base plate to the slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed "
     "at fabrication"],
    [None, "M10 platen bolt", fasteners.grade_for("CS"), 8,
     "clamp platens to the tie-bar frames, 4 per platen (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "melt_path_mm": {"barrel_od": BARREL_OD, "barrel_x": [BX0, BX1],
                     "axis_yz": [BY, BZ], "die": list(DIE)},
    "groups_mm": {"drive": list(DRIVE), "platens": list(PLATEN),
                  "mold": list(MOLD), "air": list(AIR)},
}
p["design"] = dict(DS)
p["design"].update({
    "service": "BLOW_MOLD: continuous-extrusion blow molder (Precious Plastic "
               "class) - wax/polymer articles for the shop goods loop, "
               "2.8 kg/h at 3.0 h/d on the 8.407 kg/d C11-C18 feed; products "
               "to MFG_SHOP, scrap to OIL_FRAC (node design block; "
               "AQS-EQP-MFG-001; A-M-285)",
    "material": "316L melt path (barrel, head, die); CS frame and dry groups",
    "material_basis": "duty section 3: 316L where the stream is wet (the wax "
                      "melt); CA 0 mm (AQS-STD-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; barrel axis at y 400, z 900, x "
             "80..780 with the drive at the tail and the head/die at the "
             "front; clamp platens and mold envelope x 840..1080; air group "
             "beside the clamp; guard posts at the envelope corners",
    "supports": "base plate + guard frame + 8 slab anchors; barrel cradle "
                "bolts",
    "nozzle_spread": "the two solids rows at x 600/660 on their faces; drain "
                     "at x 430 flush at the bottom, vent at x 770 flush at "
                     "the top; per-tag notes in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
