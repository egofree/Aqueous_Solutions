"""REE_RECOVER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid.

Placement frame: x along 800 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 800 x 600 x 1400 mm, node size_mm: "bench campaign skid: demag oven +
  10 L leach reactor + filter + muffle on one frame (fume-hood class, MET_SYN row);
  A-M-433 X-END-02 rare-earth route (Q-013)". The node sizing block books the
  campaign (1.618 kg NdFeB, 0.585 kg REO, 10 L reactor, 0.3 kW). The build fills
  the box with the frame.
- Route hold: the node class is `precip`, which has no row in the AQS-PLAN-006
  section 4 route table - the tracker records the hold and the acceptance cell
  reads A-core (route hold). The skid work follows the F-MACH frame + F-VES vessel
  operations as the nearest families (W10).
- Frame: the AQS-MOD-002 fixed weld pattern (four posts, top and bottom rectangles)
  at the 800 x 600 bay with 80 x 5 tube - the lib frame builder - in 316L tube
  (wet-bench class: HCl fume service, duty section 3 thermoplastic/glass rule;
  layout choice, W12), plus two 316L shelves and a floor drip plate (layout, W12).
- Equipment (the duty section 2 sizing line names the set; each is drawn as its
  envelope and interface per plan rule 6 - internals stay with the maker):
  demag oven (> 320 C, 5 L class) and the 10 L glass-lined leach reactor (55 C
  jacket, stirrer, H2 vent) on the lower shelf; the PP-H vacuum filter and the
  900 C calcining muffle (316L shell, dry oxide service) on the upper shelf.
  Envelope dimensions are layout choices (holds, W12); the reactor envelope
  covers the 10 L charge.
- Material: duty section 3 (X-MAT-22): glass-lined reactor, PTFE transfer, PP-H
  filter wetted (no metal wetted part below 60 C); 316L muffle shell (dry oxide,
  900 C). The Hastelloy C-276 alternative (campaign above 60 C) is a named hold
  (W12). Frame and shelves 316L per the wet-bench class.
- Nozzles: all 2 rows of docs-authority/nozzles/REE_RECOVER.csv: N1 drain, open
  bore through the floor plate, flush at the envelope bottom (50 datum); N2 vent
  flush at the envelope top on the frame - the H2 vent the duty section 2 sizing
  line routes to the acid-scrubber header (its 800 datum predates the 1400 box -
  hold, W12). The schedule rating column (Class 150) is carried verbatim as
  text; no flange is drawn because no process pressure is stated (W4 110 % rule).
"""
import csv, json, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, frame, materials, nozzles    # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 800 x 600 x 1400, issued skid box
REV = P["graph_revision"]
UNIT = P["unit_id"]
# the campaign figures live in the graph node sizing block (the tracker W2 file does
# not carry it); read them from the authority, report-only
SIZ = {}
for _n in json.loads((HERE.parents[2] / "flow_graph" / "plant_flow_graph.json").read_text())["nodes"]:
    if _n.get("unit_id") == UNIT:
        SIZ = (_n.get("params") or {}).get("sizing") or {}
        break

SEC, WALL = 80.0, 5.0           # AQS-MOD-002 800-bay tube (lib frame standard)
T_PLATE = 10.0                  # shelf and floor plate thickness, layout (W12)
SHELF_Z = (170.0, 890.0)        # shelf undersides (layout, W12)
PX0, PY0 = 40.0, 40.0           # plate x/y origin (laps the posts)
PX1, PY1 = L - 40.0, W - 40.0

OVEN = (300.0, 300.0, 280.0)    # demag oven envelope (layout, W12)
REACT_D, REACT_H = 240.0, 380.0  # leach reactor envelope, covers the 10 L charge (W12)
FILT = (300.0, 220.0, 250.0)    # PP-H vacuum filter envelope (layout, W12)
MUF = (320.0, 280.0, 260.0)     # calcining muffle envelope, 316L shell (layout, W12)

RHO_316 = materials.density("316L")         # 8000
RHO_PP = materials.density("PP")            # 910 (PP-H class basis)
CA_316 = materials.ca_for("316L")           # 0.0
CA_PP = materials.ca_for("PP-H")            # 0.0

