"""OIL_DRYER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box). The
  build stays inside it exactly.
- Machine per the unit's own duty sheet (float plastics 33 kg/d dried on the HX-4
  Q3 jacket heat, out to OIL_PYRO): a horizontal jacketed drying drum drawn to the
  envelope - drum OD 500 x 700 with end heads, jacket annulus 20 mm (the N1/N2
  rows are the HX-4 Q3 process heat connections, schedule service text carried
  verbatim), steel wall 6 mm, on two saddles over a 20 mm plinth. Material carbon
  steel per duty section 3, hydrocarbon service, CA 1.5 mm (AQS-STD-001).
- A-MACH guard and anchors: a four-post guard frame (40 x 40 posts, mid and top
  rails) pins the envelope around the drum; 8 slab anchors in fasteners.csv.
- Purchased items: none are named on the node or duty (no equipment row), so none
  are drawn - the dryer drive and vacuum hardware stay a named hold (W12).
- Nozzles: all 7 rows of docs-authority/nozzles/OIL_DRYER.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: nozzle DN15, no flange class, atmospheric tube or hose). Drain
  flush at the envelope bottom (50 datum); vent flush at the envelope top (800
  datum is the box top). The schedule rating column (Class 150) is carried
  verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
DRUM_OD, T_WALL, DRUM_LEN = 500.0, 6.0, 700.0              # to the envelope; wall study (W12)
T_JACKET = 20.0                                            # jacket annulus (study, W12)
OD_OUT = DRUM_OD + 2 * T_JACKET                            # 540
Y_C, Z_C = W / 2, 430.0                                    # drum axis
X0 = (L - DRUM_LEN) / 2                                    # 150: drum centred along x
MAT = "CS"                                                 # duty section 3
CA = materials.ca_for(MAT, "hydrocarbon")                  # 1.5, AQS-STD-001
RHO = materials.density(MAT)
POST = 40.0                                                # guard frame section

assert L == 1000.0 and W == 600.0 and H == 800.0, "OIL_DRYER node envelope changed"
assert OD_OUT <= W and DRUM_LEN <= L - 200.0, "drum drawn to the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + saddles
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
saddle = None
for xs in (X0 + 80.0, X0 + DRUM_LEN - 80.0):
    # saddle tops pierce the drum annulus: tangent contacts do not fuse
    s = box(xs - 80.0, Y_C - DRUM_OD / 2 - 15.0, T_PLINTH, 160.0, 2 * (DRUM_OD / 2 + 15.0),
            Z_C - (DRUM_OD / 2 - 25.0) - T_PLINTH)
    saddle = s if saddle is None else saddle.union(s)
parts["saddles"] = saddle

# ---------------------------------------------------------------- jacketed drying drum
drum = (cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
        .circle(DRUM_OD / 2).circle(DRUM_OD / 2 - T_WALL).extrude(DRUM_LEN))
ends = None
for xe in (X0, X0 + DRUM_LEN - 8.0):                       # end heads
    e = (cq.Workplane("YZ", origin=(xe, Y_C, Z_C))
         .circle(DRUM_OD / 2).circle(DRUM_OD / 2 - T_WALL - 4.0).extrude(8.0))
    ends = e if ends is None else ends.union(e)
parts["drum"] = drum.union(ends)
# jacket shell with end plates, press 3 mm onto the drum wall (fuse idiom)
jacket = (cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
          .circle(OD_OUT / 2).circle(DRUM_OD / 2 - 3.0).extrude(DRUM_LEN - 60.0))
jacket = jacket.union(cq.Workplane("YZ", origin=(X0 + 30.0, Y_C, Z_C))
                      .circle(OD_OUT / 2).circle(DRUM_OD / 2).extrude(10.0))
jacket = jacket.union(cq.Workplane("YZ", origin=(X0 + DRUM_LEN - 40.0, Y_C, Z_C))
                      .circle(OD_OUT / 2).circle(DRUM_OD / 2).extrude(10.0))
parts["jacket"] = jacket

# ---------------------------------------------------------------- guard frame (A-MACH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for z_r in (H - POST, 300.0):                              # top and mid rails
    for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                             (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
        b = box(rx, ry, z_r, dx, dy, POST)
        frame = frame.union(b)
parts["frame"] = frame

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def od_of(r):
    return dn.pipe_od(r["size"]) if r["size"].startswith("DN") else dn.pipe_od("DN15")


schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 300.0, (face, z, span)
    x = 120.0 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N6: drain flush at the envelope bottom
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N7: 800 datum is the box top
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = tube_z(dnl, 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": h if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
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
mass = {k: round(v.val().Volume() * RHO / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "horizontal jacketed drying drum drawn to the envelope: drum OD 500 "
                "x 700 with end heads, jacket annulus 20 mm (the N1/N2 rows are the "
                "HX-4 Q3 process heat connections), steel wall 6 (study - holds, "
                "W12), on two saddles over a 20 mm plinth",
        "drum_od_mm": DRUM_OD, "length_mm": DRUM_LEN, "wall_mm": T_WALL,
        "jacket_mm": T_JACKET,
        "wall_basis": "study values; no authority states a drum or jacket wall "
                      "(WORK_ORDER W12)",
        "material": MAT, "ca_mm": CA,
        "purchased": "none named on the node or duty: no equipment row exists, so "
                     "the dryer drive and vacuum hardware are not drawn (A-MACH "
                     "hold, WORK_ORDER W12)",
        "guard": "four-post guard frame (40 x 40 posts, mid and top rails) pins the "
                 "envelope around the drum (A-MACH: guard and anchor drawn)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: nozzle DN15, no flange class, atmospheric "
                    "tube or hose); the schedule rating column (Class 150) is "
                    "carried verbatim as text; the N1/N2 service text (HX-4 Q3 "
                    "process heat, dryer jacket) is carried verbatim and matches "
                    "the drawn jacket",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Drying drum OD {DRUM_OD:g} x {DRUM_LEN:g}, wall {T_WALL:g} mm (study), "
          "with end heads", 1, "carbon steel (duty section 3)", mass["drum"], "make",
     "drum drawn to the node envelope; wall a study value (hold, WORK_ORDER W12); "
     "CA 1.5 mm (AQS-STD-001 hydrocarbon rule)"],
    ["2", f"Heating jacket OD {OD_OUT:g}, annulus {T_JACKET:g} mm (study), with end "
          "plates, over the drum mid-span (the N1/N2 HX-4 Q3 connections)", 1,
     "carbon steel", mass["jacket"], "make",
     "jacket per the schedule service text (HX-4 Q3 process heat, dryer jacket); "
     "annulus a study value (hold, WORK_ORDER W12)"],
    ["3", "Guard frame: four 40 x 40 posts full height with mid and top rails "
          "(A-MACH guard), + saddles 2 off + plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["frame"] + mass["saddles"] + mass["plinth"], "make",
     "AQS-MOD-002 dry service; the frame pins the envelope (X-PAR-04); anchors in "
     "fasteners.csv"],
    ["4", "Nozzle set per docs-authority/nozzles/OIL_DRYER.csv: 5 open-bore tube "
          "stubs (DN15/DN25), drain and vent flush at the envelope faces",
     len(schedule), "carbon steel", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric tube per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per saddle station (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M12 saddle bolt + nut", fasteners.grade_for("CS"), 8,
     "saddle to drum, 4 per saddle (count from the model)",
     "8.8 on carbon steel; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "drum": {"od_mm": DRUM_OD, "length_mm": DRUM_LEN, "axis_mm": [None, Y_C, Z_C],
             "x0_mm": X0},
    "jacket_mm": T_JACKET,
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "OIL_DRYER: float plastics dried on the HX-4 Q3 jacket heat, out to "
               "OIL_PYRO, atmospheric (duty sections 1, 4 and 6)",
    "material": MAT, "ca_mm": CA,
    "wall_mm": T_WALL, "wall_basis": "study value (hold W12)",
    "jacket_mm": T_JACKET, "jacket_basis": "study value (hold W12)",
    "purchased": "none named on the node or duty (hold W12)",
    "guard": "four-post guard frame per A-MACH",
}
p["layout"] = {
    "frame": "origin at the envelope corner; drum axis along +x at y 300, z 430, "
             "drum centred x 150..850; guard posts at the envelope corners",
    "supports": "plinth + two saddles + 8 slab anchors; guard frame per A-MACH",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 120, 8 mm clear at the bore; "
                     "drain at x 460, vent at x 540; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
