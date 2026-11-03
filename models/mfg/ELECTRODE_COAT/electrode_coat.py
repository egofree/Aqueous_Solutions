"""ELECTRODE_COAT manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 800 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 800 x 1800 mm, node size_mm ("L x W x H mm, issued envelope").
  The duty section 2 envelope line agrees with the node. A four-post guard frame
  on the base plate pins the registry box so the X-PAR-04 envelope registry reads
  the build.
- Machine per the node design block and its equipment authority AQS-MFG-ELC-001
  (`docs-authority/ELECTRODE_FAB.md` Rev D, named on the node note): an open-front
  coating booth (sheet-steel hood: back, sides, top over a 316L drip tray) with
  the three issued equipment identifiers as envelopes per plan rule 6 -
  ELC-SPRAY-01 coat head (no recipe or nameplate designed; AQS-MFG-ELC-001 says
  so, hold W12), ELC-CURE-01 IR cure panel (1.2 kW, node cure_kW, purchased),
  ELC-EXH-01 exhaust fan (0.35 kW, node exhaust_kW, purchased) at the hood top
  rear. The exhaust routing is the node design line "MET_AHU -> MET_SCRUB
  (S71-S72)", named at the vent. The hood panel sizes are the layout choice
  (W12).
- Wetted hardware (coat head, drip tray, rack rails) 316L per duty section 3;
  CA 0 mm. Substrates are 316L-stainless or titanium mesh/plate per
  AQS-MFG-ELC-001 section 3 - the workpiece is not part of the machine and is
  not drawn.
- Guard and anchors: the four-post guard frame; 8 slab anchors in fasteners.csv.
  (The class carries a section 4 route hold - no F-MACH row names `coater` - so
  the acceptance set is A-core + A-SC.)
- Nozzles: all 4 rows of docs-authority/nozzles/ELECTRODE_COAT.csv drawn at tag,
  face, height and bore: N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is a schedule placeholder under the
  1800 box) - the vent carries the hood exhaust to MET_AHU (node design exhaust
  line, destination named); N3 (nickel sheet to the booth) and N4 (coated anode)
  are `solids` transfer rows drawn DN15, bore not calculated (plan W4). Duty
  section 4: atmospheric joints are hose.
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 800 x 1800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
_mach = DS.get("machine")
if isinstance(_mach, dict):            # builder-owned nesting from a previous pass
    DS = _mach
assert DS.get("machine") == "coating booth + IR cure", "node design block changed"

T_BASE = 20.0                                              # base plate (layout, W12)
POST = 40.0                                                # guard frame section
T_PANEL = 5.0                                              # hood sheet (study, W12)
MAT_WET = "316L"                                           # duty section 3 (slurry-wetted hardware)
CA = materials.ca_for(MAT_WET)                             # 0.0, AQS-STD-001
RHO_WET = materials.density(MAT_WET)
RHO_CS = materials.density("CS")

HOOD_Z1 = 1560.0                                           # hood top under the top panel
PANELS = [                                                 # (x, y, z, dx, dy, dz) - layout, W12
    (44.0, 745.0, T_BASE, 1112.0, 10.0, HOOD_Z1 - T_BASE),          # back
    (44.0, 44.0, T_BASE, 10.0, 711.0, HOOD_Z1 - T_BASE),            # left
    (1146.0, 44.0, T_BASE, 10.0, 711.0, HOOD_Z1 - T_BASE),          # right
    (44.0, 44.0, HOOD_Z1, 1112.0, 711.0, 10.0),                     # top
]
TRAY = (48.0, 48.0, T_BASE, 1104.0, 704.0, 15.0)           # 316L drip tray (wetted)
SPRAY = (560.0, 340.0, 1000.0, 60.0, 60.0, 80.0)           # ELC-SPRAY-01 envelope
RACKS = [(200.0, 300.0, 700.0, 800.0, 30.0, 30.0),         # rack rails (wetted)
         (200.0, 300.0, 900.0, 800.0, 30.0, 30.0)]
CURE = (300.0, 690.0, 1200.0, 400.0, 50.0, 150.0)          # ELC-CURE-01 IR panel (1.2 kW)
EXH = (450.0, 700.0, 1400.0, 300.0, 55.0, 160.0)           # ELC-EXH-01 fan (0.35 kW)

assert L == 1200.0 and W == 800.0 and H == 1800.0, "ELECTRODE_COAT node envelope changed"
for (x, y, z, dx, dy, dz) in PANELS + [SPRAY, CURE, EXH]:
    assert x >= 44.0 and x + dx <= L - 44.0 and y >= 44.0 and y + dy <= W - 44.0, "inside the guard"
    assert z + dz <= H - POST - 40.0, "under the top rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


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

# ---------------------------------------------------------------- booth hood (sheet panels)
hood = None
for (x, y, z, dx, dy, dz) in PANELS:
    b = box(x, y, z, dx, dy, dz)
    hood = b if hood is None else hood.union(b)
parts["hood"] = hood

# ---------------------------------------------------------------- wetted interior (316L)
tray = box(*TRAY)
racks = None
for (x, y, z, dx, dy, dz) in RACKS:
    r = box(x, y, z, dx, dy, dz)
    racks = r if racks is None else racks.union(r)
parts["tray"] = tray
parts["racks"] = racks
parts["spray"] = box(*SPRAY)                               # ELC-SPRAY-01 envelope (wetted class)

# ---------------------------------------------------------------- purchased envelopes (plan rule 6)
parts["cure"] = box(*CURE)                                 # ELC-CURE-01 IR panel, 1.2 kW
parts["exhaust"] = box(*EXH)                               # ELC-EXH-01 fan, 0.35 kW

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
    if r["face"] == "bottom":                             # N1: tray drain at the envelope bottom
        s = tube_z("DN15", T_BASE + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = ("tray drain flush at the envelope bottom; 50 datum is the "
                "schedule placeholder")
    elif r["face"] == "top":                              # N2: hood exhaust to MET_AHU
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (770.0, W / 2), (L, W, H))
        note = ("hood exhaust flush at the envelope top; the schedule datum "
                "800 mm predates the 1800 box (hold W12); the routing is the "
                "node design line MET_AHU -> MET_SCRUB (S71-S72), destination "
                "named")
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
_m = {"base": RHO_CS, "frame": RHO_CS, "hood": RHO_CS, "tray": RHO_WET,
      "racks": RHO_WET, "spray": RHO_WET, "cure": RHO_CS, "exhaust": RHO_CS,
      "nozzles": RHO_WET}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "electrode coating booth per the node design block and its "
                "equipment authority AQS-MFG-ELC-001 Rev D (named on the node "
                "note): open-front sheet-steel hood over a 316L drip tray, "
                "coat-head envelope (ELC-SPRAY-01), IR cure panel envelope "
                "(ELC-CURE-01, 1.2 kW, purchased), exhaust fan envelope "
                "(ELC-EXH-01, 0.35 kW, purchased); the formulation is the "
                "node carbon/Ni non-precious M1 class (RuO2-IrO2 deferred)",
        "exhaust_routing": "node design line MET_AHU -> MET_SCRUB (S71-S72), "
                           "named at the vent (AQS-MFG-ELC-001 section 3.2; "
                           "the afterburner is not the primary treatment)",
        "design_gap": "AQS-MFG-ELC-001: coating recipes and equipment "
                      "nameplates are not designed - the coat head is an "
                      "envelope, no internals invented (hold, WORK_ORDER W12)",
        "wetted": "coat head, drip tray and rack rails 316L per duty section "
                  "3 (coating slurry); CA 0 mm (AQS-STD-001); substrates "
                  "(316L-stainless or titanium mesh/plate per AQS-MFG-ELC-001 "
                  "section 3) are the workpiece, not drawn",
        "guard": "four-post guard frame (40 x 40 posts, top rails) on the "
                 "base plate pins the registry box (X-PAR-04); anchors in "
                 "fasteners.csv",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose joints per duty section 4; the N3/N4 "
                    "solids rows are non-piped transfers drawn DN15, bore not "
                    "calculated (plan W4); the N2 vent carries the hood "
                    "exhaust with the MET_AHU -> MET_SCRUB destination named; "
                    "the schedule rating column (Class 150) carried verbatim "
                    "as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Base plate {L:g} x {W:g} x {T_BASE:g} (ELC-BOOTH-01 booth base)", 1,
     "carbon steel (ASTM A500)", mass["base"], "make (AQS-BOM-SC-001)",
     "issued envelope frame; anchors in fasteners.csv"],
    ["2", "Guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "machine guard practice (A-MACH hardware drawn); the frame pins the "
     "registry box (X-PAR-04)"],
    ["3", "Booth hood: back, side and top sheet panels (open front), sheet "
           f"{T_PANEL:g} (study, W12)", 1, "carbon steel sheet (AQS-MOD-002)",
     mass["hood"], "make (AQS-BOM-SC-001)",
     "booth per AQS-MFG-ELC-001 section 3.2 (metal aisle, exhaust to "
     "MET_AHU); panel sizes are the layout choice (hold, W12)"],
    ["4", "Drip tray and electrode rack rails (slurry-wetted interior)", 1,
     "316L (duty section 3)", mass["tray"] + mass["racks"],
     "make (AQS-BOM-SC-001)",
     "wetted per duty section 3 (coating slurry); CA 0 mm (AQS-STD-001)"],
    ["5", "Coat head envelope on its rail (ELC-SPRAY-01)", 1,
     "316L class envelope (wetted)", mass["spray"], "make (AQS-BOM-SC-001)",
     "AQS-MFG-ELC-001: coating recipes and nameplates not designed - "
     "envelope + interface per plan rule 6, no internals invented (hold, W12)"],
    ["6", "IR cure panel envelope (ELC-CURE-01)", 1, "purchased unit (envelope)",
     mass["cure"], "buy",
     "node design cure_kW 1.2 over the 1.0 h cure (campaign 2.0 h/d); "
     "purchased per plan rule 6, rating from the node"],
    ["7", "Exhaust fan envelope (ELC-EXH-01) at the hood top rear", 1,
     "purchased unit (envelope)", mass["exhaust"], "buy",
     "node design exhaust_kW 0.35; routing MET_AHU -> MET_SCRUB (S71-S72) "
     "per the node design and AQS-MFG-ELC-001 section 3.2; purchased per "
     "plan rule 6, rating from the node"],
    ["8", "Nozzle set per docs-authority/nozzles/ELECTRODE_COAT.csv: tray "
           "drain and hood exhaust flush at the envelope faces; the two "
           "solids transfer rows drawn DN15 bore not calculated",
     len(schedule), "316L (duty section 3)", mass["nozzles"],
     "make (AQS-BOM-SC-001)",
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
    [None, "M8 hood-panel bolt", fasteners.grade_for("CS"), 12,
     "hood panels to the frame, 4 back + 4 per side rail (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "hood_mm": {"panels": [list(pl) for pl in PANELS], "sheet": T_PANEL},
    "interior_mm": {"tray": list(TRAY), "spray": list(SPRAY),
                    "racks": [list(r) for r in RACKS]},
    "purchased_mm": {"cure": list(CURE), "exhaust": list(EXH)},
}
p["design"] = dict(DS)
p["design"].update({
    "service": "ELECTRODE_COAT: coating booth + IR cure for the EW/BMED "
               "replaceable electrodes, carbon/Ni non-precious M1 class "
               "(RuO2-IrO2 deferred); exhaust MET_AHU -> MET_SCRUB (S71-S72); "
               "recoat loop IA-COAT-IN/OUT 0.02 kg/d net zero (node design "
               "block; AQS-MFG-ELC-001 Rev D)",
    "material": "316L wetted (coat head, tray, racks); CS hood and frame",
    "material_basis": "duty section 3: 316L where the stream is wet "
                      "(coating slurry); CA 0 mm (AQS-STD-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; hood panels per "
             "params.envelope.hood_mm (open front on -Y); spray head at x "
             "560..620, z 1000..1080; cure panel z 1200..1350; exhaust fan "
             "z 1400..1560 at the top rear; guard posts at the envelope "
             "corners",
    "supports": "base plate + guard frame + 8 slab anchors; hood panel bolts",
    "nozzle_spread": "the two solids rows at x 600/660 on their faces; tray "
                     "drain at x 430 flush at the bottom, hood exhaust at x "
                     "770 flush at the top; per-tag notes in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
