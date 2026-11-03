"""LITHO_ALIGN manufacturing model, AQS-PLAN-006 work order (fab lane, tier 7, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 600 x 800 mm, node size_mm ("L x W x H mm, AQS-LITH-001 rev C
  frame 6061"). The build stays inside it; a four-post guard frame on the base
  plate pins the registry box so the X-PAR-04 envelope registry reads the build.
  The duty section 2 prose still carries the seed figure "Envelope 500 x 500 x
  800 mm" - the node governs and the older figure is named (holds, WORK_ORDER
  W12, the WS_SOLV precedent).
- Machine per the node design block and its equipment authority AQS-LITH-001
  (`docs-authority/ALIGNER.md` rev C, named on the node): contact aligner, 365 nm
  LED array at 1 W optical (purchased per plan rule 6, rating from the node),
  200 mJ/cm2 dose (10 mW/cm2 x 20 s), 100 mm field; stage aluminium with the
  4140 leadscrew 10 mm at 1 mm pitch (shop-cut on the lathe per AQS-LITH-001
  section 2 - make); mask chrome on glass, 100 um pattern, cut on the mill
  (make). Frame 6061 per AQS-LITH-001 section 3. Stage/leadscrew/mask envelopes
  are named-part envelopes; their unstated plate sizes are the layout choice
  (W12). Not a stepper (node note).
- Guard and anchors: four-post guard frame (6061, 40 x 40 posts + top rails) on
  the base plate; anchors in fasteners.csv. (The class carries a section 4 route
  hold - no F-MACH row names `aligner` - so the acceptance set is A-core + A-SC;
  the guard and anchor hardware is drawn per the machine practice the lane
  applies.)
- Nozzles: both rows of docs-authority/nozzles/LITHO_ALIGN.csv drawn at tag,
  face and bore: N1 drain flush at the envelope bottom (50 datum), N2 vent flush
  at the envelope top (800 datum is the box top). Duty section 4: "No present
  edge. No nozzle." - the two schedule rows are the envelope hardware rows;
  atmospheric, hose per the duty. AQS-LITH-001 section 4 names one SB350 hose
  barb as the machine service interface; it is not a schedule row and is not
  drawn (named, WORK_ORDER W12).
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}
_mach = DS.get("machine")
if isinstance(_mach, dict):            # builder-owned nesting from a previous pass
    DS = _mach
assert DS.get("machine") == "contact aligner", "node design block changed"

T_BASE = 20.0                                              # 6061 base plate (layout, W12)
POST = 40.0                                                # guard frame section
RHO_AL = materials.density("aluminium")
RHO_4140 = materials.density("tool_steel")
RHO_GLASS = materials.density("borosilicate")

# Named-part envelopes (AQS-LITH-001 section 2-3 + node design; plate sizes are the
# layout choice, W12). (key, x, y, z, dx, dy, dz)
STAGE = (420.0, 220.0, T_BASE + 20.0, 160.0, 160.0, 15.0)      # stage plate, aluminium
LEAD = (140.0, 295.0, T_BASE + 10.0, 800.0, 10.0, 10.0)        # leadscrew 4140, 10 mm dia
HOLDER = (400.0, 200.0, 120.0, 200.0, 200.0, 8.0)              # mask holder
MASK = (420.0, 220.0, 128.0, 160.0, 160.0, 3.0)                # mask glass (chrome on glass)
LED = (430.0, 240.0, 190.0, 120.0, 120.0, 60.0)                # 365 nm LED array envelope (purchased)

assert L == 1200.0 and W == 600.0 and H == 800.0, "LITHO_ALIGN node envelope changed"
for (x, y, z, dx, dy, dz) in (STAGE, LEAD, HOLDER, MASK, LED):
    assert x >= 44.0 and x + dx <= L - 44.0 and y >= 44.0 and y + dy <= W - 44.0, "inside the guard"
    assert z + dz <= H - POST - 20.0, "under the top rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_x(d, length, y, z, x0):
    return (tube_z_x(d, length)
            .translate((x0, y - d / 2, z - d / 2)))


def tube_z_x(d, length):
    return cq.Workplane("XY").circle(d / 2).extrude(length).rotate((0, 0, 0), (0, 1, 0), 90)


parts = {}

# ---------------------------------------------------------------- base plate + guard frame (6061)
parts["base"] = box(0, 0, 0, L, W, T_BASE)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- stage, leadscrew, mask, LED head
parts["stage"] = box(*STAGE)
parts["leadscrew"] = tube_x(10.0, LEAD[3], LEAD[1] + 5.0, LEAD[2] + 5.0, LEAD[0])
parts["mask_holder"] = box(*HOLDER)
parts["mask"] = box(*MASK)
parts["led_head"] = box(*LED)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


schedule = P["nozzles"]
noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    note = "atmospheric hose joint per duty section 4"
    if r["face"] == "bottom":                             # N1: drain flush at the envelope bottom
        s = tube_z("DN15", T_BASE + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = ("drain flush at the envelope bottom; 50 datum is the schedule "
                "placeholder; duty section 4: no present process edge")
    elif r["face"] == "top":                              # N2: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (770.0, W / 2), (L, W, H))
        note = ("vent flush at the envelope top; schedule datum 800 mm is the "
                "box top; the AQS-LITH-001 section 4 SB350 hose barb is the "
                "machine service interface, not a schedule row (W12)")
    else:
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "-Y", h, (600.0, W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": r["face"],
                  "height_mm": h,
                  "drawn_height_mm": h if r["face"] in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
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
_m = {"base": RHO_AL, "frame": RHO_AL, "stage": RHO_AL, "leadscrew": RHO_4140,
      "mask_holder": RHO_AL, "mask": RHO_GLASS, "led_head": RHO_AL, "nozzles": RHO_AL}
mass = {k: round(v.val().Volume() * _m[k] / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "contact aligner per the node design block and AQS-LITH-001 rev "
                "C (named on the node): 6061 frame and base, aluminium stage "
                "plate, 4140 leadscrew 10 mm at 1 mm pitch (shop-cut on the "
                "lathe), chrome-on-glass mask with the 100 um pattern (cut on "
                "the mill), and the 365 nm LED array envelope (1 W optical) "
                "above the mask; 200 mJ/cm2 dose over the 100 mm field",
        "duty_line": "duty section 2 prose carries the seed figure 500 x 500 x "
                     "800; the node 1200 x 600 x 800 governs (hold, WORK_ORDER "
                     "W12, WS_SOLV precedent)",
        "parts": {"stage": "aluminium (AQS-LITH-001 section 3; plate size is "
                           "the layout choice around the 100 mm field, W12)",
                  "leadscrew": "4140, 10 mm dia, 1 mm pitch, cut on the lathe "
                               "(AQS-LITH-001 section 2; make)",
                  "mask": "chrome on glass, 100 um pattern, cut on the mill "
                          "(AQS-LITH-001 section 2; the pattern coating is not "
                          "a solid)",
                  "led_head": "365 nm LED array, 1 W optical (node design "
                              "source) - purchased envelope per plan rule 6"},
        "guard": "four-post guard frame (6061, 40 x 40 posts + top rails) on "
                 "the base plate pins the registry box (X-PAR-04); anchors in "
                 "fasteners.csv",
        "material_rule": "frame 6061 per AQS-LITH-001 section 3; duty section "
                         "3 (316L where the stream is wet) has nothing to "
                         "match: mass in and out are zero, the machine is dry",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "both schedule rows are envelope hardware rows drawn flush "
                    "at the envelope faces (duty section 4: 'No present edge. "
                    "No nozzle.'); the AQS-LITH-001 section 4 SB350 hose barb "
                    "is the machine service interface and is not a schedule "
                    "row (named, W12); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Base plate {L:g} x {W:g} x {T_BASE:g} (6061, AQS-LITH-001 section 3 "
           "frame)", 1, "aluminium 6061", mass["base"], "make (AQS-BOM-SC-001)",
     "equipment authority AQS-LITH-001 rev C (named on the node); anchors in "
     "fasteners.csv"],
    ["2", "Guard frame: four 40 x 40 posts + top rails pinning the "
          f"{L:g} x {W:g} x {H:g} envelope", 1, "aluminium 6061",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "machine guard practice (A-MACH hardware drawn); the frame pins the "
     "registry box (X-PAR-04)"],
    ["3", "Stage plate 160 x 160 x 15 (envelope around the 100 mm field)",
     1, "aluminium (AQS-LITH-001 section 3: stage aluminum)",
     mass["stage"], "make (AQS-BOM-SC-001)",
     "named part, no plate size stated - layout choice (hold, W12)"],
    ["4", "Leadscrew 10 mm dia, 1 mm pitch, x 140..940", 1,
     "steel 4140 (AQS-LITH-001 section 3)", mass["leadscrew"],
     "make (AQS-BOM-SC-001)",
     "AQS-LITH-001 section 2: leadscrew cut on the lathe; 10 um repeatability "
     "read by a dial, not an encoder"],
    ["5", "Mask holder 200 x 200 x 8", 1, "aluminium 6061", mass["mask_holder"],
     "make (AQS-BOM-SC-001)", "layout choice around the 100 mm field (hold, W12)"],
    ["6", "Mask 160 x 160 x 3 (chrome on glass, 100 um pattern)", 1,
     "glass, chrome coating (AQS-LITH-001 section 2)", mass["mask"],
     "make (AQS-BOM-SC-001)",
     "pattern cut on the mill per AQS-LITH-001 section 2; the coating is not "
     "drawn"],
    ["7", "365 nm LED array head envelope (1 W optical, node design source)", 1,
     "purchased unit (envelope)", mass["led_head"], "buy",
     "purchased per plan rule 6, rating from the node design block (365 nm LED "
     "array, 1 W optical; 10 mW/cm2 x 20 s = 200 mJ/cm2)"],
    ["8", "Nozzle set per docs-authority/nozzles/LITHO_ALIGN.csv: drain and "
           "vent flush at the envelope faces", len(schedule), "aluminium 6061",
     mass["nozzles"], "make (AQS-BOM-SC-001)",
     "2-row envelope hardware schedule verbatim; duty section 4: no present "
     "process edge"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M8 socket screw", fasteners.grade_for("316L"), 8,
     "guard posts to the base plate, 2 per post (count from the model)",
     "no plan grade rule covers aluminium joints; A4-70 stainless selected "
     "against galvanic action with the 6061 frame; study length, confirmed at "
     "fabrication"],
    [None, "M8 bench anchor", fasteners.grade_for("316L"), 4,
     "base plate to the bench top, one per corner (count from the model)",
     "same aluminium-joint basis; the machine sits on the fab bench per the "
     "placement seed (on the bench)"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "base_mm": [L, W, T_BASE],
    "parts": {"stage": list(STAGE), "leadscrew": list(LEAD), "mask_holder": list(HOLDER),
              "mask": list(MASK), "led_head": list(LED)},
}
p["design"] = dict(DS)
p["design"].update({
    "service": "LITHO_ALIGN: contact aligner - 365 nm exposure of the 100 mm "
               "field at 200 mJ/cm2, 5 wafer starts/d (node design block; "
               "AQS-LITH-001 rev C; not a stepper)",
    "material": "6061 frame; aluminium stage; 4140 leadscrew; chrome-on-glass "
                "mask",
    "material_basis": "AQS-LITH-001 rev C section 3 (named on the node); duty "
                      "section 3 has nothing to match (no wet stream)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; stage x 420..580, leadscrew x "
             "140..940 at y 300, mask holder x 400..600, LED head x 430..550 "
             "at z 190..250; guard posts at the envelope corners",
    "supports": "base plate + guard frame + 4 bench anchors",
    "nozzle_spread": "the two schedule rows are envelope hardware: drain at x "
                     "430 flush at the bottom, vent at x 770 flush at the top",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
