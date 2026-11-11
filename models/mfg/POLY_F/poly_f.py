"""POLY_F manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-VES).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) plus the node
design block of the graph (the kettle construction figures). Rebuilds every solid.
This replaces the pre-plan M2 study builder of the same name.

Placement frame: x along 600 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 600 x 600 x 1200 mm, node size_mm (reactor-class study minimum: jacketed
  kettle at the 0.25 kg/d monomer duty, reclaim loop to F_RECOVER, A-M-289). The
  build fills the box (vent riser to the envelope top, the X-PAR-04 registry gate).
- Kettle per the node design block: D 150 x H 225 shell (PVDF/PTFE emulsion
  polymerization kettle), wall 6 mm (study fab-page value; the node books no
  thickness - hold, W12), base and top heads, on a support ring over 4 legs and
  the plinth. The jacket and the agitator are the node power basis (the X-PAR-02
  stamp covers jacket loss + agitator, A-M-289): the jacket is drawn as its
  envelope annulus, the agitator as solids (shaft, two-blade impeller) into the
  purchased drive envelope (plan rule 6). PTFE-gasketed joints per the material
  row.
- Material: Hastelloy C-276 wetted, PTFE gasketed per duty section 3 (the node
  design row matches); 8900 kg/m3 published C-276 midpoint for mass reporting.
  The AQS-STD-001 rule has no C-276 row: no corrosion-allowance value is claimed
  (hold, W12).
- Nozzles: all rows of docs-authority/nozzles/POLY_F.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube connections (duty section 4: hose,
  atmospheric; the connecting line makes the joint at the face, the CATCH_TANK
  idiom). The 160 monomer inlets and the 600 outlet datums draw as issued; rows
  N3 and N4 carry the line-list classification `solids` (non-piped transfer) in
  their size column: drawn at DN15, bore not calculated, per plan W4, and
  labeled. The drain passes to the envelope bottom (50 datum); the vent riser
  stands on the top head and flushes at the envelope top (the 800 datum is the
  schedule placeholder - hold, W12). The rating column (Class 150) is carried
  verbatim as text, no flange (W4 110 % rule).
- A-VES: the duty claims no holdup figure (the flows are the monomer-rate design
  case, AQS-RATE-FP-MET); the gross shell volume is reported from the model and
  no residence time is derived.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles, step_export  # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 600 x 600 x 1200
REV = P["graph_revision"]
UNIT = P["unit_id"]
_g = json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())
DS = (next(n for n in _g["nodes"] if n["unit_id"] == UNIT).get("params") or {}).get("design") or {}

T_PLINTH = 20.0
CX, CY = L / 2, W / 2                                      # kettle axis
D = float(DS.get("D_mm", 150.0))                           # shell OD
H_SHELL = float(DS.get("H_mm", 225.0))                     # shell height
T_WALL = 6.0                                               # study fab-page value (hold)
R_IN = D / 2 - T_WALL
Z_RING0, Z_RING1 = 608.0, 616.0                            # support ring (annulus OD 220)
Z_SH0 = Z_RING1                                            # base head 616..628
Z_SH1 = Z_SH0 + 12.0 + H_SHELL                             # shell 628..853
Z_HEAD = Z_SH1 + 20.0                                      # top head 853..873
OD_JK, ID_JK = 184.0, 162.0                                # jacket envelope (layout choice)
Z_JK0, Z_JK1 = Z_SH0, Z_SH1 - 15.0                         # 616..838
MAT = "Hastelloy C-276"                                    # duty section 3 / node
RHO = 8900.0                                               # published C-276 midpoint (study)
CA = materials.ca_for(MAT)                                 # None: no AQS-STD-001 row (hold)

assert L == 600.0 and W == 600.0 and H == 1200.0, "POLY_F node envelope changed"
assert D == 150.0 and H_SHELL == 225.0, "POLY_F node design changed"
assert Z_HEAD < H, "kettle must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_dn(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + stand
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
legs = None
for gx in (CX - 80.0, CX + 80.0):
    for gy in (CY - 80.0, CY + 80.0):
        leg = box(gx - 15.0, gy - 15.0, T_PLINTH - 2.0, 30.0, 30.0,
                  Z_RING0 - T_PLINTH + 4.0)                # laps the support ring
        legs = leg if legs is None else legs.union(leg)
parts["legs"] = legs
ring = (cq.Workplane("XY", origin=(CX, CY, Z_RING0)).circle(110.0)
        .circle(55.0).extrude(Z_RING1 - Z_RING0))
parts["support_ring"] = ring

# ---------------------------------------------------------------- kettle (C-276) + jacket envelope
base_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
             .extrude(12.0))
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0 + 12.0)).circle(D / 2)
         .circle(R_IN).extrude(H_SHELL))
top_head = (cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
            .extrude(Z_HEAD - Z_SH1))
parts["kettle"] = base_head.union(shell).union(top_head)
jacket = (cq.Workplane("XY", origin=(CX, CY, Z_JK0)).circle(OD_JK / 2)
          .circle(ID_JK / 2).extrude(Z_JK1 - Z_JK0))
parts["jacket"] = jacket                                   # 60 C jacket envelope

# ---------------------------------------------------------------- agitator (solids) + drive envelope
shaft = (cq.Workplane("XY", origin=(CX, CY, 640.0)).circle(9.0)
         .extrude(960.0 - 640.0))
imp = None
for zz in (660.0, 700.0):
    b = box(CX - 55.0, CY - 10.0, zz, 110.0, 20.0, 8.0)
    imp = b if imp is None else imp.union(b)
parts["agitator"] = shaft.union(imp)
parts["drive"] = box(CX - 60.0, CY - 60.0, Z_HEAD, 120.0, 120.0, 120.0)   # drive envelope

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
STUB_LEN = 45.0                       # face hardware reach (the CATCH_TANK idiom)

schedule = P["nozzles"]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    span = sum(dn.pipe_od(r["size"] if str(r["size"]).startswith("DN") else "DN15") + 8.0
               for r in rows) - 8.0
    x = CX - span / 2
    for r in rows:
        dnl = r["size"] if str(r["size"]).startswith("DN") else "DN15"
        layout_x[r["tag"]] = round(x + dn.pipe_od(dnl) / 2, 1)
        x += dn.pipe_od(dnl) + 8.0

noz_pieces, drawn = [], {}
for r in schedule:
    tag, size0, face0 = r["tag"], r["size"], r["face"]
    if size0 == "cable":                                  # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": size0, "face": face0,
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
    is_dn = str(size0).startswith("DN")
    dnl = size0 if is_dn else "DN15"   # non-piped rows drawn DN15, bore not calculated (plan W4)
    od_s = dn.pipe_od(dnl)
    if face0 == "bottom":               # drain: boss under the base head, flush at z 0
        s = tube_dn(dnl, Z_SH0 + 5.0).translate((CX + 45.0, CY, 0.0))
        note = "drain boss under the base head, flush at the envelope bottom (schedule datum 50)"
        z_d, x_d = 0.0, CX + 45.0
    elif face0 == "top":                # vent: riser on the top head, flush at the box top
        s = tube_dn(dnl, H - Z_HEAD + 10.0).translate((CX, CY, Z_HEAD - 10.0))
        note = ("vent riser on the top head, flush at the envelope top; the "
                "schedule datum 800 is the placeholder (hold, WORK_ORDER W12)")
        z_d, x_d = H, CX
    else:
        h = float(r["height_mm"])
        z_d = h                          # 160 and 600 fit the 1200 box; drawn as issued
        x_d = layout_x[tag]
        s = (tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), -90)
             .translate((x_d, 0.0, z_d)) if face0 == "inlet" else
             tube_dn(dnl, STUB_LEN).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((x_d, W, z_d)))
        bore_txt = (f"{dnl} open-bore tube" if is_dn else
                    "non-piped solids transfer (line-list classification): drawn DN15, "
                    "bore not calculated (plan W4)")
        note = ("schedule datum drawn as issued; " + bore_txt + " flush at the "
                "envelope face (duty section 4: atmospheric joints are hose; the "
                "connecting line makes the joint at the face)")
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube_stub", "dn": size0, "face": face0,
                  "height_mm": r["height_mm"], "drawn_height_mm": z_d, "x_mm": x_d,
                  "schedule_rating": r["rating"], "service": r["service"], "note": note}
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- holdup (record, A-VES)
v_gross = round(math.pi * R_IN ** 2 * H_SHELL / 1e6, 4)    # L

# ---------------------------------------------------------------- export
asm = cq.Assembly(name=UNIT)
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
step_export.export_step(asm, str(out / (UNIT.lower() + ".step")))

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
    "plinth_stand": (parts["plinth"].val().Volume() + parts["legs"].val().Volume()
                     + parts["support_ring"].val().Volume()) * materials.density("CS") / 1e9,
    "kettle": parts["kettle"].val().Volume() * RHO / 1e9,
    "jacket": parts["jacket"].val().Volume() * materials.density("CS") / 1e9,
    "agitator": parts["agitator"].val().Volume() * RHO / 1e9,
    "drive": parts["drive"].val().Volume() * materials.density("PP") / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO / 1e9,
}
mass = {k: round(v, 1) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "reactor-class study minimum; jacketed kettle at the 0.25 kg/d "
    "monomer duty, reclaim loop to F_RECOVER (node envelope basis, A-M-289)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "solids_note": "the skid chain (plinth, stand, kettle, jacket envelope, "
    "agitator, drive envelope, drain and vent) fuses to one solid; the face-stub "
    "connections stay separate until the connecting lines make their joints",
    "kettle": {"od_mm": D, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_HEAD],
               "wall_basis": "study fab-page value (6 mm); the node books no "
               "thickness (WORK_ORDER W12)",
               "gross_volume_L": v_gross,
               "jacket": {"od_mm": OD_JK, "id_mm": ID_JK, "z_mm": [Z_JK0, Z_JK1],
                          "basis": "the node power basis (the X-PAR-02 stamp "
                          "covers jacket loss + agitator, A-M-289); the jacket "
                          "geometry is the envelope annulus (layout choice, "
                          "WORK_ORDER W12)"},
               "internals": {"source": "the node power basis (jacket loss + "
                             "agitator, A-M-289)",
                             "basis": "shaft and two-blade impeller drawn as "
                             "solids into the purchased drive envelope (plan "
                             "rule 6); node internals row none, so the tracker "
                             "records no internal solid"}},
    "a_ves": {"gross_volume_L": v_gross,
              "basis": "reported for the record: the duty claims no holdup "
              "figure (the flows are the AQS-RATE-FP-MET design case); no "
              "residence time is derived (A-VES)"},
    "material": {"class": "Hastelloy C-276", "ca_mm": CA,
                 "basis": "duty section 3 (the node design row matches): "
                 "Hastelloy C-276 wetted, PTFE gasketed; density 8900 kg/m3 "
                 "published midpoint for mass reporting; the AQS-STD-001 rule "
                 "has no C-276 row - no corrosion-allowance value is claimed "
                 "(hold, WORK_ORDER W12)"},
    "a_mach_named": {"purchased": "agitator drive (the node power basis names the "
                     "agitator share of the 0.0449 kW stamp) drawn as its envelope "
                     "and interface, plan rule 6; the rating reads the maker sheet "
                     "at order"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube connections flush at the envelope "
    "faces (duty section 4: atmospheric joints are hose; the W4 110 percent rule "
    "draws no flange where no process pressure is stated); the schedule rating "
    "column (Class 150) is carried verbatim as text; datums draw as issued; the "
    "N3/N4 solids rows drawn DN15, bore not calculated (plan W4)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Kettle OD {D:g} x wall {T_WALL:g}, shell {H_SHELL:g} with heads, z "
          f"{Z_SH0:g}..{Z_HEAD:g}, on the support ring, 4 legs and the plinth", 1,
     "Hastelloy C-276 plate", round(mass["kettle"] + mass["plinth_stand"], 1), "make",
     "node design D/H (AQS-DUTY-073); wall the study fab-page value (hold, "
     "WORK_ORDER W12); duty section 3 C-276 wetted, PTFE gasketed; no CA value "
     "claimed (no AQS-STD-001 C-276 row - hold, WORK_ORDER W12)"],
    ["2", f"Jacket envelope OD {OD_JK:g} / ID {ID_JK:g}, z {Z_JK0:g}..{Z_JK1:g} "
          "(the node power basis covers jacket loss, A-M-289)", 1, "carbon steel",
     mass["jacket"], "make",
     "the jacket geometry is the layout-choice annulus (WORK_ORDER W12); the "
     "60 C duty sits under the X-PAR-02 stamp"],
    ["3", "Agitator: shaft and two-blade impeller (solids) into the drive "
          "envelope", 1, "C-276 shaft / PP drive envelope",
     round(mass["agitator"] + mass["drive"], 1), "make (shaft) / buy (drive)",
     "the node power basis (jacket loss + agitator, A-M-289); the drive is the "
     "purchased item per plan rule 6, rating reads the maker sheet at order"],
    ["4", "Nozzle set per docs-authority/nozzles/POLY_F.csv: 8 atmospheric "
          "open-bore tube connections at the envelope faces (monomer inlets on "
          "-Y at 160; resin, powder and reclaim rows on +Y at 600 - N3/N4 "
          "solids rows drawn DN15 bore not calculated; drain under the base "
          "head; vent riser to the envelope top)", len(schedule), "C-276 tube",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; bores per the lib/dn Sch 40 table; "
     "the cable schedule row is carried, never drawn"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 4,
     "plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on the carbon-steel plinth; study length, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("layout_note", None)          # superseded M2 layout note
p.pop("assumptions", None)          # superseded M2 constants (lib/dn carries the table)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "kettle": {"od_mm": D, "axis_xy_mm": [CX, CY], "z_mm": [Z_SH0, Z_HEAD]},
    "jacket_z_mm": [Z_JK0, Z_JK1],
    "plinth_mm": T_PLINTH,
}
p["design"] = dict(p.get("design", {}))
p["design"].update({
    "machine": "PVDF/PTFE emulsion polymerization kettle: Hastelloy C-276 kettle "
               "D 150 x H 225 at 60 C, jacket + agitator per the node power "
               "basis (A-M-289), monomer from the gas train, reclaim to "
               "F_RECOVER (node design block, AQS-DUTY-073)",
    "mat": "Hastelloy C-276 wetted, PTFE gasketed (duty section 3; the node row "
           "matches); no CA value claimed (no AQS-STD-001 C-276 row)",
    "wall_mm": T_WALL, "wall_basis": "study fab-page value; the node books no "
                                     "thickness (WORK_ORDER W12)",
    "internals": "the agitator drawn as solids per the node power basis; node "
                 "internals row none",
    "purchased": "agitator drive - envelope and interface per plan rule 6",
})
p["layout"] = {
    "frame": "origin at the envelope corner; kettle axis at (300, 300); support "
             "ring z 608..616, shell 628..853, top head 853..873, jacket envelope "
             "616..838; drive envelope on the top head; vent riser to the "
             "envelope top (fills the node box, X-PAR-04 registry gate)",
    "nozzle_spread": "side rows flush at the envelope faces (the CATCH_TANK "
                     "idiom: the connecting line makes the joint at the face); "
                     "N1/N2 monomer in on -Y at 160; N3/N4/N5/N6 out on +Y at "
                     "600; drain boss under the base head; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "face hardware flush at the envelope faces; nothing protrudes",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
