"""COLD_MILL manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down/guard frame pins the box so the
  X-PAR-04 envelope registry reads the build.
- Machine per the unit's own duty sheet and the AQS-MFG-010 tool row (Table 2.1,
  rev C metering split): two-high cold rolling mill, nameplate 2.2 kW; energy
  basis 250 MPa x strain 2.3 / 0.55 (DIETER1988) = 0.0324 kWh/kg plus 15 % no-load
  x 1 h (A-M-177 metal-forming basis). Duty section 3: 316L where the stream is
  wet - the mill is a dry forming machine (no wetted stream on the graph), so the
  CA rule reads 0 mm shop practice and the wet-stream 316L row is carried for the
  connections.
- Housing, rolls and screw-downs are the house two-high idiom: two vertical
  housings on a bedplate, crown tie, upper and lower work rolls with journals,
  screw-down studs on the crown, entry/exit strip tables on the pass line, drive
  gearbox and motor as purchased envelopes with the node nameplate (plan rule 6),
  control cabinet as a purchased envelope. Roll and housing dimensions are study
  values sized to the strip class (holds, WORK_ORDER W12); the strip pass line
  and station arrangement are the layout choice (W12).
- A-MACH: hold-down frame and roll-zone guard drawn; 8 slab anchors
  (fasteners.csv). Purchased items named with the rating from the node
  (2.2 kW drive set).
- A-SC: the parts the on-site shop makes (housing, bedplate, tables, guard,
  connections) are flagged make with the AQS-BOM-SC-001 cross-reference; the
  drive set and cabinet are buy rows.
- Nozzles: all 4 rows of docs-authority/nozzles/COLD_MILL.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1 melt/
  strand in on -Y at z 160; N2 sheet/strip out on +Y at z 600 (the schedule datum
  is a placeholder above the pass line - hold, W12); N3 drain flush at the
  envelope bottom (50 datum); N4 vent flush at the envelope top (800 datum is the
  box top). The schedule rating column (Class 150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("COLD_MILL")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
BED_Z = 60.0                                               # bedplate top
HOU_T, HOU_W = 40.0, 360.0                                 # housing thickness/width (study)
HOU_X = (230.0, 530.0)                                     # housing stations (study, W12)
HOU_Z1 = 620.0
CROWN_T = 40.0
ROLL_D, ROLL_LEN = 120.0, 300.0                            # work rolls (study, W12)
ROLL_L, ROLL_U = 240.0, 365.0                              # lower/upper roll centres; gap 5
JOUR_D = 40.0                                              # roll journal diameter
SCREW_R, SCREW_H = 15.0, 40.0                              # screw-down studs
PASS_Z = 302.5                                             # pass line at the roll gap
TAB_T = 8.0                                                # strip table plate
KW_NAME = 2.2                                              # nameplate, AQS-MFG-010 Table 2.1
MAT = "316L"
CA = materials.ca_for(MAT)
RHO_CS = materials.density("CS")
RHO_TOOL = materials.density("tool_steel")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
CY = W / 2
assert ROLL_U - ROLL_L - ROLL_D == 5.0, "the roll gap is the 5 mm strip class"
assert HOU_Z1 + CROWN_T + 60.0 <= H, "crown + screw-downs stay under the top rails"


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

# ---------------------------------------------------------------- bedplate + housings + crown
parts["bedplate"] = box(140.0, CY - 240.0, T_PLINTH, 520.0, 480.0, BED_Z - T_PLINTH)
housing = None
for hx in HOU_X:
    h = box(hx, CY - HOU_W / 2, BED_Z, HOU_T, HOU_W, HOU_Z1 - BED_Z)
    housing = h if housing is None else housing.union(h)
parts["housings"] = housing
parts["crown"] = box(HOU_X[0], CY - HOU_W / 2, HOU_Z1, HOU_X[1] + HOU_T - HOU_X[0],
                     HOU_W, CROWN_T)

# ---------------------------------------------------------------- work rolls + journals (two-high)
parts["roll_lower"] = rod(ROLL_D / 2, (HOU_X[0] + HOU_T / 2 - ROLL_LEN / 2, CY, ROLL_L), "X", ROLL_LEN)
parts["roll_upper"] = rod(ROLL_D / 2, (HOU_X[0] + HOU_T / 2 - ROLL_LEN / 2, CY, ROLL_U), "X", ROLL_LEN)
journals = None
for rz in (ROLL_L, ROLL_U):
    for jx in (HOU_X[0] - 46.0, HOU_X[1] + HOU_T):   # journal stubs outboard of the housings
        j = rod(JOUR_D / 2, (jx, CY, rz), "X", 46.0)
        journals = j if journals is None else journals.union(j)
parts["journals"] = journals

# ---------------------------------------------------------------- screw-downs on the crown
screws = None
for sx in (HOU_X[0] + HOU_T / 2, HOU_X[1] + HOU_T / 2):
    s = rod(SCREW_R, (sx, CY, HOU_Z1 + CROWN_T), "Z", SCREW_H)
    screws = s if screws is None else screws.union(s)
parts["screw_downs"] = screws

# ---------------------------------------------------------------- entry/exit strip tables (pass line)
entry = box(180.0, POST, PASS_Z - TAB_T / 2, 440.0, CY - POST - 10.0, TAB_T)
exit_tab = box(180.0, CY + 10.0, PASS_Z - TAB_T / 2, 440.0, W - POST - (CY + 10.0), TAB_T)
parts["strip_tables"] = entry.union(exit_tab)

# ---------------------------------------------------------------- drive group + cabinet (purchased envelopes)
parts["gearbox"] = box(60.0, CY - 80.0, ROLL_L - 80.0, 170.0, 160.0, 160.0)
parts["drive_motor"] = rod(60.0, (0.0, CY, ROLL_L), "X", 60.0)
parts["control_cabinet"] = box(700.0, 180.0, T_PLINTH, 260.0, 240.0, 620.0)

# ---------------------------------------------------------------- roll-zone guard rail (A-MACH)
posts = None
for gx, gy in ((240.0, 80.0), (560.0, 80.0), (240.0, W - 80.0), (560.0, W - 80.0)):
    p_ = cq.Workplane("XY", origin=(gx, gy, BED_Z)).circle(10.0).extrude(400.0)
    posts = p_ if posts is None else posts.union(p_)
rails = None
for zz in (PASS_Z - 120.0, PASS_Z + 60.0, PASS_Z + 200.0):
    for gy in (80.0, W - 80.0):
        r_ = cq.Workplane("YZ", origin=(240.0, gy, zz)).circle(10.0).extrude(320.0)
        rails = r_ if rails is None else rails.union(r_)
for zz in (PASS_Z - 120.0, PASS_Z + 60.0, PASS_Z + 200.0):
    rails = rails.union(box(235.0, 74.0, zz, 330.0, 12.0, 12.0))
    rails = rails.union(box(235.0, W - 86.0, zz, 330.0, 12.0, 12.0))
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
    assert span <= L - 300.0, (face, z, span)
    x = 200.0 - span / 2
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
        s = nozzles.place_on_face(s, "bottom", 0.0, (350.0, CY - 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (650.0, CY), (L, W, H))
        note = "vent flush at the envelope top; the 800 datum is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        if tag == "N2":
            note += ("; the schedule datum z 600 is a placeholder above the "
                     "strip pass line (hold, WORK_ORDER W12)")
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
RHO_OF = {"roll_lower": RHO_TOOL, "roll_upper": RHO_TOOL}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_CS) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "two-high cold rolling mill per the duty sheet and the "
                "AQS-MFG-010 tool row (Table 2.1, rev C metering split): bedplate, "
                f"two vertical housings ({HOU_T:g} x {HOU_W:g}, study) with crown "
                f"tie, upper/lower work rolls OD {ROLL_D:g} x {ROLL_LEN:g} "
                f"(5 mm gap at the strip class), journals, screw-down studs, "
                "entry/exit strip tables on the pass line, drive gearbox and "
                "motor as purchased envelopes, control cabinet as a purchased "
                "envelope; roll-zone guard rail (A-MACH) + hold-down frame",
        "tool_row": "AQS-MFG-010 Table 2.1: Two-high cold rolling mill, nameplate "
                    "2.2 kW; energy basis 250 MPa x strain 2.3 / 0.55 (DIETER1988) "
                    "= 0.0324 kWh/kg + no-load 15 % x 1 h (A-M-177)",
        "pass_line": {"z_mm": PASS_Z, "gap_mm": 5.0,
                      "basis": "roll centres are study values; the strip pass "
                               "line is the layout choice (WORK_ORDER W12)"},
        "material": "316L where the stream is wet (duty section 3); the mill is a "
                    "dry forming machine - no wetted stream on the graph; CA 0 mm",
        "ca_mm": CA,
        "purchased": "drive gearbox + motor (2.2 kW nameplate, AQS-MFG-010) and "
                     "control cabinet per plan rule 6, ratings from the node",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04); roll-zone guard rail on 4 posts x 3 tiers; 8 slab "
                 "anchors (fasteners.csv)",
        "study_dims": "housing, roll and table dimensions are study values sized "
                      "to the strip class (WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 strand in on -Y at z 160; N2 sheet/strip out on +Y "
                    "at z 600 (schedule datum is a placeholder above the pass "
                    "line - hold, W12); drain flush at the envelope bottom (50 "
                    "datum); vent flush at the envelope top (800 datum is the box "
                    "top); no flange drawn (W4 110 % rule); the schedule rating "
                    "column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "frame pins the registry box (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", "Mill bedplate and two vertical housings with crown tie (two-high "
           "housing idiom)", 1, "carbon steel (ASTM A500)",
     mass["bedplate"] + mass["housings"] + mass["crown"], "make (AQS-BOM-SC-001)",
     "housing sections study (hold, WORK_ORDER W12); CA 0 mm (AQS-STD-001)"],
    ["4", f"Work rolls OD {ROLL_D:g} x {ROLL_LEN:g}, 2 off (5 mm gap), with "
           f"journals OD {JOUR_D:g}", 2, "tool steel (AR400/D2 class, lib table)",
     mass["roll_lower"] + mass["roll_upper"] + mass["journals"], "make (AQS-BOM-SC-001)",
     "two-high rolls per the AQS-MFG-010 tool row; roll size study (W12); journals "
     "turned in the shop lathe"],
    ["5", "Screw-down studs on the crown, 2 off", 2, "carbon steel",
     mass["screw_downs"], "make (AQS-BOM-SC-001)",
     "gap adjustment hardware; layout choice (W12)"],
    ["6", "Entry/exit strip tables on the pass line", 1, "carbon steel",
     mass["strip_tables"], "make (AQS-BOM-SC-001)",
     f"pass line z {PASS_Z:g}; tables are the layout choice (W12)"],
    ["7", "Roll-zone guard rail, 4 posts x 3 tiers (A-MACH: guard drawn)", 1,
     "CS tube", mass["guard_rail"], "make (AQS-BOM-SC-001)",
     "guard over the rotating roll zone; layout choice (W12)"],
    ["8", "Drive gearbox + motor (purchased, envelope and interface)", 1,
     "purchased drive (envelope)", mass["gearbox"] + mass["drive_motor"], "buy",
     f"nameplate {KW_NAME:g} kW (AQS-MFG-010 Table 2.1; node stamp); purchased per "
     "plan rule 6"],
    ["9", "Control cabinet (purchased, envelope and interface)", 1,
     "purchased cabinet (envelope)", mass["control_cabinet"], "buy",
     "purchased per plan rule 6; mass a table-density placeholder until the maker "
     "TDS quotes (W12)"],
    ["10", "Nozzle set per docs-authority/nozzles/COLD_MILL.csv: 4 DN15 stubs", len(schedule),
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
    [None, "M16 journal-block bolt + nut", fasteners.grade_for("CS"), 8,
     "roll journal blocks to the housings, 2 per journal (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "housing": {"stations_x_mm": HOU_X, "t_mm": HOU_T, "w_mm": HOU_W, "z1_mm": HOU_Z1},
    "rolls": {"od_mm": ROLL_D, "len_mm": ROLL_LEN, "centres_z_mm": [ROLL_L, ROLL_U],
              "gap_mm": 5.0, "pass_line_z_mm": PASS_Z},
    "cabinet_mm": [700.0, 180.0, 260.0, 240.0, 620.0],
}
p["design"] = {
    "service": "COLD_MILL: melt rolled to sheet/strip for the shop and goods lines "
               "(duty sections 1 and 4; strand IA-MELT-MILL in, S59 out)",
    "tool_row": "AQS-MFG-010 Table 2.1: two-high cold rolling mill, nameplate "
                "2.2 kW; 250 MPa x strain 2.3 / 0.55 (DIETER1988) + 15 % no-load "
                "(A-M-177)",
    "material": "316L where the stream is wet (duty section 3); dry forming "
                "machine, no wetted stream on the graph",
    "ca_mm": CA,
    "material_basis": "duty section 3; CA 0 mm shop rule (AQS-STD-001)",
    "purchased": "drive set (2.2 kW nameplate) and control cabinet, plan rule 6 "
                 "envelopes with the node ratings",
}
p["layout"] = {
    "frame": "origin at the envelope corner; housings x 230/530 on the bedplate, "
             "roll axes along x at the pass line z 302.5, strip along y; drive "
             "train -X, control cabinet x 700..960; hold-down posts at the "
             "envelope corners; roll-zone guard rail over the pass line",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1 on -Y at z 160, "
                     "N2 on +Y at z 600 (schedule placeholder above the pass "
                     "line), drain at x 350, vent at x 650; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
