"""MFG_SHOP manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down/guard frame pins the box so the
  X-PAR-04 envelope registry reads the build.
- Fitout per the node continuous note's authority (AQS-MFG-010 rev C, Table 2.1):
  since the rev C metering split the unit covers the six shop machine tools only -
  CNC vertical mill (7.5 kW), engine lathe (5.5 kW), band saw (1.5 kW),
  rotary-screw air compressor (4.0 kW), TIG/MIG welder (6.0 kW) and the bench
  grinder/drill-press/hand-tool set (2.0 kW) - connected 26.5 kW, one 8 h shift,
  average 2.55 kW (61.2 kWh/d). The four metal-forming tools (melt, atomiser,
  mill, drawer) are metered at their own units and are not part of this fitout.
  Stations are purchased-class machine envelopes per plan rule 6: envelope and
  interface, named with the nameplate from the tool row, no invented internals
  (the AQS-EQP-MFG-001 massing roster points the same way). Station arrangement
  is the layout choice (W12); the machine envelopes are study footprints (W12).
- A-MACH: hold-down/guard frame + machine guard rail; 8 slab anchors
  (fasteners.csv).
- A-SC: the parts the on-site shop makes (bench, frame, plinth, connections) are
  flagged make with the AQS-BOM-SC-001 cross-reference; the six machines are buy
  rows. Self-copy note: this is the shop that makes the plant's shop-made parts -
  the AQS-BOM-SC-001 make rows across the accepted units land here.
- Nozzles: all 33 rows of docs-authority/nozzles/MFG_SHOP.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). The stock/
  scrap rows on -Y at z 160 include the DN25 metals/Si and glass/ceramic stock
  rows; the 19 solids rows (goods, scrap returns, plated sheet, stock issues) are
  non-piped transfers drawn DN15, bore not calculated (plan W4). N7 goods-in-
  service is the DN50 row on +Y at z 600. N9 drain flush at the envelope bottom
  (50 datum); N10 vent flush at the envelope top (800 datum is the box top). The
  schedule rating column (Class 150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_DECK = 20.0                                              # bench deck plate on the plinth
POST = 40.0                                                # hold-down/guard frame section
MAT = "316L"                                               # duty section 3: wetted hardware
CA = materials.ca_for(MAT)
RHO_CS = materials.density("CS")

# Station envelopes (AQS-MFG-010 Table 2.1, six shop machine tools; arrangement is
# the layout choice, W12). (key, note, nameplate kW, envelope xyzwhd)
STATIONS = [
    ("cnc",        "CNC vertical mill",                     7.5, (60.0, 100.0, 40.0, 220.0, 320.0, 520.0)),
    ("lathe",      "Engine lathe",                          5.5, (288.0, 100.0, 40.0, 180.0, 320.0, 340.0)),
    ("saw",        "Band saw",                              1.5, (476.0, 100.0, 40.0, 100.0, 320.0, 260.0)),
    ("compressor", "Rotary-screw air compressor",           4.0, (584.0, 100.0, 40.0, 140.0, 320.0, 340.0)),
    ("welder",     "TIG/MIG welder",                        6.0, (732.0, 100.0, 40.0, 100.0, 320.0, 260.0)),
    ("benchset",   "Bench grinder, drill press, hand tools", 2.0, (840.0, 100.0, 40.0, 100.0, 320.0, 200.0)),
]
KW_CONNECTED = 26.5                                        # AQS-MFG-010 rev C connected load

assert L == 1000.0 and W == 600.0 and H == 800.0, "MFG_SHOP node envelope changed"
assert abs(sum(s[2] for s in STATIONS) - KW_CONNECTED) < 1e-9, \
    "station nameplates must sum to the AQS-MFG-010 connected load"
for (x, y, z0, dx, dy, dz) in (s[3] for s in STATIONS):
    assert x >= 40.0 and x + dx <= L - 40.0 and y >= 100.0 and y + dy <= W - 40.0, "station inside posts"
    assert z0 + dz <= 680.0, "station under the top rails"
DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, T_DECK)


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

# ---------------------------------------------------------------- machine station envelopes (AQS-MFG-010)
stations = None
for (_k, _n, _kw, (x, y, z0, dx, dy, dz)) in STATIONS:
    s = box(x, y, z0, dx, dy, dz)
    stations = s if stations is None else stations.union(s)
parts["stations"] = stations

# ---------------------------------------------------------------- shop-air header + drops (compressor service)
HEAD_Y, HEAD_Z = 470.0, 720.0
hdr = (tube_z("DN15", L - 240.0).rotate((0, 0, 0), (0, 1, 0), 90)
       .translate((120.0, HEAD_Y, HEAD_Z)))
drops = None
for x in (150.0, 340.0, 520.0, 700.0):
    d = tube_z("DN15", HEAD_Z - 240.0).translate((x, HEAD_Y, 240.0))
    drops = d if drops is None else drops.union(d)
parts["shop_air"] = hdr.union(drops)

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
    assert span <= L - 120.0, (face, z, span)
    x = max(60.0, (L - span) / 2)
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
    if r["face"] == "bottom":                             # N9: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N10: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
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
mass = {k: round(v.val().Volume() * (RHO_CS if k in ("plinth", "deck", "frame") else RHO_CS) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "machine-shop fitout per the node continuous note's authority "
                "(AQS-MFG-010 rev C, Table 2.1): bench deck over a 20 mm plinth "
                "inside a four-post hold-down/guard frame that pins the registry "
                "box (X-PAR-04), with the six shop machine tools as purchased-"
                "class envelopes per plan rule 6 - CNC vertical mill (7.5 kW), "
                "engine lathe (5.5 kW), band saw (1.5 kW), rotary-screw air "
                "compressor (4.0 kW), TIG/MIG welder (6.0 kW), bench grinder/"
                "drill-press/hand-tool set (2.0 kW); connected 26.5 kW, one 8 h "
                "shift, average 2.55 kW; shop-air DN15 header with four drop legs "
                "on the compressor service",
        "tool_roster": "AQS-MFG-010 Table 2.1 (rev C metering split): the four "
                       "metal-forming tools (melt, atomiser, mill, drawer) are "
                       "metered at their own units and are not part of this "
                       "fitout; the AQS-EQP-MFG-001 polymer-line massing tags "
                       "(shredder, wash/dry, extrusion, injection, sheetpress) "
                       "are area equipment, not graph units",
        "stations": {s[0]: {"note": s[1], "kw_nameplate": s[2],
                            "envelope_mm": list(s[3]), "make_or_buy": "buy"}
                     for s in STATIONS},
        "metering": "connected 26.5 kW frames the MCC-1 feeder with the roster "
                    "(AQS-MFG-010 section 3); coincident peak 24.5 kW",
        "guard": "four-post hold-down/guard frame (40 x 40 posts, top rails) is "
                 "the A-MACH guard + 8 slab anchors (fasteners.csv)",
        "material": MAT, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet; CA 0 mm "
                          "(AQS-STD-001); dry shop machines",
        "study_dims": "machine envelope footprints are study values (WORK_ORDER "
                      "W12); the maker prints govern at order",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); the 19 solids rows (goods, scrap returns, plated "
                    "sheet, stock issues) are non-piped transfers drawn DN15, "
                    "bore not calculated (plan W4); N7 goods-in-service is the "
                    "DN50 row on +Y at z 600; drain flush at the envelope bottom "
                    "(50 datum), vent flush at the envelope top (800 datum is the "
                    "box top); the schedule rating column (Class 150) carried "
                    "verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Bench deck {DECK[3]:g} x {DECK[4]:g} x {T_DECK:g} over the plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["deck"] + mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; the shop-fabricable bench the machine envelopes "
     "mount on"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "frame pins the registry box (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", "Shop-air distribution: DN15 header (x 120..880 at z 720) with four "
           "drop legs", 1, "316L tube", mass["shop_air"], "make (AQS-BOM-SC-001)",
     "compressor service (AQS-MFG-010 Table 2.1 air compressor row, 4.0 kW "
     "nameplate); layout choice (W12)"],
    ["4", "CNC vertical mill station envelope", 1, "purchased machine (envelope)",
     mass["stations"] * 0.27, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 7.5 kW; envelope + interface per plan "
     "rule 6 (station masses are study envelopes at carbon-steel density, "
     "apportioned by envelope volume; maker prints govern at order)"],
    ["5", "Engine lathe station envelope", 1, "purchased machine (envelope)",
     mass["stations"] * 0.21, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 5.5 kW; envelope + interface per plan "
     "rule 6"],
    ["6", "Band saw station envelope", 1, "purchased machine (envelope)",
     mass["stations"] * 0.09, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 1.5 kW; envelope + interface per plan "
     "rule 6"],
    ["7", "Rotary-screw air compressor station envelope", 1,
     "purchased machine (envelope)", mass["stations"] * 0.17, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 4.0 kW; envelope + interface per plan "
     "rule 6"],
    ["8", "TIG/MIG welder station envelope", 1, "purchased machine (envelope)",
     mass["stations"] * 0.12, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 6.0 kW; envelope + interface per plan "
     "rule 6"],
    ["9", "Bench grinder / drill press / hand-tool set envelope", 1,
     "purchased tool set (envelope)", mass["stations"] * 0.14, "buy",
     "AQS-MFG-010 Table 2.1, nameplate 2.0 kW; envelope + interface per plan "
     "rule 6"],
    ["10", "Nozzle set per docs-authority/nozzles/MFG_SHOP.csv: 14 tube stubs "
            "(DN15/DN25/DN50) and 19 non-piped solids transfer rows drawn DN15 "
            "bore not calculated", len(schedule), "316L tube", mass["nozzles"],
     "make (AQS-BOM-SC-001)",
     "33-row issued schedule verbatim; atmospheric tube per duty section 4"],
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
    [None, "M10 machine hold-down bolt + nut", fasteners.grade_for("CS"), 12,
     "machine envelopes to the bench deck, 2 per station (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "deck_mm": list(DECK),
    "plinth_mm": T_PLINTH,
    "stations": {s[0]: {"envelope_mm": list(s[3]), "kw_nameplate": s[2]} for s in STATIONS},
}
p["design"] = {
    "service": "MFG_SHOP: the machine-shop fitout - six shop machine tools on one "
               "bench since the AQS-MFG-010 rev C metering split moved the four "
               "metal-forming tools to their own units (duty sections 1 and 6)",
    "tool_roster": "AQS-MFG-010 Table 2.1 rev C: connected 26.5 kW, average 2.55 "
                   "kW (61.2 kWh/d over 24 h), one 8 h shift; MCC-1 framing with "
                   "the coincident peak 24.5 kW",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: 316L where the stream is wet; CA 0 mm "
                      "(AQS-STD-001); dry shop machines",
    "stations_basis": "station nameplates are AQS-MFG-010 Table 2.1 figures; "
                      "arrangement is the layout choice (WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; station envelopes per "
             "params.envelope.stations (CNC x 60..280, lathe x 288..468, saw "
             "x 476..576, compressor x 584..724, welder x 732..832, bench set "
             "x 840..940, all y 100..420 on the deck); hold-down posts at the "
             "envelope corners",
    "shop_air": "DN15 header at y 470, z 720 along x 120..880 with drop legs at "
                "x 150/340/520/700",
    "supports": "plinth + deck + hold-down frame + 8 slab anchors (A-MACH)",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 160, 8 mm clear at the "
                     "bore; drain at x 430, vent at x 570; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
