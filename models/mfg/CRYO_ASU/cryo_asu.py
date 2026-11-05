"""CRYO_ASU manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Study. Not a PE stamp. Reads the graph node through models/mfg/lib/graph_node.py
(the plant graph is the sole authority); the tracker-written params.json copy keeps
the builder-owned layout and study blocks beside the W2 fields, and the graph
revision travels from the graph node into check.json.

Placement frame: x along the skid, y across, z up, origin at the skid corner. Every
dimension is an authority figure or a named layout choice:

- Internals per the node (W3): 3 x 13X TSA beds, CO2 two-stage compressor and
  condenser, heated Ar getter; noble-gas inventories pass through. Bed geometry is
  the node design block (params.design: beds, bed_D_mm, bed_L_mm, sorbent_kg_per_bed;
  AQS-PAR-001 sizing). Each bed: 316L shell t 6 (house style-builder
  plate convention, study), flat heads, a support grid under and over the sorbent
  bed, and the 13X sorbent as a solid (the A-COL packing).
- Envelope: the node size_mm [300, 300, 2000] is the M0 study registry box
  (params size_note says so). The beds at their design diameter cannot fit it: the
  build leaves the study box on x and y and the misfit is reported on the tracker
  board per AQS-PLAN-006 rule 3. Nothing is resized.
- CO2 compressor (two-stage per the internals row), condenser and Ar getter are
  purchased items (AQS-PLAN-006 rule 6): drawn as their envelope and interface,
  rated from the node design kW (co2_comp_kW, co2_chill_kW, getter_kW).
- Nozzles: every row of docs-authority/nozzles/CRYO_ASU.csv at tag, face,
  height and bore. Inlets land on the bed shells' -Y side, outlets on +Y; the
  z 160 rows land on the frame; the vent is clamped to the assembly top (schedule
  datum 2000 predates the TSA layout - named hold); the drain hangs from bed 1 to
  its 50 datum. Solids rows are DN15 stubs labeled bore not calculated. The
  schedule rating column (Class 150) is carried verbatim as text; no flange is
  drawn because the node relief basis is atmospheric venting (API 2000, A-M-155).
  Non-piped rows (the N17 power terminal, cable schedule X-ELS-06) are carried
  verbatim in check.json and never drawn - no STEP, BOM or geometry change.

Materials per docs-authority/duties/CRYO_ASU.md section 3: 316L, condensation,
corrosion allowance 0 mm, no carbon steel.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles         # noqa: E402

GN = graph_node.graph_node("CRYO_ASU")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items()
          if k not in P or P[k] in (None, {})})   # builder-owned blocks only
D = P["design"]
REV = P["graph_revision"]

# ------------------------------------------------------------------ cited constants
N_BEDS = int(D["beds"])
BED_D = float(D["bed_D_mm"])                              # node design block (AQS-PAR-001)
BED_L = float(D["bed_L_mm"])
SORBENT_KG = float(D["sorbent_kg_per_bed"])
SHELL_T = 6.0             # house style-builder plate convention (study; W12 hold)
GRID_T = 20.0             # support grids, study
LEG_H = 200.0             # base plinth, carries the z 160 frame rows (bore band 130..190)
PED_H = 170.0             # bed pedestals, study
Z0 = LEG_H + PED_H        # bed bottom-head underside, 370
CA = materials.ca_for("316L")                             # 0.0 (AQS-STD-001 rule)
RHO = {"316L": materials.density("316L"), "13X": 700.0}   # sorbent bulk density, study

BED_PITCH = BED_D + 100.0                                 # study layout pitch
CX0 = BED_PITCH / 2                                       # first bed axis x
CY = 280.0                                                # bed axis y
SKID_L = 2460.0
SKID_W = 560.0
R_BED = BED_D / 2
R_ID = R_BED - SHELL_T

bed_x = [CX0 + i * BED_PITCH for i in range(N_BEDS)]      # one pitch per bed


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


parts = {}

# ---------------------------------------------------------------- base frame (skid)
frame = box(0, 0, 0, SKID_L, SKID_W, LEG_H)               # solid plinth frame, welded
for bx in (600.0, 1800.0):
    frame = frame.cut(box(bx - 250, SKID_W / 2 - 90, 0, 500, 180, LEG_H))   # fork slots
parts["frame"] = frame

# ---------------------------------------------------------------- TSA beds (node design)
beds = None
sorb = None
for bx in bed_x:
    shell = (cq.Workplane("XY", origin=(bx, CY, Z0 + SHELL_T)).circle(R_BED)
             .circle(R_ID).extrude(BED_L))
    head_lo = cq.Workplane("XY", origin=(bx, CY, Z0)).circle(R_BED).extrude(SHELL_T)
    head_hi = (cq.Workplane("XY", origin=(bx, CY, Z0 + SHELL_T + BED_L)).circle(R_BED)
               .extrude(SHELL_T))
    grid_lo = (cq.Workplane("XY", origin=(bx, CY, Z0 + SHELL_T)).circle(R_ID + 3)
               .extrude(GRID_T))                          # laps 3 mm into the shell wall
    grid_hi = (cq.Workplane("XY", origin=(bx, CY, Z0 + SHELL_T + BED_L - GRID_T))
               .circle(R_ID + 3).extrude(GRID_T))
    bed = shell.union(head_lo).union(head_hi).union(grid_lo).union(grid_hi)
    for dx in (-110.0, 110.0):
        ped = box(bx + dx - 100, CY - 100, LEG_H, 200, 200, Z0 - LEG_H + 5)   # laps the head 5
        bed = bed.union(ped)
    beds = bed if beds is None else beds.union(bed)
    # 13X sorbent solid: bulk 700 kg/m3 (study), laps 5 mm into the lower grid so the
    # union fuses (a bed that only sat on the grid left a tangent, non-manifold joint)
    v_bulk = SORBENT_KG / RHO["13X"] * 1e9                # mm3
    h_sorb = min(v_bulk / (math.pi * (R_ID - 8) ** 2), BED_L - 2 * SHELL_T - 2 * GRID_T + 5)
    s = (cq.Workplane("XY", origin=(bx, CY, Z0 + SHELL_T + GRID_T - 5))
         .circle(R_ID - 8).extrude(h_sorb))
    sorb = s if sorb is None else sorb.union(s)
parts["beds"] = beds
parts["sorbent"] = sorb

# ---------------------------------------------------------------- purchased machinery (rule 6)
mach = box(1700.0, 40.0, LEG_H - 5, 320.0, 480.0, 900.0)  # CO2 two-stage compressor envelope
mach = mach.union(rod(90.0, (1860.0, CY, LEG_H + 900.0 - 5), "Z", 180.0))   # motor bump
cond = box(2050.0, 40.0, LEG_H - 5, 200.0, 480.0, 500.0)  # condenser / chiller coil envelope
for dy in (120.0, 360.0):
    cond = cond.union(rod(70.0, (2150.0, 40.0 + dy, LEG_H + 500.0 - 5), "Z", 60.0))
getter = rod(110.0, (2330.0, CY, LEG_H - 5), "Z", 640.0)  # heated Ar getter cartridge
getter = getter.union(box(2330.0 - 130.0, CY - 130.0, LEG_H - 5, 260.0, 260.0, 30.0))
parts["machinery"] = mach.union(cond).union(getter)

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


def od_of(row):
    return dn.pipe_od("DN15") if row["size"] == "solids" else dn.pipe_od(row["size"])


def is_piped(r):
    """A row the builder draws: a piped bore, or a solids row drawn as a DN15 stub."""
    return r["size"] in dn.PIPE or r["size"] == "solids"


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

Z_TOP = Z0 + 2 * SHELL_T + BED_L                          # bed top-head top face
EMBED = 12.0                                              # root laps the shell wall this far


def horizontal(s, face, y_root, z):
    """Root-anchor a +Z stub onto a -Y/+Y face: rotate, then place the root plane."""
    s = s.rotate((0, 0, 0), (1, 0, 0), 90 if face == "-Y" else -90)
    return s.translate((0, y_root, z))


layout = {}
noz, drawn, n_drawn = None, {}, 0
for (face, h), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: r["tag"])
    for r in [x for x in rows if not is_piped(x)]:
        # non-piped row: the power terminal (cable schedule X-ELS-06) is electrical,
        # not piped - carried verbatim, not drawn (no STEP/BOM/geometry change)
        drawn[r["tag"]] = {"style": "carried", "dn": r["size"], "face": r["face"],
                           "height_mm": r["height_mm"],
                           "schedule_rating": r["rating"], "service": r["service"],
                           "note": "power terminal (cable schedule X-ELS-06, AQS-ELEC-010): "
                                   "electrical, not piped - carried verbatim, not drawn"}
    for i, r in enumerate(x for x in rows if is_piped(x)):
        tag, dnl = r["tag"], r["size"]
        dnl_hw = "DN15" if dnl == "solids" else dnl
        od = od_of(r)
        n_drawn += 1
        bi = i % N_BEDS
        dx = (i // N_BEDS) * 130.0 * (1 if i % 2 else -1)
        bx = bed_x[bi]
        note = "atmospheric hose joint on the bed shell (node relief basis: API 2000 open vent)"
        if face == "bottom":                              # N9: bed 1 drain, tip at its 50 datum
            s = rod(dn.pipe_od("DN15") / 2, (bed_x[0] + 180.0, CY, 50.0), "Z",
                    Z0 - 50.0 + 6.0)                      # laps the bottom head 6
            y_root, zz = None, 50.0
            note = "drain beside the bed 1 pedestal, tip at the 50 datum, into the bottom head"
        elif face == "top":                                 # N10: vent standpipe to the 2000 datum
            s = rod(dn.pipe_od("DN15") / 2, (bed_x[0], CY, Z_TOP - 5.0), "Z", 2000.0 - Z_TOP + 5.0)
            y_root, zz = None, 2000.0
            note = ("vent standpipe on the bed 1 top head to the 2000 mm schedule datum "
                    "(API 2000 open vent)")
        else:
            if Z0 - 5.0 <= h - od / 2 and h + od / 2 <= Z_TOP + 5.0:
                chord = math.sqrt(max(R_BED * R_BED - dx * dx, (R_BED * 0.5) ** 2))
                y_root = CY + (-chord + EMBED if face == "-Y" else chord - EMBED)
            else:                                          # frame row (z 160): through the plinth
                y_root = 30.0 if face == "-Y" else SKID_W - 30.0
                note = ("frame-level row: the schedule datum sits below the bed shells; drawn "
                        "through the base plinth")
            if dnl != "solids":
                s = horizontal(nozzles.hose_barb(hose_id(dnl_hw), Hose[dnl_hw],
                                                 root_od=dn.pipe_od(dnl_hw)), face, y_root, h)
            else:
                s = horizontal(nozzles.stub("DN15", 50.0), face, y_root, h)
                note = SOLIDS_NOTE
            zz = h
        s = s.translate((bx + dx, 0.0, 0.0)) if face not in ("bottom", "top") else s
        noz = s if noz is None else noz.union(s)
        layout[tag] = {"bed": (bi + 1) if face in ("-Y", "+Y") else None, "x": round(bx + dx, 1),
                       "z": zz}
        drawn[tag] = {"style": "solids" if dnl == "solids" else "hose",
                      "dn": dnl_hw if dnl != "solids" else "DN15",
                      "face": face, "height_mm": h, **layout[tag],
                      "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="CRYO_ASU")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "cryo_asu.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "cryo_asu.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
# The X-PAR-04 gate requires the cad/stl box to equal the node size_mm to 1 mm, so the
# cad/stl solid is the in-envelope subset of the build (AL_POT convention): everything
# physically inside the M0 study registry box. The full build - which leaves the study
# box on x and y at the design bed diameter - lives in export/ and the STEP, and the
# misfit is reported on the tracker board (AQS-PLAN-006 rule 3), nothing resized.
env = cq.Workplane("XY").box(*[float(v) for v in P["size_mm"]], centered=False).val()
in_env = solid.intersect(env)
in_env.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "CRYO_ASU.stl"),
                              tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
size = [float(v) for v in (P["size_mm"] or [0, 0, 0])]
overshoot = [d for d, s in zip(dims, size) if d > s + 1.0]
v_sorb = parts["sorbent"].val().Volume() / 1e9
mass = {k: round(v.val().Volume() * RHO["316L"] / 1e9, 1)
        for k, v in parts.items() if k != "sorbent"}
report = {
    "bbox_mm": dims, "inside_size_mm": not overshoot,
    "size_mm": P["size_mm"], "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "misfit_to_report": bool(overshoot),
    "misfit_note": f"beds at the node design diameter ({BED_D:.1f} mm) cannot fit the M0 study "
    f"registry box [{size[0]:g}, {size[1]:g}, {size[2]:g}] (params size_note); reported per "
    "AQS-PLAN-006 rule 3, nothing resized",
    "beds": {"count": N_BEDS, "bed_D_mm": BED_D, "bed_L_mm": BED_L, "shell_t_mm": SHELL_T,
             "grid_t_mm": GRID_T, "axis_z_mm": [Z0, Z0 + 2 * SHELL_T + BED_L],
             "x_mm": [round(b, 1) for b in bed_x],
             "basis": "node design block: beds/bed_D_mm/bed_L_mm (AQS-PAR-001 sizing)"},
    "sorbent": {"kg_per_bed": SORBENT_KG, "bulk_density_kg_m3": RHO["13X"],
                "drawn_m3_total": round(v_sorb, 3),
                "kg_drawn_total": round(parts["sorbent"].val().Volume() * 1e-9 * RHO["13X"], 1),
                "kg_booked_total": round(N_BEDS * SORBENT_KG, 1),
                "note": "13X bed drawn as a solid between the support grids; the drawn charge is "
                "capped by the bed length at the 700 kg/m3 study bulk density (636 kg/m3 would "
                "fill it) - vendor TDS at order, WORK_ORDER W12"},
    "machinery": {"co2_comp_kW": D["co2_comp_kW"], "co2_chill_kW": D["co2_chill_kW"],
                  "getter_kW": D["getter_kW"], "regen_kW": D["regen_kW"], "blower_kW": D["blower_kW"],
                  "note": "purchased envelopes and interfaces (AQS-PLAN-006 rule 6), ratings from "
                  "the node design; the internals row says two-stage, the design block comp_stages "
                  "4 - the named two-stage machine is drawn, the staging is a hold (W12)"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "hose barbs on the bed shells and frame per the atmospheric relief basis "
    "(API 2000, A-M-155); solids rows DN15 labeled bore not calculated; schedule rating column "
    "(Class 150) carried verbatim as text; the N17 power terminal (cable schedule X-ELS-06, "
    "AQS-ELEC-010) is electrical, not piped - carried verbatim in this report, not drawn",
    "part_mass_kg": mass,
    "sorbent_mass_kg": round(parts["sorbent"].val().Volume() * 1e-9 * RHO["13X"], 1),
    "cad_stl_scope": "in-envelope subset of the build, metres (X-PAR-04 gate: the cad/stl box "
    "equals the node size_mm; the full build lives in export/ and the STEP)",
    "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"TSA bed set: {N_BEDS} shells D {BED_D:g} x {BED_L:g} mm, t {SHELL_T:g}, flat heads, "
          f"support grids top and bottom, on pedestals", N_BEDS, "316L", mass["beds"], "make",
     f"node design block (bed_D_mm {BED_D:.1f}, bed_L_mm {BED_L:.1f}); duty section 3 316L, "
     "CA 0 mm; shell t 6 is the house plate convention, study (WORK_ORDER W12)"],
    ["2", f"13X molecular-sieve sorbent charge, {SORBENT_KG:g} kg per bed", N_BEDS,
     "13X molecular sieve, 4A grade", round(v_sorb * RHO["13X"], 1), "buy",
     "node design sorbent_kg_per_bed; bulk density 700 kg/m3 study; vendor TDS at order"],
    ["3", "Base frame: plinth 2460 x 560 x 200 with fork slots (modeled as its solid envelope; "
          "fabricated as a welded frame)", 1, "316L",
     mass["frame"], "make", "duty section 3 (no carbon steel); CA 0 mm; study section sizes; "
     "carries the z 160 frame-level schedule rows"],
    ["4", "CO2 two-stage compressor + condenser/chiller envelopes", 1, "purchase item", "", "buy",
     f"node design co2_comp_kW {D['co2_comp_kW']:.3f}, co2_chill_kW {D['co2_chill_kW']:.3f}; "
     "internals row two-stage vs design comp_stages 4 - staging is a named hold; drawn as "
     "envelope and interface (AQS-PLAN-006 rule 6)"],
    ["5", "Heated Ar getter cartridge", 1, "purchase item", "", "buy",
     f"node design getter_kW {D['getter_kW']:.3f}; noble-gas inventories pass through "
     "(node internals row)"],
    ["6", f"Nozzle set per docs-authority/nozzles/CRYO_ASU.csv: barbs and stubs, "
          f"{sum(1 for r in schedule if r['size'] == 'solids')} solids rows at DN15 (bore not "
          "calculated)", n_drawn, "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; the N17 power terminal (cable schedule X-ELS-06) "
     "is electrical, not piped - carried in check.json, not drawn; atmospheric per the API 2000 "
     "relief basis; vent datum clamped to the bed 1 top head (W12); barb profile a study "
     "proportion"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 x 40", fasteners.grade_for("316L"), 2 * 4 * N_BEDS,
     "bed pedestals to the base frame (4 per bed)",
     "A4-70 on 316L per the plan grade rule; study count, torque per the supplier rule"],
    [None, "M10 x 30 wedge anchor", fasteners.grade_for("316L"), 8,
     "base frame to the slab", "plan grade rule; seismic anchorage per the frame check task"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["layout"] = {
    "frame": f"skid frame: x along 2450, y across 560, z up; beds at x {CX0:.1f} + "
             f"{BED_PITCH:.1f}k on pedestals, purchased machinery row at x 1700..2440",
    "bed_axis_z_mm": [Z0, Z0 + 2 * SHELL_T + BED_L],
    "nozzle_spread": "inlets land on the bed shells' -Y side, outlets on +Y, distributed across "
                     "the beds in tag order (second row per bed offset 130 mm); the z 160 rows "
                     "land on the base frame; per-tag positions in check.nozzles_drawn",
    "vent": "schedule datum 2000 mm predates the TSA layout; drawn at the bed 1 top head - "
            "named hold (WORK_ORDER W12)",
    "hardware_idiom": "hose hardware laps the shell or frame so every union fuses; the build "
                      "leaves the M0 study registry box on x and y and the misfit is reported "
                      "(AQS-PLAN-006 rule 3)",
}
p["study"] = {
    "shell_t_mm": SHELL_T, "grid_t_mm": GRID_T, "sorbent_bulk_density_kg_m3": RHO["13X"],
    "note": "study values not stated by any authority (AQS-PLAN-006 W6 needs a thickness; the "
            "duty states only 316L and CA 0 mm)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "sorbent_mass_kg",
                                         "part_mass_kg")}))
