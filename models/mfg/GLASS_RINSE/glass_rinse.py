"""GLASS_RINSE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 5, A-PIPE).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 600 x 800 mm, node size_mm ("issued envelope"). The build stays
  inside it exactly.
- Machine per the unit's own duty sheet and the ported AQS-MFG-001 form
  (`models/openscad/detail/mfg_rinse.scad`: rinse + dewater, liquor to SALT FEED,
  not sewer): an open-topped 316L rinse bath drawn to the envelope - tank walls 10
  mm (study - no wall thickness on the node or duty, W12), inside 1180 x 580, on a
  20 mm plinth with a channel frame. Bath volume at the 100 mm freeboard is
  reported against the duty section 2 seven-day charge 0.2577 m3. The dewater
  pump is not drawn: no pump is named on the node or duty (W12; the legacy form
  carried a DN80 pump hint only).
- Nozzles: all 4 rows of docs-authority/nozzles/GLASS_RINSE.csv drawn at tag, face,
  height and bore as atmospheric hose barbs flush at the envelope faces (duty
  section 4). Drain flush at the envelope bottom (50 datum is the schedule
  placeholder); vent flush at the envelope top (schedule datum 800 mm is the box
  top). The schedule rating column (Class 150) is carried verbatim as text; no
  flange is drawn because no process pressure is stated (plan W4 110 % rule).
- A-PIPE line list: `line_list.csv` is generated here from the unit's edges in
  `flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
  (AQS-PIP-004). No new edge.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
T_WALL = 10.0                                              # tank wall, study (W12)
FREEBOARD = 100.0                                          # freeboard above the working level
CHARGE_M3 = 0.2577                                         # duty section 2, seven-day charge
MAT = "316L"                                               # duty section 3
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)

assert L == 1200.0 and W == 600.0 and H == 800.0, "GLASS_RINSE node envelope changed"
V_BATH_M3 = ((L - 2 * T_WALL) * (W - 2 * T_WALL) * (H - T_PLINTH - T_WALL - FREEBOARD)
             / 1e9)                                        # bath to the freeboard line


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- rinse bath (the machine shell)
z0 = T_PLINTH
bath = box(0, 0, z0, L, W, T_WALL)                                        # base head
bath = bath.union(box(0, 0, z0 + T_WALL, L, T_WALL, H - z0 - T_WALL))      # -Y wall
bath = bath.union(box(0, W - T_WALL, z0 + T_WALL, L, T_WALL, H - z0 - T_WALL))  # +Y wall
bath = bath.union(box(0, T_WALL, z0 + T_WALL, T_WALL, W - 2 * T_WALL, H - z0 - T_WALL))
bath = bath.union(box(L - T_WALL, T_WALL, z0 + T_WALL, T_WALL, W - 2 * T_WALL,
                      H - z0 - T_WALL))
parts["bath"] = bath

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
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = nozzles.stub("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum sits at the box top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
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
asm.export(str(out / (UNIT.lower() + ".step")))

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
mass = {k: round(v.val().Volume() * (RHO if k != "plinth" else materials.density("CS")) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "open-topped rinse bath drawn to the envelope: 316L walls 10 mm "
                "(study), inside 1180 x 580, on a 20 mm plinth (ported AQS-MFG-001 "
                "form mfg_rinse.scad: rinse + dewater, liquor to SALT FEED, not sewer)",
        "wall_mm": T_WALL,
        "wall_basis": "study value; no authority states a tank wall (WORK_ORDER W12)",
        "v_bath_m3": round(V_BATH_M3, 4),
        "freeboard_mm": FREEBOARD,
        "charge_duty_m3": CHARGE_M3,
        "charge_note": f"duty section 2 seven-day charge {CHARGE_M3:g} m3; the bath "
                       f"holds {V_BATH_M3:.3f} m3 to the {FREEBOARD:g} mm freeboard - "
                       "reported, nothing resized (plan rule 3); the charge basis is a "
                       "capacity figure, not a residence time",
        "dewater": "dewater pump not designed: no pump is named on the node or duty "
                   "(WORK_ORDER W12; the legacy form carried a DN80 pump hint only)",
        "material": MAT,
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (duty section "
                    "4); the schedule rating column (Class 150) is carried verbatim as "
                    "text, no flange drawn (no process pressure stated)",
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
    ["1", f"Rinse bath {L:g} x {W:g} x {H - T_PLINTH:g}, wall {T_WALL:g} mm (study), "
          "open-topped, with base head on the plinth", 1, "316L (duty section 3)",
     mass["bath"], "make",
     "bath drawn to the node envelope; no wall thickness on the node or duty (hold, "
     "WORK_ORDER W12); CA 0 mm (AQS-STD-001 316L rule); bath volume report in "
     "check.machine"],
    ["2", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1,
     "carbon steel (ASTM A500)", mass["plinth"], "make",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["3", "Nozzle set per docs-authority/nozzles/GLASS_RINSE.csv: 2 hose barbs "
          "(DN25), drain and vent flush at the envelope faces", len(schedule),
     "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "barb profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per 1.2 m bay (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "bath": {"wall_mm": T_WALL, "freeboard_mm": FREEBOARD, "z0_mm": z0},
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "GLASS_RINSE: cullet rinsed to the mill feed; liquor to SALT FEED, "
               "not sewer (duty sections 1 and 4; legacy form note)",
    "material": MAT, "ca_mm": CA,
    "v_bath_m3": round(V_BATH_M3, 4), "charge_duty_m3": CHARGE_M3,
    "charge_basis": "duty section 2 seven-day charge; capacity figure, not a "
                    "residence time",
}
p["layout"] = {
    "frame": "origin at the envelope corner; bath walls to the envelope, z 20..800",
    "supports": "plinth + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row "
                     "per face/height group at the envelope face, 8 mm clear at the "
                     "bore; drain at x 560, vent at x 640; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "v_bath_m3": round(V_BATH_M3, 4), "missing": missing, "extra": extra}))
