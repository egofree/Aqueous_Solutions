"""VAC_IND manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid.

Machine: vacuum induction skull-melt (ISM) furnace, N+1 diverse standby of IND_MELT
(duty section 2: standby-zero design-day rate, energized on the IND_MELT relining
outage, outage_d 2; A-M-282/A-M-283). A real machine drawn per the node design
block and duty section 3: 304L vacuum chamber (t6) with the ceramic-fibre insulation
package inside the vacuum boundary, water-cooled copper induction crucible (no
wetted-refractory interface), RF/ISM coil and leads, tilt-pour trunnions and lip,
and the PSU cabinet on the +X bay. The 2 kg design-case skull melt is drawn as a
process-inventory solid, not a BOM part. No measured rate is claimed anywhere.

Placement frame: x along 1000 mm, y along 1000 mm, z up, origin at the envelope
corner. The schedule carries inlet/outlet/bottom/top faces, so the compass
assignment is the registered layout choice (params.json layout block); heights,
bores and ratings are docs-authority/nozzles/VAC_IND.csv verbatim. Connection
hardware draws flush at the envelope faces: nothing protrudes (A-core 2).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials          # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])         # 1000 x 1000 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO = {k: materials.density(m) for k, m in (("chamber", "304"), ("fibre", None), ("coil", "Cu"),
                                            ("crucible", "Cu"), ("plinth_frame_psu", "CS"))}
RHO_FIBRE = 128.0                                  # ceramic-fibre board 128 kg/m3 (IND_MELT lining class)

T_WALL = 6.0                       # 304L vacuum chamber shell, study fab-page value (hold, W12)
FIBRE_T = 40.0                     # insulation package on the shell (duty section 3), study
CH_X, CH_Y = 660.0, 800.0          # chamber outer footprint
CH_Z0, CH_Z1 = 60.0, 1160.0        # chamber shell on the plinth; lid on top
T_LID = 40.0
T_PLINTH = 60.0
CRUC_D, CRUC_H = 120.0, 160.0      # water-cooled Cu crucible, 2 kg ISM design case
CRUC_WALL = 10.0                   # cooling-jacket wall
COIL_TURNS, COIL_OD, COIL_WALL = 8, 15.0, 2.5
CX, CY = CH_X / 2, CH_Y / 2        # crucible axis
BATH = 600.0                       # melt-row schedule datum


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)


def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)


def dn15():
    return dn.pipe_od("DN15") / 2, dn.pipe_od("DN15") / 2 - dn.pipe_wall("DN15", 40)


parts = {}

# ---------------------------------------------------------------- plinth + anchors
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth

# ---------------------------------------------------------------- vacuum chamber (304L t6)
shell = box(0, 0, CH_Z0, CH_X, CH_Y, CH_Z1 - CH_Z0).cut(
    box(T_WALL, T_WALL, CH_Z0 + T_WALL, CH_X - 2 * T_WALL, CH_Y - 2 * T_WALL,
        CH_Z1 - CH_Z0 - 2 * T_WALL))
shell = shell.cut(rod(45.0, (CX, CY, -5.0), "Z", T_PLINTH + 10.0))          # drain pass through the floor
shell = shell.cut(rod(35.0, (CX, CY, CH_Z1 + T_LID - 5.0), "Z", T_LID + 10.0))   # vent pass in the lid
shell = shell.cut(rod(dn15()[0] + 1.0, (240.0, -5.0, 160.0), "Y", T_WALL + 10.0))   # N2 charge port
for sx in (240.0, 420.0):
    shell = shell.cut(rod(dn15()[0] + 1.0, (sx, CH_Y - T_WALL - 5.0, BATH), "Y", T_WALL + 10.0))
shell = shell.cut(rod(12.5, (CH_X - T_WALL - 1.0, CY, 300.0), "X", T_WALL + 14.0))   # coil-lead pass, full through-cut
parts["chamber_shell"] = shell
lid = box(0, 0, CH_Z1, CH_X, CH_Y, T_LID)
lid = lid.cut(rod(35.0, (CX, CY, CH_Z1 - 5.0), "Z", T_LID + 10.0))
parts["chamber_lid"] = lid

# ---------------------------------------------------------------- insulation package (fibre, inside the vacuum boundary)
fibre = box(T_WALL, T_WALL, CH_Z0 + T_WALL, CH_X - 2 * T_WALL, CH_Y - 2 * T_WALL,
            CH_Z1 - CH_Z0 - 2 * T_WALL).cut(
    box(T_WALL + FIBRE_T, T_WALL + FIBRE_T, CH_Z0 + T_WALL + FIBRE_T,
        CH_X - 2 * (T_WALL + FIBRE_T), CH_Y - 2 * (T_WALL + FIBRE_T),
        CH_Z1 - CH_Z0 - 2 * (T_WALL + FIBRE_T) - 60.0))
parts["fibre_lining"] = fibre

# ---------------------------------------------------------------- water-cooled Cu crucible + ISM coil
parts["crucible_jacket"] = tube(CRUC_D / 2, CRUC_D / 2 - CRUC_WALL, (CX, CY, 200.0), "Z", CRUC_H)
coil = None
for i in range(COIL_TURNS):
    t = tube(COIL_OD / 2, COIL_OD / 2 - COIL_WALL, (CX, CY, 180.0 + i * 26.0), "Z", 16.0)
    coil = t if coil is None else coil.union(t)
parts["ism_coil"] = coil
# the lead exits through the insulation package to the PSU bay (fused at the fibre pass;
# a 5 mm study clearance keeps it off the crucible jacket tangent)
parts["coil_leads"] = rod(COIL_OD / 2, (CX + 65.0, CY, 300.0), "X", L - (CX + 65.0) - 320.0)

# ---------------------------------------------------------------- pour hardware (tilt, trunnions, lip)
parts["pour_lip"] = box(CX - 60.0, CH_Y - 20.0, BATH - 60.0, 120.0, 40.0, 70.0)
parts["trunnion_pins"] = rod(30.0, (CX, 0.0, 500.0), "Y", 40.0).union(
    rod(30.0, (CX, CH_Y - 40.0, 500.0), "Y", 40.0))

# ---------------------------------------------------------------- PSU cabinet (+X bay) + tilt hydraulics
parts["psu_cabinet"] = box(CH_X, 0, 0, L - CH_X, 500.0, 1400.0).cut(
    box(CH_X + 8.0, 8.0, 8.0, L - CH_X - 16.0, 484.0, 1384.0))
parts["tilt_frame"] = box(CH_X, 500.0, 0, L - CH_X, W - 500.0, 500.0)

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the envelope faces)
r15, w15 = dn15()
noz = {}
noz["N1_melt_stub"] = tube(r15, w15, (240.0, CH_Y - T_WALL, BATH), "Y", W - (CH_Y - T_WALL))
noz["N3_investment_stub"] = tube(r15, w15, (420.0, CH_Y - T_WALL, BATH), "Y", W - (CH_Y - T_WALL))
noz["N2_charge_port"] = tube(r15, w15, (240.0, 0.0, 160.0), "Y", T_WALL + 40.0)
noz["N4_drain"] = tube(30.5, r15, (CX, CY, 0.0), "Z", CH_Z0)
noz["N5_vent_riser"] = tube(r15, w15, (CX, CY, CH_Z1 + T_LID - 6.0), "Z", H - (CH_Z1 + T_LID - 6.0))
for k, v in noz.items():
    parts[k] = v

# ---------------------------------------------------------------- process inventory (not a BOM part)
inv = {"skull_melt_inventory": rod(CRUC_D / 2 - CRUC_WALL - 2.0, (CX, CY, 210.0), "Z", CRUC_H - 20.0)}

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
    "plinth": vol["plinth"] * RHO["plinth_frame_psu"] / 1e9,
    "chamber_shell": vol["chamber_shell"] * RHO["chamber"] / 1e9,
    "chamber_lid": vol["chamber_lid"] * RHO["chamber"] / 1e9,
    "fibre_lining": vol["fibre_lining"] * RHO_FIBRE / 1e9,
    "crucible_jacket": vol["crucible_jacket"] * RHO["crucible"] / 1e9,
    "ism_coil": (vol["ism_coil"] + vol["coil_leads"]) * RHO["coil"] / 1e9,
    "pour_hardware": (vol["pour_lip"] + vol["trunnion_pins"]) * RHO["plinth_frame_psu"] / 1e9,
    "psu_cabinet": vol["psu_cabinet"] * RHO["plinth_frame_psu"] / 1e9,
    "tilt_frame": vol["tilt_frame"] * RHO["plinth_frame_psu"] / 1e9,
    "nozzles": sum(vol[k] for k in noz) * RHO["plinth_frame_psu"] / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
schedule = [r for r in P["nozzles"]]
drawn = {}
for r in schedule:
    tag = r["tag"]
    style = "tube"
    note = "atmospheric open-bore DN15 tube, flush at the envelope face (duty section 4)"
    if r["size"] == "solids":
        note += "; solids row drawn at DN15, bore not calculated (W4 rule)"
    if r["face"] == "top":
        note += "; schedule datum 800 is the placeholder elevation - the riser stands on the chamber lid and flushes at the envelope top (hold, WORK_ORDER W12)"
    if r["face"] == "bottom":
        note += "; flush at the envelope bottom (schedule datum 50)"
    drawn[tag] = {"style": style, "dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": BATH, "N3": BATH, "N2": 160.0, "N4": 0.0, "N5": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 melt class N+1 rated envelope (A-M-282): real machine, "
    "standby-zero design-day rate",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "chamber": {"od_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + T_LID],
                    "wall_mm": T_WALL, "wall_basis": "study fab-page 304L t6 vacuum shell "
                    "(no thickness booked on the node - hold, WORK_ORDER W12)"},
        "crucible": {"od_mm": CRUC_D, "h_mm": CRUC_H, "wall_mm": CRUC_WALL,
                     "basis": "water-cooled copper induction crucible, no wetted-refractory "
                     "interface (duty section 3); the 2 kg ISM design case (node design "
                     "design_case_kg) sets the size class"},
        "coil": {"turns": COIL_TURNS, "tube_od_mm": COIL_OD,
                 "basis": "ISM through-coil; the duty section 2 connected_kW "
                 f"{DS.get('connected_kW')} is the node rating"},
        "psu": {"bay": "x 660..1000, 15 kW connected (node design); purchased cabinet "
                "drawn as its envelope per plan rule 6"}},
    "standby": {"state": "standby_rated N+1 diverse of IND_MELT (A-M-282/A-M-283); "
                "energized only on the IND_MELT relining/repair outage "
                f"(outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study; the machine is designed per the node "
                "design block so the alternate is real, not a placeholder"},
    "material": {"class": "304L vacuum chamber + water-cooled Cu crucible, ceramic-fibre "
                 "insulation on the shell",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22): the water-cooled copper face keeps the "
                 "Ti melt out of contact with any refractory; 304L chamber; CA 0 mm "
                 "(AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore DN15 tube connections flush at the envelope "
    "faces (duty section 4: hose, atmospheric); the schedule inlet/outlet/bottom/top faces "
    "are mapped to compass faces by the registered layout (params.json layout block); the "
    "solids row is drawn at DN15 labeled bore not calculated (W4 rule); the schedule rating "
    "column (Class 150) is carried verbatim as text; datums are the schedule placeholders "
    "(holds, WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry furnace-shop service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Vacuum chamber 304L t6, {CH_X:g} x {CH_Y:g} x {CH_Z1 - CH_Z0:g}, lid t{T_LID:g}, "
          "with drain/vent/charge/pour passes", 1, "304L plate", 
     round(mass["chamber_shell"] + mass["chamber_lid"], 1), "make",
     "duty section 3: 304L vacuum chamber (X-MAT-22); wall is the study fab-page value "
     "(hold, WORK_ORDER W12); standby_rated N+1 of IND_MELT (A-M-282)"],
    ["3", f"Ceramic-fibre insulation package t{FIBRE_T:g} inside the vacuum boundary", 1,
     "ceramic-fibre board 128 kg/m3", mass["fibre_lining"], "make",
     "duty section 3: ceramic-fibre insulation on the shell"],
    ["4", f"Water-cooled Cu crucible OD {CRUC_D:g} x {CRUC_H:g}, jacket wall {CRUC_WALL:g} "
          f"(the {DS.get('design_case_kg')} kg ISM design case)", 1, "copper, water-cooled",
     mass["crucible_jacket"], "make",
     "duty section 3: no wetted-refractory interface (CRC_TI 1668 C class); cooling-water "
     "circuit is loop hardware, not modeled (WORK_ORDER W12)"],
    ["5", f"ISM induction coil, {COIL_TURNS} turns x OD {COIL_OD:g} Cu, with leads", 1,
     "Cu ETP tube", mass["ism_coil"], "make",
     "duty section 2: the node connected_kW is the rating; coil water interlock is a "
     "unit-task item"],
    ["6", "Tilt-pour lip and trunnion pins", 1, "carbon steel", mass["pour_hardware"], "make",
     "tilt pour to the +Y melt rows at z 600; study geometry (WORK_ORDER W12)"],
    ["7", f"PSU cabinet, {DS.get('connected_kW')} kW connected (node design), IP54", 1,
     "purchased cabinet (envelope)", mass["psu_cabinet"], "buy",
     "purchased per plan rule 6; the maker rating reads the sheet at order; standby unit, "
     "energized only on the IND_MELT outage (A-M-282)"],
    ["8", "Tilt-frame hydraulics bay on the +X floor", 1, "carbon steel", mass["tilt_frame"], "make",
     "WORK_ORDER W10 route; actuator package purchased at fabrication (WORK_ORDER W12)"],
    ["9", "Nozzle set per docs-authority/nozzles/VAC_IND.csv: 5 atmospheric open-bore "
          "tube connections flush at the envelope faces (drain through the plinth, vent "
          "riser on the chamber lid)", len(schedule), "304L tube", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; solids row at DN15, bore not calculated (W4)"],
]
import csv  # noqa: E402
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per rail (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at fabrication"],
    [None, "M10 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("304"), 12,
     "chamber lid clamp and PSU cabinet rails",
     "grade rule W5: A4-70 on the 304L joint; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 melt class N+1 rated envelope (A-M-282); real machine, standby-zero "
             "design-day rate",
    "chamber": {"xy_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + T_LID], "wall_mm": T_WALL},
    "psu_bay": {"x_mm": [CH_X, L]},
}
p["design"] = {
    "machine": "vacuum induction skull-melt (ISM) furnace, N+1 diverse standby of IND_MELT "
               "(node design service)",
    "mat": "304L vacuum chamber + water-cooled Cu crucible, ceramic-fibre insulation "
           "(duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_WALL, "wall_basis": "study fab-page 304L t6 vacuum shell (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none); the 2 kg design-case skull melt is "
                 "a process-inventory solid, not a BOM part",
    "purchased": f"PSU cabinet {DS.get('connected_kW')} kW connected, drawn as its envelope "
                 "(plan rule 6); actuator package at fabrication",
}
p["layout"] = {
    "frame": "origin at the envelope corner; chamber on the plinth x 0..660, y 0..800, "
             "z 60..1200; PSU bay x 660..1000; tilt hydraulics floor bay; crucible axis at "
             "the chamber centre",
    "nozzle_spread": "the schedule gives inlet/outlet/bottom/top and heights only; +Y melt "
                     "stubs at x 240/420 flush at the envelope face; -Y charge port at "
                     "x 240; drain under the crucible axis; vent riser on the chamber lid "
                     "to the envelope top; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
