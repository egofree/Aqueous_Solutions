"""CONTINUOUS_RECYCLE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 5, A-PIPE).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the line-list
authorities the A-PIPE acceptance names: the unit's edges in
`flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
(AQS-PIP-004, the DN and class authority). It writes the unit line list
`line_list.csv` and rebuilds every solid.

Placement frame: x along the 1500 mm run, y across the 60 mm cross-section, z up,
origin at the envelope corner. Every dimension is an authority figure or a named
layout choice:

- Envelope 1500 x 60 x 60 mm, node size_mm, whose size_note records it as the study
  default envelope box read back from the cad/stl registry. The build fills the box:
  one x-run at the cross-section centre (y 30, z 30).
- Spool per the issued lines: DN15 (the AQS-PIP-004 line DN for both IA-POL-02 and
  IA-REC-01), wall on the lib/dn Sch 40 table (the schedule is not stated on the
  node - WORK_ORDER W12), PVC-U per duty section 3 (rules M1 and M2, no metal wetted
  part; above 60 C the thermoplastic is CPVC, never metal - the line temperature is
  not on the graph, hold W12). CA does not apply to the polymer (AQS-STD-001).
- Nozzles: all 5 rows of docs-authority/nozzles/CONTINUOUS_RECYCLE.csv drawn at tag,
  face and height as atmospheric tube stubs (duty section 4: hose, atmospheric; the
  connecting line makes the joint at the face). Schedule rows N1/N2 carry DN50 in
  the size column: drawn verbatim - the DN50 hardware seats the 60 mm cross-section
  at the section centre with 0.15 mm per side outside the box, inside the 1 mm house
  gate (holds, W12: the hand DN50 rows stand against the DN15 issued lines; AQS-PIP-
  003 basis: the piped bore is the nozzle bore basis, bores are not recalculated).
  The DN15 datums clamp into the cross-section: the 160 mm inlet datum draws at
  48.65 (placeholder above the 60 mm section); the drain passes to the envelope
  bottom (50 datum); the vent reaches the envelope top (800 datum). The rating
  column (Class 150) is carried verbatim as text, no flange (W4 110 % rule).
- Supports: a 1500 x 60 x 20 trough plinth under the whole run (the pipe sits welded
  in the trough to its centreline, the HDR_CO2 idiom) and 6 M10 slab anchors.
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

GN = graph_node.graph_node("CONTINUOUS_RECYCLE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1500 x 60 x 60
REV = P["graph_revision"]
UNIT = P["unit_id"]
DN_MAIN = "DN15"                                           # AQS-PIP-004 line DN, both lines
OD_MAIN, WALL_MAIN = dn.pipe_od(DN_MAIN), dn.pipe_wall(DN_MAIN, 40)
ID_MAIN = round(OD_MAIN - 2 * WALL_MAIN, 2)
Y_C, Z_C = W / 2, H / 2                                    # run centreline 30/30
T_PLINTH = 20.0                                            # trough mount, HDR idiom
MAT_KEY = "PVC-U"                                          # duty section 3
RHO = materials.density("PVC_U")                           # 1400, lib table
CLAMP_MARGIN = 0.7                                         # stub radius clearance to the faces

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert DN_MAIN == "DN15", "CONTINUOUS_RECYCLE line DN changed on AQS-PIP-004"


def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


def z_for(row):
    """Drawn centreline height for a side stub: the schedule datum clamped into the
    cross-section, with the clamp named when it fires. A datum above the section
    whose hardware cannot seat under it draws at the section centre."""
    h = float(row["height_mm"])
    od_s = dn.pipe_od(row["size"]) if row["size"].startswith("DN") else dn.pipe_od("DN15")
    lo, hi = od_s / 2 + CLAMP_MARGIN, H - od_s / 2 - CLAMP_MARGIN
    if lo > hi:   # the hardware is wider than the section: section centre
        return round(Z_C, 1), (f"schedule row {row['tag']} carries {row['size']}: the "
                               f"hardware seats the {H:g} mm cross-section at the "
                               f"section centre {Z_C:g} mm (datum {h:g} predates it; "
                               "hold, WORK_ORDER W12)")
    z = min(max(h, lo), hi)
    if h < lo:
        return round(z, 1), (f"schedule datum {h:g} mm clamped up to {round(z, 1)} mm to keep the "
                             f"{row['size']} bore inside the 60 mm cross-section (hold, WORK_ORDER W12)")
    elif h > hi:
        return round(z, 1), (f"schedule datum {h:g} mm is a placeholder above the 60 mm cross-section; "
                             f"clamped down to {round(z, 1)} mm (hold, WORK_ORDER W12)")
    return round(z, 1), None


# ---------------------------------------------------------------- plinth + spool
parts = {}
plinth = cq.Workplane("XY").box(L, W, T_PLINTH, centered=False)
parts["plinth"] = plinth
pipe = (cq.Workplane("YZ", origin=(0, Y_C, Z_C))
        .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(L))
parts["spool"] = pipe

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0                       # past the bore wall, so every union fuses
y_inner = Y_C - ID_MAIN / 2             # bore wall stand-off from the -Y face

schedule = P["nozzles"]
layout_x = {"N1": 400.0, "N5": 700.0, "N2": 1100.0, "N3": 1300.0, "N4": 200.0}
noz, drawn = None, {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    is_dn = dnl.startswith("DN")
    od_s = dn.pipe_od(dnl) if is_dn else dn.pipe_od("DN15")
    wall_s = dn.pipe_wall(dnl if is_dn else "DN15", 40)
    if face0 == "bottom":                                     # drain: boss to the section bottom
        stub = tube(dnl if is_dn else "DN15", Z_C + STUB_PIERCE)
        s = stub.translate((layout_x[tag], Y_C, 0.0))
        note = "drain boss, flush at the envelope bottom; 50 datum passes through the section"
        z_d, x_d = 0.0, layout_x[tag]
    elif face0 == "top":                                      # vent: flush at the envelope top
        stub = tube(dnl if is_dn else "DN15", H - Z_C + STUB_PIERCE)
        s = stub.translate((layout_x[tag], Y_C, Z_C - STUB_PIERCE))
        note = ("vent, flush at the envelope top (schedule datum 800 is the "
                "placeholder above the 60 mm cross-section)")
        z_d, x_d = H, layout_x[tag]
    else:
        stub_len = y_inner + STUB_PIERCE
        z_d, note = z_for(r)
        x_d = layout_x[tag]
        stub = (tube(dnl if is_dn else "DN15", stub_len)
                .rotate((0, 0, 0), (1, 0, 0), -90)            # +Z maps to +Y
                .translate((x_d, 0.0, z_d)) if face0 == "inlet" else
                (tube(dnl if is_dn else "DN15", stub_len)
                 .rotate((0, 0, 0), (1, 0, 0), 90)            # +Z maps to -Y: +Y face
                 .translate((x_d, W, z_d))))
        s = stub
        note = (note or "schedule datum drawn") + (
            f"; {dnl} atmospheric tube stub flush at the envelope face (duty "
            "section 4); the connecting line makes the joint at the face")
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
extra = [t for t in ll_tags if not t in edge_tags]

RATING_PIPED = ("atmospheric tube/hose joint at the face (duty section 4); pipe "
                "class per AQS-PIP-003")
with open(HERE / "line_list.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["line", "from", "to", "dn", "class", "service", "rating", "note"])
    w.writerow(["MAIN", "spool start", "spool end", DN_MAIN, "-", "continuous recycle liquor",
                "atmospheric; no flange class (duty section 4)",
                "recycle-line spool per the unit duty (node design: DN15 per the "
                "issued lines); modeled as the in-envelope run of this unit's "
                "1500 x 60 x 60 box; material per duty section 3"])
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
over = [round(d - s, 2) for d, s in zip(dims, [L, W, H]) if d > s]
mass = {k: round(v.val().Volume() * RHO / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "misfit": misfit,
    "hardware_overshoot_mm": over,
    "hardware_overshoot_basis": "the DN50 schedule rows N1/N2 seat the 60 mm "
    "cross-section at the section centre; the 0.15 mm per side sits inside the 1 mm "
    "house gate (A-core 2) and is reported here, nothing resized",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "spool": {
        "type": "single run, modeled as the in-envelope 1500 mm spool on a 20 mm "
                "trough plinth (the HDR_CO2 idiom)",
        "dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN,
        "wall_basis": "lib/dn Sch 40 table (ASME B36.10M); the node states no schedule "
                      "(WORK_ORDER W12)",
        "id_mm": ID_MAIN,
        "run_basis": "the routed run (17.0 m + 9.7 m per AQS-PIP-004) stays in the "
                     "line-list route lengths; the model draws the in-envelope run",
        "material": P.get("material"),
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric tube stubs flush at the envelope faces (duty section 4: "
                    "hose, atmospheric; the connecting line makes the joint at the face; "
                    "the W4 110 percent rule draws no flange where no process pressure "
                    "is stated); schedule rating column (Class 150) carried verbatim as "
                    "text; the DN50 hand rows N1/N2 drawn verbatim against the DN15 "
                    "issued lines (holds, WORK_ORDER W12); DN15 datums clamped into the "
                    "60 mm cross-section",
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
    ["1", f"Spool {DN_MAIN} OD {OD_MAIN:g} x wall {WALL_MAIN:g} (Sch 40 table), "
          f"{L / 1000.0:g} m modeled of the routed run; bore open both ends", 1,
     "PVC-U tube (duty section 3)", mass["spool"], "make",
     "AQS-PIP-004 line DN15 (both IA-POL-02 and IA-REC-01); schedule not stated on "
     "the node - Sch 40 table drawn (hold, WORK_ORDER W12); CA does not apply to the "
     "polymer (AQS-STD-001); above 60 C the thermoplastic is CPVC - the line "
     "temperature is not on the graph (hold, WORK_ORDER W12)"],
    ["2", f"Branch connection set: {len(schedule)} atmospheric tube stubs at the "
          "schedule tags/faces/heights (N1/N2 DN50 drawn verbatim; drain and vent "
          "flush at the envelope faces)", len(schedule),
     "PVC-U tube", mass["nozzles"], "make",
     "docs-authority/nozzles/CONTINUOUS_RECYCLE.csv verbatim; datums clamped into "
     "the 60 mm cross-section (holds)"],
    ["3", f"Trough plinth {L:g} x {W:g} x {T_PLINTH:g}, the spool mount (AQS-MOD-002 "
          "dry service class)", 1, "carbon steel (ASTM A500)", mass["plinth"], "make",
     "support scheme carries the HDR_CO2 idiom (the pipe sits welded in the trough "
     "to its centreline); the wetted line is polymer and the dry support steel sees "
     "no aqueous chloride, so no corrosion allowance is applied to it "
     "(duty section 3)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for(MAT_KEY, joint="polymer"), 6,
     "trough plinth to slab, 4 per 2 m spool segment (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "pipe": {"dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN, "z_mm": Z_C},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "dn_label": DN_MAIN, "wall_mm": WALL_MAIN,
    "wall_basis": "lib/dn Sch 40 table; schedule not stated on the node (WORK_ORDER W12)",
    "mat": "PVC-U wetted per AQS-STD-002 rules M1 and M2 (duty section 3); above "
           "60 C the thermoplastic is CPVC, never metal - line temperature hold",
})
p["layout"] = {
    "frame": "origin at the envelope corner; spool along +x at the cross-section "
             "centre (y 30, z 30), trough plinth z 0..20",
    "supports": "trough plinth + 6 slab anchors (the HDR_CO2 idiom)",
    "nozzle_spread": "the schedule gives face and height; branch stubs at the "
                     "registered x positions (N1 400, N5 700, N2 1100, drain 1300, "
                     "vent 200); per-tag positions in check.nozzles_drawn",
    "line_list": "models/mfg/CONTINUOUS_RECYCLE/line_list.csv generated from the "
                 "graph edges and AQS-PIP-004; no new edge",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "missing": missing, "extra": extra}))
