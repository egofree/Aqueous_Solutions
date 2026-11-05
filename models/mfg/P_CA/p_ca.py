"""P_CA manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid.

Placement frame: x along 300 mm, y along 300 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 300 x 300 x 400 mm, node size_mm: "envelope from the placement seed
  (AQS-PLACE-SEED-001); sized by need"; the node envelope block records it as the
  calcium-soap precipitation vessel at the 0.025 kg/d thickener draw. The build
  fills it.
- Route hold: the node class is `precip`, which has no row in the AQS-PLAN-006
  section 4 route table - the tracker records the hold and the acceptance cell
  reads A-core (route hold). The vessel work itself follows the F-VES operations
  as the nearest family (W10).
- Body: PP-H precipitation vessel (duty section 3, X-MAT-22) - OD 250, wall 6
  (study; no thickness booked on the node - hold, W12) - with heads, seated on a
  steel frame plinth (duty section 3: "steel frame and housing outside the
  wetted headspace"). The PP agitator the duty section 3 names is drawn from the
  model: shaft down the vessel axis with two blades (study dims - hold, W12)
  and the drive envelope above the top head.
- Nozzles: all 2 rows of docs-authority/nozzles/P_CA.csv (duty section 4: no
  piped process connection on the graph yet; the CSV carries only the drain and
  vent utilities): N1 drain, open bore through the plinth and base head, flush
  at the envelope bottom (50 datum); N2 vent flush at the vessel top head (its
  800 datum predates the 400 box - hold, W12). PE slurry lines: the graph has no
  rated edges yet, so none are drawn (hold, W12). The schedule rating column
  (Class 150) is carried verbatim as text; no flange is drawn because no
  process pressure is stated (W4 110 % rule).
- A-VES does not apply (the class carries A-core only); the vessel working
  volume is still reported from the model for the record.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, graph_node, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("P_CA")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 300 x 300 x 400, seed envelope
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                 # steel frame plinth (duty section 3: steel frame)
T_WALL = 6.0                    # PP-H sheet wall, study - no node booking (WORK_ORDER W12)
D = 250.0                       # vessel OD (layout choice: 25 mm stand-off to the faces)
R_IN = D / 2 - T_WALL           # 119
CX, CY = L / 2, W / 2
Z_SH0 = T_PLINTH - 2.0          # base head seat, sunk 2 into the plinth so the union fuses
Z_SH1 = 336.0                   # shell 18..336
T_HEAD = 20.0
Z_TOP = Z_SH1                   # top head 336..356
SHAFT_D = 12.0                  # PP agitator shaft, study (duty section 3 names the agitator)
SHAFT_Z1 = 396.0                # shaft from the base head up through the top head into the drive
BLADE_Z = (80.0, 150.0)         # blade heights, study
BLADE_W, BLADE_T = 70.0, 6.0    # blade span x thickness, study
MOTOR_D, MOTOR_Z0 = 90.0, Z_TOP + T_HEAD       # drive envelope on the top head, 356..400

CA_PP = materials.ca_for("PP-H")            # 0.0, polymer: AQS-STD-001
RHO_PP = materials.density("PP")            # 910, lib PP table (PP-H class basis)
RHO_CS = materials.density("CS")            # 7850

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert MOTOR_Z0 + 44.0 <= H, "drive envelope must stay inside the envelope"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- steel frame plinth
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["frame_plinth"] = plinth

# ---------------------------------------------------------------- PP-H vessel + heads
vessel = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
          .circle(R_IN).extrude(Z_SH1 - Z_SH0))
vessel = vessel.union(cq.Workplane("XY", origin=(CX, CY, Z_TOP)).circle(D / 2)
                      .extrude(T_HEAD))                                      # top head 336..356
vessel = vessel.union(cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
                      .extrude(T_HEAD))                                      # base head laps plinth
parts["vessel"] = vessel

# ---------------------------------------------------------------- PP agitator (duty section 3)
agit = cq.Workplane("XY", origin=(CX, CY, Z_SH0 + T_HEAD)).circle(SHAFT_D / 2).extrude(SHAFT_Z1 - Z_SH0 - T_HEAD)
for z_b in BLADE_Z:
    agit = agit.union(box(CX - BLADE_W / 2, CY - BLADE_T / 2, z_b, BLADE_W, BLADE_T, BLADE_T))
parts["agitator"] = agit
drive = (cq.Workplane("XY", origin=(CX - MOTOR_D / 2, CY - MOTOR_D / 2, MOTOR_Z0))
         .circle(MOTOR_D / 2).extrude(H - MOTOR_Z0))
drive = drive.union(cq.Workplane("XY", origin=(CX, CY, SHAFT_Z1)).circle(SHAFT_D / 2)
                    .extrude(H - SHAFT_Z1))             # shaft hub through the drive
parts["agitator_drive"] = drive

# ---------------------------------------------------------------- nozzles (schedule verbatim)
def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


schedule = [r for r in P["nozzles"]]
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    od = dn.pipe_od(dnl)
    if face0 == "bottom":                      # N1 drain: open bore through plinth + base head
        s = tube(dnl, 50.0).translate((CX + 80.0, CY, 0.0))
        note = "drain, open bore through the plinth and base head, flush at the envelope bottom (50 datum)"
        z_d, x_d = 0.0, CX + 80.0
    else:                                      # N2 vent: flush at the vessel top head
        s = tube(dnl, 40.0).translate((CX - 80.0, CY, Z_TOP - 20.0))
        note = ("vent, flush at the vessel top head; schedule datum 800 predates the "
                "400 box (hold, WORK_ORDER W12)")
        z_d, x_d = Z_TOP + T_HEAD, CX - 80.0
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "x_mm": x_d, "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
# the pieces stay a compound; each roots in the plinth or head and is fused piecewise
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

# ---------------------------------------------------------------- vessel volume (for the record)
v_work = round(math.pi * R_IN ** 2 * (SHAFT_Z1 - (Z_SH0 + T_HEAD)) / 1e9, 4)

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
    "frame_plinth": parts["frame_plinth"].val().Volume() * RHO_CS / 1e9,
    "vessel": parts["vessel"].val().Volume() * RHO_PP / 1e9,
    "agitator": parts["agitator"].val().Volume() * RHO_PP / 1e9,
    "agitator_drive": parts["agitator_drive"].val().Volume() * RHO_PP / 1e9,
    "nozzles": sum(p.val().Volume() for p in noz_pieces) * RHO_PP / 1e9,
}
mass = {k: round(v, 2) for k, v in mass.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "envelope from the placement seed (params size_note); the node "
    "envelope block records the calcium-soap precipitation vessel at the 0.025 kg/d "
    "thickener draw",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "route_hold": "the node class is precip, which has no row in the AQS-PLAN-006 "
    "section 4 route table - the tracker records the hold; the vessel work follows "
    "the F-VES operations as the nearest family (WORK_ORDER W10)",
    "working_volume_m3": v_work,
    "working_volume_basis": "reported for the record: the duty section 2 books no "
    "holdup basis (sizing study pending), so no level or residence is derived",
    "vessel": {"wall_mm": T_WALL, "wall_basis": "study value; no thickness booked on "
               "the node (WORK_ORDER W12)",
               "internals": {"source": "the duty section 3 material line names the PP "
                             "agitator; drawn from the model",
                             "basis": "shaft and blade dimensions are study values "
                             "(WORK_ORDER W12); the node internals row is none, so the "
                             "tracker records no internal solid"}},
    "material": {"class": "PP-H", "ca_mm": CA_PP,
                 "basis": "duty section 3 (X-MAT-22): PP-H vessel + PP agitator, PE "
                 "slurry lines, steel frame outside the wetted headspace; scale is "
                 "knocked down mechanically at clean-out (a design note, not an "
                 "allowance); the 316L mixed-build alternative is a named hold "
                 "(WORK_ORDER W12); the duty section 8 line 'material selection "
                 "pending (unit task 09)' predates the issued X-MAT-22 selection",
                 "density_basis": "PP-H at the lib PP table density (910 kg/m3)"},
    "open_items": ["relief case study pending (unit task 07) - no set point is "
                   "claimed on this page (duty section 6)",
                   "no piped process connection on the graph yet; the PCA_TO_GREASE "
                   "edges carry no kg/d rate yet (duty section 8)",
                   "instrument loops P_CALT-01, P_CAPT-01, P_CATE-01 are loop "
                   "hardware, not modeled (duty section 5)",
                   "nozzle elevations are schedule placeholders (unit tasks 02/06)"],
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube (lib/dn Sch 40 table), flush at the "
    "envelope bottom and the vessel top head; the schedule rating column (Class 150) "
    "is carried verbatim as text, no flange drawn (W4 110 % rule: no process pressure "
    "stated)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Steel frame plinth {L:g} x {W:g} x {T_PLINTH:g} (duty section 3: steel "
          "frame outside the wetted headspace)", 1, "carbon steel (ASTM A500)",
     mass["frame_plinth"], "make",
     "CA 1.5 mm carbon-steel rule not applied: the frame is outside the wetted "
     "headspace and carries the vessel only (duty section 3); paint scheme at "
     "fabrication"],
    ["2", f"PP-H vessel OD {D:g}, wall {T_WALL:g} mm, z {Z_SH0:g}..{Z_SH1:g}, with "
          "heads", 1, "PP-H plate",
     round(mass["vessel"], 2), "make",
     "duty section 3 (X-MAT-22): PP-H precipitation vessel; wall study (hold, "
     "WORK_ORDER W12); CA 0 mm (AQS-STD-001 polymer rule); the 316L mixed-build "
     "alternative is a named hold"],
    ["3", "PP agitator: shaft on the vessel axis with two blades (duty section 3 "
          "names the agitator; dimensions study)", 1, "PP-H rod/plate",
     mass["agitator"], "make", "study dimensions (hold, WORK_ORDER W12)"],
    ["4", "Agitator drive envelope on the top head (purchased, maker class at "
          "order)", 1, "polymer/maker class", mass["agitator_drive"], "buy",
     "plan rule 6: purchased item drawn as its envelope and interface; drive rating "
     "per the maker TDS at order (WORK_ORDER W12)"],
    ["5", "Nozzle set per docs-authority/nozzles/P_CA.csv: 1 drain (through the "
          "plinth and base head), 1 vent at the vessel top head", len(schedule),
     "PP-H pipe (lib/dn Sch 40 table dims)", mass["nozzles"], "make",
     "schedule verbatim; no piped process connection on the graph yet - drain and "
     "vent utilities only; PE slurry lines wait for rated edges (hold, WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M8 wedge anchor", fasteners.grade_for("CS"), 4,
     "frame plinth to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M10 hold-down bolt", fasteners.grade_for("316L"), 4,
     "vessel base ring to the frame plinth (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); "
     "study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "envelope from the placement seed (params size_note); the calcium-soap "
             "precipitation vessel at the 0.025 kg/d thickener draw (node envelope "
             "block)",
    "vessel": {"od_mm": D, "z_mm": [Z_SH0, Z_TOP + T_HEAD]},
    "frame_plinth_mm": T_PLINTH,
}
p["design"] = {
    "duty": GN.design["duty"],
    "thickener_kgd": GN.design["thickener_kgd"],
    "mat": "PP-H precipitation vessel + PP agitator; steel frame outside the wetted "
           "headspace (duty section 3, X-MAT-22)",
    "ca_mm": CA_PP,
    "wall_mm": T_WALL, "wall_basis": "study value (WORK_ORDER W12)",
    "internals": "PP agitator per duty section 3; dimensions study (WORK_ORDER W12)",
    "route": "route hold: no AQS-PLAN-006 section 4 class for precip; F-VES "
             "operations as the nearest family (WORK_ORDER W10)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; vessel axis at x 150, y 150, z up; "
             "frame plinth z 0..20; drive envelope z 356..400",
    "nozzle_spread": "drain through the plinth at x 230; vent at the vessel top head "
                     "at x 70; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "working_volume_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
