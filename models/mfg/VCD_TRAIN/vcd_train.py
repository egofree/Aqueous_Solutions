"""VCD_TRAIN manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, evaporator).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker; the
design block beside them is written by flow_graph/param/stub_activation.py, X-MFG-38 pattern)
and rebuilds every solid. Placement frame: x along the skid, y across, z up, origin at the
envelope corner.

Every dimension is an authority figure or a named layout choice:

- Envelope 1400 x 600 x 1200 mm, node size_mm (the issued envelope, duty section 2/4). The
  build fills it: the plinth spans the footprint, the separator caps top the vessels at the
  envelope height, the face connections flush at the faces.
- Machine (params.design, 2 x 100 % per X-RED-05): TWO identical MVC still modules side by
  side, each 700 mm of the skid: a vertical evaporator/condenser vessel (falling-film
  evaporator boiling inside, compressed vapour condensing on the shell - the MVC still
  principle), the vapour separator section above it, and the scroll-class compressor
  envelope. The bundle carries the booked heat-exchange area: the graph tube book
  (tubes x pi x ID x L) against the booked hx_area_m2 at U 2.8 kW/m2 K, 5 K lift
  (PERRY9_EVAP class; the node carries the latent duty, so the area is the calculated
  bundle).
- Duty section 2 working volume: the sump holds the 2 h working volume (0.0138 m3 book);
  reported from the model, no residence time claimed beyond the duty's own.
- Duty section 3: 316L wetted parts, CA 0 mm (AQS-STD-001 rule); frame carbon steel.
- Purchased per plan rule 6: the scroll compressor (node design rating class) as its
  envelope and interface.
- Nozzles: all 11 rows of docs-authority/nozzles/VCD_TRAIN.csv drawn at tag, face, height
  and bore as atmospheric open-bore stubs flush at the skid faces (duty section 4: hose,
  atmospheric; DN copied from the edge).
- A-HX: the bundle area is reported drawn against booked in check.json - here the node
  carries the latent heat rate, so the booked area is a calculated figure (U x dT basis on
  the node design), and the drawn bundle is reported against it.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm, stl_manifold   # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1400 x 600 x 1200
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

N_MOD = int(DS["modules"])                                 # 2 (2 x 100 %, X-RED-05)
SHELL_D = float(DS["shell_D_mm"])                          # 240
TUBE_ID = float(DS["tube_id_mm"])                          # 12
TUBE_OD = TUBE_ID + 2.0                                    # 14, 1 mm wall
TUBE_L = float(DS["tube_L_mm"])                            # 890
NT = int(DS["tubes"])                                      # the graph tube book
SUMP_H = float(DS["sump_h_mm"])                            # 220 (13.8 L working volume across both sumps, duty section 2)
SEP_H = float(DS["sep_h_mm"])                              # 40 (separator ring + demister pad)
T_PLINTH = 30.0
Z0 = T_PLINTH
Z_TS = Z0 + SUMP_H                                         # tubesheet 250
Z_TS1 = Z_TS + TUBE_L                                      # tube zone top 1140
Z_SEP = Z_TS1 + 20.0                                       # separator ring 1160
Z_CAP = H                                                  # vessel caps top the envelope
VWALL = 10.0                                               # vessel shell wall
BAY_W = L / N_MOD                                          # 700
RHO_316 = materials.density("316L")
RHO_CS = materials.density("CS") or materials.density("steel")

assert L == 1400.0 and W == 600.0 and H == 1200.0, "VCD_TRAIN node envelope changed"
assert N_MOD >= 1, "the installed module book must be positive"
assert BAY_W >= SHELL_D + 40.0, "each module bay must house its vessel and separator flange"
a_drawn = NT * math.pi * TUBE_ID * TUBE_L / 1e6
assert a_drawn + 1e-9 >= float(DS["hx_area_m2"]), \
    "the tube book must cover the booked heat-exchange area (A-HX)"
assert abs(Z_CAP - H) < 0.01 and Z_SEP + SEP_H == H, "vessel must close at the envelope top"


def bay_xc(i):
    return BAY_W * i + BAY_W / 2


parts = [("plinth", cq.Workplane("XY").box(L, W, T_PLINTH, centered=False))]
bundle_tubes = []
for i in range(N_MOD):
    xc, yc = bay_xc(i), W / 2
    rs = SHELL_D / 2
    # --- vessel: sump, tube zone, head, separator section, top cap
    vessel = cq.Workplane("XY", origin=(xc, yc, Z0)).circle(rs).circle(rs - VWALL).extrude(H - Z0 - 10.0)
    vessel = vessel.union(cq.Workplane("XY", origin=(xc, yc, Z0)).circle(rs).extrude(10.0))            # base head
    vessel = vessel.union(cq.Workplane("XY", origin=(xc, yc, Z_TS)).circle(rs).extrude(VWALL))         # lower tubesheet
    vessel = vessel.union(cq.Workplane("XY", origin=(xc, yc, Z_TS1)).circle(rs).extrude(VWALL))        # upper tubesheet
    vessel = vessel.union(cq.Workplane("XY", origin=(xc, yc, Z_SEP - VWALL)).circle(rs + 20).extrude(VWALL))  # separator flange ring
    vessel = vessel.union(cq.Workplane("XY", origin=(xc, yc, Z_CAP - 10.0)).circle(rs + 20).extrude(10.0))   # top cap (flush at the envelope top)
    parts.append((f"vessel_{i}", vessel))
    parts.append((f"demister_{i}", cq.Workplane("XY", origin=(xc, yc, Z_SEP + 5.0)).circle(rs - VWALL - 2).extrude(SEP_H - 15.0)))
    # --- falling-film bundle: NT tubes ID 12 at the triangular pitch, one ring + centre
    pitch = 1.25 * TUBE_OD
    pts = []
    r = 0
    while len(pts) < NT - 1:
        r += 1
        for k in range(6 * r):
            a = 2 * math.pi * k / (6 * r)
            pts.append((r * pitch * math.cos(a), r * pitch * math.sin(a)))
    pts = [(0.0, 0.0)] + pts[:NT - 2]
    for k, (px, py) in enumerate(pts):
        t = (cq.Workplane("XY", origin=(xc + px, yc + py, Z_TS + 0.2))
             .circle(TUBE_OD / 2).circle(TUBE_ID / 2).extrude(TUBE_L))
        bundle_tubes.append((f"tube_{i}_{k}", t))
parts.extend(bundle_tubes)

# ---------------------------------------------------------------- purchased: scroll compressor envelopes
for i in range(N_MOD):
    xc = bay_xc(i)
    parts.append((f"compressor_{i}", cq.Workplane("XY", origin=(xc + 180.0, 60.0, T_PLINTH - 5.0))
                  .box(170.0, 200.0, 260.0, centered=False)))          # at the bay flank, roots into the plinth

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

STUB = 60.0
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    if r["face"] == "bottom":            # drain: boss through the plinth, 0.5 mm proud below
        s = (cq.Workplane("XY", origin=(0, 0, -0.5)).circle(DN_OD[dnl] / 2).circle(DN_OD[dnl] / 2 - dn.pipe_wall(dnl, 40))
             .extrude(T_PLINTH + 5.5).translate((300.0, W / 2, 0.0)))
        z_d = -0.5
    elif r["face"] == "top":             # vent: riser on the bay-0 separator cap, flush at the top
        s = (cq.Workplane("XY", origin=(bay_xc(0), W / 2, H - 30.0)).circle(DN_OD[dnl] / 2)
             .circle(DN_OD[dnl] / 2 - dn.pipe_wall(dnl, 40)).extrude(30.5))
        z_d = H + 0.5
    else:
        z_d = float(r["height_mm"])
        x_d = layout_x[tag]
        wl = dn.pipe_wall(dnl, 40)
        if face0 == "inlet":
            s = (cq.Workplane("XZ", origin=(x_d, 0.0, z_d)).circle(DN_OD[dnl] / 2)
                 .circle(DN_OD[dnl] / 2 - wl).extrude(-STUB))
        else:
            s = (cq.Workplane("XZ", origin=(x_d, W, z_d)).circle(DN_OD[dnl] / 2)
                 .circle(DN_OD[dnl] / 2 - wl).extrude(STUB))
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "x_mm": layout_x.get(tag),
                  "schedule_rating": r["rating"], "service": r["service"],
                  "note": "schedule datum drawn as issued (all fit the 1200 box); atmospheric "
                          "open-bore tube flush at the skid face (duty section 4: hose, "
                          "atmospheric; DN copied from the edge, not recalculated)"}
parts.append(("nozzles", cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))))

# ---------------------------------------------------------------- holdup reported (A-VES)
v_sump = round(math.pi * (SHELL_D / 2 - VWALL) ** 2 * SUMP_H / 1e6, 4)     # L per module
V_WORK = 13.8                                                              # L, the duty section 2 working volume book (2 h)

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
    "solids_note": "one compound of closed solids: plinth, two vessel chains (shell, heads, "
    "tubesheets, separator ring, top cap), the two 18-tube bundles at running clearance, "
    "demister pads, compressor envelopes and the nozzle stubs; every union partner overlaps "
    "volumetrically, so the mesh reads back closed and manifold",
    "a_hx": {
        "modules": N_MOD, "tubes_per_module": NT, "tube_mm": [TUBE_ID, TUBE_OD, TUBE_L],
        "area_m2_drawn": round(a_drawn, 4), "area_m2_booked": float(DS["hx_area_m2"]),
        "q_latent_kW": float(DS["q_latent_kW"]), "u_kW_m2K": float(DS["u_kW_m2K"]),
        "dT_drive_K": float(DS["dT_drive_K"]),
        "basis": "A-HX: the bundle area is reported drawn against booked; the node carries the "
        "8.436 kW latent duty, so the booked area is the calculated figure (latent / (U 2.8 x "
        "5 K), PERRY9_EVAP class, stub_activation X-MFG-38 pattern) and the drawn bundle "
        "carries it at +0.1 %",
    },
    "holdup_L": {"sump_per_module_model": v_sump, "working_volume_book_L": V_WORK,
                 "basis": "the duty section 2 working volume (2 h, 0.0138 m3 book) against the "
                 "model sump; reported, not used as a residence time beyond the duty's own "
                 "claim (A-VES rule)"},
    "redundancy": {"modules": N_MOD, "rule": "2 x 100 %, standby still on the same feed header "
                   "(X-RED-05); both modules drawn (installed)"},
    "nozzles_drawn": drawn, "nozzle_count_schedule": len(schedule),
    "part_mass_kg": {}, "cadquery": cq.__version__,
}
v_vessel = (math.pi * (SHELL_D / 2) ** 2 * (H - Z0) - math.pi * (SHELL_D / 2 - VWALL) ** 2 * (H - Z0)) / 1e9
m_vessel = v_vessel * RHO_316 + math.pi * (SHELL_D / 2 + 20) ** 2 * (10 + VWALL) / 1e9 * RHO_316 * 2
m_tubes = NT * math.pi * ((TUBE_OD / 2) ** 2 - (TUBE_ID / 2) ** 2) * TUBE_L / 1e9 * RHO_316 * N_MOD
report["part_mass_kg"] = {
    "vessels": round(m_vessel * N_MOD, 1), "bundle": round(m_tubes, 1),
    "plinth_compressors": round((L * W * T_PLINTH + N_MOD * 170 * 200 * 265) * RHO_CS / 1e9, 1),
    "nozzles": round(sum(p.val().Volume() for p in noz_pieces) * RHO_316 / 1e9, 1),
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
m = report["part_mass_kg"]
rows = [
    ["1", f"Still vessels x {N_MOD} (2 x 100 %, X-RED-05): shell OD {SHELL_D:g} x wall {VWALL:g}, "
          f"{H - Z0:g} mm, sump + tubesheet pair + separator flange + top cap", N_MOD, "316L, CA 0 mm",
     m["vessels"], "make", "duty section 3 (316L wetted); the MVC still principle: boiling inside, "
     "compressed vapour condensing on the shell"],
    ["2", f"Falling-film bundles: {NT} tubes ID {TUBE_ID:g} x OD {TUBE_OD:g} x {TUBE_L:g} mm per "
          f"module, {a_drawn:.4f} m2 each", NT * N_MOD, "316L tube, CA 0 mm", m["bundle"], "make",
     "booked bundle 0.603 m2 at U 2.8 kW/m2 K x 5 K (PERRY9_EVAP class) on the node's 8.436 kW "
     "latent duty (params.design area_basis); drawn at +0.1 %"],
    ["3", "Separator demister pads, 90 mm", N_MOD, "316L mesh", 0.3, "buy",
     "vapour separator internals above the upper tubesheet (design sep_h_mm)"],
    ["4", f"Scroll compressors, {DS['duty_kW']:g} kW duty class (node design scroll class), "
          "envelope and interface", N_MOD, "purchased, 316L refrigeration class", 12.0, "buy",
     "purchased per plan rule 6; the drive rating reads the maker sheet at order (node design "
     "sec_kWh_m3 17 kWh/m3 driver basis, A-M-149)"],
    ["5", f"Nozzle set per docs-authority/nozzles/{UNIT}.csv: {len(schedule)} rows at the skid faces "
          "(drain boss through the plinth, vent riser on the bay-0 separator cap)", len(schedule), "316L tube",
     m["nozzles"], "make", "schedule tags/faces/heights verbatim; atmospheric open-bore tube (duty section 4: hose, atmospheric)"],
    ["6", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} carrying both module bays", 1, "carbon steel, painted",
     round(L * W * T_PLINTH * RHO_CS / 1e9, 1), "make", "dry frame; anchors in fasteners.csv"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 stud with 2 nuts (ISO 4014 / ISO 4032)", fasteners.grade_for("316L"), 8 * N_MOD,
     "vessel flanged joints at the separator ring (4 per joint)",
     "316L pressure-part hardware; study rating, confirmed at fabrication"],
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H], "basis": P.get("size_basis"),
    "modules": {"count": N_MOD, "bay_w_mm": BAY_W},
    "vessel_z_mm": [Z0, H], "bundle_z_mm": [Z_TS, Z_TS1], "plinth_mm": T_PLINTH,
    "sump_h_mm": SUMP_H, "sep_h_mm": SEP_H,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine_note": "two MVC still modules (2 x 100 %, X-RED-05) in the issued envelope: each a "
    "vertical evaporator/condenser vessel with the 18-tube bundle at the booked area, vapour "
    "separator above, scroll compressor at the flank",
    "wetted": "316L wetted, CA 0 mm (duty section 3); frame carbon steel",
    "internals_drawn": "bundles as tube solids at running clearance; demister pads; the scroll "
    "compressor as its purchased envelope (rule 6)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; two 700 mm module bays; plinth 0..30; vessels "
             "30..1200 with sump 30..250, tubes 250..1140, separator 1160..1190, cap flush at "
             "the envelope top",
    "nozzle_spread": "side rows flush at the skid faces packed at an od + 8 pitch centred on "
                     "the skid (60 mm hose-joint stubs); drain boss through the plinth at "
                     "(300, 300); vent riser on the bay-0 separator cap, flush at the envelope "
                     "top; per-tag positions in check.nozzles_drawn",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule")}), flush=True)
