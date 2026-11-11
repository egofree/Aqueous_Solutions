"""GLASS_MILL manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 5, A-PIPE).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 800 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 800 x 600 x 800 mm, node size_mm ("issued envelope"). The build stays
  inside it exactly.
- Machine per the unit's own duty sheet and the ported AQS-MFG-001 form
  (`models/openscad/detail/mfg_mill.scad`: mill jar + media): a horizontal 316L jar
  mill - jar OD 350 x 500, wall 8 mm (study - no jar dimension on the node or duty,
  W12) with end heads and trunnion journals, riding in two roll-stand cradles on a
  20 mm plinth. The jar-full volume is reported against the duty section 2 seven-day
  charge 0.2577 m3; the media charge is not drawn - the node carries internals none
  (W12).
- Nozzles: all 6 rows of docs-authority/nozzles/GLASS_MILL.csv drawn at tag, face,
  height and bore as atmospheric hose barbs flush at the envelope faces (duty
  section 4). The N6 solids row (spent ceramic shell to the solids line) is a
  non-piped transfer: drawn DN15, bore not calculated (plan W4). Drain flush at the
  envelope bottom (50 datum is the schedule placeholder); vent flush at the envelope
  top (schedule datum 800 mm sits at the box top). The schedule rating column
  (Class 150) is carried verbatim as text; no flange is drawn because no process
  pressure is stated (plan W4 110 % rule).
- A-PIPE line list: `line_list.csv` is generated here from the unit's edges in
  `flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
  (AQS-PIP-004). No new edge.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("GLASS_MILL")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 800 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
JAR_OD, JAR_WALL, JAR_LEN = 350.0, 8.0, 500.0              # to the form; wall study (W12)
JAR_ID = JAR_OD - 2 * JAR_WALL
Y_C, Z_C = W / 2, 430.0                                    # jar axis
X0 = (L - JAR_LEN) / 2                                     # 150: jar centred along the run
ROLL_OD, ROLL_W = 70.0, 24.0                               # cradle rolls under the jar
CHARGE_M3 = 0.2577                                         # duty section 2, seven-day charge
MAT = "316L"                                               # duty section 3
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert JAR_OD <= W - 40.0 and JAR_LEN <= L - 200.0, "jar drawn to the envelope"
V_JAR_M3 = math.pi / 4 * JAR_ID ** 2 * JAR_LEN / 1e9


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- mill jar (the machine shell)
jar = (cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
       .circle(JAR_OD / 2).circle(JAR_ID / 2).extrude(JAR_LEN))
jar = jar.union(cq.Workplane("YZ", origin=(X0, Y_C, Z_C)).circle(JAR_OD / 2)
                .extrude(8.0))                             # -X end head
jar = jar.union(cq.Workplane("YZ", origin=(X0 + JAR_LEN - 8.0, Y_C, Z_C))
                .circle(JAR_OD / 2).extrude(8.0))          # +X end head
for sx in (X0 - 20.0, X0 + JAR_LEN + 20.0 - 40.0):         # trunnion journals at the ends
    jar = jar.union(cq.Workplane("YZ", origin=(sx, Y_C, Z_C))
                    .circle(20.0).extrude(40.0))
parts["jar"] = jar

# ---------------------------------------------------------------- roll stands (ported jar-mill cradle)
stand = None
for xs in (X0 + 70.0, X0 + JAR_LEN - 70.0):                # roll stations under the jar
    base = box(xs - 90.0, Y_C - 80.0, T_PLINTH, 180.0, 160.0, 16.0)
    rolls = None
    for ang in (-30.0, 30.0):                              # V-cradle rolls touching the jar
        rx = xs + (JAR_OD / 2 + ROLL_OD / 2 - 10.0) * math.sin(math.radians(ang))
        rz = Z_C - (JAR_OD / 2 + ROLL_OD / 2 - 10.0) * math.cos(math.radians(ang))
        r = (cq.Workplane("YZ", origin=(rx - ROLL_W / 2, 0, 0))
             .circle(ROLL_OD / 2).extrude(ROLL_W)
             .translate((0, Y_C, rz)))
        rolls = r if rolls is None else rolls.union(r)
    ped = box(xs - 120.0, Y_C - 80.0, T_PLINTH + 16.0, 240.0, 160.0,
              Z_C - (JAR_OD / 2 + ROLL_OD / 2 - 10.0) * math.cos(math.radians(30.0))
              + 10.0 - T_PLINTH - 16.0)
    # the cross-beam tops pierce the roll and jar surfaces: plane-to-curve tangent
    # contacts leave parts unfused (the GLASS_BURNOUT housing fix)
    s = base.union(ped).union(rolls)
    stand = s if stand is None else stand.union(s)
parts["stands"] = stand

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0}                        # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


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
    assert span <= L - 80.0, (face, z, span)
    x = L / 2 - span / 2
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
    if r["face"] == "bottom":                             # N4: drain flush at the envelope bottom
        s = nozzles.stub("DN15", 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N5: 800 datum sits at the box top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
        dnl_draw = dnl if dnl.startswith("DN") else "DN15"
        s = nozzles.hose_barb(hose_id(dnl_draw), Hose[dnl_draw], root_od=od)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
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
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- line list (A-PIPE)
ROOT = HERE.parents[2]
graph = json.loads((ROOT / "flow_graph" / "plant_flow_graph.json").read_text())
edges = [e for e in graph["edges"] if e.get("presence") == "present"
         and UNIT in (e["from_unit_id"], e["to_unit_id"])]
ll_rows = []
for line in (ROOT / "docs-authority" / "LINE_LIST.md").read_text().splitlines():
    if not line.startswith("| ") or line.startswith("| Line") or line.startswith("| ---"):
        continue
    c = [x.strip() for x in line.split("|")[1:-1]]
    if len(c) >= 6 and UNIT in (c[1], c[2]):
        ll_rows.append(dict(line=c[0], frm=c[1], to=c[2], dn=c[3], cls=c[4], service=c[5]))

edge_tags = sorted(e["stream_id"] for e in edges)
ll_tags = sorted(r["line"] for r in ll_rows)
missing = [t for t in edge_tags if t not in ll_tags]
extra = [t for t in ll_tags if t not in edge_tags]
study = {e["stream_id"] for e in graph["edges"]
         if UNIT in (e["from_unit_id"], e["to_unit_id"]) and e.get("presence") != "present"}

with open(HERE / "line_list.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["line", "from", "to", "dn", "class", "service", "rating", "note"])
    for r in sorted(ll_rows, key=lambda r: r["line"]):
        if r["dn"].startswith("DN") and r["dn"][2:].isdigit():
            rating, note = ("atmospheric tube/hose joint at the machine face (duty "
                            "section 4); pipe class per AQS-PIP-003"), ""
        elif r["dn"] == "cable":
            rating, note = "-", "not piped: heat/electrical cable (cable schedule X-ELS-06)"
        elif r["dn"] == "solids":
            rating, note = "-", "not piped: solids transfer (conveyor, bin or hand)"
        else:
            rating, note = "bore not calculated", "no DN issued on the line yet"
        if r["line"] in study:
            note = (note + "; " if note else "") + "graph edge present as study; drawn verbatim, no new edge"
        w.writerow([r["line"], r["frm"], r["to"], r["dn"], r["cls"], r["service"], rating, note])

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * (RHO if k != "plinth" and k != "stands"
                                     else materials.density("CS")) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "jar mill: horizontal 316L jar OD 350 x 500 with end heads and "
                "trunnion journals in two V-roll cradle stands on a 20 mm plinth "
                "(ported AQS-MFG-001 form mfg_mill.scad: jar + media)",
        "jar_od_mm": JAR_OD, "jar_len_mm": JAR_LEN, "wall_mm": JAR_WALL,
        "wall_basis": "study value; no authority states a jar wall (WORK_ORDER W12)",
        "v_full_m3": round(V_JAR_M3, 4),
        "charge_duty_m3": CHARGE_M3,
        "charge_note": f"duty section 2 seven-day charge {CHARGE_M3:g} m3; the jar "
                       f"holds {V_JAR_M3:.3f} m3 full - reported, nothing resized "
                       "(plan rule 3); the media charge is not drawn: the node "
                       "carries internals none (WORK_ORDER W12)",
        "drive": "jar drive not designed: no drive is named on the node or duty "
                 "(WORK_ORDER W12)",
        "material": MAT,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (duty section "
                    "4); the N6 solids row is a non-piped transfer drawn DN15, bore "
                    "not calculated (plan W4); the schedule rating column (Class 150) "
                    "is carried verbatim as text, no flange drawn (no process pressure "
                    "stated)",
    "line_list": {
        "csv": f"models/mfg/{UNIT}/line_list.csv",
        "source": "unit edges in flow_graph/plant_flow_graph.json + docs-authority/"
                  "LINE_LIST.md (AQS-PIP-004, DN and class authority)",
        "edges": len(edges), "rows": len(ll_rows),
        "missing_line_rows": missing, "rows_without_edge": extra,
        "no_new_edge": True,
    },
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Mill jar OD {JAR_OD:g} x {JAR_LEN:g}, wall {JAR_WALL:g} mm (study), with "
          "end heads and trunnion journals", 1, "316L (duty section 3)", mass["jar"],
     "make",
     "jar drawn to the ported AQS-MFG-001 form; no jar dimension on the node or duty "
     "(hold, WORK_ORDER W12); CA 0 mm (AQS-STD-001 316L rule); capacity report in "
     "check.machine"],
    ["2", "V-roll cradle stands, 2 off: 180 x 160 base, pedestal, two OD 70 rolls", 2,
     "carbon steel (ASTM A500)", mass["stands"], "make",
     "jar-mill cradle form (AQS-MOD-002 dry service class); roll fit is a study "
     "proportion, confirmed at fabrication (WORK_ORDER W12)"],
    ["3", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1,
     "carbon steel (ASTM A500)", mass["plinth"], "make",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["4", "Nozzle set per docs-authority/nozzles/GLASS_MILL.csv: 5 hose barbs "
          "(DN15/DN25), drain and vent flush at the envelope faces", len(schedule),
     "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; the N6 solids row drawn DN15, bore not "
     "calculated (plan W4); atmospheric hose per duty section 4; barb profile a "
     "study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per stand station (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M12 roll-shaft bolt + nut", fasteners.grade_for("CS"), 4,
     "cradle rolls to pedestal, 2 per stand (count from the model)",
     "8.8 on carbon steel; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "jar": {"od_mm": JAR_OD, "len_mm": JAR_LEN, "axis_mm": [None, Y_C, Z_C],
            "x0_mm": X0},
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "GLASS_MILL: rinsed cullet milled to the burnout feed, with the spent "
               "ceramic shell to the solids line and mill dust to the baghouse, "
               "atmospheric (duty sections 1, 4 and 6)",
    "material": MAT, "ca_mm": CA,
    "v_full_m3": round(V_JAR_M3, 4), "charge_duty_m3": CHARGE_M3,
    "charge_basis": "duty section 2 seven-day charge; capacity figure, not a "
                    "residence time",
}
p["layout"] = {
    "frame": "origin at the envelope corner; jar axis along +x at y 300, z 430, jar "
             "centred x 150..650; roll stations at x 220/580",
    "supports": "plinth + two V-roll cradle stands + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row "
                     "per face/height group at the envelope face, 8 mm clear at the "
                     "bore; drain at x 360, vent at x 440; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "v_full_m3": round(V_JAR_M3, 4), "missing": missing, "extra": extra}))
