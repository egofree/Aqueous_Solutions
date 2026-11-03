"""GLASS_DIGEST manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid. This is the M2 close-out of the Oct-31-era `reactors.py` study build:
the vessel construction (DN400 CPVC shell, bolted lid, agitator, Q3 coil, 4 legs)
is the issued AQS-DUTY-062 / X-MFG-31 design carried through the current shared
lib, the 12-row issued nozzle schedule replaces the 5-row study layout, and the
section 5 artifacts (check record, make-or-buy BOM, W1-W12 work order, drawing
set, duty section 7 pointer) are completed per the HX8 close pattern.

Placement frame: x along 700 mm, y along 700 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 700 x 700 x 900 mm, node size_mm (set by flow_graph/param/reactor_design.py,
  X-MFG-31). The build stays inside it exactly.
- Vessel per the node design block: OD 400 (D_mm), wall 4.0 (wall_mm), shell H 400
  (H_mm), CPVC to 93 C (design.material; DVS 2205 allowable 3.0 MPa at 85 C; duty
  section 3 names 316L - the design row is the X-MFG-31 construction and the wetted
  polymer follows AQS-STD-002 M2; the conflict is carried as a hold, W12, nothing
  resized). PVDF impeller and shaft sleeve per design.material.
- Agitator per the node design block: 4-blade 45 deg PBT D133 (D_imp_mm) at 358 rpm
  (rpm), 0.09 kW motor (motor_kW) - the motor is a purchased envelope (plan rule 6).
- Heat per the node design block: Q3 coil (design.heat "Q3 coil HX-6", graph
  HL-Q3-A/B-HX6) - a PVDF DN15 helical coil, 3 turns, R 155 (inside the ID 392 shell).
- Legs: 4 CPVC 40 x 40 legs, 150 mm (layout choice carried from the issued
  construction; the node names no support - hold, W12).
- Nozzles: all 12 rows of docs-authority/nozzles/GLASS_DIGEST.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube connections from the shell to
  the envelope faces (duty section 4: atmospheric tube or hose; the connecting line
  makes the joint at the face). Schedule datums are the house placeholders (inlet
  160, outlet 600) and predate the leg-mounted vessel: they draw clamped into the
  shell span [175, 525] (the HDR_CO2 clamp idiom; holds, W12). The vent riser
  stands on the lid and flushes at the envelope top (the 800 datum is the schedule
  placeholder); the drain passes to the envelope bottom (50 datum). The N11 solids
  row (glass/ceramic goods) is a non-piped transfer drawn DN15, bore not calculated
  (plan W4). The schedule rating column (Class 150) is carried verbatim as text;
  no flange is drawn because no process pressure is stated (plan W4 110 % rule).
- A-VES: the shell volume from the model is reported against the node V_L 49.9724 L
  (design V_work_L 37.4793, tau 22.5014 h); no new residence time is derived.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 700 x 700 x 900
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}

D_OD, T_WALL, H_SHELL = float(DS.get("D_mm", 400)), float(DS.get("wall_mm", 4.0)), float(DS.get("H_mm", 400))
R_ID = D_OD / 2 - T_WALL                                   # 196
Z_LEG = 150.0                                              # leg height, layout choice (W12)
Z_SH0, Z_SH1 = Z_LEG, Z_LEG + H_SHELL                      # shell 150..550
T_LID = 16.0                                               # lid flange ring 550..566
OD_LID = D_OD + 60.0
AG = DS.get("agitator") or {}
D_IMP = float(AG.get("D_imp_mm", 133))
V_L_NODE = float(DS.get("V_L_L", DS.get("V_L", 49.9724)))
COIL_R, COIL_TURNS, COIL_PITCH = 155.0, 3, 33.0
COIL_TUBE_OD = dn.pipe_od("DN15")
CX, CY = L / 2, W / 2
MAT_SHELL = "CPVC"                                         # design.material (X-MFG-31); hold, W12
MAT_IMP = "PVDF"
CA = materials.ca_for(MAT_SHELL)                           # 0.0, AQS-STD-001 polymer rule
RHO = {"CPVC": materials.density("CPVC"), "PVDF": materials.density("PVDF"),
       "CS": materials.density("CS")}

assert L == 700.0 and W == 700.0 and H == 900.0, "GLASS_DIGEST node envelope changed"
assert D_OD == 400.0 and T_WALL == 4.0 and H_SHELL == 400.0, "GLASS_DIGEST node design changed"
assert Z_SH1 + T_LID + 130.0 < H, "agitator + riser must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- hold-down frame (pins the envelope)
post = 40.0
frame = None
for (fx, fy) in ((0.0, 0.0), (L - post, 0.0), (0.0, W - post), (L - post, W - post)):
    b = box(fx, fy, 0.0, post, post, H - post)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, post), (0.0, W - post, L, post),
                         (0.0, 0.0, post, W), (L - post, 0.0, post, W)):
    b = box(rx, ry, H - post, dx, dy, post)
    frame = frame.union(b)
parts["frame"] = frame

# ---------------------------------------------------------------- legs
leg = None
for (lx, ly) in ((CX - 140.0, CY - 140.0), (CX + 100.0, CY - 140.0),
                 (CX - 140.0, CY + 100.0), (CX + 100.0, CY + 100.0)):
    b = box(lx, ly, 0, 40.0, 40.0, Z_LEG)
    leg = b if leg is None else leg.union(b)
parts["legs"] = leg

# ---------------------------------------------------------------- shell + lid (CPVC, X-MFG-31)
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D_OD / 2)
         .circle(R_ID).extrude(H_SHELL))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D_OD / 2)
                    .extrude(T_WALL))                      # base head
parts["shell"] = shell
lid = (cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(OD_LID / 2)
       .circle(D_OD / 2 - T_WALL).extrude(T_LID))
lid = lid.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D_OD / 2)
                .circle(D_OD / 2 - T_WALL).extrude(6.0))   # lid disc
parts["lid"] = lid

# ---------------------------------------------------------------- agitator (node design block)
shaft_d = 24.0
shaft = cq.Workplane("XY", origin=(CX, CY, Z_SH1 + T_LID)).circle(shaft_d / 2).extrude(120.0)
shaft = shaft.union(cq.Workplane("XY", origin=(CX, CY, 300.0)).circle(shaft_d / 2)
                    .extrude(Z_SH1 - 300.0))
blade = (cq.Workplane("XY", origin=(CX, CY, 300.0 - 12.5))
         .rect(D_IMP, 25.0).extrude(25.0))                 # PBT blade stock
parts["agitator"] = shaft.union(blade)
parts["motor"] = (cq.Workplane("XY", origin=(CX - 45.0, CY - 45.0, Z_SH1 + T_LID + 120.0))
                  .circle(45.0).extrude(10.0)
                  .union(cq.Workplane("XY", origin=(CX - 35.0, CY - 35.0,
                                                    Z_SH1 + T_LID + 130.0))
                         .rect(70.0, 70.0).extrude(60.0)))  # purchased 0.09 kW gearmotor envelope

# ---------------------------------------------------------------- Q3 coil (node design.heat)
coil = None
for i in range(COIL_TURNS):                                # 3 stacked tube rings, pitch 33
    zc = Z_SH0 + 60.0 + i * COIL_PITCH
    path = cq.Workplane("XY", origin=(CX, CY, zc)).circle(COIL_R)
    ring = (cq.Workplane("XZ", origin=(CX + COIL_R, CY, zc))
            .circle(COIL_TUBE_OD / 2).sweep(path))
    coil = ring if coil is None else coil.union(ring)
parts["coil"] = coil

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
LO, HI = Z_SH0 + 25.0, Z_SH1 - 25.0                        # clamp band into the shell span


def z_for(row):
    h = float(row["height_mm"])
    z = min(max(h, LO), HI)
    note = None
    if h < LO:
        note = (f"schedule datum {h:g} mm clamped up to {round(z, 1)} mm: the datum "
                "predate the leg-mounted vessel (placeholder elevation; hold, WORK_ORDER W12)")
    elif h > HI:
        note = (f"schedule datum {h:g} mm clamped down to {round(z, 1)} mm into the "
                "shell span (placeholder elevation; hold, WORK_ORDER W12)")
    return round(z, 1), note


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
    span = sum(od_of(r) + 12.0 for r in rows) - 12.0
    assert span <= L - 120.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 12.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    dnl_draw = dnl if dnl.startswith("DN") else "DN15"
    note = "atmospheric open-bore tube connection, shell to the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N9: drain to the envelope bottom
        s = tube_z("DN15", 60.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 40.0, CY), (L, W, H))
        note = "drain boss, flush at the envelope bottom; 50 datum is the placeholder"
    elif r["face"] == "top":                              # N10: vent riser on the lid
        riser_h = H - (Z_SH1 + T_LID)
        s = tube_z("DN15", riser_h)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 70.0, CY - 60.0), (L, W, H))
        note = ("vent riser stands on the lid and flushes at the envelope top; the "
                "800 datum is the schedule placeholder")
    else:
        z_d, clamp = z_for(r)
        stub_len = (150.0 if face == "-Y" else 155.0) + STUB_PIERCE
        s = tube_z(dnl_draw, stub_len)
        s = nozzles.place_on_face(s, face, z_d, (layout_x[tag], CY), (L, W, H))
        note = (note + ("; " + clamp if clamp else ""))
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": z_d if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
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
mass = {k: round(v.val().Volume() * ((RHO["PVDF"] if k in ("coil",) else
                                      RHO["CS"] if k in ("motor", "frame") else
                                      RHO["CPVC"])) / 1e9, 2)
        for k, v in parts.items()}
v_shell_l = math.pi / 4 * (2 * R_ID) ** 2 * H_SHELL / 1e6
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "vessel": {
        "type": "CPVC stirred digestor per the X-MFG-31 node design: OD 400 shell, "
                "wall 4.0, H 400, bolted lid flange, 4 legs, top-entry PBT agitator "
                "(D133, 358 rpm, 0.09 kW purchased gearmotor envelope), Q3 PVDF "
                "DN15 helical coil (3 turns, R 155)",
        "od_mm": D_OD, "wall_mm": T_WALL, "shell_h_mm": H_SHELL,
        "material": "CPVC shell and lid (design.material; duty section 3 names 316L "
                    "- conflict carried as a hold, WORK_ORDER W12); PVDF impeller "
                    "and shaft sleeve; motor envelope carbon-steel frame",
        "v_shell_model_l": round(v_shell_l, 2),
        "v_L_node_l": V_L_NODE,
        "v_note": f"model shell volume {v_shell_l:.1f} L against the node design "
                  f"V_L {V_L_NODE:.4f} L (V_work {DS.get('V_work_L', 37.4793):.4f} L, "
                  "tau 22.5014 h at 85 C); reported, no new residence time derived "
                  "(A-VES)",
        "leg_mm": Z_LEG, "leg_basis": "layout choice carried from the issued "
        "construction; the node names no support (hold, WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections from the shell to the "
                    "envelope faces (duty section 4: atmospheric tube or hose); the "
                    "12-row issued schedule replaces the 5-row study layout of the "
                    "Oct-31-era build; placeholder datums clamped into the shell "
                    "span [175, 525] (holds); vent riser flush at the envelope top, "
                    "drain flush at the bottom; the N11 solids row drawn DN15, bore "
                    "not calculated (plan W4); the schedule rating column (Class "
                    "150) carried verbatim as text, no flange drawn (no process "
                    "pressure stated)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {D_OD:g} x wall {T_WALL:g} x H {H_SHELL:g} with base head, on "
          f"4 CPVC legs 40 x 40 x {Z_LEG:g}", 1, "CPVC sheet (duty section 3 conflict "
     "carried; design.material X-MFG-31)", mass["shell"] + mass["legs"], "make",
     "node design D/H/wall (AQS-DUTY-062/X-MFG-31); CA 0 mm (AQS-STD-001 polymer "
     "rule); duty section 3 names 316L - hold, WORK_ORDER W12"],
    ["1b", f"Four-post hold-down frame pinning the {L:g} x {W:g} x {H:g} envelope "
          f"(40 x 40 posts, top rails), around the vessel", 1,
     "carbon steel (ASTM A500)", mass["frame"], "make",
     "HX8 hold-down idiom: the frame pins the registry box so the build fills the "
     "node envelope (X-PAR-04); AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Bolted lid: flange ring OD {OD_LID:g} x {T_LID:g} with lid disc, "
          "12-bolt circle", 1, "CPVC sheet", mass["lid"], "make",
     "issued construction (reactors.py Oct-31 build carried through the lib); bolt "
     "circle in fasteners.csv"],
    ["3", f"Agitator: shaft D24 with 4-blade 45 deg PBT D{D_IMP:g} (PVDF), at 358 "
          "rpm", 1, "PVDF (design.material)", mass["agitator"], "make",
     "node design agitator block (D_imp, rpm, shaft_W); impeller and shaft sleeve "
     "PVDF per design.material"],
    ["4", "Gearmotor for the agitator, 0.09 kW, with mounting ring", 1,
     "purchased unit (carbon-steel frame envelope)", mass["motor"], "buy",
     "node design motor_kW 0.09 - purchased envelope per plan rule 6; rating from "
     "the node"],
    ["5", f"Q3 coil: PVDF DN15 helical coil, {COIL_TURNS:g} turns R {COIL_R:g}, "
          "per design.heat (graph HL-Q3-A/B-HX6)", 1, "PVDF", mass["coil"], "make",
     "node design.heat 'Q3 coil HX-6'; the schedule N1/N2 service text says jacket - "
     "carried verbatim, the coil is the issued construction (hold, WORK_ORDER W12)"],
    ["6", "Nozzle set per docs-authority/nozzles/GLASS_DIGEST.csv: 12 open-bore tube "
          "connections shell-to-face (vent riser on the lid, drain boss at the "
          "bottom, N11 solids row drawn DN15 bore not calculated)", len(schedule),
     "CPVC", mass["nozzles"], "make",
     "12-row issued schedule verbatim; placeholder datums clamped into the shell "
     "span (holds); atmospheric tube per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 x 40 lid bolt with nut and washers", fasteners.grade_for("CPVC"), 12,
     "lid flange at 100 mm pitch (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 4,
     "leg feet to slab (count from the model)",
     "8.8 on carbon steel; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "vessel": {"od_mm": D_OD, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_SH1],
               "axis_mm": [CX, CY]},
    "legs_mm": Z_LEG,
}
p["design"] = dict(p.get("design") or {})
p["design"].update({
    "service": "GLASS_DIGEST: NaOH digest of burned cullet at 85 C (design T_C); "
               "silicate liquor to leach, stock to the shop, at atmospheric (duty "
               "sections 2, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "node design wall_mm (X-MFG-31)",
    "ca_mm": CA,
    "v_shell_model_l": round(v_shell_l, 2), "v_L_node_l": V_L_NODE,
    "agitator": {"D_imp_mm": D_IMP, "rpm": AG.get("rpm", 358),
                 "motor_kW": AG.get("motor_kW", 0.09), "motor": "purchased envelope"},
    "coil": {"tube": "PVDF DN15", "turns": COIL_TURNS, "radius_mm": COIL_R,
             "basis": "node design.heat 'Q3 coil HX-6' (graph HL-Q3-A/B-HX6)"},
})
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at x 350, y 350; legs 150; "
             "shell z 150..550; lid 550..566; agitator to 696; vent riser to 900; "
             "four-post hold-down frame (40 x 40 posts + top rails) pins the "
             "envelope so the build fills the registry box (X-PAR-04)",
    "supports": "4 CPVC legs + four-post hold-down frame + 4 slab anchors (layout "
                "choice, hold W12)",
    "nozzle_spread": "the schedule gives face and height only; side ports pack in "
                     "one row per face/height group, 12 mm clear at the bore, drawn "
                     "as open-bore stubs from the shell to the envelope face; "
                     "placeholder datums clamped into [175, 525]; vent riser at "
                     "x 420, y 290; drain at x 390; per-tag positions in "
                     "check.nozzles_drawn",
    "close_out": "M2 close-out of the Oct-31-era reactors.py study build per the "
                 "HX8 close pattern: 12-row issued schedule, lib builders, section "
                 "5 artifacts completed; nothing resized",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"v_shell_model_l": round(v_shell_l, 2)}))
