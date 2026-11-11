"""WIRE_DRAW manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid. The DRAW accepted model (commit 30f5abf4, bench wire/rod draw bench) is
the idiom this wire variant reuses: bench bed, die stand with die casings, take-up
drum with the drive group, wire guides, and the guard rail - scaled to the node box
and to the bull-block machine class the AQS-MFG-010 tool row names.

Placement frame: x along 1000 mm (x 0 = die-stand tail, x 1000 = bull-block head),
y along 600 mm, z up, origin at the envelope corner. Every dimension is an authority
figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down/guard frame and the vent riser pin the
  box so the X-PAR-04 envelope registry reads the build.
- Machine per the unit's own duty sheet and the AQS-MFG-010 tool row (Table 2.1,
  rev C metering split): bull-block wire drawer, nameplate 1.1 kW; energy basis
  250 MPa x strain 3.0 / 0.55 (DIETER1988) = 0.0423 kWh/kg + no-load 15 % x 1 h
  (A-M-177 metal-forming basis). Duty section 3: 316L where the stream is wet -
  the drawer is a dry forming machine (the capstan hardware carries the machine
  lubricant programme), so CA 0 mm shop practice applies and the 316L row is
  carried for the connection stubs.
- Machine per the DRAW idiom: steel bench bed on legs, die stand with the tungsten-
  carbide die set in tool-steel casings (consumable buy set; die count is a study
  value - hold, W12), bull-block take-up drum with shaft, wire-guide sheaves, a
  draw-fume extraction hood over the die zone (the N4 fume row routes to the
  house scrubber train), drive group and control cabinet as purchased envelopes
  (nameplate 1.1 kW from the node stamp, plan rule 6). Drum, bench and die-station
  dimensions are study values (holds, WORK_ORDER W12); the pass line and station
  arrangement are the layout choice (W12).
- A-MACH: hold-down/guard frame + die-zone/drum guard rail; 8 slab anchors
  (fasteners.csv). Purchased items named with the rating from the node.
- A-SC: the parts the on-site shop makes (bench, die stand, guards, guides,
  connections) are flagged make with the AQS-BOM-SC-001 cross-reference; the die
  set, drive group and cabinet are buy rows.
- Nozzles: all 7 rows of docs-authority/nozzles/WIRE_DRAW.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1 billet in
  on -Y at z 160 and N7 rod/wire stock in (solids row, drawn DN15, bore not
  calculated, plan W4) beside it; N2 wire product out, N3 draw scrap out and N4
  draw fume out on +Y at z 600; N5 drain flush at the envelope bottom (50 datum);
  N6 vent flush at the envelope top (800 datum is the box top). The schedule
  rating column (Class 150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("WIRE_DRAW")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
CY = 300.0                                                 # bench centreline (layout, W12)
BED_X0, BED_X1 = 100.0, 700.0
BED_Z0, BED_Z1 = 300.0, 420.0                              # bench bed section
BLOCK_D, BLOCK_W = 300.0, 140.0                            # bull-block drum (study, W12)
BLOCK_X = 780.0
OUT_Z = 600.0                                              # take-off / wire-out datum
N_DIES = 4                                                 # die set (study, W12)
KW_NAME = 1.1                                              # nameplate, AQS-MFG-010 Table 2.1
RHO_CS = materials.density("CS")
RHO_TOOL = materials.density("tool_steel")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert BLOCK_X + BLOCK_D / 2 <= L - POST, "bull block clears the frame"
assert BLOCK_D / 2 * 2 <= W - 2 * POST, "drum clears the posts"
assert BED_Z1 + 40.0 <= H, "hood clears the bench"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down/guard frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- bench bed + legs (DRAW idiom)
parts["bench_bed"] = box(BED_X0, CY - 100.0, BED_Z0, BED_X1 - BED_X0, 200.0, BED_Z1 - BED_Z0)
for lx, ly in ((BED_X0 + 20.0, 120.0), (BED_X0 + 20.0, CY + 180.0),
               (BED_X1 - 220.0, 120.0), (BED_X1 - 220.0, CY + 180.0)):
    parts["bench_bed"] = parts["bench_bed"].union(box(lx, ly, T_PLINTH, 60.0, 40.0, BED_Z0 - T_PLINTH))

# ---------------------------------------------------------------- die stand (-X head) with die casings
parts["die_stand"] = box(BED_X0, CY - 140.0, BED_Z1, 120.0, 280.0, 300.0)
dies = None
for i in range(N_DIES):
    dx = BED_X0 + 25.0 + (i % 2) * 50.0
    dz = BED_Z1 + 50.0 + (i // 2) * 90.0
    d_ = rod(28.0, (dx, CY, dz), "X", 56.0)                # carbide die in its tool-steel casing
    dies = d_ if dies is None else dies.union(d_)
parts["die_set"] = dies

# ---------------------------------------------------------------- bull-block drum + shaft + wire guides
parts["bull_block"] = rod(BLOCK_D / 2, (BLOCK_X - BLOCK_W / 2, CY, OUT_Z), "Y", BLOCK_W)
parts["block_shaft"] = rod(35.0, (BLOCK_X - 130.0, CY, OUT_Z), "Y", 260.0)
guides = None
for gx in (BED_X0 + 180.0, BED_X0 + 380.0, BED_X1 - 60.0):
    g_ = rod(20.0, (gx, CY - 90.0, OUT_Z - 160.0), "Z", 120.0)
    guides = g_ if guides is None else guides.union(g_)
parts["wire_guides"] = guides

# ---------------------------------------------------------------- draw-fume hood over the die zone
parts["fume_hood"] = box(BED_X0 - 20.0, CY - 160.0, BED_Z1 + 200.0, 240.0, 320.0, 60.0)

# ---------------------------------------------------------------- drive group + cabinet (purchased envelopes)
parts["drive_group"] = box(BED_X1, CY - 140.0, T_PLINTH, L - BED_X1 - POST - 40.0, 280.0, 300.0)
parts["control_cabinet"] = box(60.0, 440.0, T_PLINTH, 240.0, 120.0, 700.0)

# ---------------------------------------------------------------- guard rail over the die zone and drum (A-MACH)
posts = None
for gx, gy in ((220.0, 110.0), (740.0, 110.0), (220.0, W - 110.0), (740.0, W - 110.0)):
    p_ = cq.Workplane("XY", origin=(gx, gy, T_PLINTH)).circle(10.0).extrude(720.0)
    posts = p_ if posts is None else posts.union(p_)
rails = None
for gy in (110.0, W - 110.0):
    for zz in (360.0, 480.0, 700.0):
        r_ = cq.Workplane("YZ", origin=(220.0, gy, zz)).circle(10.0).extrude(520.0)
        rails = r_ if rails is None else rails.union(r_)
for zz in (360.0, 480.0, 700.0):
    rails = rails.union(box(214.0, 100.0, zz, 532.0, 20.0, 20.0))
parts["guard_rail"] = posts.union(rails)

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
    assert span <= L - 120.0, (face, z, span)
    x = max(60.0, (L - span) / 2)
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
    if r["face"] == "bottom":                             # N5: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (450.0, CY - 100.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N6: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (720.0, CY), (L, W, H))
        note = "vent flush at the envelope top; the 800 datum is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
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
RHO_OF = {"die_set": RHO_TOOL}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_CS) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "bull-block wire drawer per the duty sheet and the AQS-MFG-010 "
                "tool row (Table 2.1, rev C metering split), built on the DRAW "
                "accepted idiom (commit 30f5abf4) scaled to the node box: steel "
                "bench bed on legs, die stand with the tungsten-carbide die set "
                "in tool-steel casings (consumable buy set), bull-block take-up "
                "drum OD 300 with shaft, wire-guide sheaves, draw-fume extraction "
                "hood over the die zone, drive group and control cabinet as "
                "purchased envelopes; die-zone/drum guard rail (A-MACH) + "
                "hold-down frame",
        "tool_row": "AQS-MFG-010 Table 2.1: Bull-block wire drawer, nameplate "
                    "1.1 kW; energy basis 250 MPa x strain 3.0 / 0.55 (DIETER1988) "
                    "= 0.0423 kWh/kg + no-load 15 % x 1 h (A-M-177)",
        "bench": {"bed_x_mm": [BED_X0, BED_X1], "z_mm": [BED_Z0, BED_Z1],
                  "basis": "DRAW bench idiom scaled to the node box; study "
                           "sections (hold, WORK_ORDER W12)"},
        "die_set": {"count": N_DIES, "basis": "tungsten-carbide drawing dies in "
                    "tool-steel casings (duty section 3 class, DIETER1988 ch. "
                    "20/21); consumable buy set; the die count is a study value "
                    "(hold, WORK_ORDER W12)"},
        "bull_block": {"od_mm": BLOCK_D, "w_mm": BLOCK_W, "axis_z_mm": OUT_Z,
                       "basis": "study drum size (hold, WORK_ORDER W12); the "
                       "capstan hardware carries the machine lubricant programme "
                       "- no wetted stream (duty section 3)"},
        "fume": "the N4 draw-fume row routes to the house scrubber train; the "
                "extraction hood over the die zone is the layout choice (W12)",
        "purchased": "drive group and control cabinet on their bays, drawn as "
                     f"their envelopes per plan rule 6 (nameplate {KW_NAME:g} kW "
                     "is the node stamp); the carbide die set is the purchased "
                     "consumable",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04); die-zone and drum guard rail on 4 posts x 3 tiers; "
                 "8 slab anchors (fasteners.csv)",
        "material": "316L where the stream is wet (duty section 3); dry forming "
                    "machine - CA 0 mm",
        "ca_mm": 0.0,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 billet in and N7 rod/wire stock in (solids row "
                    "drawn DN15, bore not calculated, plan W4) on -Y at z 160; "
                    "N2 wire product, N3 draw scrap and N4 draw fume on +Y at "
                    "z 600; drain flush at the envelope bottom (50 datum); vent "
                    "flush at the envelope top (800 datum is the box top); no "
                    "flange drawn (W4 110 % rule); the schedule rating column "
                    "(Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make (AQS-BOM-SC-001)", "dry machine-shop floor service, CA 0 mm "
     "(AQS-STD-001 shop rule); anchors in fasteners.csv"],
    ["2", f"Bench bed {BED_X1 - BED_X0:g} long on 4 legs (DRAW bench idiom scaled "
           "to the node box)", 1, "carbon steel",
     mass["bench_bed"] + mass["die_stand"], "make (AQS-BOM-SC-001)",
     "duty section 3: steel bench; study sections (WORK_ORDER W12)"],
    ["3", f"Tungsten-carbide drawing die set, {N_DIES} dies in tool-steel casings", 1,
     "carbide + tool steel (consumable set)", mass["die_set"], "buy",
     "duty section 3 class (DIETER1988 ch. 20/21); consumable, buy; the die count "
     "is a study value (hold, WORK_ORDER W12)"],
    ["4", f"Bull-block take-up drum OD {BLOCK_D:g} with shaft and wire-guide "
           "sheaves", 1, "carbon steel",
     mass["bull_block"] + mass["block_shaft"] + mass["wire_guides"],
     "make (AQS-BOM-SC-001)",
     "duty section 3: capstan hardware carries the machine lubricant programme "
     "(no wetted stream); drum size is the study value (hold, WORK_ORDER W12)"],
    ["5", "Draw-fume extraction hood over the die zone (N4 routes to the house "
           "scrubber train)", 1, "carbon steel", mass["fume_hood"],
     "make (AQS-BOM-SC-001)", "layout choice (WORK_ORDER W12)"],
    ["6", "Drive group on the drum bay (purchased, envelope and interface)", 1,
     "purchased drive (envelope)", mass["drive_group"], "buy",
     f"purchased per plan rule 6; nameplate {KW_NAME:g} kW is the node stamp "
     "(AQS-MFG-010 Table 2.1)"],
    ["7", "Control cabinet (purchased, envelope and interface)", 1,
     "purchased cabinet (envelope)", mass["control_cabinet"], "buy",
     "purchased per plan rule 6; mass a table-density placeholder until the maker "
     "TDS quotes (W12)"],
    ["8", "Die-zone and bull-block guard rail, 4 posts x 3 tiers (A-MACH: guard "
           "drawn)", 1, "CS tube", mass["guard_rail"], "make (AQS-BOM-SC-001)",
     "guard over the die zone and rotating drum; layout choice (WORK_ORDER W12)"],
    ["9", "Nozzle set per docs-authority/nozzles/WIRE_DRAW.csv: 6 DN15 stubs and "
           "1 solids row drawn DN15 bore not calculated", len(schedule),
     "316L tube", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
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
    [None, "M12 drum-bearing block bolt + nut", fasteners.grade_for("CS"), 4,
     "bull-block bearing blocks to the frame bay (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "bench": {"x_mm": [BED_X0, BED_X1], "z_mm": [BED_Z0, BED_Z1]},
    "bull_block": {"od_mm": BLOCK_D, "w_mm": BLOCK_W, "x_mm": BLOCK_X, "axis_z_mm": OUT_Z},
    "die_stand": {"x_mm": [BED_X0, BED_X0 + 120.0], "dies": N_DIES},
    "purchased_bays": {"drive_x_mm": [BED_X1, L - POST],
                       "cabinet_xy_mm": [60.0, 440.0, 300.0, 560.0]},
}
p["design"] = {
    "service": "WIRE_DRAW: billet drawn to wire product (S58); draw scrap returns "
               "and the draw-fume row routes to the house scrubber train (duty "
               "sections 1 and 4)",
    "tool_row": "AQS-MFG-010 Table 2.1: bull-block wire drawer, nameplate 1.1 kW; "
                "250 MPa x strain 3.0 / 0.55 (DIETER1988) + no-load 15 % (A-M-177)",
    "idiom": "the DRAW accepted model (commit 30f5abf4) is the bench idiom this "
             "wire variant reuses, scaled to the node box and the bull-block class",
    "material": "316L where the stream is wet (duty section 3); dry forming machine",
    "ca_mm": 0.0,
    "material_basis": "duty section 3; CA 0 mm shop rule (AQS-STD-001)",
    "purchased": "drive group and control cabinet (nameplate 1.1 kW, node stamp), "
                 "plan rule 6 envelopes; the carbide die set is the purchased "
                 "consumable",
}
p["layout"] = {
    "frame": "origin at the envelope corner; bench centreline y 300; bed x 100..700 "
             "at z 300..420; die stand on the -X head, bull block +X at z 600 with "
             "the drive bay behind it; control cabinet on the -X floor; guard rail "
             "over the die zone and drum",
    "fume": "extraction hood over the die zone; the N4 row is the fume edge to the "
            "house scrubber train",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1/N7 pack one row "
                     "on -Y at z 160; N2/N3/N4 on +Y at z 600; drain under the "
                     "bench centre, vent on the drum head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
