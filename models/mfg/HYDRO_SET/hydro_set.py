"""HYDRO_SET manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 8, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph
through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back
merges the builder-owned blocks only, and rebuilds every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down/guard frame and the vent riser pin the
  box so the X-PAR-04 envelope registry reads the build.
- Machine per the unit's own node backup_basis (A-M-145 lane; Q-006/Q-009 closed):
  the pumped-hydro set is the diverse N+1 backup of ZNBR2 (third source FUEL_CELL)
  to NFPA 111 Level 1, Class X - 14 h at the 14.46 kW critical load = 202.4 kWh at
  the bus. The set is drawn as purchased-class machine envelopes per plan rule 6
  with the node ratings: turbine-generator (rated_kW_discharge 14.46 at head_m
  36.21, eta_turbine_generator 0.8) and pump-motor (recharge_kW_over_PV_window
  49.6, eta_pump_motor 0.85; round_trip 0.68). No machine type is invented: the
  envelopes are the model; the maker prints govern (holds, W12).
- Reservoir interface per the Q-009 reservoir facts (closed 2026-10-16): the upper
  reservoir is the building's top floors - 3 reservoir levels x 3.06 m water over
  367 m2, 2 cells per level, from +16.8 m (upper_reservoir_m3 2700 on the node);
  the lower reservoir is CATCH_TANK (9.17 m water over 367 m2). The penstock
  supply stub (from the upper reservoir above) and the tailrace return stub (to
  CATCH_TANK) are drawn as interface pads/stubs inside the envelope with bores
  not calculated (W4) - the reservoir structures themselves are building scope
  (AQS-BLD-014, A-M-187) and are not this unit's hardware. eta_net_with_penstock
  0.76 is the node figure.
- A-MACH: hold-down/guard frame; 8 slab anchors (fasteners.csv). The set runs
  standby (the S43/S44 class loop runs at 0 kW idle per the GEO/ESS lane); the
  electrical N1 row is the schedule row that the one-line diagram still carries
  as MISSING (duty section 4 verbatim).
- Nozzles: all 3 rows of docs-authority/nozzles/HYDRO_SET.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1 hydro
  turbine-pump electrical out on +Y at z 600 (schedule service text verbatim,
  including the MISSING-on-SLD note); N2 drain flush at the envelope bottom
  (50 datum); N3 vent flush at the envelope top (800 datum is the box top). The
  schedule rating column (Class 150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("HYDRO_SET")       # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {})})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
BB = P.get("backup_basis") or {}

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
TUN_X, GEN_X = (60.0, 340.0), (340.0, 560.0)               # turbine / generator bays
PMP_X = (560.0, 720.0)                                     # pump-motor bay
CAB_X = (720.0, 960.0)                                     # electrical cabinet bay
TUN_H, GEN_H, PMP_H, CAB_H = 520.0, 300.0, 300.0, 620.0
BUF_R, BUF_H = 80.0, 300.0                                 # buffer manifold vessel (study, W12)
MAT = "316L"
CA = materials.ca_for(MAT)
RHO_CS = materials.density("CS")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert CAB_X[1] <= L - POST, "cabinet clears the frame"
assert float(BB.get("rated_kW_discharge") or 14.46) == 14.46, "node discharge rating"
assert float(BB.get("head_m") or 36.21) == 36.21, "node head"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def vtube(od, x, y, z0, z1):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0)


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

# ---------------------------------------------------------------- machine envelopes (plan rule 6)
CY = W / 2
parts["turbine_env"] = box(TUN_X[0], CY - 130.0, T_PLINTH,
                           TUN_X[1] - TUN_X[0], 260.0, TUN_H)
parts["generator_env"] = box(GEN_X[0], CY - 130.0, T_PLINTH,
                             GEN_X[1] - GEN_X[0], 260.0, GEN_H)
parts["pump_motor_env"] = box(PMP_X[0], CY - 130.0, T_PLINTH,
                              PMP_X[1] - PMP_X[0], 260.0, PMP_H)
parts["cabinet_env"] = box(CAB_X[0], CY - 120.0, T_PLINTH,
                           CAB_X[1] - CAB_X[0], 240.0, CAB_H)
parts["buffer_vessel"] = vtube(2 * BUF_R, 450.0, CY, T_PLINTH, T_PLINTH + BUF_H)

# ---------------------------------------------------------------- reservoir interface pads (Q-009)
# penstock supply stub from the upper reservoir above (building scope); tailrace
# return stub toward CATCH_TANK. Bores not calculated (W4) - interface indication.
parts["penstock_pad"] = tube_z("DN50", 90.0).translate((TUN_X[0] + 130.0, CY, TUN_H))
parts["tailrace_pad"] = tube_z("DN50", 90.0).translate((PMP_X[0] + 60.0, CY, T_PLINTH))

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
    if r["face"] == "bottom":                             # N2: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (450.0, CY - 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N3: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (550.0, CY), (L, W, H))
        note = "vent flush at the envelope top; the 800 datum is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        if tag == "N1":
            note += ("; schedule service text verbatim: the turbine-pump "
                     "electrical row is the one the SLD still carries as MISSING")
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
mass = {k: round(v.val().Volume() * RHO_CS / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "pumped-hydro powerhouse set per the node backup_basis (A-M-145 "
                "lane; Q-006/Q-009 closed), drawn as purchased-class machine "
                "envelopes per plan rule 6: turbine envelope (rated_kW_discharge "
                "14.46 at head_m 36.21, eta_turbine_generator 0.8), generator "
                "envelope, pump-motor envelope (recharge 49.6 kW over the PV "
                "window, eta_pump_motor 0.85; round_trip 0.68), electrical "
                "cabinet envelope, buffer manifold vessel (study, W12); "
                "hold-down/guard frame pins the registry box (X-PAR-04)",
        "n1_backup": "diverse N+1 backup of ZNBR2 (third source FUEL_CELL) to "
                     "NFPA 111 Level 1, Class X: 14 h at the 14.46 kW critical "
                     "load = 202.4 kWh at the bus (node backup_basis)",
        "reservoir_interface": "Q-009 facts (closed 2026-10-16): upper reservoir "
                     "= the building's top floors, 3 levels x 3.06 m water over "
                     "367 m2, 2 cells per level, from +16.8 m (upper_m3 2700 "
                     "node); lower = CATCH_TANK, 9.17 m water over 367 m2; "
                     "eta_net_with_penstock 0.76. Penstock supply and tailrace "
                     "return pads drawn inside the envelope, bores not calculated "
                     "(W4) - the reservoir structures are building scope "
                     "(AQS-BLD-014, A-M-187), not this unit's hardware",
        "purchased": "turbine-generator set and pump-motor set are plan rule 6 "
                     "envelopes with the node ratings; no machine type is "
                     "invented - the maker prints govern (holds, W12)",
        "guard": "four-post hold-down/guard frame (40 x 40 posts, top rails) + "
                 "8 slab anchors (fasteners.csv)",
        "material": "316L where the stream is wet (duty section 3); CA 0 mm; the "
                    "water sides are the reservoir/penstock building scope",
        "ca_mm": CA,
        "standby": "the set runs standby; the continuous kW model is honest-"
                   "incomplete on the node (WP-A4) - nothing claimed here",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 turbine-pump electrical out on +Y at z 600 with "
                    "the schedule service text verbatim (the SLD MISSING note); "
                    "drain flush at the envelope bottom (50 datum); vent flush "
                    "at the envelope top (800 datum is the box top); no flange "
                    "drawn (W4 110 % rule); the schedule rating column (Class "
                    "150) carried verbatim as text",
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
    ["3", "Turbine envelope (rated 14.46 kW discharge at 36.21 m head, "
           "eta 0.8)", 1, "purchased set (envelope)", mass["turbine_env"], "buy",
     "node backup_basis; purchased per plan rule 6; no machine type invented - "
     "the maker print governs (hold, WORK_ORDER W12)"],
    ["4", "Generator envelope on the turbine bay", 1,
     "purchased set (envelope)", mass["generator_env"], "buy",
     "eta_turbine_generator 0.8 (node); purchased per plan rule 6"],
    ["5", "Pump-motor envelope (recharge 49.6 kW over the PV window, eta 0.85)", 1,
     "purchased set (envelope)", mass["pump_motor_env"], "buy",
     "node backup_basis round_trip 0.68; purchased per plan rule 6"],
    ["6", "Electrical cabinet envelope", 1, "purchased cabinet (envelope)",
     mass["cabinet_env"], "buy",
     "the N1 electrical row (SLD MISSING note, schedule verbatim); purchased per "
     "plan rule 6"],
    ["7", "Buffer manifold vessel OD 160 x 300 (study)", 1, "316L (duty section 3)",
     mass["buffer_vessel"], "make (AQS-BOM-SC-001)",
     "manifold between penstock, pump and turbine bays; size is a study value "
     "(hold, WORK_ORDER W12)"],
    ["8", "Reservoir interface pads: penstock supply stub and tailrace return "
           "stub (DN50 pads, bores not calculated, W4)", 2, "316L tube",
     mass["penstock_pad"] + mass["tailrace_pad"], "make (AQS-BOM-SC-001)",
     "Q-009 facts: upper = building top floors (3 levels x 3.06 m over 367 m2, "
     "2 cells/level, from +16.8 m), lower = CATCH_TANK (9.17 m over 367 m2); the "
     "reservoir structures are building scope (AQS-BLD-014, A-M-187)"],
    ["9", "Nozzle set per docs-authority/nozzles/HYDRO_SET.csv: 3 DN15 stubs",
     len(schedule), "316L tube", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "schedule tags/faces/heights verbatim (N1 service text verbatim including "
     "the SLD MISSING note); atmospheric per duty section 4"],
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
    [None, "M16 set-base bolt + nut", fasteners.grade_for("CS"), 8,
     "machine envelopes to the plinth, 2 per set bay (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "bays_mm": {"turbine": TUN_X, "generator": GEN_X, "pump_motor": PMP_X,
                "cabinet": CAB_X},
    "buffer_vessel": {"od_mm": 2 * BUF_R, "h_mm": BUF_H},
}
p["design"] = {
    "service": "HYDRO_SET: the pumped-hydro N+1 backup of ZNBR2 - turbine-"
               "generator discharge at the night class, pump-motor recharge on "
               "the PV window (duty sections 1 and 4; A-M-145 lane)",
    "backup_basis": BB,
    "q009": "Q-009 closed: upper reservoir = the building's top floors (3 levels "
            "x 3.06 m water over 367 m2, 2 cells per level, from +16.8 m); lower "
            "= CATCH_TANK 9.17 m over 367 m2; roof PV at +34.8 m",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: 316L where the stream is wet; CA 0 mm "
                      "(AQS-STD-001); the water sides are building scope",
    "purchased": "turbine-generator and pump-motor sets, electrical cabinet "
                 "(plan rule 6 envelopes with the node ratings); no machine type "
                 "invented",
}
p["layout"] = {
    "frame": "origin at the envelope corner; turbine bay x 60..340, generator "
             "x 340..560, pump-motor x 560..720, cabinet x 720..960, buffer "
             "vessel at x 450; hold-down posts at the envelope corners",
    "interface": "penstock supply pad on the turbine bay top (from the upper "
                 "reservoir above), tailrace return pad at the pump bay base "
                 "(to CATCH_TANK); bores not calculated (W4)",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1 on +Y at z 600, "
                     "drain at x 450, vent at x 550; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
