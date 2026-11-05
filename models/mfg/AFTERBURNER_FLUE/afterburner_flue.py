"""AFTERBURNER_FLUE manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the
line-list authorities the A-PIPE idiom names: the unit's edges in
`flow_graph/plant_flow_graph.json` and the issued rows of `docs-authority/LINE_LIST.md`
(AQS-PIP-004, the DN and class authority). It writes the unit line list
`line_list.csv` and rebuilds every solid.

Route hold: the `flue_junction` class has no AQS-PLAN-006 section 4 route class,
so the acceptance is A-core with the route hold named (the COMB_HEAT/RES_HEAT
precedent). The node design block defines a duct - "afterburner flue duct to the
knock-out (flue gas at 200 C class)", DN 100, 20 m run - so the model follows the
A-PIPE idiom (spool + line list) while the route hold stays on the board; the
tracker does not extend the plan.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box). The
  build stays inside it exactly.
- Spool per the node design block: DN100 seat, 20 m run (volume 0.133 m3), modeled
  as a 1000 mm representative spool; the per-line route lengths stay in the line
  list and are not redrawn. DN100 sits outside the lib/dn DN15-DN50 table: the
  spool carries OD 114.3, wall 6.02 (ASME B36.10M Sch 40, the same table the lib
  cites; the MEOH_SYNTH DN100 jacket carried the same figures) - named, not a new
  table. Material 316L per duty section 3 ("316L pipe, dry flue at 300 C,
  insulated to hold the wall above the acid dew point"); the node design block
  says "CS Sch 40, insulated per AQS-THM-003" - the duty section 3 selection
  governs the wetted part and the conflict is carried as a hold (W12, nothing
  resized). Insulation 40 mm is a study value (AQS-THM-003 states no thickness for
  this line; hold, W12). The dielectric isolating flange at FLUE_KO
  (AQS-STD-002 section 4.3) is drawn as the interface disc at the +X spool end.
- Supports: a 20 mm trough plinth under the whole run (the spool sits welded in
  the trough to its centreline, the HDR_CO2 idiom) and 8 M10 slab anchors.
- Nozzles: all 5 rows of docs-authority/nozzles/AFTERBURNER_FLUE.csv drawn at
  tag, face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: no duct bore, no flange class). Drain flush at
  the envelope bottom (50 datum); vent flush at the envelope top (800 datum is
  the box top). The schedule rating column (Class 150) is carried verbatim as
  text.
- A-PIPE line list: `line_list.csv` is generated here from the unit's edges and
  the issued AQS-PIP-004 rows (tag, from, to, DN, class, service, rating). No new
  edge.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402  (nozzles: placement)
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("AFTERBURNER_FLUE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design
D = DS.get("design") or DS                                 # the node design block rides params.design

DN_MAIN = f'DN{float(D.get("DN", 100)):.0f}'               # DN100 seat (node design)
OD_MAIN, WALL_MAIN = 114.3, 6.02                           # ASME B36.10M Sch 40 (named; lib table is DN15-DN50)
ID_MAIN = round(OD_MAIN - 2 * WALL_MAIN, 2)
INSUL = 40.0                                               # study thickness (hold, W12)
Z_C, Y_C = 400.0, W / 2                                    # spool centreline
T_PLINTH = 20.0                                            # trough mount, HDR_CO2 idiom
MAT = "316L"                                               # duty section 3 (issued); node design says CS - hold, W12
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert OD_MAIN + 2 * INSUL <= W - 100.0, "insulated spool drawn to the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- trough plinth + spool
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
pipe = (cq.Workplane("YZ", origin=(0, Y_C, Z_C))
        .circle(OD_MAIN / 2).circle(ID_MAIN / 2).extrude(L))
iso_fl = (cq.Workplane("YZ", origin=(L - 20.0, Y_C, Z_C))     # dielectric isolating flange at the FLUE_KO end
          .circle(95.0).circle(OD_MAIN / 2).extrude(20.0))
parts["spool"] = pipe.union(iso_fl)
insul = (cq.Workplane("YZ", origin=(0, Y_C, Z_C))
         .circle(OD_MAIN / 2 + INSUL).circle(OD_MAIN / 2).extrude(L - 20.0))
parts["insulation"] = insul

# ---------------------------------------------------------------- nozzles (schedule verbatim)
STUB_PIERCE = 5.0
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def od_of(r):
    return dn.pipe_od(r["size"]) if r["size"].startswith("DN") else dn.pipe_od("DN15")


schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault(face, []).append(r)

layout_x = {}
for face in ("-Y", "+Y"):
    rows = sorted(groups.get(face, ()), key=lambda r: r["tag"])
    x = 150.0
    for r in rows:
        od_s = od_of(r)
        layout_x[r["tag"]] = round(x + od_s / 2, 1)
        x += od_s + 40.0


def tube(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


noz, drawn = None, {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    is_dn = dnl.startswith("DN")
    od_s = od_of(r)
    if face0 == "bottom":                                  # N4: drain boss, flush at the envelope bottom
        stub = tube("DN15", Y_C - (OD_MAIN / 2 + INSUL) + STUB_PIERCE)
        s = nozzles.place_on_face(stub, "bottom", 0.0, (L / 2 - 30.0, Y_C), (L, W, H))
        note = "drain boss, flush at the envelope bottom; 50 datum is the placeholder"
        z_d, x_d = 0.0, L / 2 - 30.0
    elif face0 == "top":                                   # N5: vent, flush at the envelope top
        stub = tube("DN15", (H - Z_C) - (OD_MAIN / 2 + INSUL) + STUB_PIERCE)
        s = nozzles.place_on_face(stub, "top", 0.0, (L / 2 + 30.0, Y_C), (L, W, H))
        note = "vent, flush at the envelope top (duty section 4: stays on the gas edge, not the room)"
        z_d, x_d = H, L / 2 + 30.0
    else:
        stub_len = Y_C - (OD_MAIN / 2 + INSUL) + STUB_PIERCE   # from the face to the insulation surface
        stub = tube(dnl if is_dn else "DN15", stub_len)
        s = nozzles.place_on_face(stub, face, float(r["height_mm"]), (layout_x[tag], Y_C), (L, W, H))
        note = ("schedule datum drawn; "
                + (dnl if is_dn else "no bore stated: drawn DN15, bore not calculated (plan W4)")
                + " atmospheric tube stub flush at the envelope face (duty section 4)")
        z_d = float(r["height_mm"])
        x_d = layout_x[tag]
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

with open(HERE / "line_list.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["line", "from", "to", "dn", "class", "service", "rating", "note"])
    w.writerow(["MAIN", "spool start", "spool end", DN_MAIN, "-", D.get("service", "afterburner flue duct"),
                "atmospheric; no flange class (duty section 4)",
                f"flue duct spool per the node design block ({DN_MAIN}, "
                f'{D.get("length_m", 20):g} m run, {D.get("volume_m3", 0.133):g} m3); '
                "modeled as the 1000 mm representative spool; material per duty "
                "section 3 (316L; the node design block says CS - hold, WORK_ORDER "
                "W12); dielectric isolating flange at the FLUE_KO end (AQS-STD-002 "
                "section 4.3)"])
    for r in sorted(ll_rows, key=lambda r: r["line"]):
        if r["dn"].startswith("DN") and r["dn"][2:].isdigit():
            rating, note = ("atmospheric tube joint at the duct face (duty "
                            "section 4); pipe class per AQS-PIP-003"), ""
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
mass = {k: round(v.val().Volume() * (RHO if k in ("spool", "nozzles") else
                                     120.0 if k == "insulation" else
                                     materials.density("CS")) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "misfit": misfit,
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "spool": {
        "type": "flue duct run (the spool set as the node design block defines it), "
                "modeled as a 1000 mm representative spool on a 20 mm trough plinth",
        "dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN,
        "wall_basis": "ASME B36.10M Sch 40 (named values; the lib/dn table covers "
                      "DN15-DN50; the MEOH_SYNTH DN100 jacket carried the same "
                      "figures) - WORK_ORDER W12",
        "id_mm": ID_MAIN,
        "id_req_mm": D.get("id_req_mm", 17.0),
        "id_note": f'node design sizing: required id {D.get("id_req_mm", 17.0):g} mm '
                   f'at {D.get("v_m_s", 8.0):g} m/s, DN100 seat; the Sch 40 bore '
                   f"{ID_MAIN:g} mm sits inside the DN100 seat; nothing resized",
        "run_basis": f'{D.get("length_m", 20):g} m run carried by the line-list route '
                     "lengths (AQS-PIP-004); not redrawn",
        "insulation_mm": INSUL,
        "insulation_basis": "study value; AQS-THM-003 states no thickness for this "
                            "line (hold, WORK_ORDER W12); duty section 3: "
                            "insulated to hold the wall above the acid dew point",
        "isolating_flange": "dielectric isolating flange at the FLUE_KO end "
                            "(AQS-STD-002 section 4.3), drawn as the interface disc",
        "material": MAT,
        "material_note": "duty section 3: 316L pipe, dry flue at 300 C (issued "
                         "selection); the node design block says CS Sch 40 "
                         "insulated per AQS-THM-003 - conflict carried as a hold "
                         "(WORK_ORDER W12), nothing resized",
    },
    "route_hold": "no AQS-PLAN-006 section 4 route class for class flue_junction; "
                  "the node design block defines a duct, so the model follows the "
                  "A-PIPE idiom (spool + line list) with the route hold named "
                  "(COMB_HEAT/RES_HEAT precedent)",
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric tube stubs flush at the envelope faces (duty "
                    "section 4: no flange class; the W4 110 % rule draws no flange "
                    "where no process pressure is stated); schedule rating column "
                    "(Class 150) carried verbatim as text",
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
    ["1", f"Flue duct spool {DN_MAIN} OD {OD_MAIN:g} x wall {WALL_MAIN:g} (Sch 40 "
          f"table), {L / 1000.0:g} m modeled of the {D.get('length_m', 20):g} m run; "
          "bore open both ends; dielectric isolating flange at the FLUE_KO end", 1,
     "316L tube (duty section 3)", mass["spool"], "make",
     "node design DN100 x 20 m run; DN100 outside the lib/dn table - named values "
     "per ASME B36.10M Sch 40 (hold, WORK_ORDER W12); duty section 3 names 316L, "
     "the node design block says CS - conflict carried (hold); CA 0 mm (AQS-STD-001 "
     "316L rule)"],
    ["2", f"Insulation jacket OD {OD_MAIN + 2 * INSUL:g} over the spool run "
          "(isolating-flange end bare)", 1, "mineral wool + cladding (class per "
     "AQS-THM-003)", mass["insulation"], "make",
     "duty section 3: insulated to hold the wall above the acid dew point; "
     "thickness a study value (hold, WORK_ORDER W12)"],
    ["3", f"Trough plinth {L:g} x {W:g} x {T_PLINTH:g}, the spool mount (AQS-MOD-002 "
          "dry service class)", 1, "carbon steel (ASTM A500)", mass["plinth"], "make",
     "HDR_CO2 trough-mount idiom carried; CA 1.5 mm carbon-steel rule not applied: "
     "dry flue service (duty section 3)"],
    ["4", "Branch connection set: 3 atmospheric tube stubs at the schedule "
          "tags/faces/heights, drain and vent flush at the envelope faces",
     len(schedule), "316L tube", mass["nozzles"], "make",
     "docs-authority/nozzles/AFTERBURNER_FLUE.csv verbatim; no-bore rows drawn DN15 "
     "and labeled bore not calculated (plan W4)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "trough plinth to slab, 4 per metre of spool (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "pipe": {"dn": DN_MAIN, "od_mm": OD_MAIN, "wall_mm": WALL_MAIN, "z_mm": Z_C},
    "insulation_mm": INSUL,
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(D)
p["design"].update({
    "dn_label": DN_MAIN, "wall_mm": WALL_MAIN,
    "wall_basis": "ASME B36.10M Sch 40 named values (lib table DN15-DN50; hold W12)",
    "material": MAT, "material_basis": "duty section 3 issued selection; node "
    "design block says CS - conflict carried (hold W12)",
    "insulation_mm": INSUL, "insulation_basis": "study value (hold W12)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; duct along +x at the box centre "
             "(y 300, z 400), trough plinth z 0..20; isolating flange at the +X end",
    "supports": "trough plinth + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; branch stubs pack "
                     "per face group from x 150 at OD + 40 mm pitch; drain at x "
                     "470, vent at x 530; per-tag positions in check.nozzles_drawn",
    "line_list": "models/mfg/AFTERBURNER_FLUE/line_list.csv generated from the "
                 "graph edges and AQS-PIP-004; no new edge",
    "route_hold": "flue_junction has no plan section 4 route class: A-core with "
                  "the route hold named; A-PIPE idiom per the node duct design",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"line_list_rows": report["line_list"]["rows"],
                  "missing": missing, "extra": extra}))
