"""LITHO_DEV manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 600 x 900 mm, node size_mm ("L x W x H mm, issued envelope
  (A-M-287)"). The build stays inside it; a four-post hold-down frame on the base
  plate pins the registry box so the X-PAR-04 envelope registry reads the build.
  The duty section 2 prose still carries the seed figure "Envelope 500 x 500 x
  800 mm" - the node governs and the older figure is named (holds, WORK_ORDER
  W12, the WS_SOLV precedent).
- Bench per the node design block and note ("Wet develop bench on the WET_BENCH
  chemistry class (TMAH/KOH developer fork, S38 resist-waste loop)"; A-M-287
  basis: puddle-develop dispense 40 mL/wafer at 150 mm): the develop bowl is the
  wetted station, 316L per duty section 3 (the developer stream is the wet
  service), with the puddle dispense point envelope above it. Bowl size is the
  layout choice (W12); the puddle figure 40 mL/wafer is a node figure.
- A-MACH guard and anchors: the four-post hold-down frame is the guard; 8 slab
  anchors in fasteners.csv. No purchased item is named on the node or duty, so
  none is drawn; the A-MACH purchased-item criterion has nothing to match (the
  WS_SOLV precedent).
- Nozzles: all 4 rows of docs-authority/nozzles/LITHO_DEV.csv drawn at tag,
  face, height and bore: N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is a schedule placeholder under the
  900 box); N3 (spent resist and solvent out) on +Y at z 600 and N4 (resist/
  solvent carry in from the coat bench) on -Y at z 160 are `solids` transfer
  rows drawn DN15, bore not calculated (plan W4). Duty section 4: atmospheric
  joints are hose; DN is copied from the edge and is not recalculated.
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 600 x 900
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
_mach = DS.get("machine")
if isinstance(_mach, dict):            # builder-owned nesting from a previous pass
    DS = _mach
assert DS.get("machine") == "wet develop bench", "node design block changed"

T_BASE = 20.0                                              # base plate (layout, W12)
POST = 40.0                                                # hold-down/guard frame section
T_WALL = 10.0                                              # bowl wall (study, W12)
MAT_WET = "316L"                                           # duty section 3 (developer wetted)
CA = materials.ca_for(MAT_WET)                             # 0.0, AQS-STD-001
RHO_WET = materials.density(MAT_WET)
RHO_CS = materials.density("CS")

# Develop bowl on the base (size is the layout choice, W12; the puddle figure
# 40 mL/wafer is a node design figure).
BOWL = (150.0, 150.0, T_BASE + 20.0, 300.0, 200.0, 120.0)  # inner dx dy dz
DISPENSE = (280.0, 230.0, BOWL[2] + BOWL[5] + 40.0, 40.0, 40.0, 40.0)   # dispense point envelope

assert L == 1200.0 and W == 600.0 and H == 900.0, "LITHO_DEV node envelope changed"
assert BOWL[0] >= 44.0 and BOWL[0] + BOWL[3] + 2 * T_WALL <= L - 44.0, "bowl inside the guard"
assert DISPENSE[2] + DISPENSE[5] <= H - POST - 40.0, "dispense under the top rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- base plate + hold-down/guard frame
parts["base"] = box(0, 0, 0, L, W, T_BASE)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- develop bowl (wetted 316L)
bx, by, bz, bdx, bdy, bdz = BOWL
outer = box(bx, by, bz, bdx + 2 * T_WALL, bdy + 2 * T_WALL, bdz + T_WALL)
void = box(bx + T_WALL, by + T_WALL, bz + T_WALL, bdx, bdy, bdz + 1.0)
parts["bowl"] = outer.cut(void).union(box(bx + T_WALL, by + T_WALL, bz, bdx, bdy, T_WALL))
parts["dispense"] = box(*DISPENSE)

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
    note = "atmospheric hose joint per duty section 4"
    if r["face"] == "bottom":                             # N1: drain flush at the envelope bottom
        s = tube_z("DN15", T_BASE + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder")
    elif r["face"] == "top":                              # N2: 800 datum predates the 900 box
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (770.0, W / 2), (L, W, H))
        note = ("vent flush at the envelope top; the schedule datum 800 mm "
                "predates the 900 box (hold, WORK_ORDER W12)")
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
asm.export(str(out / (UNIT.lower() + ".step")))

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
_m = {"base": RHO_CS, "frame": RHO_CS, "bowl": RHO_WET, "dispense": RHO_WET,
      "nozzles": RHO_WET}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "wet develop bench per the node design block and note (A-M-287): "
                "develop bowl in 316L per duty section 3 (TMAH 2.38 % class "
                "developer, the shared WET_BENCH chemistry fork) with the "
                "puddle dispense point envelope above it; waste on the "
                "S38-class resist/solvent loop to OIL_FRAC",
        "duty_line": "duty section 2 prose carries the seed figure 500 x 500 x "
                     "800; the node 1200 x 600 x 900 governs (hold, WORK_ORDER "
                     "W12, WS_SOLV precedent)",
        "bowl": {"inner_mm": [bdx, bdy, bdz],
                 "nominal_l": round(bdx * bdy * bdz / 1e6, 1),
                 "wall_mm": T_WALL,
                 "size_basis": "layout choice (hold, W12); the puddle figure "
                               f"{DS.get('puddle_mL_per_wafer')} mL/wafer is a "
                               "node design figure"},
        "material": MAT_WET, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet "
                          "(developer); CA 0 mm (AQS-STD-001)",
        "guard": "four-post hold-down frame (40 x 40 posts, top rails) is the "
                 "A-MACH guard + 8 slab anchors (fasteners.csv)",
        "purchased": "no purchased item is named on the node or duty, so none "
                     "is drawn (WS_SOLV precedent)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose joints per duty section 4 (DN copied from "
                    "the edge and not recalculated); the N3/N4 solids rows are "
                    "non-piped transfers drawn DN15, bore not calculated (plan "
                    "W4); the N2 vent datum 800 predates the 900 box (hold, "
                    "W12); the schedule rating column (Class 150) carried "
                    "verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Base plate {L:g} x {W:g} x {T_BASE:g}", 1, "carbon steel (ASTM A500)",
     mass["base"], "make (AQS-BOM-SC-001)",
     "issued envelope frame (A-M-287); anchors in fasteners.csv"],
    ["2", "Hold-down/guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "HX8 hold-down idiom (X-PAR-04); A-MACH guard"],
    ["3", f"Develop bowl (inner {bdx:g} x {bdy:g} x {bdz:g}, wall {T_WALL:g} "
           "study)", 1, "316L (duty section 3)", mass["bowl"],
     "make (AQS-BOM-SC-001)",
     "wetted per duty section 3 (TMAH class developer, the shared WET_BENCH "
     "chemistry fork); CA 0 mm (AQS-STD-001); bowl size is the layout choice "
     "(hold, W12)"],
    ["4", "Puddle dispense point envelope above the bowl (40 mL/wafer per the "
           "node design)", 1, "316L (duty section 3)", mass["dispense"],
     "make (AQS-BOM-SC-001)",
     "node design puddle_mL_per_wafer 40; the dispense valve is bench "
     "hardware, no rating named on the node or duty"],
    ["5", "Nozzle set per docs-authority/nozzles/LITHO_DEV.csv: drain and vent "
           "flush at the envelope faces; the two solids transfer rows drawn "
           "DN15 bore not calculated", len(schedule), "316L (duty section 3)",
     mass["nozzles"], "make (AQS-BOM-SC-001)",
     "4-row issued schedule verbatim; atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "base plate to the slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed "
     "at fabrication"],
    [None, "M8 bowl-clip bolt", fasteners.grade_for("316L"), 4,
     "bowl base flange to the base plate, one per corner (count from the model)",
     "A4-70 on the 316L wetted assembly per the grade rule; study pattern, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "bowl_mm": list(BOWL) + [T_WALL],
    "dispense_mm": list(DISPENSE),
}
p["design"] = dict(DS)
p["design"].update({
    "service": "LITHO_DEV: wet develop bench - TMAH 2.38 % class developer on "
               "the shared WET_BENCH chemistry fork, puddle 40 mL/wafer, waste "
               "on the S38-class resist/solvent loop to OIL_FRAC (node design "
               "block; A-M-287)",
    "material": "316L wetted (bowl, dispense, hardware); CS dry frame",
    "material_basis": "duty section 3: 316L where the stream is wet "
                      "(developer); CA 0 mm (AQS-STD-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; bowl at x 150..480, y 150..370, "
             "z 40..170 with the dispense point above; hold-down posts at the "
             "envelope corners",
    "supports": "base plate + hold-down frame + 8 slab anchors; bowl base "
                "flange bolts",
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
