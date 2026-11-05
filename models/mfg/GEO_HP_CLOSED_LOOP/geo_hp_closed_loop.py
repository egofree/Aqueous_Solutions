"""GEO_HP_CLOSED_LOOP manufacturing model, AQS-PLAN-006 work order (M0 lane,
tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the
shared reader (models/mfg/lib/graph_node.py); the params.json write-back
beside it carries only the builder-owned envelope, design and layout blocks.
It rebuilds every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (the
  placement seed seats an 800 x 800 x 800 "loop vessel beside GHEX" box: the
  node governs, the seed figure is a named hold, WORK_ORDER W12). The build
  fills the node box.
- Unit per the node design block: the closed source loop between the bore
  field (GEO_GHEX) and the heat-pump evaporators (GEO_HP) - the S43 class edge
  carries it on the graph at 0 kW idle standby; the design case is
  design_case_kW_th 3.0 at flow 0.2564 kg/s, DN 32, dT 3 K, head 25 m, with the
  AQS-DUTY-076 source-loop circulator at pump_W 125.7 (the node continuous
  0.1257 kW stamp). The skid: DN32 HDPE supply/return header runs, the loop
  buffer manifold vessel (the seed's "loop vessel"), the circulator envelope
  (purchased per plan rule 6), and the tie stubs - below-grade interface to the
  GHEX bore field and the skid-side tie toward GEO_HP (interface indications;
  the buried ground array is the GHEX/site lane's - hold, W12). Skid
  dimensions are study values (holds, W12).
- Nozzles: all 4 rows of docs-authority/nozzles/GEO_HP_CLOSED_LOOP.csv drawn
  at tag, face, height and bore as atmospheric hose barbs flush at the
  envelope faces (duty section 4: atmospheric joints are hose; DN copied from
  the edge, not recalculated; rows read "Bore not calculated. Rating hose,
  atmospheric"). N3 geothermal loop fluid in on -Y at z 160 (the return from
  the GHEX bore field); N1 drain flush at the envelope bottom (50 datum); N2
  vent flush at the envelope top (800 datum is the box top). N4 is the power
  terminal (cable schedule X-ELS-06, AQS-ELEC-010): electrical, not piped -
  drawn as a DN15 stand-in penetration flush at the envelope top, bore not
  calculated (plan W4). The schedule rating column carried verbatim as text.
- Route hold: the node class is blank - no AQS-PLAN-006 section 4 class;
  acceptance A-core with the route hold named (W12), the
  AFTERBURNER_FLUE/REE_RECOVER precedent.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("GEO_HP_CLOSED_LOOP")   # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}                                # the node design block

T_PLINTH = 20.0
POST = 40.0                                                # hold-down/guard frame section
LOOP_DN = "DN32"                                           # node design DN 32
HDR_Z0, HDR_Z1 = 320.0, 380.0                              # supply/return header lines
HDR_X0, HDR_X1 = 120.0, 620.0
BUF_R, BUF_H = 110.0, 300.0                                # loop buffer manifold vessel
PUMP = (640.0, 170.0, T_PLINTH, 240.0, 260.0, 460.0)                 # circulator envelope (125.7 W node)
TIE_X = (200.0, 480.0)                                     # tie-in stub stations
RHO_HDPE = materials.density("HDPE")
RHO_CS = materials.density("CS")

assert L == 1000.0 and W == 600.0 and H == 800.0, "GEO_HP_CLOSED_LOOP node envelope changed"
CY = W / 2
assert TIE_X[1] < HDR_X1, "tie stubs on the header runs"
assert PUMP[0] + PUMP[2] <= L - POST, "pump envelope clears the frame"


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

# ---------------------------------------------------------------- loop buffer manifold vessel
parts["buffer_vessel"] = vtube(2 * BUF_R, 200.0, CY, T_PLINTH, T_PLINTH + BUF_H)

# ---------------------------------------------------------------- supply/return header runs (DN32)
h0 = dn_pipe(LOOP_DN, HDR_X1 - HDR_X0).rotate((0, 0, 0), (0, 1, 0), 90).translate(
    (HDR_X0, CY - 70.0, HDR_Z0))
h1 = dn_pipe(LOOP_DN, HDR_X1 - HDR_X0).rotate((0, 0, 0), (0, 1, 0), 90).translate(
    (HDR_X0, CY + 70.0, HDR_Z1))
parts["headers"] = h0.union(h1)

# ---------------------------------------------------------------- tie-in stubs (GHEX bore field / GEO_HP)
stubs = None
for tx, zz in ((TIE_X[0], HDR_Z1), (TIE_X[1], HDR_Z0)):
    s = dn_pipe(LOOP_DN, zz + 40.0).translate((tx, CY + 70.0, 0.0))
    stubs = s if stubs is None else stubs.union(s)
parts["tie_stubs"] = stubs

# ---------------------------------------------------------------- circulator envelope
parts["pump_env"] = box(*PUMP)

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
    elif r["face"] == "top" and dnl == "cable":           # N4: power terminal (X-ELS-06)
        s = nozzles.stub("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (470.0, CY), (L, W, H))
        note = ("power terminal (cable schedule X-ELS-06): an electrical drop, not "
                "piped - drawn as a DN15 stand-in penetration flush at the envelope "
                "top beside the vent, bore not calculated (plan W4)")
    elif r["face"] == "top":                              # N2: 800 datum is the box top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, CY), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], CY), (L, W, H))
        if tag == "N3":
            note += "; the loop return from the GHEX bore field"
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose" if dnl in Hose else "stub", "dn": dnl, "face": face, "height_mm": h,
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
        "type": "closed source-loop distribution skid per the node design "
                "block: the loop between the GHEX bore field and the heat-pump "
                f"evaporators (GEO_HP) - DN32 HDPE supply/return header runs, "
                f"the loop buffer manifold vessel (OD {2 * BUF_R:g} x {BUF_H:g}, "
                "the seed's 'loop vessel'; study, W12), the circulator envelope "
                "(pump_W 125.7, node - purchased per plan rule 6), and the tie "
                "stubs (below-grade interface to the bore field; skid-side tie "
                "toward GEO_HP)",
        "node_class": "blank on the node - the tracker row says what is known; "
                      "route hold carried by name (no AQS-PLAN-006 section 4 "
                      "class; AFTERBURNER_FLUE/REE_RECOVER precedent)",
        "loop": {"dn": LOOP_DN, "design_case_kW_th": DS.get("design_case_kW_th"),
                 "flow_kg_s": DS.get("flow_kg_s"), "dT_K": DS.get("dT_K"),
                 "head_m": DS.get("head_m"), "pump_W": DS.get("pump_W"),
                 "fluid": "25 % propylene glycol (freeze protection to -10 C, "
                          "node material)",
                 "standby": "the S43 class edge runs at 0 kW idle standby on "
                            "the graph (node design duty text)"},
        "buried_scope": "the buried ground array is the GHEX/site lane's - the "
                        "tie stubs are the interface indication, the below-"
                        "grade runs are named, not drawn (hold, WORK_ORDER W12)",
        "purchased": "circulator envelope (AQS-DUTY-076 source-loop circulator, "
                     "125.7 W node stamp; node continuous 0.1257 kW) - "
                     "purchased per plan rule 6",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04); 8 slab anchors (fasteners.csv)",
        "material": "HDPE DR-11 buried; 25 % propylene glycol (node material); "
                    "skid frame painted A500",
        "ca_mm": 0.0,
        "study_dims": "skid header stations, buffer vessel and pump envelope "
                      "are study values (hold, WORK_ORDER W12)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (duty "
                    "section 4: atmospheric joints are hose; DN copied from the "
                    "edge, not recalculated; rows read 'Bore not calculated. "
                    "Rating hose, atmospheric'); N3 geothermal loop fluid in on "
                    "-Y at z 160 (the return from the GHEX bore field); drain "
                    "flush at the envelope bottom (50 datum); vent flush at the "
                    "envelope top (800 datum is the box top); no flange (W4 110 "
                    "% rule); the schedule rating column carried verbatim as "
                    "text; the N4 power terminal (cable schedule X-ELS-06) is "
                    "electrical, not piped: drawn as a DN15 stand-in at the "
                    "envelope top, bore not calculated",
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
    ["3", f"Loop buffer manifold vessel OD {2 * BUF_R:g} x {BUF_H:g} (the seed's "
           "'loop vessel'; study)", 1, "HDPE", mass["buffer_vessel"], "make",
     "seed note 'loop vessel beside GHEX'; vessel size is a study value (hold, "
     "WORK_ORDER W12)"],
    ["4", f"DN32 HDPE supply/return header runs (x {HDR_X0:g}..{HDR_X1:g})", 2,
     "HDPE DR-11 (node material)", mass["headers"], "make",
     "node design DN 32; skid stations are study values (hold, WORK_ORDER W12)"],
    ["5", "Tie-in stubs, 2 off: below-grade interface to the GHEX bore field "
           "and the skid-side tie toward GEO_HP", 2, "HDPE DR-11",
     mass["tie_stubs"], "make",
     "interface indications - the buried ground array is the GHEX/site lane's "
     "(hold, WORK_ORDER W12)"],
    ["6", "Circulator envelope (AQS-DUTY-076 source-loop circulator, 125.7 W "
           "node stamp)", 1, "purchased pump (envelope)", mass["pump_env"], "buy",
     "purchased per plan rule 6, rating from the node; mass a table-density "
     "placeholder until the maker TDS quotes (W12)"],
    ["7", "Nozzle set per docs-authority/nozzles/GEO_HP_CLOSED_LOOP.csv: 2 hose "
           "barbs (DN15), 1 drain stub, 1 power-terminal penetration (DN15 "
           "stand-in) at the top", len(schedule), "HDPE", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim (bores not calculated, hose, "
     "atmospheric); atmospheric hose per duty section 4; the N4 power terminal "
     "(cable schedule X-ELS-06) is electrical, not piped"],
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
    "buffer_vessel": {"od_mm": 2 * BUF_R, "h_mm": BUF_H},
    "headers": {"dn": LOOP_DN, "x_mm": [HDR_X0, HDR_X1], "z_mm": [HDR_Z0, HDR_Z1]},
    "tie_stubs_x_mm": TIE_X,
    "pump_env_mm": PUMP,
}
p["design"] = dict(DS)
p["design"].update({
    "service": "GEO_HP_CLOSED_LOOP: the closed source loop between the GHEX "
               "bore field and the heat-pump evaporators - the S43 class edge "
               "at 0 kW idle standby, design case 3.0 kW th (duty sections 1 "
               "and 4)",
    "material": "HDPE DR-11 buried; 25 % propylene glycol (freeze protection "
                "to -10 C; node material)",
    "ca_mm": 0.0,
    "material_basis": "node material row; CA does not apply to the HDPE "
                      "(AQS-STD-001)",
    "node_class": "blank on the node (the tracker row says what is known); "
                  "route hold named (W12)",
    "purchased": "circulator envelope (AQS-DUTY-076, 125.7 W node stamp)",
    "buried_scope": "the buried ground array is the GHEX/site lane's; the tie "
                    "stubs are interface indications",
})
p["layout"] = {
    "frame": "origin at the envelope corner; buffer vessel at x 200 on the skid "
             "centreline; header runs x 120..620 at z 320/380 +/- 70; tie stubs "
             "at x 200/480; circulator envelope x 640..880",
    "below_grade": "the tie stubs run to the box floor and below grade toward "
                   "the GHEX bore field - interface indication only",
    "supports": "plinth + hold-down frame + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; N3 on -Y at z "
                     "160 (the return from the bore field), drain at x 430, "
                     "vent at x 570; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
