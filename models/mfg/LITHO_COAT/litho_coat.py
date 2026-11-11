"""LITHO_COAT manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 800 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 800 x 1400 mm, node size_mm ("L x W x H mm, issued envelope
  (A-M-287)"). The build stays inside it; a four-post guard frame on the base
  plate pins the registry box so the X-PAR-04 envelope registry reads the build.
  The duty section 2 prose still carries the seed figure "Envelope 600 x 500 x
  800 mm" - the node governs and the older figure is named (holds, WORK_ORDER
  W12, the WS_SOLV precedent).
- Machine per the node design block and its note ("Spin-coater line: spin bowl,
  vacuum chuck, softbake hotplate"; A-M-287 basis: spin-chuck motor 0.75 kW
  peak, softbake hotplate 0.3 kW at 100 C hold): spin bowl and coat catch bowl
  in 316L per duty section 3 (the resist/solvent stream is the wet service),
  the 150 mm vacuum chuck (node chuck_mm) on the spindle inside the bowl, the
  spin-chuck motor and the softbake hotplate drawn as purchased envelopes per
  plan rule 6 with the ratings from the node. Chuck diameter 150 mm is a node
  figure; the bowl and hotplate envelope sizes are the layout choice (W12).
  Resist novolac 1 um, 5000 rpm, 2.0 mL dispense per wafer (node design).
- Guard and anchors: four-post guard frame (40 x 40 posts + top rails) on the
  base plate; anchors in fasteners.csv. (The class carries a section 4 route
  hold - no F-MACH row names `coater` - so the acceptance set is A-core + A-SC;
  the guard and anchor hardware is drawn per the machine practice the lane
  applies.)
- Nozzles: all rows of docs-authority/nozzles/LITHO_COAT.csv drawn at tag,
  face, height and bore: N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is a schedule placeholder under the
  1400 box); N3 (spent resist and solvent in) and N4 (resist/solvent carry to
  the develop bench) are `solids` transfer rows drawn DN15, bore not calculated
  (plan W4). Duty section 4: atmospheric joints are hose; DN copied from the
  edge and not recalculated.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 800 x 1400
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
_mach = DS.get("machine")
if isinstance(_mach, dict):            # builder-owned nesting from a previous pass
    DS = _mach
assert DS.get("machine") == "spin-coater line", "node design block changed"

T_BASE = 20.0                                              # base plate (layout, W12)
POST = 40.0                                                # guard frame section
MAT_WET = "316L"                                           # duty section 3 (resist/solvent wetted)
CA = materials.ca_for(MAT_WET)                             # 0.0, AQS-STD-001
RHO_WET = materials.density(MAT_WET)
RHO_CS = materials.density("CS")

CX, CY = 300.0, 400.0                                      # spin station axis (layout, W12)
BOWL_OD, BOWL_WALL = 360.0, 10.0                           # bowl envelope (layout around the chuck, W12)
BOWL_Z0, BOWL_Z1 = 140.0, 340.0                            # bowl on its stand
CATCH_OD = 480.0                                           # coat catch bowl envelope (layout, W12)
CATCH_Z0, CATCH_Z1 = 140.0, 200.0
CHUCK_D = float(DS.get("chuck_mm", 150))                   # node chuck_mm
SPINDLE_D = 30.0
SPINDLE_Z0, CHUCK_Z0, CHUCK_Z1 = BOWL_Z0 + 10.0, 300.0, 330.0
STAND = (CX - 120.0, CY - 120.0, T_BASE, 240.0, 240.0, 100.0)   # bowl stand over the deck
MOTOR = (CX - 120.0, CY - 120.0, T_BASE, 240.0, 240.0, 100.0)   # motor envelope (inside stand zone)
HP = (700.0, 300.0, T_BASE, 250.0, 250.0, 60.0)            # softbake hotplate envelope

assert L == 1200.0 and W == 800.0 and H == 1400.0, "LITHO_COAT node envelope changed"
assert CHUCK_D < BOWL_OD - 2 * BOWL_WALL - 40.0, "chuck inside the bowl bore"
assert BOWL_Z1 <= H - POST - 40.0 and HP[0] + HP[3] <= L - 44.0, "inside the guard"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def vtube(od, x, y, z0, z1):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0)


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

# ---------------------------------------------------------------- spin station (wetted 316L)
bowl = vtube(BOWL_OD, CX, CY, BOWL_Z0, BOWL_Z1)
bowl = bowl.union(vtube(BOWL_OD, CX, CY, BOWL_Z0, BOWL_Z0 + BOWL_WALL))       # floor
bowl = bowl.cut(vtube(BOWL_OD - 2 * BOWL_WALL, CX, CY, BOWL_Z0 + BOWL_WALL, BOWL_Z1 + 1.0))
bowl = bowl.union(box(CX - 100.0, CY - 100.0, BOWL_Z1, 200.0, 200.0, 20.0))   # rim collar
parts["spin_bowl"] = bowl
catch = vtube(CATCH_OD, CX, CY, CATCH_Z0, CATCH_Z1)
catch = catch.union(vtube(CATCH_OD, CX, CY, CATCH_Z0, CATCH_Z0 + BOWL_WALL))  # tray floor
catch = catch.cut(vtube(CATCH_OD - 2 * BOWL_WALL, CX, CY, CATCH_Z0 + BOWL_WALL, CATCH_Z1 + 1.0))
parts["catch_bowl"] = catch
parts["stand"] = box(*STAND)
spindle = (vtube(SPINDLE_D, CX, CY, SPINDLE_Z0, CHUCK_Z0)
           .union(vtube(CHUCK_D, CX, CY, CHUCK_Z0, CHUCK_Z1)))                # spindle + chuck
parts["chuck"] = spindle

# ---------------------------------------------------------------- purchased envelopes (plan rule 6)
parts["motor"] = box(*MOTOR)                               # spin-chuck motor, 0.75 kW peak
parts["hotplate"] = box(*HP)                               # softbake hotplate, 0.3 kW at 100 C

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {600.0: 0.0}
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
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, CY), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder")
    elif r["face"] == "top":                              # N2: 800 datum predates the 1400 box
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (770.0, CY), (L, W, H))
        note = ("vent flush at the envelope top; the schedule datum 800 mm "
                "predates the 1400 box (hold, WORK_ORDER W12)")
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
_m = {"base": RHO_CS, "frame": RHO_CS, "spin_bowl": RHO_WET, "catch_bowl": RHO_WET,
      "stand": RHO_CS, "chuck": RHO_WET, "motor": RHO_CS, "hotplate": RHO_CS,
      "nozzles": RHO_WET}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "spin-coater line per the node design block and note (A-M-287): "
                "spin bowl and coat catch bowl in 316L per duty section 3, the "
                "150 mm vacuum chuck (node chuck_mm) on the spindle inside the "
                "bowl, spin-chuck motor and softbake hotplate drawn as "
                "purchased envelopes per plan rule 6 with the node ratings",
        "duty_line": "duty section 2 prose carries the seed figure 600 x 500 x "
                     "800; the node 1200 x 800 x 1400 governs (hold, WORK_ORDER "
                     "W12, WS_SOLV precedent)",
        "wetted": "spin bowl, catch bowl, chuck and hardware 316L per duty "
                  "section 3 (resist/solvent stream); CA 0 mm (AQS-STD-001)",
        "parts": {"spin_bowl": f"OD {BOWL_OD:g} x {BOWL_Z1 - BOWL_Z0:g} deep, wall "
                               f"{BOWL_WALL:g} (envelope sizes are the layout choice, W12)",
                  "catch_bowl": f"OD {CATCH_OD:g} x {CATCH_Z1 - CATCH_Z0:g} tray (the "
                                "IA-LITHO-CARRY stream names the coat catch bowl)",
                  "chuck": f"vacuum chuck D {CHUCK_D:g} (node chuck_mm) on the "
                           "spindle; the vacuum source is not named on the node "
                           "or duty - none drawn (hold, W12)",
                  "motor": "spin-chuck motor envelope, 0.75 kW peak (node "
                           "spin_peak_kW; A-M-287 basis) - purchased per plan rule 6",
                  "hotplate": "softbake hotplate envelope, 0.3 kW at the node "
                              "100 C hold (node softbake_kW/softbake_C) - "
                              "purchased per plan rule 6"},
        "guard": "four-post guard frame (40 x 40 posts, top rails) on the base "
                 "plate pins the registry box (X-PAR-04); anchors in "
                 "fasteners.csv",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose joints per duty section 4 (DN copied from "
                    "the edge and not recalculated); the N3/N4 solids rows are "
                    "non-piped transfers drawn DN15, bore not calculated (plan "
                    "W4); the N2 vent datum 800 predates the 1400 box (hold, "
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
    ["2", "Guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "machine guard practice (A-MACH hardware drawn); the frame pins the "
     "registry box (X-PAR-04)"],
    ["3", f"Spin bowl OD {BOWL_OD:g} x {BOWL_Z1 - BOWL_Z0:g}, wall {BOWL_WALL:g} "
           "(study), with rim collar, on the stand", 1, "316L (duty section 3)",
     mass["spin_bowl"], "make (AQS-BOM-SC-001)",
     "wetted per duty section 3 (resist/solvent); CA 0 mm (AQS-STD-001); bowl "
     "envelope is the layout choice around the node 150 mm chuck (hold, W12)"],
    ["4", f"Coat catch bowl OD {CATCH_OD:g} x {CATCH_Z1 - CATCH_Z0:g} tray (the "
           "IA-LITHO-CARRY stream names the coat catch bowl)", 1,
     "316L (duty section 3)", mass["catch_bowl"], "make (AQS-BOM-SC-001)",
     "catch tray under the spin bowl; envelope is the layout choice (hold, W12)"],
    ["5", f"Vacuum chuck D {CHUCK_D:g} (node chuck_mm) on the spindle", 1,
     "316L (duty section 3)", mass["chuck"], "make (AQS-BOM-SC-001)",
     "node design chuck_mm; the vacuum source is not named on the node or duty "
     "- none drawn (hold, W12)"],
    ["6", "Spin-chuck motor envelope under the bowl stand", 1,
     "purchased drive (envelope)", mass["motor"], "buy",
     "node spin_peak_kW 0.75 (A-M-287 basis: spin-chuck motor 0.75 kW peak); "
     "purchased per plan rule 6, rating from the node"],
    ["7", "Softbake hotplate envelope on the deck", 1,
     "purchased unit (envelope)", mass["hotplate"], "buy",
     "node softbake_kW 0.3 at the 100 C hold (A-M-287 basis); purchased per "
     "plan rule 6, rating from the node"],
    ["8", "Nozzle set per docs-authority/nozzles/LITHO_COAT.csv: drain and vent "
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
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "base plate to the slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed "
     "at fabrication"],
    [None, "M8 bowl-stand bolt", fasteners.grade_for("316L"), 4,
     "spin-bowl stand to the base plate, one per corner (count from the model)",
     "A4-70 on the 316L wetted assembly per the grade rule; study pattern, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "spin_station_mm": {"axis_xy": [CX, CY], "bowl_od": BOWL_OD, "bowl_z": [BOWL_Z0, BOWL_Z1],
                        "catch_od": CATCH_OD, "chuck_d": CHUCK_D},
    "hotplate_mm": list(HP),
}
p["design"] = dict(DS)
p["design"].update({
    "service": "LITHO_COAT: spin-coater line - dispense 2.0 mL, spin 5000 rpm, "
               "softbake 100 C, novolac resist 1 um, 5 wafer starts/d (node "
               "design block; A-M-287; AQS-LITH-001 chemistry)",
    "material": "316L wetted (spin bowl, catch bowl, chuck, hardware); CS dry "
                "frame",
    "material_basis": "duty section 3: 316L where the stream is wet "
                      "(resist/solvent); CA 0 mm (AQS-STD-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; spin station axis at (300, 400), "
             "bowl z 140..340 on the stand over the base plate, catch tray "
             "z 140..200, chuck z 300..330; hotplate at x 700..950; guard "
             "posts at the envelope corners",
    "supports": "base plate + guard frame + 8 slab anchors; bowl stand bolts",
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
