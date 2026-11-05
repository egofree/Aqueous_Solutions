"""WS_PHOS manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-MACH).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 350 mm, node size_mm (set by docs-authority/_storage_sizing.py,
  AQS-DUTY-064). The duty section 4 prose block still carries the seed line "Size
  800 x 800 x 1100 mm" - the node governs and the older figure is named (holds, W12).
  The build fills the node box.
- Machine: a reagent day-station - bund tray over the envelope and the day tank
  at the back, on the acid_phos bund seat of the placement seed. Duty section 2:
  the seven-day charge V = (0.6200/1000) x (168/24) = 0.0043 m3 (the
  box-over-flow line is explicitly not a residence time) - the model working
  level is set by that charge basis and reported (holds, W12).
- Material: PVC-U wetted, per AQS-STD-002 rules M1 and M2, no metal wetted part
  (duty section 3). CA does not apply to the polymer (AQS-STD-001).
- Nozzles: all 5 rows of docs-authority/nozzles/WS_PHOS.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections on tray risers, flush
  at the envelope faces (duty section 4: atmospheric joints are hose; hose makeup
  by the connecting line at the face). The schedule rating column (Class 150) is
  carried verbatim as text, no flange (W4 110 % rule - no process pressure stated).
  Side datums sit in the 350 mm box: the 160 mm inlet draws as issued; the 600 mm
  outlet datum predates the box and clamps to the box bound (hold, W12). The drain
  passes through the tray floor (50 datum); the vent riser stands on the tank head
  to the envelope top (its 800 datum predates the box - hold, W12).
- A-MACH: guard and anchor drawn - the service-zone guard rail and the slab
  anchors. No purchased item is named on the node or the duty sheet for this
  station, so none is drawn (the criterion has nothing to match; WORK_ORDER W12).
- A-VES does not apply (the reagent class carries A-core + A-MACH); the tank
  working volume is reported from the model for the record.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("WS_PHOS")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 350, storage-sizing box
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_TRAY = 20.0                   # bund tray floor
CURB_H, CURB_T = 60.0, 10.0     # tray curb (the drip tray; the duty own-bund figure is room-side)
TX, TY = 300.0, 380.0           # tank axis, back of the tray
D = 180.0                       # tank OD (layout choice within the box - WORK_ORDER W12)
R_IN = D / 2 - 10.0             # wall 10, study fab-page polymer wall (hold, W12)
Z_SH0 = T_TRAY + 20.0           # tank seat z 40
Z_SH1 = 290.0                   # shell top
T_HEAD = 20.0
Z_TOP = Z_SH1 + T_HEAD          # head top 310
VENT_Z0 = Z_TOP - 20.0          # vent riser seat inside the head
CHARGE_M3 = 0.0043              # duty section 2: the seven-day charge
GUARD = (130.0, 100.0, 150.0)   # service-zone guard rail, L x W x H (A-MACH: guard drawn)
GUARD_X0, GUARD_Y0 = 465.0, 15.0

CA_TANK = materials.ca_for("PVC-U")                         # 0.0, polymer: AQS-STD-001
RHO_TANK = materials.density("PVC_U")                       # 1400, lib table
RHO_PP = materials.density("PP")                            # 910, guard rail

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert TY + D / 2 <= W and TX + D / 2 <= L, "tank must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- bund tray
tray = box(0, 0, 0, L, W, T_TRAY)
for x, y, dx, dy in ((0, 0, L, CURB_T), (0, W - CURB_T, L, CURB_T),
                     (0, CURB_T, CURB_T, W - 2 * CURB_T),
                     (L - CURB_T, CURB_T, CURB_T, W - 2 * CURB_T)):
    tray = tray.union(box(x, y, T_TRAY - 2.0, dx, dy, CURB_H - 2.0))
parts["tray"] = tray

# ---------------------------------------------------------------- day tank
tank = (cq.Workplane("XY", origin=(TX, TY, Z_SH0)).circle(D / 2)
        .circle(R_IN).extrude(Z_SH1 - Z_SH0))
tank = tank.union(cq.Workplane("XY", origin=(TX, TY, Z_SH1)).circle(D / 2)
                  .extrude(T_HEAD))
tank = tank.union(cq.Workplane("XY", origin=(TX, TY, T_TRAY - 2.0)).circle(D / 2)
                  .extrude(Z_SH0 - T_TRAY + T_HEAD + 2.0))
parts["tank"] = tank

# ---------------------------------------------------------------- guard rail (A-MACH: guard drawn)
posts = None
for gx in (GUARD_X0 + 6.0, GUARD_X0 + GUARD[0] - 6.0):
    for gy in (GUARD_Y0 + 6.0, GUARD_Y0 + GUARD[1] - 6.0):
        p_ = cq.Workplane("XY", origin=(gx, gy, T_TRAY - 2.0)).circle(6.0).extrude(GUARD[2])
        posts = p_ if posts is None else posts.union(p_)
rails = None
for gy in (GUARD_Y0 + 6.0, GUARD_Y0 + GUARD[1] - 6.0):
    r_ = (cq.Workplane("YZ", origin=(GUARD_X0, gy, T_TRAY - 2.0 + GUARD[2] - 6.0))
          .circle(6.0).extrude(GUARD[0]))
    rails = r_ if rails is None else rails.union(r_)
for gx in (GUARD_X0 + 6.0, GUARD_X0 + GUARD[0] - 6.0):
    r_ = box(gx - 6.0, GUARD_Y0, T_TRAY - 2.0 + GUARD[2] - 6.0, 12.0, GUARD[1], 12.0)
    rails = rails.union(r_) if rails is not None else r_
parts["guard_rail"] = posts.union(rails)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
CLAMP_MARGIN = 0.7
Y_RISER = 60.0
PACK_X = {"-Y": 420.0, "+Y": 300.0}


def z_for(row):
    """Drawn centreline height for a side nozzle, clamped deep enough that the
    branch and its riser top both stay inside the box."""
    h = row.get("height_mm")
    od_s = dn.pipe_od(row["size"])
    hi = H - od_s - 8.0
    if h in (None, ""):
        return round(hi, 1), ("no datum on the schedule row; drawn at the +Y band "
                              "bound (layout choice, WORK_ORDER W12)")
    h = float(h)
    z = min(max(h, od_s / 2 + CLAMP_MARGIN), hi)
    if h > hi:
        return round(z, 1), (f"schedule datum {h:g} mm predates the box; clamped to "
                             f"{round(z, 1)} mm so the branch and riser stay inside "
                             "(hold, WORK_ORDER W12)")
    return round(z, 1), None


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, r.get("height_mm") or "no_datum"), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    x = PACK_X[face]
    for r in rows:
        w_od = dn.pipe_od(r["size"])
        layout_x[r["tag"]] = round(x + w_od / 2, 1)
        x += w_od + 8.0

noz_pieces, drawn, clamp_notes = [], {}, []
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    od = dn.pipe_od(dnl)
    if face0 == "bottom":                      # drain: open bore through the tray floor
        s = tube(dnl, 40.0 - T_TRAY + 2.0).translate((560.0, 300.0, T_TRAY - 2.0))
        note = "drain, open bore through the tray floor, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, 560.0
    elif face0 == "top":                       # vent: riser on the tank head to the box top
        s = tube(dnl, H - VENT_Z0).translate((TX, TY, VENT_Z0))
        note = ("vent riser on the tank head, flush at the envelope top; schedule "
                "datum 800 predates the box (hold, WORK_ORDER W12)")
        z_d, x_d = H, TX
    else:
        z_d, note = z_for(r)
        if note:
            clamp_notes.append(note)
        x_d = layout_x[tag]
        y_r = Y_RISER if face == "-Y" else W - Y_RISER
        riser = tube(dnl, z_d - T_TRAY + 2.0 + od / 2 + 4.0).translate((x_d, y_r, T_TRAY - 2.0))
        branch = nozzles.place_on_face(tube(dnl, Y_RISER - od / 2 + 5.0), face, z_d,
                                       (x_d, W / 2), (L, W, H))
        s = riser.union(branch)
        note = (note or "schedule datum drawn") + (
            "; atmospheric open-bore tube on a tray riser, flush at the envelope face "
            "(duty section 4)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube", "dn": dnl, "face": face,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
# the pieces stay a compound; each roots in the tray or tank and is fused piecewise
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- tank working volume (record)
area = math.pi * (R_IN / 1000.0) ** 2
z_charge = round(Z_SH0 + CHARGE_M3 / area * 1000.0, 1)   # 1 L/m2 = 1 mm
v_charge = round(area * (z_charge - Z_SH0) / 1000.0, 4)
assert abs(v_charge - CHARGE_M3) < 1e-6 and z_charge < Z_SH1, (z_charge, v_charge)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

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
    "tray": parts["tray"].val().Volume() * RHO_TANK / 1e9,
    "tank": parts["tank"].val().Volume() * RHO_TANK / 1e9,
    "guard_rail": parts["guard_rail"].val().Volume() * RHO_PP / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO_TANK / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "storage-sizing box (node size_mm, AQS-DUTY-064); the duty section 4 "
    "prose seed line 800 x 800 x 1100 predates it (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "tank": {"od_mm": D, "xy_mm": [TX, TY], "z_mm": [Z_SH0, Z_TOP],
             "wall_mm": 10.0, "wall_basis": "study fab-page polymer wall (10 mm); no "
             "thickness booked on the node (WORK_ORDER W12)",
             "working_volume_m3": v_charge,
             "working_volume_basis": "the duty section 2 charge basis: the "
             "seven-day charge 0.0043 m3 sets the working level z "
             + f"{z_charge:g}" + " (reported); the box-over-flow line in duty "
             "section 2 is explicitly not a residence time (A-VES n/a; WORK_ORDER "
             "W12); duty section 8: the phosphoric concentration is not on the "
             "node, so 316L is not confirmed - PVC-U drawn per duty section 3 "
             "(hold, WORK_ORDER W12)",
             "internals": {"source": "none: the node internals row is none and no "
                           "study page issues internals for this station",
                           "basis": "no internal solid drawn (WORK_ORDER W12)"}},
    "material": {"class": "PVC-U", "ca_mm": CA_TANK,
                 "basis": "duty section 3: PVC-U wetted per AQS-STD-002 rules M1 and "
                 "M2, no metal wetted part; CA does not apply to the polymer"},
    "a_mach": {"guard": "service-zone guard rail over the front-right floor zone "
               "(A-MACH: guard drawn; layout choice, WORK_ORDER W12)",
               "anchors": "4 M10 wedge anchors, tray to slab (fasteners.csv)",
               "purchased": "none named on the node or the duty sheet for this "
               "station - none drawn (the criterion has nothing to match, WORK_ORDER W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections on tray risers, flush at "
    "the envelope faces (duty section 4: atmospheric joints are hose; the W4 110 "
    "percent rule draws no flange where no process pressure is stated); the schedule "
    "rating column (Class 150) is carried verbatim as text; clamped datums named in "
    "nozzles_drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Bund tray {L:g} x {W:g}, floor {T_TRAY:g} + curb {CURB_H:g} x {CURB_T:g}", 1,
     "PVC-U plate", mass["tray"], "make",
     "skid layout choice (WORK_ORDER W12); CA 0 mm (AQS-STD-001 polymer rule); the "
     "duty section 4 prose own-bund lines are room-side containment (hold)"],
    ["2", f"Day tank OD {D:g}, wall 10 mm, z {Z_SH0:g}..{Z_TOP:g}, with heads", 1,
     "PVC-U plate/pipe", mass["tank"], "make",
     "duty section 3 PVC-U wetted (rules M1 and M2); station day-tank envelope - no "
     "vessel diameter or holdup basis on the node or duty (hold, WORK_ORDER W12)"],
    ["3", f"Service-zone guard rail {GUARD[0]:g} x {GUARD[1]:g} x {GUARD[2]:g}, tube "
          "12 (A-MACH: guard drawn)", 1, "PP tube", mass["guard_rail"], "make",
     "guard over the front-right floor zone; layout choice (WORK_ORDER W12)"],
    ["4", "Nozzle set per docs-authority/nozzles/WS_PHOS.csv: 8 atmospheric "
          "open-bore tube connections on tray risers (drain through the floor, vent "
          "riser on the tank head)", len(schedule), "PVC-U", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric per duty section 4; bore per "
     "the lib/dn Sch 40 table"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("PVC-U", joint="polymer"), 4,
     "tray to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "storage-sizing box (node size_mm, AQS-DUTY-064); the duty section 4 "
             "prose seed line 800 x 800 x 1100 is an older figure (WORK_ORDER W12)",
    "tank": {"od_mm": D, "xy_mm": [TX, TY], "z_mm": [Z_SH0, Z_TOP]},
    "tray_mm": T_TRAY,
}
p["design"] = {
    "machine": "phosphoric acid day-station (H3PO4 to WET_BENCH, phosphate to "
               "dopant; duty section 2: seven-day charge basis)",
    "mat": "PVC-U wetted per AQS-STD-002 rules M1 and M2 (duty section 3)",
    "ca_mm": CA_TANK,
    "wall_mm": 10.0, "wall_basis": "study fab-page polymer wall (WORK_ORDER W12)",
    "internals": "none drawn (node internals row none; WORK_ORDER W12)",
    "purchased": "none named on the node or the duty sheet - none drawn (WORK_ORDER W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; tank axis at x 300, y 380, z up; tray "
             "floor z 0..20; guard rail over the front-right floor zone",
    "nozzle_spread": "the schedule gives face and height only; side rows ride tray "
                     "risers packed from x 420/470; drain through the floor at x 560; "
                     "vent riser on the tank head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
