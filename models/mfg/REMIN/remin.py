"""REMIN manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared
reader (models/mfg/lib/graph_node.py); the params.json write-back beside it carries
only the builder-owned envelope, design and layout blocks.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 600 mm, node size_mm (set by docs-authority/_storage_sizing.py,
  AQS-DUTY-064). The duty section 2 line "Envelope 600 x 400 x 800 mm is the shell"
  predates the storage-sizing box - the node governs and the older figure is named
  (holds, W12). The build fills the node box.
- Body: a dosing skid - vertical PVC-U day tank (OD 460, wall 10 per the study fab
  page, plinth tray with heads) plus the purchased envelopes the node design block
  names: 2 x metering diaphragm pumps (Ca slurry, MgCl2) and the UV unit after the
  dose (potable integrity). Purchased items are drawn as their envelope and
  interface, not as invented internals (plan rule 6); their internals stay with the
  maker (holds, W12).
- Internals: the node carries `internals: none`, so the tracker records no internal
  solid; the pumps and UV are equipment envelopes on the skid, not node internals.
- Material: PVC-U drawn (duty section 3: "PVC-U or HDPE, per AQS-STD-002 rule M1";
  CATCH_TANK idiom). The unresolved HDPE alternative is a named hold (W12). CA does
  not apply to the polymer (AQS-STD-001).
- Nozzles: all 5 rows of docs-authority/nozzles/REMIN.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: side connections
  ride tray risers, flush at the envelope faces (the tank stands clear of the ±Y
  faces to leave the pump and UV floor zone); the schedule rating column
  (Class 150) is carried verbatim as text, no flange (W4 110 % rule - no process
  pressure stated). N2/N5 outlet datums 600 predates the box and clamps to the
  stub-radius bound (hold, W12). N3 drain through the tray floor (50 datum); N4
  vent flush at the tank top head (its 800 datum predates the box - hold, W12).
- A-VES: the duty section 2 carries a holdup basis (7 days of throughput at the
  10 L/d potable tap = 0.0700 m3 working volume); the model working level is set
  by it and reported. It is not turned into a new residence-time claim.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("REMIN")           # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 600, storage-sizing box
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_TRAY = 20.0
T_WALL = 10.0                   # study fab-page polymer wall - no node booking (WORK_ORDER W12)
D = 460.0                       # day tank OD (layout choice: leaves the pump/UV floor zone)
R_IN = D / 2 - T_WALL                                        # 220
TX, TY = 300.0, 350.0           # tank axis: back of the skid, clear of the +Y riser zone
Z_SH0, Z_SH1 = 40.0, H - T_TRAY                              # shell 40..580
T_HEAD = 20.0
Z_TOP = H - T_HEAD                                           # top head 580..600
DUTY_WORKING = 0.0700            # m3, 7 days of throughput, duty section 2 (A-VES basis)
CA = materials.ca_for("PVC-U")                               # 0.0, polymer: AQS-STD-001
RHO = materials.density("PVC_U")                            # 1400, lib table
RHO_PP = materials.density("PP")                             # 910, purchased-envelope mass basis

assert TY + D / 2 <= W, "tank must stay inside the envelope"

# pump and UV floor zone (front strip), tank footprint checked clear of it
PUMP = (110.0, 90.0, 130.0)     # metering pump envelope, L x W x H (layout choice, W12)
PUMP_X0, PUMP_YS = 490.0, (15.0, 115.0)
UV_D, UV_LEN = 90.0, 220.0      # UV lantern envelope, horizontal on the tray front-left
UV_X0, UV_YC = 40.0, 60.0


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- tray
tray = box(0, 0, 0, L, W, T_TRAY)
parts["tray"] = tray

# ---------------------------------------------------------------- day tank
tank = (cq.Workplane("XY", origin=(TX, TY, Z_SH0)).circle(D / 2)
        .circle(R_IN).extrude(Z_SH1 - Z_SH0))
tank = tank.union(cq.Workplane("XY", origin=(TX, TY, Z_TOP)).circle(D / 2)
                  .extrude(T_HEAD))                                          # top head 580..600
tank = tank.union(cq.Workplane("XY", origin=(TX, TY, T_TRAY - 2.0)).circle(D / 2)
                  .extrude(Z_SH0 + T_HEAD - T_TRAY + 2.0))                   # base head laps tray
parts["tank"] = tank

# ---------------------------------------------------------------- purchased envelopes (plan rule 6)
pumps = None
for y0 in PUMP_YS:
    p = box(PUMP_X0, y0, T_TRAY - 2.0, PUMP[0], PUMP[1], PUMP[2])
    pumps = p if pumps is None else pumps.union(p)
parts["metering_pumps"] = pumps
uv = (cq.Workplane("YZ", origin=(UV_X0, UV_YC, 64.0)).circle(UV_D / 2).extrude(UV_LEN))
parts["uv_unit"] = uv

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
CLAMP_MARGIN = 0.7                             # stub radius clearance to the faces
Y_RISER = 60.0                                 # riser stand-off from each face (layout, W12)
STUB_PIERCE = 5.0                              # past the riser wall, so the union fuses


def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def z_for(row):
    """Drawn centreline height for a side nozzle, clamped deep enough that the
    branch and its riser top both stay inside the box."""
    h = float(row["height_mm"])
    od_s = dn.pipe_od(row["size"])
    hi = H - od_s - 8.0
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
    if face in ("-Y", "+Y") and r["size"] in dn.PIPE:
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

# pack side rows clear of the tank footprint at the riser line (layout choice, W12)
PACK_X = {"-Y": 300.0, "+Y": 470.0}
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    x = PACK_X[face]
    for r in rows:
        w = dn.pipe_od(r["size"]) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz_pieces, drawn, n_drawn = [], {}, 0
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    if dnl not in dn.PIPE:
        # non-piped row: the power terminal (cable schedule X-ELS-06) is electrical,
        # not piped - carried verbatim, not drawn (no STEP/BOM/geometry change)
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal (cable schedule X-ELS-06, AQS-ELEC-010): "
                              "electrical, not piped - carried verbatim, not drawn"}
        continue
    n_drawn += 1
    od = dn.pipe_od(dnl)
    if face0 == "bottom":                      # N3 drain: open bore through the tray floor
        s = tube(dnl, 40.0 - T_TRAY + 2.0).translate((560.0, 300.0, T_TRAY - 2.0))
        note = "drain, open bore through the tray floor, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, 560.0
    elif face0 == "top":                       # N4 vent: flush at the tank top head
        s = nozzles.hose_barb(round(od - 2 * dn.pipe_wall(dnl), 2), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (TX, TY), (L, W, H))
        note = ("vent flush at the tank top head; schedule datum 800 predates the box "
                "(hold, WORK_ORDER W12)")
        z_d, x_d = H, TX
    else:
        z_d, note = z_for(r)
        x_d = layout_x[tag]
        y_r = Y_RISER if face == "-Y" else W - Y_RISER
        riser = tube(dnl, z_d - T_TRAY + 2.0 + od / 2 + 4.0).translate((x_d, y_r, T_TRAY - 2.0))
        branch = nozzles.place_on_face(tube(dnl, Y_RISER - od / 2 + 5.0), face, z_d,
                                       (x_d, W / 2), (L, W, H))
        s = riser.union(branch)
        note = (note or "schedule datum drawn") + (
            "; atmospheric open-bore tube on a tray riser, flush at the envelope face "
            "(duty section 4; hose makeup by the connecting line at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube", "dn": dnl, "face": face, "height_mm": float(r["height_mm"]),
                  "drawn_height_mm": z_d, "x_mm": x_d, "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
# the pieces stay a compound; each roots in the tray or tank and is fused piecewise
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (A-VES, duty basis)
area = math.pi * (R_IN / 1000.0) ** 2
z_level = round((Z_SH0 + T_HEAD) + DUTY_WORKING / area * 1000.0, 1)
v_liq = round(math.pi * R_IN ** 2 * (z_level - (Z_SH0 + T_HEAD)) / 1e9, 4)
assert abs(v_liq - DUTY_WORKING) < 1e-6, (v_liq, DUTY_WORKING)
assert z_level < Z_SH1, "working level must sit in the tank shell"

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
    "tray": parts["tray"].val().Volume() * RHO / 1e9,
    "tank": parts["tank"].val().Volume() * RHO / 1e9,
    "metering_pumps": parts["metering_pumps"].val().Volume() * RHO_PP / 1e9,
    "uv_unit": parts["uv_unit"].val().Volume() * RHO_PP / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "storage-sizing box (node size_mm, AQS-DUTY-064); the duty section 2 "
    "shell line 600 x 400 x 800 predates it (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_liq,
    "holdup_basis": "the duty section 2 holdup basis (7 days of throughput at the 10 L/d "
    "potable tap = 0.0700 m3) sets the working level z " + f"{z_level:g}" + " (A-VES: "
    "the duty already carries a holdup basis, so the model level is set by it and "
    "reported; not turned into a new residence-time claim)",
    "tank": {"wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall (10 mm); "
             "no thickness booked on the node (WORK_ORDER W12)",
             "internals": {"source": "none: the node internals row is none; the pumps "
                           "and UV are purchased equipment envelopes on the skid, not "
                           "node internals",
                           "basis": "no internal solid drawn; purchased internals stay "
                           "with the maker (WORK_ORDER W12)"}},
    "purchased": {
        "basis": "plan rule 6: purchased items are named as purchased, drawn as their "
        "envelope and interface; the node design block names them",
        "metering_pumps": "2 x metering diaphragm (Ca slurry, MgCl2) - node design "
        "block; envelope " + f"{PUMP[0]:g} x {PUMP[1]:g} x {PUMP[2]:g}" + " each; "
        "drive rating with the maker TDS at order",
        "uv_unit": "UV unit after the dose (potable integrity) - node design block; "
        "envelope OD " + f"{UV_D:g}" + " x " + f"{UV_LEN:g}" + " long on the tray "
        "front-left; lamp rating with the maker TDS at order",
        "skid_duty_kW": 0.046,
    },
    "material": {"class": "PVC-U", "ca_mm": CA,
                 "basis": "duty section 3: PVC-U or HDPE per AQS-STD-002 rule M1; "
                 "PVC-U drawn, the HDPE alternative is a named hold (WORK_ORDER W12); "
                 "corrosion allowance does not apply to the polymer"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections on tray risers, flush at "
    "the envelope faces (duty section 4: atmospheric tube or hose; the W4 110 % rule "
    "draws no flange where no process pressure is stated); the schedule rating column "
    "(Class 150) is carried verbatim as text; clamped datums named in nozzles_drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Day tank OD {D:g}, wall {T_WALL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with heads", 1,
     "PVC-U plate/pipe", mass["tank"], "make",
     "duty section 3 PVC-U-or-HDPE conditional hold (PVC-U drawn, WORK_ORDER W12); "
     "wall the study fab-page polymer value (hold); CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"Skid tray {L:g} x {W:g} x {T_TRAY:g}", 1, "PVC-U plate", mass["tray"], "make",
     "skid layout choice (WORK_ORDER W12); the duty section 2 shell line "
     "600 x 400 x 800 predates the storage-sizing box (hold)"],
    ["3", "Metering diaphragm pump, Ca slurry duty (node design block: 2 x metering "
          f"diaphragm); envelope {PUMP[0]:g} x {PUMP[1]:g} x {PUMP[2]:g}", 2,
     "polymer (maker class at order)", mass["metering_pumps"], "buy",
     "plan rule 6: purchased item named with the rating from the node; drawn as the "
     "envelope and interface only; wetted parts and drive rating per the maker TDS "
     "at order (WORK_ORDER W12)"],
    ["4", f"UV unit, potable integrity (node design block); envelope OD {UV_D:g} x "
          f"{UV_LEN:g} long", 1, "polymer (maker class at order)", mass["uv_unit"], "buy",
     "plan rule 6: purchased item named with the rating from the node; UV unit after "
     "the dose; lamp rating per the maker TDS at order (WORK_ORDER W12)"],
    ["5", "Nozzle set per docs-authority/nozzles/REMIN.csv: 5 atmospheric open-bore "
          "tube connections on tray risers (drain through the floor, vent at the tank "
          "top head)", n_drawn, "PVC-U", mass["nozzles"], "make",
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
    [None, "M8 hold-down bolt", fasteners.grade_for("PVC-U", joint="polymer"), 8,
     "purchased pump and UV envelopes to the tray, 4 per envelope (count from the "
     "model)", "polymer joint to the supplier rule; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "storage-sizing box (node size_mm, AQS-DUTY-064); the duty section 2 "
             "shell line 600 x 400 x 800 is an older figure (WORK_ORDER W12)",
    "tank": {"od_mm": D, "xy_mm": [TX, TY], "z_mm": [Z_SH0, Z_TOP]},
    "tray_mm": T_TRAY,
}
p["design"] = {
    "service": "remineralization dosing skid, atmospheric (duty sections 2, 4 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study fab-page polymer wall", "ca_mm": CA,
    "internals": "none drawn: pumps and UV are purchased envelopes (plan rule 6)",
    "working_level_mm": z_level,
    "working_level_basis": "the duty section 2 holdup basis (7 days at 10 L/d = 0.07 m3)",
    "machine": P["design"]["machine"],
    "pumps": P["design"]["pumps"],
    "uv": P["design"]["uv"],
    "chemistry": P["design"]["chemistry"],
}
p["layout"] = {
    "frame": "origin at the envelope corner; tank axis at x 300, y 350, z up; tray "
             "floor z 0..20 over the full envelope",
    "purchased_zone": "pump envelopes front-right (x 490..600, y 15..205), UV lantern "
                      "front-left along x (x 40..260, y centre 60); the tank footprint "
                      "stays clear of the floor zone",
    "nozzle_spread": "the schedule gives face and height only; side rows ride tray "
                     "risers packed clear of the tank at the riser line; drain through "
                     "the floor; vent at the tank top head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
