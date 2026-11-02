"""HX8 manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AC. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 600 mm, y along 400 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 400 x 600 mm, node size_mm - the study registry box (params
  size_note records the M0 study envelope; the duty section 2 sizing gives area,
  U and LMTD, not the box). The build fills it; the study-box basis is a hold (W12).
- Machine per duty sections 2 and 3: a vertical PVC-U shell (OD 340, wall 6 study)
  on a 20 mm plinth inside a four-post hold-down frame (20 mm posts and top bars
  pin the envelope), with a PVDF straight-tube bundle between two PVDF tube sheets.
  The bundle is drawn as real tubes: 45 tubes of OD 10 x 360 between sheets at
  z 100 and 480, 0.509 m2 of tube area against the 0.51 m2 duty figure (A-HX;
  4.59 kW = 1500 W/m2K x 0.51 m2 x 6 K, duty section 2). Tube wall 1.5 mm is a
  study value; the PVDF bundle was adopted by the owner 2026-10-15 (AQS-STD-002
  section 4.5); titanium plates were withdrawn and graphite is not used (duty 3).
- Nozzles: all 7 rows of docs-authority/nozzles/HX8.csv drawn at tag, face, height
  and bore. Atmospheric tube or hose per duty section 4 (design_kPa 17.8 is the old
  head-plus-10 figure and is not a pressure rating): hose barbs flush at the
  envelope faces (the shell stands 30 off the face, within the barb reach), the
  schedule rating column carried verbatim as text. The z 600 outlet datums sit at
  the envelope top and are clamped below the barb radius (holds, W12); the 800
  vent datum is drawn flush on the top head.
- A-HX: the tube area from the model is reported against the duty 0.51 m2; the
  duty carries a heat rate (4.59 kW), so the figure is stated as duty-sized, not
  invented here.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 400 x 600, study registry box
REV = P["graph_revision"]

T_SHELL = 6.0                    # study wall - no authority states one (WORK_ORDER W12)
T_PLINTH = 20.0
SHELL_OD, CX, CY = 340.0, L / 2, W / 2
R_IN = SHELL_OD / 2 - T_SHELL                               # 164
Z_SH0, Z_SH1 = 40.0, H - T_PLINTH - 20.0                    # shell 40..560
Z_TS0, Z_TS1 = 100.0, 480.0                                 # tube sheets, 15 thick
TUBE_OD, TUBE_L, TUBE_WALL = 10.0, 360.0, 1.5               # study wall (hold, W12)
AREA_DUTY_M2 = 0.51                                         # duty section 2
PITCH = 28.0
CA = materials.ca_for("PVDF")
RHO = {"PVDF": materials.density("PVDF"), "PVC_U": materials.density("PVC_U")}

assert L == 600.0 and W == 400.0 and H == 600.0, "HX8 node envelope changed"


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
                    .extrude(20.0))                                        # top head 560..580
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(SHELL_OD / 2)
                    .extrude(T_PLINTH + 20.0))                             # base head laps the plinth
parts["shell"] = shell

# ---------------------------------------------------------------- PVDF tube bundle (A-HX)
sheets = (cq.Workplane("XY", origin=(CX, CY, Z_TS0)).circle(R_IN).extrude(15.0)
          .union(cq.Workplane("XY", origin=(CX, CY, Z_TS1)).circle(R_IN).extrude(15.0)))
parts["tube_sheets"] = sheets
# deterministic grid placement inside the sheet radius, y-major, then x
positions = []
ny = int((2 * R_IN - TUBE_OD) // PITCH) + 1
for iy in range(ny):
    y = (iy - (ny - 1) / 2) * PITCH
    if abs(y) > R_IN - TUBE_OD / 2 - 4:
        continue
    nx = int((2 * math.sqrt(max(R_IN ** 2 - y ** 2, 1.0)) - TUBE_OD) // PITCH) + 1
    for ix in range(nx):
        x = (ix - (nx - 1) / 2) * PITCH
        positions.append((x, y))
need = math.ceil(AREA_DUTY_M2 / (math.pi * TUBE_OD / 1000.0 * TUBE_L / 1000.0))
positions = sorted(positions, key=lambda p: (p[1], p[0]))[:need]
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


def od_of(r):
    return dn.pipe_od("DN15") if r["size"] == "solids" else dn.pipe_od(r["size"])


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = CX - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N4: boss on the base head
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 40.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N5: 800 datum predates the box
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 50.0, CY), (L, W, H))
        note = ("vent flush at the top head; schedule datum 800 mm predates the 600 "
                "box - named hold, WORK_ORDER W12")
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm sits at the envelope top; drawn "
                     f"clamped to {round(h_d, 1)} mm (barb radius rule) - WORK_ORDER W12")
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="HX8")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "hx8.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "hx8.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "HX8.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "hx8.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
area_model_m2 = len(positions) * math.pi * TUBE_OD / 1000.0 * TUBE_L / 1000.0
mass = {k: round(v.val().Volume() * (RHO["PVDF"] if k in ("tube_sheets", "bundle")
                                     else RHO["PVC_U"]) / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); the duty section 2 sizing "
    "gives area, U and LMTD, not the box (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "hx": {"type": "vertical straight-tube, PVDF bundle in PVC-U shell",
           "shell_od_mm": SHELL_OD, "wall_mm": T_SHELL,
           "tube_sheets_z_mm": [Z_TS0, Z_TS1], "tubes": len(positions),
           "tube": f"OD {TUBE_OD:g} x t {TUBE_WALL:g} (study wall) x {TUBE_L:g} long",
           "area_model_m2": round(area_model_m2, 4), "area_duty_m2": AREA_DUTY_M2,
           "duty_kW": 4.59, "duty_basis": "1500 W/m2K x 0.51 m2 x 6 K, duty "
           "section 2 (edges sum 4.572 kW); area not resized",
           "material_basis": "duty section 3: PVDF tubes and tube sheets (AQS-STD-002 "
           "section 4.5, owner adoption 2026-10-15), PVC-U shell on the Q4 water side; "
           "titanium plates withdrawn, graphite not used"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "stands 30 off the face, within the barb reach); the schedule rating column "
    "(Class 150) is carried verbatim as text, no flange drawn (duty section 4: no "
    "process pressure; design_kPa 17.8 is the old head-plus-10 figure)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"PVC-U shell OD {SHELL_OD:g}, wall {T_SHELL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, "
          f"with heads, on a {L:g} x {W:g} plinth in a four-post hold-down frame", 1,
     "PVC-U pipe/plate", round(mass["shell"] + mass["plinth"] + mass["frame"], 1), "make",
     "study registry envelope; wall a study value (WORK_ORDER W12); CA 0 mm "
     "(AQS-STD-001 polymer rule); duty section 3: PVC-U on the Q4 water side"],
    ["2", f"PVDF tube sheet pair, OD {2 * R_IN:g} x 15 at z {Z_TS0:g}/{Z_TS1:g}", 2,
     "PVDF", mass["tube_sheets"], "make",
     "duty section 3: PVDF tubes and tube sheets (AQS-STD-002 section 4.5); study "
     "thickness"],
    ["3", f"PVDF straight-tube bundle: {len(positions)} tubes OD {TUBE_OD:g} x "
          f"{TUBE_L:g}, {area_model_m2:.3f} m2 against the {AREA_DUTY_M2:g} m2 duty "
          "figure", len(positions), "PVDF", mass["bundle"], "make",
     "A-HX: area from the model reported against duty section 2 (4.59 kW at U 1500, "
     "LMTD 6 K); tube wall a study value (WORK_ORDER W12)"],
    ["4", "Nozzle set per docs-authority/nozzles/HX8.csv: 5 hose barbs "
          "(DN15/DN25), 1 drain boss, 1 vent at the top head",
     len(schedule), "PVC-U", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim (z 600 datums clamped below the barb "
     "radius, 800 vent datum - holds); atmospheric hose per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
n_bolt = 8
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("PVC_U"), 4,
     "plinth to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
    [None, "M12 PVDF bolt + nut", fasteners.grade_for("PVDF"), n_bolt,
     "top-head to shell service joint (study pattern at the bolt circle)",
     "polymer joint to the supplier rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note); the duty section 2 sizing gives "
             "area, U and LMTD, not the box (WORK_ORDER W12)",
    "shell": {"od_mm": SHELL_OD, "z_mm": [Z_SH0, Z_SH1]},
}
p["design"] = {
    "service": "HX-8: EW reject cooling against Q4 return preheat, atmospheric "
               "(duty sections 2 and 6)",
    "wall_mm": T_SHELL, "wall_basis": "study value", "ca_mm": CA,
    "area_model_m2": round(area_model_m2, 4), "area_duty_m2": AREA_DUTY_M2,
    "tubes": len(positions), "tube": "PVDF OD 10 x 360 (study wall 1.5)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at x 300, y 200, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row "
                     "per face/height group at the envelope face, 8 mm clear at the "
                     "bore; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N5 flush at the top head (800 datum predates the 600 box); N4 drain "
                  "boss on the base head",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"tubes": len(positions), "area_model_m2": round(area_model_m2, 4)}))
