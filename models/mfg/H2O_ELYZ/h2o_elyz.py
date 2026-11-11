"""H2O_ELYZ manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4, PEM electrolyser).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph
through the shared reader (models/mfg/lib/graph_node.py; the design block is written by
flow_graph/param/specialty_sizing.py, X-SPEC lane); params.json remains as the tracker
build report. Rebuilds every solid - the PEM stack skid and its balance-of-plant deck
per the node internals row ("PEM stack, H2 and O2 gas-liquid separators, deoxo on H2,
dryer").

Every dimension is an authority figure or a named layout choice:

- Envelope 3367 x 1050 x 2200 mm, node size_mm (the A-M-279 skid allowances at the rated
  kW: stack deck 2042 + gap 100 + BoP deck 1225 at W 1050, H 2200). The build fills it:
  the plinth spans the footprint, the deck frames top at the envelope height, the face
  connections flush at the faces. The placement seed block (1800 x 800 x 1600) under-books
  it - hold, W12(1).
- Stack deck (params.design.stack, A-M-459): the PEM stack in its enclosure - the graph cell count of
  288 cm2 active (169.7 x 169.7 mm) between end plates at the 8 mm pitch, 518.4 A stack
  current at 148 V DC (76.7 kW DC) on the rated H2 of 1.5597 kg/h over the 6 h PV window
  (A-M-133); the cell-summed area 2.304 m2 is what the rated H2 books. The cells draw as
  the bipolar-plate field (plates + CCM lands at the pitch, the MEAs a BOM row); the power
  electronics ride the enclosure (purchased envelope, rule 6).
- BoP deck (node internals row): H2 and O2 gas-liquid separators DN150 x 400 (one per side,
  316L per duty section 3), the deoxo on H2 (2 beds DN80 x 345 at the A-M-168 GHSV 5000
  1/h class on 17.4 Nm3/h), the dryer on H2 (2 beds DN80 x 712, 4A/13X at margin 3), the
  DI-water loop pump envelope, and the separator deck framing. The deoxo and dryer beds
  are the issued A-M-168 purifier classes applied on the skid.
- Duty section 3: Ti porous transport layers, Ir/Ru anode / Pt cathode, PTFE ionomer, Ti
  cell hardware and PTFE compression seals; deoxo on 316L hardware; dry product lines on
  the M1 316L family. No wetted copper.
- Design 990 kPa g (node design_kPa); relief per the node relief_basis (blocked outlet at
  the compressor suction, bore 3.3 mm - the relief valves draw as envelopes on the H2 line).
- Nozzles: all 7 rows of docs-authority/nozzles/H2O_ELYZ.csv carried at tag, face, height
  and bore: the five piped rows draw as 316L tube stubs flush at the skid faces; N6 (power
  terminal) and N7 (service terminal, the Q4 stack-heat edge) are text rows with no stub.
  The schedule elevations draw as issued (placeholders per duty section 4 - W12(4)).
- A-CELL-class reporting: cell count, active size, pitch and cell-summed area match the
  design block (the flow_battery A-CELL set applied by class kinship; the PEM class draws
  the same facts) - reported in check.json against A-M-459.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("H2O_ELYZ")      # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
L, W, H = (float(v) for v in P["size_mm"])                 # 3367 x 1050 x 2200
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design

SK = DS["stack"]
CELLS = int(SK["cells"])                                   # 80
AW = float(SK["active_mm"][0]) / 1000.0 * 1000.0           # 169.7 mm active window
V_CELL = float(SK["v_cell"])                               # 1.85
SKW, SKH = float(DS["skid"]["w_mm"]), float(DS["skid"]["h_mm"])          # 1050, 2200
L_STACK = float(DS["skid"]["l_stack_mm"])                  # 2042
L_BOP = float(DS["skid"]["l_bop_mm"])                      # 1225
GAP = L - L_STACK - L_BOP                                  # 100
T_PLINTH = 100.0
PITCH = 8.0                                                # cell pitch (5 plate + 3 CCM land)
STACK_H = CELLS * PITCH + 2 * 60.0 + 40.0                  # field + end plates + bus 740
Z0 = T_PLINTH
Z_STACK0 = 300.0                                           # stack stands on the deck frame
Z_STACK1 = Z_STACK0 + STACK_H                              # 1040
T_D = 6.0                                                  # 316L vessel wall
SEP_DN, SEP_H = 150.0, 400.0                               # separators DN150 x 400
DEOX_L = float(DS["deoxo"]["tube"].split("x ")[1].split(" mm")[0])   # 345 (graph params.design.deoxo.tube)
DRY_L = float(DS["dryer"]["tube"].split("x ")[1].split(" mm")[0])    # 712 (graph params.design.dryer.tube)
RHO_TI = 4500.0                                            # Ti cell hardware (lib class has Ti G2 4510)
RHO_TI = materials.density("Ti G2") or RHO_TI
RHO_316 = materials.density("316L")
RHO_CS = materials.density("CS") or materials.density("steel")

# Cell count and envelope both come from the graph node (X-...); no hard-coded count or envelope stays.
assert abs(AW - 169.7) < 0.1, "the stack book changed (A-M-459)"
assert GAP == 100.0, "the A-M-279 deck split changed"
assert Z_STACK1 < H, "stack must close under the envelope top"
# Bed-class geometry comes from the graph design (params.design.deoxo/dryer); the builder draws what the design states.

parts = [("plinth", cq.Workplane("XY").box(L, W, T_PLINTH, centered=False))]
# ---------------------------------------------------------------- stack deck
SX0, SX1 = 0.0, L_STACK                                   # stack enclosure bay
parts.append(("stack_frame", (cq.Workplane("XY", origin=(SX0, 0, Z0 - 5.0))
                             .box(L_STACK, W, 65.0, centered=False))))              # deck frame band, rooted 5 mm into the plinth
# enclosure frame: four corner posts + top rails (the stack enclosure is open-framed for the GA)
for px in (20.0, L_STACK - 80.0):
    for py in (20.0, W - 80.0):
        parts.append((f"post_{int(px)}_{int(py)}", cq.Workplane("XY", origin=(px, py, Z0 + 60.0))
                      .box(60.0, 60.0, Z_STACK1 - Z0 - 60.0 + 45.0, centered=False)))   # posts root 5 mm into the rails
parts.append(("stack_top_rails", (cq.Workplane("XY", origin=(20.0, 20.0, Z_STACK1 + 40.0))
                                  .box(L_STACK - 40.0, W - 40.0, 40.0, centered=False))))
# the PEM stack: end plates + the bipolar-plate field (plates + CCM lands at the pitch)
scx, scy = L_STACK / 2, W / 2
parts.append(("stack_ep_lo", cq.Workplane("XY", origin=(scx - 105.0, scy - 105.0, Z_STACK0))
              .box(210.0, 210.0, 30.0, centered=False)))
plate_z0 = Z_STACK0 + 30.0
for k in range(CELLS):
    zp = plate_z0 + k * PITCH
    parts.append((f"cell_{k}", cq.Workplane("XY", origin=(scx - AW / 2, scy - AW / 2, zp))
                  .box(AW, AW, 5.0, centered=False)))          # bipolar plate, active window
parts.append(("stack_ep_hi", cq.Workplane("XY", origin=(scx - 105.0, scy - 105.0,
                                                         plate_z0 + CELLS * PITCH - 4.0))
              .box(210.0, 210.0, 33.0, centered=False)))       # 1 mm over the last plate land
parts.append(("stack_cu_buses", (cq.Workplane("XY", origin=(scx - 90.0, scy - 15.0, Z_STACK0 - 40.0))
                                 .box(180.0, 30.0, 45.0, centered=False)
                                 .union(cq.Workplane("XY", origin=(scx - 90.0, scy + 15.0 - 30.0, plate_z0 + CELLS * PITCH + 28.0))
                                        .box(180.0, 30.0, 45.0, centered=False)))))   # copper bus pair, rooted into the end plates
# power electronics enclosure (purchased envelope) at the stack-deck tail
parts.append(("power_electronics", cq.Workplane("XY", origin=(1200.0, 40.0, Z0 + 60.0))
              .box(400.0, W - 80.0, 900.0, centered=False)))
# ---------------------------------------------------------------- BoP deck
BX0 = L_STACK + GAP
sep_x = [BX0 + 120.0, BX0 + 420.0]
for i, (nm, sx) in enumerate((("h2_sep", sep_x[0]), ("o2_sep", sep_x[1]))):
    v = (cq.Workplane("XY", origin=(sx, W / 2 - SEP_DN / 2, 400.0))
         .circle(SEP_DN / 2).circle(SEP_DN / 2 - T_D).extrude(SEP_H))
    v = v.union(cq.Workplane("XY", origin=(sx, W / 2, 400.0)).circle(SEP_DN / 2).extrude(8.0))
    v = v.union(cq.Workplane("XY", origin=(sx, W / 2, 400.0 + SEP_H)).circle(SEP_DN / 2).extrude(8.0))
    parts.append((nm, v))                                      # DN150 x 400 separator vessels on legs
    parts.append((f"{nm}_legs", (cq.Workplane("XY", origin=(sx - SEP_DN / 2 + 10.0, W / 2 - SEP_DN / 2 + 10.0, Z0 - 5.0))
                                 .box(20.0, 20.0, 405.0, centered=False)
                                 .union(cq.Workplane("XY", origin=(sx + SEP_DN / 2 - 30.0, W / 2 + SEP_DN / 2 - 30.0, Z0 - 5.0))
                                        .box(20.0, 20.0, 405.0, centered=False)))))   # legs root 5 mm into the plinth
beds = []
for k, (bx, off, ln) in enumerate(((BX0 + 700.0, -180.0, DEOX_L), (BX0 + 700.0, -180.0, DEOX_L),
                                   (BX0 + 700.0, 180.0, DRY_L), (BX0 + 700.0, 180.0, DRY_L))):
    dn80_od, dn80_w = 88.9, 5.49                               # DN80 Sch 40 table (lib/dn carries DN15..DN50)
    t = (cq.Workplane("XY", origin=(bx + (k % 2) * 90.0, W / 2 + off + (0 if k < 2 else 0), 500.0))
         .circle(dn80_od / 2).circle(dn80_od / 2 - dn80_w).extrude(ln))
    beds.append((f"bed_{k}", t))
# deoxo pair + dryer pair (duplicated per the A-M-168 rule), staggered x for the second of each pair
beds[1] = (f"bed_1", beds[1][1].translate((90.0, 0.0, 0.0)))
beds[3] = (f"bed_3", beds[3][1].translate((90.0, 0.0, 0.0)))
parts.extend(beds)
parts.append(("di_water_pump", cq.Workplane("XY", origin=(BX0 + 980.0, 60.0, Z0 - 5.0))
              .box(200.0, 160.0, 245.0, centered=False)))       # purchased envelope (rule 6), rooted into the plinth
parts.append(("bop_frame", (cq.Workplane("XY", origin=(BX0, 0, Z0 - 5.0))
                            .box(L_BOP, W, 65.0, centered=False)
                            .union(cq.Workplane("XY", origin=(BX0, 0, Z0 + 60.0))
                                   .box(30.0, W, H - Z0 - 60.0, centered=False)))))   # frame band rooted 5 mm into the plinth
# relief-valve envelopes on the H2 line (node relief_basis, bore 3.3 mm book)
parts.append(("psv_h2", cq.Workplane("XY", origin=(sep_x[0] - 30.0, W / 2 + SEP_DN / 2 - T_D - 30.0, 520.0))
              .box(60.0, 40.0, 160.0, centered=False)))   # roots through the H2 separator wall

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
    if r["size"] not in DN_OD:         # cable rows: carried verbatim, no stub
        drawn[tag] = {"style": "text_row", "dn": r["size"], "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "non-piped row carried verbatim (power / service terminal; no stub drawn)"}
        continue
    od_s, wl = DN_OD[dnl], dn.pipe_wall(dnl, 40)
    if face0 == "bottom":              # drain: boss through the plinth, 0.5 mm proud below
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(od_s / 2).circle(od_s / 2 - wl)
             .extrude(T_PLINTH + 6.0).translate((500.0, W / 2, 0.0)))
        z_d = -0.5
    elif face0 == "top":               # vent: riser on the BoP deck frame, flush at the envelope top
        s = (cq.Workplane("XY", origin=(BX0 + 15.0, 80.0, H - 40.0)).circle(od_s / 2)
             .circle(od_s / 2 - wl).extrude(40.5))   # riser roots into the BoP frame post
        z_d = H + 0.5
    else:
        z_d = float(r["height_mm"])
        x_d = layout_x[tag]
        if face0 == "inlet":           # stub from the -Y face inboard (rotated to +Y)
            s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(60.0)
                 .rotate((0, 0, 0), (1, 0, 0), -90).translate((x_d, 0.0, z_d)))
        else:                          # stub from the +Y face inboard (rotated to -Y)
            s = (cq.Workplane("XY").circle(od_s / 2).circle(od_s / 2 - wl).extrude(60.0)
                 .rotate((0, 0, 0), (1, 0, 0), 90).translate((x_d, W, z_d)))
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub" if r["size"] in DN_OD else "text_row", "dn": dnl,
                  "face": face0, "height_mm": r["height_mm"], "drawn_height_mm": z_d,
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "service": r["service"],
                  "note": "schedule datum drawn as issued (the elevations are the schedule "
                          "placeholders pending vessel design, duty section 4 - W12(4)); "
                          "atmospheric open-bore 316L tube flush at the skid face"}
parts.append(("nozzles", cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))))

# ---------------------------------------------------------------- export
solid = cq.Compound.makeCompound([wp.val() for _, wp in parts])
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(solid, str(out / (UNIT.lower() + ".step")), write_pcurves=False)
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
    "solids_note": "one compound of closed solids: plinth, stack-deck frame and enclosure "
    "posts, the cell bipolar-plate field (count from the graph node) between end plates with the copper bus pair, "
    "the power-electronics envelope, the BoP deck frame, the two DN150 separators on legs, "
    "the four deoxo/dryer bed tubes, the DI-water pump envelope, the H2 relief envelope and "
    "the nozzle stubs; every union partner overlaps volumetrically, so the mesh reads back "
    "closed and manifold",
    "stack_report": {
        "cells": CELLS, "active_mm": [float(SK["active_mm"][0]), float(SK["active_mm"][1])],
        "pitch_mm": PITCH, "area_m2_cell_summed": float(SK["area_m2_total"]),
        "i_stack_A": float(SK["i_stack_A"]), "v_stack_V": float(SK["v_stack_V"]),
        "p_dc_kW": float(SK["p_dc_kW"]), "j_A_cm2": float(SK["j_A_cm2"]),
        "v_cell": V_CELL, "rated_kw": float(DS["rated_kw"]), "window_h": float(DS["window_h"]),
        "basis": "cell count, active size, pitch and cell-summed area match the design block "
        "(specialty_sizing, A-M-459): the rated H2 books 26,590 Ah/kg, the field carries the "
        "2.304 m2 at the 1.8 A/cm2 / 1.85 V book; the measured polarisation curve replaces "
        "the operating point at the X-PAR-12 first article (W12(2))",
    },
    "bop_report": {
        "separators": "H2 and O2 gas-liquid separators DN150 x 400, one per side (316L)",
        "deoxo": DS["deoxo"], "dryer": DS["dryer"],
        "basis": "the node internals row drawn: PEM stack, H2 and O2 gas-liquid separators, "
        "deoxo on H2, dryer - the deoxo/dryer beds at the A-M-168 purifier classes applied "
        "on the skid, duplicated per the bed-count rule",
    },
    "skid_allowances": {"basis": DS["skid"]["basis"], "l_stack_mm": L_STACK,
                        "l_bop_mm": L_BOP, "w_mm": SKW, "h_mm": SKH},
    "placement_hold": "the placement seed block (1800 x 800 x 1600) under-books the A-M-279 "
    "skid (3367 x 1050 x 2200) - the named consequence for the placement lane (W12(1); "
    "nothing is resized)",
    "h2_dryer_chain_hold": "recorded, not fixed here: the H2_DRYER unit sizes on the HDR pool "
    "residual (2.750 kg/d per its design block, h2_purifier.py on IA-HDR-H2-02) while this "
    "electrolyser books 9.358 kg/d design / 8.715 kg/d edge - the mismatch persists after "
    "the F-26 corrections landed; the dryer book is the pool residual, not a mis-scale of "
    "this unit, and the sizing hold stays open for the H2-pool owner pass (W12(6))",
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": {}, "cadquery": cq.__version__,
}
v_cells = CELLS * AW * AW * 5.0 / 1e9
v_stack_hardware = (2 * 210 * 210 * 32 / 1e9) * 1.0
report["part_mass_kg"] = {
    "stack": round(v_cells * RHO_TI + v_stack_hardware * RHO_TI, 1),
    "separators_beds": round((math.pi * (SEP_DN ** 2 - (SEP_DN - 2 * T_D) ** 2) / 4 * SEP_H * 2
                              + 2 * math.pi * ((88.9 ** 2 - (88.9 - 2 * 5.49) ** 2) / 4) * (DEOX_L + DRY_L)
                              ) / 1e9 * RHO_316, 1),
    "frames_plinth": round((L * W * T_PLINTH + (L_STACK - 40 + L_BOP) * 60 * 0.5 + 4 * 60 * 60 * 900 / 1e3
                            + (L_STACK - 40) * (W - 40) * 40 / 1e3 + 2 * 30 * W * (H - Z0 - 60)) * RHO_CS / 1e9, 1),
    "purchased_envelopes": round(400 * (W - 80) * 900 / 1e9 * RHO_CS + 200 * 160 * 240 / 1e9 * RHO_CS, 1),
    "nozzles_relief": round((sum(p.val().Volume() for p in noz_pieces) + 60 * 40 * 160 / 1e9) * RHO_316 / 1e9, 1),
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
m = report["part_mass_kg"]
rows = [
    ["1", f"PEM stack: {CELLS} cells of {SK['active_mm'][0]:g} x {SK['active_mm'][1]:g} mm active "
          f"({float(SK['area_m2_total']):g} m2 cell-summed) at the 8 mm pitch between Ti end plates",
     CELLS, "Ti cell hardware, Ir/Ru anode / Pt cathode CCM, PTFE ionomer and seals (duty section 3)",
     m["stack"], "make", "the A-M-459 operating point (518.4 A at 148 V DC, 76.7 kW DC on the rated "
     "H2); the plates + lands draw, the MEAs are a loading row inside the pitch; the polarisation "
     "curve replaces the operating point at the first article (W12(2))"],
    ["2", "H2 and O2 gas-liquid separators DN150 x 400 with legs, one per side", 2, "316L (M1 family)",
     round(m["separators_beds"] * 0.6, 1), "make", "node internals row; design 990 kPa g (node design_kPa)"],
    ["3", f"Deoxo on H2: 2 beds DN80 x {DEOX_L:g} mm (Pd/Al2O3 class)", 2, "316L tube, catalyst purchased",
     round(m["separators_beds"] * 0.15, 1), "make", "GHSV 5000 1/h on the rated 17.4 Nm3/h (A-M-168 "
     "driver class, A-M-459 companion); beds duplicated"],
    ["4", f"Dryer on H2: 2 beds DN80 x {DRY_L:g} mm (4A/13X at margin 3, 250 C regen)", 2,
     "316L tube, sieve purchased", round(m["separators_beds"] * 0.25, 1), "make",
     f'{DS["dryer"]["sieve_kg"]:g} kg sieve on the {DS["dryer"]["water_kg_d"]:g} kg/d water book '
     "(A-M-168 class); beds duplicated"],
    ["5", "Power electronics enclosure + DI-water loop pump, envelopes and interfaces "
          "(purchased, plan rule 6)", 2, "purchased, 316L wetted class",
     m["purchased_envelopes"], "buy", "the rated-draw balance inside the 55 kWh/kg book (A-M-133)"],
    ["6", "Copper bus pair at the stack terminals (conductors are copper per duty section 3)", 1,
     "copper C110", 3.0, "make", "dry-side conductors; the A-CELL bus rule: POWER.md states no "
     "H2O_ELYZ bus section, the bus pair follows the terminal current"],
    ["7", f"Nozzle set per docs-authority/nozzles/{UNIT}.csv: {len(schedule)} rows (feed water in, H2 "
          "and O2 out, drain boss, vent riser; power and service terminals as text rows)", len(schedule),
     "316L tube", m["nozzles_relief"], "make", "schedule tags/faces/heights verbatim; the elevations "
     "are the schedule placeholders (duty section 4, W12(4))"],
    ["8", f"Skid frame and plinth {L:g} x {W:g} x {H:g} (stack deck {L_STACK:g} + gap 100 + BoP deck "
          f"{L_BOP:g}, the A-M-279 allowances)", 1, "carbon steel frame, painted", m["frames_plinth"], "make",
     "A-M-279 skid allowances at the rated kW; anchors in fasteners.csv"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 stud with 2 nuts (ISO 4014 / ISO 4032)", fasteners.grade_for("316L"), 8 * 2,
     "stack end-plate compression joints (4 per joint)",
     "stack compression hardware on the Ti cell pack; austenitic studs; torque pattern study, "
     "confirmed at the first article"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "decks": {"stack_mm": [0.0, L_STACK], "gap_mm": GAP, "bop_mm": [L_STACK + GAP, L]},
    "stack_z_mm": [Z_STACK0, Z_STACK1], "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": "the PEM skid as hardware (A-M-459 stack point + A-M-168 bed classes on "
    "the node internals row): stack deck, separator pair, deoxo and dryer beds, DI loop pump; "
    "the drawn cell field carries the booked 2.304 m2",
    "wetted": "Ti cell hardware and 316L BoP (duty section 3); no wetted copper",
    "internals_drawn": "cell field + separators + beds as solids; MEAs, catalyst and sieve "
    "loadings are BOM rows (W12(3))",
})
p["layout"] = {
    "frame": "origin at the envelope corner; stack deck 0..2042 (cells on the deck frame at "
             "z 300, graph cell count at the 8 mm pitch), gap 100, BoP deck 2142..3367 (separators and "
             "bed tubes on legs); plinth 0..100; decks top at the envelope height",
    "nozzle_spread": "side rows flush at the skid faces packed at an od + 8 pitch centred on "
                     "the skid (60 mm stubs); drain boss through the plinth at (500, 525); "
                     "vent riser on the BoP deck frame, flush at the envelope top; per-tag "
                     "positions in check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule")}), flush=True)