assert L == 800.0 and W == 600.0 and H == 1400.0, "REE_RECOVER node envelope changed"
assert REACT_H * 3.14159 * (REACT_D / 2) ** 2 / 1e9 >= 0.010, "reactor envelope must cover the 10 L charge"
assert SHELF_Z[1] + T_PLATE + max(FILT[2], MUF[2]) < H - SEC, "upper-shelf gear must clear the top rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- AQS-MOD-002 frame
parts["frame"] = frame.frame_members(L, W, H, SEC, WALL)

# ---------------------------------------------------------------- shelves + floor plate
shelf_a = box(PX0, PY0, SHELF_Z[0], PX1 - PX0, PY1 - PY0, T_PLATE)
shelf_b = box(PX0, PY0, SHELF_Z[1], PX1 - PX0, PY1 - PY0, T_PLATE)
floor = box(0.0, 0.0, 0.0, L, W, T_PLATE)
shelving = shelf_a.union(shelf_b).union(floor)
parts["shelving"] = shelving

# ---------------------------------------------------------------- equipment envelopes (plan rule 6)
SEAT = 2.0                       # equipment seat sink into the shelves, so unions fuse
oven = box(90.0, 90.0, SHELF_Z[0] + T_PLATE - SEAT, *OVEN)
parts["demag_oven"] = oven
reactor = (cq.Workplane("XY", origin=(560.0 - REACT_D / 2, 300.0 - REACT_D / 2,
                                                 SHELF_Z[0] + T_PLATE - SEAT))
           .circle(REACT_D / 2).extrude(REACT_H))
parts["leach_reactor"] = reactor
filt = box(90.0, 95.0, SHELF_Z[1] + T_PLATE - SEAT, *FILT)
parts["vacuum_filter"] = filt
muf = box(420.0, 110.0, SHELF_Z[1] + T_PLATE - SEAT, *MUF)
parts["calcining_muffle"] = muf

# ---------------------------------------------------------------- nozzles (schedule verbatim)
def tube(dnl, length):
    """An open-bore pipe tube along +Z from the origin plane (the HDR spool idiom)."""
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


schedule = [r for r in P["nozzles"]]
noz_pieces, drawn = [], {}
for r in schedule:
    tag, dnl, face0 = r["tag"], r["size"], r["face"]
    if face0 == "bottom":                      # N1 drain: through the floor plate
        s = tube(dnl, 60.0).translate((400.0, 300.0, 0.0))
        note = "drain, open bore through the floor plate, flush at the envelope bottom (50 datum)"
        z_d, x_d = 0.0, 400.0
    else:                                      # N2 vent: riser from the upper shelf to the top face
        s = tube(dnl, H - SHELF_Z[1] + 2.0).translate((400.0, 300.0, SHELF_Z[1] - 2.0))
        note = ("vent riser from the upper-shelf zone to the envelope top (the H2 "
                "vent to the acid-scrubber header, duty section 2 sizing); schedule "
                "datum 800 predates the 1400 box (hold, WORK_ORDER W12)")
        z_d, x_d = H, 400.0
    noz_pieces.append(s)
    drawn[tag] = {"style": "tube", "dn": dnl, "face": face0, "height_mm": r["height_mm"],
                  "drawn_height_mm": z_d, "x_mm": x_d, "schedule_rating": r["rating"],
                  "service": r["service"], "note": note}
