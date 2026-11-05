"""SINTER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Machine: Ti/Mo/Cr powder sinter furnace, N+1 consolidation standby of ROLL (node
design: press-and-sinter P/M route at the 0.5 kg/d powder class, design_case_kg_d
0.5, T_C 1300, connected_kW 8, outage_d 2 on a roll-stand outage; A-M-282/A-M-283).
A real machine drawn per the node material row and duty section 3 (ASM_V7
reactive-powder class): graphite resistance elements around a 95 % alumina muffle
under inert/vacuum atmosphere, on a water-cooled nickel-free steel jacket - the
jacket is a double wall with a cooling-water annulus (the water circuit is loop
hardware, not modeled), ceramic-fibre board between the jacket and the hot zone
(study construction), alumina hearth, front charge door, and the 8 kW controls
cabinet as a purchased envelope on the +X bay per plan rule 6. The powder charge
is drawn as a process-inventory solid, not a BOM part. No measured rate anywhere.

Placement frame: x along 1000 mm, y along 1000 mm, z up, origin at the envelope
corner. The 3 schedule rows of docs-authority/nozzles/SINTER.csv draw flush at
the envelope faces. Standby named in the WORK_ORDER header, the BOM rows and the
build log.
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials          # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("SINTER")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])         # 1000 x 1000 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_GRAPHITE = materials.density("graphite")
RHO_ALUMINA = 3700.0               # 95 % alumina muffle class, study value (hold, W12)
RHO_FIBRE = 128.0                  # ceramic-fibre board 128 kg/m3 (IND_MELT lining class)

T_WALL = 4.0                       # jacket walls (outer + inner), study fab-page value (hold, W12)
GAP_W = 15.0                       # cooling-water annulus between the jacket walls (loop hardware, W12)
T_FIBRE = 100.0                    # fibre board between jacket and hot zone, study (hold, W12)
JX, JY = 660.0, 1000.0             # jacket footprint
JZ0, JZ1 = 60.0, 1160.0            # jacket on the plinth
T_PLINTH = 60.0
CX, CY = JX / 2, JY / 2
MUF_OD, MUF_ID, MUF_H = 260.0, 220.0, 480.0   # 95 % alumina muffle (duty section 3)
DN15 = dn.pipe_od("DN15") / 2
DN15W = DN15 - dn.pipe_wall("DN15", 40)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)


def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- water-cooled steel jacket (double wall)
w0, w1 = T_WALL, T_WALL + GAP_W                    # outer wall 0..4; water gap 4..19; inner wall 19..23
casing_outer = box(0, 0, JZ0, JX, JY, JZ1 - JZ0).cut(
    box(w0, w0, JZ0 + w0, JX - 2 * w0, JY - 2 * w0, JZ1 - JZ0 - 2 * w0))
casing_outer = casing_outer.cut(rod(32.0, (CX, CY, JZ0 - 5.0), "Z", T_PLINTH + 14.0))   # N2 drain pass
casing_outer = casing_outer.cut(rod(DN15 + 1.0, (CX, CY, JZ1 - 5.0), "Z", 20.0))        # N3 vent pass
casing_outer = casing_outer.cut(box(-5.0, 350.0, 60.0, 10.0, 300.0, 500.0))             # charge door opening
parts["jacket_outer"] = casing_outer
jacket_inner = box(w1, w1, JZ0 + w0, JX - 2 * w1, JY - 2 * w1, JZ1 - JZ0 - 2 * w0).cut(
    box(w1 + T_WALL, w1 + T_WALL, JZ0 + w0 + T_WALL, JX - 2 * (w1 + T_WALL),
        JY - 2 * (w1 + T_WALL), JZ1 - JZ0 - 2 * w0 - 2 * T_WALL))
jacket_inner = jacket_inner.cut(rod(32.0, (CX, CY, JZ0 - 5.0), "Z", T_PLINTH + 24.0))   # N2 drain pass
jacket_inner = jacket_inner.cut(rod(DN15 + 1.0, (CX, CY, JZ1 - 5.0), "Z", 24.0))        # N3 vent pass
jacket_inner = jacket_inner.cut(box(-5.0, 350.0, 60.0, w1 + 6.0, 300.0, 500.0))         # door opening
parts["jacket_inner"] = jacket_inner

# ---------------------------------------------------------------- charge door face (-X, flush)
parts["door_face"] = box(0.0, 340.0, JZ0 + w0, 50.0, 320.0, 500.0)
for dz in (140.0, 300.0):
    parts["door_face"] = parts["door_face"].union(box(0.0, 350.0, JZ0 + w0 + dz, 50.0, 300.0, 16.0))

# ---------------------------------------------------------------- ceramic-fibre board between jacket and hot zone
fibre = box(w1 + T_WALL, w1 + T_WALL, JZ0 + w0 + T_WALL, JX - 2 * (w1 + T_WALL),
            JY - 2 * (w1 + T_WALL), JZ1 - JZ0 - 2 * w0 - 2 * T_WALL).cut(
    box(w1 + T_WALL + T_FIBRE, w1 + T_WALL + T_FIBRE, JZ0 + w0 + T_WALL + T_FIBRE,
        JX - 2 * (w1 + T_WALL + T_FIBRE), JY - 2 * (w1 + T_WALL + T_FIBRE),
        JZ1 - JZ0 - 2 * w0 - 2 * T_WALL - T_FIBRE))
fibre = fibre.cut(box(-5.0, 350.0, 60.0, w1 + T_WALL + T_FIBRE + 2.0, 300.0, 500.0))    # door throat
parts["fibre_lining"] = fibre

# ---------------------------------------------------------------- alumina hearth + 95 % alumina muffle
parts["hearth_plate"] = box(150.0, 150.0, JZ0 + w0 + T_WALL + T_FIBRE,
                            JX - 300.0, JY - 300.0, 30.0)
parts["muffle"] = tube(MUF_OD / 2, MUF_ID / 2, (CX, CY, JZ0 + w0 + T_WALL + T_FIBRE + 30.0), "Z", MUF_H)
parts["muffle_lid"] = tube(MUF_OD / 2 + 10.0, MUF_ID / 2,
                           (CX, CY, JZ0 + w0 + T_WALL + T_FIBRE + 30.0 + MUF_H), "Z", 20.0)

# ---------------------------------------------------------------- graphite resistance elements (wall racks + crown)
elements = None
for ex in (170.0, 490.0):
    for zz in (280.0, 420.0, 560.0, 700.0, 840.0):
        e = rod(12.0, (ex, 210.0, zz), "Y", 580.0)
        elements = e if elements is None else elements.union(e)
for ey in (330.0, 500.0, 670.0):
    e = rod(12.0, (CX - 180.0, ey, 1040.0), "X", 360.0)   # crown elements
    elements = elements.union(e) if elements is not None else e
parts["element_racks"] = elements

# ---------------------------------------------------------------- controls cabinet (+X bay, purchased envelope)
parts["controls_cabinet"] = box(JX, 0, 0, L - JX, 500.0, H).cut(
    box(JX + 8.0, 8.0, 8.0, L - JX - 16.0, 484.0, H - 16.0))

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the faces)
noz = {}
noz["N1_stock_chute"] = box(L - 40.0, CY - 60.0, 550.0, 40.0, 120.0, 100.0)   # N1 +X z 600, flush at the face
noz["N2_drain"] = tube(30.5, DN15, (CX, CY, 0.0), "Z", JZ0 + 8.0)             # through the plinth, flush at the bottom
noz["N3_vent_riser"] = tube(DN15, DN15W, (CX, CY, JZ1 - 6.0), "Z", H - (JZ1 - 6.0))   # to the envelope top
for k, v in noz.items():
    parts[k] = v

# ---------------------------------------------------------------- process inventory (not a BOM part)
inv = {"sinter_charge_inventory": rod(70.0, (CX, CY, JZ0 + w0 + T_WALL + T_FIBRE + 40.0), "Z", 60.0)}

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid_val = solid.val()
solid_val.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid_val.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                                 tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
valid = all(v.val().isValid() for v in list(parts.values()) + list(inv.values()))
vol = {k: v.val().Volume() for k, v in parts.items()}
mass = {
    "plinth": vol["plinth"] * RHO_CS / 1e9,
    "jacket_outer": vol["jacket_outer"] * RHO_CS / 1e9,
    "jacket_inner": vol["jacket_inner"] * RHO_CS / 1e9,
    "door_face": vol["door_face"] * RHO_CS / 1e9,
    "fibre_lining": vol["fibre_lining"] * RHO_FIBRE / 1e9,
    "hearth_plate": vol["hearth_plate"] * RHO_ALUMINA / 1e9,
    "muffle": (vol["muffle"] + vol["muffle_lid"]) * RHO_ALUMINA / 1e9,
    "element_racks": vol["element_racks"] * RHO_GRAPHITE / 1e9,
    "controls_cabinet": vol["controls_cabinet"] * RHO_CS / 1e9,
    "nozzles": sum(vol[k] for k in noz) * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
schedule = [r for r in P["nozzles"]]
drawn = {}
for r in schedule:
    tag = r["tag"]
    note = "flush at the envelope face (duty section 4)"
    if r["size"] == "solids":
        note += "; solids row drawn as an outlet chute, bore not calculated (W4 rule)"
    if r["face"] == "top":
        note += "; schedule datum 800 is the placeholder elevation - the riser stands on the jacket roof and flushes at the envelope top (hold, WORK_ORDER W12)"
    if r["face"] == "bottom":
        note += "; through the plinth, flush at the envelope bottom (schedule datum 50)"
    drawn[tag] = {"dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": 600.0, "N2": 0.0, "N3": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 melt class N+1 rated envelope (A-M-282): real machine, "
    "standby-zero design-day rate",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "jacket": {"od_mm": [JX, JY], "z_mm": [JZ0, JZ1], "wall_mm": T_WALL,
                   "water_gap_mm": GAP_W,
                   "basis": "water-cooled nickel-free steel jacket (duty section 3): double "
                   "wall with the cooling-water annulus; the water circuit is loop hardware, "
                   "not modeled (hold, WORK_ORDER W12); wall is the study fab-page value "
                   "(hold, WORK_ORDER W12)"},
        "muffle": {"od_mm": MUF_OD, "id_mm": MUF_ID, "h_mm": MUF_H,
                   "basis": "95 % alumina muffle under inert/vacuum atmosphere (duty section "
                   "3, ASM_V7 reactive-powder class); buy consumable, change-out per campaign"},
        "elements": {"material": "graphite, OD 24 rods in wall and crown racks",
                     "basis": f"duty section 3 element class at T_C {DS.get('T_C')} C (node "
                     "design); connected_kW "
                     f"{DS.get('connected_kW')} is the node rating; Mo elements are the duty "
                     "alternative for an air variant (not drawn)"},
        "cabinet": {"bay": "x 660..1000, 8 kW connected (node design); purchased cabinet "
                    "drawn as its envelope per plan rule 6"}},
    "standby": {"state": "standby_rated N+1 consolidation of ROLL (A-M-282/A-M-283); "
                "energized on the roll-stand outage "
                f"(outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study; the machine is designed per the node "
                "design block so the alternate is real, not a placeholder"},
    "material": {"class": "water-cooled CS jacket, ceramic-fibre board, 95 % alumina muffle "
                 "and hearth, graphite elements",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22): nickel-free hot zone; Ti embrittles in "
                 "air/N2 (CRC_TI); CA 0 mm - dry furnace service (AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "the 3 schedule rows draw flush at the envelope faces (duty section 4); "
    "the solids row (N1 sintered stock) is drawn as an outlet chute labeled bore not "
    "calculated (W4 rule); the schedule rating column (Class 150) is carried verbatim as "
    "text; datums are the schedule placeholders (holds, WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry furnace-shop service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Water-cooled steel jacket, double wall t{T_WALL:g} with the {GAP_W:g} mm cooling-water "
           f"annulus, {JX:g} x {JY:g} x {JZ1 - JZ0:g}, with charge door", 1, "carbon steel (nickel-free)",
     round(mass["jacket_outer"] + mass["jacket_inner"] + mass["door_face"], 1), "make",
     "duty section 3: nickel-free hot zone on a water-cooled steel jacket; wall is the study "
     "fab-page value (hold, WORK_ORDER W12); the water circuit is loop hardware, not modeled "
     "(hold, WORK_ORDER W12); standby_rated N+1 of ROLL (A-M-282)"],
    ["3", f"Ceramic-fibre board between jacket and hot zone, t{T_FIBRE:g}", 1,
     "ceramic-fibre board 128 kg/m3", mass["fibre_lining"], "make",
     "study furnace construction (IND_MELT lining class; SCHACHT2004); thickness is the study "
     "value (hold, WORK_ORDER W12)"],
    ["4", f"95 % alumina muffle OD {MUF_OD:g} x {MUF_H:g} with lid and alumina hearth "
           "(inert/vacuum chamber)", 1, "95 % alumina (consumable set)", mass["muffle"] + mass["hearth_plate"], "buy",
     "duty section 3 muffle class (ASM_V7 reactive-powder sinter); change-out per campaign "
     "(hold, WORK_ORDER W12)"],
    ["5", f"Graphite resistance elements, OD 24, wall and crown racks "
     f"({DS.get('connected_kW')} kW connected, T_C {DS.get('T_C')} node design)", 13,
     "graphite (consumable set)", mass["element_racks"], "buy",
     "duty section 3 element class at 1300 C; element change-out is the consumable cycle "
     "(A-M-282); Mo elements are the air-variant alternative (not drawn)"],
    ["6", f"Controls cabinet, {DS.get('connected_kW')} kW connected (node design), IP54", 1,
     "purchased cabinet (envelope)", mass["controls_cabinet"], "buy",
     "purchased per plan rule 6; standby unit, energized only on the roll-stand outage "
     "(A-M-282); vacuum/inert atmosphere package purchased at fabrication (WORK_ORDER W12)"],
    ["7", "Nozzle set per docs-authority/nozzles/SINTER.csv: stock chute (solids, bore not "
           "calculated), drain and vent riser, flush at the envelope faces", len(schedule),
     "carbon steel tube", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; N1 solids row bore not calculated (W4)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per rail (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at fabrication"],
    [None, "M10 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("CS"), 12,
     "door face hinge and muffle lid clamp",
     "grade rule W5: 8.8 on the carbon-steel joints; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 melt class N+1 rated envelope (A-M-282); real machine, standby-zero "
             "design-day rate",
    "jacket": {"xy_mm": [JX, JY], "z_mm": [JZ0, JZ1], "wall_mm": T_WALL, "water_gap_mm": GAP_W},
    "cabinet_bay": {"x_mm": [JX, L]},
}
p["design"] = {
    "machine": "Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL (node design service)",
    "mat": "water-cooled nickel-free steel jacket, ceramic-fibre board, 95 % alumina muffle, "
           "graphite resistance elements (duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_WALL, "wall_basis": "study fab-page jacket wall (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none); the alumina muffle and hearth are "
                 "furnace furniture (buy consumables), not internals; the powder charge is a "
                 "process-inventory solid",
    "purchased": f"controls cabinet {DS.get('connected_kW')} kW connected (node design), drawn "
                 "as its envelope (plan rule 6); alumina muffle set and graphite element set "
                 "are purchased consumables (buy rows); vacuum/inert atmosphere package at "
                 "fabrication",
}
p["layout"] = {
    "frame": "origin at the envelope corner; jacket on the plinth x 0..660, y 0..1000, "
             "z 60..1160; charge door face -X; muffle on the hearth at the jacket centre; "
             "controls bay x 660..1000",
    "nozzle_spread": "the 3 schedule rows draw flush at the envelope faces: N1 stock chute +X "
                     "at z 600; N2 drain through the plinth; N3 vent riser on the jacket roof "
                     "to the envelope top; per-tag notes in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
