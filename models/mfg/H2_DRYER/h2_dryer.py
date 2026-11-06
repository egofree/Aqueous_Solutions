"""H2_DRYER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 600 mm, y along 400 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope from the node size_mm (600 x 400 x 1000 at this revision). The build fills it exactly.
- Skid per the node design block (the issued dryer sizing): the dryer vessel
  OD 60.3 (D_mm 60, DN50) x 628 (H_mm), wall 3.91 (wall_mm), 316L annealed (duty
  section 3: dry H2 per M6, AQS-REV-H2-001) with 38 mm insulation (insulation_mm);
  two deoxo tubes DN25 Sch 40 x 328 (beds.deoxo: V_L 0.183 L, count 2); two guard
  tubes DN25 Sch 40 x 300 (beds.guard: 0.05 L, count 2); two TSA bed tubes DN50
  Sch 40 x 300 (beds.TSA: V_L 0.5044 L, count 2) with the molecular-sieve bed
  envelopes inside (sieve_kg 0.353 per design; guard_kg 0.032); the regeneration
  heater envelope at the vessel base (regen_W 1.03, purchased per plan rule 6);
  and the PVC-U inlet knock-out pot (duty section 3: inlet knock-out PVC-U, wet).
  Bed positions are the layout choice (W12) - the design names the components and
  counts, not their arrangement.
- A-MACH guard and anchors: a four-post guard frame (30 x 30 posts, top rail) on
  a 20 mm plinth; 8 slab anchors in fasteners.csv.
- Nozzles: all 9 rows of docs-authority/nozzles/H2_DRYER.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: no duct bore, no flange class). The N7 solids row (dried
  hydrogen - the product gas edge) is a non-piped transfer row drawn DN15, bore
  not calculated (plan W4). The N4 vent is the S24 relief edge to RELIEF_H2 (duty
  section 6) - drawn flush at the envelope top with the destination named. Drain
  flush at the envelope bottom (50 datum). The schedule rating column (Class 150)
  is carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # node envelope (tracker-synced)
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
Z0 = 120.0                                                 # tube seat height (layout choice, W12)
V_OD, V_WALL, V_H = 60.3, float(DS.get("wall_mm", 3.91)), float(DS.get("H_mm", 628.0))
V_ID = V_OD - 2 * V_WALL
INSUL = float(DS.get("insulation_mm", 38.0))
TSA_OD = dn.pipe_od("DN50")
DEO_OD = dn.pipe_od("DN25")
DEO_L, GUARD_L, TSA_L = 328.0, 300.0, 300.0
BED_ENDS = 10.0                                            # support disc allowance per end
MAT = "316L"                                               # duty section 3 (dry vessel; M6)
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)
RHO_PVC = materials.density("PVC_U")
RHO_SIEVE = 900.0                                          # molecular-sieve bulk, study (buy row)
POST = 30.0                                                # guard frame section

POS = {                                                    # bed stations (layout choice, W12)
    "ko": (60.0, 200.0), "deoxo1": (150.0, 120.0), "deoxo2": (150.0, 280.0),
    "guard1": (220.0, 120.0), "guard2": (220.0, 280.0),
    "tsa1": (300.0, 120.0), "tsa2": (300.0, 280.0), "vessel": (450.0, 200.0),
}

assert L >= 540.0 and W >= 380.0, "H2_DRYER envelope too small for the laid-out bed stations (W12)"
assert POS["vessel"][0] - V_OD / 2 - INSUL > POS["tsa1"][0] + TSA_OD / 2 + INSUL, "stations clear"
assert Z0 + V_H + INSUL + 200.0 < H, "vessel + heater stays inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def vtube(od, x, y, z0, z1):
    return (cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + guard frame (A-MACH)
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H - POST)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- dryer vessel (design block) + insulation
vx, vy = POS["vessel"]
vessel = vtube(V_OD, vx, vy, Z0, Z0 + V_H)
vessel = vessel.union(vtube(V_OD, vx, vy, Z0, Z0 + 6.0))          # base head
vessel = vessel.union(vtube(V_OD, vx, vy, Z0 + V_H - 6.0, Z0 + V_H))  # top head
parts["vessel"] = vessel
parts["insulation"] = (cq.Workplane("XY", origin=(vx, vy, Z0))
                       .circle(V_OD / 2 + INSUL).circle(V_OD / 2)
                       .extrude(V_H))

# ---------------------------------------------------------------- beds (design block, layout choice W12)
beds = None
for (od, x, y, zlen) in ((DEO_OD, *POS["deoxo1"], DEO_L), (DEO_OD, *POS["deoxo2"], DEO_L),
                         (DEO_OD, *POS["guard1"], GUARD_L), (DEO_OD, *POS["guard2"], GUARD_L),
                         (TSA_OD, *POS["tsa1"], TSA_L), (TSA_OD, *POS["tsa2"], TSA_L)):
    t = vtube(od, x, y, Z0, Z0 + zlen)
    beds = t if beds is None else beds.union(t)
parts["beds"] = beds

# media envelopes inside the TSA (sieve, sieve_kg 0.353) and guard (guard_kg 0.032)
media = None
for (od, x, y, zlen) in ((TSA_OD, *POS["tsa1"], TSA_L), (TSA_OD, *POS["tsa2"], TSA_L),
                         (DEO_OD, *POS["guard1"], GUARD_L), (DEO_OD, *POS["guard2"], GUARD_L)):
    m = vtube(od - 2 * 1.5, x, y, Z0 + BED_ENDS, Z0 + zlen - BED_ENDS)
    media = m if media is None else media.union(m)
parts["media"] = media

# ---------------------------------------------------------------- heater envelope + KO pot
hx, hy = POS["vessel"]
parts["heater"] = (cq.Workplane("XY", origin=(hx - V_OD / 2 - INSUL, hy - V_OD / 2 - INSUL, Z0))
                   .box(V_OD + 2 * INSUL, V_OD + 2 * INSUL, 60.0, centered=False))
kox, koy = POS["ko"]
parts["ko_pot"] = (cq.Workplane("XY", origin=(kox, koy, Z0))
                   .circle(30.0).extrude(120.0))           # PVC-U inlet knock-out, wet side

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
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 200.0, (face, z, span)
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
    dnl_draw = dnl if dnl.startswith("DN") else "DN15"
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (180.0, 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: vent = S24 relief to RELIEF_H2
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "top", 0.0, (400.0, 200.0), (L, W, H))
        note = ("vent flush at the envelope top; the schedule datum 800 mm is a "
                f"placeholder under the {H:g} box; the vent is S24 to RELIEF_H2 "
                "(duty section 6) - destination named")
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
        s = tube_z(dnl_draw, 50.0)
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
mass = {k: round(v.val().Volume() * (RHO_PVC if k == "ko_pot" else
                                     RHO_SIEVE if k == "media" else
                                     RHO) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "H2 dryer skid per the node design block: dryer vessel OD 60.3 x "
                "628 (wall 3.91, 316L annealed per M6/AQS-REV-H2-001) with 38 mm "
                "insulation; 2 deoxo tubes DN25 x 328; 2 guard tubes DN25 x 300 "
                "with guard media envelopes; 2 TSA bed tubes DN50 x 300 with "
                "molecular-sieve bed envelopes (sieve_kg 0.353); regeneration "
                "heater envelope at the vessel base (1.03 W); PVC-U inlet "
                "knock-out pot (duty section 3); guard frame + plinth (A-MACH)",
        "vessel": {"od_mm": V_OD, "h_mm": V_H, "wall_mm": V_WALL, "insulation_mm": INSUL},
        "beds": {"deoxo": "DN25 x 328, 2 off (V_L 0.183 L per design)",
                 "guard": "DN25 x 300, 2 off (guard_kg 0.032 media envelope)",
                 "tsa": "DN50 x 300, 2 off (sieve_kg 0.353 media envelope)",
                 "layout": "stations are the layout choice; the design names "
                           "components and counts, not arrangement (W12)"},
        "material": MAT, "ca_mm": CA,
        "wet_side": "inlet knock-out PVC-U per duty section 3 (wet); dryer vessel "
                    "and dry outlet 316L annealed (M6, dry H2)",
        "purchased": {"heater": "regeneration heater envelope, 1.03 W (node design "
                                "regen_W) - purchased per plan rule 6",
                      "deoxo_catalyst": "deoxo catalyst charge, buy row (V_L 0.183 L "
                                        "per the design beds block), not drawn",
                      "sieve": "molecular sieve charge 0.353 kg, buy row (bed "
                               "envelope drawn)"},
        "guard": "four-post guard frame (30 x 30 posts, top rail) + 8 slab anchors "
                 "(A-MACH: guard and anchor drawn)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: no duct bore, no flange class); the N7 "
                    "solids row (dried hydrogen product edge) drawn DN15, bore not "
                    "calculated (plan W4); the N4 vent is the S24 relief edge to "
                    "RELIEF_H2 (duty section 6) with the destination named; the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Dryer vessel OD {V_OD:g} x {V_H:g}, wall {V_WALL:g} (node design "
          "D_mm/H_mm/wall_mm), with heads", 1, "316L annealed (duty section 3, M6; "
     "AQS-REV-H2-001)", mass["vessel"], "make",
     "node design block; CA 0 mm (AQS-STD-001 316L rule); T_C 250 design class"],
    ["2", f"Insulation jacket {INSUL:g} mm over the vessel", 1,
     "mineral wool + cladding (class per AQS-THM-003)", mass["insulation"], "make",
     "node design insulation_mm 38; regeneration held per the duty"],
    ["3", "Bed tubes: 2 deoxo DN25 x 328, 2 guard DN25 x 300, 2 TSA DN50 x 300 "
          "(Sch 40 table)", 6, "316L tube", mass["beds"], "make",
     "node design beds block (tube, L_mm, count); stations are the layout choice "
     "(hold, WORK_ORDER W12)"],
    ["4", "Media envelopes: molecular sieve 0.353 kg in the TSA tubes; guard media "
          "0.032 kg in the guard tubes", 4, "molecular sieve (buy charge; envelope "
     "drawn)", mass["media"], "buy",
     "node design sieve_kg/guard_kg; sieve and guard charges are buy rows per "
     "plan rule 6"],
    ["5", "Deoxo catalyst charge 0.183 L, 2 tubes", 2, "deoxo catalyst (purchased "
     "charge)", 0.0, "buy",
     "node design beds.deoxo V_L; catalyst not drawn (plan rule 6)"],
    ["6", "Regeneration heater envelope at the vessel base", 1,
     "purchased unit (envelope)", mass["heater"], "buy",
     "node design regen_W 1.03; purchased envelope per plan rule 6, rating from "
     "the node"],
    ["7", "PVC-U inlet knock-out pot OD 60 x 120 (duty section 3: inlet knock-out "
          "PVC-U, wet)", 1, "PVC-U", mass["ko_pot"], "make",
     "duty section 3 wet-side selection; CA 0 mm (AQS-STD-001 polymer rule)"],
    ["8", "Guard frame: four 30 x 30 posts with top rail (A-MACH guard) + plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["frame"] + mass["plinth"], "make",
     "AQS-MOD-002 dry service; the frame pins the envelope (X-PAR-04); anchors in "
     "fasteners.csv"],
    ["9", "Nozzle set per docs-authority/nozzles/H2_DRYER.csv: 8 open-bore tube "
          "stubs (DN15), the N7 solids row drawn DN15 bore not calculated",
     len(schedule), "316L tube", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; the N4 vent is S24 to RELIEF_H2 "
     "(destination named); atmospheric tube per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 2 per corner post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M8 tube-clip bolt + nut", fasteners.grade_for("316L"), 16,
     "bed tubes to the plinth clip rail, 2 per tube (count from the model)",
     "A4-70 on 316L per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "vessel": {"od_mm": V_OD, "h_mm": V_H, "wall_mm": V_WALL,
               "pos_mm": [POS["vessel"][0], POS["vessel"][1], Z0]},
    "insulation_mm": INSUL,
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(DS)
p["design"].update({
    "service": "H2_DRYER: process H2 dried on the molecular-sieve beds; the vent "
               "is S24 to RELIEF_H2 (duty sections 1, 4 and 6)",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: inlet knock-out PVC-U (wet); dryer vessel "
                      "and dry outlet 316L annealed (M6, dry H2; AQS-REV-H2-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; bed stations per POS (KO pot x 60, "
             "deoxo x 150, guard x 220, TSA x 300, vessel x 450, all on the z 120 "
             "seat); guard posts at the envelope corners",
    "supports": "plinth + guard frame + 8 slab anchors; tube clip rail (A-MACH)",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 200, 8 mm clear at the "
                     "bore; drain at x 180, vent at x 400; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
