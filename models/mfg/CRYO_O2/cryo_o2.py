"""CRYO_O2 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AC. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. (W2 fields by the
tracker; the layout and study blocks beside them are builder-owned).

Placement frame: x along the rack (6696), y across (1500), z up (600), origin at the
rack corner. Every dimension is an authority figure or a named layout choice:

- The unit is the oxygen cylinder bank (node design block, A-M-167): 16 tubes
  SA-312 TP316L seamless DN100 Sch 160, OD 114.3 x wall 13.49, 6.096 m, O2-cleaned
  to ASTM G93, in 2 halves of 8 (the API 521 fire case is carried per half: node
  relief_mm 9, 2 valves). The rack envelope 6696 x 1500 x 600 is the node size_mm
  set by flow_graph/param/receivers.py - the build fills it exactly. Tubes stand
  in 2 tiers (z 200/440) of 9 rows (y pitch 166.7): the main bank is rows 1-7 in
  both tiers (14 tubes), the crew reserve is the 2 separate tubes of rows 8-9 in
  the lower tier behind a divider plate (node banks: main + crew reserve).
- Frame: 12 mm skid plate, hollow 80 x 80 x 5 SHS posts and side rails (316L per
  duty section 3), grooved tier combs, saddles under every tube.
- Nozzles: all 9 rows of docs-authority/nozzles/CRYO_O2.csv at tag, face and
  bore. The schedule heights (160..2000 mm) were issued against the 300 x 300 x
  2000 study boxes that predate the A-M-167 rack envelope: heights that fit the
  600 mm rack are drawn as issued (400, 160), the rest are clamped onto the rack
  (1500 -> mid-rail centre, 600 -> top-rail centre, top datum 2000 -> flush at
  the 600 rack top, bottom datum 50 -> skid-top stub) and every clamp is named in
  check.nozzles_drawn and WORK_ORDER W12. Inlets -Y, outlets +Y (house face
  mapping). No flange is drawn: the schedule rating column (Class 150) is carried
  verbatim as text against the node design 22000 kPa - the rating reconciliation
  is a named hold (lib/dn.py carries no flange table above Class 150).

Materials per docs-authority/duties/CRYO_O2.md section 3: 316L, condensation,
corrosion allowance 0 mm, no carbon steel; the O2 bank is cleaned to ASTM G93
(node storage_mode).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles  # noqa: E402

GN = graph_node.graph_node("CRYO_O2")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
D = GN.design
REV = P["graph_revision"]

# ------------------------------------------------------------------ cited constants
L, W, H = [float(v) for v in P["size_mm"]]                # 6696 x 1500 x 600 (A-M-167)
TUBE_OD = float(D["OD_mm"])                               # 114.3
TUBE_WALL = float(D["wall_mm"])                           # 13.49
TUBE_LEN = float(D["tube_m"]) * 1e3                       # 6096
N_TUBES = int(D["tubes"])                                 # 16
N_MAIN, N_CREW = 14, 2                                    # node banks: main 14 + crew reserve 2
HALVES = 2                                                # fire case per half (node relief_basis)
TIERS, ROWS = 2, 9                                        # 2 tiers x 9 rows = 18 slots, 16 used
SKID_T = 12.0             # skid plate, study
SHS = 80.0                # post / rail box section, study
SHS_W = 5.0
R_TUBE = TUBE_OD / 2
TIER_Z = [SKID_T + 130.0 + i * 240.0 for i in range(TIERS)]      # 142 / 382
ROW_Y = [W * (1 + 2 * k) / (2 * ROWS) for k in range(ROWS)]      # 83.3 .. 1416.7
DIVIDER_Y = (ROW_Y[6] + ROW_Y[7]) / 2                     # main bank | crew reserve
CA = materials.ca_for("316L")                             # 0.0
RHO = materials.density("316L")

X0 = (L - TUBE_LEN) / 2                                   # 300


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


def shs(x, y, z, dx, dy, dz):
    """Hollow square section along the longest of dx/dy/dz, wall 5; thin sections stay solid."""
    outer = box(x, y, z, dx, dy, dz)
    if min(dx, dy, dz) <= 2 * SHS_W:
        return outer
    wx, wy, wz = dx - 2 * SHS_W, dy - 2 * SHS_W, dz - 2 * SHS_W
    inner = box(x + SHS_W, y + SHS_W, z + SHS_W,
                wx if dx > SHS_W else dx, wy if dy > SHS_W else dy, wz if dz > SHS_W else dz)
    return outer.cut(inner)


parts = {}

# ---------------------------------------------------------------- rack frame
frame = box(0, 0, 0, L, W, SKID_T)                                                     # skid plate
for x in (0.0, L - SHS):
    for y in (0.0, W - SHS):
        frame = frame.union(shs(x, y, SKID_T - 5, SHS, SHS, H - SKID_T + 5))           # posts
for y in (0.0, W - SHS):
    frame = frame.union(shs(SHS, y, H - SHS - 10, L - 2 * SHS, SHS, 10))               # tie bars
    frame = frame.union(shs(SHS, y, H - 130.0, L - 2 * SHS, SHS, 100))                 # top rail
    frame = frame.union(shs(SHS, y, 350.0, L - 2 * SHS, SHS, 100))                     # mid rail
    frame = frame.union(shs(SHS, y, 100.0, L - 2 * SHS, SHS, 100))                     # bottom rail
for tz in TIER_Z:                                                                      # tier combs
    comb = shs(60.0, 0.0, tz - 8.0, 6300.0, W, 10)
    for y in ROW_Y[:7] + (ROW_Y[7:] if tz == TIER_Z[0] else []):   # crew rows, lower tier only
        comb = comb.cut(rod(R_TUBE - 12, (X0 - 50.0, y, tz), "X", TUBE_LEN + 100.0))
    frame = frame.union(comb)
for x in (X0 + TUBE_LEN / 6, X0 + TUBE_LEN / 2, X0 + 5 * TUBE_LEN / 6):                # cross ties
    frame = frame.union(shs(x - SHS / 2, SHS, SKID_T - 5, SHS, W - 2 * SHS, 130.0))
parts["frame"] = frame

# ---------------------------------------------------------------- tubes + saddles
tubes, saddles = None, None
slots = [(tz, y) for tz in TIER_Z for y in ROW_Y[:7]] + [(TIER_Z[0], y) for y in ROW_Y[7:]]
for (tz, y) in slots:                                      # 14 main + 2 crew
    t = rod(R_TUBE, (X0, y, tz), "X", TUBE_LEN)
    t = t.cut(rod(R_TUBE - TUBE_WALL, (X0 - 50.0, y, tz), "X", TUBE_LEN + 100.0))
    tubes = t if tubes is None else tubes.union(t)
    for sx in (X0 + TUBE_LEN / 6, X0 + TUBE_LEN / 2, X0 + 5 * TUBE_LEN / 6):
        s = box(sx - 75.0, y - 70.0, tz - 62.0, 150.0, 140.0, 124.0)
        s = s.cut(rod(R_TUBE - 12, (sx - 80.0, y, tz), "X", 160.0))
        saddles = s if saddles is None else saddles.union(s)
parts["tubes"] = tubes
parts["saddles"] = saddles

# ---------------------------------------------------------------- crew divider (NFPA 2 separation)
parts["divider"] = box(X0, DIVIDER_Y - 3.0, SKID_T - 5.0, TUBE_LEN + 120.0, 6.0, 330.0)

# ---------------------------------------------------------------- relief valves (purchased, rule 6)
relief = None
for y in (ROW_Y[3], ROW_Y[4]):                             # one 9 mm API 520 valve per half
    v = box(L - 260.0, y - 60.0, SKID_T - 5.0, 180.0, 120.0, 150.0)
    relief = v if relief is None else relief.union(v)
parts["relief_valves"] = relief

# ---------------------------------------------------------------- nozzles (schedule verbatim)
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
CLAMP_NOTE = ("schedule datum {h:g} mm was issued against the 300 x 300 x 2000 study box that "
              "predates the A-M-167 rack envelope (H {H:g}); drawn clamped at {z:g} mm - named "
              "hold, WORK_ORDER W12")


def od_of(row):
    return dn.pipe_od("DN15") if row["size"] == "solids" else dn.pipe_od(row["size"])


def horizontal(s, face, y_root, z):
    s = s.rotate((0, 0, 0), (1, 0, 0), 90 if face == "-Y" else -90)
    return s.translate((0, y_root, z))


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

BANDS = {"-Y": [(100.0, 200.0), (350.0, 450.0), (H - 130.0, H - 30.0)],
         "+Y": [(100.0, 200.0), (350.0, 450.0), (H - 130.0, H - 30.0)]}


def land_z(face, h, od):
    """Schedule height if it fits a side-rail band, else the nearest rail centre (clamped)."""
    for (z0, z1) in BANDS[face]:
        if z0 + od / 2 + 2 <= h <= z1 - od / 2 - 2:
            return h, False
    return (BANDS[face][1][0] + BANDS[face][1][1]) / 2, True


noz, drawn = None, {}
for (face, h), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = 3200.0
    for i, r in enumerate(rows):
        tag, dnl = r["tag"], r["size"]
        dnl_hw = "DN15" if dnl == "solids" else dnl
        od = od_of(r)
        x = L / 2 - span / 2 + (i + 0.5) * span / max(len(rows), 1)
        note = "atmospheric stub on the rack side rail (hose makeup at the rack face)"
        if face == "bottom":                               # N3: skid-top stub at the -X end
            s = rod(dn.pipe_od(dnl_hw) / 2, (400.0, W / 2, SKID_T - 5.0), "Z", 50.0 - SKID_T + 5.0)
            zz, y_root = 50.0, None
            note = "skid-top stub beside the -X post, tip at the 50 datum"
        elif face == "top":                                # N4: up the -Y tie bar to the 600 top
            s = rod(dn.pipe_od(dnl_hw) / 2, (x, 40.0, H - SHS - 10.0 - 8.0), "Z", SHS + 18.0)
            zz, y_root = H, None
            note = CLAMP_NOTE.format(h=h, H=H, z=H) + "; vent up the tie bar to the rack top"
        else:
            z, clamped = land_z(face, h, od)
            if clamped:
                note = CLAMP_NOTE.format(h=h, H=H, z=z)
            y_root = 60.0 if face == "-Y" else W - 60.0    # tip flush at the rail face
            s = horizontal(nozzles.stub(dnl_hw, 60.0), face, y_root, z) \
                if dnl != "solids" else horizontal(nozzles.stub("DN15", 60.0), face, y_root, z)
            if dnl == "solids":
                note = SOLIDS_NOTE
            zz = z
        if face in ("-Y", "+Y"):
            s = s.translate((x, 0.0, 0.0))
        noz = s if noz is None else noz.union(s)
        drawn[tag] = {"style": "solids" if dnl == "solids" else "stub",
                      "dn": dnl_hw if dnl != "solids" else "DN15",
                      "face": face, "height_mm": h, "x_mm": round(x, 1), "z_drawn_mm": zz,
                      "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="CRYO_O2")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cryo_o2.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "cryo_o2.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CRYO_O2.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
tube_mass = math.pi / 4 * (TUBE_OD ** 2 - (TUBE_OD - 2 * TUBE_WALL) ** 2) * TUBE_LEN * RHO / 1e9
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": P["size_mm"], "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "tubes": {"count": N_TUBES, "od_mm": TUBE_OD, "wall_mm": TUBE_WALL, "length_mm": TUBE_LEN,
              "halves": HALVES, "tiers_z_mm": TIER_Z, "rows_y_mm": [round(v, 1) for v in ROW_Y],
              "main_tubes": N_MAIN, "crew_tubes": N_CREW,
              "divider_y_mm": round(DIVIDER_Y, 1),
              "tube_x_span_mm": [X0, X0 + TUBE_LEN],
              "material": D["material"],
              "drawn_mass_kg": round(N_TUBES * tube_mass, 1),
              "node_steel_kg": D.get("steel_kg"),
              "note": "drawn tube set vs the node steel_kg: the node figure is the receivers.py "
              "sizing record and is carried, not recalculated (WORK_ORDER W12)"},
    "relief": {"design_kPa": P.get("design_kPa"), "relief_mm": P.get("relief_mm"), "valves": HALVES,
               "basis": "node relief_basis: API 520 blocked-outlet governing with the API 521 "
               "fire case per half bank (8 tubes per half); valves purchased, bore 9 mm"},
    "storage": {"mode": P.get("storage_mode"), "store_kg": P.get("store_kg"),
                "crew_reserve_kg": P.get("crew_reserve_kg"),
                "crew_basis": P.get("crew_reserve_basis")},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric stubs on the rack side rails; schedule rating column (Class 150) "
    "carried verbatim as text against node design 22000 kPa (hold, W12)",
    "part_mass_kg": mass, "cad_stl_scope": "full build, metres (the build fills the A-M-167 rack "
    "envelope exactly)", "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Cylinder tubes SA-312 TP316L seamless DN100 Sch 160, OD {TUBE_OD:g} x t "
          f"{TUBE_WALL:g}, {TUBE_LEN / 1000:g} m, O2-cleaned to ASTM G93", N_TUBES, "316L",
     round(N_TUBES * tube_mass, 1), "buy",
     "node design block (OD/wall/length, A-M-167) and storage_mode (O2-clean, NFPA 2 ch. 7 "
     "separation); drawn set " + f"{round(N_TUBES * tube_mass, 1):g} kg vs node steel_kg "
     f"{D.get('steel_kg'):g} - basis difference named, W12; duty section 3 CA 0 mm"],
    ["2", "Rack frame: skid plate + SHS posts, tie bars, tier combs and side rails + cross ties",
     1, "316L", round(mass["frame"] + mass["saddles"], 1), "make",
     "duty section 3 (no carbon steel); SHS 80 x 80 x 5 and skid 12 are study sections (W12)"],
    ["3", "Tube saddles, 3 per tube, with wear groove", N_TUBES * 3, "316L",
     mass["saddles"], "make", "study section; saddle laps the tube 6 mm"],
    ["4", "Crew-reserve divider plate, main bank | crew bank", 1, "316L",
     mass["divider"], "make",
     "node banks (main + crew reserve, separate banks per crew_reserve_basis, NFPA 2 ch. 7); "
     "study plate"],
    ["5", f"Relief valves, API 520 / API 521 fire case per half bank, bore "
          f"{P.get('relief_mm'):g} mm", HALVES, "purchase item", "", "buy",
     "node relief_basis (valves 2, per_half_bore 8.606 -> 9 mm); O2-cleaned per ASTM G93; "
     "rated for the 22000 kPa design - the schedule Class 150 column is a named hold (W12)"],
    ["6", f"Connection set per docs-authority/nozzles/CRYO_O2.csv ({len(schedule)} rows, "
          "clamped heights per check.nozzles_drawn)", len(schedule), "316L", mass["nozzles"],
     "make", "schedule tags/faces/bore verbatim; heights clamped onto the rack where the issued "
     "datum predates the A-M-167 envelope (W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 x 40", fasteners.grade_for("316L"), 8 * N_TUBES,
     "tube saddles to the cross ties and skid (8 per tube)",
     "A4-70 on 316L per the plan grade rule; study count"],
    [None, "M10 x 30 wedge anchor", fasteners.grade_for("316L"), 8,
     "skid to the slab", "plan grade rule; seismic anchorage per the frame check task"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["layout"] = {
    "frame": "rack frame: x along 6696, y across 1500, z up 600; skid 12, SHS 80 x 80 x 5 posts "
             "and side rails, grooved tier combs, cross ties",
    "tubes": f"{N_TUBES} tubes ({N_MAIN} main + {N_CREW} crew reserve) in {TIERS} tiers (z "
             f"{'/'.join(f'{v:g}' for v in TIER_Z)}) x {ROWS} rows (y pitch 166.7); main = rows "
             f"1-7 both tiers, crew = rows 8-9 lower tier behind the divider at y "
             f"{DIVIDER_Y:g}; rows y < 750 = relief half 1, above = half 2",
    "relief": "one 9 mm API 520/521 valve per half bank at the +X end posts",
    "nozzle_spread": "connections land on the side rails; schedule heights that fit the 600 rack "
                     "are drawn as issued, the rest clamped (per-tag in check.nozzles_drawn)",
    "hardware_idiom": "stubs lap the rails or skid so every union fuses; bbox = the A-M-167 rack "
                      "envelope exactly",
}
p["study"] = {
    "skid_t_mm": SKID_T, "shs_mm": [SHS, SHS_W], "tier_pitch_mm": 240.0,
    "note": "frame sections and tier pitch are study sizes not stated by any authority (the "
            "duty names only 316L and CA 0 mm)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}))
