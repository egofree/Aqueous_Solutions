"""GROW_BED manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 9, F-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along the bed length, y along the bed width, z up, origin at the
bed corner. Every dimension is an authority figure or a named layout choice:

- A-FARM: the bed area matches the node and is NOT shrunk to fit the block.
  The node area is area_m2 29.12 - "crew duty (A-M-229): S14 4.2 kg/d / 0.1442
  kg/m2/d = 29.12 m2 (supersedes the BH ~28 m2 / 120.4 m2 residue-claim studies
  [A-M-151])". The build is the full bed: interior 7280 x 4000 mm = 29.12 m2,
  framed per A-M-469 (4 x 2 nominal 2000 x 1000 bays, 15 mm basin walls, LED
  canopy to z 900 + 15 mm rail). The node size_mm 7310 x 4030 x 915 is the
  assembly envelope - the reservation the build sits inside (2026-11-08
  reservation adoption: the former single-bay study box stated no bay count or
  canopy height and is withdrawn). The bay module (2000 x 1000 x 400) lives on
  the node design block grow_bed_layout_mm; `cad/stl/GROW_BED.stl` keeps the
  in-envelope bay module per the CRYO_ASU X-PAR-04 treatment (scope recorded in
  check.json cad_stl_scope), and the full bed lives in `export/` and the STEP.
- Bed per the node and duty section 3: HDPE basin (walls and floor 15 mm) with an
  EPDM liner (5 mm, the ponded-zone class of the GROWBED_A idiom), LECA media
  envelope at a 250 mm study depth (the duty names no media depth - hold, W12),
  a drain sump at the bay corner with the N9 drain above it (A-FARM: liner and
  drain drawn), internal cross-ribs framing the nominal 2000 x 1000 bays. Height
  400 mm is the node z. Duty section 3: "HDPE or PVC for the water. The frame is
  not the wetted part"; CA does not apply to the polymer.
- LED canopy per the node continuous stamp (2.0463 kW = 29.12 m2 x 70.3 W/m2,
  DLI 17 at 2.8 umol/J, A-M-133/A-M-144 crew duty): perimeter posts and rails
  with the LED panel envelope over the bed (purchased per plan rule 6, the node
  rating). Canopy height is a layout choice (hold, W12).
- Nozzles: all 22 rows of docs-authority/nozzles/GROW_BED.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1-N4 in on
  the -Y wall at z 80; N5-N8 out on the +Y wall at z 300 (bed water line); N13/
  N14/N16/N17/N19 in at z 160; the canopy rows N11, N12, N15, N18, N20, N21, N22
  at the schedule z 600 datum sit above the 400 mm bed - drawn flush at the
  envelope top with the placeholder note (the GLASS_BURNOUT stale-datum idiom;
  hold, W12). N9 drain flush at the envelope bottom (50 datum) above the sump;
  N10 vent flush at the envelope top. The schedule rating column (Class 150)
  carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("GROW_BED")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
LAYOUT = (P.get("design") or {}).get("grow_bed_layout_mm") or {}
IX, IY = (float(v) for v in LAYOUT["interior_xy_mm"])      # the A-M-229 area, framed (A-M-469)
T_WALL = float(LAYOUT["wall_mm"])                          # HDPE basin wall/floor (GROWBED_A idiom)
CANOPY_Z1 = float(LAYOUT["canopy_top_mm"])                 # canopy top (registered layout, W12)
RAIL_ALLOW = float(LAYOUT["rail_allowance_mm"])            # the rail above the canopy top
T_LINER = 5.0                                              # EPDM liner
MEDIA_D = 250.0                                            # LECA media depth (study, W12)
SUMP = (1700.0, 700.0, 300.0, 300.0, 120.0)                # drain sump x,y,dx,dy,depth (W12)
LED_W = 2.0463                                             # node continuous kW (A-M-144)
REV = P["graph_revision"]
UNIT = P["unit_id"]
AREA_M2 = float(GN.params["area_m2"])                     # node area_m2 (A-M-229)
BW, BD, BH = (float(v) for v in LAYOUT["bay_module_mm"])   # the nominal bay module (A-M-469)
LX, LY = IX + 2 * T_WALL, IY + 2 * T_WALL                  # basin outer 7310 x 4030
LZ = BH                                                    # the bed depth the node sized
PANEL_T = 60.0
RHO_HDPE = materials.density("HDPE")
RHO_EPDM = materials.density("EPDM")
RHO_LECA = materials.density("LECA")
RHO_CS = materials.density("CS")

assert abs(IX * IY / 1e6 - float(GN.params["area_m2"])) < 1e-9, "bed interior matches the A-M-229 area"

T_X0, T_Y0 = 0.0, 0.0                                      # bed origin


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def basin_piece(x0, y0, x1, y1):
    """Basin walls + floor + liner + media over the region [x0,x1) x [y0,y1)."""
    piece = box(x0, y0, 0.0, x1 - x0, y1 - y0, LZ)                      # outer wall block
    piece = piece.cut(box(x0 + T_WALL, y0 + T_WALL, T_WALL,
                          x1 - x0 - 2 * T_WALL, y1 - y0 - 2 * T_WALL, LZ - T_WALL))
    piece = piece.union(box(x0 + T_WALL, y0 + T_WALL, 0.0,                        # floor
                            x1 - x0 - 2 * T_WALL, y1 - y0 - 2 * T_WALL, T_WALL))
    piece = piece.union(box(x0 + T_WALL, y0 + T_WALL, T_WALL,                     # EPDM liner
                            x1 - x0 - 2 * T_WALL, y1 - y0 - 2 * T_WALL, T_LINER))
    return piece


def media_piece(x0, y0, x1, y1):
    return box(x0 + T_WALL + T_LINER, y0 + T_WALL + T_LINER, T_WALL + T_LINER,
               x1 - x0 - 2 * (T_WALL + T_LINER), y1 - y0 - 2 * (T_WALL + T_LINER), MEDIA_D)


parts = {}

# ---------------------------------------------------------------- bay module (the registry subset)
bay = basin_piece(0.0, 0.0, 2000.0, 1000.0)
bay = bay.union(media_piece(0.0, 0.0, 2000.0, 1000.0))
sx, sy, sdx, sdy, sdz = SUMP
bay = bay.union(box(sx, sy, 0.0, sdx, sdy, T_WALL + sdz))                 # drain sump block
bay = bay.union(box(sx + 20.0, sy + 20.0, T_WALL,
                    sdx - 40.0, sdy - 40.0, sdz).cut(
    box(sx + 30.0, sy + 30.0, 0.0, sdx - 60.0, sdy - 60.0, sdz)))         # sump rim (hollow)
parts["bay_module"] = bay

# ---------------------------------------------------------------- basin: the rest of the L
rest = basin_piece(2000.0, 0.0, LX, LY)
rest = rest.union(basin_piece(0.0, 1000.0, 2000.0, LY))
rest = rest.union(media_piece(2000.0, 0.0, LX, LY))
rest = rest.union(media_piece(0.0, 1000.0, 2000.0, LY))
# internal cross-ribs framing the nominal 2000 x 1000 bays (every 1820 mm inside)
ribs = None
for rx in range(2000, int(IX), 1820):
    r = box(T_WALL + rx, T_WALL, 0.0, 20.0, IY, T_WALL + 120.0)
    ribs = r if ribs is None else ribs.union(r)
for ry in range(1000, int(IY), 1000):
    r = box(T_WALL, T_WALL + ry, 0.0, IX, 20.0, T_WALL + 120.0)
    ribs = r if ribs is None else ribs.union(r)
parts["basin"] = rest if ribs is None else rest.union(ribs)

# ---------------------------------------------------------------- LED canopy (node 2.0463 kW, A-M-144)
canopy = None
for cx_, cy_ in ((60.0, 60.0), (LX - 120.0, 60.0), (60.0, LY - 120.0), (LX - 120.0, LY - 120.0)):
    c = box(cx_, cy_, LZ, 60.0, 60.0, CANOPY_Z1 - LZ)
    canopy = c if canopy is None else canopy.union(c)
for (rx, ry, dx, dy) in ((0.0, 0.0, LX, 60.0), (0.0, LY - 60.0, LX, 60.0),
                         (0.0, 0.0, 60.0, LY), (LX - 60.0, 0.0, 60.0, LY)):
    canopy = canopy.union(box(rx, ry, CANOPY_Z1 - 60.0, dx, dy, 60.0))
parts["canopy"] = canopy
parts["led_panel"] = box(T_WALL + 200.0, T_WALL + 200.0, CANOPY_Z1 - 60.0 - PANEL_T,
                         IX - 400.0, IY - 400.0, PANEL_T)

# ---------------------------------------------------------------- nozzles (schedule verbatim, full build)
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
    assert span <= LX - 120.0, (face, z, span)
    x = max(80.0, (LX - span) / 2)
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
    if r["face"] == "bottom":                             # N9: drain flush at the envelope bottom
        s = tube_z("DN15", T_WALL + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (sx + sdx / 2, sy + sdy / 2), (LX, LY, LZ))
        note = "drain flush at the envelope bottom over the bay sump; 50 datum is the schedule placeholder"
        drawn_h = 0.0
    elif r["face"] == "top":                              # N10: vent flush at the envelope top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (LX / 2, LY / 2), (LX, LY, LZ))
        note = "vent flush at the envelope top (the canopy top; 400 datum is the bed height)"
        drawn_h = LZ
    else:
        z_draw = h
        if h > LZ:                                        # canopy rows at the stale 600 datum
            z_draw = CANOPY_Z1
            note += ("; the schedule datum z 600 predates the build height - "
                     "drawn flush at the envelope top (hold, WORK_ORDER W12)")
        else:
            assert h <= LZ - od / 2 - 5.0, (tag, h)
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
        s = nozzles.place_on_face(s, face, z_draw, (layout_x[tag], LY / 2), (LX, LY, LZ))
        drawn_h = z_draw
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": drawn_h,
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
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.5, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04): the in-envelope BAY MODULE
# (2000 x 1000 x 400, the design-block bay per A-M-469) - the CRYO_ASU treatment;
# the full bed is the export/ build and the STEP, inside the 7310 x 4030 x 915
# reservation (node size_mm).
bay_solid = parts["bay_module"].val()
bay_solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                                 tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [float(v) for v in P["size_mm"]]))
bay_dims = stl_bbox_mm(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")))
RHO_OF = {"led_panel": RHO_CS, "canopy": RHO_CS}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_HDPE) / 1e9, 2) for k, v in parts.items()}
# the bay and basin masses mix HDPE and the LECA media: split the media volume out
media_vol = (IX - 2 * T_LINER) * (IY - 2 * T_LINER) * MEDIA_D + \
            (2000.0 - 40.0) * (1000.0 - 40.0) * MEDIA_D      # rest-of-bed + bay media
mass["bay_module"] = round((parts["bay_module"].val().Volume() - 1960.0 * 960.0 * MEDIA_D)
                           * RHO_HDPE / 1e9 + 1960.0 * 960.0 * MEDIA_D * RHO_LECA / 1e9, 2)
mass["basin"] = round((parts["basin"].val().Volume() - (media_vol - 1960.0 * 960.0 * MEDIA_D))
                      * RHO_HDPE / 1e9
                      + (media_vol - 1960.0 * 960.0 * MEDIA_D) * RHO_LECA / 1e9, 2)
mass["media_total_kg"] = round(media_vol * RHO_LECA / 1e9, 2)
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [float(v) for v in P["size_mm"]],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "cad_stl_scope": "in-envelope bay module of the build, metres (X-PAR-04 "
                     "registry: the registry keeps the bay module 2000 x 1000 x "
                     "400, the design-block bay per A-M-469; the node size_mm "
                     "7310 x 4030 x 915 is the assembly envelope and the full "
                     "bed lives in export/ and the STEP - the CRYO_ASU "
                     "treatment; 2026-11-08 reservation adoption)",
    "cad_stl_bbox_mm": bay_dims,
    "machine": {
        "type": "crop grow bed per the node area_basis (A-M-229): HDPE basin "
                f"(walls and floor 15 mm) with EPDM liner (5 mm), interior "
                f"{IX:g} x {IY:g} mm = {AREA_M2:g} m2 (NOT shrunk to fit the "
                "study box - A-FARM), LECA media envelope at a 250 mm study "
                "depth, drain sump at the bay corner with the N9 drain above it, "
                "internal cross-ribs framing the nominal 2000 x 1000 bays, and "
                f"the LED canopy with the panel envelope ({LED_W:g} kW = "
                "29.12 m2 x 70.3 W/m2, DLI 17 at 2.8 umol/J, A-M-133/A-M-144)",
        "area": {"m2": AREA_M2, "interior_mm": [IX, IY],
                 "basis": "crew duty (A-M-229): S14 4.2 kg/d / 0.1442 kg/m2/d; "
                          "supersedes the A-M-151 residue-line claim studies",
                 "a_farm": "bed area matches the node; liner and drain drawn; "
                           "not shrunk to fit the block"},
        "misfit": {"export_bbox_mm": dims, "size_mm": [float(v) for v in P["size_mm"]],
                   "note": "the reservation is the built array per A-M-469 (2026-11-08 "
                           "adoption): the former single-bay study box stated no bay "
                           "count or canopy height and is withdrawn"},
        "media": "LECA media envelope at a 250 mm study depth (the duty names no "
                 "media depth - hold, WORK_ORDER W12); GROWBED_A media idiom",
        "circulation": "duty section 2: 19100.9 kg/d, two-minute holdup "
                       "0.0265 m3 - reported, not a residence time claim",
        "purchased": "the LED panel envelope (2.0463 kW node stamp, A-M-144) - "
                     "purchased per plan rule 6",
        "material": "HDPE basin, EPDM liner, LECA media (duty section 3: HDPE or "
                    "PVC for the water; the frame is not the wetted part); "
                    "canopy painted A500",
        "ca_mm": 0.0,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1-N4 in on -Y at z 80, N5-N8 out on +Y at z 300 "
                    "(the bed water line), the z 160 inlets on -Y, and the "
                    "canopy rows (N11/N12/N15/N18/N20/N21/N22) drawn flush at "
                    "the envelope top - the schedule z 600 datum predates the "
                    "build height (hold, W12); N9 drain over the bay sump; N10 "
                    "vent at the top; no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"HDPE basin: walls and floor 15 mm, interior {IX:g} x {IY:g} mm "
           f"(29.12 m2, A-M-229) x 400 high, with internal cross-ribs", 1,
     "HDPE (duty section 3)", mass["bay_module"] + mass["basin"], "make",
     "A-FARM: bed area matches the node, not shrunk to fit the block; CA does "
     "not apply to the polymer (AQS-STD-001)"],
    ["2", "EPDM liner 5 mm over the basin floor and walls", 1,
     "EPDM (duty section 3 water class; GROWBED_A liner idiom)",
     round((IX * IY + 2 * (IX + IY) * LZ) * T_LINER * RHO_EPDM / 1e9, 2), "buy",
     "A-FARM: liner drawn; sheet goods, buy roll"],
    ["3", f"LECA media envelope at a 250 mm study depth over {IX:g} x {IY:g} mm", 1,
     "expanded clay (LECA, buy charge; envelope drawn)", 0.0, "buy",
     "media depth is a study value (hold, WORK_ORDER W12); the charge is a buy "
     "row, the envelope drawn per plan rule 6"],
    ["4", "Drain sump at the bay corner (300 x 300 x 120) with the N9 drain "
           "above it", 1, "HDPE", 0.0, "make",
     "A-FARM: drain drawn; sump size is a study value (hold, WORK_ORDER W12)"],
    ["5", f"LED canopy: 4 posts and perimeter rails to z {CANOPY_Z1:g}", 1,
     "painted A500 (farm frame class)", mass["canopy"], "make",
     "canopy height is the layout choice (hold, WORK_ORDER W12); frame is not "
     "the wetted part (duty section 3)"],
    ["6", "LED panel envelope over the bed", 1,
     "purchased LED fixture (envelope)", mass["led_panel"], "buy",
     "node continuous 2.0463 kW = 29.12 m2 x 70.3 W/m2, DLI 17 at 2.8 umol/J "
     "(A-M-133/A-M-144); purchased per plan rule 6"],
    ["7", "Nozzle set per docs-authority/nozzles/GROW_BED.csv: 22 rows drawn as "
           "DN15 tube stubs (bed wall and canopy rows)", len(schedule),
     "HDPE/CPVC tube", 0.0, "make",
     "schedule tags/faces/heights verbatim; the z 600 canopy rows drawn at the "
     "envelope top (stale datum, hold W12); atmospheric per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 basin hold-down bolt + nut", fasteners.grade_for("316L"), 8,
     "basin flange ribs to the pad, 2 per wall line (count from the model)",
     "A4-70 on the polymer-joint hardware per the plan grade rule (polymer "
     "supplier rule named at order)"],
    [None, "M12 canopy base plate bolt + nut", fasteners.grade_for("CS"), 8,
     "canopy posts to the pad, 2 per post (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [float(v) for v in P["size_mm"]],
    "basis": P.get("size_basis") or "node size_mm is the bay-module registry box; "
             "the bed area is the A-M-229 29.12 m2 duty",
    "bed": {"interior_mm": [IX, IY], "outer_mm": [LX, LY], "height_mm": LZ,
            "area_m2": AREA_M2},
    "wall_mm": T_WALL, "liner_mm": T_LINER, "media_depth_mm": MEDIA_D,
    "sump_mm": SUMP,
    "canopy_z_mm": [LZ, CANOPY_Z1],
}
p["design"] = {
    "service": "GROW_BED: the crew-duty crop bed (S14 4.2 kg/d food out on the "
               "BVAD2022 tomato proxy, A-M-229); irrigated media culture with "
               "the LED canopy (duty sections 1 and 3)",
    "area_basis": "crew duty (A-M-229): 29.12 m2; supersedes the A-M-151 "
                  "residue-line claim studies",
    "material": "HDPE basin, EPDM liner, LECA media; canopy painted A500",
    "ca_mm": 0.0,
    "material_basis": "duty section 3: HDPE or PVC for the water; the frame is "
                      "not the wetted part; CA does not apply to the polymer",
    "purchased": "LED panel envelope (2.0463 kW node stamp, A-M-144; plan rule 6); "
                 "LECA media charge (buy)",
    "a_farm": "bed area matches the node; liner and drain drawn; not shrunk to "
              "fit the block",
    "cad_stl_scope": report["cad_stl_scope"],
}
p["layout"] = {
    "frame": "origin at the bed corner; basin interior 7280 x 4000 with cross-"
             "ribs framing the nominal 2000 x 1000 bays; sump at the bay corner "
             "(x 1700..2000, y 700..1000); LED canopy posts and rails to z 900 "
             "with the panel at z 840",
    "supports": "basin on the pad + hold-down bolts; canopy posts base-plated",
    "nozzle_spread": "the schedule gives face and height only; bed rows on the "
                     "-Y/+Y walls at z 80/160/300; the z 600 canopy rows drawn "
                     "at the envelope top; drain over the sump, vent at the "
                     "centreline; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; the "
                      "full-bed build is the export/ STEP (the registry carries "
                      "the bay module)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
