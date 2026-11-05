"""MET_SYN manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1500 mm, y along 1000 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1500 x 1000 x 1800 mm, node size_mm ("bench fume-hood train: glass-lined
  reactor column (2 L working volume), reagent feed tanks, Hastelloy C crystalliser;
  the 9 g/d DL-Met duty sets nothing larger (A-M-416 route A; X-UI-002)"). The build
  fills it; a four-post hold-down frame pins the registry box (X-PAR-04).
- Train per the node sizing/design blocks and duty section 3: borosilicate glass-lined
  reactor column (2 L working volume) with a heating-jacket band, PTFE-lined transfer
  lines, SS304 reagent feed tanks (the schedule names CH3OH, H2S and NH3 feeds), and
  a Hastelloy C crystalliser (duty section 3: the product-quality bottleneck,
  X-UI-002). The connected set - heating jacket, stirrer and metering pumps - is
  0.2 kW on the node; the set is drawn as purchased-class envelopes per plan rule 6
  with the shared node rating named (no per-item figure is invented). Column, tank
  and crystalliser shell dimensions are study values sized to the 2 L working volume
  and the bench class (holds, WORK_ORDER W12).
- Chemistry chain (node design block, carried as text): step 1 CH3OH + H2S -> CH3SH
  (K2O/Al2O3, 350 C); step 2 CH3SH + acrolein -> MMP; step 3 Strecker (NH3 + HCN) to
  DL-Met. The column is drawn once; the three steps run through it in campaign
  sequence (the node names the sequence, not separate hardware).
- A-MACH practice: the bench frame is the hold-down/guard structure; 8 slab anchors
  in fasteners.csv. Purchased items named with the rating from the node (plan rule 6).
- Nozzles: all 6 rows of docs-authority/nozzles/MET_SYN.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: Class 150 rows, atmospheric tube or hose; no process pressure is
  stated so no flange is drawn - plan W4 110 % rule). N1-N3 reagent feeds on -Y at
  z 160 (under the bench deck, where the metering pumps sit); N4 DL-Met crystals out
  on +Y at z 600 (the crystalliser discharge point - a solids row in service; drawn
  DN15, bore not calculated, plan W4); N5 drain flush at the envelope bottom (50
  datum); N6 vent flush at the envelope top (the 800 datum predates the 1800 box -
  hold, WORK_ORDER W12). The schedule rating column (Class 150) carried verbatim.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("MET_SYN")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1500 x 1000 x 1800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_DECK = 20.0                                              # bench deck plate on the plinth
POST = 40.0                                                # hold-down/guard frame section
DECK_Z = 800.0                                             # deck top; hood 800..1800 (layout, W12)
MAT_STRUCT = "316L"                                        # bench/hood structure, wet-bench
# class under HCN/acrolein fume (REE_RECOVER idiom; layout choice, W12)
CA = materials.ca_for(MAT_STRUCT)                          # 0.0, AQS-STD-001
RHO = materials.density(MAT_STRUCT)
RHO_GLASS = materials.density("borosilicate")              # 2230, lib table
RHO_SS304 = materials.density("304")                       # 8000, lib table
RHO_HAST = 8900.0          # Hastelloy C-class density, published band midpoint; the
# crystalliser is a buy-row envelope - the maker TDS governs at order (W12)
RHO_PTFE = 2200.0          # PTFE lines, published PTFE class (study; buy consumable)

# ---------------------------------------------------------------- authority dimensions
COL_OD, COL_H = 150.0, 600.0            # glass-lined reactor column (study, W12): the
V_WORK_L = 2.0                          # 2 L working volume (node sizing) fits with margin
# 2 L inside a 150 bore x 500 liquid height at ~30 % freeboard
COL_X, COL_Y = 400.0, 500.0
JACK_OD, JACK_H = 190.0, 300.0          # heating-jacket band over the lower column (set)
TANK_OD, TANK_H = 200.0, 300.0          # SS304 reagent feed tanks (study, W12)
TANK_YS = (300.0, 550.0, 800.0)         # CH3OH / H2S / NH3 rows per the schedule feeds
TANK_X = 700.0
CRYS_OD, CRYS_H = 220.0, 350.0          # Hastelloy C crystalliser (study, W12)
CRYS_X, CRYS_Y = 1150.0, 500.0
KW_SET = 0.2                            # connected set: jacket + stirrer + pumps (node)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert math.pi / 4 * 60.0 ** 2 * 500.0 * 1e-3 >= V_WORK_L, "column covers the 2 L duty"
assert DECK_Z + 20.0 + COL_H + 120.0 <= H, "column + motor stay under the hood top"
assert TANK_X + TANK_OD / 2 < CRYS_X - CRYS_OD / 2, "tank row clears the crystalliser"

DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, T_DECK)


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def vtube(od, x, y, z0, z1):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0)


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth, deck, hold-down frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
parts["deck"] = box(*DECK)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- fume hood shell over the bench
# walls lap the posts and the deck volumetrically (2 mm): face-to-face junctions
# leave the export non-manifold (the farm_hab.py lesson)
Z_HOOD0 = DECK_Z + T_DECK - 2.0
hood = box(0.0, POST - 2.0, Z_HOOD0, L, 34.0, H - POST - 15.0 - Z_HOOD0)
hood = hood.union(box(0.0, W - POST - 32.0, Z_HOOD0, L, 34.0, H - POST - 15.0 - Z_HOOD0))
hood = hood.union(box(0.0, POST - 2.0, Z_HOOD0, 34.0, W - 2 * POST + 4.0,
                      H - POST - 15.0 - Z_HOOD0))
hood = hood.union(box(0.0, 0.0, H - POST - 30.0, L, W, 30.0))
parts["hood"] = hood

# ---------------------------------------------------------------- reactor column (glass-lined) + jacket
col = vtube(COL_OD, COL_X, COL_Y, DECK_Z + T_DECK, DECK_Z + T_DECK + COL_H)
col = col.union(vtube(COL_OD, COL_X, COL_Y, DECK_Z + T_DECK, DECK_Z + T_DECK + 10.0))  # base head
col = col.union(vtube(COL_OD, COL_X, COL_Y, DECK_Z + T_DECK + COL_H - 10.0,
                      DECK_Z + T_DECK + COL_H))                                        # top head
parts["column"] = col
parts["glass_liner"] = vtube(COL_OD - 12.0, COL_X, COL_Y, DECK_Z + T_DECK + 10.0,
                             DECK_Z + T_DECK + COL_H - 10.0)   # borosilicate glass lining
parts["jacket"] = vtube(JACK_OD, COL_X, COL_Y, DECK_Z + T_DECK,
                        DECK_Z + T_DECK + JACK_H)              # heating-jacket band

# ---------------------------------------------------------------- stirrer drive (purchased envelope)
parts["stirrer"] = box(COL_X - 60.0, COL_Y - 60.0, DECK_Z + T_DECK + COL_H,
                       120.0, 120.0, 90.0)

# ---------------------------------------------------------------- reagent feed tanks (SS304) + metering pumps
tanks = None
for ty in TANK_YS:
    t = vtube(TANK_OD, TANK_X, ty, DECK_Z + T_DECK, DECK_Z + T_DECK + TANK_H)
    t = t.union(vtube(TANK_OD, TANK_X, ty, DECK_Z + T_DECK, DECK_Z + T_DECK + 8.0))
    t = t.union(vtube(TANK_OD, TANK_X, ty, DECK_Z + T_DECK + TANK_H - 8.0,
                      DECK_Z + T_DECK + TANK_H))
    tanks = t if tanks is None else tanks.union(t)
parts["feed_tanks"] = tanks
pumps = None
for ty in TANK_YS:
    p = box(TANK_X - 40.0, ty - 60.0, DECK_Z + T_DECK, 80.0, 120.0, 90.0)
    pumps = p if pumps is None else pumps.union(p)
parts["metering_pumps"] = pumps

# ---------------------------------------------------------------- Hastelloy C crystalliser
cr = vtube(CRYS_OD, CRYS_X, CRYS_Y, DECK_Z + T_DECK, DECK_Z + T_DECK + CRYS_H)
cr = cr.union(vtube(CRYS_OD, CRYS_X, CRYS_Y, DECK_Z + T_DECK, DECK_Z + T_DECK + 10.0))
cr = cr.union(vtube(CRYS_OD, CRYS_X, CRYS_Y, DECK_Z + T_DECK + CRYS_H - 10.0,
                    DECK_Z + T_DECK + CRYS_H))
parts["crystalliser"] = cr

# ---------------------------------------------------------------- PTFE-lined transfer lines (tube runs)
# one horizontal run per joint, each end embedded volumetrically in its vessel wall
# (face-to-face or rim-coincident junctions leave single bad edges in the export)
line = cq.Workplane("XY", origin=(COL_X + 55.0, COL_Y, DECK_Z + T_DECK + 386.0))
line = line.box(CRYS_X - CRYS_OD / 2 + 6.0 - (COL_X + 55.0), 12.0, 12.0, centered=False)
line = line.union(vtube(12.0, CRYS_X, CRYS_Y, DECK_Z + T_DECK + CRYS_H - 6.0,
                        DECK_Z + T_DECK + CRYS_H + 40.0))   # vent stub laps the top head
for ty in TANK_YS:                                          # pump discharge risers to the column
    line = line.union(cq.Workplane("XY", origin=(TANK_X, ty, DECK_Z + T_DECK))
                      .box(12.0, 12.0, 80.0, centered=False))
parts["ptfe_lines"] = line

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
    x = 150.0 - span / 2
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
    if r["face"] == "bottom":                             # N5: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N6: 800 datum predates the 1800 box
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = ("vent flush at the envelope top; schedule datum 800 mm predates the "
                "1800 box - named hold, WORK_ORDER W12")
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
RHO_OF = {"plinth": RHO, "deck": RHO, "frame": RHO, "hood": RHO,
          "column": RHO_GLASS, "glass_liner": RHO_GLASS,
          "feed_tanks": RHO_SS304, "crystalliser": RHO_HAST, "ptfe_lines": RHO_PTFE}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "bench fume-hood synthesis train per the node sizing/design blocks "
                "and duty section 3: borosilicate glass-lined reactor column "
                f"(OD {COL_OD:g} x {COL_H:g}, 2 L working volume, node sizing "
                "throughput_g_d 9 at the bench class) with heating-jacket band "
                f"({JACK_OD:g} x {JACK_H:g}); 3 SS304 reagent feed tanks "
                f"(OD {TANK_OD:g} x {TANK_H:g}, CH3OH / H2S / NH3 per the schedule "
                f"feeds); Hastelloy C crystalliser (OD {CRYS_OD:g} x {CRYS_H:g}, "
                "duty section 3: the product-quality bottleneck, X-UI-002); "
                "PTFE-lined transfer lines; metering pumps and stirrer drive as "
                "purchased-class envelopes",
        "chemistry": DS.get("chemistry"),
        "connected_kw": {"value": KW_SET,
                         "basis": "node continuous_kw 0.2 kW: heating jacket + "
                                  "stirrer + metering pumps as one connected set; "
                                  "no per-item figure is stated or invented"},
        "work_volume_L": V_WORK_L,
        "study_dims": "column/tank/crystalliser shell dimensions are study values "
                      "sized to the 2 L duty and the bench class (WORK_ORDER W12)",
        "structure": "316L bench frame, deck and fume hood (wet-bench class under "
                     "HCN/acrolein fume; REE_RECOVER idiom; layout choice, W12)",
        "purchased": "stirrer drive, metering pumps and the heating jacket are "
                     "purchased-class envelopes per plan rule 6 (connected set "
                     "0.2 kW from the node); the Hastelloy C crystalliser is a "
                     "buy-row envelope",
        "guard": "four-post hold-down/guard frame (40 x 40 posts, top rails) pins "
                 "the registry box (X-PAR-04); 8 slab anchors (fasteners.csv)",
        "material": "borosilicate glass-lined column, PTFE-lined transfer lines, "
                    "SS304 feed tanks, Hastelloy C crystalliser (duty section 3, "
                    "X-MAT-22)", "ca_mm": CA,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: Class 150 rows, atmospheric tube or hose); "
                    "N1-N3 reagent feeds on -Y at z 160 under the bench deck; N4 "
                    "DL-Met crystals (solids service) on +Y at z 600 drawn DN15, "
                    "bore not calculated (plan W4); drain flush at the envelope "
                    "bottom (50 datum); vent flush at the envelope top (the 800 "
                    "datum predates the 1800 box - hold, WORK_ORDER W12); no flange "
                    "drawn (W4 110 % rule - no process pressure stated); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Bench deck {DECK[3]:g} x {DECK[4]:g} x {T_DECK:g} over the plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["deck"] + mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; the bench the train mounts on"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "frame pins the registry box (X-PAR-04); anchors in fasteners.csv"],
    ["3", "Fume-hood shell: back/side walls and top over the bench (wet-bench "
           "class, HCN/acrolein fume)", 1, "316L (layout choice, hold WORK_ORDER W12)",
     mass["hood"], "make (AQS-BOM-SC-001)",
     "bench fume-hood train per the node size_note; REE_RECOVER fume-hood class idiom"],
    ["4", f"Glass-lined reactor column OD {COL_OD:g} x {COL_H:g} with borosilicate "
           f"lining and base/top heads (2 L working volume, node sizing)", 1,
     "borosilicate glass lining on 316L shell (duty section 3)", mass["column"] + mass["glass_liner"],
     "make (AQS-BOM-SC-001)",
     "node sizing throughput_g_d 9 / power_kW 0.2; shell dimensions study (W12); "
     "CA 0 mm (AQS-STD-001)"],
    ["5", f"Heating-jacket band {JACK_OD:g} x {JACK_H:g} on the column", 1,
     "316L jacket (purchased-class envelope)", mass["jacket"], "buy",
     "connected set 0.2 kW (node): jacket + stirrer + metering pumps; purchased per "
     "plan rule 6, the set rating from the node"],
    ["6", "Stirrer drive on the column head (purchased-class envelope)", 1,
     "purchased drive (envelope)", mass["stirrer"], "buy",
     "connected set 0.2 kW (node); purchased per plan rule 6"],
    ["7", f"Reagent feed tanks OD {TANK_OD:g} x {TANK_H:g}, 3 off (CH3OH / H2S / NH3 "
           "per the schedule feeds)", 3, "SS304 (duty section 3)", mass["feed_tanks"],
     "make (AQS-BOM-SC-001)",
     "node design precursor chain; shell dimensions study (W12); CA 0 mm"],
    ["8", f"Hastelloy C crystalliser OD {CRYS_OD:g} x {CRYS_H:g} (duty section 3: the "
           "product-quality bottleneck, X-UI-002)", 1,
     "Hastelloy C (buy-row envelope; maker TDS mass governs)", mass["crystalliser"], "buy",
     "duty section 3 selection (X-MAT-22); drawn as its envelope per plan rule 6; "
     "density is the published Hastelloy C class midpoint (study)"],
    ["9", "PTFE-lined transfer lines: column-to-crystalliser run, pump discharge "
           "risers, crystalliser vent stub", 1, "PTFE (duty section 3)", mass["ptfe_lines"],
     "make (AQS-BOM-SC-001)",
     "duty section 3: PTFE-lined transfer for the HCN/acrolein/methanethiol class; "
     "tubing OD is a study proportion (W12)"],
    ["10", "Metering pump set on the tank bases (purchased-class envelopes)", 3,
     "purchased pumps (envelopes)", mass["metering_pumps"], "buy",
     "connected set 0.2 kW (node); purchased per plan rule 6"],
    ["11", "Nozzle set per docs-authority/nozzles/MET_SYN.csv: 3 reagent feed stubs "
            "(DN15), product/drain/vent stubs (DN15)", len(schedule), "316L tube",
     mass["nozzles"], "make (AQS-BOM-SC-001)",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4; the N4 "
     "crystals row drawn DN15, bore not calculated (plan W4)"],
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
    [None, "M8 hold-down bolt + nut", fasteners.grade_for("316L"), 8,
     "column, tanks and crystalliser to the deck, 2 per vessel (count from the model)",
     "A4-70 on 316L per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "deck_z_mm": DECK_Z,
    "hood_z_mm": [DECK_Z + T_DECK, H],
    "column": {"od_mm": COL_OD, "h_mm": COL_H, "pos_mm": [COL_X, COL_Y],
               "jacket_od_mm": JACK_OD, "jacket_h_mm": JACK_H},
    "tanks": {"od_mm": TANK_OD, "h_mm": TANK_H, "y_mm": TANK_YS, "x_mm": TANK_X},
    "crystalliser": {"od_mm": CRYS_OD, "h_mm": CRYS_H, "pos_mm": [CRYS_X, CRYS_Y]},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(DS)
p["design"].update({
    "service": "MET_SYN: DL-methionine synthesis, the three-step Strecker route in "
               "campaign sequence through one glass-lined column (duty sections 1 "
               "and 3; A-M-416 route A)",
    "material": "borosilicate glass-lined column, PTFE-lined transfer lines, SS304 "
                "feed tanks, Hastelloy C crystalliser",
    "ca_mm": CA,
    "material_basis": "duty section 3 (X-MAT-22): glass-lined for the reaction "
                      "column, PTFE for the transfer, Hastelloy C for the acidic "
                      "hydrolysis/crystallisation; structure 316L wet-bench class "
                      "(layout choice, W12)",
    "connected_kw": KW_SET,
    "purchased": "stirrer drive, heating jacket, metering pumps, Hastelloy C "
                 "crystalliser (plan rule 6 envelopes; connected set 0.2 kW from "
                 "the node)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; bench deck at z 800 over the 20 mm "
             "plinth; reactor column x 400 y 500, feed-tank row x 700 at y 300/550/"
             "800, crystalliser x 1150 y 500 - all on the deck inside the four-post "
             "hold-down frame; fume-hood shell over the bench z 820..1800",
    "supports": "plinth + hold-down frame + 8 slab anchors (A-MACH practice)",
    "nozzle_spread": "the schedule gives face and height only; N1-N3 pack one row "
                     "on -Y at z 160 from x 150, 8 mm clear at the bore; N4 on +Y "
                     "at z 600 at the crystalliser discharge; drain at x 710, vent "
                     "at x 790; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
