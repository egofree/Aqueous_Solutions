"""COMB_HEAT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Machine: combustion reheating furnace, tertiary N+1 standby of IND_MELT (duty
section 2: standby-zero design-day rate, energized only on a long IND_MELT outage
with both electric alternates unavailable, outage_d 2, thermal_kW 30; A-M-282/
A-M-283). A real machine drawn per the duty section 3 construction: alumina-silica
brick + castable crown hot face on a mild-steel shell, 310S radiant burner tube
(combustion products stay inside the tube), flue path dry above the acid dew point
with the N1 takeoff to MET_SCRUB. The controls cabinet (connected_kW 0.05) is a
purchased envelope on the +X bay per plan rule 6. The reheating hearth rail is
drawn; no charge inventory is claimed (standby). No measured rate anywhere.

Placement frame: x along 1000 mm, y along 1000 mm, z up, origin at the envelope
corner. The schedule carries outlet/bottom/top faces, so the compass assignment
is the registered layout choice (params.json layout block); heights, bores and
ratings are docs-authority/nozzles/COMB_HEAT.csv verbatim. Connection hardware
draws flush at the envelope faces: nothing protrudes (A-core 2).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("COMB_HEAT")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])         # 1000 x 1000 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_310S = 8000.0                  # 310S class, study value (AQS-STD-001 duty-side decision named in WO W12)
RHO_BRICK = 2200.0                 # alumina-silica brick, study fab-page value (hold, W12)

T_SHELL = 4.0                      # mild-steel shell, study fab-page value (hold, W12)
T_BRICK = 115.0                    # alumina-silica brick hot face, study (hold, W12)
CH_X, CH_Y = 660.0, 1000.0         # shell footprint
CH_Z0, CH_Z1 = 60.0, 1160.0        # shell on the plinth, roof on top
T_PLINTH = 60.0
TUBE_D = 130.0                     # 310S radiant burner tube OD
CX, CY = CH_X / 2, CH_Y / 2
TUBE_Z = 600.0                     # radiant-tube axis at the melt-row datum class


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

# ---------------------------------------------------------------- furnace shell (mild steel t4)
shell = box(0, 0, CH_Z0, CH_X, CH_Y, CH_Z1 - CH_Z0).cut(
    box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
        CH_Z1 - CH_Z0 - 2 * T_SHELL))
shell = shell.cut(rod(45.0, (CX, CY, -5.0), "Z", T_PLINTH + 10.0))            # drain pass
shell = shell.cut(rod(28.0, (-5.0, CY, TUBE_Z), "X", T_BRICK + 20.0))         # burner-tube pass, -X wall
parts["furnace_shell"] = shell

# ---------------------------------------------------------------- hot face: brick lining + castable crown
brick = box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
            CH_Z1 - CH_Z0 - 2 * T_SHELL - 40.0).cut(
    box(T_SHELL + T_BRICK, T_SHELL + T_BRICK, CH_Z0 + T_SHELL + T_BRICK,
        CH_X - 2 * (T_SHELL + T_BRICK), CH_Y - 2 * (T_SHELL + T_BRICK),
        CH_Z1 - CH_Z0 - 2 * (T_SHELL + T_BRICK) - 40.0))
brick = brick.cut(rod(TUBE_D / 2 + 10.0, (-5.0, CY, TUBE_Z), "X", T_BRICK + 30.0))
parts["brick_lining"] = brick
crown = box(T_SHELL + T_BRICK, T_SHELL + T_BRICK, CH_Z1 - 140.0,
            CH_X - 2 * (T_SHELL + T_BRICK), CH_Y - 2 * (T_SHELL + T_BRICK), 100.0).cut(
    box(T_SHELL + T_BRICK + 30.0, T_SHELL + T_BRICK + 30.0, CH_Z1 - 130.0,
        CH_X - 2 * (T_SHELL + T_BRICK + 30.0), CH_Y - 2 * (T_SHELL + T_BRICK + 30.0), 80.0))
parts["castable_crown"] = crown

# ---------------------------------------------------------------- 310S radiant burner tube + burner block
parts["burner_tube"] = tube(TUBE_D / 2, TUBE_D / 2 - 8.0, (30.0, CY, TUBE_Z), "X", CH_X - 30.0 - 150.0)
parts["burner_block"] = box(0.0, CY - 90.0, TUBE_Z - 90.0, 60.0, 180.0, 180.0)
parts["hearth_rail"] = box(180.0, CY - 45.0, 420.0, CH_X - 420.0, 90.0, 60.0)

# ---------------------------------------------------------------- flue: dry path above the acid dew point, N1 to MET_SCRUB
flue = tube(TUBE_D / 2 + 10.0, TUBE_D / 2, (CH_X - 220.0, CY, TUBE_Z), "X", 120.0)
flue = flue.union(box(CH_X - 110.0, CY - 30.0, TUBE_Z - 30.0, 40.0, 60.0, CH_Y - CY - 40.0 + 90.0))
parts["flue_duct"] = flue

# ---------------------------------------------------------------- controls cabinet (+X bay, purchased envelope)
parts["controls_cabinet"] = box(CH_X, 0, 0, L - CH_X, 500.0, 1400.0).cut(
    box(CH_X + 8.0, 8.0, 8.0, L - CH_X - 16.0, 484.0, 1384.0))

# ---------------------------------------------------------------- nozzle hardware (schedule verbatim, flush at the envelope faces)
r15, w15 = dn15()
noz = {}
noz["N1_offgas_stub"] = tube(r15, w15, (CH_X - 100.0, CH_Y - T_SHELL, 600.0), "Y", W - (CH_Y - T_SHELL))
noz["N2_drain"] = tube(30.5, r15, (CX, CY, 0.0), "Z", CH_Z0)
noz["N3_vent_riser"] = tube(r15, w15, (CX, CY, CH_Z1 - 6.0), "Z", H - (CH_Z1 - 6.0))
for k, v in noz.items():
    parts[k] = v

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

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
valid = all(v.val().isValid() for v in parts.values())
vol = {k: v.val().Volume() for k, v in parts.items()}
mass = {
    "plinth": vol["plinth"] * RHO_CS / 1e9,
    "furnace_shell": vol["furnace_shell"] * RHO_CS / 1e9,
    "brick_lining": vol["brick_lining"] * RHO_BRICK / 1e9,
    "castable_crown": vol["castable_crown"] * RHO_BRICK / 1e9,
    "burner_tube": (vol["burner_tube"] + vol["burner_block"]) * RHO_310S / 1e9,
    "hearth_rail": vol["hearth_rail"] * RHO_CS / 1e9,
    "flue_duct": vol["flue_duct"] * RHO_310S / 1e9,
    "controls_cabinet": vol["controls_cabinet"] * RHO_CS / 1e9,
    "nozzles": sum(vol[k] for k in noz) * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
schedule = [r for r in P["nozzles"]]
drawn = {}
for r in schedule:
    tag = r["tag"]
    note = "atmospheric open-bore DN15 tube, flush at the envelope face (duty section 4)"
    if tag == "N1":
        note = "combustion off-gas takeoff on +Y at z 600 (registered layout), dry flue path " \
               "above the acid dew point to MET_SCRUB (duty section 3); atmospheric open-bore " \
               "DN15 tube, flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":
        note += "; flush at the envelope bottom (schedule datum 50)"
    if r["face"] == "top":
        note += "; schedule datum 800 is the placeholder elevation - the riser stands on the " \
                "shell roof and flushes at the envelope top (hold, WORK_ORDER W12)"
    drawn[tag] = {"style": "tube", "dn": r["size"], "face": r["face"], "height_mm": r["height_mm"],
                  "drawn_height_mm": {"N1": 600.0, "N2": 0.0, "N3": float(H)}[tag],
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "shell": {"od_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1], "wall_mm": T_SHELL,
                  "wall_basis": "study fab-page mild-steel t4 shell (no thickness booked on "
                  "the node - hold, WORK_ORDER W12)"},
        "lining": {"brick_mm": T_BRICK, "basis": "alumina-silica brick + castable crown hot "
                   "face (duty section 3), study t115 (hold, WORK_ORDER W12)"},
        "burner_tube": {"od_mm": TUBE_D, "axis_z_mm": TUBE_Z,
                        "basis": "310S radiant tube (duty section 3): combustion products stay "
                        "inside the tube; thermal_kW 30 is the node rating; the fuel class is "
                        "the plant C5-C10 product (duty section 1)"},
        "flue": "dry flue path above the acid dew point; N1 takeoff to MET_SCRUB when "
                "energized (node design offgas)"},
    "standby": {"state": "standby_rated tertiary N+1 of IND_MELT (A-M-282/A-M-283); energized "
                f"only on a long IND_MELT outage with both electric alternates unavailable "
                f"(outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "mild-steel shell, alumina-silica brick + castable crown hot face, "
                 "310S burner tube", "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22); CA 0 mm - dry furnace service "
                 "(AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore DN15 tube connections flush at the envelope "
    "faces (duty section 4: hose, atmospheric); the schedule outlet/bottom/top faces are "
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
     mass["plinth"], "make", "dry furnace-shop service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Furnace shell mild steel t{T_SHELL:g}, {CH_X:g} x {CH_Y:g} x {CH_Z1 - CH_Z0:g}",
     1, "carbon steel", mass["furnace_shell"], "make",
     "duty section 3: mild-steel shell; wall is the study fab-page value (hold, WORK_ORDER "
     "W12); tertiary N+1 standby of IND_MELT (A-M-282)"],
    ["3", f"Hot face: alumina-silica brick t{T_BRICK:g} + castable crown", 1,
     "alumina-silica brick + castable", round(mass["brick_lining"] + mass["castable_crown"], 1),
     "make", "duty section 3 (SCHACHT2004 ch. 10 class); thickness is the study fab-page "
     "value (hold, WORK_ORDER W12)"],
    ["4", f"310S radiant burner tube OD {TUBE_D:g} with burner block "
          f"(thermal_kW {DS.get('thermal_kW')} node rating)", 1, "310S",
     mass["burner_tube"], "make",
     "duty section 3: combustion products stay inside the tube; fuel class is the plant "
     "C5-C10 product (duty section 1); stoichiometry per TURNS2012"],
    ["5", "Hearth rail on the chamber floor", 1, "carbon steel", mass["hearth_rail"], "make",
     "reheating hearth (study, WORK_ORDER W12)"],
    ["6", "Dry flue duct with N1 takeoff to MET_SCRUB", 1, "310S", mass["flue_duct"], "make",
     "duty section 3: flue path dry above the acid dew point into MET_SCRUB when energized"],
    ["7", f"Controls cabinet, {DS.get('connected_kW')} kW connected (node design), IP54", 1,
     "purchased cabinet (envelope)", mass["controls_cabinet"], "buy",
     "purchased per plan rule 6; standby unit, energized only on the IND_MELT outage "
     "(A-M-282); burner train purchased at fabrication (WORK_ORDER W12)"],
    ["8", "Nozzle set per docs-authority/nozzles/COMB_HEAT.csv: 3 atmospheric open-bore "
          "tube connections flush at the envelope faces (off-gas takeoff, drain through "
          "the plinth, vent riser on the shell roof)", len(schedule), "carbon steel",
     mass["nozzles"], "make", "schedule tags/faces/heights verbatim; atmospheric per "
     "duty section 4"],
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
     "shell roof hatch and burner-block clamp",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "shell": {"xy_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1], "wall_mm": T_SHELL},
    "cabinet_bay": {"x_mm": [CH_X, L]},
}
p["design"] = {
    "machine": "combustion reheating furnace, tertiary N+1 standby of IND_MELT "
               "(node design service)",
    "mat": "mild-steel shell, alumina-silica brick + castable crown hot face, 310S radiant "
           "burner tube (duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_SHELL, "wall_basis": "study fab-page mild-steel t4 shell (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none); the hearth rail is furnace furniture, "
                 "a BOM part, not an internal",
    "purchased": f"controls cabinet {DS.get('connected_kW')} kW connected (node design), "
                 "drawn as its envelope (plan rule 6); burner train at fabrication",
}
p["layout"] = {
    "frame": "origin at the envelope corner; furnace shell on the plinth x 0..660, y 0..1000, "
             "z 60..1160; radiant tube along X at z 600; controls bay x 660..1000",
    "nozzle_spread": "the schedule gives outlet/bottom/top and heights only; N1 off-gas "
                     "takeoff rides the dry flue duct to +Y flush at the envelope face; N2 "
                     "drain under the crown centre; N3 vent riser on the shell roof to the "
                     "envelope top; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing protrudes, "
                      "bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}), flush=True)
