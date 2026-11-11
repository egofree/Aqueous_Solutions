"""C29_RECYCLE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 5, A-PIPE).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the line-list
authorities the A-PIPE acceptance names: the unit's edges in
`flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
(AQS-PIP-004, the DN and class authority). It writes the unit line list
`line_list.csv` and rebuilds every solid.

Placement frame: x along the 1000 mm box, y across the 600 mm depth, z up, origin at
the envelope corner. Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm, whose size_note records it as the
  study default envelope box read back from the cad/stl registry ("design sizing per
  the duty sheet follows"). The duty section 4 prose block states "Size 2000 x 60 x 60
  mm" with its L1/L2 rows at height 30: an older study frame. The node governs for the
  W2 envelope; the older figures are named (holds, W12). The build sits inside the
  node box and under-fills it (a DN15 line in a study box); nothing is resized.
- Spool per the schedule and the issued lines: DN15 (the AQS-PIP-004 line DN for
  both C29_RECYCLE and C29_TO_PYRO), wall on the lib/dn Sch 40 table (the schedule
  is not stated on the node - WORK_ORDER W12), carbon steel per duty section 3
  (hydrocarbon, no aqueous chloride; line class M2). CA 1.5 mm per the AQS-STD-001
  hydrocarbon rule, carried in the procurement basis; the drawn wall is the table
  value.
- Geometry: one x-run at the schedule inlet datum (z 160) along the box at the depth
  centre (y 300), the N1 inlet branch rising... entering from the -Y face at x 500
  (the duty section 4 L1/L2 rows sit at the mid-run x 3000 of the old 2000 frame -
  the mid-run choice carries over, layout choice W12), and the N2 outlet leaving the
  +Y face at the schedule outlet datum (z 600) through a bend riser at x 500. All
  joints are set-in welds of the same DN15 tube (the spool idiom of the accepted
  header lane); bores stay open, nothing traps.
- Supports: a trough plinth (1000 x 60 x 20) under the run zone with two saddle
  stands (30 x 30 posts) carrying the run at its 160 datum, and 4 M10 slab anchors.
- Nozzles: all 4 rows of docs-authority/nozzles/C29_RECYCLE.csv drawn at tag, face,
  height and bore as atmospheric tube stubs (duty section 4: hose, atmospheric; the
  connecting line makes the joint at the face). The schedule datums draw as issued:
  the 160 inlet and 600 outlet fit the 800 box; the drain passes to the envelope
  bottom (50 datum); the vent riser reaches the envelope top (800 datum = the box
  top). The rating column (Class 150) is carried verbatim as text, no flange (W4
  110 % rule - no process pressure stated).
- A-PIPE line list: `line_list.csv` is generated here from the graph edges and the
  issued AQS-PIP-004 rows (tag, from, to, DN, class, service, rating). No new edge.
"""
import csv, json, math, pathlib, re, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("C29_RECYCLE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DN_MAIN = "DN15"                                           # AQS-PIP-004 line DN, both lines
OD_MAIN, WALL_MAIN = dn.pipe_od(DN_MAIN), dn.pipe_wall(DN_MAIN, 40)
ID_MAIN = round(OD_MAIN - 2 * WALL_MAIN, 2)
Y_C = W / 2                                                # run depth centre 300
Z_RUN = 160.0                                              # schedule inlet datum
Z_OUT = 600.0                                              # schedule outlet datum
X_JOINT = 500.0                                            # mid-run branch x (the old L1/L2 frame)
T_PLINTH = 20.0                                            # trough mount, HDR idiom
MAT_KEY = "CS"                                             # duty section 3: carbon steel
RHO = materials.density(MAT_KEY)
CA_PIPE = materials.ca_for(MAT_KEY, "hydrocarbon")         # 1.5, AQS-STD-001 rule

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert DN_MAIN == "DN15", "C29_RECYCLE line DN changed on AQS-PIP-004"


def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + stands
plinth = cq.Workplane("XY").box(L, 60.0, T_PLINTH, centered=False).translate((0, Y_C - 30.0, 0))
parts["plinth"] = plinth
stands = None
for xs in (250.0, 750.0):
    s = cq.Workplane("XY").box(30.0, 30.0, Z_RUN - OD_MAIN / 2 - T_PLINTH + 2.0,
                               centered=False).translate((xs - 15.0, Y_C - 15.0, T_PLINTH - 2.0))
    saddle = cq.Workplane("XY").box(60.0, 44.0, 8.7, centered=False).translate(
        (xs - 30.0, Y_C - 22.0, Z_RUN - OD_MAIN / 2 - 6.0))     # laps into the pipe wall
    s = s.union(saddle)
    stands = s if stands is None else stands.union(s)
parts["stands"] = stands

# ---------------------------------------------------------------- spool: x-run, bend riser, outlet branch
run = (cq.Workplane("YZ", origin=(0, Y_C, Z_RUN))
       .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(L))
parts["run"] = run
riser = (cq.Workplane("XY", origin=(X_JOINT, Y_C, Z_RUN))
         .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(Z_OUT - Z_RUN))
parts["riser"] = riser
out_branch = (tube(DN_MAIN, W - Y_C)
              .rotate((0, 0, 0), (1, 0, 0), -90)          # +Z maps to +Y
              .translate((X_JOINT, Y_C, Z_OUT)))
parts["out_branch"] = out_branch
in_branch = (cq.Workplane("XZ", origin=(X_JOINT, Y_C, Z_RUN))
             .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(Y_C))   # XZ normal -Y: y 300 -> 0
parts["in_branch"] = in_branch

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0                       # past the bore wall, so every union fuses

schedule = P["nozzles"]
noz, drawn = None, {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    is_dn = dnl.startswith("DN")
    od_s = dn.pipe_od(dnl) if is_dn else dn.pipe_od("DN15")
    if face0 == "bottom":               # drain: boss under the run, flush at the envelope bottom
        stub = tube(dnl if is_dn else "DN15", Z_RUN + STUB_PIERCE)
        s = stub.translate((300.0, Y_C, 0.0))
        note = "drain boss under the run, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, 300.0
    elif face0 == "top":                # vent: riser off the run, flush at the envelope top
        stub = tube(dnl if is_dn else "DN15", H - Z_RUN + STUB_PIERCE)
        s = stub.translate((700.0, Y_C, Z_RUN - STUB_PIERCE))
        note = "vent riser off the run, flush at the envelope top (schedule datum 800 = the box top)"
        z_d, x_d = H, 700.0
    elif face0 == "inlet":              # N1: -Y face at the mid-run joint, 160 datum
        stub = (tube(dnl if is_dn else "DN15", Y_C + STUB_PIERCE)
                .rotate((0, 0, 0), (1, 0, 0), -90)      # +Z maps to +Y
                .translate((X_JOINT, 0.0, float(r["height_mm"]))))
        s = stub
        note = ("schedule datum 160 drawn as issued; branch stub from the -Y face, "
                "set-in weld at the mid-run joint (duty section 4: hose, atmospheric)")
        z_d, x_d = float(r["height_mm"]), X_JOINT
    else:                               # N2: the outlet branch is the spool itself
        s = parts["out_branch"]
        note = ("schedule datum 600 drawn as issued; the +Y face branch of the bend "
                "riser is the outlet hardware (duty section 4: hose, atmospheric)")
        z_d, x_d = Z_OUT, X_JOINT
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face0,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
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

RATING_PIPED = ("atmospheric tube/hose joint at the face (duty section 4); pipe "
                "class per AQS-PIP-003")
with open(HERE / "line_list.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["line", "from", "to", "dn", "class", "service", "rating", "note"])
    w.writerow(["MAIN", "spool start", "spool end", DN_MAIN, "-", "C29 heavy cut",
                "atmospheric; no flange class (duty section 4)",
                "recycle-line spool per the unit duty (node design: DN15 per the "
                "issued lines); modeled as the in-envelope run of this unit's "
                "1000 x 600 x 800 study box; material per duty section 3"])
    for r in sorted(ll_rows, key=lambda r: r["line"]):
        if re.fullmatch(r"DN\d+", r["dn"]):
            rating, note = RATING_PIPED, ""
        elif r["dn"] == "cable":
            rating, note = "-", "not piped: heat/electrical cable (cable schedule X-ELS-06)"
        elif r["dn"] == "solids":
            rating, note = "-", "not piped: solids transfer (conveyor, bin or hand)"
        else:
            rating, note = "bore not calculated", "no DN issued on the line yet"
        w.writerow([r["line"], r["frm"], r["to"], r["dn"], r["cls"], r["service"], rating, note])

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
misfit = None if inside else (f"bbox {dims} against size_mm {[L, W, H]}; nothing resized "
                              "(plan rule 3)")
mass = {k: round(v.val().Volume() * (RHO if k != "plinth" and k != "stands" else RHO) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "misfit": misfit,
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "spool": {
        "type": "one x-run at the schedule inlet datum (z 160) on a trough plinth with "
                "two saddle stands; mid-run inlet branch from the -Y face; bend riser "
                "to the outlet datum (z 600) leaving the +Y face",
        "dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN,
        "wall_basis": "lib/dn Sch 40 table (ASME B36.10M); the node states no schedule "
                      "(WORK_ORDER W12)",
        "id_mm": ID_MAIN,
        "run_basis": "the routed run (2.4 m + 6.8 m per AQS-PIP-004) stays in the "
                     "line-list route lengths; the model draws the in-envelope run of "
                     "the node study box",
        "material": P.get("material"),
        "ca_mm": CA_PIPE,
        "ca_basis": "AQS-STD-001 hydrocarbon rule on carbon steel, carried in the "
                    "procurement basis; the drawn wall is the Sch 40 table value",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric tube stubs (duty section 4: hose, atmospheric; the "
                    "connecting line makes the joint at the face; the W4 110 percent "
                    "rule draws no flange where no process pressure is stated); "
                    "schedule rating column (Class 150) carried verbatim as text; "
                    "datums draw as issued - the 160 and 600 datums fit the 800 box, "
                    "the drain passes to the envelope bottom and the vent riser "
                    "reaches the envelope top",
    "line_list": {
        "csv": f"models/mfg/{UNIT}/line_list.csv",
        "source": "unit edges in flow_graph/plant_flow_graph.json + docs-authority/"
                  "LINE_LIST.md (AQS-PIP-004, DN and class authority)",
        "edges": len(edges), "rows": len(ll_rows) + 1,
        "missing_line_rows": missing, "rows_without_edge": extra,
        "no_new_edge": True,
    },
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Spool {DN_MAIN} OD {OD_MAIN:g} x wall {WALL_MAIN:g} (Sch 40 table): x-run "
          f"{L:g} mm, inlet branch, bend riser to z {Z_OUT:g}, +Y outlet branch; "
          "bores open, joints set-in welds", 1,
     "carbon steel tube (duty section 3)", round(mass["run"] + mass["riser"]
                                                 + mass["out_branch"] + mass["in_branch"]
                                                 + mass["nozzles"], 2), "make",
     "AQS-PIP-004 line DN15 (both C29 lines); schedule not stated on the node - Sch "
     "40 table drawn (hold, WORK_ORDER W12); CA 1.5 mm hydrocarbon rule carried in "
     "the procurement basis (AQS-STD-001)"],
    ["2", f"Trough plinth {L:g} x 60 x {T_PLINTH:g} with two saddle stands (AQS-MOD-002 "
          "dry service class)", 1, "carbon steel (ASTM A500)", round(mass["plinth"] + mass["stands"], 2),
     "make",
     "support scheme carries the HDR_CO2 idiom; the run sits at the schedule 160 "
     "datum on the stands; the dry oil-line service sees no aqueous chloride, so the "
     "1.5 mm hydrocarbon-rule allowance is not applied to the support steel "
     "(duty section 3)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per metre of spool (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "pipe": {"dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN,
             "xy_mm": [None, Y_C], "run_z_mm": Z_RUN},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "dn_label": DN_MAIN, "wall_mm": WALL_MAIN,
    "wall_basis": "lib/dn Sch 40 table; schedule not stated on the node (WORK_ORDER W12)",
    "mat": "carbon steel per duty section 3 (hydrocarbon, line class M2); CA 1.5 mm "
           "carried in the procurement basis (AQS-STD-001)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; x-run at depth centre y 300, z 160 "
             "(schedule inlet datum); inlet branch at the mid-run x 500; bend riser "
             "to z 600 (schedule outlet datum) leaving the +Y face; trough plinth "
             "under the run zone with two saddle stands",
    "supports": "trough plinth + 2 saddle stands + 4 slab anchors - the HDR_CO2 "
                "idiom at the schedule datum height (layout choice, WORK_ORDER W12)",
    "nozzle_spread": "the schedule gives face and height; N1 at the mid-run x 500 "
                     "(the old L1/L2 mid-run frame), N2 the bend-riser branch, drain "
                     "boss under the run at x 300, vent riser at x 700; per-tag "
                     "positions in check.nozzles_drawn",
    "line_list": "models/mfg/C29_RECYCLE/line_list.csv generated from the graph edges "
                 "and AQS-PIP-004; no new edge",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "missing": missing, "extra": extra}))
