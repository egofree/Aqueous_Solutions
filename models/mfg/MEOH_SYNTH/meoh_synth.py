"""MEOH_SYNTH manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads the graph node through the shared
reader (models/mfg/lib/graph_node.py); the params.json write-back beside it carries
only the builder-owned envelope, design and layout blocks. Rebuilds every solid.

Placement frame: x along 414 mm, y along 414 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 414 x 414 x 2585 mm, node size_mm (set by flow_graph/param/reactor_design.py,
  X-MFG-31). The build fills it: the vent riser tops the box, the drain clears the
  base, the +Y/-Y branch hardware spans the depth.
- Machine: the fixed-bed synthesis tube of the node design block: DN50 (OD 60.3),
  wall t_nom 3.91 mm, tube length L_bed 1485 + 400 = 1885 mm (the A-M-156 / X-MFG-31
  construction the M2 study build carried), DN100 Sch 40 thermal-oil jacket (exotherm
  to Q3), DN50 Class 600 weld-neck flanges top and bottom (ASME B16.5; the M2 build's
  OD 165 x 32 figures), catalyst bed of V_bed_L 3.2143 (cat 3.5357 kg, Cu/ZnO/Al2O3,
  a purchased-bed envelope per plan rule 6), support grids, and the feed preheater
  (0.818 kW, purchased envelope).
- Material: the pressure part is 316L per duty section 3 ("Synthesis 50 bar a,
  250 C (study); 316L per API 941, AQS-REV-H2-001 section 5"; above 200 C with H2
  partial pressure no carbon steel). The node design row "SA-106 B tube" predates
  that selection and is superseded; the jacket and shell follow the same alloy
  (holds, W12). Wall geometry stays the node t_nom 3.91 (t_req 2.8796, t_ok true).
- Nozzles: all 10 rows of docs-authority/nozzles/MEOH_SYNTH.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections on the skid faces (duty
  section 4: hose, atmospheric; the connecting line makes the joint at the face).
  The 160 inlets and 600 outlets draw as issued (both fit the 2585 box); the drain
  passes to the envelope bottom (50 datum); the vent riser stands on the top flange
  and flushes at the envelope top (the 800 datum is the schedule placeholder). N10
  is the power terminal (cable schedule X-ELS-06, AQS-ELEC-010): electrical, not
  piped - drawn as a DN15 stand-in penetration flush at the envelope top beside the
  vent riser, bore not calculated (plan W4). The rating column (Class 150) is
  carried verbatim as text, no flange hardware is drawn at the face connections
  (W4 110 % rule); the pressure-part flanges carry the B16.5 Class 600 rating of
  the node construction.
- A-VES: the bed volume is reported from the model against the node V_work_L; no
  residence time is derived (the duty section 2 claims no holdup; a fixed bed).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("MEOH_SYNTH")      # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
L, W, H = (float(v) for v in P["size_mm"])                 # 414 x 414 x 2585
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design                                # node design block (reactor_design.py, X-MFG-31)

T_PLINTH = 20.0
CX, CY = L / 2, W / 2                                      # vessel axis
OD_TUBE = 60.3                                             # DN50 (node design tube)
WALL_TUBE = float(DS.get("t_nom_mm", 3.91))                # node design t_nom
ID_TUBE = round(OD_TUBE - 2 * WALL_TUBE, 2)
L_TUBE = float(DS.get("L_bed_mm", 1485.0)) + 400.0         # A-M-156 construction
Z_FL0 = 88.0                                               # bottom flange base
T_FL = 32.0                                                # B16.5 Class 600 DN50 flange
OD_FL = 165.0
Z_FL1 = Z_FL0 + T_FL                                       # 120
Z_T0, Z_T1 = Z_FL1, Z_FL1 + L_TUBE                         # tube 120..2005
Z_TFL0 = Z_T1                                              # top flange 2005..2037
Z_TOP = Z_TFL0 + T_FL
OD_JK = float(DS.get("D_mm", 114.0))                       # node design D_mm 114 (DN100)
WALL_JK = 6.02                                             # DN100 Sch 40 table
Z_JK0, Z_JK1 = Z_T0 + 150.0, Z_T1 - 150.0                  # jacket 270..1855
L_BED = float(DS.get("L_bed_mm", 1485.0))
Z_BED0, Z_BED1 = Z_JK0 + 80.0, Z_JK0 + 80.0 + L_BED        # bed 350..1835
MAT = "316L"                                               # duty section 3 (API 941)
CA = materials.ca_for(MAT)                                 # 0.0, AQS-STD-001
RHO = materials.density(MAT)                               # 8000, lib table
RHO_BED = 2400.0                                           # catalyst bulk, study value (buy row)

assert Z_TOP < H and Z_BED1 < Z_JK1, "internals must stay inside the shell"


def od_of(r):
    """Hardware OD for a schedule row: lib-table DN rows at the table OD, and
    non-piped rows (cable, solids) at the DN15 stand-in."""
    return dn.pipe_od(r["size"]) if r["size"] in dn.PIPE else dn.pipe_od("DN15")


def tube_z(length):
    """An open-bore DN50 tube along +Z from the origin plane (the spool idiom)."""
    return (cq.Workplane("XY").circle(OD_TUBE / 2).circle(OD_TUBE / 2 - WALL_TUBE)
            .extrude(length))


def tube_dn(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth
parts["plinth"] = cq.Workplane("XY").box(L, W, T_PLINTH, centered=False)

# ---------------------------------------------------------------- pressure part: flanges + tube
flange = (cq.Workplane("XY", origin=(0, 0, 0)).circle(OD_FL / 2)
          .circle(OD_TUBE / 2 - WALL_TUBE).extrude(T_FL))
parts["bottom_flange"] = flange.translate((CX, CY, Z_FL0))
parts["top_flange"] = flange.translate((CX, CY, Z_TFL0))
parts["tube"] = tube_z(L_TUBE).translate((CX, CY, Z_T0))

# ---------------------------------------------------------------- jacket (thermal oil, to Q3)
jk = (cq.Workplane("XY", origin=(CX, CY, Z_JK0)).circle(OD_JK / 2)
      .circle(OD_JK / 2 - WALL_JK).extrude(Z_JK1 - Z_JK0))
jk = jk.union(cq.Workplane("XY", origin=(CX, CY, Z_JK0 - 10.0)).circle(OD_JK / 2)
              .circle(OD_JK / 2 - 4.0).extrude(10.0))            # bottom jacket plate
jk = jk.union(cq.Workplane("XY", origin=(CX, CY, Z_JK1)).circle(OD_JK / 2)
              .circle(OD_JK / 2 - 4.0).extrude(10.0))            # top jacket plate
parts["jacket"] = jk

# ---------------------------------------------------------------- catalyst bed envelope + grids (rule 6)
bed = (cq.Workplane("XY", origin=(CX, CY, Z_BED0)).circle(ID_TUBE / 2 - 0.2)
       .extrude(L_BED))
parts["bed"] = bed
grid = (cq.Workplane("XY").circle(ID_TUBE / 2 - 0.5)
        .circle(ID_TUBE / 2 - 4.5).extrude(6.0))
parts["grid_bottom"] = grid.translate((CX, CY, Z_BED0 - 6.0))
parts["grid_top"] = grid.translate((CX, CY, Z_BED1))

# ---------------------------------------------------------------- purchased envelope: feed preheater
parts["preheater"] = cq.Workplane("XY").box(120.0, 120.0, 160.0, centered=False).translate(
    (260.0, 30.0, T_PLINTH))

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
PACK_X = {"-Y": 90.0, "+Y": 90.0}
STUB_PIERCE = 5.0

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    # the pack centres on the vessel axis so every stub lands on the jacket/tube wall
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    x = CX - span / 2
    for r in rows:
        od_s = od_of(r)
        layout_x[r["tag"]] = round(x + od_s / 2, 1)
        x += od_s + 8.0

noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    face = FACE_OF.get(face0, face0)
    od_s = od_of(r)
    dnl_hw = dnl if dnl in dn.PIPE else "DN15"    # non-piped rows at the DN15 stand-in
    if face0 == "bottom":               # drain: boss under the bottom flange, flush at z 0
        s = tube_dn(dnl_hw, Z_FL0 + STUB_PIERCE).translate((CX, CY, 0.0))
        note = "drain boss under the bottom flange, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, CX
    elif face0 == "top" and dnl not in dn.PIPE:   # N10: power terminal (X-ELS-06)
        s = tube_dn("DN15", H - Z_TOP + STUB_PIERCE).translate((CX - 60.0, CY, Z_TOP - STUB_PIERCE))
        note = ("power terminal (cable schedule X-ELS-06): an electrical drop, not "
                "piped - drawn as a DN15 stand-in penetration flush at the envelope "
                "top beside the vent riser, bore not calculated (plan W4)")
        z_d, x_d = H, CX - 60.0
    elif face0 == "top":                # vent: riser on the top flange, flush at the box top
        s = tube_dn(dnl_hw, H - Z_TOP + STUB_PIERCE).translate((CX, CY, Z_TOP - STUB_PIERCE))
        note = ("vent riser on the top flange, flush at the envelope top; schedule "
                "datum 800 is the placeholder elevation (hold, WORK_ORDER W12)")
        z_d, x_d = H, CX
    else:
        z_d = float(r["height_mm"])     # 160 and 600 fit the 2585 box; drawn as issued
        x_d = layout_x[tag]
        stub_len = CY + STUB_PIERCE     # face to the tube axis, piercing the walls
        s = (tube_dn(dnl_hw, stub_len).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)) if face == "-Y" else
             tube_dn(dnl_hw, stub_len).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x_d, W, z_d)))
        note = ("schedule datum drawn as issued; the piped takeoff lands on the tube "
                "at the placeholder elevation (duty section 4: elevations are the "
                "schedule placeholders pending vessel design, unit tasks 02/06); "
                "atmospheric open-bore tube, flush at the envelope face")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (reported, A-VES)
v_bed = round(math.pi * (ID_TUBE / 2 - 0.2) ** 2 * L_BED / 1e6, 4)   # L
V_NODE = float(DS.get("V_bed_L", 3.2143))

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / (UNIT.lower() + ".step")))

solid = None
for k, v in parts.items():
    if k == "nozzles":
        for piece in noz_pieces:
            solid = piece if solid is None else solid.union(piece)
        continue
    solid = v if solid is None else solid.union(v)
solid = solid.val()
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {
    "plinth": parts["plinth"].val().Volume() * materials.density("CS") / 1e9,
    "pressure_part": sum(parts[k].val().Volume() for k in
                         ("bottom_flange", "top_flange", "tube")) * RHO / 1e9,
    "jacket": parts["jacket"].val().Volume() * RHO / 1e9,
    "grids": sum(parts[k].val().Volume() for k in ("grid_bottom", "grid_top")) * RHO / 1e9,
    "bed": parts["bed"].val().Volume() * RHO_BED / 1e9,
    "preheater": parts["preheater"].val().Volume() * RHO / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
v_tube = math.pi * ((OD_TUBE / 2) ** 2 - (OD_TUBE / 2 - WALL_TUBE) ** 2) * L_TUBE / 1e9
v_flanges = 2 * math.pi * ((OD_FL / 2) ** 2 - (OD_TUBE / 2 - WALL_TUBE) ** 2) * T_FL / 1e9
m_tube = round(v_tube * RHO, 1)
m_flanges = round(v_flanges * RHO, 1)
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "two solids: the vessel chain (plinth, flanges, tube, jacket, "
    "branches, preheater) and the catalyst-bed envelope with its support grids, "
    "which sit at their running clearances inside the tube bore and are not welded "
    "to the pressure part; both closed and manifold",
    "reactor": {
        "tube": {"dn": "DN50", "od_mm": OD_TUBE, "wall_mm": WALL_TUBE,
                 "z_mm": [Z_T0, Z_T1], "length_mm": L_TUBE,
                 "construction": "node design: DN50 Sch 40 SA-106 B, L_bed + 400 "
                 "(A-M-156 / X-MFG-31); the alloy follows duty section 3 - 316L per "
                 "API 941 (AQS-REV-H2-001 section 5); the SA-106 B row predates it "
                 "(hold, WORK_ORDER W12)"},
        "flanges": {"rating": "ASME B16.5 Class 600 (Group 1.1 at the 250 C design)",
                    "od_mm": OD_FL, "t_mm": T_FL, "z_mm": [Z_FL0, Z_FL1], "top_z_mm": [Z_TFL0, Z_TOP]},
        "jacket": {"od_mm": OD_JK, "wall_mm": WALL_JK, "z_mm": [Z_JK0, Z_JK1],
                   "service": "DN100 thermal-oil jacket, exotherm to Q3 (node design)"},
        "design_pressure": {"MPa": float(DS.get("design_MPa", 5.5)),
                            "t_req_mm": float(DS.get("t_req_mm", 2.8796)),
                            "t_nom_mm": WALL_TUBE,
                            "basis": "node design t_ok; wall geometry per the node, "
                            "alloy per duty section 3"},
        "bed": {"length_mm": L_BED, "volume_L_model": v_bed, "volume_L_node": V_NODE,
                "cat_kg": float(DS.get("cat_kg", 3.5357)),
                "basis": "purchased-bed envelope per plan rule 6 (Cu/ZnO/Al2O3 "
                "pellets, CTC2020_CZA class); the node V_bed_L is the authority"},
    },
    "a_ves": {"holdup_L": v_bed,
              "basis": "reported from the model bed envelope against the node "
              "V_work_L; no residence time is derived - the duty section 2 claims "
              "no holdup and a fixed bed is not a liquid holdup (A-VES)"},
    "material": {"class": "316L", "ca_mm": CA,
                 "basis": "duty section 3: synthesis 50 bar a, 250 C (study); 316L "
                 "per API 941 (AQS-REV-H2-001 section 5); above 200 C with H2 "
                 "partial pressure no carbon steel; CA 0 mm (AQS-STD-001 rule)"},
    "a_mach_named": {"purchased": "feed preheater 0.818 kW (node design preheat_kW) "
                     "drawn as its envelope and interface, plan rule 6; the drive "
                     "rating reads the maker sheet at order"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: hose, atmospheric; the W4 110 percent rule draws no "
    "flange hardware where no process pressure is stated at the face); the pressure-"
    "part flanges carry the B16.5 Class 600 rating of the node construction; the "
    "schedule rating column (Class 150) is carried verbatim as text; datums draw as "
    "issued (160 and 600 fit the 2585 box); drain flush at the envelope bottom; "
    "vent riser flush at the envelope top; the N10 power terminal (cable schedule "
    "X-ELS-06) is electrical, not piped: drawn as a DN15 stand-in penetration at "
    "the envelope top, bore not calculated",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Reactor tube DN50 OD {OD_TUBE:g} x wall {WALL_TUBE:g}, {L_TUBE:g} mm "
          "(L_bed 1485 + 400), bore open", 1, "316L tube (duty section 3)",
     m_tube, "make",
     "node design tube row (X-MFG-31, A-M-156); alloy per duty section 3: 316L per "
     "API 941 (AQS-REV-H2-001 section 5), the SA-106 B row superseded (hold, W12); "
     "CA 0 mm (AQS-STD-001)"],
    ["2", "Weld-neck flanges DN50 Class 600 RF (OD 165 x 32, B16.5), one pair", 2,
     "SA-182 F316L", m_flanges,
     "make", "ASME B16.5 Class 600 at the 250 C / 5.5 MPa design (node design; the "
     "A-M-156 construction); stud bolts in fasteners.csv"],
    ["3", f"Jacket DN100 (OD {OD_JK:g} x wall {WALL_JK:g}), {Z_JK1 - Z_JK0:g} mm, "
          "end plates, thermal-oil service to Q3", 1, "316L tube/plate", mass["jacket"],
     "make", "node design jacket row (DN100 thermal-oil jacket, exotherm to Q3)"],
    ["4", f"Catalyst bed envelope {ID_TUBE - 0.4:g} x {L_BED:g} mm: "
          f'{DS.get("cat_kg", 3.5357):g} kg Cu/ZnO/Al2O3 pellets '
          f'({DS.get("V_bed_L", 3.2143):g} L)', 1, "Cu/ZnO/Al2O3 (bulk)", mass["bed"],
     "buy", "purchased catalyst, drawn as its envelope per plan rule 6 "
     "(CTC2020_CZA class); the reduction schedule is an operating-procedure item"],
    ["5", "Catalyst support grids (pair) and inert-alumina ball layer (loading, not "
          "drawn)", 2, "316L / alpha-alumina", mass["grids"], "make",
     "the A-M-156 construction; ball layer is a loading item, not a solid"],
    ["6", "Feed preheater 0.818 kW (node design preheat_kW), envelope and "
          "interface only", 1, "316L sheath (envelope)", mass["preheater"], "buy",
     "purchased heater per plan rule 6; the maker rating reads the sheet at order"],
    ["7", "Nozzle set per docs-authority/nozzles/MEOH_SYNTH.csv: 9 atmospheric "
          "open-bore tube connections at the skid faces (drain under the bottom "
          "flange, vent riser on the top flange) plus the N10 power-terminal "
          "penetration (DN15 stand-in) at the top", len(schedule), "316L tube",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table; "
     "elevations are the schedule placeholders pending vessel design (duty "
     "section 4, hold W12); the N10 power terminal (cable schedule X-ELS-06) is "
     "electrical, not piped"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "5/8 in stud bolt with 2 heavy hex nuts", "ASTM A193 B8M / A194 8MA", 16,
     "DN50 Class 600 flange joints, top and bottom (8 per joint)",
     "ASME B16.5 stud pattern at the 250 C / 5.5 MPa design; austenitic studs for "
     "the 316L pressure part (the pre-duty-3 SA-106 build carried B7/2H, superseded "
     "by the duty section 3 alloy - hold, WORK_ORDER W12); torque per ASME PCC-1"],
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "vessel": {"axis_xy_mm": [CX, CY], "tube_z_mm": [Z_T0, Z_T1],
               "jacket_z_mm": [Z_JK0, Z_JK1], "top_flange_top_mm": Z_TOP},
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "fixed-bed methanol synthesis tube (DN50, L_bed 1485 + 400) in a "
               "DN100 thermal-oil jacket, exotherm to Q3 (node design, A-M-156)",
    "mat": "316L per duty section 3 (API 941, AQS-REV-H2-001 section 5); the node "
           "SA-106 B tube row predates the selection (WORK_ORDER W12)",
    "ca_mm": CA,
    "wall_mm": WALL_TUBE, "wall_basis": "node design t_nom (t_req 2.88, t_ok true)",
    "internals": "catalyst bed envelope (purchased, rule 6) + support grids drawn; "
                 "node internals row none, so the tracker records no internal solid",
    "purchased": "catalyst bed (3.54 kg Cu/ZnO/Al2O3) and feed preheater (0.818 kW) "
                 "drawn as envelopes and interfaces per plan rule 6",
})
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at (207, 207), plinth "
             "z 0..20; bottom flange 88..120, tube 120..2005, top flange 2005..2037, "
             "jacket 270..1855, bed 350..1835; preheater envelope at the +X corner",
    "nozzle_spread": "side rows flush at the skid faces packed from x 90 at an "
                     "od + 8 pitch (N1/N2/N8 on -Y at 160; N3/N6/N7/N9 on +Y at "
                     "600); drain under the bottom flange; vent riser on the top "
                     "flange; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "face connection hardware flush at the envelope faces; the "
                      "pressure-part flanges carry the Class 600 rating",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
