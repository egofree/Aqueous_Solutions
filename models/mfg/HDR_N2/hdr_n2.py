"""HDR_N2 manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 5, A-PIPE).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the line-list
authorities the A-PIPE acceptance names: the unit's edges in
`flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
(AQS-PIP-004, the DN and class authority). It writes the unit line list
`line_list.csv` and rebuilds every solid.

Placement frame: x along the 2000 mm run, y across the 50 mm cross-section, z up,
origin at the envelope corner. Every dimension is an authority figure or a named
layout choice:

- Envelope 2000 x 50 x 50 mm, node size_mm: "DN32 manifold x 20 m run (0.009 m3),
  header sizing (flow_graph/param/headers.py, AQS-DUTY-075)". The model is the spool
  set as the node defines it: one manifold run, modeled as a 2000 mm representative
  spool; the per-line route lengths stay in the line list and are not redrawn.
- Manifold per the node design block: DN32 (OD 42.4), 316L tube (duty section 3).
  Wall on the lib/dn Sch 40 table (the schedule is not stated on the node - WORK_ORDER
  W12); the M1 class sheet (AQS-PIP-003) carries the schedule at order. Bore open at
  both spool ends.
- Supports: a 20 mm plinth trough under the whole run and 8 M10 slab anchors (the
  layout the HDR_CO2 acceptance carries).
- Nozzles: all 13 rows of docs-authority/nozzles/HDR_N2.csv drawn at tag, face,
  height and bore as open-bore tube stubs flush at the envelope faces (duty section 4:
  atmospheric, no flange class). The DN50 row (N1, OD 60.3) is larger than the 50 mm
  cross-section: drawn at the manifold centreline and the mesh leaves the envelope in
  z - the misfit is reported (plan rule 3), nothing is resized. The N12 solids row
  (nitrogen return) is drawn DN15 and labeled bore not calculated (plan W4). Schedule
  datums 10 mm are clamped up for the branch bore; the DN25 branch datums (37 mm) are
  clamped down to clear the crown; the 160 mm and 600 mm datums are placeholders and
  are clamped (holds, W12). The rating column (Class 150) is carried verbatim as text.
  N3 and N4 carry services with no present edge on the graph; drawn verbatim, no edge
  created.
- A-PIPE line list: `line_list.csv` is generated here from the graph edges and the
  issued AQS-PIP-004 rows (tag, from, to, DN, class, service, rating). No new edge.
"""
import csv, json, math, pathlib, re, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402  (nozzles: placement)
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 2000 x 50 x 50
REV = P["graph_revision"]
UNIT = P["unit_id"]
D = P["design"]
DN_MAIN = f'DN{D["DN"]:.0f}'                               # DN32
OD_MAIN, WALL_MAIN = dn.pipe_od(DN_MAIN), dn.pipe_wall(DN_MAIN, 40)
ID_MAIN = round(OD_MAIN - 2 * WALL_MAIN, 2)
Z_C, Y_C = H / 2, W / 2                                    # manifold centreline
T_PLINTH = 20.0                                            # trough mount
MAT_KEY = "316L"                                           # duty section 3: 316L tube
RHO = materials.density(MAT_KEY)
CLAMP_MARGIN = 0.7                                         # stub radius clearance to the faces

assert L == 2000.0 and W == 50.0 and H == 50.0, "HDR_N2 node envelope changed"
assert DN_MAIN == "DN32", "HDR_N2 node design DN changed"

FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def z_for(row):
    """Drawn centreline height for a side stub: the schedule datum clamped into the
    cross-section, with the clamp or the cross-section misfit named."""
    h = float(row["height_mm"])
    od_s = dn.pipe_od(row["size"]) if row["size"].startswith("DN") else dn.pipe_od("DN15")
    lo, hi = od_s / 2 + CLAMP_MARGIN, H - od_s / 2 - CLAMP_MARGIN
    if lo > hi:
        return round(Z_C, 1), (
            f"the {row['size']} hardware (OD {od_s:g} mm) is larger than the 50 mm "
            f"cross-section; drawn at the manifold centreline (schedule datum {h:g} mm is "
            "a placeholder); the mesh leaves the envelope in z by "
            f"{round(od_s - H, 1)} mm - misfit reported (plan rule 3), nothing resized "
            "(hold, WORK_ORDER W12)")
    z = min(max(h, lo), hi)
    note = None
    if h < lo:
        note = (f"schedule datum {h:g} mm clamped up to {round(z, 1)} mm to keep the "
                f"{row['size']} bore inside the 50 mm cross-section (hold, WORK_ORDER W12)")
    elif h > hi:
        note = (f"schedule datum {h:g} mm is a placeholder above the 50 mm cross-section; "
                f"clamped down to {round(z, 1)} mm (hold, WORK_ORDER W12)")
    return round(z, 1), note


