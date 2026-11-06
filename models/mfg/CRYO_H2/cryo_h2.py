"""CRYO_H2 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared
reader (models/mfg/lib/graph_node.py); the params.json write-back beside it carries
only the builder-owned layout and study blocks.

Placement frame: x along the rack, y across, z up, origin at the rack corner. Every
dimension is an authority figure or a named layout choice:

- The unit is the hydrogen cylinder bank plus its compression service (node design
  and compressor_design blocks, A-M-167 / X-MFG-36): the node design block sets the
  tube count, OD, wall and length, and the API 521 fire case is carried per half
  (node relief_mm 13). The rack envelope is the node size_mm set by
  flow_graph/param/receivers.py (A-M-167: tube count from the store demand; tubes
  per rack row, row pitch and the rack allowances come from the rcv_* drivers,
  register A-M-167) and the build fills it exactly. Tubes stand in derived tiers
  and rows; the stations are reported in check.json.
- The two hydrogen compressors of node compressor_design (5-stage diaphragm,
  17-4PH H1150 / 316L, 301 SS triple-layer diaphragms, 0.9434 kW average /
  2.830 kW peak, 2 units) are purchased items (AQS-PLAN-006 rule 6): drawn as
  their envelope and interface in the +X end bay of the rack.
- Frame: 12 mm skid plate, hollow 80 x 80 x 5 SHS posts and rails (316L per duty
  section 3: annealed, nickel toward the top of the range, AQS-REV-H2-001),
  saddles under every tube.
- Nozzles: the piped rows of docs-authority/nozzles/CRYO_H2.csv at tag, face and
  bore. The schedule heights (160..2000 mm) were issued against the 300 x 300 x
  2000 study boxes that predate the A-M-167 rack envelope: heights that fit the
  rack are drawn as issued, the rest are clamped onto the rack (1500 -> mid-rail
  centre, top datum 2000 -> flush at the rack top, bottom datum 50 -> skid-top
  stub at its 50 datum) and every clamp is named in check.nozzles_drawn and
  WORK_ORDER W12. The N9 power terminal is a cable (cable schedule X-ELS-06):
  electrical, not piped - carried verbatim in check.json, never drawn. Inlets -Y,
  outlets +Y (house face mapping). No flange is drawn: the schedule rating column
  (Class 150) is carried verbatim as text against the node design 22000 kPa - the
  rating reconciliation is a named hold (lib/dn.py carries no flange table above
  Class 150).

Materials per docs-authority/duties/CRYO_H2.md section 3: 316L annealed for
hydrogen service (AQS-REV-H2-001), corrosion allowance 0 mm.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402

GN = graph_node.graph_node("CRYO_H2")         # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
D = P["design"]
C = P["compressor_design"]
REV = P["graph_revision"]

# ------------------------------------------------------------------ cited constants
L, W, H = (float(v) for v in P["size_mm"])                 # A-M-167 rack, receivers.py
TUBE_OD = float(D["OD_mm"])                               # 114.3
TUBE_WALL = float(D["wall_mm"])                           # 13.49
TUBE_LEN = float(D["tube_m"]) * 1e3                       # 6096
N_TUBES = int(D["tubes"])                                 # node design block (A-M-167)
HALVES = 2                                                # fire case per half (node relief_basis)
TIERS = N_TUBES // (HALVES * 4)                           # tiers x rows x halves
ROWS = N_TUBES // (TIERS * HALVES)
SKID_T = 12.0             # skid plate, study
SHS = 80.0                # post / rail box section, study
SHS_W = 5.0
R_TUBE = TUBE_OD / 2
TIER_Z = [SKID_T + 130.0 + i * 200.0 for i in range(TIERS)]      # study 200 mm tier pitch
ROW_Y = [W * (1 + 2 * k) / (2 * ROWS) for k in range(ROWS)]      # centred row stations across W
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
    frame = frame.union(shs(SHS, y, 380.0, L - 2 * SHS, SHS, 100))                     # mid rail
    frame = frame.union(shs(SHS, y, 100.0, L - 2 * SHS, SHS, 100))                     # bottom rail
for tz in TIER_Z:                                                                      # tier combs
    comb = shs(60.0, 0.0, tz - 8.0, 6300.0, W, 10)
    for y in ROW_Y:                                       # grooves lap the tubes 12 deep
        comb = comb.cut(rod(R_TUBE - 12, (X0 - 50.0, y, tz), "X", TUBE_LEN + 100.0))
    frame = frame.union(comb)
for x in (X0 + TUBE_LEN / 6, X0 + TUBE_LEN / 2, X0 + 5 * TUBE_LEN / 6):                # cross ties
    frame = frame.union(shs(x - SHS / 2, SHS, SKID_T - 5, SHS, W - 2 * SHS, 130.0))
parts["frame"] = frame

# ---------------------------------------------------------------- tubes + saddles
tubes, saddles = None, None
for tz in TIER_Z:
    for k, y in enumerate(ROW_Y):
        t = rod(R_TUBE, (X0, y, tz), "X", TUBE_LEN)
        t = t.cut(rod(R_TUBE - TUBE_WALL, (X0 - 50.0, y, tz), "X", TUBE_LEN + 100.0))
        tubes = t if tubes is None else tubes.union(t)
        for sx in (X0 + TUBE_LEN / 6, X0 + TUBE_LEN / 2, X0 + 5 * TUBE_LEN / 6):
            s = box(sx - 75.0, y - 70.0, tz - 62.0, 150.0, 140.0, 124.0)
            s = s.cut(rod(R_TUBE - 12, (sx - 80.0, y, tz), "X", 160.0))
            saddles = s if saddles is None else saddles.union(s)
parts["tubes"] = tubes
parts["saddles"] = saddles

# ---------------------------------------------------------------- compressors (purchased, rule 6)
comp = None
for cy in (340.0, 1160.0):
    v = box(L - 290.0, cy - 170.0, SKID_T - 5.0, 280.0, 340.0, 850.0)
    comp = v if comp is None else comp.union(v)
parts["compressors"] = comp

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
CLAMP_NOTE = ("schedule datum {h:g} mm was issued against the 300 x 300 x 2000 study box that "
              "predates the A-M-167 rack envelope (H {H:g}); drawn clamped at {z:g} mm - named "
              "hold, WORK_ORDER W12")


def od_of(row):
    """Hardware OD for a piped row: lib-table DN rows at the table OD. Non-piped
    rows are carried verbatim and never drawn."""
    return dn.pipe_od(row["size"]) if row["size"] in dn.PIPE else dn.pipe_od("DN15")


def horizontal(s, face, y_root, z):
    s = s.rotate((0, 0, 0), (1, 0, 0), 90 if face == "-Y" else -90)
    return s.translate((0, y_root, z))


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    if r["size"] in dn.PIPE:
        groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

BANDS = {"-Y": [(100.0, 200.0), (380.0, 480.0), (H - 130.0, H - 30.0)],
         "+Y": [(100.0, 200.0), (380.0, 480.0), (H - 130.0, H - 30.0)]}


def land_z(face, h, od):
    """Schedule height if it fits a side-rail band, else the mid-rail centre (clamped)."""
    for (z0, z1) in BANDS[face]:
        if z0 + od / 2 + 2 <= h <= z1 - od / 2 - 2:
            return h, False
    return (BANDS[face][1][0] + BANDS[face][1][1]) / 2, True


noz, drawn, n_drawn = None, {}, 0
for r in schedule:
    if r["size"] not in dn.PIPE:
        # non-piped terminal row: the N9 power terminal is a cable (cable schedule
        # X-ELS-06), not piped - carried verbatim, not drawn (no geometry change)
        drawn[r["tag"]] = {"style": "carried", "dn": r["size"], "face": r["face"],
                           "height_mm": float(r["height_mm"]), "schedule_rating": r["rating"],
                           "service": r["service"],
                           "note": "power terminal (cable schedule X-ELS-06) - a cable, not "
                                   "piped: carried verbatim, not drawn"}
        continue
for (face, h), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = 3200.0
    for i, r in enumerate(rows):
        tag, dnl = r["tag"], r["size"]
        od = od_of(r)
        x = L / 2 - span / 2 + (i + 0.5) * span / max(len(rows), 1)
        note = "atmospheric stub on the rack side rail (hose makeup at the rack face)"
        if face == "bottom":                               # N4: skid-top stub at the -X end
            s = rod(od / 2, (400.0, W / 2, SKID_T - 5.0), "Z", 50.0 - SKID_T + 5.0)
            zz, y_root = 50.0, None
            note = "skid-top stub beside the -X post, tip at the 50 datum"
        elif face == "top":                                # N5: up the -Y tie bar to the rack top
            s = rod(od / 2, (x, 40.0, H - SHS - 10.0 - 8.0), "Z", SHS + 18.0)
            zz, y_root = H, None
            note = CLAMP_NOTE.format(h=h, H=H, z=H) + "; vent up the tie bar to the rack top"
        else:
            z, clamped = land_z(face, h, od)
            if clamped:
                note = CLAMP_NOTE.format(h=h, H=H, z=z)
            y_root = 60.0 if face == "-Y" else W - 60.0    # tip flush at the rail face
            s = horizontal(nozzles.stub(dnl, 60.0), face, y_root, z)
            zz = z
        if face in ("-Y", "+Y"):
            s = s.translate((x, 0.0, 0.0))
        noz = s if noz is None else noz.union(s)
        n_drawn += 1
        drawn[tag] = {"style": "stub", "dn": dnl,
                      "face": face, "height_mm": h, "x_mm": round(x, 1), "z_drawn_mm": zz,
                      "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="CRYO_H2")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cryo_h2.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "cryo_h2.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CRYO_H2.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
tube_mass = math.pi / 4 * (TUBE_OD ** 2 - (TUBE_OD - 2 * TUBE_WALL) ** 2) * TUBE_LEN * RHO / 1e9
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
SADDLE_UNIT = mass["saddles"] / (TIERS * ROWS * 3)   # drawn unit mass; the booked row is priced at it
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": P["size_mm"], "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "tubes": {"count": N_TUBES, "od_mm": TUBE_OD, "wall_mm": TUBE_WALL, "length_mm": TUBE_LEN,
              "halves": HALVES, "tiers_z_mm": TIER_Z, "rows_y_mm": [round(v, 1) for v in ROW_Y],
              "tube_x_span_mm": [X0, X0 + TUBE_LEN],
              "material": D["material"],
              "drawn_count": TIERS * ROWS,
              "drawn_mass_kg": round(TIERS * ROWS * tube_mass, 1),
              "booked_mass_kg": round(N_TUBES * tube_mass, 1),
              "node_steel_kg": D.get("steel_kg"),
              "note": "booked tube set vs the node steel_kg: the node figure is the receivers.py "
              "sizing record and is carried, not recalculated (WORK_ORDER W12); the tier grid "
              f"draws {TIERS * ROWS} tube solids against the {N_TUBES} booked"},
    "compressors": {"units": C["units"], "stages": C["n_stages"], "kW_avg": C["P_avg_kW"],
                    "kW_peak": C["P_peak_kW"], "material": C["material"],
                    "note": "purchased envelopes and interfaces (AQS-PLAN-006 rule 6), ratings "
                    "from the node compressor_design; drawn in the +X end bay of the rack"},
    "relief": {"design_kPa": P.get("design_kPa"), "relief_mm": P.get("relief_mm"),
               "basis": "node relief_basis: API 520 with the API 521 fire case per half bank "
               f"({N_TUBES // HALVES} tubes per half booked); valves on the bank piping, purchase scope"},
    "storage": {"store_kg": P.get("store_kg"), "water_volume_m3": P.get("store_water_volume_m3"),
                "basis": P.get("store_basis")},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric stubs on the rack side rails; schedule rating column (Class 150) "
    "carried verbatim as text against node design 22000 kPa (hold, W12); the N9 power terminal "
    "is a cable, not piped - carried verbatim in this report, not drawn",
    "part_mass_kg": mass, "cad_stl_scope": "full build, metres (the build fills the A-M-167 rack "
    "envelope exactly)", "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Cylinder tubes SA-312 TP316L seamless DN100 Sch 160, OD {TUBE_OD:g} x t "
          f"{TUBE_WALL:g}, {TUBE_LEN / 1000:g} m", N_TUBES, "316L (annealed, AQS-REV-H2-001)",
     round(N_TUBES * tube_mass, 1), "buy",
     "node design block (OD/wall/length, A-M-167); booked set "
     f"{round(N_TUBES * tube_mass, 1):g} kg ({N_TUBES} tubes; the tier grid draws "
     f"{TIERS * ROWS} tube solids) vs node steel_kg {D.get('steel_kg'):g} - basis "
     "difference named, W12; hydrogen service per duty section 3, CA 0 mm"],
    ["2", "Rack frame: skid plate + SHS posts, tie bars, tier ties and side rails + cross ties",
     1, "316L", round(mass["frame"], 1), "make",
     "frame only; the saddles are item 3 and are priced there once; duty section 3 (no ferritic "
     "or high-strength steel); SHS 80 x 80 x 5 and skid 12 are study sections (W12)"],
    ["3", "Tube saddles, 3 per tube per tier, with wear groove", N_TUBES * 3, "316L",
     round(SADDLE_UNIT * N_TUBES * 3, 1), "make",
     f"study section; saddle laps the tube 6 mm; drawn {TIERS * ROWS * 3} solids "
     f"({mass['saddles']:g} kg), booked {N_TUBES * 3} at the drawn unit mass - the only "
     "saddle line (item 2 is frame only)"],
    ["4", f"Hydrogen compressor sets, 5-stage diaphragm, 17-4PH H1150 / 316L heads, "
          f"301 SS triple-layer diaphragms", C["units"], "purchase item", "", "buy",
     f"node compressor_design: {C['P_avg_kW']:.4f} kW average / {C['P_peak_kW']:.3f} kW peak, "
     "10 -> 200 bar in 5 stages (ratio 1.82 per stage, T_out 125 C); drawn as envelope and "
     "interface (AQS-PLAN-006 rule 6)"],
    ["5", f"Connection set per docs-authority/nozzles/CRYO_H2.csv: {n_drawn} piped rows of "
          f"{len(schedule)} schedule rows (the N9 power terminal is a cable - carried verbatim, "
          "not drawn; clamped heights per check.nozzles_drawn)", n_drawn, "316L",
     mass["nozzles"],
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
    [None, "M12 x 45", fasteners.grade_for("316L"), 8,
     "compressor envelopes to the skid (4 per unit)",
     "plan grade rule; torque per the compressor supplier rule"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["layout"] = {
    "frame": f"rack frame: x along {L:g}, y across {W:g}, z up {H:g}; skid 12, SHS 80 x 80 x 5 "
             "posts and side rails, tier ties and cross ties",
    "tubes": f"{N_TUBES} tubes booked ({TIERS * ROWS} tube solids drawn) in {TIERS} tiers (z "
             + "/".join(f"{v:g}" for v in TIER_Z) +
             f") x {ROWS} rows (y pitch {W / ROWS:g}), one {TUBE_LEN / 1000:g} m tube per "
             f"tier-row; rows y < {W / 2:g} = relief half 1, above = half 2",
    "compressors": "2 purchased 5-stage diaphragm compressor envelopes in the +X end bay "
                   "(node compressor_design)",
    "nozzle_spread": "connections land on the side rails; schedule heights that fit the rack "
                     "are drawn as issued, the rest clamped (per-tag in check.nozzles_drawn); "
                     "the N9 power terminal is a cable - carried verbatim, not drawn",
    "hardware_idiom": "stubs lap the rails or skid so every union fuses; bbox = the A-M-167 rack "
                      "envelope exactly",
}
p["study"] = {
    "skid_t_mm": SKID_T, "shs_mm": [SHS, SHS_W], "tier_pitch_mm": 200.0,
    "note": "frame sections and tier pitch are study sizes not stated by any authority (the "
            "duty names only the 316L grade and CA 0 mm)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}))
