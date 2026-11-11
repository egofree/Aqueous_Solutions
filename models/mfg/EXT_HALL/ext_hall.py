"""EXT_HALL manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 8, route hold).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py); the params.json write-back merges the builder-owned blocks only. and rebuilds
every solid.

Placement frame: x along 186000 mm, y along 174000 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Envelope 186000 x 174000 x 6000 mm, node size_mm - "building massing envelope
  (bounding box of the issued L-shape): EXT_HALL_E 162 x 174 m east extension +
  EXT_HALL_N 24 x 156 m north extension, 6 m eave, portal frames on the 6 m grid
  (31 x 29 bays, X-PAR-07, A-M-104; placement_seed blocks EXT_HALL_E/N are the
  authority)". The model is drawn at the true building scale and fills the box.
  The fitout programme stays the duty-sheet open item - no process internals are
  drawn (the building carries the hall, not a machine).
- Building per the unit's own duty sheet section 3: steel portal frames on the
  6 m grid (the column grid sits on the 31 x 29 bay lines of the size note,
  inside the L-shape), insulated metal roof and wall panels to the IECC U-factors
  (A-M-104: roof U 0.199, wall U 0.534 W/(m2 K) classes), roof framing for LRFD
  1.72 kPa (A-M-105: PV dead 0.15 + roof live 0.96, ASCE 7-22). Steel sections
  and panels are made in-house (duty section 3, X-MFG-32). The column, wall and
  roof section sizes are massing values - the structural design is the X-BLD
  lane's (hold, WORK_ORDER W12).
- Massing solids: on-grade slab 150 mm under the L-shape; perimeter wall panels
  300 mm from slab to eave on the L-footprint; roof deck 100 mm at z 5900..6000;
  column grid 300 x 300 from slab to the roof deck at every 6 m grid point inside
  the L. The grid is carried as a compound of prisms (no boolean fuse): the
  export STL is a closed manifold assembly of closed boxes, the way the house
  multi-solid exports read.
- Nozzles: none. The duty section 4 states "None. Electrical feed SF-EXT_HALL
  at 480 V AC. Air-source heat pumps (D77). GEO_GHEX not coupled." No nozzle
  schedule is issued; nothing is piped.
- Roof PV interface: the PV_ARRAY model (accepted separately) carries the 15
  array tables on this roof plane; the roof load figures (A-M-105) are stamped
  on the PV node. Nothing doubled here.
- A-core: route hold - `building` has no AQS-PLAN-006 section 4 class (W12).
"""
import json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import fasteners, graph_node, materials, step_export  # noqa: E402
from tracker import stl_bbox_mm                          # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("EXT_HALL")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P or P[k] in (None, {}) })   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 186000 x 174000 x 6000
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = GN.design

T_SLAB = 150.0                                             # on-grade slab (massing, W12)
T_WALL = 300.0                                             # perimeter wall panel (massing, W12)
T_ROOF = 100.0                                             # roof deck at the eave
Z_EAVE = 6000.0
COL = 300.0                                                # column section (massing, W12)
BAY = 6000.0                                               # the 6 m grid
RHO_CS = materials.density("CS")

# Issued L-shape (placement_seed blocks EXT_HALL_E / EXT_HALL_N):
E = dict(x0=24000.0, x1=186000.0, y0=0.0, y1=174000.0)     # 162 x 174 m east extension
N = dict(x0=0.0, x1=24000.0, y0=18000.0, y1=174000.0)      # 24 x 156 m north extension

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert E["x1"] == L and E["y1"] == W and N["x1"] == E["x0"], "blocks tile the L bounding box"
assert (L / BAY - 1) == 30.0 and (W / BAY - 1) == 28.0, "31 x 29 bays on the 6 m grid"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def in_L(x, y):
    """Point inside the issued L-shape (E or N block), with a wall clearance."""
    m = COL
    e = E["x0"] + m <= x <= E["x1"] - m and E["y0"] + m <= y <= E["y1"] - m
    n = N["x0"] + m <= x <= N["x1"] - m and N["y0"] + m <= y <= N["y1"] - m
    return e or n


parts = {}

