"""WAFER_FAB manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box; the size_note
  points at the cad/stl registry and defers design sizing to the duty sheet, and the
  duty states none - holds, WORK_ORDER W12). A four-post hold-down frame pins the
  registry box so the X-PAR-04 envelope registry reads the build.
- Machine per the node equipment list (the load basis the node names): CZ puller
  (charge heat-up over the 7 d campaign + 4 h hot hold, 0.2317 kW), ingot cool/anneal
  station (N2 circulator duty share, 0.02 kW), crop/grind/edge tools at 5 starts/d
  (0.04 kW), FAB_TOOL dry row parasitics (ox, RTA, metal, probe standby, 0.12 kW) and
  the N2 purge distribution (ISO 14644 Class 6 row, 0.03 kW) drawn as the DN15 header
  with drop legs. Stations are purchased-class tool envelopes per plan rule 6: envelope
  and interface, named with the rating from the node, no invented internals. Station
  arrangement is the layout choice (W12) - the node names stations and ratings, not
  arrangement.
- A-MACH guard and anchors: the four-post hold-down frame is the guard; 8 slab anchors
  in fasteners.csv.
- Nozzles: all rows of docs-authority/nozzles/WAFER_FAB.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: nozzle DN15, no flange class, atmospheric tube or hose). The four
  solids rows (specialty stock, polymer feedstock, dopant in; spent resist and solvent
  out) are non-piped transfer rows drawn DN15, bore not calculated (plan W4). Drain
  flush at the envelope bottom (50 datum); vent flush at the envelope top (800 datum is
  the box top). The schedule rating column (Class 150) is carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_DECK = 20.0                                              # bench deck plate on the plinth
POST = 40.0                                                # hold-down/guard frame section
MAT = "316L"                                               # duty section 3: wetted hardware
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)
RHO_CS = materials.density("CS")

# Station envelopes (node equipment list; arrangement is the layout choice, W12).
STATIONS = [
    ("cz",     "CZ puller (charge heat-up over the 7 d campaign + 4 h hot hold)",
     0.2317, (60.0, 100.0, 40.0, 220.0, 320.0, 520.0)),
    ("ingot",  "ingot cool/anneal station (N2 circulator duty share)",
     0.02, (300.0, 100.0, 40.0, 140.0, 320.0, 320.0)),
    ("sawset", "crop/grind/edge tools at 5 starts/d",
     0.04, (460.0, 100.0, 40.0, 180.0, 320.0, 260.0)),
    ("dryrow", "FAB_TOOL dry row parasitics (ox, RTA, metal, probe standby)",
     0.12, (660.0, 100.0, 40.0, 280.0, 320.0, 200.0)),
]
KW_TOTAL_NODE = 0.4417                                     # total connected (calculated), node

assert L == 1000.0 and W == 600.0 and H == 800.0, "WAFER_FAB node envelope changed"
assert abs(sum(s[2] for s in STATIONS) + 0.03 - KW_TOTAL_NODE) < 1e-9, \
    "station kW figures must sum with the purge row to the node total"
for (x, y, z0, dx, dy, dz) in (s[3] for s in STATIONS):
    assert x >= 40.0 and x + dx <= L - 40.0 and y >= 100.0 and y + dy <= W - 40.0, "station inside posts"
    assert z0 + dz <= 680.0, "station under the top rails"
DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, T_DECK)
# deck faces sit 4 mm inside the post lines: no coplanar T-junction with the frame
assert DECK[3] > 800.0 and DECK[4] > 300.0, "deck carries the station envelopes"


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

# ---------------------------------------------------------------- station envelopes (node equipment)
stations = None
for (_k, _n, _kw, (x, y, z0, dx, dy, dz)) in STATIONS:
    s = box(x, y, z0, dx, dy, dz)
    stations = s if stations is None else stations.union(s)
parts["stations"] = stations

# ---------------------------------------------------------------- N2 purge distribution header + drops
HEAD_Y, HEAD_Z = 470.0, 720.0                              # header line along the row (layout, W12)
hdr = (tube_z("DN15", L - 240.0).rotate((0, 0, 0), (0, 1, 0), 90)
       .translate((120.0, HEAD_Y, HEAD_Z)))
drops = None
for x in (170.0, 370.0, 550.0, 800.0):
    d = tube_z("DN15", HEAD_Z - 240.0).translate((x, HEAD_Y, 240.0))
    drops = d if drops is None else drops.union(d)
parts["purge"] = hdr.union(drops)

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
    if dnl == "cable":                                    # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
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
mass = {k: round(v.val().Volume() * (RHO if k in ("nozzles", "purge") else RHO_CS) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "wafer-fab tool row on a shop bench: bench deck over a 20 mm plinth "
                "inside a four-post hold-down frame that pins the registry box "
                "(X-PAR-04), with the node equipment stations as purchased-class "
                "envelopes per plan rule 6: CZ puller (0.2317 kW), ingot cool/anneal "
                "(0.02 kW), crop/grind/edge tools (0.04 kW), FAB_TOOL dry row "
                "(ox/RTA/metal/probe standby, 0.12 kW); N2 purge distribution as the "
                "DN15 header with four drop legs (ISO 14644 Class 6 row, 0.03 kW)",
        "stations": {s[0]: {"note": s[1], "kw_connected": s[2],
                            "envelope_mm": list(s[3]), "make_or_buy": "buy"}
                     for s in STATIONS},
        "iso_note": "node note carried as text: ISO 14644-1 Class 7 wet bench, "
                    "Class 6 tool row (room-side classification, not modeled hardware)",
        "guard": "four-post hold-down frame (40 x 40 posts, top rails) is the A-MACH "
                 "guard + 8 slab anchors (fasteners.csv)",
        "material": MAT, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet; CA 0 mm "
                          "(AQS-STD-001)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: nozzle DN15, no flange class, atmospheric tube "
                    "or hose); the four solids rows (specialty stock, polymer "
                    "feedstock, dopant in; spent resist and solvent out) are non-piped "
                    "transfers drawn DN15, bore not calculated (plan W4); drain flush "
                    "at the envelope bottom (50 datum), vent flush at the envelope top "
                    "(800 datum is the box top); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Bench deck {DECK[3]:g} x {DECK[4]:g} x {T_DECK:g} over the plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["deck"] + mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; the shop-fabricable bench the station envelopes "
     "mount on"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "HX8 hold-down idiom: the frame pins the registry box so the build fills the "
     "node envelope (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", "N2 purge distribution: DN15 Sch 40 header (x 120..880 at z 720) with "
           "four drop legs to the stations", 1, "316L tube",
     mass["purge"], "make (AQS-BOM-SC-001)",
     "node equipment row: N2 purge distribution (ISO 14644 Class 6 row), 0.03 kW "
     "connected parasitics named on the node"],
    ["4", "CZ puller station envelope (charge heat-up over the 7 d campaign + 4 h "
           "hot hold)", 1, "purchased tool (envelope)", mass["stations"] * 0.45, "buy",
     "node equipment list 0.2317 kW connected; envelope + interface per plan "
     "rule 6, vendor print governs (station masses are study envelopes at carbon-"
     "steel density, apportioned by envelope volume)"],
    ["5", "Ingot cool/anneal station envelope (N2 circulator duty share)", 1,
     "purchased tool (envelope)", mass["stations"] * 0.10, "buy",
     "node equipment list 0.02 kW connected; envelope + interface per plan rule 6"],
    ["6", "Crop/grind/edge tool set envelope (5 starts/d)", 1,
     "purchased tool (envelope)", mass["stations"] * 0.15, "buy",
     "node equipment list 0.04 kW connected; envelope + interface per plan rule 6"],
    ["7", "FAB_TOOL dry row envelope (ox, RTA, metal, probe standby)", 1,
     "purchased tool (envelope)", mass["stations"] * 0.30, "buy",
     "node equipment list 0.12 kW connected parasitics; envelope + interface per "
     "plan rule 6"],
    ["8", "Nozzle set per docs-authority/nozzles/WAFER_FAB.csv: 10 open-bore tube "
           "stubs (DN15/DN25), 4 non-piped solids transfer rows drawn DN15 bore not "
           "calculated, drain and vent flush at the envelope faces",
     len(schedule), "316L tube", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "issued schedule verbatim; the cable schedule row is carried, never drawn; "
     "atmospheric tube per duty section 4"],
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
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "deck_mm": list(DECK),
    "plinth_mm": T_PLINTH,
    "stations": {s[0]: {"envelope_mm": list(s[3]), "kw_connected": s[2]} for s in STATIONS},
}
p["design"] = {
    "service": "WAFER_FAB: the wafer-fab tool row - CZ crystal growth, ingot "
               "cool/anneal, crop/grind/edge, and the dry tool row behind one "
               "envelope; N2 purge on the ISO 14644 Class 6 row (duty sections 1 "
               "and 6; node note)",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: 316L where the stream is wet; CA 0 mm "
                      "(AQS-STD-001)",
    "stations_basis": "node equipment list (the calculated connected load, "
                      "0.4417 kW total): station kW figures are node figures; "
                      "arrangement is the layout choice (WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; station envelopes per "
             "params.envelope.stations (CZ x 60..280, ingot x 300..440, crop/"
             "grind/edge x 460..640, dry row x 660..940, all y 100..420 on the "
             "deck); hold-down posts at the envelope corners",
    "purge": "DN15 header at y 470, z 720 along x 120..880 with drop legs at x "
             "170/370/550/800",
    "supports": "plinth + deck + hold-down frame + 8 slab anchors (A-MACH)",
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
