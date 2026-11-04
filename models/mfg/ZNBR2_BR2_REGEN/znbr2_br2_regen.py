"""ZNBR2_BR2_REGEN manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-COL).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker; the
design block beside them is written by flow_graph/param/ess_tf.py, X-MFG-43b) and rebuilds
every solid. Placement frame: column axis on the skid centre, z up, origin at the envelope
corner.

Every dimension is an authority figure or a named layout choice:

- Envelope 400 x 400 x 3700 mm, node size_mm (set by ess_tf with the design, X-MFG-43b).
  The build fills it: the plinth spans the footprint, the vent riser tops the box.
- Column: PVC-U DN100 Sch 80 (OD 114.3, wall 8.56, ASTM D1785) at the duty section 2 rules
  on the live purge: diameter at 1.5 m/s on the 35.9 m3/h headspace purge (D_req 92.0 mm;
  the duty 30 m3/h figure and its 84 mm diameter predate the X-PAR-02 TF re-solve - hold,
  W12(1)); bed = NTU 6 x HTU 0.5 m = 3000 mm of 25 mm PVC-U Pall rings (in-house cut tube
  rings, X-MFG-32 class). HTU and NTU stay the duty-held figures (duty section 8: HTU is a
  packing figure, not a measured transfer unit - A-COL hold, W12(2)).
- Internals as solids (A-COL): perforated packing support plate (50 % open envelope), the
  random ring bed, a drip-pipe liquid distributor and a mesh demister pad (the AQS-DUTY-061
  house classes). No liquor inlet is drawn (duty section 2: no liquor inlet; the scrub
  liquor loop is the S69B return); the sump is the 450 mm house class, not derived from the
  gas mass (duty section 2 rule).
- Material: duty section 3 - PVC-U shell, sump, liquor piping and packing; FKM gaskets; no
  metal wetted part; PVDF excluded above pH 12 and PP excluded for halogens (AQS-STD-002);
  the hypobromite rating stands on a coupon test (hold, W12(3)).
- Nozzles: all 4 rows of docs-authority/nozzles/ZNBR2_BR2_REGEN.csv drawn at tag, face,
  height and bore as solvent-welded PVC-U socket stubs flush at the column/skid faces
  (duty section 4: hose, atmospheric; DN copied from the edge). N4's 2000 datum is the
  schedule placeholder: the riser stands on the top head and flushes at the envelope top
  (hold, W12(4)).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials   # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 400 x 400 x 3700
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

OD = float(DS["od_mm"])                                    # 114.3 PVC-U DN100 Sch 80
T = float(DS["wall_mm"])                                   # 8.56
SUMMP = float(DS["sump_mm"])                               # 450
SUPPORT_T = float(DS["support_mm"])                        # 10
BED = float(DS["packed_mm"])                               # 3000
DISTR_T = float(DS["distributor_mm"])                      # 80
DEM_T = float(DS["demister_mm"])                           # 100
TOP_T = 8.0                                                # top cap plate, solvent-welded
Z0 = 40.0                                                  # plinth to column base
T_PLINTH = Z0
Z_SUMPTOP = Z0 + SUMMP                                     # 490
Z_SUP0 = Z_SUMPTOP                                         # support plate 490..500
Z_BED0 = Z_SUP0 + SUPPORT_T - 0.5                          # bed roots 0.5 mm into the support plate
Z_BED1 = Z_BED0 + BED                                      # 3499.5
Z_DISTR0 = Z_BED1 + 0.5                                    # distributor 3500..3580
Z_DEM0 = Z_DISTR0 + DISTR_T + 10.0                         # demister 3590..3690 (10 mm clear of the distributor)
Z_DEM1 = Z_DEM0 + DEM_T                                    # 3690
Z_CAP0 = Z_DEM1 + 0.5                                      # top cap 3690.5..3698.5
Z_TOP = H                                                  # riser tops the envelope (0.5 proud of the cap)

RHO_PVC = materials.density("PVC") or 1400.0               # PVC-U sheet/pipe class
RHO_FKM = 1800.0                                           # FKM gasket class, study density

assert L == 400.0 and W == 400.0 and H == 3700.0, "ZNBR2_BR2_REGEN node envelope changed"
assert OD == 114.3 and T == 8.56, "column nominal changed"
assert abs(Z_CAP0 + TOP_T - (H - 1.5)) < 0.01, "column internals must close just under the envelope top"
assert float(DS["gas_m3_h"]) > float(DS["gas_duty_m3_h"]), "the live purge must bound the duty figure"


def tube(len_, r_out=OD / 2, r_in=OD / 2 - T):
    return cq.Workplane("XY").circle(r_out).circle(r_in).extrude(len_)


parts = {}
parts["plinth"] = (cq.Workplane("XY").box(L, W, T_PLINTH, centered=False)
                   .cut(cq.Workplane("XY", origin=(L / 2 - 60, W / 2 - 60, 0))
                        .box(120, 120, Z0, centered=False)))            # drain slot in the plinth
CX, CY = L / 2, W / 2
shell = tube(H - Z0 - 8.5).translate((CX, CY, Z0 + 0.5))                  # 40.5..3691, rooted 0.5 mm into the plinth and into the cap
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z0 - 0.5)).circle(OD / 2).extrude(1.0))
parts["shell"] = shell                                                     # shell + base ring rooted into the plinth (no bottom plate: the plinth carries the sump)
parts["sump_floor"] = (cq.Workplane("XY", origin=(CX, CY, Z0 - 0.5)).circle(OD / 2 - T)
                       .extrude(6.0))                                      # PVC-U sump floor, rooted 0.5 mm into the plinth
parts["top_cap"] = (cq.Workplane("XY", origin=(CX, CY, Z_CAP0)).circle(OD / 2)
                    .extrude(TOP_T))                                       # solvent-welded top cap; the shell roots into it
parts["support"] = (cq.Workplane("XY", origin=(CX, CY, Z_SUP0)).circle(OD / 2 - T)
                    .extrude(SUPPORT_T)
                    .cut(cq.Workplane("XY", origin=(CX, CY, Z_SUP0)).circle(OD / 2 - T)
                         .polygon(12, (OD / 2 - T) * 1.35).extrude(SUPPORT_T)))   # perforated support (50 % open envelope)
parts["bed"] = (cq.Workplane("XY", origin=(CX, CY, Z_BED0)).circle(OD / 2 - T - 1.0)
                .extrude(BED))                                             # random ring bed envelope
parts["distributor"] = (cq.Workplane("XY", origin=(CX, CY, Z_DISTR0)).circle(OD / 2 - T)
                        .extrude(DISTR_T)
                        .cut(cq.Workplane("XY", origin=(CX + 20, CY, Z_DISTR0 + 10))
                             .box(OD, OD, 60, centered=False)))            # drip-pipe distributor envelope with the header channel
parts["demister"] = (cq.Workplane("XY", origin=(CX, CY, Z_DEM0)).circle(OD / 2 - T)
                     .extrude(DEM_T))                                      # mesh pad envelope
# vent riser on the top cap, flush at the envelope top
parts["vent_riser"] = (cq.Workplane("XY", origin=(CX, CY, Z_TOP - 60.5)).circle(30.4)
                       .circle(30.4 - 3.4).extrude(61.0))                  # DN50 riser, roots into the cap, 0.5 mm proud at the envelope top

# ---------------------------------------------------------------- nozzles (schedule verbatim)
schedule = P["nozzles"]
DN_OD = {r["size"]: dn.pipe_od(r["size"]) for r in schedule if r["size"].startswith("DN")}
WALL40 = {r["size"]: dn.pipe_wall(r["size"], 40) for r in schedule if r["size"].startswith("DN")}
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    od_s, wl = DN_OD[dnl], WALL40[dnl]
    if face0 == "bottom":              # drain: boss through the plinth slot, 0.5 mm proud below
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(od_s / 2).circle(od_s / 2 - wl)
             .extrude(Z0 + 6.5).translate((CX, CY, 0.0)))
        z_d = -0.5
        note = "drain boss through the plinth slot (schedule datum 50)"
    elif face0 == "top":               # the CSV carries top/2000: the riser IS the vent
        s = None
        note = ("schedule datum 2000 is the placeholder elevation: the vent is the DN50 riser "
                "on the top cap, flush at the envelope top (hold, W12(4))")
        z_d = H
    elif face0 in ("inlet", "outlet"):
        z_d = float(r["height_mm"])
        y_d = CY
        ln = 55.0 + 20.0               # pierce the shell wall, root inside the cavity
        if face0 == "inlet":
            s = (cq.Workplane("YZ", origin=(0.0, y_d, z_d)).circle(od_s / 2).circle(od_s / 2 - wl)
                 .extrude(CX - OD / 2 + ln))
        else:
            s = (cq.Workplane("YZ", origin=(L, y_d, z_d)).circle(od_s / 2).circle(od_s / 2 - wl)
                 .extrude(-(L - (CX + OD / 2) + ln)))
        note = ("schedule datum drawn as issued; solvent-welded PVC-U socket stub, atmospheric "
                "open bore flush at the skid face (duty section 4: hose, atmospheric)")
    else:
        continue
    if s is not None:
        noz_pieces.append(s)
    drawn[tag] = {"style": "pvc_socket_stub" if s is not None else "riser", "dn": dnl,
                  "face": face0, "height_mm": r["height_mm"], "drawn_height_mm": z_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup reported (A-VES)
v_sump = round(math.pi * (OD / 2 - T) ** 2 * SUMMP / 1e6, 1)               # L, nominal sump volume

solid = cq.Compound.makeCompound([wp.val() for _, wp in parts.items()])
out = HERE / "export"; out.mkdir(exist_ok=True)
cq.exporters.export(solid, str(out / (UNIT.lower() + ".step")), opt={"write_pcurves": False, "precision_mode": 0})
cq.exporters.export(solid, str(out / (UNIT.lower() + ".stl")))
cq.exporters.export(cq.Compound.makeCompound([wp.val().scale(0.001) for _, wp in parts.items()]),
                    str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")), opt={"ascii": True})
assert stl_manifold(str(out / (UNIT.lower() + ".stl"))), "export STL must read back closed and manifold"

dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"), "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(wp.val().isValid() for wp in parts.values()),
    "solids_note": "one compound of closed solids: plinth with drain slot, shell, sump floor, "
    "perforated support plate, ring bed, distributor, demister, top cap, vent riser and the "
    "socket stubs; every union/cut partner overlaps or clears, so the mesh reads back "
    "closed and manifold",
    "a_col": {
        "packed_mm": BED, "packing": DS["packing"], "htu_m": float(DS["htu_m"]), "ntu": int(DS["ntu"]),
        "removal": float(DS["removal"]), "y_out_ppmv": int(DS["y_out_ppmv"]),
        "D_req_mm": float(DS["D_req_mm"]), "DN_mm": int(DS["DN_mm"]),
        "gas_m3_h": float(DS["gas_m3_h"]), "gas_duty_m3_h": float(DS["gas_duty_m3_h"]),
        "basis": "A-COL: packing height, support, distributor and demister are solids; HTU and "
        "NTU stay the duty-held figures (duty section 8; W12(2)). Diameter at 1.5 m/s on the "
        "live purge (ess_tf, X-MFG-43b); the duty 30 m3/h / 84 mm figures predate the TF "
        "re-solve (W12(1))",
    },
    "holdup_L": {"sump_nominal": v_sump,
                 "basis": "the nominal sump class is hardware (AQS-DUTY-061 house class), not a "
                 "residence time derived from the gas mass (duty section 2 rule); reported, "
                 "not used (A-VES rule)"},
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": {}, "cadquery": cq.__version__,
}
v_shell = math.pi * (OD * OD - (OD - 2 * T) ** 2) / 4 * (H - Z0) / 1e9
report["part_mass_kg"] = {
    "shell_caps": round(v_shell * RHO_PVC + math.pi * OD * OD / 4 * (TOP_T + 6.0) / 1e9 * RHO_PVC, 1),
    "internals": round((math.pi * (OD / 2 - T) ** 2 / 1e6) * (SUPPORT_T + DISTR_T + DEM_T) * RHO_PVC / 1e3
                       + math.pi * (OD / 2 - T - 1) ** 2 * BED / 1e9 * 380.0, 1),   # bed at the 380 kg/m3 bulk class of cut PVC rings
    "plinth_riser_stub": round((L * W * T_PLINTH - 120 * 120 * Z0) * 7800 / 1e9
                               + math.pi * 30.4 * 30.4 * 60 / 1e9 * RHO_PVC
                               + sum(p.val().Volume() for p in noz_pieces) * RHO_PVC / 1e9, 1),
    "gaskets": round(2 * math.pi * OD * 3 * 3 / 1e9 * RHO_FKM, 2),
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
m = report["part_mass_kg"]
rows = [
    ["1", f"Column shell PVC-U DN100 Sch 80 (OD {OD:g} x wall {T:g}), {H:g} mm with solvent-welded "
          "base ring and top cap", 1, "PVC-U (ASTM D1785), CA not applicable", m["shell_caps"], "make",
     "duty section 3: PVC-U shell, no metal wetted part; AQS-STD-002 halogen class; "
     f"sized at 1.5 m/s on the {DS['gas_m3_h']:g} m3/h purge (ess_tf, X-MFG-43b)"],
    ["2", "Packing support plate, perforated 50 % open envelope", 1, "PVC-U sheet", round(math.pi * (OD / 2 - T) ** 2 * SUPPORT_T / 1e9 * RHO_PVC, 1), "make",
     "A-COL support as a solid; AQS-DUTY-061 house class (not derived from the gas mass)"],
    ["3", f"Random packing: 25 mm PVC-U Pall rings (in-house cut tube rings), bed {BED:g} mm", 1,
     "PVC-U cut rings (bulk 380 kg/m3 class)", round(math.pi * (OD / 2 - T - 1) ** 2 * BED / 1e9 * 380.0, 1), "make",
     "duty section 2 packing (25 mm Pall rings) at the X-MFG-32 cut-ring class; X-MFG-32 jellybean line makes them"],
    ["4", "Liquid distributor, drip-pipe envelope with header channel", 1, "PVC-U", round(math.pi * (OD / 2 - T) ** 2 * DISTR_T / 1e9 * RHO_PVC, 1), "make",
     "A-COL distributor as a solid (AQS-DUTY-061 class); no liquor inlet is piped - the scrub liquor is the S69B return (duty section 2)"],
    ["5", "Mesh demister pad 100 mm", 1, "PVC or PP mesh", round(math.pi * (OD / 2 - T) ** 2 * DEM_T / 1e9 * 150.0, 1), "buy",
     "A-COL demister as a solid (AQS-DUTY-061 class); PP excluded for halogens (AQS-STD-002) - PVC mesh, coupon test with the hypobromite rating (W12(3))"],
    ["6", f"Nozzle set per docs-authority/nozzles/{UNIT}.csv: {len(schedule)} rows (gas in, electrolyte "
          "return out, drain boss, vent riser)", len(schedule), "PVC-U socket + FKM gaskets", round(sum(p.val().Volume() for p in noz_pieces) * RHO_PVC / 1e9 + report["part_mass_kg"]["gaskets"], 1), "make",
     "schedule tags/faces/heights verbatim; solvent-welded PVC-U per ASTM D2564; FKM gaskets "
     "(duty section 3); vent datum 2000 is the placeholder (W12(4))"],
    ["7", "Plinth 400 x 400 x 40 with drain slot", 1, "PVC-U sheet on a plinth class", round((L * W * T_PLINTH - 120 * 120 * Z0) * 7800 / 1e9, 1), "make",
     "skid seating; the drain drops through the plinth slot"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M8 U-bolt with nut and gasketed clamp", fasteners.grade_for("316L", "polymer"), 2,
     "column hold-down clamps to the plinth (dry side)",
     "polymer-joint rule: stainless hardware at PVC-U, supplier rule named (AQS-PLAN-006 W5); "
     "study size, confirmed at fabrication"],
    [None, "Solvent cement joints", "PVC-U per ASTM D2564", 1,
     "all shell, cap, stub and riser joints",
     "solvent-welded PVC-U per ASTM D2564 (duty section 3 construction); not a bolted joint - "
     "the register row carries the joint system"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "column": {"od_mm": OD, "wall_mm": T, "z_mm": [Z0, Z_DEM1 + TOP_T]},
    "bed_z_mm": [Z_BED0, Z_BED1], "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": "packed Br2-recovery wash column at the duty section 2 rules on the live "
    "purge (ess_tf, X-MFG-43b); internals as solids per A-COL",
    "wetted": "PVC-U wetted path, FKM gaskets, no metal wetted part (duty section 3); "
    "hypobromite rating on coupon test (W12(3))",
})
p["layout"] = {
    "frame": "origin at the envelope corner; column axis at the skid centre; plinth 0..40 "
             "(tanks and shell root 0.5 mm into it); sump to 490; support 490..500; bed "
             "499.5..3499.5; distributor 3500..3580; demister 3590..3690; top cap to 3698.5; "
             "vent riser flush at the envelope top",
    "nozzle_spread": "gas in -Y at z 400 and electrolyte return +Y at z 1500 as issued; drain "
                     "boss through the plinth; vent as the DN50 riser on the top cap flush at "
                     "the envelope top; per-tag positions in check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule")}), flush=True)
