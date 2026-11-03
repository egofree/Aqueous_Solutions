"""GEO_GHEX manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 6, F-HX).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned)
and rebuilds every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (the
  placement seed seats a 1200 x 800 x 800 "bore field tie, massing only" box:
  the node governs, the seed figure is a named hold, WORK_ORDER W12). The build
  fills the node box.
- Unit per the node design block (design_survey_locked, ST-ORC-01): the ground
  heat exchanger - 2 boreholes at bore_depth_m 45, bore_spacing_m 6 m
  (bore_metres_installed 90), HDPE DR-11 U-tubes on loop_DN 32 with 25 %
  propylene-glycol loop fluid at loop_flow 0.2564 kg/s and loop_dT 3 K against
  the q_per_m 35 W/m and Q_ceiling_kW_th 3.0 class, tied by header_m 6 of
  horizontal header. The manufacturable hardware at the box is the manifold
  skid: DN32 HDPE flow/return header runs, the two bore-pair tie-in stubs to
  below grade (interface indication - the boreholes are drilled subsurface
  works, not shop fabrication; their depth and spacing are node facts named,
  not drawn to depth - hold, W12), the circulation-pump envelope
  (circ_pump_W 125.7, purchased per plan rule 6), and the glycol fill pot.
  Skid dimensions are study values (holds, W12).
- A-HX: the loop heat-transfer area is reported from the model and the node
  figures - pipe length 2 bores x 2 legs x 45 m + 6 m header = 186 m of DN32
  (OD 42.4) = 24.8 m2 of wetted loop area - and is NOT called a calculated
  duty: the duty sheet section 2 states no mass throughput; q_per_m 35 W/m and
  Q_ceiling_kW_th 3.0 are the node's survey-locked class figures.
- Nozzles: all 3 rows of docs-authority/nozzles/GEO_GHEX.csv drawn at tag,
  face, height and bore as atmospheric hose barbs flush at the envelope faces
  (duty section 4: atmospheric joints are hose; DN copied from the edge, not
  recalculated; rows read "Bore not calculated. Rating hose, atmospheric").
  N3 geothermal loop fluid out on +Y at z 600 (the loop tie to GEO_HP);
  N1 drain flush at the envelope bottom (50 datum); N2 vent flush at the
  envelope top (800 datum is the box top). The schedule rating column carried
  verbatim as text.
- Grout and borehole works are the site/well lane's scope; nothing below grade
  is drawn beyond the tie-in stubs (hold, W12).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}

T_PLINTH = 20.0
POST = 40.0                                                # hold-down/guard frame section
LOOP_DN = "DN32"                                           # node design loop_DN 32
HDR_Z0, HDR_Z1 = 300.0, 360.0                              # flow/return header lines
HDR_X0, HDR_X1 = 120.0, 700.0
BORE_X = (200.0, 800.0)                                    # bore tie-in stub stations
PUMP = (720.0, 150.0, 240.0, 220.0, 300.0, 480.0)          # circ-pump envelope (125.7 W node)
POT_R, POT_H = 70.0, 220.0                                 # glycol fill pot (study, W12)
RHO_HDPE = materials.density("HDPE")
RHO_CS = materials.density("CS")

assert L == 1000.0 and W == 600.0 and H == 800.0, "GEO_GHEX node envelope changed"
CY = W / 2
assert BORE_X[0] > HDR_X0 and BORE_X[1] < L - POST, "bore stubs on the skid"
assert PUMP[0] + PUMP[2] <= L - POST, "pump envelope clears the frame"
# A-HX loop area from the node-quoted run + drawn skid
LOOP_M = 2 * 2 * float(DS.get("bore_depth_m") or 45.0) + float(DS.get("header_m") or 6.0)
LOOP_AREA_M2 = math.pi * (dn.pipe_od(LOOP_DN) / 1000.0) * LOOP_M
assert abs(LOOP_M - 186.0) < 1e-9, "2 bores x 2 legs x 45 m + 6 m header"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def dn_pipe(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def vtube(od, x, y, z0, z1):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(od / 2).extrude(z1 - z0)


def tube_z(dnl, length):
    return dn_pipe(dnl, length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down/guard frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- flow/return headers (DN32 HDPE)
h0 = dn_pipe(LOOP_DN, HDR_X1 - HDR_X0).rotate((0, 0, 0), (0, 1, 0), 90).translate(
    (HDR_X0, CY - 80.0, HDR_Z0))
h1 = dn_pipe(LOOP_DN, HDR_X1 - HDR_X0).rotate((0, 0, 0), (0, 1, 0), 90).translate(
    (HDR_X0, CY + 80.0, HDR_Z1))
parts["headers"] = h0.union(h1)

# ---------------------------------------------------------------- bore-pair tie-in stubs (below-grade interface)
stubs = None
for bx in BORE_X:
    for dy, zz in ((-80.0, HDR_Z0), (80.0, HDR_Z1)):
        s = dn_pipe(LOOP_DN, zz + 40.0).translate((bx, CY + dy, 0.0))   # to the box floor
        stubs = s if stubs is None else stubs.union(s)
parts["bore_stubs"] = stubs

# ---------------------------------------------------------------- circulation pump envelope + fill pot
parts["pump_env"] = box(*PUMP)
parts["fill_pot"] = vtube(2 * POT_R, 860.0, CY, T_PLINTH, T_PLINTH + POT_H)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
Hose = {"DN15": 45.0, "DN25": 50.0}


def od_of(r):
    return dn.pipe_od(r["size"]) if r["size"].startswith("DN") else dn.pipe_od("DN15")


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


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
    assert span <= L - 120.0, (face, z, span)
    x = max(60.0, (L - span) / 2)
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric hose joint at the envelope face (duty section 4; bore not calculated, hose, atmospheric)"
    if r["face"] == "bottom":                             # N1: drain flush at the envelope bottom
        s = nozzles.stub("DN15", 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, CY - 200.0), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N2: 800 datum is the box top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, CY), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], CY), (L, W, H))
        if tag == "N3":
            note += "; the loop tie to GEO_HP (the S43 class edge)"
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": h if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
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
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
RHO_OF = {"plinth": RHO_CS, "frame": RHO_CS, "pump_env": RHO_CS}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_HDPE) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "ground heat exchanger manifold skid per the node design block "
                "(design_survey_locked, ST-ORC-01): DN32 HDPE flow/return "
                "header runs on the skid, two bore-pair tie-in stubs to below "
                "grade (interface indication), the circulation-pump envelope "
                "(circ_pump_W 125.7, node) and the glycol fill pot; the "
                "hold-down/guard frame pins the registry box",
        "bore_field": {"bores": DS.get("bores"), "depth_m": DS.get("bore_depth_m"),
                       "spacing_m": DS.get("bore_spacing_m"),
                       "metres_installed": DS.get("bore_metres_installed"),
                       "metres_required": DS.get("bore_metres_req"),
                       "grout": "borehole grout thermal (node material)",
                       "note": "the boreholes are drilled subsurface works - "
                               "not shop fabrication; the tie-in stubs are the "
                               "interface indication, the depth/spacing are "
                               "node facts named, not drawn to depth (hold, "
                               "WORK_ORDER W12)"},
        "loop": {"dn": LOOP_DN, "fluid": DS.get("loop_fluid"),
                 "flow_kg_s": DS.get("loop_flow_kg_s"), "dT_K": DS.get("loop_dT_K"),
                 "q_per_m_W": DS.get("q_per_m_W"), "Q_ceiling_kW_th": DS.get("Q_ceiling_kW_th"),
                 "T_source_K": DS.get("T_source_K"), "k_ground_W_mK": DS.get("k_ground_W_mK"),
                 "status": DS.get("status")},
        "a_hx_area": {"loop_m": LOOP_M, "area_m2": round(LOOP_AREA_M2, 2),
                      "basis": "pipe length 2 bores x 2 legs x 45 m + 6 m "
                               "header = 186 m of DN32 (OD 42.4) = 24.8 m2 "
                               "wetted loop area, from the model skid plus the "
                               "node-quoted buried run; NOT called a calculated "
                               "duty - the duty sheet states no mass throughput; "
                               "q_per_m 35 W/m and Q_ceiling 3.0 kW th are the "
                               "node's survey-locked class figures"},
        "purchased": "circulation pump envelope (125.7 W, node design "
                     "circ_pump_W) - purchased per plan rule 6",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04); 8 slab anchors (fasteners.csv)",
        "material": "HDPE DR-11 U-tubes, 1 in bore + horizontal runs; borehole "
                    "grout thermal (node material); skid frame painted A500",
        "ca_mm": 0.0,
        "study_dims": "skid header stations, pump envelope and fill pot are "
                      "study values (hold, WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (duty "
                    "section 4: atmospheric joints are hose; DN copied from the "
                    "edge, not recalculated; rows read 'Bore not calculated. "
                    "Rating hose, atmospheric'); N3 geothermal loop fluid out on "
                    "+Y at z 600 (the loop tie to GEO_HP); drain flush at the "
                    "envelope bottom (50 datum); vent flush at the envelope top "
                    "(800 datum is the box top); no flange (W4 110 % rule); the "
                    "schedule rating column carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["plinth"], "make", "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make", "frame pins the registry box (X-PAR-04); anchors in "
     "fasteners.csv"],
    ["3", f"DN32 HDPE flow/return header runs on the skid (x {HDR_X0:g}..{HDR_X1:g})",
     2, "HDPE DR-11 (node material)", mass["headers"], "make",
     "node design loop_DN 32; header_m 6 of horizontal header quoted on the "
     "node; skid stations are study values (hold, WORK_ORDER W12)"],
    ["4", "Bore-pair tie-in stubs, 2 off (below-grade interface indication)", 2,
     "HDPE DR-11", mass["bore_stubs"], "make",
     f"2 bores x {DS.get('bore_depth_m'):g} m at {DS.get('bore_spacing_m'):g} m "
     "spacing (node design; 90 m installed); the boreholes are drilled "
     "subsurface works - depth/spacing named, not drawn to depth (hold, "
     "WORK_ORDER W12)"],
    ["5", "Circulation pump envelope (125.7 W, node design circ_pump_W)", 1,
     "purchased pump (envelope)", mass["pump_env"], "buy",
     "purchased per plan rule 6, rating from the node; mass a table-density "
     "placeholder until the maker TDS quotes (W12)"],
    ["6", f"Glycol fill pot OD {2 * POT_R:g} x {POT_H:g} (study)", 1,
     "HDPE", mass["fill_pot"], "make",
     "fill point for the 25 % propylene-glycol loop fluid (node design); study "
     "size (hold, WORK_ORDER W12)"],
    ["7", "Nozzle set per docs-authority/nozzles/GEO_GHEX.csv: 3 hose barbs "
           "(DN15)", len(schedule), "HDPE", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim (bores not calculated, hose, "
     "atmospheric); atmospheric hose per duty section 4"],
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
    [None, "M10 header clip bolt + nut", fasteners.grade_for("CS"), 6,
     "DN32 header runs to the skid clip rail, 3 per run (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "headers": {"dn": LOOP_DN, "x_mm": [HDR_X0, HDR_X1], "z_mm": [HDR_Z0, HDR_Z1]},
    "bore_stubs_x_mm": BORE_X,
    "pump_env_mm": PUMP,
    "fill_pot": {"od_mm": 2 * POT_R, "h_mm": POT_H},
}
p["design"] = dict(DS)
p["design"].update({
    "service": "GEO_GHEX: the ground heat exchanger - 2 boreholes x 45 m at 6 m "
               "spacing, HDPE DR-11 U-tubes on the DN32 glycol loop, tied to "
               "GEO_HP by the S43 class edge (duty sections 1 and 4; "
               "ST-ORC-01 design_survey_locked)",
    "material": "HDPE DR-11 U-tubes, 1 in bore + horizontal runs; borehole "
                "grout thermal (node material)",
    "ca_mm": 0.0,
    "material_basis": "node material row; CA does not apply to the HDPE "
                      "(AQS-STD-001)",
    "a_hx_area": report["machine"]["a_hx_area"],
    "purchased": "circulation pump envelope (125.7 W, node)",
    "bore_scope": "the boreholes and grout are drilled subsurface works (site/"
                  "well lane); the skid is the shop hardware",
})
p["layout"] = {
    "frame": "origin at the envelope corner; header runs x 120..700 at z 300/360 "
             "on the skid centreline +/- 80; bore tie-in stubs at x 200 and 800 "
             "to the box floor; pump envelope x 720..940; fill pot at x 860",
    "below_grade": "the boreholes continue below the box floor to the 45 m node "
                   "depth at the 6 m node spacing - interface indication only",
    "supports": "plinth + hold-down frame + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; N3 on +Y at z 600 "
                     "(the GEO_HP tie), drain at x 430, vent at x 570; per-tag "
                     "positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
