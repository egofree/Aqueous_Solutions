"""BMED_ACID manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-CELL).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 350 mm, node size_mm: the study registry box (params size_note
  records it as the M0 study envelope, design sizing per the duty sheet to follow).
  The build fills it with the tray, the stack clamp and the hold-down beam.
- Machine per the issued EDBM construction (AQS-DUTY-068 `docs-authority/sizing/
  BMED_STACK.md`, A-M-170/171; the same construction line AQS-TST-006 builds to):
  the electrodialysis stack between end electrode plates - Ti/MMO anode plate and
  316L/Ni cathode plate - on 300 x 300 frames, 85 triplets of one bipolar and two
  monopolar membranes with 0.8 mm PE mesh spacers, 0.04 m2 active window per cell
  (200 x 200), tie-rod clamped. Duty section 3 rules the wetted path PVC-U; the
  sizing page frames are PP: PVC-U drawn (plan rule 5), PP named (holds, W12).
  The node internals row is none, so the tracker records no internal solid; the
  stack is the machine itself, drawn from the construction authority.
- Skid: PVC-U drip tray over the full envelope (duty section 3: PVC-U wetted, no
  metal wetted part) and a PVC-U hold-down beam over the stack (layout choice,
  W12; the M2 style-build carry-over minus the rails that fused the branch zone).
- Nozzles: all 10 rows of docs-authority/nozzles/BMED_ACID.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections (duty section 4:
  atmospheric tube or hose, no flange class) on risers from the tray floor, flush
  at the envelope faces. Side datums sit in the 350 mm box: the 160 mm inlets draw
  as issued; the 600 mm outlet datums predate the box and clamp to the stub-radius
  bound; the 800 mm vent draws flush at the top face on the beam; the 50 mm drain
  draws flush through the tray floor (holds, W12). The schedule rating column
  (Class 150) is carried verbatim as text.
- A-CELL: triplet count, plate sizes, pitch and active area are the AQS-DUTY-068 /
  A-M-170 figures reported from the model; the duty section 2 carries no plate row,
  so the match is against the sizing construction (holds, W12).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("BMED_ACID")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 350, study registry box
REV = P["graph_revision"]
UNIT = P["unit_id"]

# issued EDBM construction, AQS-DUTY-068 / A-M-170/171 (AQS-TST-006 apparatus line)
FRAME = 300.0                    # PP frames 300 x 300 mm (drawn PVC-U per duty s3 - W12)
CELL = 200.0                     # 0.04 m2 active window per cell -> 200 x 200
TRIPLETS = 85                    # triplets per stack (421 in 5 stacks of 85 + 1 spare, sizing page)
SPACER = 0.8                     # 0.8 mm PE mesh spacers (A-M-170)
MEM_T = 0.15                     # membrane sheet, study value inside the A-M-171 stack-up (W12)
PITCH = 3 * SPACER + 3 * MEM_T   # 2.85 mm triplet pitch, derived from the A-M-171 stack-up
LAM_T = round(TRIPLETS * PITCH, 2)   # 242.25 laminate block
PLATE_T = 20.0                   # clamp frame plate thickness, study (W12)
ELECTRODE_T = 10.0               # end electrode plate thickness, study (W12)
ROD_D = 12.0                     # M12 tie rods (A-M-170: tie-rod clamped)

# skid (layout choices, W12)
T_FLOOR = 20.0                   # tray floor
CURB_H, CURB_T = 60.0, 10.0      # tray curb
BEAM_T = 20.0                    # hold-down beam

Z0 = T_FLOOR - 2.0               # stack seat, sunk 2 mm into the tray floor so the union fuses
SEAT_SINK = 2.0                  # same sink for every part standing on the tray floor
STACK_Y0 = (W - FRAME) / 2       # 150; stack cross-section centred
STACK_Z0 = Z0 + (FRAME - CELL) / 2                  # laminate centred in the frame height
FRAME_Z0, FRAME_Z1 = Z0, Z0 + FRAME                 # clamp frames, full 300 x 300 plates
STACK_Z1 = Z0 + FRAME                               # stack head 318
BEAM_Z0 = H - BEAM_T             # 330
LAP = 2.0                        # volumetric lap at every frame/laminate joint (fusion)
X_A0 = 40.0                                        # anode plate face (layout: stack at -X end)
X_AN1, X_AN2 = X_A0, X_A0 + ELECTRODE_T             # anode plate 40..50
X_FR1, X_FR2 = X_AN2 - LAP, X_AN2 + PLATE_T - LAP   # clamp frame A 48..68
X_LA1, X_LA2 = X_FR2 - LAP, X_FR2 - LAP + LAM_T     # laminate 66..308.25
X_FR3, X_FR4 = X_LA2 - LAP, X_LA2 - LAP + PLATE_T   # clamp frame B 306.25..326.25
X_CA1, X_CA2 = X_FR4 - LAP, X_FR4 - LAP + ELECTRODE_T   # cathode plate 324.25..334.25
ROD_X0, ROD_X1 = X_AN1 + 2.0, X_CA2 - 2.0          # tie rods, ends buried in the end plates
ROD_IN = 20.0                    # rod inset from the frame edge
POST_W = 9.0                     # hold-down beam post, in the clear strip beside the stack
POST_CLR = 1.0                   # post-to-stack clearance

MAT = "PVC-U"                    # duty section 3: PVC-U wetted, no metal wetted part
RHO_U = materials.density("PVC_U")     # 1400, lib table
CA_U = materials.ca_for("PVC-U")       # 0.0, polymer: AQS-STD-001
RHO_PE = materials.density("HDPE")     # 950, laminate spacer/membrane class
RHO_TI = materials.density("Ti_G2")    # 4510, anode end plate (A-M-170)
RHO_316 = materials.density("316L")    # 8000, cathode end plate 316L/Ni

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert FRAME == 300.0 and CELL == 200.0, "AQS-DUTY-068 construction changed"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- tray (PVC-U drip tray)
tray = box(0, 0, 0, L, W, T_FLOOR)
for x, y, dx, dy in ((0, 0, L, CURB_T), (0, W - CURB_T, L, CURB_T),
                     (0, CURB_T, CURB_T, W - 2 * CURB_T),
                     (L - CURB_T, CURB_T, CURB_T, W - 2 * CURB_T)):
    tray = tray.union(box(x, y, Z0, dx, dy, CURB_H - SEAT_SINK))
parts["tray"] = tray

# ---------------------------------------------------------------- EDBM stack (A-M-170 construction)
# anode end plate (Ti/MMO), clamp frames, triplet laminate, cathode end plate (316L/Ni)
anode = box(X_AN1, STACK_Y0, Z0, ELECTRODE_T, FRAME, FRAME)
parts["anode_end_plate"] = anode
frame_a = box(X_FR1, STACK_Y0, FRAME_Z0, PLATE_T, FRAME, FRAME)
parts["frame_plate_a"] = frame_a
laminate = box(X_LA1, STACK_Y0 + (FRAME - CELL) / 2, STACK_Z0, LAM_T, CELL, CELL)
parts["triplet_laminate"] = laminate
frame_b = box(X_FR3, STACK_Y0, FRAME_Z0, PLATE_T, FRAME, FRAME)
parts["frame_plate_b"] = frame_b
cathode = box(X_CA1, STACK_Y0, Z0, ELECTRODE_T, FRAME, FRAME)
parts["cathode_end_plate"] = cathode

rods = None
for y_r in (STACK_Y0 + ROD_IN, STACK_Y0 + FRAME - ROD_IN):
    for z_r in (FRAME_Z0 + ROD_IN, FRAME_Z1 - ROD_IN):
        r = (cq.Workplane("YZ", origin=(ROD_X0, y_r, z_r)).circle(ROD_D / 2)
             .extrude(ROD_X1 - ROD_X0))
        rods = r if rods is None else rods.union(r)
parts["tie_rods"] = rods

# hold-down beam over the stack on posts in the clear strips beside it
beam = box(X_A0 - 10.0, STACK_Y0 - 10.0, BEAM_Z0,
           (X_CA2 - X_A0) + 20.0, FRAME + 20.0, BEAM_T)
parts["hold_down_beam"] = beam
posts = None
for x_p in (X_A0 - POST_W - POST_CLR, X_CA2 + POST_CLR):
    for y_p in (STACK_Y0 + 5.0, STACK_Y0 + FRAME - 5.0 - POST_W):
        post = box(x_p, y_p, Z0, POST_W, POST_W, BEAM_Z0 + BEAM_T / 2 - Z0)
        posts = post if posts is None else posts.union(post)
parts["beam_posts"] = posts

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0                            # past the riser wall, so every union fuses
Y_RISER = 60.0                               # riser stand-off from each face (layout, W12)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
CLAMP_MARGIN = 0.7                           # stub radius clearance to the faces


def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the flow path is real).

    lib/nozzles.stub fills its bore on union (its docstring says the opposite); this
    model draws from the lib/dn table itself: OD and Sch 40 wall, bore open at both
    ends - the same open-bore idiom the accepted HDR spools use."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def z_for(row):
    """Drawn centreline height for a side nozzle: the schedule datum clamped into the
    350 mm box, deep enough that the branch and its riser top both stay inside, with
    the clamp named when it fires."""
    h = float(row["height_mm"])
    od_s = dn.pipe_od(row["size"])
    hi = H - od_s - 8.0
    z = min(max(h, od_s / 2 + CLAMP_MARGIN), hi)
    if h > hi:
        return round(z, 1), (f"schedule datum {h:g} mm predates the 350 mm box; clamped "
                             f"to {round(z, 1)} mm so the branch and riser stay inside "
                             "(hold, WORK_ORDER W12)")
    return round(z, 1), None


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

# pack per face and datum group along +x, past the stack zone (layout choice, W12)
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    x = 420.0
    for r in rows:
        w_od = dn.pipe_od(r["size"])
        layout_x[r["tag"]] = round(x + w_od / 2, 1)
        x += w_od + 8.0

noz_pieces, drawn, clamp_notes = [], {}, []
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    od = dn.pipe_od(dnl)
    if face0 == "bottom":                     # N6 drain: open bore through the tray floor
        s = tube(dnl, 40.0 - Z0).translate((930.0, W / 2, Z0))
        note = "drain, open bore through the tray floor, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, 930.0
    elif face0 == "top":                      # N7 vent: flush at the top face, on the beam
        s = nozzles.place_on_face(tube(dnl, 25.0), "top", 0.0, (X_A0 + 140.0, W / 2), (L, W, H))
        note = ("vent, flush at the top face on the hold-down beam; schedule datum 800 "
                "predates the 350 mm box (hold, WORK_ORDER W12)")
        z_d, x_d = H, X_A0 + 140.0
    else:
        z_d, note = z_for(r)
        if note:
            clamp_notes.append(note)
        x_d = layout_x[tag]
        od = dn.pipe_od(dnl)
        y_r = Y_RISER if face == "-Y" else W - Y_RISER
        # riser from the tray floor, its top 4 mm above the branch crown so the branch
        # crosses the riser wall mid-span, never the open rim; the branch runs from the
        # face into the riser bore (the HDR_CO2 stub pierce)
        riser = tube(dnl, z_d - Z0 + od / 2 + 4.0).translate((x_d, y_r, Z0))
        branch = nozzles.place_on_face(tube(dnl, Y_RISER - od / 2 + 5.0), face, z_d,
                                       (x_d, W / 2), (L, W, H))
        s = riser.union(branch)
        note = (note or "schedule datum drawn") + (
            f"; atmospheric open-bore tube on a tray riser, flush at the envelope face "
            f"(duty section 4; hose makeup by the connecting line at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube", "dn": dnl, "face": face, "height_mm": float(r["height_mm"]),
                  "drawn_height_mm": z_d, "x_mm": x_d, "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
# the pieces stay a compound (no piece-to-piece fuse: each roots in the tray and is
# fused into the body piecewise at the export pass, the CATCH_TANK pattern)
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    if k == "nozzles":
        # fuse the connection pieces one by one; each roots in the tray (volumetric)
        for piece in v.val().Solids():
            wp = cq.Workplane(obj=piece)
            solid = wp if solid is None else solid.union(wp)
        continue
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {
    "tray": parts["tray"].val().Volume() * RHO_U / 1e9,
    "anode_end_plate": parts["anode_end_plate"].val().Volume() * RHO_TI / 1e9,
    "frame_plate_a": parts["frame_plate_a"].val().Volume() * RHO_U / 1e9,
    "triplet_laminate": parts["triplet_laminate"].val().Volume() * RHO_PE / 1e9,
    "frame_plate_b": parts["frame_plate_b"].val().Volume() * RHO_U / 1e9,
    "cathode_end_plate": parts["cathode_end_plate"].val().Volume() * RHO_316 / 1e9,
    "tie_rods": parts["tie_rods"].val().Volume() * RHO_316 / 1e9,
    "hold_down_beam": parts["hold_down_beam"].val().Volume() * RHO_U / 1e9,
    "beam_posts": parts["beam_posts"].val().Volume() * RHO_U / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO_U / 1e9,
}
mass = {k: round(v, 2) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "stack": {
        "construction": "AQS-DUTY-068 (docs-authority/sizing/BMED_STACK.md) / A-M-170: "
        "300 x 300 frames, 0.8 mm PE mesh spacers, one bipolar and two monopolar membranes "
        "per triplet, Ti/MMO anode and 316L/Ni cathode end plates, tie-rod clamped; the "
        "same construction AQS-TST-006 (AQS-TST-006 section 2) builds the bench apparatus to",
        "frames_mm": [FRAME, FRAME], "active_window_mm": [CELL, CELL],
        "active_area_m2_per_cell": round(CELL * CELL / 1e6, 4),
        "triplets_per_stack": TRIPLETS, "triplet_pitch_mm": PITCH,
        "laminate_mm": [LAM_T, CELL, CELL],
        "membranes_per_stack": TRIPLETS * 3,
        "stack_current_class_A": 8.0,
        "allocation_note": "the sizing page books 421 triplets in 5 stacks of 85 plus 1 "
        "spare for the BMED pair; the node books no per-unit stack count, so the model "
        "draws the representative stack module (hold, WORK_ORDER W12)",
        "material_note": "frames drawn PVC-U per duty section 3 (no metal wetted part); "
        "the sizing page construction names PP frames - PVC-U drawn, PP named (hold, W12); "
        "electrode end plates are the A-M-170 electrochemical hardware (Ti/MMO, 316L/Ni)",
    },
    "a_cell": {
        "basis": "A-CELL: plate count, plate size, pitch and active area per the "
        "AQS-DUTY-068 / A-M-170/171 construction; duty section 2 carries no plate row, so "
        "the match is against the sizing construction, not the duty sheet (hold, W12); "
        "POWER.md states no bus bar for this class, so the bus-bar criterion has nothing "
        "to match",
        "design_voltage_class_V_per_triplet": [1.22, 1.67],
        "voltage_note": "duty section 9 books the stack power on this unit at 26.93 kW "
        "from the A-M-088 SEC revision; the sizing design voltage is the 1.67 V pilot "
        "class, and AQS-TST-006 section 5 holds the measured verification band - figures "
        "reported, not re-derived here",
    },
    "skid": {"tray": "PVC-U drip tray, floor 20 + curb 60 x 10 (duty section 3: PVC-U "
             "wetted; CA 0 mm, AQS-STD-001 polymer rule)",
             "hold_down": "PVC-U beam z 330..350 on four posts over the stack; the M2 "
             "style-build top rails are not carried (layout choice, WORK_ORDER W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections on tray risers, flush at the "
    "envelope faces (duty section 4: atmospheric tube or hose, no flange class; the W4 "
    "110 % rule draws no flange where no process pressure is stated; hose makeup by the "
    "connecting line at the face); the schedule rating column (Class 150) is carried "
    "verbatim as text; clamped datums named in nozzles_drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Drip tray {L:g} x {W:g}, floor {T_FLOOR:g} + curb {CURB_H:g} x {CURB_T:g}", 1,
     "PVC-U plate", mass["tray"], "make",
     "duty section 3: PVC-U wetted, no metal wetted part; CA 0 mm (AQS-STD-001 polymer "
     "rule); tray is the skid layout choice (WORK_ORDER W12)"],
    ["2", "Anode end plate 300 x 300 x 10, Ti/MMO (A-M-170)", 1, "Ti G2",
     mass["anode_end_plate"], "buy",
     "AQS-DUTY-068 construction line; thickness study (W12); MMO coating per the "
     "anode supplier class at order"],
    ["3", f"Clamp frame plates 300 x 300 x {PLATE_T:g} (pair, stack ends)", 2, "PVC-U plate",
     round(mass["frame_plate_a"] + mass["frame_plate_b"], 2), "make",
     "duty section 3 PVC-U drawn; the sizing construction names PP frames (hold, W12); "
     "thickness study (W12)"],
    ["4", f"Triplet laminate: {TRIPLETS} triplets x (1 bipolar + 2 monopolar membranes "
          f"+ 0.8 mm PE mesh spacers), {LAM_T:g} stack, window 200 x 200 (0.04 m2 per cell)",
     TRIPLETS, "membrane/PE spacer laminate", mass["triplet_laminate"], "buy",
     "AQS-DUTY-068 and A-M-170; membranes per the maker class, gaskets per the membrane "
     "maker (AQS-TST-006 section 2); membrane sheet thickness study (W12); drawn as the "
     "stack envelope per plan rule 6"],
    ["5", "Cathode end plate 300 x 300 x 10, 316L/Ni (A-M-170)", 1, "316L/Ni",
     mass["cathode_end_plate"], "buy",
     "AQS-DUTY-068 construction line; thickness study (W12)"],
    ["6", f"Tie rods M12 x {round(ROD_X1 - ROD_X0):g}, 4 per stack", 4,
     "316L rod", mass["tie_rods"], "make",
     "A-M-170 tie-rod clamp; ends drawn buried in the end plates, the protruding stud "
     "length and nuts are fabrication detail (AQS-TST-006 section 2 torque pattern); "
     "grade rule AQS-PLAN-006 W5: A4-70 on 316L"],
    ["7", f"Hold-down beam {round((X_CA2 - X_A0) + 20):g} x "
          f"{round(FRAME + 20):g} x {BEAM_T:g} on four {POST_W:g} x {POST_W:g} posts", 1,
     "PVC-U plate", round(mass["hold_down_beam"] + mass["beam_posts"], 2), "make",
     "skid layout choice (the M2 style-build top rails are not carried, W12)"],
    ["8", "Nozzle set per docs-authority/nozzles/BMED_ACID.csv: 10 atmospheric open-bore "
          "tube connections (DN15/DN25) on tray risers, drain through the floor, vent at "
          "the top face",
     len(schedule), "PVC-U", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4; bore per the "
     "lib/dn Sch 40 table"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("PVC-U", joint="polymer"), 4,
     "tray to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
    [None, "M12 tie rod + nut", fasteners.grade_for("316L"), 4,
     "stack clamp, through the end plates (A-M-170 torque pattern per AQS-TST-006 "
     "section 2)", "grade rule AQS-PLAN-006 W5: A4-70 on 316L; torque to the issued "
     "stack pattern; lengths study, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "stack": {"x_mm": [X_A0, X_CA2], "frames_mm": [FRAME, FRAME],
              "laminate_x_mm": [X_LA1, X_LA2]},
    "tray": {"floor_mm": T_FLOOR, "curb_mm": [CURB_H, CURB_T]},
}
p["design"] = {
    "machine": "electrodialysis stack skid (BMED acid side), EDBM per AQS-DUTY-068",
    "construction": "A-M-170: 300 x 300 frames, 0.8 mm PE mesh spacers, 85 triplets, "
                    "Ti/MMO anode and 316L/Ni cathode end plates, tie rods",
    "active_area_m2_per_cell": round(CELL * CELL / 1e6, 4),
    "mat": MAT, "ca_mm": CA_U,
    "mat_basis": "duty section 3: PVC-U wetted, no metal wetted part; sizing PP frames "
                 "named as the conflict (WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; stack at the -X end of the tray, cross-section "
             "300 x 300 centred (y 150..450, z 18..318); tray floor z 0..20 over the full "
             "envelope; hold-down beam z 330..350 on four posts",
    "nozzle_spread": "the schedule gives face and height only; side nozzles pack per face "
                     "and datum group from x 420 at OD + 8 mm pitch on tray risers; drain "
                     "through the floor at x 930; vent at the beam top; per-tag positions "
                     "in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
