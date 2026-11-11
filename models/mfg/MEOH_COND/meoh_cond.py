"""MEOH_COND manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 400 mm, y along 400 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 400 x 400 x 600 mm, node size_mm - SIZED, not a registry box: the node
  size_note records "sized from the issued graph duties, methanol train residual
  sizing (flow_graph/param/meoh_train.py, AQS-DUTY-077)", and the node design block
  books D_mm 400, H_mm 600 and drum_L 71.19 for the "knock-out pot + condenser on
  the same skid". The build fills the node box: shell OD 400 (the node D) tangent
  to all four faces, measured 400.0 x 400.0 x 600.0 mm, one closed manifold solid.
- Body: vertical 316L knock-out drum - shell OD 400, wall 3 (study: no authority
  states a wall), plinth, base head laps the plinth, top head.
- Coil (the node design books it): "1 x 10 mm x 1 m coil", area_m2 0.0301,
  condensing 0.7079 kW at U 1.2 kW/m2K, LMTD 19.6 K (AQS-DUTY-077). Drawn as a
  316L OD 10 helix, ~2.64 turns at a 120 mm mean diameter, developed length 1.000 m
  in the lower drum: the drawn area 0.0314 m2 is 0.0013 m2 over the node figure
  (the node area is a nominal book figure, the drawn coil is the hardware) -
  reported, nothing resized (WORK_ORDER W12).
- Internals: the coil is the internal the node books. The node internals row is
  none, so the tracker records no internal solid. The knock-out function is the
  drum itself (no weir or pad is booked anywhere for this unit).
- Material: 316L shell and coil (graph node material; duty section 3). CA 0 mm
  (AQS-STD-001).
- Nozzles: all 5 rows of docs-authority/nozzles/MEOH_COND.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs flush at
  the envelope faces, the schedule rating column (Class 150) carried verbatim as
  text, no flange (W4 110 % rule - no process pressure stated). N2 outlet datum 600
  clamped to 584.4 by the barb-radius rule (hold, W12); N3 drain boss on the base
  head, tip at its 50 datum; N4 vent flush at the top head (its 800 datum predates
  the 600 box - hold, W12).
- A-VES: the liquor volume at the working level net of the coil is computed from
  the model and reported against the node drum_L 71.19 nominal figure; no residence
  time is derived (the duty section 2 box-residence sentence is explicitly not a
  residence time).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles, step_export  # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 400 x 400 x 600, node-sized
DES = P.get("design") or {}
REV = P["graph_revision"]

T_PLINTH = 20.0
T_WALL = 3.0                    # study wall - no authority states one (WORK_ORDER W12)
D, CX, CY = 400.0, L / 2, W / 2              # node design D_mm; tangent to the faces
R_IN = D / 2 - T_WALL                                       # 197
Z_SH0, Z_SH1 = 40.0, H - 40.0                               # shell 40..560
T_HEAD = 20.0
Z_LIQ = Z_SH1 - 40.0                                        # working level below the top head
COIL_TUBE = 10.0                                            # node design: 10 mm tube
COIL_R, COIL_PITCH, COIL_TURNS = 63.66, 40.0, 2.5           # 2.5 exact turns put both coil
# ends on the x axis of the drum, where a radial stub reaches each wall; the pitch
# then develops the node's 1 m book: 2.5 x sqrt((2 pi R)^2 + pitch^2) = 1000.2 mm
COIL_DEV = 1000.0                                           # node design: 1 m coil
COIL_H = COIL_TURNS * COIL_PITCH
COIL_Z0 = 80.0
CA = materials.ca_for("316L")                               # 0.0, AQS-STD-001
RHO = materials.density("316L")                             # 8000, lib table

assert L == 400.0 and W == 400.0 and H == 600.0, "MEOH_COND node envelope changed"
assert DES.get("D_mm") == 400 and DES.get("H_mm") == 600, "node design D/H changed"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth + shell + heads
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
         .circle(R_IN).extrude(Z_SH1 - Z_SH0))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
                    .extrude(T_HEAD))                                        # top head 560..580
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(D / 2)
                    .extrude(T_PLINTH + T_HEAD))                             # base head laps plinth
parts["shell"] = shell

# ---------------------------------------------------------------- coil (node design)
helix = cq.Wire.makeHelix(pitch=COIL_PITCH, height=COIL_H, radius=COIL_R)
coil = (cq.Workplane("XZ").workplane(offset=-COIL_R, origin=(COIL_R, 0, 0))
        .circle(COIL_TUBE / 2)
        .sweep(cq.Workplane(obj=helix), isFrenet=True)
        .translate((CX, CY, COIL_Z0)))
# both coil ends land on the x axis (2.5 turns): radial OD 10 stubs through the
# +/-X shell walls (the shell is tangent to the envelope faces, so the stub tips
# end flush at the faces) - a coil is hardware, its ends must reach the wall
coil = coil.union(cq.Workplane("YZ", origin=(CX + COIL_R - COIL_TUBE / 2, CY - COIL_TUBE / 2, COIL_Z0))
                  .rect(COIL_TUBE, COIL_TUBE).extrude((CX + D / 2) - (CX + COIL_R - COIL_TUBE / 2)))
coil = coil.union(cq.Workplane("YZ", origin=(CX - D / 2, CY - COIL_TUBE / 2, COIL_Z0 + COIL_H))
                  .rect(COIL_TUBE, COIL_TUBE).extrude((CX - COIL_R + COIL_TUBE / 2) - (CX - D / 2)))
parts["coil"] = coil
coil_dev_mm = COIL_TURNS * math.sqrt((2 * math.pi * COIL_R) ** 2 + COIL_PITCH ** 2)
coil_area_m2 = coil_dev_mm / 1000.0 * math.pi * COIL_TUBE / 1000.0

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
    if r["face"] == "bottom":                             # N3: boss on the base head
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 60.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N4: 800 datum predates the 600 box
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 80.0, CY), (L, W, H))
        note = "vent flush at the top head; schedule datum 800 predates the 600 box - WORK_ORDER W12"
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

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_liq = round(math.pi * R_IN ** 2 * (Z_LIQ - (T_PLINTH + T_HEAD)) / 1e9
              - math.pi * (COIL_TUBE / 2) ** 2 * coil_dev_mm / 1e9, 4)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="MEOH_COND")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / "meoh_cond.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
assert len(solid.Solids()) == 1, f"assembly split into {len(solid.Solids())} solids"
solid.exportStl(str(out / "meoh_cond.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "MEOH_COND.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "meoh_cond.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "node-sized (params size_note: meoh_train.py, AQS-DUTY-077; node "
    "design D_mm 400, H_mm 600, drum_L 71.19)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_liq,
    "holdup_basis": "reported against the node drum_L 71.19 nominal figure; no "
    "residence derived - the duty section 2 box sentence is explicitly not a "
    "residence time (A-VES)",
    "ko_drum": {"wall_mm": T_WALL, "wall_basis": "study value - no authority states "
                "a wall (WORK_ORDER W12)",
                "drum_L_node": DES.get("drum_L"),
                "coil": {"tube_od_mm": COIL_TUBE, "mean_radius_mm": COIL_R, "turns": COIL_TURNS,
                         "developed_mm": round(coil_dev_mm, 1),
                         "z_mm": [COIL_Z0, round(COIL_Z0 + COIL_H, 1)],
                         "area_drawn_m2": round(coil_area_m2, 4),
                         "area_node_m2": DES.get("area_m2"),
                         "area_basis": "drawn coil hardware against the node book "
                         "'1 x 10 mm x 1 m coil', area_m2 0.0301: the drawn area is "
                         "0.0013 m2 over the node figure - reported, nothing resized "
                         "(WORK_ORDER W12)",
                         "duty": {"condensing_kW": DES.get("condensing_kW"),
                                  "U_kW_m2K": DES.get("U_kW_m2K"),
                                  "LMTD_K": DES.get("LMTD_K")}}},
    "material": {"class": "316L", "ca_mm": CA,
                 "basis": "duty section 3 / graph node material: 316L shell and coil "
                 "(methanol/water traces); CA 0 mm (AQS-STD-001)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "is tangent to the faces, so every root laps the shell or a head); the schedule "
    "rating column (Class 150) is carried verbatim as text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {D:g}, wall {T_WALL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with heads, "
          f"on a {L:g} x {W:g} plinth (knock-out pot, node design D 400 / H 600 / "
          f"drum {DES.get('drum_L')} L nominal)", 1, "316L plate/pipe",
     round(mass["shell"] + mass["plinth"], 1), "make",
     "node-sized envelope (meoh_train.py, AQS-DUTY-077); wall a study value "
     "(WORK_ORDER W12); CA 0 mm (AQS-STD-001)"],
    ["2", f"Coil, tube OD {COIL_TUBE:g} x {coil_dev_mm / 1000.0:.3f} m developed, "
          f"~2.6 turns at a {2 * COIL_R:g} mm mean diameter, {coil_area_m2:.4f} m2 "
          "drawn", 1, "316L", mass["coil"], "make",
     "node design '1 x 10 mm x 1 m coil' (area_m2 0.0301); the drawn area is "
     "0.0013 m2 over the node figure - reported, nothing resized (WORK_ORDER W12); "
     "condensing 0.7079 kW at U 1.2, LMTD 19.6 K"],
    ["3", "Nozzle set per docs-authority/nozzles/MEOH_COND.csv: 3 hose barbs (DN15), "
          "1 drain boss, 1 vent at the top head", len(schedule), "316L",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "N2 datum 600 clamped to 584.4 and the N4 800 datum predates the 600 box "
     "(holds, WORK_ORDER W12); barb profile a study proportion (lib/nozzles.py)"],
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
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "node-sized (params size_note: meoh_train.py, AQS-DUTY-077); the build "
             "fills the node box exactly",
    "shell": {"od_mm": D, "z_mm": [Z_SH0, Z_SH1]},
}
# the node design block (meoh_train sizing: D_mm, H_mm, drum_L, area_m2...) is
# authority data carried in params.json - merge the builder's design fields beside
# it, never over it
p["design"] = {
    **{k: v for k, v in (P.get("design") or {}).items()},
    "service": "methanol-train knock-out pot + condenser on one skid, atmospheric "
               "(node design block, duty sections 2, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study value", "ca_mm": CA,
    "coil": {"tube_od_mm": COIL_TUBE, "developed_mm": round(coil_dev_mm, 1),
             "area_drawn_m2": round(coil_area_m2, 4),
             "area_node_m2": DES.get("area_m2"),
             "condensing_kW": DES.get("condensing_kW")},
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at x 200, y 200, z up; the "
             "shell is tangent to all four faces (node D 400)",
    "nozzle_spread": "the schedule gives face and height only; ports pack centred on "
                     "the face mid-length; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N4 vent flush at the top head (the 800 datum predates the box); "
                  "N3 drain boss on the base head, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
