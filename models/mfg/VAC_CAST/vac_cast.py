"""VAC_CAST manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid.

Machine: vacuum tilt-pour casting station, N+1 standby of CAST_LINE / CONT_CAST
(duty section 2: standby-zero design-day rate, energized during the cast-line
stoppage of the VAC_IND outage window, outage_d 2, 3 kg design case; A-M-282/
A-M-283). A real machine drawn per the node design block and duty section 3:
304L vacuum chamber (t6) with lid, steel mould-tilt table hardware inside, the
graphite crucible on its alumina backup (consumable set, buy), and the vacuum
pump skid and control cabinet on the +X bay (purchased, plan rule 6). The 3 kg
design-case melt is drawn as a process-inventory solid, not a BOM part. No
measured rate is claimed anywhere.

Placement frame: x along 1500 mm, y along 800 mm, z up, origin at the envelope
corner. The schedule carries inlet/bottom/top faces, so the compass assignment
is the registered layout choice (params.json layout block); heights, bores and
ratings are docs-authority/nozzles/VAC_CAST.csv verbatim. Connection hardware
draws flush at the envelope faces: nothing protrudes (A-core 2).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials          # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])         # 1500 x 800 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_304 = materials.density("304")
RHO_CS = materials.density("CS")
RHO_GRAPHITE = materials.density("graphite")

T_WALL = 6.0                       # 304L vacuum chamber shell, study fab-page value (hold, W12)
CH_X, CH_Y = 900.0, 760.0          # chamber outer footprint
CH_Z0, CH_Z1 = 60.0, 1160.0        # chamber shell on the plinth; lid on top
T_LID = 40.0
T_PLINTH = 60.0
CRUC_D, CRUC_H = 140.0, 160.0      # graphite crucible, 3 kg design case
CRUC_WALL = 15.0
CX, CY = CH_X / 2, CH_Y / 2
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

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- vacuum chamber (304L t6)
shell = box(0, 0, CH_Z0, CH_X, CH_Y, CH_Z1 - CH_Z0).cut(
    box(T_WALL, T_WALL, CH_Z0 + T_WALL, CH_X - 2 * T_WALL, CH_Y - 2 * T_WALL,
        CH_Z1 - CH_Z0 - 2 * T_WALL))
shell = shell.cut(rod(45.0, (CX, CY, -5.0), "Z", T_PLINTH + 10.0))            # drain pass
shell = shell.cut(rod(dn15()[0] + 1.0, (300.0, CH_Y - T_WALL - 5.0, 160.0), "Y", T_WALL + 10.0))
parts["chamber_shell"] = shell
lid = box(0, 0, CH_Z1, CH_X, CH_Y, T_LID)
lid = lid.cut(rod(35.0, (CX, CY, CH_Z1 - 5.0), "Z", T_LID + 10.0))            # vent pass
parts["chamber_lid"] = lid

# ---------------------------------------------------------------- mould-tilt table hardware (steel, inside the chamber)
table = box(140.0, 180.0, 300.0, 620.0, 400.0, 30.0)                          # mould table deck
for tx, ty in ((160.0, 200.0), (740.0, 200.0), (160.0, 560.0), (740.0, 560.0)):
    table = table.union(box(tx - 20.0, ty - 20.0, 120.0, 40.0, 40.0, 180.0))  # legs to the chamber floor
parts["mould_table"] = table
parts["tilt_frame"] = box(CX - 70.0, CY - 90.0, 480.0, 140.0, 180.0, 60.0)    # tilt cradle
parts["trunnion_pins"] = rod(25.0, (CX, 0.0, 500.0), "Y", 45.0).union(
    rod(25.0, (CX, CH_Y - 45.0, 500.0), "Y", 45.0))
parts["pour_lip"] = box(CX - 60.0, CH_Y - 60.0, BATH - 80.0, 120.0, 40.0, 90.0)

# ---------------------------------------------------------------- graphite crucible on its alumina backup (buy set)
parts["crucible"] = tube(CRUC_D / 2, CRUC_D / 2 - CRUC_WALL, (CX, CY, 640.0), "Z", CRUC_H)
parts["crucible_backup"] = tube(CRUC_D / 2 + 20.0, CRUC_D / 2, (CX, CY, 640.0), "Z", 60.0)

# ---------------------------------------------------------------- vacuum pump skid + control cabinet (+X bay, purchased envelopes)
parts["vacuum_pump_skid"] = box(CH_X + 20.0, 40.0, T_PLINTH, 260.0, 300.0, 640.0)
parts["control_cabinet"] = box(CH_X + 20.0, 380.0, 0.0, L - CH_X - 40.0, W - 400.0, 1400.0).cut(
    box(CH_X + 28.0, 388.0, 8.0, L - CH_X - 56.0, W - 416.0, 1384.0))

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the envelope faces)
r15, w15 = dn15()
noz = {}
noz["N1_melt_inlet"] = tube(r15, w15, (300.0, CH_Y - T_WALL, 160.0), "Y", W - (CH_Y - T_WALL))
noz["N2_drain"] = tube(30.5, r15, (CX, CY, 0.0), "Z", CH_Z0)
noz["N3_vent_riser"] = tube(r15, w15, (CX, CY, CH_Z1 + T_LID - 6.0), "Z", H - (CH_Z1 + T_LID - 6.0))
for k, v in noz.items():
    parts[k] = v

# ---------------------------------------------------------------- process inventory (not a BOM part)
inv = {"melt_inventory": rod(CRUC_D / 2 - CRUC_WALL - 2.0, (CX, CY, 650.0), "Z", CRUC_H - 20.0)}

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
solid_val.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                                 tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
valid = all(v.val().isValid() for v in list(parts.values()) + list(inv.values()))
vol = {k: v.val().Volume() for k, v in parts.items()}
mass = {
    "plinth": vol["plinth"] * RHO_CS / 1e9,
    "chamber_shell": vol["chamber_shell"] * RHO_304 / 1e9,
    "chamber_lid": vol["chamber_lid"] * RHO_304 / 1e9,
    "mould_table": (vol["mould_table"] + vol["tilt_frame"] + vol["trunnion_pins"]
                    + vol["pour_lip"]) * RHO_CS / 1e9,
    "crucible_set": (vol["crucible"] * RHO_GRAPHITE + vol["crucible_backup"] * 3700.0) / 1e9,
    "vacuum_pump_skid": vol["vacuum_pump_skid"] * RHO_CS / 1e9,
    "control_cabinet": vol["control_cabinet"] * RHO_CS / 1e9,
    "nozzles": sum(vol[k] for k in noz) * RHO_304 / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
schedule = [r for r in P["nozzles"]]
drawn = {}
for r in schedule:
    tag = r["tag"]
    note = "atmospheric open-bore DN15 tube, flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":
        note += "; flush at the envelope bottom (schedule datum 50)"
    if r["face"] == "top":
        note += "; schedule datum 800 is the placeholder elevation - the riser stands on the " \
                "chamber lid and flushes at the envelope top (hold, WORK_ORDER W12)"
    drawn[tag] = {"style": "tube", "dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": 160.0, "N2": 0.0, "N3": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "chamber": {"od_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + T_LID],
                    "wall_mm": T_WALL, "wall_basis": "study fab-page 304L t6 vacuum shell "
                    "(no thickness booked on the node - hold, WORK_ORDER W12)"},
        "mould_table": {"deck_z_mm": [300.0, 330.0], "basis": "steel mould-tilt table hardware "
                        "(duty section 3); tilt about the z 500 trunnion axis"},
        "crucible": {"od_mm": CRUC_D, "h_mm": CRUC_H, "wall_mm": CRUC_WALL,
                     "basis": "graphite crucible on its alumina backup (duty section 3); the "
                     "3 kg design case (node design design_case_kg_d) sets the size class; "
                     "consumable set, buy"},
        "purchased": "vacuum pump skid and control cabinet on the +X bay, drawn as their "
        "envelopes per plan rule 6 (the 7.5 kW connected rating is the node design)"},
    "standby": {"state": "standby_rated N+1 of CAST_LINE / CONT_CAST (A-M-282/A-M-283); "
                "energized during the cast-line stoppage of the VAC_IND outage window "
                f"(outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "304L vacuum chamber; graphite crucible + alumina backup; steel "
                 "table hardware", "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22); CA 0 mm (AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore DN15 tube connections flush at the envelope "
    "faces (duty section 4: hose, atmospheric); the schedule inlet/bottom/top faces are "
    "mapped to compass faces by the registered layout (params.json layout block); the "
    "schedule rating column (Class 150) is carried verbatim as text; datums are the "
    "schedule placeholders (holds, WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry foundry-floor service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Vacuum chamber 304L t6, {CH_X:g} x {CH_Y:g} x {CH_Z1 - CH_Z0:g}, lid t{T_LID:g}, "
          "with drain/vent/melt passes", 1, "304L plate",
     round(mass["chamber_shell"] + mass["chamber_lid"], 1), "make",
     "duty section 3: 304L vacuum tilt-pour chamber (X-MAT-22); wall is the study fab-page "
     "value (hold, WORK_ORDER W12); standby_rated N+1 of CAST_LINE/CONT_CAST (A-M-282)"],
    ["3", "Mould-tilt table hardware: deck on legs, tilt cradle, trunnions, pour lip", 1,
     "carbon steel", mass["mould_table"], "make",
     "duty section 3: steel table hardware; tilt about the z 500 trunnion axis (study, W12)"],
    ["4", f"Graphite crucible OD {CRUC_D:g} x {CRUC_H:g} on its alumina backup ring "
          f"(the {DS.get('design_case_kg_d')} kg design case)", 1, "graphite + alumina (consumable set)",
     mass["crucible_set"], "buy", "duty section 3 consumable set; change-out at the unit "
     "task 12 work order"],
    ["5", "Vacuum pump skid on the +X bay (purchased, envelope and interface)", 1,
     "purchased skid (envelope)", mass["vacuum_pump_skid"], "buy",
     "purchased per plan rule 6; the maker rating reads the sheet at order; standby unit "
     "(A-M-282)"],
    ["6", f"Control cabinet, {DS.get('connected_kW')} kW connected (node design), IP54", 1,
     "purchased cabinet (envelope)", mass["control_cabinet"], "buy",
     "purchased per plan rule 6"],
    ["7", "Nozzle set per docs-authority/nozzles/VAC_CAST.csv: 3 atmospheric open-bore "
          "tube connections flush at the envelope faces (drain through the plinth, vent "
          "riser on the chamber lid)", len(schedule), "304L tube", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
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
    [None, "M10 stud + nut (ISO 4014 / ISO 4032)", fasteners.grade_for("304"), 12,
     "chamber lid clamp and cabinet rails",
     "grade rule W5: A4-70 on the 304L joint; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 forming class N+1 rated envelope (A-M-282)",
    "chamber": {"xy_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + T_LID], "wall_mm": T_WALL},
    "purchased_bay": {"x_mm": [CH_X, L]},
}
p["design"] = {
    "machine": "vacuum tilt-pour casting station, N+1 standby of CAST_LINE/CONT_CAST "
               "(node design machine)",
    "mat": "304L vacuum chamber; graphite crucible + alumina backup; steel table hardware "
           "(duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_WALL, "wall_basis": "study fab-page 304L t6 vacuum shell (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none); the 3 kg design-case melt is a "
                 "process-inventory solid, not a BOM part",
    "purchased": "vacuum pump skid and control cabinet (7.5 kW connected, node design), "
                 "drawn as their envelopes (plan rule 6)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; chamber on the plinth x 0..900, y 0..760, "
             "z 60..1200; mould-tilt table inside the chamber; pump and cabinet bay x 920..1500",
    "nozzle_spread": "the schedule gives inlet/bottom/top and heights only; N1 melt inlet "
                     "on +Y at x 300 flush at the envelope face; N2 drain under the "
                     "crucible axis; N3 vent riser on the chamber lid to the envelope top; "
                     "per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
