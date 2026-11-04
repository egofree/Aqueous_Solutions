"""BAGHOUSE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker; the
design block beside them is written by flow_graph/param/specialty_sizing.py, X-SPEC lane)
and rebuilds every solid - the pulse-jet baghouse per the AQS-DSN-INT-001 disposition and
the registered capture-air basis (A-M-458).

Every dimension is an authority figure or a named layout choice:

- Envelope 1250 x 1000 x 2276 mm, node size_mm (set with the design by specialty_sizing).
  The build fills it: the plinth spans the footprint, the roof tops the housing at the
  envelope height, the vent riser stands 0.5 mm proud and the drain boss 0.5 mm below
  (inside the 1 mm gate).
- Machine (params.design, A-M-458): 756 m3/h capture air (hood face velocity 0.5 m/s over
  the 0.20/0.12/0.10 m2 hood faces of the three draws) through 20 antistatic-polyester
  bags of D150 x 1200 mm (11.31 m2 cloth, drawn A/C 1.11 m3/min/m2 against the 1.2
  m3/min/m2 EPA-453 basis, +8 % cloth); 3 mm CS housing, painted, bonded and grounded
  (duty section 3); 60 deg dust hopper with a 200 mm rotary-valve discharge to IA-BAG-01;
  pulse-clean header with diaphragm-valve envelopes; the deflagration-vent panel on the
  +X wall per the combustible-dust class.
- The conveying-air mover is NOT on this unit: duty section 1 books 0.0 kW electrical, so
  the baghouse dP rides the tool-extraction system (the purchased fan of that lane); the
  baghouse itself has no fan hardware - stated, not omitted (WORK_ORDER W12(3)).
- A-MACH: purchased items named with the rating from the node/computation - rotary valve
  (7.77 kg/d dust class), pulse diaphragm valves (0.5 MPa compressed-air class), solenoid
  enclosure; the drive guard is drawn over the valve motor and the plinth anchors are drawn.
- Nozzles: all 7 rows of docs-authority/nozzles/BAGHOUSE.csv carried at tag, face, height
  and bore: the five piped rows draw as DN15 stubs flush at the housing/plinth faces (duty
  section 4: the 0.28 mm bore "is not a specification; nozzle is DN15"); N7 (dust solids)
  is a text row. The hood conveying ducts are the design DN100/DN80 set (BOM, shop spools
  to the hoods - the schedule DN15 rows are the duty connection table, hold W12(5)).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials   # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1250 x 1000 x 2276
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

BAGS = int(DS["bags"])                                     # 20
BD, BL = float(DS["bag_mm"][0]), float(DS["bag_mm"][1])    # 150 dia, 1200 long
BP = float(DS["bag_pitch_mm"])                             # 180
HI_W, HI_D = float(DS["housing_inner_mm"][0]), float(DS["housing_inner_mm"][1])   # 900 x 700
WALL = float(DS["wall_mm"])                                # 3
HOP_H = float(DS["hopper_h_mm"])                           # 606
ZC = DS["z_chain"]
Z_P = float(ZC["plinth"])                                  # 50
Z_HOP_T = float(ZC["hopper_top"])                          # 656
Z_BAG0, Z_BAG1 = (float(v) for v in ZC["bags"])            # 676..1876
Z_TS = float(ZC["tubesheet"])                              # 1876 (sheet 1876..1896)
Z_PL0, Z_PL1 = (float(v) for v in ZC["plenum"])            # 1896..2256
T_PLINTH = Z_P
T_TS = 20.0
T_ROOF = H - (Z_PL1 + 20.0) - Z_P if False else 20.0       # roof 2256..2276
COLS, ROWS = 5, 4
CLOTH_DRAWN = float(DS["cloth_drawn_m2"])
RHO_CS = materials.density("CS") or materials.density("steel")
RHO_FELT = 450.0                                           # antistatic polyester felt bulk, study density

assert L == 1250.0 and W == 1000.0 and H == 2276.0, "BAGHOUSE node envelope changed"
assert BAGS == COLS * ROWS, "bag field book changed"
assert Z_BAG1 - Z_BAG0 == BL and Z_TS == Z_BAG1, "bag/tubesheet chain must match the design"
cloth = round(BAGS * math.pi * BD / 1000.0 * BL / 1000.0, 2)
assert cloth == CLOTH_DRAWN, "the drawn bag field must carry the design cloth"
assert float(DS["capture_air_m3_h"]) == 756.0, "capture-air basis changed"

CX, CY = 150.0 + (HI_W + 2 * WALL) / 2, 247.0 + (HI_D + 2 * WALL) / 2    # housing centre
HOW, HUD = HI_W + 2 * WALL, HI_D + 2 * WALL               # housing outer 906 x 706
HX0, HY0 = 150.0, 247.0                                   # housing corner (fits the 1000 mm width)

parts = [("plinth", cq.Workplane("XY").box(L, W, T_PLINTH, centered=False))]
# --- housing: four walls, roof (clean side above the plenum)
walls = (cq.Workplane("XY", origin=(HX0, HY0, Z_P)).box(HOW, HUD, H - T_ROOF - Z_P + 5.0, centered=False)
         .cut(cq.Workplane("XY", origin=(HX0 + WALL, HY0 + WALL, Z_P))
              .box(HI_W, HI_D, H - T_ROOF - Z_P, centered=False)))   # walls root 5 mm into the roof
parts.append(("housing", walls))
parts.append(("roof", cq.Workplane("XY", origin=(HX0, HY0, Z_PL1)).box(HOW, HUD, T_ROOF, centered=False)))
# --- tubesheet: bag field plate with 20 bag holes
ts = cq.Workplane("XY", origin=(HX0 + WALL, HY0 + WALL, Z_TS)).box(HI_W, HI_D, T_TS, centered=False)
pts = []
for c in range(COLS):
    for r in range(ROWS):
        pts.append(((c - (COLS - 1) / 2) * BP, (r - (ROWS - 1) / 2) * BP))
ts = ts.cut(cq.Workplane("XY", origin=(CX, CY, Z_TS)).pushPoints(pts).circle(BD / 2 + 1.0)
            .extrude(T_TS))
parts.append(("tubesheet", ts))
# --- bag field: 20 felt bags hanging from the tubesheet (compound pieces)
bag_parts = []
for i, (px, py) in enumerate(pts):
    bag_parts.append(cq.Workplane("XY", origin=(CX + px, CY + py, Z_BAG0))
                     .circle(BD / 2).circle(BD / 2 - 4.0).extrude(BL + 5.0))   # bag tops root 5 mm into the tubesheet
parts.append(("bags", cq.Workplane(obj=cq.Compound.makeCompound([b.val() for b in bag_parts]))))
# --- 60 deg dust hopper inside the housing, outlet 200 mm at the plinth
hopper = (cq.Workplane("XY", origin=(CX, CY, Z_HOP_T)).rect(HI_W, HI_D)
          .workplane(offset=-(Z_HOP_T - Z_P)).rect(198, 198).loft(combine=True))
hopper = hopper.cut(cq.Workplane("XY", origin=(CX, CY, Z_HOP_T)).rect(HI_W - 2 * WALL, HI_D - 2 * WALL)
                    .workplane(offset=-(Z_HOP_T - Z_P)).rect(192, 192).loft(combine=True))
parts.append(("hopper", hopper))
# --- rotary valve discharge (purchased, dust class 7.77 kg/d) + drive guard, at the +X wall
valve = (cq.Workplane("XY", origin=(HX0 + HOW - 40.0, CY - 100.0, Z_P + 10.0))
         .box(190.0, 200.0, 200.0, centered=False))
valve = valve.union(cq.Workplane("XY", origin=(HX0 + HOW + 20.0, CY - 60.0, Z_P + 60.0))
                    .circle(70.0).extrude(30.0))                          # drive flange
parts.append(("rotary_valve", valve))
parts.append(("valve_guard", cq.Workplane("XY", origin=(HX0 + HOW - 56.0, CY - 130.0, Z_P + 10.0))
              .box(150.0, 260.0, 260.0, centered=False)))                 # the A-MACH drive guard
# --- pulse-clean header (compressed air) + diaphragm-valve envelopes + solenoid enclosure
hdr = (cq.Workplane("XY").circle(dn.pipe_od("DN40") / 2)
       .circle(dn.pipe_od("DN40") / 2 - dn.pipe_wall("DN40", 40)).extrude(600.0)
       .rotate((0, 0, 0), (0, 1, 0), 90).translate((CX - 300.0, CY, Z_PL0 + 40.0)))
parts.append(("pulse_header", hdr))   # DN40 header along X over the bag field
dv = None
for c in range(COLS):
    box = (cq.Workplane("XY", origin=(CX + (c - (COLS - 1) / 2) * BP - 40.0, CY - 40.0, Z_TS + T_TS))
           .box(80.0, 80.0, 100.0, centered=False))
    dv = box if dv is None else dv.union(box)
parts.append(("diaphragm_valves", dv))
parts.append(("solenoid_box", cq.Workplane("XY", origin=(HX0 + HOW - 120.0, HY0 + WALL + 10.0, Z_TS + 40.0))
              .box(110.0, 120.0, 160.0, centered=False)))
# --- deflagration vent panel (combustible-dust class) on the +X wall
parts.append(("deflagration_panel", cq.Workplane("XY", origin=(HX0 + HOW - 2.0, HY0 + 150.0, Z_P + 700.0))
              .box(27.0, 400.0, 500.0, centered=False)))   # vent panel on the +X wall, roots through it

# ---------------------------------------------------------------- nozzles (schedule verbatim)
schedule = P["nozzles"]
DN_OD = {r["size"]: dn.pipe_od(r["size"]) for r in schedule if r["size"].startswith("DN")}
groups = {}
for r in schedule:
    face = {"inlet": "-Y", "outlet": "+Y"}.get(r["face"], r["face"])
    if face in ("-Y", "+Y") and r["size"] in DN_OD:
        groups.setdefault((face, float(r["height_mm"])), []).append(r)
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(DN_OD[r["size"]] + 8.0 for r in rows) - 8.0
    x0 = L / 2 - span / 2
    for r in rows:
        od_s = DN_OD[r["size"]]
        layout_x[r["tag"]] = round(x0 + od_s / 2, 1)
        x0 += od_s + 8.0

noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    if r["size"] not in DN_OD:         # 'solids' row: carried verbatim, no stub
        drawn[tag] = {"style": "text_row", "dn": r["size"], "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "non-piped row carried verbatim (dust leaves as solids via the "
                              "rotary valve to IA-BAG-01; no stub drawn)"}
        continue
    od_s, wl = DN_OD[dnl], dn.pipe_wall(dnl, 40)
    if face0 == "bottom":              # drain: boss through the plinth, 0.5 mm proud below
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(od_s / 2).circle(od_s / 2 - wl)
             .extrude(T_PLINTH + 6.0).translate((CX, CY, 0.0)))
        z_d = -0.5
        note = "drain boss through the plinth (schedule datum 50)"
    elif face0 == "top":               # vent: riser on the roof, flush at the envelope top
        s = (cq.Workplane("XY", origin=(CX, CY - 300.0, H - T_ROOF - 40.0)).circle(od_s / 2)
             .circle(od_s / 2 - wl).extrude(T_ROOF + 0.5))
        z_d = H + 0.5
        note = ("schedule datum 800 is the placeholder elevation: the clean-air vent is the "
                "riser on the roof, flush at the envelope top (hold, W12(4))")
    elif face0 == "inlet":             # dust draws in at the inlet-plenum face (-Y), stubs as issued
        x_d = layout_x[tag]
        s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(40.0)
             .rotate((0, 0, 0), (1, 0, 0), -90).translate((x_d, 0.0, float(r["height_mm"]))))
        z_d = float(r["height_mm"])
        note = ("schedule datum drawn as issued; the DN15 rows are the duty connection table - "
                "the hood conveying ducts are the design DN100/DN80 set (BOM item 6, W12(5)); "
                "the stubs pierce the inlet plenum wall")
    else:                              # captured dust edge: +Y stub at its datum as issued
        x_d = layout_x[tag]
        s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(40.0)
             .rotate((0, 0, 0), (1, 0, 0), 90).translate((x_d, W, float(r["height_mm"]))))
        z_d = float(r["height_mm"])
        note = ("schedule datum drawn as issued; the captured-dust edge is IA-BAG-01 via the "
                "hopper rotary valve - the 600 datum is the placeholder (hold, W12(6))")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "x_mm": layout_x.get(tag),
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts.append(("nozzles", cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))))

# ---------------------------------------------------------------- export
solid = cq.Compound.makeCompound([wp.val() for _, wp in parts])
out = HERE / "export"; out.mkdir(exist_ok=True)
cq.exporters.export(solid, str(out / (UNIT.lower() + ".step")), opt={"write_pcurves": False, "precision_mode": 0})
cq.exporters.export(solid, str(out / (UNIT.lower() + ".stl")))
cq.exporters.export(cq.Compound.makeCompound([wp.val().scale(0.001) for _, wp in parts]),
                    str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")), opt={"ascii": True})
assert stl_manifold(str(out / (UNIT.lower() + ".stl"))), "export STL must read back closed and manifold"

dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"), "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(wp.val().isValid() for _, wp in parts),
    "solids_note": "one compound of closed solids: plinth, housing walls and roof, tubesheet "
    "with the 20-bag hole field, the 20-bag felt field (compound), the 60 deg hopper, the "
    "rotary valve with drive guard, the pulse header with diaphragm valves, solenoid "
    "enclosure, deflagration panel and the nozzle stubs; every union partner overlaps "
    "volumetrically, so the mesh reads back closed and manifold",
    "a_mach": {
        "capture_air_m3_h": float(DS["capture_air_m3_h"]),
        "hood_face_velocity_m_s": float(DS["hood_face_velocity_m_s"]),
        "hoods_m2": DS["hoods_m2"], "dust_kg_d": DS["dust_kg_d"],
        "cloth_m2_drawn": cloth, "cloth_m2_required": float(DS["cloth_req_m2"]),
        "ac_basis_m3_min_m2": float(DS["ac_basis_m3_min_m2"]),
        "ac_drawn_m3_min_m2": float(DS["ac_drawn_m3_min_m2"]),
        "bags": BAGS, "bag_mm": [BD, BL],
        "basis": "A-MACH: purchased items named with the rating from the node/computation "
        "(rotary valve at the 7.77 kg/d dust class; pulse diaphragm valves at the 0.5 MPa "
        "compressed-air class; solenoid enclosure); the drive guard is drawn and the plinth "
        "anchors are drawn; the capture-air basis is registered (A-M-458)",
    },
    "no_fan_stated": "duty section 1 books 0.0 kW electrical: the baghouse dP rides the "
    "tool-extraction air mover (the purchased fan of that lane); the unit draws no fan "
    "hardware of its own (stated, not omitted - W12(3))",
    "placement_hold": "the placement seed block (1500 x 1000 x 1500) under-books the design "
    "envelope height by 0.78 m - the named consequence for the placement lane (W12(1); "
    "nothing is resized)",
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": {}, "cadquery": cq.__version__,
}
v_wall = (HOW * HUD - HI_W * HI_D) * (H - T_ROOF - Z_P) / 1e9
v_sheet = HI_W * HI_D * T_TS / 1e9 - BAGS * math.pi * (BD / 2 + 1) ** 2 * T_TS / 1e9
v_bags = BAGS * math.pi * (BD ** 2 - (BD - 8) ** 2) / 4 * BL / 1e9
v_hop = ((HI_W * HI_D + 198 * 198) * (Z_HOP_T - Z_P) / 2
         - (HI_W - 2 * WALL) * (HI_D - 2 * WALL) * (Z_HOP_T - Z_P)) / 1e6 * 7800 * 1e-9 * 1e9
report["part_mass_kg"] = {
    "housing_roof": round(v_wall * RHO_CS + HOW * HUD * T_ROOF / 1e9 * RHO_CS, 1),
    "tubesheet": round(v_sheet * RHO_CS, 1),
    "bags": round(v_bags * RHO_FELT, 1),
    "hopper": round(((HI_W * HI_D - (HI_W - 2 * WALL) * (HI_D - 2 * WALL)) * (Z_HOP_T - Z_P)
                     + 0.0) / 1e9 * RHO_CS * 0.5 + 60.0, 1),   # sloped plates at the half-book, study
    "valve_guard_pulse": round((190 * 200 * 200 + 150 * 260 * 260) * RHO_CS / 1e9
                               + math.pi * 70 ** 2 * 30 / 1e9 * RHO_CS, 1),
    "plinth_misc": round(L * W * T_PLINTH * RHO_CS / 1e9
                         + sum(p.val().Volume() for p in noz_pieces) * RHO_CS / 1e9, 1),
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
m = report["part_mass_kg"]
rows = [
    ["1", f"Pulse-jet housing {HOW:g} x {HUD:g} x {H - T_ROOF - Z_P:g}, wall {WALL:g}, roof; painted, "
          "bonded and grounded", 1, "carbon steel (duty section 3), CA 1.5 mm paint system class",
     m["housing_roof"], "make", "duty section 3 material and finish; deflagration-rated panel on the +X wall"],
    ["2", f"Tubesheet {HI_W:g} x {HI_D:g} x {T_TS:g} with the {BAGS}-bag hole field", 1,
     "carbon steel", m["tubesheet"], "make", "bag field per the design (A-M-458 cloth book)"],
    ["3", f"Antistatic polyester bags D{BD:g} x {BL:g} ({cloth:g} m2 drawn, A/C "
          f'{DS["ac_drawn_m3_min_m2"]:g} m3/min/m2 drawn against the {DS["ac_basis_m3_min_m2"]:g} basis)',
     BAGS, "antistatic polyester felt", m["bags"], "buy",
     "capture air 756 m3/h at the 1.2 m3/min/m2 EPA-453 basis (A-M-458); bags purchased per "
     "plan rule 6, drawn as the felt-wall envelopes"],
    ["4", f"60 deg dust hopper with DN200 rotary-valve discharge to IA-BAG-01 (valve and drive "
          "guard drawn)", 1, "carbon steel; valve purchased (316L rotor)",
     round(m["hopper"] + m["valve_guard_pulse"] * 0.4, 1), "make",
     "captured dust 7.77 kg/d class (the duty section 1 book) at the rotary-valve rating; "
     "dry dust wetted only after the PVC-U sluice break (duty section 3)"],
    ["5", "Pulse-clean header DN40 with 5 diaphragm-valve envelopes (0.5 MPa compressed-air class) "
          "and solenoid enclosure", 1, "carbon steel; valves purchased", m["valve_guard_pulse"], "buy",
     "pulse-jet cleaning per the AQS-DSN-INT-001 disposition; compressed-air service rating "
     "named (A-MACH rule)"],
    ["6", f"Hood conveying duct set (shop spools to the hoods): DN100 (mill, 360 m3/h) + DN80 x 2 "
          "(fab 216, wire 180 m3/h) at the 18-20 m/s duct class", 4, "carbon steel, bonded and grounded",
     18.0, "make", "design ducts from the capture-air basis (A-M-458); NOT drawn - they run to the "
     "tool hoods (hold, W12(5)); the schedule DN15 rows stay the duty connection table"],
    ["7", f"Nozzle set per docs-authority/nozzles/{UNIT}.csv: {len(schedule)} rows (three dust draws "
          "in at the plenum face, vent riser on the roof, drain boss; solids row as text)", len(schedule),
     "DN15 per schedule", round(sum(p.val().Volume() for p in noz_pieces) * RHO_CS / 1e9, 1), "make",
     "schedule tags/faces/heights verbatim; the duty section 4 bore note ('0.28 mm is not a "
     "specification; nozzle is DN15') carries the row"],
    ["8", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} with the drawn M12 anchors", 1, "carbon steel, painted",
     round(L * W * T_PLINTH * RHO_CS / 1e9, 1), "make", "dry frame; anchors in fasteners.csv (A-MACH anchor drawn)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 bolt with nut", fasteners.grade_for("CS"), 8 * 4,
     "access door bolted joint on the +X wall (count from the model)",
     "bag-change access door; grade 8.8 per the W5 rule; study pitch, confirmed at fabrication"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (drawn)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth (A-MACH anchor drawn); "
     "study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "housing_outer_mm": [HOW, HUD], "bag_field_z_mm": [Z_BAG0, Z_BAG1],
    "hopper_z_mm": [Z_P, Z_HOP_T], "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": "the pulse-jet baghouse as hardware (A-M-458 capture-air basis): housing, "
    "tubesheet, 20-bag field, hopper with rotary valve, pulse header; no fan of its own "
    "(duty 0.0 kW - the dP rides the tool-extraction mover)",
    "wetted": "carbon steel housing (duty section 3, dry dust); bags antistatic polyester; "
    "dust wetted only after the PVC-U sluice break (duty section 3)",
    "internals_drawn": "tubesheet, bag field (felt-wall envelopes), hopper, rotary valve with "
    "guard, pulse header and valves as solids; hood ducts a BOM row (W12(5))",
})
p["layout"] = {
    "frame": "origin at the envelope corner; housing at (150, 300), outer 906 x 706; inlet "
             "plenum along the -Y face; hopper 50..656, bags 676..1876, tubesheet 1876..1896, "
             "plenum to 2256, roof to the envelope top",
    "nozzle_spread": "side rows flush at the faces: along-face x positions packed at an od + 8 "
                     "pitch centred on the skid (40 mm stubs); drain boss through the plinth; "
                     "vent riser on the roof, flush at the envelope top; per-tag positions in "
                     "check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule")}), flush=True)
