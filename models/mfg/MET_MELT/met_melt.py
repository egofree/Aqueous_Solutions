"""MET_MELT manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 7, F-VES).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down frame and the hood vent riser pin the
  box so the X-PAR-04 envelope registry reads the build.
- Machine per the unit's own duty sheet and the AQS-MFG-010 tool row: coreless
  induction melt furnace, 10 kg Cu crucible class, nameplate 7.5 kW (Table 2.1,
  rev C metering split). Duty section 3 construction: graphite or refractory on
  the hot face; frame A500 behind a heat shield; CA 0 mm on the frame. A-M-177
  melt basis: eta 0.55, 10 kg charge, 0.5 h melt, 100 K superheat. The duty
  section 2 holdup basis is the 1 h charge V = (13.99/1000) x (1/24) = 0.0006 m3;
  the crucible is sized to it (bore 100 x melt line 80 => 0.63 L) and the model
  holdup is reported against the duty figure (A-VES), not used as a new rate.
- Furnace per the IND_MELT accepted idiom (AQS-PLAN-006 lane): CS casing with
  base head and top head, refractory hot face, induction coil band (copper),
  clay-graphite crucible (buy consumable, change-out per campaign), tilt trunnions,
  pour lip toward +Y (the three melt-out rows), fume hood over the furnace with
  the vent riser at the box top, power-supply cabinet as a purchased envelope
  (nameplate 7.5 kW from the node stamp, plan rule 6). Casing, coil and crucible
  dimensions are study values (holds, WORK_ORDER W12).
- A-MACH practice: hold-down frame is the guard; 8 slab anchors (fasteners.csv).
- A-SC: the parts the on-site shop makes (casing, frame, plinth, hood, shield,
  spouts, connections) are flagged make with the AQS-BOM-SC-001 cross-reference;
  the crucible and the power supply are buy rows.
- Nozzles: all 7 rows of docs-authority/nozzles/MET_MELT.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1 cathode
  sheet charge in on -Y at z 160; N7 off-spec powder return (solids row) on -Y at
  z 160, drawn DN15, bore not calculated (plan W4); N2 billet, N3 melt-to-mill and
  N4 melt-to-atomizer pour rows on +Y at z 600 at the pour lip; N5 drain flush at
  the envelope bottom (50 datum); N6 vent on the hood riser flush at the envelope
  top (the 800 datum is the box top). The schedule rating column (Class 150) is
  carried verbatim as text; no flange is drawn (W4 110 % rule).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("MET_MELT")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
CAS_OD, CAS_WALL = 420.0, 6.0                              # furnace casing (study, W12)
FACE_T = 40.0                                              # refractory hot face (study, W12)
COIL_T = 30.0                                              # induction coil band (study, W12)
CRUC_OD, CRUC_WALL = 110.0, 15.0                           # clay-graphite crucible (buy)
CRUC_Z0, CRUC_Z1 = 120.0, 420.0
MELT_H = 80.0                                              # melt line above the crucible floor
CAS_Z0, CAS_Z1 = 60.0, 660.0
LIP_Z = 600.0                                              # pour lip / melt-out row datum
HOOD_Z0, HOOD_Z1 = 700.0, 780.0                            # fume hood over the furnace
KW_NAME = 7.5                                              # nameplate, AQS-MFG-010 Table 2.1
DUTY_V_M3 = 0.0006                                         # duty section 2: 1 h charge basis
MAT = "316L"
CA = materials.ca_for(MAT)
RHO_CS = materials.density("CS")
RHO_CU = materials.density("Cu")
RHO_GRAPH = materials.density("graphite")
RHO_REFR = 2600.0          # published alumina/refractory class midpoint; liner charge,
# supplier TDS governs at order (W12)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
CX, CY = 300.0, W / 2
assert CAS_OD <= W - 2 * 40.0 + 20.0, "casing clears the hold-down posts"
assert CAS_Z1 + 40.0 <= HOOD_Z0, "hood clears the casing"
R_CAS_I = CAS_OD / 2 - CAS_WALL
R_FACE_I = R_CAS_I - FACE_T
R_COIL_O, R_COIL_I = R_FACE_I, R_FACE_I - COIL_T           # coil band inside the hot face
CRUC_X0, CRUC_X1 = CRUC_Z0, CRUC_Z1
V_CRUC_M3 = math.pi / 4 * (CRUC_OD - 2 * CRUC_WALL) ** 2 * MELT_H / 1e9


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def ring_z(cx_, cy_, r_out, r_in, z0, z1):
    return (cq.Workplane("XY", origin=(cx_, cy_, z0)).circle(r_out).circle(r_in)
            .extrude(z1 - z0))


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

# ---------------------------------------------------------------- furnace casing + heads
casing = ring_z(CX, CY, CAS_OD / 2, R_CAS_I, CAS_Z0, CAS_Z1)
casing = casing.union(cq.Workplane("XY", origin=(CX, CY, CAS_Z0))
                      .circle(CAS_OD / 2).extrude(20.0))           # base head (laps plinth)
casing = casing.union(cq.Workplane("XY", origin=(CX, CY, CAS_Z1 - 20.0))
                      .circle(CAS_OD / 2).extrude(20.0))           # top head
parts["casing"] = casing

# ---------------------------------------------------------------- hot face + induction coil band
parts["hot_face"] = ring_z(CX, CY, R_CAS_I, R_COIL_O, CRUC_Z0 - 40.0, CRUC_Z1 + 40.0)
parts["coil"] = ring_z(CX, CY, R_COIL_O, R_COIL_I, CRUC_Z0 - 20.0, CRUC_Z1 + 20.0)

# ---------------------------------------------------------------- crucible (buy consumable) + melt line
cruc = ring_z(CX, CY, CRUC_OD / 2, CRUC_OD / 2 - CRUC_WALL, CRUC_Z0, CRUC_Z1)
cruc = cruc.union(cq.Workplane("XY", origin=(CX, CY, CRUC_Z0))
                  .circle(CRUC_OD / 2).extrude(12.0))                # base
parts["crucible"] = cruc
parts["melt_line"] = cq.Workplane("XY", origin=(CX, CY, CRUC_Z0 + 12.0)) \
    .circle((CRUC_OD - 2 * CRUC_WALL) / 2).extrude(MELT_H)           # process inventory, not a part

# ---------------------------------------------------------------- tilt trunnions + pour lip
trun = None
for tz in (CAS_Z0 + 60.0,):
    for ty in (CY - CAS_OD / 2 - 30.0, CY + CAS_OD / 2 + 30.0):
        t = cq.Workplane("YZ", origin=(CX, ty, tz)).circle(30.0).extrude(60.0)
        trun = t if trun is None else trun.union(t)
parts["trunnions"] = trun
lip = cq.Workplane("XY", origin=(CX - 70.0, CY + CAS_OD / 2 - 4.0, LIP_Z - 30.0))
lip = lip.box(140.0, 60.0, 30.0, centered=False)                     # pour lip over the +Y rows
parts["pour_lip"] = lip

# ---------------------------------------------------------------- heat shield + hood + cabinet
parts["heat_shield"] = box(CX - CAS_OD / 2 - 30.0, CY - CAS_OD / 2 - 30.0,
                           T_PLINTH, 2 * (CAS_OD / 2 + 30.0), 2 * (CAS_OD / 2 + 30.0), 10.0)
hood = box(CX - 260.0, CY - 220.0, HOOD_Z0, 520.0, 440.0, HOOD_Z1 - HOOD_Z0 - 20.0)
hood = hood.union(box(CX - 260.0, CY - 220.0, HOOD_Z1 - 20.0, 520.0, 440.0, 20.0))
parts["hood"] = hood
parts["power_cabinet"] = box(700.0, 180.0, T_PLINTH, 260.0, 240.0, 620.0)

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
    if r["face"] == "bottom":                             # N5: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX, CY - 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N6: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (CX, CY), (L, W, H))
        note = "vent on the hood riser flush at the envelope top; the 800 datum is the box top"
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
RHO_OF = {"coil": RHO_CU, "crucible": RHO_GRAPH, "hot_face": RHO_REFR}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_CS) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "coreless induction melt furnace per the duty sheet and the "
                "AQS-MFG-010 tool row (Table 2.1, rev C metering split): CS casing "
                f"OD {CAS_OD:g} (wall {CAS_WALL:g}, study) with refractory hot face "
                f"{FACE_T:g} mm, induction coil band, clay-graphite crucible "
                f"(OD {CRUC_OD:g}, bore {CRUC_OD - 2 * CRUC_WALL:g}), tilt "
                "trunnions and pour lip toward +Y (the three melt-out rows), fume "
                "hood with the vent riser at the box top, power-supply cabinet as "
                "a purchased envelope; hold-down frame is the guard (A-MACH "
                "practice)",
        "tool_row": "AQS-MFG-010 Table 2.1: Induction melt furnace, coreless, "
                    "10 kg Cu crucible, nameplate 7.5 kW",
        "a177": "A-M-177 melt basis: eta 0.55, 10 kg charge, 0.5 h melt, 100 K "
                "superheat",
        "holdup": {"crucible_m3": round(V_CRUC_M3, 6),
                   "duty_basis_m3": DUTY_V_M3,
                   "note": "duty section 2: V = (13.99/1000) x (1/24) = 0.0006 m3, "
                           "1 h charge; the crucible melt line is sized to it and "
                           "the model figure is reported (A-VES), not used as a "
                           "new rate; the melt solid is process inventory, not a "
                           "BOM part and not an internal"},
        "material": "graphite/refractory hot face; frame A500 behind a heat shield "
                    "(duty section 3); CA 0 mm on the frame",
        "ca_mm": CA,
        "purchased": {"crucible": "clay-graphite crucible, buy consumable "
                                  "(change-out per campaign, IND_MELT W6 idiom)",
                      "power_supply": "7.5 kW nameplate (AQS-MFG-010 Table 2.1); "
                                      "purchased per plan rule 6, rating from the "
                                      "node stamp"},
        "guard": "four-post hold-down/guard frame (40 x 40 posts, top rails) pins "
                 "the registry box (X-PAR-04); 8 slab anchors (fasteners.csv)",
        "study_dims": "casing, coil and crucible dimensions are study values sized "
                      "to the 10 kg class at the bench box (WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 charge in and N7 solids powder return on -Y at "
                    "z 160 (N7 drawn DN15, bore not calculated, plan W4); N2/N3/N4 "
                    "pour rows on +Y at z 600 at the pour lip; drain flush at the "
                    "envelope bottom (50 datum); vent on the hood riser flush at "
                    "the envelope top (the 800 datum is the box top); no flange "
                    "drawn (W4 110 % rule - no process pressure stated); the "
                    "schedule rating column (Class 150) carried verbatim as text",
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
    ["3", f"Furnace casing OD {CAS_OD:g} (wall {CAS_WALL:g}, study) with heads", 1,
     "carbon steel (duty section 3 frame class)", mass["casing"], "make (AQS-BOM-SC-001)",
     "duty section 3: frame A500 behind a heat shield; shell dimensions study (W12); "
     "CA 0 mm - dry, non-hydrocarbon furnace service (AQS-STD-001)"],
    ["4", f"Refractory hot face {FACE_T:g} mm band inside the casing", 1,
     "refractory liner charge (supplier TDS governs)", mass["hot_face"], "buy",
     "duty section 3: graphite or refractory on the hot face; density is the "
     "published refractory class midpoint (study)"],
    ["5", f"Induction coil band {COIL_T:g} mm between hot face and crucible", 1,
     "copper tube (study section, W12)", mass["coil"], "make (AQS-BOM-SC-001)",
     "coreless induction per the AQS-MFG-010 tool row; A-M-177 eta 0.55; coil "
     "section is a study value"],
    ["6", f"Clay-graphite crucible OD {CRUC_OD:g} (bore {CRUC_OD - 2 * CRUC_WALL:g}), "
           "10 kg Cu class", 1, "clay-graphite (buy consumable, change-out per campaign)",
     mass["crucible"], "buy",
     "duty section 3; IND_MELT W6 consumable idiom; maker TDS mass governs at order"],
    ["7", "Tilt trunnions and pour lip over the +Y melt-out rows", 1,
     "carbon steel", mass["trunnions"] + mass["pour_lip"], "make (AQS-BOM-SC-001)",
     "pour lip at z 600 over the N2/N3/N4 rows; layout choice (W12)"],
    ["8", "Heat shield plate under the frame line", 1, "carbon steel",
     mass["heat_shield"], "make (AQS-BOM-SC-001)",
     "duty section 3: frame behind a heat shield"],
    ["9", "Fume hood over the furnace with the vent riser at the box top", 1,
     "carbon steel", mass["hood"], "make (AQS-BOM-SC-001)",
     "hood riser carries the N6 vent flush at the envelope top (800 datum = box top)"],
    ["10", "Power-supply cabinet (purchased, envelope and interface)", 1,
     "purchased cabinet (envelope)", mass["power_cabinet"], "buy",
     f"nameplate {KW_NAME:g} kW (AQS-MFG-010 Table 2.1; node stamp); purchased per "
     "plan rule 6; cabinet mass is a table-density placeholder until the maker TDS "
     "quotes (W12)"],
    ["11", "Nozzle set per docs-authority/nozzles/MET_MELT.csv: 6 DN15 stubs and 1 "
            "solids row drawn DN15 bore not calculated", len(schedule), "316L tube",
     mass["nozzles"], "make (AQS-BOM-SC-001)",
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
    [None, "M12 trunnion stud + nut", fasteners.grade_for("CS"), 4,
     "trunnion blocks to the casing plates (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "furnace": {"casing_od_mm": CAS_OD, "wall_mm": CAS_WALL, "hot_face_mm": FACE_T,
                "coil_mm": COIL_T, "z_mm": [CAS_Z0, CAS_Z1], "pos_mm": [CX, CY]},
    "crucible": {"od_mm": CRUC_OD, "wall_mm": CRUC_WALL, "z_mm": [CRUC_Z0, CRUC_Z1],
                 "melt_line_mm": MELT_H},
    "hood_z_mm": [HOOD_Z0, HOOD_Z1],
    "cabinet_mm": [700.0, 180.0, 260.0, 240.0, 620.0],
}
p["design"] = {
    "service": "MET_MELT: cathode sheet and off-spec powder melted to the billet, "
               "mill and atomizer charges (duty sections 1 and 4)",
    "tool_row": "AQS-MFG-010 Table 2.1: coreless induction melt furnace, 10 kg Cu "
                "crucible, nameplate 7.5 kW",
    "material": "graphite/refractory hot face; frame A500 behind a heat shield",
    "ca_mm": CA,
    "material_basis": "duty section 3; CA 0 mm on the frame (dry, non-hydrocarbon "
                      "furnace service, AQS-STD-001)",
    "holdup_basis": "duty section 2: 1 h charge V = 0.0006 m3; crucible melt line "
                    "sized to it (A-VES report, no new rate)",
    "purchased": "crucible (buy consumable) and 7.5 kW power supply (plan rule 6 "
                 "envelope, rating from the AQS-MFG-010 tool row)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; furnace centre x 300 on the plinth, "
             "pour lip toward +Y over the melt-out rows; power cabinet x 700..960; "
             "hood over the furnace z 700..780; hold-down posts at the envelope "
             "corners",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1/N7 pack one row "
                     "on -Y at z 160 from x 200; N2/N3/N4 pour rows on +Y at z 600 "
                     "under the pour lip; drain under the plinth centre at x 300; "
                     "vent on the hood riser at x 300; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
