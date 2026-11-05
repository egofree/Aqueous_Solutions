"""SI_REDUCE manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 1200 mm, y along 1000 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1200 x 1000 x 1600 mm, node size_mm ("graphite hot-face furnace (the
  issued sec3 selection) at the batch class"). The build stays inside it; the retort
  does not fill it (the batch shaft is sized to the 1.8 kg/d Si draw, not to the box).
- Machine per the unit's own duty section 3 lining stack (X-MAT-22; SCHACHT2004
  ch. 8 carbonaceous hot faces; CRC_SI the element benchmark for the reduction duty
  class): a vertical carbothermic reduction retort in the Kroll-class idiom shared
  with the AQS-DUTY-072 pot-cell lineage (TI_CELL train) - mild-steel casing with
  alumina brick backup and a graphite hot face; the hot face stays dry (M7). Shell
  radii are study values sized to the batch class; no authority states a bore or a
  wall (holds, WORK_ORDER W12).
- Charge handling per duty section 3 ("dry char and silica-class feed handling"):
  a charge hopper cone on the retort lid for the dry char/silica blend (design
  block: sio2_kgd 3.85 + char_kgd 1.924 per 1.8 kg/d Si). Product-tap hardware is
  not named on the node or duty - none drawn (W12).
- Heater envelope: the furnace power is the node continuous_kw 5.0 kW (the X-SPEC
  carbothermic study class at the 1.8 kg/d draw); the heater band is drawn as a
  purchased-class envelope per plan rule 6 with the node rating named. The duty
  loop SI_REDUCETE-01 (temperature trip, AQS-CTL-001) is control hardware; its
  sensor circuit is not modeled (W12, IND_MELT loop precedent).
- Nozzles: none. The duty section 4 states "no piped process connection on the
  graph ... no nozzle schedule is issued yet"; the CHAR_TO_SI edge is a solids
  feed with no kg/d rate. Nothing is piped; nothing is drawn at the faces.
- A-core structure: plinth and anchor frame per AQS-MOD-002 dry service; 8 slab
  anchors in fasteners.csv. Route hold: `furnace` has no section 4 class (W12) -
  the IND_MELT precedent carries the acceptance A-core with the route hold named.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import fasteners, graph_node, materials                      # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("SI_REDUCE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1200 x 1000 x 1600
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
CAS_OD, CAS_WALL = 700.0, 6.0                              # mild-steel casing (study, W12)
BRICK_T = 60.0                                             # alumina brick backup (study, W12)
FACE_T = 40.0                                              # graphite hot face (study, W12)
CAS_Z0, CAS_Z1 = 0.0, 1260.0                               # casing z span (laps the plinth)
LID_T = 20.0
HOP_R0, HOP_R1 = 240.0, 80.0
HOP_H = 280.0                                              # hopper cone (study, W12); the
HATCH_H = 40.0                                             # lid stack tops at the envelope
# 1600 datum so the build pins the X-PAR-04 registry box (feed handling per sec3)
HEAT_SIDE, HEAT_Z1 = 800.0, 700.0                          # heater band box envelope (5.0 kW set)
KW_SET = 5.0                                               # node continuous_kw
MAT_CAS = "CS"
MAT_FACE = "graphite"
CA_CAS = materials.ca_for(MAT_CAS, "dry furnace service")  # duty section 3: dry, non-hydrocarbon
RHO_CS = materials.density(MAT_CAS)
RHO_FACE = materials.density(MAT_FACE)                     # 1550, lib table
RHO_BRICK = 2600.0         # published alumina brick class midpoint; the brick is a buy-row
# liner charge - the supplier TDS governs at order (W12)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert CAS_Z1 + LID_T + HOP_H + HATCH_H == H, "lid stack tops at the envelope datum"
assert CAS_OD + 2 * 50.0 <= min(L, W), "casing clears the envelope walls"
R_CAS_I = CAS_OD / 2 - CAS_WALL
R_BRICK_I = R_CAS_I - BRICK_T
R_FACE_I = R_BRICK_I - FACE_T
CX, CY = L / 2, W / 2


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def ring_z(r_out, r_in, z0, z1):
    return (cq.Workplane("XY", origin=(CX, CY, z0)).circle(r_out).circle(r_in)
            .extrude(z1 - z0))


parts = {}

# ---------------------------------------------------------------- plinth + anchor frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)

# ---------------------------------------------------------------- retort shell: casing + brick + hot face
casing = ring_z(CAS_OD / 2, R_CAS_I, CAS_Z0, CAS_Z1)
casing = casing.union(cq.Workplane("XY", origin=(CX, CY, CAS_Z1))
                      .circle(CAS_OD / 2).extrude(LID_T))          # top head (lid plate)
casing = casing.union(cq.Workplane("XY", origin=(CX, CY, 0))
                      .circle(CAS_OD / 2).extrude(T_PLINTH + 40.0))  # base head laps plinth
parts["casing"] = casing
parts["brick_backup"] = ring_z(R_CAS_I, R_BRICK_I, T_PLINTH + 40.0,
                               CAS_Z1 - LID_T - 40.0)              # between the heads
parts["hot_face"] = ring_z(R_BRICK_I, R_FACE_I, T_PLINTH + 40.0,
                           CAS_Z1 - LID_T - 40.0)                  # graphite, dry (M7)
parts["bore"] = cq.Workplane("XY", origin=(CX, CY, T_PLINTH + 40.0)) \
    .circle(R_FACE_I).extrude(10.0)                                # hearth floor disc

# ---------------------------------------------------------------- clamp ring on the lid joint
parts["clamp_ring"] = ring_z(CAS_OD / 2 + 20.0, R_CAS_I, CAS_Z1 + LID_T,
                             CAS_Z1 + LID_T + 30.0).translate((0, 0, -30.0))

# ---------------------------------------------------------------- charge hopper (dry char + silica feed)
hop = (cq.Workplane("XY", origin=(CX, CY, CAS_Z1 + LID_T))
       .circle(HOP_R0).workplane(offset=HOP_H).circle(HOP_R1).loft(ruled=True))
hop = hop.union(cq.Workplane("XY", origin=(CX - HOP_R1, CY - 60.0, CAS_Z1 + LID_T + HOP_H))
                .box(2 * HOP_R1, 120.0, HATCH_H, centered=False))   # charge hatch box
parts["hopper"] = hop

# ---------------------------------------------------------------- heater band envelope (purchased, 5.0 kW)
parts["heater_band"] = box(CX - HEAT_SIDE / 2, CY - HEAT_SIDE / 2, T_PLINTH,
                           HEAT_SIDE, HEAT_SIDE, HEAT_Z1 - T_PLINTH)

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

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
RHO_OF = {"plinth": RHO_CS, "casing": RHO_CS, "heater_band": RHO_CS,
          "brick_backup": RHO_BRICK, "hot_face": RHO_FACE, "bore": RHO_FACE}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_CS) / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "carbothermic silicon reduction retort per the duty section 3 "
                "lining stack (X-MAT-22; SCHACHT2004 ch. 8; CRC_SI benchmark): "
                f"mild-steel casing OD {CAS_OD:g} (wall {CAS_WALL:g}, study) with "
                f"alumina brick backup {BRICK_T:g} mm and a graphite hot face "
                f"{FACE_T:g} mm (dry, M7) in the Kroll-class retort idiom shared "
                "with the AQS-DUTY-072 pot-cell lineage (TI_CELL train); charge "
                "hopper on the lid for the dry char/silica blend; heater band "
                "envelope (node continuous 5.0 kW)",
        "lining": {"casing_od_mm": CAS_OD, "wall_mm": CAS_WALL,
                   "brick_mm": BRICK_T, "hot_face_mm": FACE_T,
                   "bore_mm": 2 * R_FACE_I,
                   "basis": "study radii - no authority states a bore or a wall "
                            "(WORK_ORDER W12)"},
        "duty": DS,
        "heater": {"kw": KW_SET,
                   "basis": "node continuous_kw 5.0 kW (X-SPEC carbothermic study "
                            "class at the 1.8 kg/d Si draw); heater band drawn as "
                            "its envelope per plan rule 6"},
        "feed_handling": "charge hopper cone on the lid (duty section 3: dry char "
                         "and silica-class feed handling; design sio2_kgd 3.85 + "
                         "char_kgd 1.924 per si_kgd 1.8)",
        "not_drawn": {"product_tap": "no tap hardware is named on the node or duty "
                                     "(WORK_ORDER W12)",
                      "loop": "SI_REDUCETE-01 temperature loop (AQS-CTL-001) is "
                              "control hardware; sensor circuit not modeled "
                              "(IND_MELT loop precedent, W12)"},
        "structure": "plinth + anchor frame per AQS-MOD-002 dry service; 8 slab "
                     "anchors (fasteners.csv)",
        "material": MAT_FACE + " hot face, alumina brick backup, mild-steel casing "
                    "(duty section 3)",
        "ca_mm": CA_CAS,
        "ca_basis": "duty section 3: the hot face stays dry (M7); dry, "
                    "non-hydrocarbon furnace service - CA 0 mm (AQS-STD-001)",
    },
    "nozzles_drawn": {},
    "nozzle_count_schedule": 0,
    "nozzle_idiom": "no nozzles: the duty section 4 states no piped process "
                    "connection on the graph and no nozzle schedule is issued yet; "
                    "the CHAR_TO_SI feed is a solids edge with no kg/d rate - "
                    "nothing piped, nothing drawn at the faces",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (anchor frame)", 1,
     "carbon steel (ASTM A500)", mass["plinth"], "make",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Retort casing OD {CAS_OD:g} (wall {CAS_WALL:g}, study) with base head, "
           "lid plate and clamp ring", 1, "mild steel (duty section 3)",
     mass["casing"] + mass["clamp_ring"], "make",
     "shell radii are study values (hold, WORK_ORDER W12); CA 0 mm - dry furnace "
     "service (AQS-STD-001)"],
    ["3", f"Alumina brick backup {BRICK_T:g} mm ring between the heads", 1,
     "alumina brick (buy-row liner charge; supplier TDS governs)", mass["brick_backup"],
     "buy", "duty section 3 (X-MAT-22, SCHACHT2004 ch. 8); density is the published "
     "alumina brick class midpoint (study)"],
    ["4", f"Graphite hot face {FACE_T:g} mm ring + hearth floor disc (dry, M7)", 1,
     "graphite (duty section 3)", mass["hot_face"] + mass["bore"], "make",
     "duty section 3: graphite hot face, dry; CA 0 mm (AQS-STD-001 graphite rule); "
     "the silicon-carbide hot-face alternative is the duty alternative row (a "
     "process-change decision, not drawn)"],
    ["5", f"Charge hopper cone (R {HOP_R0:g} -> {HOP_R1:g} x {HOP_H:g}) with hatch box "
           "on the lid", 1, "mild steel", mass["hopper"], "make",
     "duty section 3 feed handling; hopper size is a study value (W12)"],
    ["6", "Heater band envelope around the heating zone", 1,
     "purchased heater set (envelope)", mass["heater_band"], "buy",
     "node continuous_kw 5.0 kW (X-SPEC carbothermic study class); purchased per "
     "plan rule 6, rating from the node"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per side (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M12 lid clamp stud + nut", fasteners.grade_for("CS"), 8,
     "clamp ring to casing flange (count from the model)",
     "8.8 on carbon steel per the grade rule; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "retort": {"casing_od_mm": CAS_OD, "wall_mm": CAS_WALL, "brick_mm": BRICK_T,
               "hot_face_mm": FACE_T, "z_mm": [CAS_Z0, CAS_Z1],
               "pos_mm": [CX, CY]},
    "hopper_mm": {"r0": HOP_R0, "r1": HOP_R1, "h": HOP_H},
    "heater_band_mm": [CX - HEAT_SIDE / 2, CY - HEAT_SIDE / 2, HEAT_SIDE, HEAT_Z1],
}
p["design"] = dict(DS)
p["design"].update({
    "service": "SI_REDUCE: carbothermic silicon reduction for the PV cell line "
               "(SOLAR_PV_CELL draws 1.8 kg/d Si); dry hot face (duty sections 1 "
               "and 3)",
    "material": "graphite hot face, alumina brick backup, mild-steel casing",
    "ca_mm": CA_CAS,
    "material_basis": "duty section 3 (X-MAT-22; SCHACHT2004 ch. 8; CRC_SI): "
                      "construction issued at the lining level; the hot face stays "
                      "dry (M7)",
    "heater_kw": KW_SET,
    "purchased": "heater band set (plan rule 6 envelope, node continuous 5.0 kW); "
                 "alumina brick liner charge (buy)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; retort on the plinth centre "
             f"(x {CX:g}, y {CY:g}), casing z {CAS_Z0:g}..{CAS_Z1:g}, lid + "
             f"clamp ring + hopper to z {CAS_Z1 + LID_T + HOP_H + 40.0:g}; heater "
             "band box around the lower shaft",
    "supports": "plinth + base head lap + 8 slab anchors",
    "nozzle_spread": "no schedule issued (duty section 4): nothing piped, nothing "
                     "drawn at the envelope faces",
    "hardware_idiom": "shell layers lap volumetrically; nothing protrudes, bbox "
                      "inside the node envelope (the retort under-fills the box "
                      "by design - the batch class sets it, not the registry box)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
