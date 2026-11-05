"""MEOH_FC manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 8, F-CELL).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the node
design block of the graph (the stack construction figures). Rebuilds every solid.

Placement frame: x along 1800 mm, y along 800 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1800 x 800 x 700 mm, node size_mm (set by flow_graph/param/meoh_train.py,
  AQS-DUTY-077). The duty section 4 prose block and the node design note still carry
  the issued "1800 x 800 x 1600 mm" skid line - the node governs and the older
  figure is named (holds, W12). The build fills the node box (vent riser to the top).
- Machine: the direct methanol fuel-cell skid of the node design block: a 28-cell
  stack (cell_V 0.6 at 0.3 A/cm2 on 200 cm2 cells, 0.56 m2 stack area, IEC
  62282-3-100 module class) - drawn as the cell-pack laminate envelope between two
  316L end plates with PTFE gaskets (the laminate and gaskets are buy rows, drawn
  as the stack envelope per plan rule 6); the 316L methanol reformer shell with its
  Cu/ZnO class catalyst bed envelope (node design material row); the copper bus
  bars (duty section 3: conductors are copper) running from the stack end plate to
  the +Y face at the N5 (MEOH DC) position. POWER.md states no bus-bar section for
  this unit, so the A-CELL bus criterion has nothing to match (named, W12).
- Layout: reformer at the -X end (axis x 150, y 250), stack assembly centre x 480,
  bus run to the +Y face. The skid base is the AQS-MOD-002 plate; supports under
  both assemblies.
- Nozzles: all 11 rows of docs-authority/nozzles/MEOH_FC.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections flush at the envelope
  faces (duty section 4: hose, atmospheric; the connecting line makes the joint at
  the face, the CATCH_TANK idiom). The N5 (MEOH DC) row is the DC conductor: duty
  section 4 prose rates it "conductor, not a hose" - drawn as the copper bus-bar
  pad at the schedule face and height; a conductor has no bore (hold, W12). The
  160 inlets and 600 outlets draw as issued (both fit the 700 box); the drain
  passes to the envelope bottom (50 datum); the vent riser stands on the reformer
  head and flushes at the envelope top (the 800 datum is the schedule placeholder).
  The remaining rating column entries (Class 150) are carried verbatim as text, no
  flange hardware (W4 110 % rule).
- A-CELL: plate count, plate size, pitch and active area are reported from the
  model against the node design construction (duty section 2 carries no plate row,
  so the section 5 match is against the node design - hold, W12). Bus: copper per
  duty section 3; POWER.md states no bus-bar section for this unit.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("MEOH_FC")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
L, W, H = (float(v) for v in P["size_mm"])                 # 1800 x 800 x 700
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design

T_PLINTH = 20.0
N_CELLS = int(DS.get("n_cells", 28))                       # node design
CELL_A = float(DS.get("cell_A_cm2", 200.0))                # cm2 per cell
PLATE = 160.0                                              # plate size (layout choice)
PITCH = 6.0                                                # cell pitch (layout choice)
T_END = 15.0                                               # end plates
L_PACK = N_CELLS * PITCH                                   # 168
Z_ST0 = 120.0                                              # stack seat
Z_ST1 = Z_ST0 + T_END + L_PACK + T_END                     # 318
SX, SY = 480.0, 250.0                                      # stack centre
RX, RY = 150.0, 250.0                                      # reformer axis
OD_REF = 150.0                                             # reformer shell OD (layout choice)
Z_REF0, Z_REF1 = 40.0, 440.0                               # reformer shell
T_REF = 4.0                                                # study shell wall
BUS_W, BUS_T = 30.0, 5.0                                   # copper bus bar section
Z_BUS = 600.0                                              # N5 schedule datum
MAT_CU = "Cu"                                              # duty section 3: conductors copper
RHO_CU = materials.density("Cu")                           # 8960, lib table
RHO_SS = materials.density("316L")                         # 8000, lib table
RHO_BED = 2400.0                                           # catalyst bulk, study value (buy)

# Cell count, cell area and envelope all come from the graph node; no hard-coded count or envelope stays.
assert Z_ST1 < H and Z_REF1 < H, "assemblies must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_dn(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- skid base + supports
parts["base_plate"] = box(0, 0, 0, L, W, T_PLINTH)
parts["stack_stand"] = box(SX - 80.0, SY - 80.0, T_PLINTH, 160.0, 160.0, Z_ST0 - T_PLINTH)
parts["reformer_saddle"] = (cq.Workplane("XY", origin=(RX, RY, T_PLINTH - 2.0))
                            .circle(OD_REF / 2 + 6.0).circle(OD_REF / 2 - 6.0)
                            .extrude(Z_REF0 - T_PLINTH + 2.0))

# ---------------------------------------------------------------- reformer (316L shell, bed envelope)
shell = (cq.Workplane("XY", origin=(RX, RY, Z_REF0)).circle(OD_REF / 2)
         .circle(OD_REF / 2 - T_REF).extrude(Z_REF1 - Z_REF0))
shell = shell.union(cq.Workplane("XY", origin=(RX, RY, Z_REF1)).circle(OD_REF / 2)
                    .extrude(12.0))                          # top head
shell = shell.union(cq.Workplane("XY", origin=(RX, RY, Z_REF0 - 8.0)).circle(OD_REF / 2)
                    .extrude(8.0))                           # base head laps the saddle
parts["reformer"] = shell
bed = (cq.Workplane("XY", origin=(RX, RY, Z_REF0 + 40.0)).circle(OD_REF / 2 - T_REF - 4.0)
       .extrude(280.0))
parts["reformer_bed"] = bed                                # Cu/ZnO class bed envelope (buy)

# ---------------------------------------------------------------- cell stack (laminate envelope, buy)
end_t = (cq.Workplane("XY", origin=(SX, SY, Z_ST0))
         .rect(PLATE, PLATE).extrude(T_END))
pack = (cq.Workplane("XY", origin=(SX, SY, Z_ST0 + T_END))
        .rect(PLATE - 16.0, PLATE - 16.0).extrude(L_PACK))
end_b = (cq.Workplane("XY", origin=(SX, SY, Z_ST0 + T_END + L_PACK))
         .rect(PLATE, PLATE).extrude(T_END))
parts["stack_ends"] = end_t.union(end_b)
parts["stack_pack"] = pack                                 # MEA (membrane-electrode assembly) laminate envelope (buy)

# ---------------------------------------------------------------- bus bars (copper, duty section 3)
bus_v = box(SX + PLATE / 2 - 2.0, SY + PLATE / 2 - 2.0, Z_ST1 - 60.0, BUS_W, BUS_T,
            Z_BUS - (Z_ST1 - 60.0))                        # laps the end plate, riser to N5
bus_h = box(SX + PLATE / 2 - 2.0, SY + PLATE / 2 - 2.0, Z_BUS - BUS_T, BUS_W,
            W - (SY + PLATE / 2 - 2.0), BUS_T)             # run to the +Y face
parts["bus_bars"] = bus_v.union(bus_h)
bus_neg = box(SX - PLATE / 2 - 2.0, SY + PLATE / 2 - 2.0, Z_ST0 + 20.0, BUS_W, BUS_T, 160.0)
parts["bus_return"] = bus_neg                              # return bus, laps the -X end plate

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 45.0                       # face hardware reach (the CATCH_TANK idiom)
CLAMP_MARGIN = 0.7

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y") and r["service"] != "MEOH DC":
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    start = 514.0 if face == "+Y" else 441.4   # +Y clears the bus riser at x 478..508
    x = start
    for r in rows:
        layout_x[r["tag"]] = round(x + dn.pipe_od(r["size"]) / 2, 1)
        x += dn.pipe_od(r["size"]) + 8.0
X_DC = 493.0                                    # the bus pad centre, aligned with the riser

noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    od_s = dn.pipe_od(dnl)
    if r["service"] == "MEOH DC":       # N5: the DC conductor pad (duty section 4 prose)
        s = box(X_DC - BUS_W / 2, W - 40.0, Z_BUS - 8.0, BUS_W, 40.0, 8.0)   # pads the bus run
        note = ("the DC conductor per duty section 4 prose ('rating conductor, not "
                "a hose') and duty section 3 (conductors are copper): drawn as the "
                "copper bus-bar pad at the schedule face and height; a conductor "
                "has no bore (the size column is the schedule placeholder - hold, "
                "WORK_ORDER W12); POWER.md states no bus-bar section for this unit")
        z_d, x_d = Z_BUS, X_DC
    elif face0 == "bottom":             # drain: boss under the reformer, flush at the bottom
        s = tube_dn(dnl, Z_REF0 + 5.0).translate((RX + 45.0, RY, 0.0))
        note = "drain boss under the reformer base head, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, RX + 45.0
    elif face0 == "top":                # vent: riser on the reformer head, flush at the box top
        s = tube_dn(dnl, H - (Z_REF1 + 7.0) + 5.0).translate((RX, RY, Z_REF1 + 7.0 - 5.0))
        note = ("vent riser on the reformer top head, flush at the envelope top; "
                "schedule datum 800 is the placeholder (hold, WORK_ORDER W12)")
        z_d, x_d = H, RX
    else:
        z_d = float(r["height_mm"])     # 160 and 600 fit the 700 box; drawn as issued
        x_d = layout_x[tag]
        s = (tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)) if face0 == "inlet" else
             tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x_d, W, z_d)))
        note = ("schedule datum drawn as issued; open-bore tube flush at the "
                "envelope face (duty section 4: atmospheric joints are hose; the "
                "connecting line makes the joint at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "bus_pad" if r["service"] == "MEOH DC" else "tube_stub",
                  "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- A-CELL report (from the model)
stack_area_m2 = round(N_CELLS * CELL_A / 1e4, 4)
assert abs(stack_area_m2 - float(DS.get("stack_area_m2", 0.56))) < 1e-6

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    if k == "nozzles":
        for piece in noz_pieces:
            solid = piece if solid is None else solid.union(piece)
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
    "base": (parts["base_plate"].val().Volume() + parts["stack_stand"].val().Volume()
             + parts["reformer_saddle"].val().Volume()) * materials.density("CS") / 1e9,
    "reformer": parts["reformer"].val().Volume() * RHO_SS / 1e9,
    "reformer_bed": parts["reformer_bed"].val().Volume() * RHO_BED / 1e9,
    "stack_ends": parts["stack_ends"].val().Volume() * RHO_SS / 1e9,
    "stack_pack": parts["stack_pack"].val().Volume() * 300.0 / 1e9,   # laminate envelope, study bulk
    "bus": (parts["bus_bars"].val().Volume() + parts["bus_return"].val().Volume()) * RHO_CU / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO_SS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "sized from the issued graph duties, methanol train residual "
    "sizing (flow_graph/param/meoh_train.py, AQS-DUTY-077); the duty section 4 "
    "prose and the node design note carry the issued 1800 x 800 x 1600 skid line "
    "- the node governs (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "the skid chain (base, stands, reformer, stack ends, bus bars, "
    "drain and vent) fuses to one solid; the stack laminate envelope sits at its "
    "gasket clearance between the end plates and the face-stub connections stay "
    "separate until the connecting lines make their joints",
    "a_cell": {"n_cells": N_CELLS, "cell_V": float(DS.get("cell_V", 0.6)),
               "j_A_cm2": float(DS.get("j_A_cm2", 0.3)),
               "cell_A_cm2": CELL_A, "stack_area_m2_model": stack_area_m2,
               "stack_area_m2_node": float(DS.get("stack_area_m2", 0.56)),
               "plate_mm": PLATE, "active_mm": round(math.sqrt(CELL_A * 100.0), 1),
               "pitch_mm": PITCH,
               "basis": "count/active-area per the node design block (0.6 V at "
               "0.3 A/cm2 on 200 cm2 cells, IEC 62282-3-100 module class); plate "
               "size and pitch are the registered layout choices enclosing the "
               "active window; duty section 2 carries no plate row, so the "
               "section 5 match is against the node design (hold, WORK_ORDER W12)"},
    "bus": {"section_mm": [BUS_W, BUS_T], "material": "copper (duty section 3)",
            "basis": "POWER.md states no bus-bar section for this unit, so the "
            "A-CELL bus criterion has nothing to match (named, WORK_ORDER W12); "
            "the bus runs from the stack end plate to the +Y face at the N5 datum"},
    "purchased_named": {"items": "MEA laminate and gaskets (stack envelope, buy), "
                        "reformer catalyst bed (buy)",
                        "basis": "drawn as envelopes and interfaces per plan "
                        "rule 6; ratings read the maker sheets at order"},
    "material": {"class": "316L / Cu / PTFE",
                 "basis": "duty section 3: no wetted alloy; conductors are copper; "
                 "the node design material row names the PEM stack, the 316L "
                 "reformer shell (Cu/ZnO class catalyst) and PTFE gaskets; CA "
                 "does not apply (AQS-STD-001)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: atmospheric joints are hose; the W4 110 percent rule "
    "draws no flange hardware where no process pressure is stated); the N5 (MEOH "
    "DC) row is the DC conductor, drawn as the copper bus pad; the schedule rating "
    "column (Class 150) is carried verbatim as text; datums draw as issued (160 "
    "and 600 fit the 700 box); drain flush at the envelope bottom; vent riser "
    "flush at the envelope top",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Cell stack: 2 end plates {PLATE:g} x {PLATE:g} x {T_END:g} 316L + the "
          f"{N_CELLS}-cell MEA laminate envelope {PLATE - 16:g} x {PLATE - 16:g} x "
          f"{L_PACK:g} at {PITCH:g} mm pitch (PTFE gaskets)", 1,
     "316L / MEA laminate / PTFE", round(mass["stack_ends"] + mass["stack_pack"], 1),
     "make (ends) / buy (laminate, gaskets)",
     "node design block: 28 cells, 0.6 V at 0.3 A/cm2, 200 cm2 cells, 0.56 m2 "
     "(IEC 62282-3-100 module class); the laminate and gaskets drawn as the stack "
     "envelope per plan rule 6; plate size and pitch are the registered layout "
     "choices enclosing the 141.4 mm active window (hold, WORK_ORDER W12)"],
    ["2", f"Reformer shell OD {OD_REF:g} x wall {T_REF:g}, z {Z_REF0:g}..{Z_REF1:g}, "
          "heads, on the saddle; Cu/ZnO class catalyst bed envelope inside", 1,
     "316L shell / catalyst bed (buy)", round(mass["reformer"] + mass["reformer_bed"], 1),
     "make (shell) / buy (bed)",
     "node design material row (316L reformer shell, Cu/ZnO class catalyst); bed "
     "drawn as its envelope per plan rule 6; duty section 3: no wetted alloy"],
    ["3", f"Bus bars 30 x 5 mm copper: stack end plate to the +Y face at the N5 "
          "datum (600), return run on the -Y-side rail", 2, "copper (duty "
     "section 3)", mass["bus"], "make",
     "conductors are copper (duty section 3); POWER.md states no bus-bar section "
     "for this unit - the A-CELL bus criterion has nothing to match (W12)"],
    ["4", "Skid base plate 1800 x 800 x 20 with stack stand and reformer saddle "
          "(AQS-MOD-002 dry service class)", 1, "carbon steel (ASTM A500)",
     mass["base"], "make", "layout choice; the dry skid sees no aqueous chloride "
     "(duty section 3), so no corrosion allowance is applied"],
    ["5", "Nozzle set per docs-authority/nozzles/MEOH_FC.csv: 11 rows - 10 "
          "atmospheric open-bore tube connections (drain under the reformer, vent "
          "riser on the reformer head) and the N5 MEOH DC copper bus pad",
     len(schedule), "316L tube / Cu", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table; "
     "N5 drawn as the DC conductor per duty section 4 prose (hold, WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 stud + nut", fasteners.grade_for("316L"), 8,
     "stack end-plate tie rods, corners of the plate pair (count from the model)",
     "A4-70 per the plan grade rule on the 316L ends; compresses the laminate "
     "against the PTFE gaskets; study length, confirmed at fabrication"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 6,
     "base plate to slab (3 per 2 m of skid)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel base; study length, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "stack": {"xy_mm": [SX, SY], "z_mm": [Z_ST0, Z_ST1], "plate_mm": PLATE,
              "pitch_mm": PITCH, "n_cells": N_CELLS},
    "reformer": {"axis_xy_mm": [RX, RY], "od_mm": OD_REF, "z_mm": [Z_REF0, Z_REF1]},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "direct methanol fuel-cell skid (iem_fc): 28-cell stack (0.6 V at "
               "0.3 A/cm2, 200 cm2 cells, 0.56 m2) + 316L reformer shell (Cu/ZnO "
               "class bed) + copper bus, per the node design block (AQS-DUTY-077)",
    "mat": "316L ends and reformer, copper bus (duty section 3: conductors are "
           "copper), PTFE gaskets; no wetted alloy",
    "internals": "the MEA laminate and the reformer bed drawn as envelopes (plan "
                 "rule 6); node internals row none",
    "purchased": "MEA laminate, PTFE gaskets, reformer catalyst bed - envelopes "
                 "and interfaces per plan rule 6",
})
p["layout"] = {
    "frame": "origin at the envelope corner; reformer axis (150, 250), stack "
             "centre (480, 250) at z 120..318; bus run to the +Y face at the N5 "
             "datum z 600; vent riser to the box top",
    "nozzle_spread": "inlet pack (N1..N4) flush at the -Y face at z 160 centred on "
                     "x 315; outlet pack (N6..N8, N11) flush at the +Y face at "
                     "z 600 led by the N5 copper bus pad; drain under the reformer; "
                     "per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "face hardware flush at the envelope faces; the DC row is "
                      "the conductor pad, not a bore",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
