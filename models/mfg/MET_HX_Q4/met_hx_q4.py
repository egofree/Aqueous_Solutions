"""MET_HX_Q4 manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AC. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (params
  size_note records the M0 study envelope; the duty section 2 states "No kilowatts
  on the node. Area is not calculated."). The build fills it; the study-box basis is
  a hold (W12).
- Machine: a vertical shell-and-tube exchanger - shell OD 540, wall 3 (study), on a
  plinth inside a four-post hold-down frame that pins the envelope - with a straight
  tube bundle between two tube sheets. The bundle is drawn hardware; its area is
  REPORTED AS DRAWN, not called calculated: the node carries no heat rate (A-HX).
- Material: drawn 316L shell, sheets and tubes per duty section 3's wet branch
  ("316L if the stream is wet or chloride. Carbon steel only if the stream is a dry
  hydrocarbon or a dry gas"). The conditional is not resolved by any authority - the
  carbon-steel alternative is a named hold (W12). CA 0 mm on the 316L (AQS-STD-001).
- Nozzles: all 3 rows of docs-authority/nozzles/MET_HX_Q4.csv drawn at tag, face,
  height and bore: N1 DN15 "heat < 80 C" out on +Y at z 600 (fits the 800 box),
  N2 drain boss on the base head to its 50 datum, N3 vent flush at the top head
  (the 800 datum IS the envelope top). Atmospheric tube or hose per duty section 4:
  hose barbs flush at the envelope faces (the shell stands 30 off the face), the
  schedule rating column carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402

GN = graph_node.graph_node("MET_HX_Q4")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800, study registry box
REV = P["graph_revision"]

T_SHELL = 3.0                    # study wall - no authority states one (WORK_ORDER W12)
T_PLINTH = 20.0
SHELL_OD, CX, CY = 540.0, L / 2, W / 2
R_IN = SHELL_OD / 2 - T_SHELL                               # 267
Z_SH0, Z_SH1 = 40.0, H - T_PLINTH - 20.0                    # shell 40..760
Z_TS0, Z_TS1 = 120.0, 660.0                                 # tube sheets, 15 thick
TUBE_OD, TUBE_L, TUBE_WALL = 12.0, 525.0, 1.5               # study wall (hold, W12)
PITCH = 34.0
CA = materials.ca_for("316L")                               # 0.0, AQS-STD-001
RHO = materials.density("316L")

# Envelope and design both come from the graph node; no hard-coded duplicate stays.


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth + frame + shell
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
post = 20.0
posts = None
for (px, py) in ((0, 0), (L - post, 0), (0, W - post), (L - post, W - post)):
    b = box(px, py, 0, post, post, H - T_PLINTH)
    posts = b if posts is None else posts.union(b)
bars = (box(0, 0, H - T_PLINTH, L, post, T_PLINTH)
        .union(box(0, W - post, H - T_PLINTH, L, post, T_PLINTH))
        .union(box(0, post, H - T_PLINTH, post, W - 2 * post, T_PLINTH))
        .union(box(L - post, post, H - T_PLINTH, post, W - 2 * post, T_PLINTH)))
parts["frame"] = posts.union(bars)
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(SHELL_OD / 2)
         .circle(R_IN).extrude(Z_SH1 - Z_SH0))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(SHELL_OD / 2)
                    .extrude(20.0))                                        # top head 760..780
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(SHELL_OD / 2)
                    .extrude(T_PLINTH + 20.0))                             # base head laps the plinth
parts["shell"] = shell

# ---------------------------------------------------------------- tube bundle (drawn, not rated)
sheets = (cq.Workplane("XY", origin=(CX, CY, Z_TS0)).circle(R_IN).extrude(15.0)
          .union(cq.Workplane("XY", origin=(CX, CY, Z_TS1)).circle(R_IN).extrude(15.0)))
parts["tube_sheets"] = sheets
positions = []
ny = int((2 * R_IN - TUBE_OD) // PITCH) + 1
for iy in range(ny):
    y = (iy - (ny - 1) / 2) * PITCH
    if abs(y) > R_IN - TUBE_OD / 2 - 6:
        continue
    nx = int((2 * math.sqrt(max(R_IN ** 2 - y ** 2, 1.0)) - TUBE_OD) // PITCH) + 1
    for ix in range(nx):
        x = (ix - (nx - 1) / 2) * PITCH
        positions.append((x, y))
positions = sorted(positions, key=lambda p: (p[1], p[0]))
bundle = None
for (dx, dy) in positions:
    t = (cq.Workplane("XY", origin=(CX + dx, CY + dy, Z_TS0 + 15.0))
         .circle(TUBE_OD / 2).circle(TUBE_OD / 2 - TUBE_WALL)
         .extrude(TUBE_L))
    bundle = t if bundle is None else bundle.union(t)
parts["bundle"] = bundle

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    span = sum(dn.pipe_od(r["size"]) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = CX - span / 2
    for r in rows:
        w = dn.pipe_od(r["size"]) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = dn.pipe_od(dnl)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N2: boss on the base head
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 60.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N3: 800 datum IS the envelope top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 80.0, CY), (L, W, H))
        note = "vent flush at the top head, the 800 envelope top"
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm clamped to {round(h_d, 1)} mm "
                     "(barb radius rule) - WORK_ORDER W12")
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="MET_HX_Q4")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "met_hx_q4.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "met_hx_q4.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "MET_HX_Q4.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "met_hx_q4.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
area_drawn_m2 = len(positions) * math.pi * TUBE_OD / 1000.0 * TUBE_L / 1000.0
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); the duty section 2 states no "
    "kilowatts and no calculated area (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "hx": {"type": "vertical straight-tube exchanger, shell-and-bundle",
           "shell_od_mm": SHELL_OD, "wall_mm": T_SHELL,
           "tube_sheets_z_mm": [Z_TS0, Z_TS1], "tubes": len(positions),
           "tube": f"OD {TUBE_OD:g} x t {TUBE_WALL:g} (study wall) x {TUBE_L:g} long",
           "area_drawn_m2": round(area_drawn_m2, 4),
           "area_basis": "drawn area, NOT a calculated duty area: the node carries no "
           "heat rate (duty section 2; A-HX)",
           "material_basis": "duty section 3 wet branch: 316L if the stream is wet or "
           "chloride; the conditional is not resolved - the carbon-steel alternative "
           "is a named hold (WORK_ORDER W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "stands 30 off the face, within the barb reach); the schedule rating column "
    "(Class 150) is carried verbatim as text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {SHELL_OD:g}, wall {T_SHELL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with "
          f"heads, on a {L:g} x {W:g} plinth in a four-post hold-down frame", 1,
     "316L plate/pipe", round(mass["shell"] + mass["plinth"] + mass["frame"], 1), "make",
     "duty section 3 wet branch (316L if the stream is wet or chloride - conditional "
     "hold, WORK_ORDER W12); wall a study value; CA 0 mm (AQS-STD-001)"],
    ["2", f"Tube sheet pair, OD {2 * R_IN:g} x 15 at z {Z_TS0:g}/{Z_TS1:g}", 2,
     "316L", mass["tube_sheets"], "make", "study thickness; same material basis"],
    ["3", f"Straight-tube bundle: {len(positions)} tubes OD {TUBE_OD:g} x {TUBE_L:g}, "
          f"{area_drawn_m2:.3f} m2 drawn", len(positions), "316L", mass["bundle"], "make",
     "A-HX: the area is reported as drawn, not calculated - the node has no heat rate "
     "(duty section 2); tube wall a study value (WORK_ORDER W12)"],
    ["4", "Nozzle set per docs-authority/nozzles/MET_HX_Q4.csv: 1 hose barb (DN15), "
          "1 drain boss, 1 vent at the top head",
     len(schedule), "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("316L"), 4,
     "plinth to slab, one per corner (count from the model)",
     "plan W5 grade rule on 316L (ISO 3506 A4-70); study length, confirmed at "
     "fabrication"],
    [None, "M12 A4-70 bolt + nut", fasteners.grade_for("316L"), 8,
     "top-head to shell service joint (study pattern at the bolt circle)",
     "plan W5 grade rule on 316L; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note); duty section 2 states no "
             "kilowatts and no calculated area (WORK_ORDER W12)",
    "shell": {"od_mm": SHELL_OD, "z_mm": [Z_SH0, Z_SH1]},
}
p["design"] = {
    "service": "Q4 loop heat exchange at < 80 C, atmospheric (duty sections 2, 4 and 6)",
    "wall_mm": T_SHELL, "wall_basis": "study value", "ca_mm": CA,
    "area_drawn_m2": round(area_drawn_m2, 4),
    "area_basis": "drawn, not calculated: no heat rate on the node",
    "tubes": len(positions), "tube": f"316L OD {TUBE_OD:g} x {TUBE_L:g} (study wall 1.5)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at x 500, y 300, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack centred on "
                     "the face mid-length; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N3 flush at the top head (the 800 envelope top); N2 drain boss on "
                  "the base head",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"tubes": len(positions), "area_drawn_m2": round(area_drawn_m2, 4)}))
