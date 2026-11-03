"""BMED_UPW_POLISH manufacturing model, AQS-PLAN-006 work order (X-MFG-34, tier 4, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box; the duty
  states no envelope). A four-post hold-down frame on the 20 mm plinth pins the
  registry box so the X-PAR-04 envelope registry reads the build.
- Skid per the node internals row ("potable bypass; 2 x flat-sheet RO module, 2 x
  EDI stack, UV-TOC lamp") and the node design block (X-MFG-34, A-M-176,
  AQS-DUTY-070): the named internals are drawn as purchased-module envelopes per
  plan rule 6 - 2 flat-sheet TFC RO modules (membrane_m2 0.2652, modules 2, feed
  6.859 bar per the node design; A-M-176 basis 0.27 m2 per module at 6.9 bar,
  rejection 0.98, recovery 0.9547), 2 EDI stacks (EDI_A 0.00973 A / 0.39 W;
  A-M-176 basis 10 cell pairs at 4 V), the UV-TOC lamp (UV_kW 0.015 = 15 W), the
  RO pump envelope (2.6 W, node continuous-kW note), and the potable bypass run
  (bypass_kg_d 206.77 - the potable share bypasses RO/EDI per A-M-176, 2 x 100 %
  trains). Module and pump envelope sizes and the piping layout are the layout
  choice (W12); the module internals are the X-MFG-34 in-house design task and are
  not invented. The vendor-class energy bases (RO 3.0 / EDI 0.5 kWh/m3, A-M-072)
  stay a named hold pending the X-MFG-34 bench test.
- Wetted hardware 316L per duty section 3 (UPW service); CA 0 mm.
- A-MACH guard and anchors: the hold-down frame is the guard; 8 slab anchors in
  fasteners.csv.
- Nozzles: all 7 rows of docs-authority/nozzles/BMED_UPW_POLISH.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the envelope
  faces: N1 DN50 VCD distillate in on -Y at z 160; N2 DN25 UPW, N3 DN25 fab UPW,
  N4 DN15 remineralizer and N5 DN15 polish reject on +Y at z 600; N6 drain flush
  at the envelope bottom (50 datum); N7 vent flush at the envelope top (800 datum
  is the box top). Duty section 4: atmospheric joints are hose, bore not
  calculated.
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
DS = P.get("design") or {}

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_DECK = 20.0                                              # skid deck on the plinth
POST = 40.0                                                # hold-down/guard frame section
MAT = "316L"                                               # duty section 3 (UPW service)
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)
RHO_CS = materials.density("CS")
RHO_GLASS = materials.density("borosilicate")

N_MODULES = int(DS.get("modules") or 2)                    # node design: modules 2
RO_OD, RO_H = 120.0, 500.0                                 # RO module envelope (layout, W12)
EDI_W, EDI_H = 150.0, 400.0                                # EDI stack envelope (layout, W12)
UV_OD, UV_LEN = 30.0, 400.0                                # UV-TOC lamp envelope (layout, W12)
BYPASS_KGD = float(DS.get("bypass_kg_d") or 206.77)        # node design (potable share)
DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, T_DECK)

assert L == 1000.0 and W == 600.0 and H == 800.0, "BMED_UPW_POLISH node envelope changed"
assert N_MODULES == 2, "node design module count changed"
assert "RO module" in (P.get("internals") or ""), "node internals row changed"

# internals on the deck (layout, W12): (key, x, y, z, dx, dy, dz)
RO1 = (140.0, 120.0, T_PLINTH + T_DECK, RO_OD, RO_OD, RO_H)
RO2 = (300.0, 120.0, T_PLINTH + T_DECK, RO_OD, RO_OD, RO_H)
EDI1 = (470.0, 120.0, T_PLINTH + T_DECK, EDI_W, EDI_W, EDI_H)
EDI2 = (650.0, 120.0, T_PLINTH + T_DECK, EDI_W, EDI_W, EDI_H)
PUMP = (60.0, 400.0, T_PLINTH + T_DECK, 120.0, 120.0, 150.0)
UVL = (470.0, 330.0, T_PLINTH + T_DECK, UV_LEN, UV_OD, UV_OD)
for (x, y, z, dx, dy, dz) in (RO1, RO2, EDI1, EDI2, PUMP, UVL):
    assert x + dx <= L - POST - 4.0 and y + dy <= W - POST - 4.0, "inside the deck"
    assert z + dz <= H - POST - 20.0, "under the top rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def tube_x(od, x0, length, y, z):
    return (cq.Workplane("XY").circle(od / 2).extrude(length)
            .rotate((0, 0, 0), (0, 1, 0), 90)
            .translate((x0, y, z)))


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

# ---------------------------------------------------------------- internals (node row, rule 6 envelopes)
ro = None
for (x, y, z, dx, dy, dz) in (RO1, RO2):
    b = box(x, y, z, dx, dy, dz)
    ro = b if ro is None else ro.union(b)
parts["ro_modules"] = ro                                   # 2 x flat-sheet RO module
edi = None
for (x, y, z, dx, dy, dz) in (EDI1, EDI2):
    b = box(x, y, z, dx, dy, dz)
    edi = b if edi is None else edi.union(b)
parts["edi_stacks"] = edi
parts["uv_lamp"] = box(*UVL)                               # UV-TOC lamp envelope
parts["ro_pump"] = box(*PUMP)                              # RO pump envelope (2.6 W)

# ---------------------------------------------------------------- potable bypass run (node internals row)
BYP_Y, BYP_Z = 470.0, 260.0
bypass = tube_x(dn.pipe_od("DN25"), 80.0, L - 160.0, BYP_Y, BYP_Z)
bypass = bypass.union(tube_z("DN25", BYP_Z - T_PLINTH + 4.0)
                      .translate((80.0, BYP_Y, T_PLINTH)))
bypass = bypass.union(tube_z("DN25", BYP_Z - T_PLINTH + 4.0)
                      .translate((L - 80.0, BYP_Y, T_PLINTH)))
parts["bypass"] = bypass

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
    if r["face"] == "bottom":                             # N6: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N7: 800 datum is the box top
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
_m = {"plinth": RHO_CS, "deck": RHO_CS, "frame": RHO_CS, "ro_modules": RHO_CS,
      "edi_stacks": RHO_CS, "uv_lamp": RHO_GLASS, "ro_pump": RHO_CS,
      "bypass": RHO, "nozzles": RHO}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "UPW polish skid per the node internals row and design block "
                "(X-MFG-34, A-M-176, AQS-DUTY-070): 2 flat-sheet TFC RO "
                "module envelopes (membrane_m2 0.2652, feed 6.859 bar, "
                "recovery 0.9547 per the node design; A-M-176 basis 0.27 "
                "m2/module at 6.9 bar), 2 EDI stack envelopes (EDI_A 0.00973 "
                "A / 0.39 W; A-M-176 basis 10 cell pairs at 4 V), the UV-TOC "
                "lamp envelope (15 W), the RO pump envelope (2.6 W), and the "
                "potable bypass run (bypass_kg_d 206.77, the potable share "
                "bypasses RO/EDI, 2 x 100 % trains per A-M-176)",
        "internals_solid": "every named internal is a solid envelope per plan "
                           "rule 6; the module internals are the X-MFG-34 "
                           "in-house design task and are not invented (hold, "
                           "WORK_ORDER W12)",
        "vendor_basis_hold": "A-M-072 (RO 3.0 / EDI 0.5 kWh/m3) is the "
                             "vendor-class energy basis, replaced by the "
                             "X-MFG-34 in-house design and bench test - named "
                             "hold, WORK_ORDER W12",
        "material": MAT, "ca_mm": CA,
        "material_basis": "duty section 3: 316L where the stream is wet (UPW "
                          "service); CA 0 mm (AQS-STD-001)",
        "guard": "hold-down frame (40 x 40 posts, top rails) on the 20 mm "
                 "plinth is the A-MACH guard + 8 slab anchors (fasteners.csv)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope "
                    "faces (duty section 4: atmospheric joints are hose, bore "
                    "not calculated); N1 DN50 VCD distillate in on -Y at z "
                    "160; the four product/reject rows on +Y at z 600; drain "
                    "and vent flush at the envelope faces; the schedule "
                    "rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Skid deck {DECK[3]:g} x {DECK[4]:g} x {T_DECK:g} over the plinth "
          f"{L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["deck"] + mass["plinth"], "make",
     "AQS-MOD-002 dry service; dry structure outside the wetted 316L hardware"],
    ["2", "Hold-down/guard frame pinning the "
          f"{L:g} x {W:g} x {H:g} envelope (40 x 40 posts, top rails)", 1,
     "carbon steel (ASTM A500)", mass["frame"], "make",
     "HX8 hold-down idiom (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", f"Flat-sheet TFC RO module envelopes, {RO_OD:g} dia x {RO_H:g} (2 off, "
           "one per train)", N_MODULES, "purchased module (envelope)",
     mass["ro_modules"], "buy",
     "node design: membrane_m2 0.2652, modules 2, feed 6.859 bar, recovery "
     "0.9547; A-M-176 basis 0.27 m2/module at 6.9 bar, rejection 0.98; "
     "module internals are the X-MFG-34 design task (plan rule 6 envelope, "
     "hold W12)"],
    ["4", f"EDI stack envelopes, {EDI_W:g} x {EDI_W:g} x {EDI_H:g} (2 off, one "
           "per train)", N_MODULES, "purchased module (envelope)",
     mass["edi_stacks"], "buy",
     "node design EDI_A 0.00973 A / EDI_kW 0.000389; A-M-176 basis 10 cell "
     "pairs at 4 V; X-MFG-34 design task (hold W12)"],
    ["5", "UV-TOC lamp envelope", 1, "purchased lamp (quartz sleeve)",
     mass["uv_lamp"], "buy",
     "node design UV_kW 0.015 (15 W; A-M-176 basis); purchased per plan "
     "rule 6, rating from the node"],
    ["6", "RO pump envelope", 1, "purchased pump (envelope)", mass["ro_pump"],
     "buy",
     "node continuous-kW note: RO pump 2.6 W at the 6.859 bar feed (design "
     "block); purchased per plan rule 6, rating from the node"],
    ["7", "Potable bypass run DN25 Sch 40 with risers (the potable share "
           "bypasses RO/EDI)", 1, "316L tube", mass["bypass"], "make",
     "node internals row 'potable bypass' and design bypass_kg_d 206.77; "
     "A-M-176: the potable share bypasses, 2 x 100 % trains"],
    ["8", "Nozzle set per docs-authority/nozzles/BMED_UPW_POLISH.csv: N1 DN50 "
           "in on -Y, the four product/reject rows on +Y, drain and vent "
           "flush at the envelope faces", len(schedule), "316L tube",
     mass["nozzles"], "make",
     "7-row issued schedule verbatim; atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed "
     "at fabrication"],
    [None, "M8 module-clip bolt", fasteners.grade_for("316L"), 8,
     "RO/EDI modules and the pump to the deck clip rail (count from the model)",
     "A4-70 on the 316L-adjacent hardware per the grade rule; study pattern, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "deck_mm": list(DECK),
    "plinth_mm": T_PLINTH,
    "internals_mm": {"ro1": list(RO1), "ro2": list(RO2), "edi1": list(EDI1),
                     "edi2": list(EDI2), "uv_lamp": list(UVL), "ro_pump": list(PUMP)},
    "bypass_run_mm": {"y": BYP_Y, "z": BYP_Z, "dn": "DN25"},
}
p["design"] = {
    "service": "BMED_UPW_POLISH: RO/EDI polish of VCD distillate to UPW - "
               "2 x 100 % trains (flat-sheet TFC RO then EDI, UV-TOC on the "
               "product), potable share bypasses; reject to the water line "
               "(node internals row and design block; X-MFG-34, A-M-176, "
               "AQS-DUTY-070)",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: 316L where the stream is wet (UPW "
                      "service); CA 0 mm (AQS-STD-001)",
    "vendor_basis": "A-M-072 RO 3.0 / EDI 0.5 kWh/m3 vendor-class energy "
                    "bases - replaced by the X-MFG-34 in-house design and "
                    "bench test (hold, WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; internals on the deck per "
             "params.envelope.internals_mm (RO x 140/300, EDI x 470/650, UV "
             "lamp x 470..870 at y 330, pump x 60..180 at y 400); hold-down "
             "posts at the envelope corners",
    "bypass": "DN25 run at y 470, z 260 along x 80..920 with risers to the "
              "deck at both ends",
    "supports": "plinth + deck + hold-down frame + 8 slab anchors; module "
                "clip rail (A-MACH)",
    "nozzle_spread": "the schedule gives face and height only; ports pack in "
                     "one row per face/height group from x 150, 8 mm clear "
                     "at the bore; drain at x 430, vent at x 570; per-tag "
                     "positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