# the pieces stay a compound; each roots in the frame or plates and is fused piecewise
parts["nozzles"] = cq.Workplane(obj=cq.Compound.makeCompound([p.val() for p in noz_pieces]))

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
frame_mass = frame.steel_mass(L, W, H, SEC, WALL)
mass = {
    "frame": round(frame_mass, 1),
    "shelving": round(shelving.val().Volume() * RHO_316 / 1e9, 1),
    "demag_oven": round(oven.val().Volume() * RHO_316 / 1e9, 1),
    "leach_reactor": round(reactor.val().Volume() * RHO_316 / 1e9, 1),
    "vacuum_filter": round(filt.val().Volume() * RHO_PP / 1e9, 1),
    "calcining_muffle": round(muf.val().Volume() * RHO_316 / 1e9, 1),
    "nozzles": round(sum(p.val().Volume() for p in noz_pieces) * RHO_316 / 1e9, 2),
}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "bench campaign skid box (node size_note: demag oven + 10 L leach "
    "reactor + filter + muffle on one frame, fume-hood class)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "route_hold": "the node class is precip, which has no row in the AQS-PLAN-006 "
    "section 4 route table - the tracker records the hold; the skid work follows "
    "the F-MACH frame and F-VES vessel operations as the nearest families (WORK_ORDER W10)",
    "campaign": {
        "basis": SIZ.get("basis", "node sizing block"),
        "campaign_kg": SIZ.get("campaign_kg"), "reo_kg": SIZ.get("reo_kg_campaign"),
        "reactor_L": SIZ.get("reactor_L"), "power_kW": SIZ.get("power_kW"),
        "note": "figures reported from the node sizing block; nothing re-derived",
    },
    "equipment": {
        "basis": "plan rule 6: the duty section 2 sizing line names the set; each "
        "unit is drawn as its envelope and interface, internals stay with the maker",
        "demag_oven": {"envelope_mm": list(OVEN), "rating": "> 320 C demag, 5 L class "
                       "(duty section 2 sizing)", "maker_class": "enclosure maker TDS at order"},
        "leach_reactor": {"envelope_mm": [REACT_D, REACT_H], "rating": "10 L glass-lined "
                          "leach reactor, 55 C jacket, stirrer, H2 vent (duty section 2 "
                          "sizing); envelope covers the charge",
                          "maker_class": "glass-lined vessel maker TDS at order"},
        "vacuum_filter": {"envelope_mm": list(FILT), "rating": "vacuum filter, PP-H "
                          "wetted (duty section 3)", "maker_class": "filter maker TDS at order"},
        "calcining_muffle": {"envelope_mm": list(MUF), "rating": "900 C calcining "
                             "muffle, 2 L, 316L shell dry oxide (duty section 3)",
                             "maker_class": "furnace maker TDS at order"},
        "layout_note": "shelf and envelope positions are the registered layout choice "
        "(WORK_ORDER W12)",
    },
    "material": {"wetted": "glass-lined reactor, PTFE transfer, PP-H filter (duty "
                 "section 3, X-MAT-22; no metal wetted part below 60 C)",
                 "hot": "316L muffle shell, dry oxide at 900 C (duty section 3)",
                 "structure": "316L tube frame and shelves (wet-bench class, layout "
                 "choice, W12); CA 0 mm (AQS-STD-001 rules)",
                 "alt": "Hastelloy C-276 wetted parts if the campaign moves above "
                 "60 C - not required at the bench scale (named hold, W12)"},
    "open_items": ["no instrument loop yet (unit task 08) - no trip is specified",
                   "relief case study pending (unit task 07) - no set point claimed",
                   "nozzle elevations are schedule placeholders (unit tasks 02/06)"],
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube (lib/dn Sch 40 table), flush at the "
    "envelope bottom and top; the schedule rating column (Class 150) is carried "
    "verbatim as text, no flange drawn (W4 110 % rule: no process pressure stated)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"AQS-MOD-002 frame {L:g} x {W:g} x {H:g}, {SEC:g} x {WALL:g} tube, the "
          "fixed weld pattern", 1, "316L tube", mass["frame"], "make",
     "frame standard AQS-MOD-002 parameter set; 316L per the wet-bench class "
     "(HCl fume service; layout choice, WORK_ORDER W12); CA 0 mm (AQS-STD-001)"],
    ["2", f"Shelves and floor plate, {PX1 - PX0:g} x {PY1 - PY0:g} x {T_PLATE:g} "
          "and 800 x 600 x 10", 3, "316L plate", mass["shelving"], "make",
     "skid layout choice (WORK_ORDER W12); CA 0 mm (AQS-STD-001 316L rule)"],
    ["3", f"Demag oven envelope {OVEN[0]:g} x {OVEN[1]:g} x {OVEN[2]:g} (> 320 C, "
          "5 L class)", 1, "maker class", mass["demag_oven"], "buy",
     "plan rule 6: purchased item named with the rating from the duty section 2 "
     "sizing line; envelope and interface only, internals with the maker; the row "
     "mass is the envelope mass at the tabulated shell density - the maker TDS "
     "mass governs at order (WORK_ORDER W12)"],
    ["4", f"Glass-lined leach reactor envelope OD {REACT_D:g} x {REACT_H:g} (10 L, "
          "55 C jacket, stirrer, H2 vent)", 1, "glass-lined (maker class)",
     mass["leach_reactor"], "buy",
     "duty section 2 sizing / duty section 3; envelope covers the 10 L charge; "
     "wetted parts per the vessel maker TDS at order; the row mass is the "
     "envelope mass at the tabulated shell density (WORK_ORDER W12)"],
    ["5", f"PP-H vacuum filter envelope {FILT[0]:g} x {FILT[1]:g} x {FILT[2]:g}", 1,
     "PP-H (maker class)", mass["vacuum_filter"], "buy",
     "duty section 3: PP-H filter wetted; envelope only per plan rule 6; the "
     "row mass is the envelope mass at the PP-H table density (WORK_ORDER W12)"],
    ["6", f"Calcining muffle envelope {MUF[0]:g} x {MUF[1]:g} x {MUF[2]:g} (900 C, "
          "2 L, 316L shell)", 1, "316L (maker class)", mass["calcining_muffle"], "buy",
     "duty section 3: 316L muffle shell, dry oxide 900 C; envelope only per plan "
     "rule 6; the row mass is the envelope mass at the 316L table density "
     "(WORK_ORDER W12)"],
    ["7", "Nozzle set per docs-authority/nozzles/REE_RECOVER.csv: 1 drain (through "
          "the floor plate), 1 vent at the envelope top (the H2 vent to the "
          "acid-scrubber header)", len(schedule), "316L tube (lib/dn Sch 40 table "
          "dims)", mass["nozzles"], "make",
     "schedule verbatim; no piped process connection on the graph yet - drain and "
     "vent utilities only (hold, WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("316L"), 4,
     "frame to slab, one per corner (count from the model)",
     "grade rule AQS-PLAN-006 W5: A4-70 on 316L; study length, confirmed at "
     "fabrication"],
    [None, "M8 hold-down bolt", fasteners.grade_for("316L"), 16,
     "equipment envelopes to the shelves, 4 per envelope (count from the model)",
     "A4-70 per house practice; study length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "bench campaign skid box (node size_note, fume-hood class MET_SYN row)",
    "frame": {"section": [SEC, WALL], "pattern": "AQS-MOD-002 fixed weld pattern"},
    "shelves_z_mm": [SHELF_Z[0] + T_PLATE, SHELF_Z[1] + T_PLATE],
}
p["design"] = {
    "duty": (P.get("design") or {}).get("service", "rare-earth magnet recovery batch campaign"),
    "campaign_kg": SIZ.get("campaign_kg"), "reo_kg_campaign": SIZ.get("reo_kg_campaign"),
    "reactor_L": SIZ.get("reactor_L"), "power_kW": SIZ.get("power_kW"),
    "mat": "glass-lined reactor, PTFE transfer, PP-H filter; 316L muffle shell; "
           "316L frame (duty section 3, X-MAT-22)",
    "ca_mm": CA_316,
    "internals": "equipment drawn as purchased envelopes per plan rule 6 (WORK_ORDER W12)",
    "route": "route hold: no AQS-PLAN-006 section 4 class for precip; F-MACH frame "
             "and F-VES vessel operations as the nearest families (WORK_ORDER W10)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; AQS-MOD-002 bay with the tube posts at "
             "the corners; shelves at z 180 and z 900; floor plate z 0..10",
    "equipment_zone": "demag oven and reactor on the lower shelf, filter and muffle "
                      "on the upper shelf; the vent take-off stands at the box top "
                      "over the shelf centreline",
    "nozzle_spread": "drain through the floor plate at x 400; vent flush at the top "
                     "face; per-tag positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