# ---------------------------------------------------------------- spool + supports
parts = {}
plinth = cq.Workplane("XY").box(L, W, T_PLINTH, centered=False)
parts["plinth"] = plinth
pipe = (cq.Workplane("YZ", origin=(0, Y_C, Z_C))
        .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(L))
parts["manifold"] = pipe

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0                       # past the bore wall, so every union fuses
y_inner = Y_C - ID_MAIN / 2             # bore wall stand-off from the -Y face


def tube(dnl, length):
    """An open-bore pipe stub along +Z from the origin plane (the flow path is real).

    lib/nozzles.stub fills its bore on union (its docstring says the opposite); a
    header's branches carry flow, so this model draws the stub from the lib/dn table
    itself: OD and Sch 40 wall, bore open at both ends."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return (cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length))


schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault(face, []).append(r)

layout_x = {}
for face in ("-Y", "+Y"):
    rows = sorted(groups.get(face, ()), key=lambda r: r["tag"])
    x = 100.0
    for r in rows:
        od_s = dn.pipe_od(r["size"]) if r["size"].startswith("DN") else dn.pipe_od("DN15")
        layout_x[r["tag"]] = round(x + od_s / 2, 1)
        x += od_s + 30.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    is_dn = dnl.startswith("DN")
    od_s = dn.pipe_od(dnl) if is_dn else dn.pipe_od("DN15")   # no-bore rows drawn DN15 (plan W4)
    if face0 == "bottom":                                     # drain: boss to the 50 datum, flush at z 0
        stub = tube(dnl if is_dn else "DN15", y_inner + STUB_PIERCE)
        s = nozzles.place_on_face(stub, "bottom", 0.0, (L / 2 - 30.0, Y_C), (L, W, H))
        note = "drain boss, flush at the envelope bottom; 50 datum is the cross-section height"
        z_d, x_d = 0.0, L / 2 - 30.0
    elif face0 == "top":                                      # vent: flush at the envelope top
        stub = tube(dnl if is_dn else "DN15", y_inner + STUB_PIERCE)
        s = nozzles.place_on_face(stub, "top", 0.0, (L / 2 + 30.0, Y_C), (L, W, H))
        note = "vent, flush at the envelope top (duty section 4: into the loop suction, not the room)"
        z_d, x_d = H, L / 2 + 30.0
    else:
        stub_len = y_inner + STUB_PIERCE
        z_d, note = z_for(r)
        x_d = layout_x[tag]
        stub = tube(dnl if is_dn else "DN15", stub_len)
        s = nozzles.place_on_face(stub, face, z_d, (x_d, Y_C), (L, W, H))
        note = (note or "schedule datum drawn") + (
            f"; {dnl if is_dn else 'no bore stated: drawn DN15, bore not calculated (plan W4)'}"
            " atmospheric tube stub flush at the envelope face (duty section 4)")
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": float(r["height_mm"]),
                  "drawn_height_mm": z_d if face in ("-Y", "+Y", "top", "bottom") else z_d,
                  "x_mm": x_d, "schedule_rating": r["rating"], "service": r["service"], "note": note}
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
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s0 + 1.0 for d, s0 in zip(dims, [L, W, H]))
# cad/stl is the envelope registry in metres (X-PAR-04) and is gated to the node size_mm
# within 1 mm (flow_graph/param/test_envelopes.py). A build that carries the reported
# DN50 cross-section misfit does not replace the registry: the envelope-consistent study
# mesh stays (the AL_POT precedent), and the build mesh lives in export/.
if inside:
    solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                                 tolerance=0.0005, angularTolerance=0.4, ascii=True)
    cad_stl_note = "replaced from the build"
else:
    cad_stl_note = ("kept as the envelope registry at the node size (the build carries "
                    "the reported DN50 cross-section misfit; build mesh in export/)")

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

RATING_PIPED = ("atmospheric tube/hose joint at the header face (duty section 4: no "
                "flange class); pipe class per AQS-PIP-003")
with open(HERE / "line_list.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["line", "from", "to", "dn", "class", "service", "rating", "note"])
    w.writerow(["MAIN", "spool start", "spool end", DN_MAIN, "-", D["service"],
                "atmospheric; no flange class (duty section 4)",
                f"manifold spool per AQS-DUTY-075 (node design: {DN_MAIN}, "
                f'{D["length_m"]:g} m run, {D["volume_m3"]:g} m3); modeled as the '
                "2000 mm representative spool; material per duty section 3"])
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
misfit = None if inside else (f"bbox {dims} against size_mm {[L, W, H]}; the DN50 branch "
                              "hardware (OD 60.3) is larger than the 50 mm cross-section; "
                              "nothing resized (plan rule 3)")
mass = {k: round(v.val().Volume() * (RHO if k != "plinth" else materials.density("CS")) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "misfit": misfit,
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "spool": {
        "type": "single manifold run (the spool set as the node defines it), modeled as a "
                "2000 mm representative spool on a 20 mm trough plinth",
        "dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN,
        "wall_basis": "lib/dn Sch 40 table (ASME B36.10M); the node states no schedule; "
                      "the M1 class sheet carries the schedule at order (WORK_ORDER W12)",
        "id_mm": ID_MAIN,
        "id_grid_mm": D["id_req_mm"],
        "id_note": f'AQS-DUTY-075 sizing: required id {D["id_req_mm"]:g} mm at '
                   f'{D["v_m_s"]:g} m/s, seat minimum DN{D["DN"]:g}; the DN-8 grid bore and '
                   "the Sch 40 bore both seat DN25; nothing resized",
        "run_basis": f'{D["length_m"]:g} m run carried by the line-list route lengths '
                     "(AQS-PIP-004); not redrawn",
        "material": P["material"],
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces (duty "
                    "section 4: atmospheric, no flange class; the W4 110 % rule draws no "
                    "flange where no process pressure is stated); the DN50 row (N1) is "
                    "larger than the 50 mm cross-section and is drawn at the manifold "
                    "centreline - misfit reported, nothing resized; schedule rating "
                    "column (Class 150) carried verbatim as text",
    "line_list": {
        "csv": f"models/mfg/{UNIT}/line_list.csv",
        "source": "unit edges in flow_graph/plant_flow_graph.json + docs-authority/"
                  "LINE_LIST.md (AQS-PIP-004, DN and class authority)",
        "edges": len(edges), "rows": len(ll_rows) + 1,
        "missing_line_rows": missing, "rows_without_edge": extra,
        "no_new_edge": True,
    },
    "part_mass_kg": mass, "cadquery": cq.__version__,
    "cad_stl": cad_stl_note,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
pipe_len = L / 1000.0
rows = [
    ["1", f"Manifold spool {DN_MAIN} OD {OD_MAIN:g} x wall {WALL_MAIN:g} (Sch 40 table), "
          f"{pipe_len:g} m modeled of the {D['length_m']:g} m run; bore open both ends", 1,
     "316L tube (duty section 3)", mass["manifold"], "make",
     "AQS-DUTY-075 node design DN32 x 20 m run; schedule not stated on the node - Sch 40 "
     "table drawn, the M1 class sheet carries the schedule at order (hold, WORK_ORDER "
     "W12); CA 0 mm (AQS-STD-001 316L rule)"],
    ["2", f"Branch connection set: {len(schedule)} atmospheric open-bore tube stubs at the "
          "schedule tags/faces/heights, incl. 1 DN50 row (drawn at the manifold "
          "centreline - misfit reported) and 1 no-bore row drawn DN15", len(schedule),
     "316L tube", mass["nozzles"], "make",
     "docs-authority/nozzles/HDR_N2.csv verbatim; no-bore rows drawn DN15 and labeled "
     "bore not calculated (plan W4); datums clamped into the 50 mm cross-section (holds); "
     "N3/N4 carry services with no present edge, drawn verbatim"],
    ["3", f"Trough plinth {L:g} x {W:g} x {T_PLINTH:g}, the spool mount (AQS-MOD-002 dry "
          "service class)", 1, "carbon steel (ASTM A500)", mass["plinth"], "make",
     "support scheme carried from the HDR_CO2 acceptance (trough mount, no top rails); "
     "metal parts bonded per duty section 3"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "trough plinth to slab, 4 per 2 m spool segment (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
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
    "wall_basis": "lib/dn Sch 40 table; schedule not stated on the node; the M1 class "
                  "sheet carries the schedule at order (WORK_ORDER W12)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; manifold along +x at the cross-section centre "
             "(y 25, z 25), trough plinth z 0..20",
    "supports": "trough plinth + 8 slab anchors; no top rails (the branch zone stays clear)",
    "nozzle_spread": "the schedule gives face and height only; branch stubs pack per face "
                     "group from x 100 at OD + 30 mm pitch; drain at x 970, vent at x 1030; "
                     "the DN50 rows sit at the manifold centreline; per-tag positions in "
                     "check.nozzles_drawn",
    "line_list": "models/mfg/HDR_N2/line_list.csv generated from the graph edges and "
                 "AQS-PIP-004; no new edge",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "missing": missing, "extra": extra, "misfit": misfit}))
