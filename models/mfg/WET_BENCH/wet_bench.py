"""WET_BENCH manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box; the duty
  states no envelope). A four-post hold-down frame pins the registry box so the
  X-PAR-04 envelope registry reads the build.
- Bench per the node equipment list (the RCA/etch bench load basis): SC1 bath 10 L at
  80 C with immersion heater (2.479 kWh/d), SC2 bath 10 L at 80 C with immersion
  heater (2.479 kWh/d), DHF etch bath at ambient, DIW rinse + N2 guns (0.05 kWh/d).
  Wetted material per duty section 3: "PVC-U wetted, per AQS-STD-002 rules M1 and
  M2. No metal wetted part. The graph gives no temperature for this unit; above 60 C
  the thermoplastic is CPVC, never metal" - the node equipment rows give the 80 C
  bath temperatures, so the two heated baths are CPVC and the ambient baths PVC-U.
  The node equipment rows name PP tanks; the duty section 3 selection governs (plan
  rule 5) - the tension is a named hold, WORK_ORDER W12. Tank arrangement and the
  bath sizes that the node does not state are the layout choice (W12).
- A-MACH guard and anchors: the four-post hold-down frame is the guard; 8 slab
  anchors in fasteners.csv.
- Nozzles: all rows of docs-authority/nozzles/WET_BENCH.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: nozzle DN15, no flange class, atmospheric tube or hose). The
  stubs are polymer per duty section 3 (no metal wetted part). Drain flush at the
  envelope bottom (50 datum); vent flush at the envelope top (800 datum is the box
  top). The schedule rating column (Class 150) is carried verbatim as text.
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_DECK = 20.0                                              # bench deck plate on the plinth
POST = 40.0                                                # hold-down/guard frame section
T_WALL = 10.0                                              # thermoplastic bath wall (study, W12)
RHO_CPVC = materials.density("CPVC")
RHO_PVC = materials.density("PVC_U")
RHO_CS = materials.density("CS")

# Baths on the deck (arrangement and the unstated bath sizes are the layout choice, W12;
# the SC1/SC2 nominal 10 L and the 80 C temperatures are node equipment figures).
# (key, x, y, inner dx, dy, dz, material, node basis)
BATHS = [
    ("sc1",   60.0, 120.0, 250.0, 250.0, 160.0, "CPVC",
     "node equipment: SC1 bath 10 L, 80 C, immersion heater, 2.479 kWh/d"),
    ("sc2",  350.0, 120.0, 250.0, 250.0, 160.0, "CPVC",
     "node equipment: SC2 bath 10 L, 80 C, immersion heater, 2.479 kWh/d"),
    ("dhf",  640.0, 120.0, 120.0, 250.0, 160.0, "PVC_U",
     "node equipment: DHF etch bath, ambient (no bath size stated - drawn to its bay)"),
    ("rinse", 800.0, 120.0, 120.0, 250.0, 160.0, "PVC_U",
     "node equipment: DIW rinse + N2 guns, 0.05 kWh/d (no bath size stated - drawn to its bay)"),
]
for (k, x, y, dx, dy, dz, *_r) in BATHS:
    assert x >= 44.0 and x + dx + 2 * T_WALL <= L - POST - 4.0, (k, "inside the deck")
    assert dy + 2 * T_WALL <= W - 200.0, (k, "clear of the -Y inlet row")

assert L == 1000.0 and W == 600.0 and H == 800.0, "WET_BENCH node envelope changed"
DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, T_DECK)
# deck faces sit 4 mm inside the post lines: no coplanar T-junction with the frame


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth, deck, hold-down/guard frame
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

# ---------------------------------------------------------------- baths (node equipment, duty section 3)
baths, heaters = None, None
for (k, x, y, dx, dy, dz, _m, _b) in BATHS:
    z0 = T_PLINTH + T_DECK
    outer = box(x, y, z0, dx + 2 * T_WALL, dy + 2 * T_WALL, dz + T_WALL)      # floor + walls
    void = box(x + T_WALL, y + T_WALL, z0 + T_WALL, dx, dy, dz + 1.0)          # open-top void
    t = outer.cut(void)
    baths = t if baths is None else baths.union(t)
    if k in ("sc1", "sc2"):               # immersion heater envelope, purchased per plan rule 6
        h = box(x + 20.0, y + 20.0, z0 + T_WALL, 30.0, 30.0, dz - 20.0)
        heaters = h if heaters is None else heaters.union(h)
parts["baths"] = baths
parts["heaters"] = heaters

# ---------------------------------------------------------------- nozzles (schedule verbatim, polymer)
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
    if dnl == "cable":                                    # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = ("atmospheric open-bore tube stub flush at the envelope face "
            "(duty section 4; polymer per duty section 3 - no metal wetted part)")
    if r["face"] == "bottom":                             # N7: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder")
    elif r["face"] == "top":                              # N8: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
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


def _bath_mass(k, dx, dy, dz, mat):
    rho = RHO_CPVC if mat == "CPVC" else RHO_PVC
    walls = (2 * (dx + 2 * T_WALL) * T_WALL * dz + 2 * dy * T_WALL * dz
             + (dx + 2 * T_WALL) * (dy + 2 * T_WALL) * T_WALL)
    return round(walls * rho / 1e9, 2)


mass = {k: round(v.val().Volume() * (RHO_CPVC if k == "heaters" else RHO_CS)
                 / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "RCA/etch wet bench per the node equipment list: SC1 bath 10 L at "
                "80 C and SC2 bath 10 L at 80 C with immersion heater envelopes "
                "(2.479 kWh/d each), DHF etch bath at ambient, and the DIW rinse "
                "bay, on a bench deck over a 20 mm plinth inside a four-post "
                "hold-down frame that pins the registry box (X-PAR-04)",
        "baths": {b[0]: {"inner_mm": [b[2], b[3], b[4]], "material": b[5],
                         "nominal_l": round(b[2] * b[3] * b[4] / 1e6, 1),
                         "node_basis": b[6], "make_or_buy": "make"}
                  for b in BATHS},
        "material_rule": "duty section 3: PVC-U wetted per AQS-STD-002 rules M1 "
                         "and M2, no metal wetted part; above 60 C the "
                         "thermoplastic is CPVC, never metal - the node equipment "
                         "rows give the 80 C bath temperatures, so SC1/SC2 are "
                         "CPVC and the ambient baths PVC-U; the node equipment "
                         "rows name PP tanks, the duty selection governs (plan "
                         "rule 5; hold, WORK_ORDER W12)",
        "guard": "four-post hold-down frame (40 x 40 posts, top rails) is the "
                 "A-MACH guard + 8 slab anchors (fasteners.csv)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: nozzle DN15, no flange class, atmospheric "
                    "tube or hose), drawn polymer per duty section 3 (no metal "
                    "wetted part); drain flush at the envelope bottom (50 datum), "
                    "vent flush at the envelope top (800 datum is the box top); "
                    "the schedule rating column (Class 150) carried verbatim as "
                    "text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
    "bath_mass_kg": {b[0]: _bath_mass(b[0], b[2], b[3], b[4], b[5]) for b in BATHS},
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
bm = report["bath_mass_kg"]
rows = [
    ["1", f"Bench deck {DECK[3]:g} x {DECK[4]:g} x {T_DECK:g} over the plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["deck"] + mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; dry structure outside the wetted polymer"],
    ["2", "Four-post hold-down/guard frame pinning the "
          f"{L:g} x {W:g} x {H:g} envelope (40 x 40 posts, top rails)", 1,
     "carbon steel (ASTM A500)", mass["frame"], "make (AQS-BOM-SC-001)",
     "HX8 hold-down idiom (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", "SC1 bath 10 L nominal (inner 250 x 250 x 160), wall 10 (study), with "
           "immersion heater envelope", 1, "CPVC (duty section 3 rule at the node "
           "80 C bath temperature)", bm["sc1"], "make (AQS-BOM-SC-001)",
     "node equipment: SC1 bath 10 L, 80 C, 2.479 kWh/d; heater envelope is the "
     "purchased unit per plan rule 6 (BOM row 7)"],
    ["4", "SC2 bath 10 L nominal (inner 250 x 250 x 160), wall 10 (study), with "
           "immersion heater envelope", 1, "CPVC (duty section 3 rule at the node "
           "80 C bath temperature)", bm["sc2"], "make (AQS-BOM-SC-001)",
     "node equipment: SC2 bath 10 L, 80 C, 2.479 kWh/d; heater envelope is the "
     "purchased unit per plan rule 6 (BOM row 7)"],
    ["5", "DHF etch bath (inner 120 x 250 x 160, drawn to its bay), wall 10 "
           "(study)", 1, "PVC-U (duty section 3: AQS-STD-002 M1/M2)",
     bm["dhf"], "make (AQS-BOM-SC-001)",
     "node equipment: DHF etch bath, ambient; no bath size stated on the node - "
     "drawn to its bay (hold, WORK_ORDER W12)"],
    ["6", "DIW rinse bath (inner 120 x 250 x 160, drawn to its bay), wall 10 "
           "(study)", 1, "PVC-U (duty section 3: AQS-STD-002 M1/M2)",
     bm["rinse"], "make (AQS-BOM-SC-001)",
     "node equipment: DIW rinse + N2 guns, 0.05 kWh/d; no bath size stated on "
     "the node (hold, WORK_ORDER W12); the N2 gun set is a hand-tool buy row "
     "(row 8), not drawn"],
    ["7", "Immersion heater envelopes in SC1 and SC2", 2,
     "purchased unit (envelope)", mass["heaters"], "buy",
     "node equipment rows carry the energy basis (2.479 kWh/d each, heat-up + "
     "insulated hold per the node note); no per-heater kW rating is stated on "
     "the node or duty - rating hold, WORK_ORDER W12"],
    ["8", "N2 gun set (node equipment row: DIW rinse + N2 guns)", 1,
     "purchased hand tools (not drawn)", 0.0, "buy",
     "node equipment row 0.05 kWh/d; hand tools at the bench, no rating stated "
     "on the node or duty (plan rule 6: named, not invented)"],
    ["9", "Nozzle set per docs-authority/nozzles/WET_BENCH.csv: 11 open-bore tube "
           "stubs (DN15/DN25) drawn polymer per duty section 3, drain and vent "
           "flush at the envelope faces", len(schedule),
     "PVC-U (duty section 3: no metal wetted part)", mass["nozzles"],
     "make (AQS-BOM-SC-001)",
     "issued schedule verbatim; the cable schedule row is carried, never drawn; "
     "atmospheric tube per duty section 4; "
     "stub ODs follow the DN series (the steel pipe table); polymer wall is "
     "the supplier rule (hold, WORK_ORDER W12)"],
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
    [None, "M10 tank-clip bolt + nut", fasteners.grade_for("polymer"), 8,
     "bath bases to the deck clip rail, 2 per bath (count from the model)",
     "polymer joints to the polymer supplier rule; A4-70 hardware observed house "
     "practice; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "deck_mm": list(DECK),
    "plinth_mm": T_PLINTH,
    "baths": {b[0]: {"inner_mm": [b[2], b[3], b[4]], "material": b[5],
                     "xy_mm": [b[1], b[1 + 1]]} for b in BATHS},
}
p["design"] = {
    "service": "WET_BENCH: RCA/etch wet bench - SC1/SC2 at 80 C, DHF etch at "
               "ambient, DIW rinse, on the fab UPW class (duty sections 1 and 3; "
               "node equipment list)",
    "material": "PVC_U (ambient wetted); CPVC (the node 80 C baths)",
    "ca_mm": 0.0,
    "material_basis": "duty section 3: PVC-U wetted per AQS-STD-002 rules M1 and "
                      "M2, no metal wetted part; above 60 C the thermoplastic is "
                      "CPVC, never metal - the node equipment rows give the 80 C "
                      "bath temperatures; the node rows name PP tanks, the duty "
                      "selection governs (plan rule 5; hold, WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; baths on the deck per "
             "params.envelope.baths (SC1 x 60, SC2 x 350, DHF x 640, rinse x 800, "
             "all y 120); hold-down posts at the envelope corners",
    "supports": "plinth + deck + hold-down frame + 8 slab anchors; bath clip rail "
                "(A-MACH)",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 150, 8 mm clear at the "
                     "bore; drain at x 430, vent at x 570; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
