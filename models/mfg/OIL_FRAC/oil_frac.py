"""OIL_FRAC manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-COL).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid. This is the M2 close-out of the style-builders column study:
the column is rebuilt through the current shared lib, the 14-row issued schedule
replaces the study layout, and the section 5 artifacts (check record, make-or-buy
BOM, fasteners, W1-W12 work order, drawing set, duty section 7 pointer) are
completed per the HX8 close pattern.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the envelope is computed by the
  write_graph scrubber pass each regen (STAGE_OWNED_SIZE), so this builder reads
  it from params and does not pin it. The build stays inside it; a four-post
  hold-down frame pins the registry box so the X-PAR-04 envelope registry reads
  the build (the column shell itself does not fill the box).
- Column per the unit's own duty sheet (pyrolysis oil separated to the four A-M-138
  cuts): vertical carbon-steel column shell OD 480, wall 6 mm (study - the duty
  states no diameter and no wall: drawn to the envelope, holds W12), with top and
  bottom heads, on a 20 mm plinth inside the hold-down frame. Duty section 2
  claims a 30 min sump of 0.0006 m3; the sump is reported from the model against
  that figure (A-COL hold, W12). The node internals row is none: no packing,
  distributor or demister is drawn; stages and HTU are not stated anywhere and
  stay a named hold (A-COL, W12); the cut split rides the node cut_basis pass
  fractions (A-M-138, SU2018_PYRO) - a flowsheet allocation, not tray design.
- Material carbon steel per duty section 3, hydrocarbon service, CA 1.5 mm
  (AQS-STD-001).
- Nozzles: all 14 rows of docs-authority/nozzles/OIL_FRAC.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: nozzle DN15, no flange class, atmospheric tube or hose). The
  N14 solids row (spent resist and solvent) is a non-piped transfer drawn DN15,
  bore not calculated (plan W4). Drain flush at the envelope bottom (50 datum);
  vent flush at the envelope top (800 datum is the box top). The schedule rating
  column (Class 150) is carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("OIL_FRAC")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800 (stage-owned)
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
COL_OD, T_WALL = 480.0, 6.0                                # to the envelope; study values (W12)
COL_ID = COL_OD - 2 * T_WALL
Z0, Z1 = 60.0, H - 40.0                                    # shell 60..760
CX, CY = L / 2, W / 2
SUMP_M3_DUTY = 0.0006                                      # duty section 2, 30 min sump
POST = 40.0                                                # hold-down frame section
MAT = "CS"                                                 # duty section 3
CA = materials.ca_for(MAT, "hydrocarbon")                  # 1.5, AQS-STD-001
RHO = materials.density(MAT)

assert COL_OD <= W - 80.0 and Z1 - Z0 <= H - T_PLINTH - 20.0, "column drawn to the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- column shell (duty sheet, drawn to the envelope)
shell = (cq.Workplane("XY", origin=(CX, CY, Z0)).circle(COL_OD / 2)
         .circle(COL_ID / 2).extrude(Z1 - Z0))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z0)).circle(COL_OD / 2)
                    .extrude(8.0))                          # bottom head (sump floor)
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z1 - 8.0)).circle(COL_OD / 2)
                    .extrude(8.0))                          # top head
shell = shell.union(cq.Workplane("XY", origin=(CX - 160.0, CY - 160.0, T_PLINTH))
                    .box(320.0, 320.0, Z0 - T_PLINTH, centered=False))      # skirt seat (fuse into the bottom head)
parts["column"] = shell

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
    dnl_draw = dnl if dnl.startswith("DN") else "DN15"
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N9: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (460.0, CY), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N10: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (540.0, CY), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
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
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

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
mass = {k: round(v.val().Volume() * RHO / 1e9, 2) for k, v in parts.items()}
h_sump_model = SUMP_M3_DUTY * 1e9 / (math.pi / 4 * COL_ID ** 2)   # liquid height of the duty sump in the modeled bore
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "column": {
        "type": "vertical carbon-steel fractionator column drawn to the node "
                "envelope: shell OD 480 (drawn to the envelope - the duty states "
                "no diameter), wall 6 (study), top and bottom heads, skirt seat, "
                "inside a four-post hold-down frame on a 20 mm plinth",
        "od_mm": COL_OD, "wall_mm": T_WALL, "z_mm": [Z0, Z1],
        "wall_basis": "study values; the duty states no diameter and no wall "
                      "(holds, WORK_ORDER W12)",
        "sump_duty_m3": SUMP_M3_DUTY,
        "sump_model_note": f"duty section 2 sump {SUMP_M3_DUTY:g} m3 (30 min): "
                           f"that volume stands {h_sump_model:.1f} mm deep in the "
                           "modeled bore - the sump zone is the bottom head; "
                           "reported, nothing resized (A-COL; plan rule 3)",
        "internals": "the node internals row is none: no packing, distributor or "
                     "demister is drawn; stages and HTU are not stated anywhere "
                     "and stay a named hold (A-COL, W12); the cut split rides the "
                     "node cut_basis pass fractions (A-M-138, SU2018_PYRO) - a "
                     "flowsheet allocation, not tray design",
        "material": MAT, "ca_mm": CA,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: nozzle DN15, no flange class, atmospheric "
                    "tube or hose); the N14 solids row (spent resist and solvent) "
                    "drawn DN15, bore not calculated (plan W4); the schedule "
                    "rating column (Class 150) is carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Column shell OD {COL_OD:g}, wall {T_WALL:g} mm (study), z {Z0:g}..{Z1:g}, "
          "with top and bottom heads on a skirt seat", 1,
     "carbon steel (duty section 3)", mass["column"], "make",
     "drawn to the node envelope - the duty states no diameter or wall (holds, "
     "WORK_ORDER W12); CA 1.5 mm (AQS-STD-001 hydrocarbon rule); sump report in "
     "check.column"],
    ["2", f"Four-post hold-down frame pinning the {L:g} x {W:g} x {H:g} envelope "
          f"(40 x 40 posts, top rails), + plinth {L:g} x {W:g} x {T_PLINTH:g}", 1,
     "carbon steel (ASTM A500)", mass["frame"] + mass["plinth"], "make",
     "HX8 hold-down idiom: the frame pins the registry box so the build fills the "
     "node envelope (X-PAR-04); AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["3", "Nozzle set per docs-authority/nozzles/OIL_FRAC.csv: 12 open-bore tube "
          "stubs (DN15/DN25), the N14 solids row drawn DN15 bore not calculated, "
          "drain and vent flush at the envelope faces", len(schedule),
     "carbon steel", mass["nozzles"], "make",
     "14-row issued schedule verbatim (replaces the style-builders study layout); "
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
    "column": {"od_mm": COL_OD, "wall_mm": T_WALL, "z_mm": [Z0, Z1],
               "axis_mm": [CX, CY]},
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "OIL_FRAC: pyrolysis oil separated to the four A-M-138 cuts, "
               "atmospheric (duty sections 1, 4 and 6)",
    "material": MAT, "ca_mm": CA,
    "wall_mm": T_WALL, "wall_basis": "study value (hold W12)",
    "internals": "none on the node; stages/HTU not stated - named hold (A-COL, "
                 "W12); cut split per the node cut_basis fractions (A-M-138)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; column axis at x 500, y 300, shell "
             "z 60..760; hold-down posts at the envelope corners",
    "supports": "plinth + skirt seat + hold-down frame + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one "
                     "row per face/height group from x 150, 8 mm clear at the "
                     "bore; drain at x 460, vent at x 540; per-tag positions in "
                     "check.nozzles_drawn",
    "close_out": "M2 close-out of the style-builders column study per the HX8 "
                 "close pattern: 14-row issued schedule, lib builders, section 5 "
                 "artifacts completed; nothing resized",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"sump_height_mm": round(h_sump_model, 1)}))
