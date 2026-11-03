"""SOLAR_PV_CELL manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 2400 mm, y along 1200 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 2400 x 1200 x 1600 mm, node size_mm ("L x W x H mm, issued envelope
  (X-MFG-38 tool line)"). The build stays inside it; a four-post hold-down frame on
  the base plate pins the registry box so the X-PAR-04 envelope registry reads the
  build. The duty section 2 envelope line agrees with the node.
- Tool line per the node design block (X-MFG-38, A-M-178, AQS-DUTY-071): seven
  named stations drawn as envelopes with the ratings from the node - PV-TEX-01
  KOH texture bath (10 L, 80 C, immersion heater, 0.687 kWh/d), PV-EMIT-01
  POCl3 diffusion (quartz tube 200 mm x 1.0 m with 200 mm ceramic fibre, taken
  at face value as the fibre thickness), PV-PSG-01 HF PSG etch bath (ambient),
  PV-ARC-01 PECVD SiNx (parallel-plate RF chamber, 5 kg heated platen, dry
  vacuum pump purchased at the A-M-178 1.5 kW basis), PV-CON-01 screen printer
  and 200 C dryer (printer 0.2 kW, dryer 0.5 kW per A-M-178), PV-FIRE-01 IR
  fast-firing furnace (3.0 kW node peak), PV-IV-01 flash IV tester (0.1 kW).
  Station arrangement and every unstated envelope size are the layout choice
  (W12). The node KOH feed is WS_KOH; 3 cells per batch.
- Wetted material per duty section 3 ("316L where the stream is wet"); the node
  station texts name PP tanks - the duty selection governs (plan rule 5) and the
  tension is a named hold (WORK_ORDER W12). The diffusion tube is quartz and the
  screen stainless shop-cut per AQS-PV-001 (`docs-authority/PV_CELL_MOD.md`, the
  PV cell module page the lane names; its 50 mm ID x 800 mm tube figure predates
  the node design 200 mm x 1.0 m and is named, W12).
- A-MACH guard and anchors: the four-post hold-down frame is the guard; 8 slab
  anchors in fasteners.csv.
- Nozzles: all 4 rows of docs-authority/nozzles/SOLAR_PV_CELL.csv drawn at tag,
  face, height and bore: N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is a schedule placeholder under the
  1600 box); N3 (dopant concentrate in) and N4 (dopant into the wafer fab) are
  `solids` transfer rows drawn DN15, bore not calculated (plan W4). Duty
  section 4: atmospheric joints are hose; bore not calculated.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 2400 x 1200 x 1600
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
if isinstance(DS.get("tools"), list) and isinstance(DS.get("machine"), dict):
    DS = DS["machine"]                 # builder-owned nesting from a previous pass
TOOLS = DS.get("tools") or []
assert {t.get("id") for t in TOOLS} == {"PV-TEX-01", "PV-EMIT-01", "PV-PSG-01",
                                        "PV-ARC-01", "PV-CON-01", "PV-FIRE-01",
                                        "PV-IV-01"}, "node design tool table changed"

T_BASE = 20.0                                              # base plate (layout, W12)
POST = 40.0                                                # hold-down/guard frame section
T_WALL = 10.0                                              # bath walls (study, W12)
MAT_WET = "316L"                                           # duty section 3 (wetted baths)
CA = materials.ca_for(MAT_WET)                             # 0.0, AQS-STD-001
RHO_WET = materials.density(MAT_WET)
RHO_CS = materials.density("CS")
RHO_AL = materials.density("aluminium")
RHO_QUARTZ = 2200.0                                        # fused-silica study value (published band)
RHO_FIBRE = 130.0                                          # ceramic-fibre blanket study value (A-M-178 k basis)

# Station envelopes on the deck; arrangement and unstated sizes are the layout choice
# (W12). Ratings and design texts are node figures. (id, x, y, z, dx, dy, dz, mob)
STATIONS = [
    ("PV-TEX-01",  60.0,  90.0, T_BASE, 350.0, 500.0, 200.0, "make"),
    ("PV-EMIT-01", 430.0,  90.0, T_BASE, 1100.0, 600.0, 660.0, "mixed"),
    ("PV-PSG-01", 1550.0,  90.0, T_BASE, 250.0, 400.0, 200.0, "make"),
    ("PV-CON-01", 1820.0,  90.0, T_BASE, 520.0, 400.0, 300.0, "mixed"),
    ("PV-ARC-01",  60.0, 620.0, T_BASE, 600.0, 520.0, 420.0, "mixed"),
    ("PV-FIRE-01", 680.0, 620.0, T_BASE, 400.0, 520.0, 320.0, "mixed"),
    ("PV-IV-01",  1100.0, 620.0, T_BASE, 300.0, 520.0, 220.0, "buy"),
]
# diffusion internals: quartz tube 200 OD x 1000 with a 200 mm fibre annulus (node design
# text taken at face value), centred in the PV-EMIT-01 bay
TUBE_OD, TUBE_WALL, TUBE_LEN = 200.0, 5.0, 1000.0
FIBRE_T = 200.0
EMIT = STATIONS[1]
TUBE_X0 = EMIT[1] + (EMIT[4] - TUBE_LEN) / 2.0             # 480..1480 inside the bay
TUBE_YC = EMIT[2] + EMIT[5] / 2.0                          # tube axis, bay y centre
TUBE_ZC = EMIT[3] + 20.0 + TUBE_OD / 2 + FIBRE_T           # axis height, fibre base 20 off the floor

assert L == 2400.0 and W == 1200.0 and H == 1600.0, "SOLAR_PV_CELL node envelope changed"
for (sid, x, y, z, dx, dy, dz, *_r) in STATIONS:
    assert x >= 44.0 and x + dx <= L - 44.0 and y >= 44.0 and y + dy <= W - 44.0, (sid, "inside the guard")
    assert z + dz <= H - POST - 40.0, (sid, "under the top rails")
assert TUBE_X0 + TUBE_LEN <= EMIT[1] + EMIT[4], "tube inside its bay"
assert TUBE_ZC - (TUBE_OD / 2 + FIBRE_T) >= EMIT[3] and \
       TUBE_ZC + (TUBE_OD / 2 + FIBRE_T) <= EMIT[3] + EMIT[6], "fibre annulus inside its bay"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def vtube(od, x, y, z0, z1):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0)


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- base plate + hold-down/guard frame
parts["base"] = box(0, 0, 0, L, W, T_BASE)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- station envelopes (node tool table)
st_shells = None
for (sid, x, y, z, dx, dy, dz, *_r) in STATIONS:
    b = box(x, y, z, dx, dy, dz)
    st_shells = b if st_shells is None else st_shells.union(b)
parts["stations"] = st_shells

# ---------------------------------------------------------------- PV-EMIT-01 internals (node dims)
quartz = (cq.Workplane("XY").circle(TUBE_OD / 2).circle(TUBE_OD / 2 - TUBE_WALL)
          .extrude(TUBE_LEN).rotate((0, 0, 0), (0, 1, 0), 90)
          .translate((TUBE_X0, TUBE_YC, TUBE_ZC)))
fibre = (cq.Workplane("XY").circle(TUBE_OD / 2 + FIBRE_T).circle(TUBE_OD / 2)
         .extrude(TUBE_LEN).rotate((0, 0, 0), (0, 1, 0), 90)
         .translate((TUBE_X0, TUBE_YC, TUBE_ZC)))
parts["quartz_tube"] = quartz
parts["fibre"] = fibre

# ---------------------------------------------------------------- TEX heater + ARC pump envelopes
TEX = STATIONS[0]
parts["tex_heater"] = box(TEX[1] + 20.0, TEX[2] + 20.0, TEX[3] + T_WALL, 40.0, 40.0, 140.0)
ARC = STATIONS[4]
parts["arc_pump"] = box(ARC[1] + ARC[4] - 220.0, ARC[2] + ARC[5] - 270.0,
                        ARC[3], 200.0, 250.0, 250.0)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    x = 1200.0
    for r in rows:
        layout_x[r["tag"]] = round(x, 1)
        x += 60.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    note = "atmospheric hose joint per duty section 4 (bore not calculated)"
    if r["face"] == "bottom":                             # N1: drain flush at the envelope bottom
        s = tube_z("DN15", T_BASE + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (1200.0, W / 2), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder")
    elif r["face"] == "top":                              # N2: 800 datum predates the 1600 box
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (1200.0, W / 2), (L, W, H))
        note = ("vent flush at the envelope top; the schedule datum 800 mm "
                "predates the 1600 box (hold, WORK_ORDER W12)")
    else:                                                 # N3/N4: solids transfer rows
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, FACE_OF.get(r["face"], r["face"]), h,
                                  (layout_x[tag], W / 2), (L, W, H))
        note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                 "not calculated (plan W4)")
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": FACE_OF.get(r["face"], r["face"]),
                  "height_mm": h,
                  "drawn_height_mm": h if r["face"] in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
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
_m = {"base": RHO_CS, "frame": RHO_CS, "stations": RHO_CS, "quartz_tube": RHO_QUARTZ,
      "fibre": RHO_FIBRE, "tex_heater": RHO_WET, "arc_pump": RHO_CS, "nozzles": RHO_WET}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "in-house PV cell line per the node design block (X-MFG-38, "
                "A-M-178, AQS-DUTY-071): seven named stations drawn as "
                "envelopes with the node ratings, the diffusion station "
                "internally resolved per its node dims (quartz tube 200 mm x "
                "1.0 m with the 200 mm ceramic-fibre annulus taken at face "
                "value), 3 cells per batch, KOH feed from WS_KOH",
        "stations": {s[0]: {"envelope_mm": [s[1], s[2], s[3], s[4], s[5], s[6]],
                            "make_or_buy": s[7],
                            "node_text": next(t.get("design") for t in TOOLS
                                              if t.get("id") == s[0]),
                            "peak_kW": next(t.get("peak_kW") for t in TOOLS
                                            if t.get("id") == s[0])}
                     for s in STATIONS},
        "emit_internals": {"tube": f"quartz OD {TUBE_OD:g} x {TUBE_LEN:g}, wall "
                                   f"{TUBE_WALL:g} study (AQS-PV-001: tube "
                                   "quartz; the node design gives OD and "
                                   "length, not wall - hold W12)",
                           "fibre": f"{FIBRE_T:g} mm annulus (the node design "
                                    "text '200 mm ceramic fibre' taken at "
                                    "face value as the fibre thickness; "
                                    "A-M-178 fibre k basis)",
                           "legacy_note": "AQS-PV-001 rev C carries the older "
                                          "50 mm ID x 800 mm tube figure; "
                                          "the node design 200 mm x 1.0 m "
                                          "governs (hold W12)"},
        "material": MAT_WET, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet; the "
                          "node station texts name PP tanks/baths - the duty "
                          "selection governs (plan rule 5; hold W12); the "
                          "screen is stainless shop-cut and the tube quartz "
                          "per AQS-PV-001 section 3",
        "guard": "four-post hold-down frame (40 x 40 posts, top rails) is the "
                 "A-MACH guard + 8 slab anchors (fasteners.csv)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose joints per duty section 4 (bore not "
                    "calculated); the N3/N4 solids rows are non-piped "
                    "transfers drawn DN15, bore not calculated (plan W4); the "
                    "N2 vent datum 800 predates the 1600 box (hold, W12); the "
                    "schedule rating column (Class 150) carried verbatim as "
                    "text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
skg = {k: mass[k] for k in ("stations", "quartz_tube", "fibre", "tex_heater", "arc_pump")}
rows = [
    ["1", f"Base plate {L:g} x {W:g} x {T_BASE:g} (X-MFG-38 tool-line bench)", 1,
     "carbon steel (ASTM A500)", mass["base"], "make (AQS-BOM-SC-001)",
     "issued envelope frame; anchors in fasteners.csv"],
    ["2", "Hold-down/guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "HX8 hold-down idiom (X-PAR-04); A-MACH guard"],
    ["3", "Station envelopes: PV-TEX-01 KOH texture bath, PV-PSG-01 HF PSG etch "
           "bath, PV-ARC-01 PECVD chamber (with platen), PV-CON-01 screen "
           "printer, PV-FIRE-01 IR furnace housing, PV-IV-01 flash IV tester",
     6, "316L wetted baths (duty section 3); CS envelopes (dry stations)",
     skg["stations"], "mixed (per-station rows below)",
     "node design tool table (design texts and peak kW); envelope sizes are "
     "the layout choice (hold, W12); wetted material per duty section 3 - the "
     "node texts name PP, the duty governs (plan rule 5; hold W12)"],
    ["4", "PV-TEX-01 immersion heater envelope (10 L bath, 80 C)", 1,
     "purchased unit (envelope)", skg["tex_heater"], "buy",
     "node PV-TEX-01 basis 0.687 kWh/d; A-M-178 texture 10 L at 80 C; no "
     "per-heater kW rating stated (hold W12)"],
    ["5", "PV-EMIT-01 quartz diffusion tube OD 200 x 1000, wall 5 (study)", 1,
     "quartz (AQS-PV-001 section 3: tube quartz)", skg["quartz_tube"], "buy",
     "node design dims 200 mm x 1.0 m; A-M-178 diffusion basis 20 kg heated "
     "mass to 850 C; AQS-PV-001 rev C carries the older 50 mm ID x 800 mm "
     "figure - the node governs (hold W12)"],
    ["6", "PV-EMIT-01 ceramic-fibre insulation annulus 200 mm x 1000", 1,
     "ceramic fibre (A-M-178 k basis)", skg["fibre"], "buy",
     "node design text '200 mm ceramic fibre' taken at face value as the "
     "fibre thickness (hold W12)"],
    ["7", "PV-ARC-01 dry vacuum pump envelope", 1, "purchased unit (envelope)",
     skg["arc_pump"], "buy",
     "A-M-178 basis 1.5 kW vacuum pump 1 h; purchased per plan rule 6, rating "
     "from the node design basis"],
    ["8", "Screen print mesh (PV-CON-01, grid 2 mm lines at 10 mm pitch per "
           "AQS-PV-001)", 1, "stainless, shop-cut (AQS-PV-001 section 3)", 0.5,
     "make (AQS-BOM-SC-001)",
     "AQS-PV-001 section 3: screen stainless, shop-cut; mass study figure"],
    ["9", "Purchased drive/heat/electrical sets by node rating: PV-CON-01 "
           "200 C dryer 0.5 kW and printer drive 0.2 kW (A-M-178), PV-FIRE-01 "
           "IR lamp set 3.0 kW (node peak), PV-IV-01 flash IV tester 0.1 kW "
           "(node peak)", 4, "purchased units (envelopes in the station "
     "shells)", 0.0, "buy",
     "ratings from the node design tool table and A-M-178; purchased per plan "
     "rule 6, not drawn beyond their station envelopes"],
    ["10", "Nozzle set per docs-authority/nozzles/SOLAR_PV_CELL.csv: drain and "
            "vent flush at the envelope faces; the two solids transfer rows "
            "drawn DN15 bore not calculated", len(schedule),
     "316L (duty section 3)", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "4-row issued schedule verbatim; atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "base plate to the slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed "
     "at fabrication"],
    [None, "M10 tube-stand bolt", fasteners.grade_for("316L"), 4,
     "diffusion tube stands to the deck, 2 per stand (count from the model)",
     "A4-70 on the 316L-adjacent hot bay hardware per the grade rule; study "
     "pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "stations": {s[0]: {"envelope_mm": [s[1], s[2], s[3], s[4], s[5], s[6]],
                        "make_or_buy": s[7]} for s in STATIONS},
    "emit_tube_mm": {"od": TUBE_OD, "wall": TUBE_WALL, "len": TUBE_LEN,
                     "fibre": FIBRE_T, "x0": TUBE_X0, "axis_yz": [TUBE_YC, TUBE_ZC]},
}
p["design"] = dict(DS)
p["design"].update({
    "service": "SOLAR_PV_CELL: in-house PV cell line - texture, POCl3 "
               "diffusion, PSG etch, PECVD SiNx, screen print, fast firing, "
               "IV; 3 cells per batch; KOH feed from WS_KOH (node design "
               "block; X-MFG-38, A-M-178, AQS-DUTY-071)",
    "material": "316L wetted baths (duty section 3); quartz tube and ceramic "
                "fibre at PV-EMIT-01; CS bench and dry envelopes",
    "material_basis": "duty section 3: 316L where the stream is wet - the "
                      "node station texts name PP tanks/baths, the duty "
                      "selection governs (plan rule 5; hold, WORK_ORDER W12); "
                      "tube quartz and screen stainless shop-cut per "
                      "AQS-PV-001 section 3",
})
p["layout"] = {
    "frame": "origin at the envelope corner; station rows on the deck per "
             "params.envelope.stations (TEX/EMIT/PSG/CON on y 90, ARC/FIRE/IV "
             "on y 620); hold-down posts at the envelope corners",
    "supports": "base plate + hold-down frame + 8 slab anchors; tube stands",
    "nozzle_spread": "the two solids rows at x 1200 on their faces; drain and "
                     "vent at x 1200 flush at the bottom/top; per-tag notes "
                     "in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
