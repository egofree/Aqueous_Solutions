"""GREY_TREAT manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Placement frame: x along 649 mm, y along 520 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 649 x 520 x 748 mm, node size_mm - the study registry box (params
  size_note records it as read back from the cad/stl registry). The build fills
  it. The duty section 4 prose block still carries the seed line "Size 800 x
  800 x 1100 mm" - the node governs, the older figure is named (holds, W12).
- Body: vertical PVC-U treatment vessel - shell OD 460 (min(L, W) - 60, the
  flush-hardware idiom keeps the barbs within reach of the shell), wall 10 mm
  per the study fab page (no node thickness is booked - hold, W12), on a plinth
  with laps-to-plinth base head and a top head, inside the envelope.
- Internals: the node carries `internals: none` and no study page issues
  internals for this unit, so no internal solid is drawn and the tracker
  records none (hold, W12).
- Material: PVC-U (duty section 3, rules M1 and M2). CA does not apply to the
  polymer (AQS-STD-001).
- Nozzles: all 11 rows of docs-authority/nozzles/GREY_TREAT.csv drawn at tag,
  face, height and bore. Atmospheric tube or hose per duty section 4: hose
  barbs flush at the envelope faces, the schedule rating column (Class 150)
  carried verbatim as text, no flange (W4 110 % rule - no process pressure is
  stated). The issued schedule (11 rows) governs; the duty section 4 prose
  table (7 rows on the seed block) predates it and is named (hold, W12). N5
  drain boss on the base head to its 50 datum; N6 vent flush at the top head
  (its 800 datum predates the 748 box - hold, W12).
- A-VES: the duty section 2 claims no holdup ("No holdup claimed"); the model
  liquor volume at the study working level is reported and no residence time
  is derived from it.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("GREY_TREAT")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 649 x 520 x 748, study registry box
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0
T_WALL = 10.0                   # study fab-page polymer wall - no node booking (WORK_ORDER W12)
D, CX, CY = min(L, W) - 60.0, L / 2, W / 2   # shell OD 460; 30 mm stand-off to the +/-Y faces
R_IN = D / 2 - T_WALL                                       # 220
Z_SH0, Z_SH1 = 40.0, H - 40.0                               # shell 40..708
T_HEAD = 20.0
Z_LIQ = Z_SH1 - 40.0                                        # study working level below the top head
CA = materials.ca_for("PVC-U")                              # 0.0, polymer: AQS-STD-001
RHO = materials.density("PVC_U")                            # 1400, lib table

# Envelope and design both come from the graph node; no hard-coded duplicate stays.


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth + shell + heads
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
         .circle(R_IN).extrude(Z_SH1 - Z_SH0))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
                    .extrude(T_HEAD))                                        # top head 708..728
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(D / 2)
                    .extrude(T_PLINTH + T_HEAD))                             # base head laps plinth
parts["shell"] = shell

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

noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = dn.pipe_od(dnl)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N5: boss on the base head
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 60.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N6: 800 datum predates the 748 box
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 80.0, CY), (L, W, H))
        note = "vent flush at the top head; schedule datum 800 predates the 748 box - WORK_ORDER W12"
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm clamped to {round(h_d, 1)} mm "
                     "(barb radius rule) - WORK_ORDER W12")
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz_pieces.append(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
# the pieces stay a compound (no piece-to-piece fuse: each roots in the shell and is
# fused into the body piecewise at the export pass, the CATCH_TANK pattern)
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_liq = round(math.pi * R_IN ** 2 * (Z_LIQ - (T_PLINTH + T_HEAD)) / 1e9, 4)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    if k == "nozzles":
        for piece in noz_pieces:
            solid = piece if solid is None else solid.union(piece)
        continue
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {
    "plinth": parts["plinth"].val().Volume() * RHO / 1e9,
    "shell": parts["shell"].val().Volume() * RHO / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); the duty sheet section 4 "
    "prose block still carries the seed line Size 800 x 800 x 1100 mm (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_liq,
    "holdup_basis": "reported at the study working level z " + f"{Z_LIQ:g}" + ", no "
    "residence derived: the duty section 2 claims no holdup (A-VES)",
    "tank": {"wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall (10 mm); "
             "no thickness booked on the node (WORK_ORDER W12)",
             "internals": {"source": "none: the node internals row is none and no "
                           "study page issues internals for this unit",
                           "basis": "no internal solid drawn (WORK_ORDER W12)"}},
    "material": {"class": "PVC-U", "ca_mm": CA,
                 "basis": "duty section 3, rules M1 and M2; corrosion allowance does "
                 "not apply to the polymer"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "stands 30 off the +/-Y faces, within the barb reach); the schedule rating "
    "column (Class 150) is carried verbatim as text, no flange drawn; the issued "
    "schedule (11 rows) governs, the duty section 4 prose table (7 rows on the "
    "seed block) predates it (WORK_ORDER W12)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {D:g}, wall {T_WALL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with heads, "
          f"on a {L:g} x {W:g} plinth", 1, "PVC-U plate/pipe",
     round(mass["shell"] + mass["plinth"], 1), "make",
     "study registry envelope (node size_mm); wall the study fab-page polymer value "
     "(hold, WORK_ORDER W12); CA 0 mm (AQS-STD-001 polymer rule); duty section 3 "
     "PVC-U per rules M1 and M2"],
    ["2", "Nozzle set per docs-authority/nozzles/GREY_TREAT.csv: 1 DN50 and 5 DN15 "
          "hose barbs in, DN25/DN50/DN15 barbs out, 1 drain boss, 1 vent at the top "
          "head", len(schedule), "PVC-U", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "barb profile a study proportion (lib/nozzles.py); the duty section 4 prose "
     "table (7 rows) predates the issued schedule (hold, WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("PVC-U", joint="polymer"), 4,
     "plinth to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note); the duty section 4 prose seed "
             "line 800 x 800 x 1100 is an older figure (WORK_ORDER W12)",
    "shell": {"od_mm": D, "z_mm": [Z_SH0, Z_SH1]},
}
p["design"] = {
    "service": "greywater treatment vessel, atmospheric (duty sections 2, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall", "ca_mm": CA,
    "internals": "none drawn: no authority issues internals for this unit (WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at x 324.5, y 260, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack centred on "
                     "the face mid-length; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N6 vent flush at the top head (the 800 datum predates the box); "
                  "N5 drain boss on the base head, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
