"""CRU manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box). The
  build stays inside it; a four-post hold-down frame pins the registry box so the
  X-PAR-04 envelope registry reads the build (the vessel itself does not fill the
  box).
- Vessel per the unit's own duty sheet (chlorate finish: scrub liquor in, sodium
  chlorate liquor out, cell-gas sparges in, chlorine out): vertical PVC-U vessel
  OD 520, wall 10 mm (study - the duty states no diameter and no wall: drawn to
  the envelope, holds W12), z 40..700, with welded top and bottom, on a 20 mm
  plinth inside the hold-down frame. Material PVC-U per duty section 3
  ("PVC-U wetted, per AQS-STD-002 rules M1 and M2. No metal wetted part. The
  graph gives no temperature for this unit; above 60 C the thermoplastic is
  CPVC, never metal") - CA does not apply to the polymer. The 60 C watch point
  is carried as a named hold (W12): no operating temperature is stated on the
  graph.
- A-VES: the holdup volume is reported from the model; the duty states "No
  holdup basis for this class", so no residence time is derived.
- Nozzles: all 12 rows of docs-authority/nozzles/CRU.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: nozzle DN15, no flange class, atmospheric tube or hose). The
  six gas rows (N5-N8, N9, N10) are the cell-gas and chlorine connections and
  stay on their gas edges (duty section 5/6: not to the room). Drain flush at
  the envelope bottom (50 datum); vent flush at the envelope top (800 datum is
  the box top). The schedule rating column (Class 150) is carried verbatim as
  text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("CRU")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
V_OD, T_WALL = 520.0, 10.0                                 # to the envelope; study values (W12)
V_ID = V_OD - 2 * T_WALL
Z0, Z1 = 40.0, H - 120.0                                   # vessel 40..680
CX, CY = L / 2, W / 2
HOLDUP_REF_MM = Z1 - 100.0                                 # report level: 100 mm below the top weld
POST = 40.0                                                # hold-down frame section
MAT = "PVC_U"                                              # duty section 3
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001 polymer rule
RHO = materials.density(MAT)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert V_OD <= W - 80.0 and Z1 <= H - 100.0, "vessel drawn to the envelope"
V_HOLDUP_L = math.pi / 4 * V_ID ** 2 * (HOLDUP_REF_MM - Z0 - T_WALL) / 1e6


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- vessel (duty sheet, drawn to the envelope)
vessel = (cq.Workplane("XY", origin=(CX, CY, Z0)).circle(V_OD / 2)
          .circle(V_ID / 2).extrude(Z1 - Z0))
vessel = vessel.union(cq.Workplane("XY", origin=(CX, CY, Z0)).circle(V_OD / 2)
                      .extrude(T_WALL))                     # bottom
vessel = vessel.union(cq.Workplane("XY", origin=(CX, CY, Z1 - T_WALL)).circle(V_OD / 2)
                      .extrude(T_WALL))                     # welded top
vessel = vessel.union(cq.Workplane("XY", origin=(CX - 200.0, CY - 200.0, T_PLINTH))
                      .box(400.0, 400.0, Z0 - T_PLINTH, centered=False))  # seat (fuse into the bottom)
parts["vessel"] = vessel

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
    x = 150.0 - span / 2
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
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, CY), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, CY), (L, W, H))
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
mass = {k: round(v.val().Volume() * (RHO if k != "plinth" and k != "frame"
                                     else materials.density("CS")) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "vessel": {
        "type": "vertical PVC-U chlorate-finish vessel drawn to the node envelope: "
                "shell OD 520 (drawn to the envelope - the duty states no "
                "diameter), wall 10 (study), welded top and bottom, seat, inside "
                "a four-post hold-down frame on a 20 mm plinth",
        "od_mm": V_OD, "wall_mm": T_WALL, "z_mm": [Z0, Z1],
        "wall_basis": "study values; the duty states no diameter and no wall "
                      "(holds, WORK_ORDER W12)",
        "material": "PVC-U (duty section 3: AQS-STD-002 rules M1 and M2; no metal "
                    "wetted part); CA does not apply to the polymer",
        "temp_watch": "the graph gives no temperature for this unit; above 60 C "
                      "the thermoplastic is CPVC, never metal (duty section 3) - "
                      "named hold, WORK_ORDER W12",
        "holdup_model_l": round(V_HOLDUP_L, 1),
        "holdup_note": f"A-VES: the vessel holds {V_HOLDUP_L:.1f} L to 100 mm "
                       "below the top weld; the duty states no holdup basis for "
                       "this class, so no residence time is derived",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: nozzle DN15, no flange class, atmospheric "
                    "tube or hose); the gas rows (cell gas in, chlorine out) stay "
                    "on their gas edges, not the room (duty sections 5 and 6); "
                    "the schedule rating column (Class 150) is carried verbatim "
                    "as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Vessel shell OD {V_OD:g}, wall {T_WALL:g} mm (study), z {Z0:g}..{Z1:g}, "
          "welded top and bottom, on a seat to the plinth", 1,
     "PVC-U (duty section 3: AQS-STD-002 M1/M2)", mass["vessel"], "make",
     "drawn to the node envelope - the duty states no diameter or wall (holds, "
     "WORK_ORDER W12); CA does not apply to the polymer (AQS-STD-001); holdup "
     "report in check.vessel"],
    ["2", f"Four-post hold-down frame pinning the {L:g} x {W:g} x {H:g} envelope "
          f"(40 x 40 posts, top rails), + plinth {L:g} x {W:g} x {T_PLINTH:g}", 1,
     "carbon steel (ASTM A500)", mass["frame"] + mass["plinth"], "make",
     "HX8 hold-down idiom: the frame pins the registry box so the build fills the "
     "node envelope (X-PAR-04); AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["3", "Nozzle set per docs-authority/nozzles/CRU.csv: 10 open-bore tube stubs "
          "(DN15/DN25; the six gas rows stay on their gas edges), drain and vent "
          "flush at the envelope faces", len(schedule), "PVC-U", mass["nozzles"],
     "make",
     "12-row issued schedule verbatim; atmospheric tube per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "vessel": {"od_mm": V_OD, "wall_mm": T_WALL, "z_mm": [Z0, Z1],
               "axis_mm": [CX, CY]},
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "CRU: chlorine recovery and chlorate finish - scrub liquor in, "
               "sodium chlorate liquor out, cell-gas sparges in, chlorine to the "
               "fluoro trains, atmospheric (duty sections 1, 4 and 6)",
    "material": MAT, "ca_mm": CA,
    "ca_basis": "CA does not apply to the polymer (AQS-STD-001 rule)",
    "material_basis": "duty section 3: PVC-U wetted per AQS-STD-002 rules M1 and "
                      "M2; no metal wetted part; above 60 C the thermoplastic is "
                      "CPVC, never metal (temperature watch, hold W12)",
    "wall_mm": T_WALL, "wall_basis": "study value (hold W12)",
    "holdup_model_l": round(V_HOLDUP_L, 1),
}
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at x 500, y 300, shell "
             "z 40..680; hold-down posts at the envelope corners",
    "supports": "plinth + vessel seat + hold-down frame + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 150, 8 mm clear at the "
                     "bore; drain at x 430, vent at x 570; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"holdup_model_l": round(V_HOLDUP_L, 1)}))
