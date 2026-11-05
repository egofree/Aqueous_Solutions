"""GAS_ATOMIZER manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down/guard frame pins the box so the
  X-PAR-04 envelope registry reads the build.
- Machine per the unit's own duty sheet and the AQS-MFG-010 tool row (Table 2.1,
  rev C metering split): close-coupled gas atomiser with Ar recirculation, nameplate
  5.5 kW; energy basis Ar GMR 2.5 at 30 bar, 0.246 kWh/kg x 3.56 kg/d + tundish
  1 kW x 1 h (A-M-177: GMR 2.5, 30 bar, compressor isothermal eta 0.6, 10 min
  pour, 1 kW tundish). Duty section 3: 316L where the stream is wet - the powder
  loop is dry, so CA 0 mm shop practice applies and the 316L row is carried for
  the melt-contact hardware.
- Close-coupled idiom: heated tundish (vessel + heater band, the 1 kW tundish
  duty) on a stand over the atomization tower, the close-coupled gas ring at the
  tower neck (GMR 2.5 study), powder-collection pot at the tower base, Ar
  recirculation loop (DN32 tube run) to the compressor envelope (30 bar class,
  A-M-177; the relief case is pending - unit task 07, W12), control cabinet as a
  purchased envelope. Tower, tundish and ring dimensions are study values sized
  to the 3.56 kg/d class (holds, WORK_ORDER W12); station arrangement is the
  layout choice (W12).
- A-MACH: hold-down frame is the guard; 8 slab anchors (fasteners.csv). Purchased
  items named with the rating from the node (5.5 kW nameplate; 1 kW tundish;
  30 bar compressor class).
- A-SC: the parts the on-site shop makes (tower, stands, loop runs, guard,
  connections) are flagged make with the AQS-BOM-SC-001 cross-reference; the
  compressor set and cabinet are buy rows.
- Nozzles: all 7 rows of docs-authority/nozzles/GAS_ATOMIZER.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the envelope
  faces (duty section 4: DN15, no flange class, atmospheric tube or hose). N1
  melt in on -Y at z 160 and N5 standby melt row (the IND_TO_ATOM study edge,
  "when powder required") beside it; N2 metal powder out, N6 powder stock out
  (solids row) and N7 off-spec remelt out (solids row) on +Y at z 600; N3 drain
  flush at the envelope bottom (50 datum); N4 vent flush at the envelope top
  (800 datum is the box top). Solids rows drawn DN15, bore not calculated
  (plan W4). The schedule rating column (Class 150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("GAS_ATOMIZER")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
TOW_OD, TOW_WALL = 300.0, 6.0                              # atomization tower (study, W12)
TOW_Z0, TOW_Z1 = 60.0, 560.0
TUN_OD, TUN_Z1 = 160.0, 700.0                              # tundish (study, W12)
TUN_Z0 = 580.0
RING_R = 60.0                                              # close-coupled gas ring radius (study)
POT_OD, POT_Z1 = 200.0, 200.0                              # powder-collection pot (study)
KW_NAME = 5.5                                              # nameplate, AQS-MFG-010 Table 2.1
KW_TUN = 1.0                                               # tundish duty, AQS-MFG-010
MAT = "316L"
CA = materials.ca_for(MAT)
RHO_CS = materials.density("CS")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
CX, CY = 300.0, W / 2
assert TOW_OD <= W - 2 * 40.0 + 40.0, "tower clears the hold-down posts"
assert TUN_Z0 >= TOW_Z1, "tundish stands over the tower"
assert TUN_Z1 + 60.0 <= H, "tundish + hatch stay under the top rails"
R_TOW_I = TOW_OD / 2 - TOW_WALL


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def ring_z(cx_, cy_, r_out, r_in, z0, z1):
    return (cq.Workplane("XY", origin=(cx_, cy_, z0)).circle(r_out).circle(r_in)
            .extrude(z1 - z0))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r).extrude(ln)


def dn_pipe(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def tube_z(dnl, length):
    return dn_pipe(dnl, length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down/guard frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- atomization tower + powder pot
tower = ring_z(CX, CY, TOW_OD / 2, R_TOW_I, TOW_Z0, TOW_Z1)
tower = tower.union(cq.Workplane("XY", origin=(CX, CY, TOW_Z0))
                    .circle(TOW_OD / 2).extrude(20.0))             # base head (laps plinth)
tower = tower.union(cq.Workplane("XY", origin=(CX, CY, TOW_Z1 - 20.0))
                    .circle(TOW_OD / 2).extrude(20.0))             # neck head
parts["tower"] = tower
parts["powder_pot"] = cq.Workplane("XY", origin=(CX, CY, 0)).circle(POT_OD / 2) \
    .extrude(POT_Z1)                                               # powder-collection pot

# ---------------------------------------------------------------- close-coupled gas ring (GMR 2.5 study)
# one concentric annulus band at the tower neck (the coil-band idiom: a compound of
# small rods leaves seam-rim degeneracies in the export)
parts["gas_ring"] = ring_z(CX, CY, RING_R + 14.0, RING_R - 6.0, TOW_Z1 - 44.0, TOW_Z1 - 16.0)

# ---------------------------------------------------------------- tundish + heater band + stand
tun = ring_z(CX, CY, TUN_OD / 2, TUN_OD / 2 - 6.0, TUN_Z0, TUN_Z1)
tun = tun.union(cq.Workplane("XY", origin=(CX, CY, TUN_Z1 - 14.0))
                .circle(TUN_OD / 2).extrude(14.0))                 # top head
parts["tundish"] = tun
parts["tundish_heater"] = ring_z(CX, CY, TUN_OD / 2 + 14.0, TUN_OD / 2, TUN_Z0, TUN_Z0 + 90.0)
stand = None
for sx in (CX - 90.0, CX + 90.0):
    s = box(sx - 12.0, CY - 12.0, TOW_Z1 - 20.0, 24.0, 24.0, TUN_Z0 - TOW_Z1 + 20.0)
    stand = s if stand is None else stand.union(s)
parts["tundish_stand"] = stand

# ---------------------------------------------------------------- Ar recirculation loop + compressor envelope
loop = dn_pipe("DN32", 300.0).rotate((0, 0, 0), (0, 1, 0), 90).translate(
    (CX, CY, TOW_Z1 - 100.0))                                      # tower top run to +X
loop = loop.union(dn_pipe("DN32", 260.0).translate((L - 320.0, CY, 120.0)))  # return run
loop = loop.union(dn_pipe("DN32", 420.0).translate((L - 80.0, CY - 21.2, 120.0)))
parts["ar_loop"] = loop
parts["compressor"] = box(700.0, 150.0, T_PLINTH, 260.0, 300.0, 480.0)
parts["control_cabinet"] = box(700.0, 460.0, T_PLINTH, 250.0, 90.0, 420.0)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def od_of(r):
    return dn.pipe_od(r["size"]) if r["size"].startswith("DN") else dn.pipe_od("DN15")


schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 300.0, (face, z, span)
    x = 200.0 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX, CY - 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (CX, CY), (L, W, H))
        note = "vent flush at the envelope top; the 800 datum is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": h if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- exports
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * RHO_CS / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "close-coupled gas atomiser with Ar recirculation per the duty "
                "sheet and the AQS-MFG-010 tool row (Table 2.1, rev C metering "
                f"split): atomization tower OD {TOW_OD:g} (wall {TOW_WALL:g}, "
                f"study) with powder-collection pot, close-coupled gas ring "
                f"(R {RING_R:g}, GMR 2.5 study) at the tower neck, heated tundish "
                f"OD {TUN_OD:g} on a stand over the tower (1 kW tundish duty), Ar "
                "recirculation loop (DN32) to the compressor envelope (30 bar "
                "class, A-M-177), control cabinet as a purchased envelope; "
                "hold-down frame is the guard (A-MACH practice)",
        "tool_row": "AQS-MFG-010 Table 2.1: Close-coupled gas atomiser with Ar "
                    "recirculation, nameplate 5.5 kW; energy basis Ar GMR 2.5 at "
                    "30 bar: 0.246 kWh/kg x 3.56 kg/d + tundish 1 kW x 1 h",
        "a177": "A-M-177: GMR 2.5, 30 bar, compressor isothermal eta 0.6, 10 min "
                "pour, 1 kW tundish",
        "material": "316L where the stream is wet (duty section 3); the powder "
                    "loop is dry - CA 0 mm shop practice; 316L carried for the "
                    "melt-contact hardware",
        "ca_mm": CA,
        "purchased": {"compressor": "Ar recirculation compressor, 30 bar class "
                                    "(A-M-177); purchased per plan rule 6",
                      "cabinet": "control cabinet (5.5 kW nameplate, AQS-MFG-010 "
                                 "Table 2.1); purchased per plan rule 6",
                      "tundish_heater": "1 kW tundish duty (AQS-MFG-010); "
                                        "purchased per plan rule 6"},
        "pressure_class": "the 30 bar Ar loop class is the A-M-177 study basis; "
                          "no design_kPa is stated on the node and the relief "
                          "case is pending (unit task 07) - the loop hardware is "
                          "drawn as envelopes, no flange drawn (W4 110 % rule)",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04); 8 slab anchors (fasteners.csv)",
        "study_dims": "tower, tundish, ring and pot dimensions are study values "
                      "sized to the 3.56 kg/d class (WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 melt in and N5 standby melt row (the IND_TO_ATOM "
                    "study edge, 'when powder required') on -Y at z 160; N2 metal "
                    "powder, N6 powder stock and N7 off-spec remelt (solids rows "
                    "drawn DN15, bore not calculated, plan W4) on +Y at z 600; "
                    "drain flush at the envelope bottom (50 datum); vent flush at "
                    "the envelope top (800 datum is the box top); the schedule "
                    "rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "frame pins the registry box (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", f"Atomization tower OD {TOW_OD:g} (wall {TOW_WALL:g}, study) with base/neck "
           "heads and powder-collection pot", 1, "316L (duty section 3, melt contact)",
     mass["tower"] + mass["powder_pot"], "make (AQS-BOM-SC-001)",
     "tower dimensions study (hold, WORK_ORDER W12); CA 0 mm - dry powder loop "
     "(AQS-STD-001)"],
    ["4", f"Close-coupled gas ring (R {RING_R:g}, 4 gas ports + annulus)", 1,
     "316L", mass["gas_ring"], "make (AQS-BOM-SC-001)",
     "GMR 2.5 at the A-M-177 study basis; ring geometry study (W12)"],
    ["5", f"Heated tundish OD {TUN_OD:g} on a stand with heater band", 1,
     "316L + heater band (1 kW duty, purchased per plan rule 6)",
     mass["tundish"] + mass["tundish_heater"] + mass["tundish_stand"],
     "make (AQS-BOM-SC-001)",
     "tundish 1 kW x 1 h (AQS-MFG-010 Table 2.1; A-M-177); the heater set is the "
     "buy element"],
    ["6", "Ar recirculation loop, DN32 tube runs", 1, "316L tube",
     mass["ar_loop"], "make (AQS-BOM-SC-001)",
     "30 bar Ar class per A-M-177; loop runs are layout choice (W12); no flange "
     "(W4 110 % rule - no node design_kPa); relief case pending (unit task 07)"],
    ["7", "Ar compressor set (purchased, envelope and interface)", 1,
     "purchased compressor (envelope)", mass["compressor"], "buy",
     "30 bar class, isothermal eta 0.6 (A-M-177); purchased per plan rule 6; "
     "mass a table-density placeholder until the maker TDS quotes (W12)"],
    ["8", "Control cabinet (purchased, envelope and interface)", 1,
     "purchased cabinet (envelope)", mass["control_cabinet"], "buy",
     "nameplate 5.5 kW (AQS-MFG-010 Table 2.1; node stamp); purchased per plan "
     "rule 6"],
    ["9", "Nozzle set per docs-authority/nozzles/GAS_ATOMIZER.csv: 4 DN15 stubs "
           "and 3 solids rows drawn DN15 bore not calculated", len(schedule),
     "316L tube", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M10 tower-flange bolt + nut", fasteners.grade_for("316L"), 8,
     "tower neck and pot flanges (count from the model)",
     "A4-70 on 316L per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "tower": {"od_mm": TOW_OD, "wall_mm": TOW_WALL, "z_mm": [TOW_Z0, TOW_Z1],
              "pos_mm": [CX, CY]},
    "gas_ring": {"r_mm": RING_R, "gmr": 2.5},
    "tundish": {"od_mm": TUN_OD, "z_mm": [TUN_Z0, TUN_Z1]},
    "ar_loop_dn": "DN32",
    "compressor_mm": [700.0, 150.0, 260.0, 300.0, 480.0],
}
p["design"] = {
    "service": "GAS_ATOMIZER: melt atomised to metal powder (S60); off-spec powder "
               "returns to MET_MELT (IA-ATOM-REMELT) and the IND_TO_ATOM standby "
               "row stays at zero on the design day (duty sections 1 and 4)",
    "tool_row": "AQS-MFG-010 Table 2.1: close-coupled gas atomiser with Ar "
                "recirculation, nameplate 5.5 kW; GMR 2.5 at 30 bar + tundish "
                "1 kW (A-M-177)",
    "material": "316L where the stream is wet (duty section 3); dry powder loop",
    "ca_mm": CA,
    "material_basis": "duty section 3; CA 0 mm shop rule (AQS-STD-001)",
    "purchased": "Ar compressor set (30 bar class), control cabinet (5.5 kW "
                 "nameplate), tundish heater set - plan rule 6 envelopes with the "
                 "node ratings",
    "pressure_note": "no design_kPa on the node; the 30 bar loop class is the "
                     "A-M-177 study basis and the relief case is pending (unit "
                     "task 07)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; tower centre x 300 on the plinth, "
             "tundish on a stand over the tower neck, gas ring at the tower neck, "
             "Ar loop DN32 to the compressor bay x 700..960, control cabinet "
             "beside it; hold-down posts at the envelope corners",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1/N5 pack one row "
                     "on -Y at z 160; N2/N6/N7 on +Y at z 600; drain at the "
                     "plinth centre, vent on the tower axis; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
