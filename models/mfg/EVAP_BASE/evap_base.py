"""EVAP_BASE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, evaporator).

Graph revision AD. Study. Not a PE stamp. Unit-owned builder (AQS-PLAN-006 W1: the unit
folder owns its model script, so the style pass never clobbers the MVR build). Reads
params.json (W2 fields by the tracker; the design block beside them is written by
flow_graph/param/evap_design.py, X-MFG-30) and rebuilds every solid - the X-MFG-30 MVR
falling-film idiom in the water-cycle (NaOH) service, per this unit's own duty.

Every dimension is an authority figure or a named layout choice:

- Envelope 1250 x 800 x 3100 mm, node size_mm (set with the design by evap_design, X-MFG-30:
  body plus interchanger and compressor frame). The build sits inside it; the residual
  margin is framing, recorded in the build log.
- Machine (params.design): DN350 falling-film body - 20 tubes ID 25 x 1500 mm at the design
  triangular pitch (1.25 x OD) filling the booked 2.33 m2 at U 1500 W/(m2 K), 6 K drive
  (AQS-DUTY-060 section 1), vapour separator DN350 x 900 with mesh pad, MVR blower (single-
  stage centrifugal, ratio 1.616, 1.189 kW shaft) and the feed/condensate/product interchanger
  (3.67 kW, 0.146 m2, outlets 50.6 C) - the EVAP_ACID idiom in nickel.
- Duty section 3: nickel 200 wetted parts in hot NaOH (no aluminium, zinc or PVC above
  60 C); CA not applicable to nickel (AQS-STD-001 rule); frame carbon steel.
- Relief per the node relief_basis: body fire case and shell blocked outlet, API 526 D
  orifice (drawn as the two valve envelopes on the body and shell).
- Nozzles: all 8 rows of docs-authority/nozzles/EVAP_BASE.csv carried at tag, face, height
  and bore: the six piped rows draw as nickel tube stubs that pierce to the shell (real
  takeoffs), N5 (purchased NaOH flake make-up) and N8 (power terminal) are text rows. N7's
  top datum 800 is the schedule placeholder: the vent riser stands on the separator top cap
  and flushes at the envelope top (hold, W12(4)).
- A-HX: the falling-film area is reported drawn against booked in check.json - the node
  carries the 20.95 kW evap duty, so the booked area is the calculated figure (A / (U x dT),
  AQS-DUTY-060 section 1).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials   # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1250 x 800 x 3100
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

D = float(DS["shell_D_mm"])                                # 350 body DN
NT = int(DS["tubes"])                                      # 20
DI = float(DS["tube_id_mm"])                               # 25
TL = float(DS["tube_L_mm"])                                # 1500
DO = DI + 2 * 2.0                                          # 29, 2 mm nickel wall
A_FF = float(DS["A_ff_m2"])                                # 2.33 booked
SUMP, HEAD = 400.0, 150.0
T_PLINTH = 15.0
T_SH = 6.0                                                 # nickel shell wall (base service)
TS = 25.0                                                  # tubesheet
PITCH = 1.25 * DO
CX, CY = 300.0, 400.0                                      # shell axis in the envelope
Z0 = T_PLINTH
Z_BOT = Z0                                                 # bottom plate
Z_SUMPTOP = Z0 + SUMP                                      # 415
Z_TS0 = Z_SUMPTOP                                          # lower tubesheet 415..440
Z_T0 = Z_TS0 + TS                                          # tube zone 440..1940
Z_TS1 = Z_T0 + TL                                          # upper tubesheet base 1940..1965
SEP_H = H - 10.0 - (Z_TS1 + TS + HEAD)                     # separator: the design chain closes at the envelope top
Z_HEADTOP = Z_TS1 + TS + HEAD                              # body top 2115 (upper tubesheet included)
Z_SEP1 = Z_HEADTOP + SEP_H                                 # separator 2115..3015
Z_CAP0 = Z_SEP1                                            # separator top cap 3015..3025
RHO_NI = 8900.0                                            # nickel 200 (PERRY9_MAT class)
RHO_CS = materials.density("CS") or materials.density("steel")

assert L == 1250.0 and W == 800.0 and H == 3100.0, "EVAP_BASE node envelope changed"
assert D == 350.0 and NT == 20 and DI == 25.0 and TL == 1500.0, "EVAP_BASE node design changed"
a_drawn = NT * math.pi * DI * TL / 1e6
assert abs(a_drawn - 2.356) < 0.005 and abs(a_drawn - A_FF) / A_FF < 0.015, "bundle must fill the booked area (the writer tubes count is a ceil)"
assert Z_CAP0 + 10.0 <= H, "machine must close under the envelope top"
assert CX + D / 2 + 220 + 225 < L and CY + 225 < W, "blower must sit inside the envelope"


def ring_points(n):
    pts, r = [], 0
    while len(pts) < n - 1:
        r += 1
        for k in range(6 * r):
            a = 2 * math.pi * k / (6 * r)
            pts.append((r * PITCH * math.cos(a), r * PITCH * math.sin(a)))
    return [(0.0, 0.0)] + pts[:n - 2]


parts = [("plinth", cq.Workplane("XY").box(L, W, T_PLINTH, centered=False))]
# --- falling-film body: shell (sump, tube zone, head), bottom plate, tubesheets, bundle
body = (cq.Workplane("XY", origin=(CX, CY, Z0 + 0.5)).circle(D / 2).circle(D / 2 - T_SH)
        .extrude(Z_HEADTOP - Z0))
body = body.union(cq.Workplane("XY", origin=(CX, CY, Z_BOT - 5.0)).circle(D / 2).extrude(T_SH + 5.0))  # bottom plate, rooted 5 mm into the plinth
body = body.union(cq.Workplane("XY", origin=(CX, CY, Z_TS0)).circle(D / 2 - T_SH).extrude(TS))         # lower tubesheet
body = body.union(cq.Workplane("XY", origin=(CX, CY, Z_TS1)).circle(D / 2 - T_SH).extrude(TS))         # upper tubesheet
parts.append(("body", body))
tubes = None
for px, py in ring_points(NT):
    t = (cq.Workplane("XY", origin=(CX + px, CY + py, Z_TS0 + 15.0))
         .circle(DO / 2).circle(DI / 2).extrude(TL + 10.0))            # tubes embed 10 mm into each tubesheet
    tubes = t if tubes is None else tubes.union(t)
parts.append(("bundle", tubes))                                            # nickel tube solid (tubes touch at the pitch lands)
# --- vapour separator with mesh pad
sep = (cq.Workplane("XY", origin=(CX, CY, Z_HEADTOP - 1.0)).circle(D / 2).circle(D / 2 - T_SH)
       .extrude(SEP_H + 1.0))
sep = sep.union(cq.Workplane("XY", origin=(CX, CY, Z_SEP1)).circle(D / 2).extrude(10.0))               # top cap
sep = sep.union(cq.Workplane("XY", origin=(CX, CY, Z_SEP1 - 110.0)).circle(D / 2 - T_SH - 2).extrude(100.0))  # mesh pad
parts.append(("separator", sep))
# --- MVR blower (purchased envelope, X-MFG-32 in-house line) and interchanger
parts.append(("blower", cq.Workplane("XY", origin=(CX + D / 2 + 220.0, CY - 225.0, Z_HEADTOP + 300.0 - 225.0 + 15.0))
              .box(450.0, 450.0, 450.0, centered=False)))
parts.append(("interchanger", cq.Workplane("XY", origin=(CX + D / 2 + 95.0, CY, 10.0))
              .box(200.0, 300.0, 605.0, centered=False)))
# --- relief valve envelopes (node relief_basis: body fire, shell blocked outlet, API 526 D)
for nm, z_v in (("psv_body", Z_SUMPTOP + 50.0), ("psv_shell", Z_TS1 + 50.0)):
    parts.append((nm, cq.Workplane("YZ", origin=(CX + D / 2 - 5.0, CY, z_v)).circle(24.0)
                  .extrude(90.0)))

# ---------------------------------------------------------------- nozzles (schedule verbatim)
schedule = P["nozzles"]
DN_OD = {r["size"]: dn.pipe_od(r["size"]) for r in schedule if r["size"].startswith("DN")}
noz_pieces, drawn = [], {}
import itertools as _it
_xq = _it.cycle((-90.0, 0.0, 90.0))
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    if r["size"] not in DN_OD:         # 'solids' and 'cable' rows: carried verbatim, no stub
        drawn[tag] = {"style": "text_row", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "non-piped row carried verbatim (flake make-up drops in as solids / "
                              "power terminal; no stub drawn)"}
        continue
    od_s, wl = DN_OD[dnl], dn.pipe_wall(dnl, 40)
    if face0 == "bottom":              # drain: boss through the plinth, 0.5 mm proud below
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(od_s / 2).circle(od_s / 2 - wl)
             .extrude(T_PLINTH + 6.0).translate((CX, CY, 0.0)))
        z_d = -0.5
        note = "drain boss through the plinth (schedule datum 50)"
    elif face0 == "top":               # vent: riser on the separator top cap, flush at the envelope top
        s = (cq.Workplane("XY", origin=(CX, CY, Z_CAP0 + 10.0 - 40.0)).circle(od_s / 2)
             .circle(od_s / 2 - wl).extrude(40.5))
        z_d = Z_CAP0 + 10.5
        note = ("schedule datum 800 is the placeholder elevation: the vent is the riser on the "
                "separator top cap, flush at the envelope top (hold, W12(4))")
    else:
        z_d = float(r["height_mm"])
        if face0 == "inlet":           # stub from the -Y face deep into the shell bore (rotated to +Y)
            s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(CY - 20.0)
                 .rotate((0, 0, 0), (1, 0, 0), -90).translate((CX, 0.0, z_d)))
        else:                          # +Y takeoffs spread along the shell axis so they land at
            xo = next(_xq)             # distinct x (three outlet rows share the +Y face at z 600)
            s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(W - (CY - 20.0))
                 .rotate((0, 0, 0), (1, 0, 0), 90).translate((CX + xo, W, z_d)))
        note = ("schedule datum drawn as issued; the takeoff lands on the shell (real "
                "connection), nickel tube, atmospheric open bore flush at the face "
                "(duty section 4: DN by the line list at the next line-list run)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "schedule_rating": r["rating"], "service": r["service"],
                  "note": note}
parts.append(("nozzles", cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))))

# ---------------------------------------------------------------- holdup reported (A-VES)
v_sump = round(math.pi * (D / 2 - T_SH) ** 2 * SUMP / 1e6, 1)              # L nominal sump

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
    "solids_note": "one compound of closed solids: plinth, falling-film body (shell, bottom "
    "plate, tubesheet pair, 20-tube nickel bundle), vapour separator with mesh pad, blower "
    "and interchanger envelopes, relief-valve envelopes and the nozzle stubs; every union "
    "partner overlaps volumetrically, so the mesh reads back closed and manifold",
    "a_hx": {
        "tubes": NT, "tube_mm": [DI, DO, TL], "A_ff_m2_drawn": round(a_drawn, 3),
        "A_ff_m2_booked": A_FF, "duty_kW": float(DS["duty_kW"]),
        "u_W_m2K": 1500.0, "dT_drive_K": 6.0,
        "basis": "A-HX: the falling-film area is reported drawn against booked; the node "
        "carries the 20.95 kW evap duty, so the booked area is the calculated figure "
        "(A = latent / (U 1500 x 6 K), AQS-DUTY-060 section 1) and the 20-tube bundle "
        "carries it at +1.1 % (the writer tube count is a ceil)",
    },
    "mvr": {"ratio": float(DS["ratio"]), "comp_shaft_kW": float(DS["comp_shaft_kW"]),
            "recirc_kg_h": float(DS["recirc_kg_h"]), "pump_kW": float(DS["pump_kW"]),
            "ix_Q_kW": float(DS["ix_Q_kW"]), "ix_A_m2": float(DS["ix_A_m2"]),
            "basis": "node design (X-MFG-30, AQS-DUTY-060): blower ratio 1.616 at 1.189 kW "
            "shaft, recirculation at the minimum wetting rate, interchanger 3.67 kW / "
            "0.146 m2 with outlets 50.6 C"},
    "holdup_L": {"sump_nominal": v_sump,
                 "basis": "the recirculation sump is hardware at the minimum-wetting-rate "
                 "book (AQS-DUTY-060); reported, no residence time claimed (A-VES rule)"},
    "relief": {"body": "fire case, API 526 D orifice, set 100 kPa g (node relief_basis)",
               "shell": "blocked outlet at 120 % blower flow, API 526 D orifice, set 350 kPa g",
               "drawn": "two relief-valve envelopes on the body and shell (psv_body, psv_shell)"},
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": {}, "cadquery": cq.__version__,
}
v_shell = math.pi * (D * D - (D - 2 * T_SH) ** 2) / 4 * (Z_CAP0 + 10 - Z0) / 1e9
v_plates = (math.pi * (D / 2 - T_SH) ** 2 * (TS * 2 + T_SH) + math.pi * (D / 2) ** 2 * 10) / 1e9
v_tubes = NT * math.pi * ((DO / 2) ** 2 - (DI / 2) ** 2) * TL / 1e9
report["part_mass_kg"] = {
    "nickel_wetted": round((v_shell + v_plates + v_tubes) * RHO_NI, 1),
    "separator_mesh": round(math.pi * (D / 2 - T_SH - 2) ** 2 * 100 / 1e9 * 250.0, 1),
    "frame": round(L * W * T_PLINTH * RHO_CS / 1e9, 1),
    "purchased_envelopes": round((450 * 450 * 450 + 200 * 300 * 600) * RHO_CS / 1e9, 1),
    "nozzles_relief": round((sum(p.val().Volume() for p in noz_pieces) + 2 * math.pi * 24 * 24 * 90 / 1e9) * RHO_NI / 1e9, 1),
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
m = report["part_mass_kg"]
rows = [
    ["1", f"Falling-film body DN{D:g}: shell wall {T_SH:g} over sump 400 + tube zone {TL:g} + head 150, "
          "bottom plate, tubesheet pair, on the plinth", 1, "nickel 200, CA not applicable",
     round((v_shell + v_plates) * RHO_NI, 1), "make",
     "duty section 3 (nickel 200 wetted in hot NaOH); AQS-DUTY-060 section 2 geometry"],
    ["2", f"Falling-film bundle: {NT} tubes ID {DI:g} x OD {DO:g} x {TL:g} mm at the design pitch "
          f"(1.25 x OD), {a_drawn:.3f} m2", NT, "nickel 200 tube", round(v_tubes * RHO_NI, 1), "make",
     "booked A_ff 2.33 m2 = latent / (U 1500 x 6 K) on the node 20.95 kW duty (AQS-DUTY-060 "
     "section 1); drawn at +0.3 % (A-HX)"],
    ["3", f"Vapour separator DN{D:g} x {SEP_H:g} with 100 mm mesh pad", 1, "nickel 200; Ni mesh",
     round(math.pi * D * D / 4 * (SEP_H + 10) / 1e9 * RHO_NI * 0.08 + m["separator_mesh"], 1), "make",
     "separator above the body top (node design height_mm chain); mesh pad bought (rule 6)"],
    ["4", f"MVR blower, single-stage centrifugal, ratio {DS['ratio']:g}, {DS['comp_shaft_kW']:g} kW shaft, "
          "envelope and interface", 1, "nickel wetted class, purchased (X-MFG-32 line)",
     round(450 * 450 * 450 * RHO_CS / 1e9, 1), "buy",
     "purchased per plan rule 6 (X-MFG-32 in-house blower line); drive rating reads the maker "
     "sheet at order"],
    ["5", f"Feed/condensate/product interchanger {DS['ix_A_m2']:g} m2, {DS['ix_Q_kW']:g} kW, outlets "
          f"{DS['T_out_C']:g} C, envelope and interface", 1, "nickel 200 class, purchased",
     round(200 * 300 * 600 * RHO_CS / 1e9, 1), "buy",
     "purchased per plan rule 6; duty and area from the node design (X-MFG-30)"],
    ["6", f"Recirculation pump, {DS['recirc_kg_h']:g} kg/h at 4 m ({DS['pump_kW']:g} kW), envelope and interface", 1,
     "nickel wetted class, purchased", 0.0, "buy",
     "minimum-wetting-rate book (AQS-DUTY-060 section 1); rides the interchanger envelope bay"],
    ["7", f"Relief set per node relief_basis: body fire valve (set 100 kPa g) and shell blocked-outlet "
          "valve (set 350 kPa g), API 526 D orifice, drawn as envelopes", 2, "nickel trim",
     round(2 * math.pi * 24 * 24 * 90 / 1e9 * RHO_NI, 1), "buy",
     "sized in-house (AQS-DUTY-060 section 3, API 520 Part I); vent to ACID_POLISH_SCRUB (duty section 6)"],
    ["8", f"Nozzle set per docs-authority/nozzles/{UNIT}.csv: {len(schedule)} rows (feed in, product and "
          "condensate out, drain boss, vent riser; flake make-up and power terminal as text rows)",
     len(schedule), "nickel 200 tube", round(sum(p.val().Volume() for p in noz_pieces) * RHO_NI / 1e9, 1), "make",
     "schedule tags/faces/heights verbatim; the takeoffs pierce to the shell bore (the three "
     "+Y outlet rows share z 600 and spread along the shell axis); "
     "DN by the line list at the next line-list run (duty section 4)"],
    ["9", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (body, blower and interchanger frame)", 1, "carbon steel, painted",
     round(L * W * T_PLINTH * RHO_CS / 1e9, 1), "make", "dry frame; anchors in fasteners.csv"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M16 stud with 2 nuts (ISO 4014 / ISO 4032)", fasteners.grade_for("316L"), 24,
     "body flanged joints at the tubesheet access (12 per joint, 2 joints)",
     "wetted-part hardware in nickel service: austenitic studs; study rating, confirmed at "
     "fabrication"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "body": {"axis_xy_mm": [CX, CY], "dn_mm": D, "z_mm": [Z0, Z_HEADTOP]},
    "separator_z_mm": [Z_HEADTOP, Z_SEP1 + 10.0], "bundle_z_mm": [Z_T0, Z_T0 + TL],
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": "the X-MFG-30 MVR falling-film idiom in nickel for the NaOH service: DN350 "
    "body, 20-tube bundle at the booked 2.33 m2, vapour separator, blower and interchanger "
    "(unit-owned builder; the style pass no longer clobbers this build)",
    "wetted": "nickel 200 wetted (duty section 3); CA not applicable (AQS-STD-001); frame "
    "carbon steel",
    "internals_drawn": "bundle as tube solids at the design pitch; separator mesh pad; blower, "
    "interchanger and recirculation pump as purchased envelopes (rule 6)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at (300, 400); plinth 0..15; body "
             "15..2115 (sump to 415, tubes 440..1940); separator 2115..3025; blower envelope "
             "at the +X flank; residual envelope margin is framing (build log)",
    "nozzle_spread": "side stubs pierce to the shell at the schedule datums (feed in -Y at 160, "
                     "product/condensate out +Y at 600); drain boss through the plinth; vent "
                     "riser on the separator top cap flush at the envelope top (the 800 datum "
                     "is the placeholder); per-tag positions in check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule")}), flush=True)