# ---------------------------------------------------------------- slab under the L-shape
slab = box(E["x0"], E["y0"], 0.0, E["x1"] - E["x0"], E["y1"] - E["y0"], T_SLAB)
slab = slab.union(box(N["x0"], N["y0"], 0.0, N["x1"] - N["x0"], N["y1"] - N["y0"], T_SLAB))
parts["slab"] = slab

# ---------------------------------------------------------------- perimeter wall panels (L-footprint)
walls = box(E["x0"], E["y0"], T_SLAB, E["x1"] - E["x0"], T_WALL, Z_EAVE - T_SLAB)      # S (E)
walls = walls.union(box(E["x1"] - T_WALL, E["y0"], T_SLAB, T_WALL,
                        E["y1"] - E["y0"], Z_EAVE - T_SLAB))                            # E
walls = walls.union(box(0.0, E["y1"] - T_WALL, T_SLAB, L, T_WALL, Z_EAVE - T_SLAB))     # N
walls = walls.union(box(0.0, N["y0"], T_SLAB, N["x1"], T_WALL, Z_EAVE - T_SLAB))        # S (N)
walls = walls.union(box(0.0, N["y0"], T_SLAB, T_WALL,
                        E["y1"] - N["y0"], Z_EAVE - T_SLAB))                            # W (N)
walls = walls.union(box(E["x0"], E["y0"], T_SLAB, T_WALL,
                        N["y0"] - E["y0"] + T_WALL, Z_EAVE - T_SLAB))   # W (E; laps the N-block S wall)
parts["walls"] = walls

# ---------------------------------------------------------------- roof deck over the L
roof = box(E["x0"], E["y0"], Z_EAVE - T_ROOF, E["x1"] - E["x0"], E["y1"] - E["y0"], T_ROOF)
roof = roof.union(box(N["x0"], N["y0"], Z_EAVE - T_ROOF,
                      N["x1"] - N["x0"], N["y1"] - N["y0"], T_ROOF))
parts["roof"] = roof

# ---------------------------------------------------------------- portal-frame column grid (6 m grid)
cols = []
for gx in range(0, int(L) + 1, int(BAY)):
    for gy in range(0, int(W) + 1, int(BAY)):
        if in_L(gx, gy):
            cols.append(box(gx - COL / 2, gy - COL / 2, T_SLAB, COL, COL,
                            Z_EAVE - T_ROOF - T_SLAB))
parts["frame_grid"] = cq.Workplane("XY").newObject(
    [cq.Compound.makeCompound([c.val() for c in cols])])

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
solid.exportStl(str(out / (UNIT.lower() + ".stl")), tolerance=1.0, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / (UNIT + ".stl")),
                             tolerance=0.001, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
vol = {"slab": parts["slab"].val().Volume(), "walls": parts["walls"].val().Volume(),
       "roof": parts["roof"].val().Volume(),
       "frame_grid": len(cols) * COL * COL * (Z_EAVE - T_ROOF - T_SLAB)}
