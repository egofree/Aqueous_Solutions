"""RF_HEAT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Machine: RF preheat/hold unit, N+1 diverse standby of IND_MELT at equal melt duty
(duty section 2: standby-zero design-day rate, energized on the IND_MELT coil/PSU
outage, outage_d 2, crucible_kg 10 class, 100-400 kHz through-coil, connected_kW 5;
A-M-282/A-M-232). A real machine drawn per the duty section 3 construction:
clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing (the same
melt-shop lining class as IND_MELT), with the water-cooled copper RF coil inside
its enclosure, RF/PSU cabinet on the +X bay (purchased envelope per plan rule 6).
The clay-graphite crucible is the purchased consumable (buy row). There is no
piped process connection on the graph for this unit (duty section 4: no nozzle
schedule is issued), so no nozzle hardware is drawn - the named hold sits in
WORK_ORDER W12. No measured rate anywhere.

Placement frame: x along 1000 mm, y along 1000 mm, z up, origin at the envelope
corner. Connection hardware: none (no schedule).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import fasteners, graph_node, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm                    # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("RF_HEAT")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])         # 1000 x 1000 x 1500
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

RHO_CS = materials.density("CS")
RHO_CU = materials.density("Cu")
RHO_GRAPHITE = materials.density("graphite")
RHO_FIBRE = 128.0                  # ceramic-fibre board 128 kg/m3 (IND_MELT lining class)

T_SHELL = 4.0                      # CS casing, study fab-page value (hold, W12)
T_FIBRE = 150.0                    # ceramic-fibre hot face (duty section 3: same lining class as IND_MELT)
CH_X, CH_Y = 660.0, 1000.0         # casing footprint
CH_Z0, CH_Z1 = 60.0, 1160.0        # casing on the plinth
T_PLINTH = 60.0
CX, CY = CH_X / 2, CH_Y / 2
CRUC_D, CRUC_H = 110.0, 165.0      # clay-graphite crucible, 10 kg class (duty section 2)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- CS casing t4 with lid
casing = box(0, 0, CH_Z0, CH_X, CH_Y, CH_Z1 - CH_Z0).cut(
    box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
        CH_Z1 - CH_Z0 - 2 * T_SHELL))
parts["casing"] = casing
parts["lid"] = box(0, 0, CH_Z1, CH_X, CH_Y, 40.0)

# ---------------------------------------------------------------- ceramic-fibre hot face t150
fibre = box(T_SHELL, T_SHELL, CH_Z0 + T_SHELL, CH_X - 2 * T_SHELL, CH_Y - 2 * T_SHELL,
            CH_Z1 - CH_Z0 - 2 * T_SHELL).cut(
    box(T_SHELL + T_FIBRE, T_SHELL + T_FIBRE, CH_Z0 + T_SHELL + T_FIBRE,
        CH_X - 2 * (T_SHELL + T_FIBRE), CH_Y - 2 * (T_SHELL + T_FIBRE),
        CH_Z1 - CH_Z0 - 2 * (T_SHELL + T_FIBRE)))
parts["fibre_lining"] = fibre

# ---------------------------------------------------------------- clay-graphite crucible (consumable) + pedestal
parts["crucible"] = tube(CRUC_D / 2, CRUC_D / 2 - 12.0, (CX, CY, 300.0), "Z", CRUC_H)
parts["crucible_pedestal"] = rod(70.0, (CX, CY, CH_Z0 + T_SHELL + T_FIBRE), "Z", 146.0)

# ---------------------------------------------------------------- water-cooled Cu RF coil + enclosure + leads
coil = None
for i in range(8):
    t = tube(7.5, 5.0, (CX, CY, 320.0 + i * 26.0), "Z", 16.0)
    coil = t if coil is None else coil.union(t)
parts["rf_coil"] = coil
parts["coil_enclosure"] = box(CX - 120.0, CY - 120.0, 280.0, 240.0, 240.0, 340.0).cut(
    box(CX - 110.0, CY - 110.0, 288.0, 220.0, 220.0, 324.0))
parts["coil_leads"] = rod(7.5, (CX + 120.0, CY, 360.0), "X", CH_X - CX - 120.0)

# ---------------------------------------------------------------- RF / PSU cabinet (+X bay, purchased envelope)
parts["rf_cabinet"] = box(CH_X, 0, 0, L - CH_X, 500.0, H).cut(
    box(CH_X + 8.0, 8.0, 8.0, L - CH_X - 16.0, 484.0, H - 16.0))

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
    "casing": vol["casing"] * RHO_CS / 1e9,
    "lid": vol["lid"] * RHO_CS / 1e9,
    "fibre_lining": vol["fibre_lining"] * RHO_FIBRE / 1e9,
    "crucible": vol["crucible"] * RHO_GRAPHITE / 1e9,
    "crucible_pedestal": vol["crucible_pedestal"] * RHO_GRAPHITE / 1e9,
    "rf_coil": (vol["rf_coil"] + vol["coil_leads"]) * RHO_CU / 1e9,
    "coil_enclosure": vol["coil_enclosure"] * RHO_CS / 1e9,
    "rf_cabinet": vol["rf_cabinet"] * RHO_CS / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "graph_revision": REV,
    "solids": len(solid_val.Solids()), "all_parts_valid": valid,
    "machine": {
        "casing": {"od_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + 40.0], "wall_mm": T_SHELL,
                   "wall_basis": "study fab-page 4 mm CS casing (duty section 3 lining class; "
                   "no thickness booked on the node - hold, WORK_ORDER W12)"},
        "lining": {"fibre_mm": T_FIBRE, "basis": "ceramic-fibre hot face t150 (duty section 3: "
                   "the same melt-shop lining class as IND_MELT)"},
        "crucible": {"od_mm": CRUC_D, "h_mm": CRUC_H,
                     "basis": "clay-graphite crucible, the 10 kg class (node design "
                     "crucible_kg); consumable, buy"},
        "coil": {"turns": 8, "tube_od_mm": 15.0,
                 "basis": "water-cooled copper RF coil inside its enclosure (duty section 3), "
                 "100-400 kHz through-coil (node design freq_kHz); connected_kW "
                 f"{DS.get('connected_kW')} is the node rating"},
        "rf_cabinet": "RF generator / PSU cabinet on the +X bay - purchased envelope per "
                      "plan rule 6",
        "quartz_sleeve": "the duty section 3 quartz isolation-sleeve alternative applies only "
                         "past the crucible wall under flux vapours - not drawn (hold, W12)"},
    "standby": {"state": "standby_rated N+1 diverse of IND_MELT at equal melt duty "
                "(A-M-282/A-M-232); energized on the IND_MELT coil/PSU outage "
                f"(outage_d {DS.get('outage_d')}); design-day rate zero on the graph",
                "basis": "duty section 2 sizing study"},
    "material": {"class": "clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing",
                 "ca_mm": 0.0,
                 "basis": "duty section 3 (X-MAT-22, the IND_MELT lining class); CA 0 mm - "
                 "dry furnace service (AQS-STD-001 shop rule)"},
    "a_mach_anchors": "8 M12 wedge anchors, plinth to slab (fasteners.csv)",
    "nozzles": "no piped process connection on the graph; no nozzle schedule is issued "
    "(duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)",
    "nozzle_count_schedule": 0,
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (CS, anchor bosses)", 1, "carbon steel",
     mass["plinth"], "make", "dry furnace-shop service, CA 0 mm (AQS-STD-001 shop rule); "
     "anchors in fasteners.csv"],
    ["2", f"Furnace casing CS t{T_SHELL:g}, {CH_X:g} x {CH_Y:g} x {CH_Z1 - CH_Z0:g}, with lid",
     1, "carbon steel", round(mass["casing"] + mass["lid"], 1), "make",
     "duty section 3: 4 mm CS casing (the IND_MELT lining class); wall is the study fab-page "
     "value (hold, WORK_ORDER W12); N+1 diverse standby of IND_MELT (A-M-282)"],
    ["3", f"Ceramic-fibre hot face t{T_FIBRE:g}", 1, "ceramic-fibre board 128 kg/m3",
     mass["fibre_lining"], "make", "duty section 3: the IND_MELT melt-shop lining class"],
    ["4", f"Clay-graphite crucible D{CRUC_D:g} x {CRUC_H:g} on its pedestal "
          f"({DS.get('crucible_kg'):g} kg class)", 1, "clay-graphite (consumable)",
     round(mass["crucible"] + mass["crucible_pedestal"], 1), "buy",
     "duty section 3 consumable; change-out at the unit task 12 work order"],
    ["5", f"Water-cooled Cu RF coil, 8 turns x OD 15, inside its enclosure "
          f"({DS.get('freq_kHz')} kHz through-coil, node design)", 1, "Cu ETP tube",
     mass["rf_coil"] + mass["coil_enclosure"], "make",
     "duty section 3: the coil enclosure keeps the water-cooled coil out of the melt space; "
     "cooling-water circuit is loop hardware, not modeled (WORK_ORDER W12)"],
    ["6", f"RF generator / PSU cabinet, {DS.get('connected_kW')} kW connected (node design), "
          "IP54", 1, "purchased cabinet (envelope)", mass["rf_cabinet"], "buy",
     "purchased per plan rule 6; standby unit, energized only on the IND_MELT outage "
     "(A-M-282); the RF supply is the A-M-232 rating held"],
    ["7", "Nozzle set: none - no piped process connection on the graph, no schedule issued "
          "(duty section 4; hold, WORK_ORDER W12)", 0, "n/a", 0.0, "n/a",
     "no nozzle hardware drawn; a schedule row lands as a DN15 set-in when the graph rates "
     "an edge"],
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
     "lid clamp and coil-enclosure cover",
     "grade rule W5: 8.8 on carbon steel; study torque, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "A-M-199 melt class N+1 rated envelope (A-M-282)",
    "casing": {"xy_mm": [CH_X, CH_Y], "z_mm": [CH_Z0, CH_Z1 + 40.0], "wall_mm": T_SHELL},
    "cabinet_bay": {"x_mm": [CH_X, L]},
}
p["design"] = {
    "machine": "RF preheat/hold unit, N+1 diverse standby of IND_MELT at equal melt duty "
               "(node design service)",
    "mat": "clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing (duty section 3)",
    "ca_mm": 0.0,
    "wall_mm": T_SHELL, "wall_basis": "study fab-page CS t4 casing (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none)",
    "purchased": f"RF generator / PSU cabinet {DS.get('connected_kW')} kW connected (node "
                 "design), drawn as its envelope (plan rule 6); crucible is the purchased "
                 "consumable",
}
p["layout"] = {
    "frame": "origin at the envelope corner; casing on the plinth x 0..660, y 0..1000, "
             "z 60..1200; crucible axis at the chamber centre; RF cabinet bay x 660..1000",
    "nozzle_spread": "no piped process connection on the graph (duty section 4); no nozzle "
                     "hardware drawn (hold, WORK_ORDER W12)",
    "hardware_idiom": "no connection hardware; bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "part_mass_kg")}), flush=True)
