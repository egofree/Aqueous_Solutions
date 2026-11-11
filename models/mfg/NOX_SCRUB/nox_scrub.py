"""NOX_SCRUB manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared
reader (models/mfg/lib/graph_node.py); the params.json write-back beside it carries
only the builder-owned envelope, design and layout blocks.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 4103 mm, node size_mm set by flow_graph/param/house_scrubbers.py
  (X-PAR-03). Column design on the node: D 200, packed height 2303, column H 3803,
  duty "flue, leach off-gas and nitric vents", PP rings, PP mesh demister. The build
  fills the envelope: 20 mm plinth at the base, shell to 4063 with a 20 mm top head,
  the DN15 vent riser closing the 4103 top.
- Internals (A-COL): packing support grid, two packed beds of the 2303 mm packing
  divided by a redistribution disc, a liquid distributor above the bed, and a demister
  pad below the top head - all drawn as their envelope solids (the rings and the mesh
  are not modelled piece-wise); the node internals row is none, so the tracker records
  no internal solid (holds, W12). Bed elevations are the layout choice (the design
  gives packed height only). The plinth and the top-head vent riser close the envelope.
- Material: CPVC shell, sump and packing support per duty section 3 (AQS-STD-002
  M1/M2/M5; leach off-gas arrives at up to 85 C); packing and demister PP (polymer).
  The node design block names PP-H - duty section 3 governs wetted materials (plan
  rule 5); the disagreement is a hold (W12). Wall 6 mm is a study value (hold).
- Nozzles: all 15 rows of docs-authority/nozzles/NOX_SCRUB.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs at the
  envelope faces with extension spools crossing to the shell (the column stands off
  the envelope face), the schedule rating column carried verbatim as text, no flange
  (W4 110 % rule). N11/N12 carry no schedule height: drawn at z 3400 in the gas
  space above the distributor (layout choice, hold). N10's 2000 datum predates the
  sized column and is drawn flush at the top head (hold).
- A-COL: packing height, support, distributor and demister are solids; no stage or
  HTU count is claimed anywhere (packed column; dP 1171 Pa is the node design figure).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402

GN = graph_node.graph_node("NOX_SCRUB")       # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 4103, X-PAR-03
D = float(GN.design["D_mm"])        # node design block D_mm (house_scrubbers.py, X-PAR-03)
REV = P["graph_revision"]

T_SHELL = 6.0                    # study wall - no authority states one (WORK_ORDER W12)
T_PLINTH = 20.0                  # base plinth / top hold-down frame, envelope idiom
Z_SKIRT0, Z_SHELL0 = 12.0, 150.0                            # skirt laps the plinth and the shell
Z_SHELL1 = H - 2 * T_PLINTH                                 # shell top 4063
D_IN = D - 2 * T_SHELL                                      # inner diameter 188
Z_SUP = 700.0                                               # packing support grid
PACKED = 2303.0                  # node design block packed_mm (cited; carried in params.design)
BED = (PACKED - 15.0) / 2                                   # two beds, redistribution disc between
Z_BED0, Z_RED, Z_BED1 = Z_SUP + 15.0, Z_SUP + 15.0 + BED, Z_SUP + 15.0 + PACKED + 15.0
Z_DIST = Z_BED1 + 27.0                                      # liquid distributor plate
Z_DEM = Z_SHELL1 - 20.0 - 40.0                              # demister pad below the top head
CA = materials.ca_for("CPVC")
RHO = {"CPVC": materials.density("CPVC"), "PP": materials.density("PP")}

CX = L / 2


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def cyl(r_out, r_in, z0, z1):
    return (cq.Workplane("XY", origin=(CX, W / 2, z0))
            .circle(r_out).circle(max(r_in, 0.1)).extrude(z1 - z0))


parts = {}

# ---------------------------------------------------------------- plinth, skirt, shell, heads
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
skirt = cyl(D / 2 + 20, D / 2 - 2, Z_SKIRT0, Z_SHELL0)      # laps the plinth and the shell
parts["skirt"] = skirt
shell = cyl(D / 2, D_IN / 2, Z_SHELL0, Z_SHELL1)
shell = shell.union(cyl(D / 2, 0.1, Z_SHELL1, Z_SHELL1 + 20))            # top head plate
parts["shell"] = shell

# ---------------------------------------------------------------- internals (A-COL)
support = cyl(D_IN / 2, 0.1, Z_SUP, Z_SUP + 15)             # packing support grid (envelope)
parts["support"] = support
bed1 = cyl(D_IN / 2, 0.1, Z_BED0, Z_RED)
redist = cyl(D_IN / 2, 0.1, Z_RED, Z_RED + 15)              # redistribution disc
bed2 = cyl(D_IN / 2, 0.1, Z_RED + 15, Z_BED1)
parts["packing"] = bed1.union(redist).union(bed2)
parts["distributor"] = cyl(D_IN / 2, 0.1, Z_DIST, Z_DIST + 15)
parts["demister"] = cyl(D_IN / 2, 0.1, Z_DEM, Z_DEM + 40)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
Z_BLANK = 3400.0                 # gas space above the distributor (N11/N12, no schedule datum)


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


def od_of(r):
    """Hardware OD for a piped row: lib-table DN rows at the table OD. Non-piped
    rows are carried verbatim and never drawn."""
    return dn.pipe_od(r["size"]) if r["size"] in dn.PIPE else dn.pipe_od("DN15")


def drawn_height(r):
    h = r["height_mm"]
    return Z_BLANK if h is None else float(h)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y") and r["size"] in dn.PIPE:
        groups.setdefault((face, drawn_height(r)), []).append(r)

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

noz, drawn, n_drawn = None, {}, 0
for r in schedule:
    tag, dnl, h_raw = r["tag"], r["size"], r["height_mm"]
    h = drawn_height(r)
    face = FACE_OF.get(r["face"], r["face"])
    if dnl not in dn.PIPE:
        # non-piped row: the power terminal (cable schedule X-ELS-06) is electrical,
        # not piped - carried verbatim, not drawn (no STEP/BOM/geometry change)
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"], "height_mm": h_raw,
                      "schedule_rating": r["rating"], "service": r["service"],
                      "note": "power terminal (cable schedule X-ELS-06, AQS-ELEC-010): "
                              "electrical, not piped - carried verbatim, not drawn"}
        continue
    n_drawn += 1
    od = od_of(r)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N9: boss at the skirt base
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 105.0, W / 2), (L, W, H))
        note = "drain boss laps the skirt ring at the plinth, tip at the 50 datum"
    elif r["face"] == "top":                              # N10: 2000 datum predates the column
        # vent riser on the top head: laps the head plate and closes the envelope at 4103
        s = nozzles.stub(dnl, 60.0)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 50.0, W / 2), (L, W, H))
        note = ("vent riser on the top head to the 4103 envelope top; schedule datum "
                "2000 mm predates the sized column - named hold, WORK_ORDER W12")
    else:
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        # the shell stands (600-200)/2 = 200 off the envelope face: the barb sits flush
        # at the face and an extension spool crosses the air gap and the shell wall.
        # The spool length follows the port's own ray: the shell surface at along-face
        # offset dx stands at W/2 - sqrt(R^2 - dx^2) from the face, so a fixed-length
        # spool would stop short of the curved wall at the ends of a packed row.
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        dx = abs(layout_x[tag] - CX)
        r_shell = min(math.sqrt(max(D / 2 ** 2 - dx ** 2, 4.0)), D / 2)
        # the spool runs from the barb end to 10 mm past the inner wall along the
        # port's own ray (the XZ workplane extrudes -normal = -Y for +len)
        if face == "-Y":
            y0 = Hose[dnl]
            spool_len = max((W / 2 - r_shell + T_SHELL + 10.0) - y0, 12.0)
            spool = (cq.Workplane("XZ", origin=(layout_x[tag], y0, h))
                     .circle(od / 2).extrude(-spool_len))
        else:
            y0 = W - Hose[dnl]
            spool_len = max(y0 - (W / 2 + r_shell + T_SHELL + 10.0), 12.0)
            spool = (cq.Workplane("XZ", origin=(layout_x[tag], y0, h))
                     .circle(od / 2).extrude(spool_len))
        s = s.union(spool)
        if h_raw is None:
            note += (f"; no schedule height: drawn at z {Z_BLANK:g} in the gas space "
                     "above the distributor (layout choice) - WORK_ORDER W12")
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h_raw,
                  "drawn_height_mm": round(h, 1) if face in ("-Y", "+Y")
                  else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="NOX_SCRUB")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / "nox_scrub.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / "nox_scrub.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "NOX_SCRUB.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "nox_scrub.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * (RHO["PP"] if k in ("packing", "demister")
                                     else RHO["CPVC"]) / 1e9, 1) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "node size_mm set by flow_graph/param/house_scrubbers.py (X-PAR-03)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "column": {"D_mm": D, "shell_z_mm": [Z_SHELL0, Z_SHELL1], "wall_mm": T_SHELL,
               "wall_basis": "study value - no authority states a thickness (WORK_ORDER W12)",
               "packed_mm": PACKED, "beds": 2,
               "beds_z_mm": [[Z_BED0, Z_RED], [Z_RED + 15, Z_BED1]],
               "support_z_mm": [Z_SUP, Z_SUP + 15],
               "redistribution_z_mm": [Z_RED, Z_RED + 15],
               "distributor_z_mm": [Z_DIST, Z_DIST + 15],
               "demister_z_mm": [Z_DEM, Z_DEM + 40],
               "note": "beds, support, distributor and demister drawn as their envelope "
               "solids (A-COL); ring count and mesh not modelled piece-wise; bed "
               "elevations are the layout choice - the design gives packed height only"},
    "material": {"class": "CPVC shell / PP packing and demister", "ca_mm": CA,
                 "basis": "duty section 3: CPVC shell, sump and packing support "
                 "(AQS-STD-002 M1/M2/M5, 85 C feed); packing polymer. The node design "
                 "block names PP-H - duty section 3 governs wetted materials (plan "
                 "rule 5); hold, W12"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces with extension "
    "spools crossing to the shell (the column stands off the face); the schedule "
    "rating column (Class 150 / hose) is carried verbatim as text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"CPVC column shell OD {D:g}, wall {T_SHELL:g} mm, z {Z_SHELL0:g}..{Z_SHELL1:g}, "
          f"with top head, skirt and 600 x 600 plinth", 1, "CPVC pipe/plate",
     round(mass["shell"] + mass["skirt"] + mass["plinth"], 1), "make",
     "node envelope (X-PAR-03) and design D 200; wall a study value (WORK_ORDER W12); "
     "CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"Packing support grid, OD {D_IN:g} x 15 at z {Z_SUP:g}", 1, "CPVC",
     mass["support"], "make", "A-COL support solid (envelope); layout elevation"],
    ["3", f"Pall-ring bed, {PACKED:g} mm of PP rings in two beds with a redistribution "
          f"disc, drawn as its envelope OD {D_IN:g}", 1, "PP (in-house cut rings)",
     mass["packing"], "make",
     "node design packed_mm 2303, PP rings (duty section 3); ring count not modelled; "
     "bed split and elevations are the layout choice"],
    ["4", f"Liquid distributor plate, OD {D_IN:g} x 15 at z {Z_DIST:g}", 1, "CPVC",
     mass["distributor"], "make", "A-COL distributor solid (envelope); recirc feed "
     "0.4775 m3/h per the node design; layout elevation"],
    ["5", f"PP mesh demister pad, OD {D_IN:g} x 40 below the top head", 1, "PP mesh",
     mass["demister"], "make", "A-COL demister solid (envelope); duty section 3 PP mesh"],
    ["6", "Nozzle set per docs-authority/nozzles/NOX_SCRUB.csv: 13 hose barbs "
          "(DN15/DN25/DN50) on extension spools, 1 drain boss, 1 vent at the top head",
     n_drawn, "CPVC", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim (N11/N12 carry no datum: drawn at z 3400, "
     "hold); atmospheric hose per duty section 4; barb profile a study proportion"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CPVC"), 4,
     "plinth to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
    [None, "M12 bolt + nut, PP-flanged joint", fasteners.grade_for("CPVC"), 16,
     "top head to shell service joint (4 bolt-holes assumed at DN50 flange pitch, "
     "count from the model geometry)",
     "polymer joint to the supplier rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "node size_mm set by flow_graph/param/house_scrubbers.py (X-PAR-03)",
    "column": {"D_mm": D, "shell_z_mm": [Z_SHELL0, Z_SHELL1]},
}
p["design"] = {
    "service": "flue, leach off-gas and nitric vents, atmospheric (duty sections 4 and 6)",
    "wall_mm": T_SHELL, "wall_basis": "study value", "ca_mm": CA,
    "packed_mm": PACKED, "beds_z_mm": [[Z_BED0, Z_RED], [Z_RED + 15, Z_BED1]],
    "dP_Pa": 1171.034, "recirc_m3_h": 0.4775,
    "material_node_PP_H_vs_duty_CPVC": "hold, WORK_ORDER W12",
}
p["layout"] = {
    "frame": "origin at the envelope corner; column axis at x 300, y 300, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row per "
                     "face/height group at the envelope face, 8 mm clear at the bore; "
                     "extension spools cross the air gap and the shell wall",
    "vent_drain": "N10 flush at the top head (2000 datum predates the column); N9 drain "
                  "boss lapping the skirt ring at the plinth",
    "internals": "support grid, two beds + redistribution disc, distributor, demister - "
                 "envelope solids at the recorded layout elevations",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}))