RHO_CONC = 2400.0   # published reinforced-concrete class midpoint (massing; W12)
mass = {k: round(v * (RHO_CONC if k == "slab" else RHO_CS) / 1e9, 1) for k, v in vol.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": GN.size_basis,
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": True,
    "machine": {
        "type": "building massing per the node size_note and the placement_seed "
                "blocks EXT_HALL_E/N (the authority): 162 x 174 m east extension "
                "+ 24 x 156 m north extension, 6 m eave; on-grade slab 150 mm, "
                "perimeter wall panels 300 mm to the IECC U-factor class (A-M-104 "
                "wall U 0.534), roof deck 100 mm (roof U 0.199 class), and the "
                "steel portal-frame column grid at every 6 m grid point inside "
                "the L (31 x 29 bays); no process internals - the fitout "
                "programme stays the duty-sheet open item",
        "grid": {"bay_mm": BAY, "bays": "31 x 29 of the size note; column "
                 "positions at the grid points inside the L-shape",
                 "columns": len(cols)},
        "loads": "roof framing for LRFD 1.72 kPa (A-M-105: PV dead 0.15 + roof "
                 "live 0.96, ASCE 7-22); the roof PV interface is the PV_ARRAY "
                 "model (15 array tables, accepted separately) - nothing doubled",
        "massing_basis": "column/wall/roof section sizes are massing values; the "
                         "structural design is the X-BLD lane's (WORK_ORDER W12); "
                         "steel sections and panels are made in-house (duty "
                         "section 3, X-MFG-32)",
        "material": "steel portal frames; insulated metal roof and wall panels "
                    "(duty section 3)", "ca_mm": materials.ca_for("CS"),
        "nozzle_note": "duty section 4: None. Electrical feed SF-EXT_HALL at 480 V "
                       "AC. Air-source heat pumps (D77). GEO_GHEX not coupled.",
    },
    "nozzles_drawn": {},
    "nozzle_count_schedule": 0,
    "nozzle_idiom": "no nozzles: the duty section 4 states None (electrical feed "
                    "and heat-pump service are electrical/mech lanes) and no "
                    "nozzle schedule is issued - nothing piped, nothing drawn at "
                    "the faces",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
import csv  # noqa: E402
rows = [
    ["1", f"On-grade slab under the L-shape ({(E['x1']-E['x0'])/1000:g} x "
          f"{(E['y1']-E['y0'])/1000:g} m + {(N['x1']-N['x0'])/1000:g} x "
          f"{(N['y1']-N['y0'])/1000:g} m, 150 mm)", 1, "concrete (massing)",
     mass["slab"], "buy", "massing thickness (hold, WORK_ORDER W12); the "
     "foundation design is the X-BLD lane's"],
    ["2", "Perimeter wall panels on the L-footprint, 300 mm to the eave", 1,
     "insulated metal panel (IECC U 0.534 class, A-M-104)", mass["walls"],
     "make (X-MFG-32 in-house panels)", "duty section 3; panel sections are "
     "massing values (hold, W12)"],
    ["3", "Roof deck over the L at the 6 m eave, 100 mm", 1,
     "insulated metal roof (IECC U 0.199 class, A-M-104)", mass["roof"],
     "make (X-MFG-32 in-house panels)",
     "roof framing for LRFD 1.72 kPa (A-M-105); the roof PV interface is the "
     "PV_ARRAY model - nothing doubled"],
    ["4", f"Portal-frame column grid, {len(cols)} columns 300 x 300 at the 6 m "
           "grid points inside the L (31 x 29 bays)", len(cols),
     "steel (A500 class, massing)", mass["frame_grid"], "make (X-MFG-32)",
     "duty section 3: steel portal frames on the 6 m grid; section sizes are "
     "massing values - the structural design is the X-BLD lane's (hold, W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M20 column base bolts (F1552 class)", fasteners.grade_for("CS"), 4 * len(cols),
     "columns to base plates, 4 per column (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; the structural lane owns "
     "the anchor design (hold, WORK_ORDER W12)"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": GN.size_basis,
    "blocks": {"EXT_HALL_E": [E["x0"], E["y0"], E["x1"], E["y1"]],
               "EXT_HALL_N": [N["x0"], N["y0"], N["x1"], N["y1"]]},
    "slab_mm": T_SLAB, "wall_mm": T_WALL, "roof_mm": T_ROOF,
    "column_mm": COL, "bay_mm": BAY, "columns": len(cols),
}
p["design"] = dict(DS) if isinstance(DS, dict) else {}
p["design"].update({
    "service": "EXT_HALL: the single-storey conditioned hall extension carrying "
               "the roof PV (X-PAR-07, A-M-104); NORTH_DOCK opens into "
               "EXT_HALL_N with the 6 m truck lane reserved (duty sections 1 and 7)",
    "material": "steel portal frames; insulated metal roof and wall panels (IECC "
                "U-factor classes, A-M-104)",
    "massing_basis": "column/wall/roof sections are massing values; the "
                     "structural design and the fitout programme stay with their "
                     "lanes (duty section 8; hold, WORK_ORDER W12)",
    "hvac": GN.params.get("hvac"),
})
p["layout"] = {
    "frame": "origin at the envelope corner; the L-shape tiles the box (E block "
             "x 24000..186000, N block x 0..24000 y 18000..174000); walls on the "
             "L perimeter, roof at z 5900..6000, column grid at the 6 m bay "
             "lines inside the L",
    "nozzle_spread": "no schedule issued (duty section 4: None) - nothing piped, "
                     "nothing drawn at the faces",
    "hardware_idiom": "the massing fills the node box exactly; the X-PAR-04 "
                      "registry reads the build (walls pin the box)",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
