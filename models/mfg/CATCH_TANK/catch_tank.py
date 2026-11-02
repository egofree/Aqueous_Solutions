"""CATCH_TANK manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 649 mm, y along 520 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 649 x 520 x 748 mm, node size_mm - the study registry box (params size_note
  records it as read back from the cad/stl registry). The duty sheet section 4 still
  carries the unit-task-04 reservoir line "Size 12000 x 8000 x 4000 mm" and the
  AQS-MFG-001 study page a generic 1000 x 600 x 800: the node governs, both older
  figures are named holds (WORK_ORDER W12). The build fills the node box.
- Body: vertical PVC-U storage tank - shell OD 460 (min(L, W) - 60, the flush-hardware
  idiom keeps the barbs within reach of the shell), wall 10 mm per the study fab page
  ("Shell 6 mm on metal, 10 mm on polymer"; no node thickness is booked), on a plinth
  with laps-to-plinth base head and a top head, inside the envelope.
- Internals: dip pipe and stilling well - the two internals the AQS-MFG-001 study page
  (`docs-authority/fab/CATCH_TANK.md`) issues for this unit. Drawn as concentric
  tubes: stilling well OD 110 (wall 5) from the floor to above the working level, dip
  pipe OD 60 (wall 4) inside it from the top head down to z 100 (feed enters down the
  dip pipe, the well damps the inlet jet for the level instruments). Dimensions are
  study values - the fab page names the internals, no authority sizes them (holds).
  The node internals row is none, so the tracker records no internal solid.
- Material: PVC-U drawn per duty section 3 ("PVC-U or HDPE, per AQS-STD-002 rule M1";
  the M1 audit list books this unit in the PVC-U or HDPE water-tank family). The
  unresolved HDPE alternative is a named hold (W12). CA does not apply to the polymer.
- Nozzles: all 6 rows of docs-authority/nozzles/CATCH_TANK.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs flush at
  the envelope faces, the schedule rating column (Class 150) carried verbatim as
  text, no flange (W4 110 % rule - no process pressure stated). N5 drain boss on the
  base head, tip at its 50 datum; N6 vent flush at the top head (its 800 datum
  predates the 748 box - hold, W12).
- A-VES: the liquor volume at the working level net of the well and dip pipe is
  computed from the model and reported; the duty claims a two-minute holdup figure
  (0.2778 m3 at 200 t/d circulation) but no designed volume, so no residence time is
  derived from the model volume.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles          # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 649 x 520 x 748, study registry box
REV = P["graph_revision"]

T_PLINTH = 20.0
T_WALL = 10.0                   # study fab-page polymer wall - no node booking (WORK_ORDER W12)
D, CX, CY = min(L, W) - 60.0, L / 2, W / 2   # shell OD 460; 30 mm stand-off to the +/-Y faces
R_IN = D / 2 - T_WALL                                       # 220
Z_SH0, Z_SH1 = 40.0, H - 40.0                               # shell 40..708
T_HEAD = 20.0
Z_LIQ = Z_SH1 - 40.0                                        # working level below the top head
WELL_OD, WELL_T = 110.0, 5.0                                # stilling well (study)
DIP_OD, DIP_T = 60.0, 4.0                                   # dip pipe inside the well (study)
WELL_Z0, WELL_Z1 = 35.0, Z_SH1 + 15.0                       # laps the floor and the top head
DIP_Z0, DIP_Z1 = 100.0, Z_SH1 + 15.0                        # hung from the top head
CA = materials.ca_for("PVC-U")                              # 0.0, polymer: AQS-STD-001
RHO = materials.density("PVC_U")                            # 1400, lib table

assert L == 649.0 and W == 520.0 and H == 748.0, "CATCH_TANK node envelope changed"


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

# ---------------------------------------------------------------- dip pipe + stilling well
well = (cq.Workplane("XY", origin=(CX, CY, WELL_Z0)).circle(WELL_OD / 2)
        .circle(WELL_OD / 2 - WELL_T).extrude(WELL_Z1 - WELL_Z0))
well = well.union(cq.Workplane("XY", origin=(CX, CY, WELL_Z1 - 5)).circle(WELL_OD / 2)
                  .extrude(5))                                               # well cap laps top head
parts["stilling_well"] = well
dip = (cq.Workplane("XY", origin=(CX, CY, DIP_Z0)).circle(DIP_OD / 2)
       .circle(DIP_OD / 2 - DIP_T).extrude(DIP_Z1 - DIP_Z0))
parts["dip_pipe"] = dip

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
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_shell_liq = math.pi * R_IN ** 2 * (Z_LIQ - (T_PLINTH + T_HEAD)) / 1e9
v_well = math.pi * (WELL_OD / 2 - WELL_T) ** 2 * (Z_LIQ - WELL_Z0) / 1e9
v_dip = math.pi * (DIP_OD / 2 - DIP_T) ** 2 * max(Z_LIQ - DIP_Z0, 0.0) / 1e9
v_liq = round(v_shell_liq - v_well - v_dip, 4)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="CATCH_TANK")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "catch_tank.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "catch_tank.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CATCH_TANK.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "catch_tank.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * RHO / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note); the duty sheet section 4 "
    "still carries the unit-task-04 reservoir line 12000 x 8000 x 4000 (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_liq,
    "holdup_basis": "reported, no residence derived: the duty section 2 two-minute "
    "figure (0.2778 m3 at 200 t/d circulation) is not a designed volume (A-VES)",
    "tank": {"wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall (10 mm); "
             "no thickness booked on the node (WORK_ORDER W12)",
             "internals": {"source": "docs-authority/fab/CATCH_TANK.md (AQS-MFG-001 "
                           "study page): dip pipe, stilling well",
                           "stilling_well": {"od_mm": WELL_OD, "wall_mm": WELL_T,
                                             "z_mm": [WELL_Z0, WELL_Z1]},
                           "dip_pipe": {"od_mm": DIP_OD, "wall_mm": DIP_T,
                                        "z_mm": [DIP_Z0, DIP_Z1]},
                           "basis": "internals named by the issued study page; "
                           "dimensions study values (WORK_ORDER W12); node internals "
                           "row none, so the tracker records no internal solid"}},
    "material": {"class": "PVC-U", "ca_mm": CA,
                 "basis": "duty section 3: PVC-U or HDPE per AQS-STD-002 rule M1; "
                 "PVC-U drawn, the HDPE alternative is a named hold (WORK_ORDER W12); "
                 "corrosion allowance does not apply to the polymer"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "stands 30 off the +/-Y faces, within the barb reach); the schedule rating column "
    "(Class 150) is carried verbatim as text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {D:g}, wall {T_WALL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with heads, "
          f"on a {L:g} x {W:g} plinth", 1, "PVC-U plate/pipe",
     round(mass["shell"] + mass["plinth"], 1), "make",
     "study registry envelope (node size_mm); wall the study fab-page polymer value; "
     "CA 0 mm (AQS-STD-001 polymer rule); duty section 3 PVC-U-or-HDPE conditional "
     "hold (WORK_ORDER W12)"],
    ["2", f"Stilling well, OD {WELL_OD:g} x wall {WELL_T:g}, z {WELL_Z0:g}..{WELL_Z1:g}",
     1, "PVC-U pipe", mass["stilling_well"], "make",
     "internals issued by the AQS-MFG-001 study page (fab/CATCH_TANK.md); dimensions "
     "study values (WORK_ORDER W12); node internals row none"],
    ["3", f"Dip pipe inside the well, OD {DIP_OD:g} x wall {DIP_T:g}, "
          f"z {DIP_Z0:g}..{DIP_Z1:g}", 1, "PVC-U pipe", mass["dip_pipe"], "make",
     "same study-page basis; feed enters down the dip pipe, the well damps the jet "
     "for the level instruments (duty section 5)"],
    ["4", "Nozzle set per docs-authority/nozzles/CATCH_TANK.csv: 4 hose barbs "
          "(DN15/DN50), 1 drain boss, 1 vent at the top head", len(schedule), "PVC-U",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "barb profile a study proportion (lib/nozzles.py)"],
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
    "basis": "study registry box (params size_note); the duty sheet section 4 "
             "reservoir line and the fab study page envelope are older figures "
             "(WORK_ORDER W12)",
    "shell": {"od_mm": D, "z_mm": [Z_SH0, Z_SH1]},
}
p["design"] = {
    "service": "pumped-hydro catch tank, atmospheric (duty sections 2, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall", "ca_mm": CA,
    "internals": "dip pipe + stilling well (fab study page; dims study)",
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
