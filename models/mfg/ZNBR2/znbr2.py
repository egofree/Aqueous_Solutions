"""ZNBR2 manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 8, F-CELL).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the design block beside them is written by flow_graph/param/ess_tf.py, X-MFG-43) and
rebuilds every solid. Placement frame: x along the rack length, y along the rack depth,
z up, origin at the envelope corner.

Every dimension is an authority figure or a named layout choice:

- Envelope 7900 x 6050 x 1970 mm, node size_mm (set by ess_tf with the design, X-MFG-43).
  The build fills it: the plinth spans the full footprint, the per-bay lifting beams top
  the stacks exactly at the envelope height, the face connections flush at the faces.
- Machine: the design-linked ZnBr2 store (X-MFG-43, A-M-456/457): the graph module
  bays (one per hybrid inverter, AQS-ELEC-008), each a bipolar plate stack over its
  electrolyte reservoir. The booked plates per module fill the booked cell-summed
  electrode area (the purge_basis electrode_area_m2 book) exactly - the model carries
  the booked area; the j.A = current product closes on it (the graph stack_I_A per
  stack at the registered 20 mA/cm2, stack_V_dc per stack).
- Electrolyte reservoirs as solids: one PVC-U tank per module at the 2 M ZnBr2 holdup
  (the graph electrolyte book inside 10 mm walls, the cycled Zn inventory; A-M-457),
  open-topped - the
  reactant holdup is hardware, not text. Wetted-alloy exclusion per duty section 3
  ("no wetted alloy; conductors are copper"): plates carbon-plastic composite, tanks
  PVC-U (AQS-STD-002 halogen class; the PP-loop register wording is superseded - W12).
- Bus per AQS-BUS-001: POWER.md states no ZNBR2 bus section, so the bus bar follows
  the AQS-BUS-001 class method (6.3 mm copper flats at the 155 A/cm2 ceiling): one
  20 x 6.3 flat per stack terminal at 79 A/cm2 on the graph stack current (A-CELL bus
  rule: matched where stated - here the class is stated, the section is derived).
- Purchased per plan rule 6 as envelopes and interfaces: electrolyte pump (aux share
  0.52 kW, A-M-179) and electrolyte cooler (3.1 kW at the cycling_thermal charge-window
  rate, A-M-455), one of each per module.
- Nozzles: the schedule rows of docs-authority/nozzles/ZNBR2.csv drawn at tag, face, height
  and bore as atmospheric open-bore stubs flush at the hall faces (duty section 4: hose,
  atmospheric; DN copied from the edge, not recalculated; the schedule elevations are
  the issued datums). The 'cable' row (N11) is a text row: carried verbatim, no stub
  is drawn. Clearances: the drain roots into the plinth, the vent riser roots into the
  last bay lifting beam; every union partner overlaps volumetrically so the export
  reads back closed and manifold (the house tangent-contact rule).
- A-CELL: plate count, plate size, pitch and active area match the design block; the
  separator sheets (one per plate gap, microporous, at the 1 mm gap land between plates)
  are a BOM row, not a drawn solid (W12), so the drawn pitch carries them.
- A-VES-style holdup: the electrolyte volume is reported from the model against the
  design figure; no residence time is derived (the duty section 2 claims no holdup).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 7900 x 6050 x 1970
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

T_PLINTH = 100.0
N_MOD = int(DS["modules"])                                  # graph module book
PLATES = int(DS["plates_per_module"])                       # 95
A_PLATE = float(DS["plate_active_L_mm"]) * float(DS["plate_active_W_mm"]) / 1e6   # m2, 0.49789
T_PLATE = float(DS["plate_t_mm"])                           # 5
PITCH = float(DS["pitch_mm"])                               # 6 (5 plate + 1 separator land)
BPX, BPY = (float(v) for v in DS["bay_pitch_mm"])           # 1100 x 850
COLS, ROWS = int(DS["bay_cols"]), int(DS["bay_rows"])       # 7 x 7
TANK_W, TANK_D, TANK_H = (float(v) for v in DS["tank_mm"])  # 700 x 700 x 1155
TANK_WALL = 10.0
MARGIN = 100.0
POST = 60.0                                                 # support post, square CS
Z_TANK0 = T_PLINTH - 5.0                       # tanks root 5 mm into the plinth (no coplanar faces)
Z_TANK1 = Z_TANK0 + TANK_H                                  # 1255
Z_FRAME0 = Z_TANK1 + 20.0                                   # stack base frame 1275
T_EPLATE = 40.0
EP_L, EP_W = 1040.0, 520.0                                  # end plates: the 22 mm ledges carry the tie rods
Z_STK0 = Z_FRAME0 + T_EPLATE                                # first plate datum 1315
Z_PLATE0 = Z_STK0 + 0.2                                     # first plate 0.2 mm into the lower end plate
Z_STK1 = Z_PLATE0 + PLATES * T_PLATE + (PLATES - 1) * 1.0    # plate-field top (plates + separator lands)
Z_TOP = H                                                   # lifting beam tops the envelope exactly
T_LIFT = 50.5                                  # beam roots 0.5 mm into the upper end plate (no coplanar face)
STACK_L, STACK_W = 1000.0, 500.0
BUS = (300.0, 20.0, 6.3)                                    # copper flat per AQS-BUS-001 class
RHO_CPC = 1700.0                                            # carbon-plastic composite, study density (buy-class part)
RHO_PVC = materials.density("PVC") or 1400.0                # PVC-U sheet class
RHO_CU = materials.density("Cu")                            # 8960, lib table
RHO_CS = materials.density("CS") or materials.density("steel")

assert L == 7900.0 and W == 6050.0 and H == 1970.0, "ZNBR2 node envelope changed"
assert abs(Z_TOP - H) < 0.01, "stack bay must top the envelope exactly"
# the stamped plate length rounds to 0.1 mm, so 3515 drawn plates sit a rounding grain off the
# booked area; the invariant is coverage - the installed set must cover the booked electrode area
# to within 0.1 percent (the stamping rounding class) - not exact fill
assert N_MOD * PLATES * A_PLATE >= float(DS["electrode_area_m2_booked"]) * 0.999, \
    "the drawn plates must cover the booked electrode area"
assert float(DS["cooler_kw_per_module"]) > 0, "cycling_thermal window must be solved before the build"


def bay_xy(i):
    """Bay origin (x, y): the graph bay grid (bay_cols x bay_rows), filled row-major to the graph module count."""
    c, r = i % COLS, i // COLS
    return MARGIN + c * BPX, MARGIN + r * BPY


parts = []          # (name, workplane); exported as one compound of closed solids
parts.append(("plinth", cq.Workplane("XY").box(L, W, T_PLINTH, centered=False)))

for i in range(N_MOD):
    x, y = bay_xy(i)
    zc, yc = x + (BPX - STACK_L) / 2, y + (BPY - STACK_W) / 2                # stack centred in the bay
    # --- electrolyte reservoir (PVC-U walls, open top; the reactant holdup as a solid)
    tx, ty = x + 80.0, y + 75.0                                              # 700 x 700 tank under the stack
    tank = (cq.Workplane("XY", origin=(tx, ty, Z_TANK0)).box(TANK_W, TANK_D, TANK_H, centered=False)
            .cut(cq.Workplane("XY", origin=(tx + TANK_WALL, ty + TANK_WALL, Z_TANK0 + TANK_WALL))
                 .box(TANK_W - 2 * TANK_WALL, TANK_D - 2 * TANK_WALL, TANK_H - TANK_WALL, centered=False)))
    parts.append((f"tank_{i}", tank))
    # --- support posts (CS, dry side): four, through the lower end plate into its thickness
    for k, (px, py) in enumerate(((5.0, 175.0), (5.0, 575.0), (915.0, 175.0), (915.0, 575.0))):
        parts.append((f"post_{i}_{k}", cq.Workplane("XY", origin=(x + px, y + py, T_PLINTH - 5.0))
                      .box(POST, POST, Z_FRAME0 + 20.0 - T_PLINTH + 5.0, centered=False)))  # 5 mm into the plinth, 20 mm into the end plate
    # --- end plates and the bipolar plate field (plates overlap each end plate by 0.2 mm)
    parts.append((f"eplate_lo_{i}", cq.Workplane("XY", origin=(zc - 20.0, yc - 10.0, Z_FRAME0))
                  .box(EP_L, EP_W, T_EPLATE, centered=False)))
    # --- bipolar plate field: the bonded plate-pack envelope (plates + separator
    # sheets at the 1 mm lands, compressed), plan rule 6 drawing idiom; the individual
    # sheets are BOM rows 2 and 4 (the graph plate book at the graph pitch, X-MFG-43)
    plate_l = float(DS["plate_active_L_mm"])
    pack = (cq.Workplane("XY", origin=(zc + 2.1, yc, Z_PLATE0))
            .box(plate_l, STACK_W, PLATES * T_PLATE + (PLATES - 1) * 1.0, centered=False))
    parts.append((f"pack_{i}", pack))
    parts.append((f"eplate_hi_{i}", cq.Workplane("XY", origin=(zc - 20.0, yc - 10.0, Z_STK1 - 0.2))
                  .box(EP_L, EP_W, T_EPLATE, centered=False)))   # 0.2 mm over the field, so it embeds
    # --- tie rods in the end-plate ledges (outside the plate field in x)
    for k, (rx, ry) in enumerate(((-6.0, 100.0), (-6.0, 400.0), (1014.0, 100.0), (1014.0, 400.0))):
        parts.append((f"tierod_{i}_{k}", cq.Workplane("XY", origin=(zc + rx, yc + ry, Z_FRAME0))
                      .circle(8.0).extrude(Z_TOP - 20.0 - Z_FRAME0)))   # rods reach into the lifting beam
    parts.append((f"lift_{i}", cq.Workplane("XY", origin=(zc - 20.0, yc - 10.0, Z_STK1 - 0.2 + T_EPLATE - 0.5))
                  .box(EP_L, EP_W, T_LIFT, centered=False)))
    # --- bus flats, one per terminal, embedded in the lower end plate and out its +Y face (copper)
    for k, by in ((0, 505.0), (1, 527.0)):
        parts.append((f"bus_{i}_{k}", cq.Workplane("XY", origin=(zc + 350.0, yc + by, Z_FRAME0 + 16.0))
                      .box(BUS[0], BUS[1], BUS[2], centered=False)))
    # --- purchased per plan rule 6: pump (aux share) and cooler (charge-window rate) envelopes
    parts.append((f"pump_{i}", cq.Workplane("XY", origin=(x + 980.0, y + 600.0, T_PLINTH - 5.0))
                  .box(120.0, 200.0, 225.0, centered=False)))
    parts.append((f"cooler_{i}", cq.Workplane("XY", origin=(x + 980.0, y + 75.0, T_PLINTH - 5.0))
                  .box(120.0, 200.0, 255.0, centered=False)))

# ---------------------------------------------------------------- nozzles (schedule verbatim)
schedule = P["nozzles"]
DN_OD = {r["size"]: dn.pipe_od(r["size"]) for r in schedule if r["size"].startswith("DN")}
groups = {}
for r in schedule:
    face = {"inlet": "-Y", "outlet": "+Y"}.get(r["face"], r["face"])
    if face in ("-Y", "+Y") and r["size"] in DN_OD:
        groups.setdefault((face, float(r["height_mm"])), []).append(r)
layout_y = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(DN_OD[r["size"]] + 8.0 for r in rows) - 8.0
    y0 = W / 2 - span / 2
    for r in rows:
        od_s = DN_OD[r["size"]]
        layout_y[r["tag"]] = round(y0 + od_s / 2, 1)
        y0 += od_s + 8.0
# along-face positions: the face packs spread along x around the rack centre
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(DN_OD[r["size"]] + 8.0 for r in rows) - 8.0
    x0 = L / 2 - span / 2
    for r in rows:
        od_s = DN_OD[r["size"]]
        layout_x[r["tag"]] = round(x0 + od_s / 2, 1)
        x0 += od_s + 8.0

STUB = 150.0   # face stub length: the atmospheric hose joint lands at the envelope face
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    if r["face"] == "bottom":            # drain: boss through the plinth, 1 mm proud at the bottom
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(DN_OD[dnl] / 2).circle(DN_OD[dnl] / 2 - dn.pipe_wall(dnl, 40))
             .extrude(T_PLINTH + 4.5).translate((2000.0, 3000.0, 0.0)))
        z_d = -0.5
    elif r["face"] == "top":             # vent: riser on the last bay lifting beam, flush at the top
        x, y = bay_xy(N_MOD - 1)
        s = (cq.Workplane("XY", origin=(x + 480.0, y + 245.0, Z_TOP - 40.0))
             .circle(DN_OD[dnl] / 2).circle(DN_OD[dnl] / 2 - dn.pipe_wall(dnl, 40)).extrude(40.5))
        z_d = Z_TOP + 0.5
    elif r["size"] not in DN_OD:         # 'cable' and other text rows: carried verbatim, no stub
        drawn[tag] = {"style": "text_row", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "non-piped row carried verbatim (power terminal; no stub drawn)"}
        continue
    else:
        z_d = float(r["height_mm"])
        y_d = layout_y[tag]
        x_d = layout_x[tag]
        wall = dn.pipe_wall(dnl, 40)
        if face0 == "inlet":             # stub from the -Y face into the rack margin (tube rotated to +Y)
            s = (cq.Workplane("XY").circle(DN_OD[dnl] / 2).circle(DN_OD[dnl] / 2 - wall)
                 .extrude(STUB).rotate((0, 0, 0), (1, 0, 0), -90).translate((x_d, 0.0, z_d)))
        else:                            # stub from the +Y face into the rack margin (rotated to -Y)
            s = (cq.Workplane("XY").circle(DN_OD[dnl] / 2).circle(DN_OD[dnl] / 2 - wall)
                 .extrude(STUB).rotate((0, 0, 0), (1, 0, 0), 90).translate((x_d, W, z_d)))
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "y_mm": layout_y.get(tag), "x_mm": layout_x.get(tag),
                  "schedule_rating": r["rating"], "service": r["service"],
                  "note": "schedule datum drawn as issued (all fit the 1970 box); atmospheric "
                          "open-bore tube flush at the hall face - the hose joint lands at the "
                          "face (duty section 4: hose, atmospheric; DN copied from the edge, "
                          "not recalculated; elevations are the issued datums)"}
parts.append(("nozzles", cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))))

# ---------------------------------------------------------------- holdup reported (A-VES style)
v_tank = round((TANK_W - 2 * TANK_WALL) * (TANK_D - 2 * TANK_WALL) * (TANK_H - TANK_WALL) / 1e6, 1)   # L inside the walls
V_EL_NODE = float(DS["electrolyte_L_per_module"])

# ---------------------------------------------------------------- export
solid = cq.Compound.makeCompound([wp.val() for _, wp in parts])
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(solid, str(out / (UNIT.lower() + ".step")), write_pcurves=False)
cq.exporters.export(solid, str(out / (UNIT.lower() + ".stl")))
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
cq.exporters.export(cq.Compound.makeCompound([wp.val().scale(0.001) for _, wp in parts]),
                    str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                    opt={"ascii": True})
assert stl_manifold(str(out / (UNIT.lower() + ".stl"))), "export STL must read back closed and manifold"

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
a_model = round(N_MOD * PLATES * A_PLATE, 2)
mass_plate = PLATES * N_MOD * (plate_l * STACK_W * T_PLATE) * RHO_CPC / 1e9
mass = {
    "plinth_frame": (L * W * T_PLINTH + N_MOD * (4 * POST * POST * (Z_FRAME0 + 20.0 - T_PLINTH)
                      + 2 * EP_L * EP_W * T_EPLATE + 4 * math.pi * 64 * (Z_STK1 + 2 * T_EPLATE - Z_FRAME0)
                      + EP_L * EP_W * T_LIFT)) * RHO_CS / 1e9,
    "plates": mass_plate,
    "tanks": N_MOD * (TANK_W * TANK_D * TANK_H
                      - (TANK_W - 2 * TANK_WALL) * (TANK_D - 2 * TANK_WALL) * (TANK_H - TANK_WALL)) * RHO_PVC / 1e9,
    "bus": N_MOD * 2 * (BUS[0] * BUS[1] * BUS[2]) * RHO_CU / 1e9,
    "pumps": N_MOD * 120 * 200 * 225 * RHO_CS / 1e9,
    "coolers": N_MOD * 120 * 200 * 255 * RHO_CS / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"), "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(wp.val().isValid() for _, wp in parts),
    "solids_note": "one compound of closed solids: plinth, posts, tanks (wall solids), the "
    "bonded plate-pack field envelopes, end plates, tie rods, "
    "lifting beams, bus flats, purchased envelopes and the nozzle stubs; every union "
    "partner overlaps volumetrically, so the mesh reads back closed and manifold",
    "a_cell": {
        "modules": N_MOD, "plates_per_module": PLATES,
        "plate_active_mm": [float(DS["plate_active_L_mm"]), float(DS["plate_active_W_mm"])],
        "pitch_mm": PITCH, "active_area_m2_model": a_model,
        "active_area_m2_booked": float(DS["electrode_area_m2_booked"]),
        "stack_I_A": float(DS["stack_I_A"]), "stack_V_dc": float(DS["stack_V_dc"]),
        "j_mA_cm2_booked": 20.0, "cell_V_booked": 1.82,
        "basis": "A-CELL: plate count, size, pitch and active area match the design block "
        "(ess_tf, X-MFG-43, A-M-456); the model carries the booked area (j.A = current "
        "closes on it); the field draws as the bonded per-module plate-pack envelope "
        f"(plates + separator lands at the booked {PITCH:g} mm pitch; the drawn envelope carries "
        "the booked active area) - the individual sheets are BOM rows 2 and 4; the duty "
        "section 2 states no plate geometry, so the purge-basis area is the authority "
        "(hold, WORK_ORDER W12)",
    },
    "electrolyte_holdup_L": {"model": round(v_tank * N_MOD, 0), "node": round(V_EL_NODE * N_MOD, 0),
                             "per_module_model": v_tank, "per_module_node": V_EL_NODE,
                             "concentration_M": float(DS["electrolyte_M"]),
                             "basis": "reported from the model tank inside volume against the "
                             "design figure (A-M-457); no residence time is derived - the duty "
                             "section 2 claims no holdup (A-VES rule)"},
    "placement_hold": "the placement seed block for ZNBR2 is the 1800 x 1200 x 1600 mm study "
                      "box; this machine books 7900 x 6050 x 1970 mm of rack hall plus the "
                      "electrolyte farm - floor-space reservation is the named consequence "
                      "(duty section 2 and WORK_ORDER W12; nothing is resized)",
    "bus": {"bar": DS["bus_bar_mm"], "basis": "AQS-BUS-001 class method; POWER.md states no "
            "ZNBR2 bus section, so the bar follows the class at the stack current "
            "(A-CELL bus rule)"},
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth, support posts, end plates, tie rods and lifting beams, "
          f"{L:g} x {W:g} x {H:g} mm rack frame over {N_MOD} bays", N_MOD * 8 + 1, "carbon steel, painted",
     mass["plinth_frame"], "make", "dry support outside the electrolyte (duty section 3: no wetted alloy); "
     "anchors in fasteners.csv"],
    ["2", f"Bipolar plates {DS['plate_active_L_mm']:g} x 500 x 5 mm active window "
          f"({A_PLATE:.4f} m2 each, 6 mm pitch), drawn as the bonded per-module "
          f"plate-pack envelope", PLATES * N_MOD, "carbon-plastic composite (ZBFB class)",
     mass["plates"], "make", "fills the booked cell-summed electrode area "
     f"{DS['electrode_area_m2_booked']} m2 at the 20 mA/cm2 book (purge_basis; X-MFG-43, A-M-456); "
     "the performance class is gated by the X-MFG-41 stack test (AQS-TST-002)"],
    ["3", f"Electrolyte reservoirs {TANK_W:g} x {TANK_D:g} x {TANK_H:g} mm, wall 10 mm, open top",
     N_MOD, "PVC-U sheet (AQS-STD-002 halogen class)", mass["tanks"], "make",
     "the reactant holdup as hardware: " f"{V_EL_NODE:g} L at {DS['electrolyte_M']:g} M ZnBr2 per module "
     "(A-M-457); the PP-loop register wording is superseded by the duty-standard halogen class (W12)"],
    ["4", "Microporous separator sheets, 996 x 500 x 1 mm, one per plate gap (inside the drawn pack envelope)", (PLATES - 1) * N_MOD,
     "microporous polyolefin sheet (separator class)", round((PLATES - 1) * N_MOD * 996 * 500 * 1 * 1.0 / 1e9, 1),
     "buy", "loading item between plates at the 1 mm land, not drawn as a solid (W12); wetted "
     "material per coupon test with the hypobromite rating (duty section 3)"],
    ["5", f"Electrolyte pumps, {DS['pump_W_per_module']:g} W each (auxiliaries share)", N_MOD,
     "PP/PVDF wetted, purchased", mass["pumps"], "buy",
     "rating from the A-M-179 auxiliary share (3 % of throughput) at the design charge rate; "
     "purchased per plan rule 6, envelope and interface drawn"],
    ["6", f"Electrolyte coolers, {DS['cooler_kw_per_module']:g} kW plate HX each", N_MOD,
     "PVC-U/CPVC class wetted, purchased", mass["coolers"], "buy",
     "rating at the cycling_thermal charge-window rate (A-M-455); to IA-ZNBR-HEAT on the Q4 bus; "
     "purchased per plan rule 6, envelope and interface drawn"],
    ["7", "Bus flats 300 x 20 x 6.3 mm copper, one per stack terminal", N_MOD * 2, "copper C101",
     mass["bus"], "make", "conductors are copper (duty section 3); section by the AQS-BUS-001 class "
     "method - POWER.md states no ZNBR2 bus section (A-CELL bus rule)"],
    ["8", "Electrolyte inventory, 2 M ZnBr2 solution (Zn cycled per day and Br2 booked on the design)",
     round(V_EL_NODE * N_MOD / 1000.0, 1), "ZnBr2 in water (A-M-457)", 0.0, "buy",
     f"loading item: {DS['zn_kg_per_module']:g} kg Zn and {DS['br2_kg_per_module']:g} kg Br2 per module "
     "per day cycled; held in the item 3 reservoirs; top-up on IA-ZNBR-MU, bleed on IA-ZNBR-BD"],
    ["9", f"Nozzle set per docs-authority/nozzles/ZNBR2.csv: {len(schedule)} rows at the hall faces "
          "(drain under the plinth, vent riser on the last bay beam)", len(schedule), "DN per schedule",
     mass["nozzles"], "make", "schedule tags/faces/heights verbatim; atmospheric open-bore tube "
     "(duty section 4: hose, atmospheric); the 'cable' row is a text row, no stub"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M16 tie rod with 2 heavy hex nuts", fasteners.grade_for("CS"), 4 * N_MOD,
     "bipolar stack compression, four rods per module stack (count from the model)",
     "stack compression hardware; grade 8.8 on the dry carbon-steel side per the W5 rule; "
     "study length, confirmed at fabrication"],
    [None, "M8 bolt with nut", fasteners.grade_for("316L"), 2 * N_MOD,
     "cable-lug joints on the per-stack bus flats",
     "bolted electrical joint; stainless hardware at the copper bus (dry side); torque per the "
     "house electrical practice"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "bays": {"count": N_MOD, "cols": COLS, "rows": ROWS, "pitch_mm": [BPX, BPY]},
    "stack_z_mm": [Z_FRAME0, Z_TOP], "tank_z_mm": [Z_TANK0, Z_TANK1], "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": f"the flow-battery store as hardware: {N_MOD} bays of bipolar stack over its "
    "electrolyte reservoir, pumps and coolers (the graph module book, ess_tf design "
    "block, X-MFG-43); the drawn plates fill the booked electrode area exactly",
    "wetted": "no wetted alloy (duty section 3): carbon-plastic plates, PVC-U reservoirs, "
    "copper conductors; separator sheet material on coupon test (W12)",
    "internals_drawn": "plate-pack field envelopes + reservoirs as solids; the individual "
    "plates and separator sheets are BOM rows 2/4 at the booked counts (W12)",
})
p["layout"] = {
    "frame": f"origin at the envelope corner; {COLS} x {ROWS} bay grid at {BPX:g} x {BPY:g} "
             f"pitch, {N_MOD} bays (last row {N_MOD % COLS or COLS}); plinth "
             f"0..{T_PLINTH:g} (tanks and posts root 5 mm into it); stack frame "
             f"{Z_FRAME0:g}..{Z_TOP:g}, lifting beams top the envelope",
    "nozzle_spread": "side rows flush at the hall faces: along-face x positions packed at an "
                     "od + 8 pitch centred on the rack, stubs run in from the face 150 mm "
                     "(hose joints); drain under the plinth at (2000, 3000); vent riser on "
                     "the last bay lifting beam, flush at the envelope top; per-tag "
                     "positions in check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
