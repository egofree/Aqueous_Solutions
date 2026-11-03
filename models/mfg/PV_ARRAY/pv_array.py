"""PV_ARRAY manufacturing model, AQS-PLAN-006 work order (M0 lane, tier 8, F-MACH).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (the M0 study registry box). The build
  fills it exactly: the four-post hold-down frame pins the box so the X-PAR-04
  envelope registry reads the build. The unit is drawn the way the accepted
  room-scale units are (WAFER_FAB bench precedent): a representative array-table
  section at the registry box, with the full array facts read from the node and
  reported - the array itself spans the roof planes (footprint_mm 210000 x
  138000, 15 array tables of 40293 x 43968 mm per the solver roof_close segment
  math, area_m2 26574, 6052 modules x 0.5 kW = nameplate 3026 kWp,
  roof_capacity_kWp 3029.5 class, mounting "roof only (X-PAR-07); ground field
  removed").
- Table and tilt per the node and its registers: low-tilt rows at GCR 0.6
  (A-M-103); the tilt is drawn about +X with the +Y edge raised - equator-facing,
  site north = +Y (the models/freecad heritage rule in params.py). The numeric
  tilt (10 deg drawn) is a study value: the driver's verification test is a
  PVWatts run at the roof tilt and azimuth (hold, W12). Module strips cover 60 %
  of the table plane (the GCR figure); modules are purchased envelopes per plan
  rule 6 (module_kw 0.5, pv_module_eff 0.19 STC, count 6052 from the node).
- Ballast and anchors per A-M-105 (roof_pv_dead_kPa 0.15: modules and ballasted
  racking): four ballast feet under the table rails (the A-MACH anchor drawn);
  the roof dead/live loads (service 1.11 / LRFD 1.716 kPa) are node figures.
  Array mass basis: struct_pv_kg_m2 17.0 kg/m2 (A-M-184) over the node area_m2
  = 451.8 t of modules and ballasted racking across the roof, reported here and
  not carried by the representative build.
- A-MACH: hold-down/guard frame + ballast anchors drawn; the frame pins the box.
- Nozzles: all 4 rows of docs-authority/nozzles/PV_ARRAY.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4 verbatim: "DN is copied from the edge and is not recalculated").
  N1 solar into the array (DN25) on -Y at z 160; N2 PV daily average (DN25) on
  +Y at z 600 - the electrical edges drawn as the schedule's tube rows with the
  conductor note carried (the duty inline rows read "Rating conductor. Not a
  hose"); N3 drain flush at the envelope bottom (50 datum); N4 vent flush at the
  envelope top (800 datum is the box top). The schedule rating column (Class
  150) carried verbatim as text.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles         # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]
DS = P.get("design") or {}

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
POST = 40.0                                                # hold-down/guard frame section
DECK_T = 20.0                                              # roof-plane segment deck
DECK = (POST + 4.0, POST + 4.0, T_PLINTH, L - 2 * POST - 8.0, W - 2 * POST - 8.0, DECK_T)
TILT_DEG = 10.0                                            # low-tilt rows (A-M-103); study (W12)
TILT = math.radians(TILT_DEG)
TAB_L, TAB_W = 860.0, 480.0                                # table section (box-scale rep)
TAB_CX, TAB_CY = L / 2, W / 2
GCR = 0.6                                                  # A-M-103 ground-cover ratio
N_STRIPS = 3                                               # module strips over 60 % of the plane
STRIP_T = 12.0                                             # module plane envelope thickness
FOOT = 80.0                                                # ballast foot section
FOOT_H = 240.0
MODULE_KW = 0.5                                            # node module_kw
MODULE_COUNT = 6052                                        # node count
ARRAY_M2 = 26574.0                                         # node area_m2 (table footprint)
KG_M2 = 17.0                                               # A-M-184 PV + ballasted racking

assert L == 1000.0 and W == 600.0 and H == 800.0, "PV_ARRAY node envelope changed"
assert abs(GCR - 0.6) < 1e-9 and N_STRIPS * (TAB_W * GCR / N_STRIPS) == TAB_W * GCR, "GCR coverage"
RISE = TAB_W * math.sin(TILT)
assert T_PLINTH + DECK_T + FOOT_H + RISE + 60.0 <= H, "tilted table stays under the rails"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + hold-down/guard frame
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
frame = None
for (fx, fy) in ((0.0, 0.0), (L - POST, 0.0), (0.0, W - POST), (L - POST, W - POST)):
    b = box(fx, fy, 0.0, POST, POST, H)
    frame = b if frame is None else frame.union(b)
for (rx, ry, dx, dy) in ((0.0, 0.0, L, POST), (0.0, W - POST, L, POST),
                         (0.0, 0.0, POST, W), (L - POST, 0.0, POST, W)):
    frame = frame.union(box(rx, ry, H - POST, dx, dy, POST))
parts["frame"] = frame

# ---------------------------------------------------------------- roof-plane segment deck
parts["roof_deck"] = box(*DECK)

# ---------------------------------------------------------------- table rails + ballast feet (A-M-105 class)
z0 = T_PLINTH + DECK_T
rails = box(TAB_CX - TAB_L / 2, TAB_CY - TAB_W / 2 + 40.0, z0 + FOOT_H,
            TAB_L, 60.0, 60.0)
rails = rails.union(box(TAB_CX - TAB_L / 2, TAB_CY + TAB_W / 2 - 100.0, z0 + FOOT_H + RISE,
                        TAB_L, 60.0, 60.0))
parts["table_rails"] = rails
feet = None
for fx in (TAB_CX - TAB_L / 2 + 40.0, TAB_CX + TAB_L / 2 - 40.0 - FOOT):
    for fy, fz in ((TAB_CY - TAB_W / 2 + 40.0, z0), (TAB_CY + TAB_W / 2 - 120.0, z0 + RISE)):
        f = box(fx, fy, fz, FOOT, FOOT, FOOT_H)
        feet = f if feet is None else feet.union(f)
parts["ballast_feet"] = feet

# ---------------------------------------------------------------- tilted module plane (GCR 0.6 strips)
z_lo = z0 + FOOT_H + 60.0
z_hi = z_lo + RISE
plane = None
strip_w = TAB_W * GCR / N_STRIPS
step = (TAB_W - N_STRIPS * strip_w) / (N_STRIPS - 1)       # 60 % coverage, even gaps
for i in range(N_STRIPS):
    y0 = TAB_CY - TAB_W / 2 + i * (strip_w + step)
    s = (cq.Workplane("XY", origin=(TAB_CX - TAB_L / 2, y0, z_lo + (y0 - (TAB_CY - TAB_W / 2)) * math.tan(TILT)))
         .box(TAB_L, strip_w, STRIP_T, centered=False))
    plane = s if plane is None else plane.union(s)
parts["module_strips"] = plane

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


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
    assert span <= L - 120.0, (face, z, span)
    x = max(60.0, (L - span) / 2)
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = tube_z("DN15", T_PLINTH + 15.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (430.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum is the box top
        s = tube_z("DN15", 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (570.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = tube_z(dnl if dnl.startswith("DN") else "DN15", 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        if r["rating"] and "conductor" in str(r.get("service", "")).lower():
            note += "; conductor service per the duty inline rows (drawn as the schedule's tube row)"
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "tube_stub", "dn": dnl, "face": face, "height_mm": h,
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

# ---------------------------------------------------------------- checks + report
dims = stl_bbox_mm(str(out / (UNIT.lower() + ".stl")))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
mass = {k: round(v.val().Volume() * materials.density("CS") / 1e9, 2) for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "representative array-table section at the registry box (the "
                "WAFER_FAB room-scale precedent): roof-plane deck, ballast feet, "
                "table rails, and the tilted module plane with 3 strips covering "
                "60 % of the plane (GCR 0.6, A-M-103), tilt +10 deg about +X "
                "with the +Y edge raised (equator-facing, site north = +Y, "
                "models/freecad heritage rule)",
        "array_facts": {
            "tables": 15, "modules": MODULE_COUNT, "module_kw": MODULE_KW,
            "nameplate_kWp": 3026, "area_m2": ARRAY_M2,
            "roof_footprint_mm": [210000, 138000],
            "table_mm": [40293.2, 43968.0],
            "pathways": "perimeter 1829 mm, interior 1219 mm (IFC 2027 1205.3 / "
                        "NFPA 1 11.12; solver roof_close segment math)",
            "mounting": "roof only (X-PAR-07); ground field removed",
            "mass_t": round(ARRAY_M2 * KG_M2 / 1000.0, 1),
            "mass_basis": "struct_pv_kg_m2 17.0 kg/m2 modules + ballasted "
                          "racking (A-M-184) over the node area_m2",
            "loads_kPa": {"service": 1.11, "lrfd": 1.716},
            "roof_capacity_kWp_class": 3029.5,
        },
        "tilt": {"deg_drawn": TILT_DEG,
                 "basis": "low-tilt rows at GCR 0.6 (A-M-103); the numeric tilt "
                          "is a study value - the verification test is a PVWatts "
                          "run at the roof tilt and azimuth (hold, WORK_ORDER "
                          "W12); azimuth equator-facing per the site-north +Y "
                          "heritage rule"},
        "purchased": "PV modules (0.5 kW, STC eff 0.19) and the inverter row are "
                     "purchased per plan rule 6; the ballasted racking is the "
                     "shop make",
        "guard": "four-post hold-down/guard frame pins the registry box "
                 "(X-PAR-04) and is the A-MACH guard; the ballast feet are the "
                 "A-MACH anchor (A-M-105 roof_pv_dead 0.15 kPa: modules and "
                 "ballasted racking); 8 slab anchors (fasteners.csv)",
        "material": "no wetted alloy (duty section 3); conductors copper; "
                    "structure carbon steel/aluminium class; CA does not apply",
        "ca_mm": 0.0,
        "rep_scale": "the representative build is box-scale; the array itself "
                     "spans the roof planes (facts above) - the drawing set and "
                     "this check carry the array figures (WAFER_FAB room-scale "
                     "precedent)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4 verbatim: DN copied from the edge, not "
                    "recalculated); N1 solar into the array (DN25) on -Y at "
                    "z 160; N2 PV daily average (DN25) on +Y at z 600 - the "
                    "electrical edges drawn as the schedule's tube rows with the "
                    "conductor note carried; drain flush at the envelope bottom "
                    "(50 datum); vent flush at the envelope top (800 datum is "
                    "the box top); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Plinth {L:g} x {W:g} x {T_PLINTH:g} (rep-section base)", 1,
     "carbon steel (ASTM A500)", mass["plinth"], "make (AQS-BOM-SC-001)",
     "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["2", f"Four-post hold-down/guard frame pinning the {L:g} x {W:g} x {H:g} "
           "envelope (40 x 40 posts, top rails)", 1, "carbon steel (ASTM A500)",
     mass["frame"], "make (AQS-BOM-SC-001)",
     "frame pins the registry box (X-PAR-04); A-MACH guard; anchors in fasteners.csv"],
    ["3", "Roof-plane segment deck (the representative roof plane)", 1,
     "carbon steel", mass["roof_deck"], "make (AQS-BOM-SC-001)",
     "representative section; the roof structure is the EXT_HALL/X-BLD lane's "
     "(LRFD 1.72 kPa, A-M-105)"],
    ["4", f"Array table rails + 4 ballast feet (rep section; {TILT_DEG:g} deg low-tilt)",
     1, "carbon steel + ballast", mass["table_rails"] + mass["ballast_feet"],
     "make (AQS-BOM-SC-001)",
     "ballasted racking per A-M-105 (roof_pv_dead 0.15 kPa: modules and ballasted "
     "racking); the A-MACH anchor drawn; array total 451.8 t at 17 kg/m2 "
     "(A-M-184) reported in check.machine"],
    ["5", "Tilted module-plane strips, 3 off covering 60 % of the table plane "
           "(GCR 0.6, A-M-103)", 3, "PV module plane (purchased, envelope)",
     mass["module_strips"], "buy",
     "modules 0.5 kW x 6052 = nameplate 3026 kWp (node); purchased per plan "
     "rule 6; STC eff 0.19 (pv_module_eff)"],
    ["6", "Nozzle set per docs-authority/nozzles/PV_ARRAY.csv: 2 DN25 electrical "
           "edges + DN15 drain/vent, drawn as the schedule's tube rows",
     len(schedule), "316L tube", mass["nozzles"], "make (AQS-BOM-SC-001)",
     "schedule tags/faces/heights verbatim; conductor service noted per the duty "
     "inline rows; atmospheric per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 2 per frame post line (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M10 ballast-foot bolt + nut", fasteners.grade_for("CS"), 8,
     "ballast feet to the table rails, 2 per foot (count from the model)",
     "8.8 on carbon steel per the grade rule; the roof-ballast design is the "
     "X-BLD lane's (hold, WORK_ORDER W12)"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "rep_scale": "box-scale representative table section (WAFER_FAB precedent); "
                 "the array facts are reported, not shrunk onto the box",
    "table": {"l_mm": TAB_L, "w_mm": TAB_W, "tilt_deg": TILT_DEG, "gcr": GCR,
              "strips": N_STRIPS},
    "ballast_foot_mm": [FOOT, FOOT, FOOT_H],
}
p["design"] = dict(DS) if isinstance(DS, dict) else {}
p["design"].update({
    "service": "PV_ARRAY: the roof PV - 15 array tables over the extension roof, "
               "nameplate 3026 kWp (6052 x 0.5 kW), roof only per X-PAR-07 "
               "(duty sections 1 and 2; A-M-233 rebasis)",
    "array_facts": report["machine"]["array_facts"],
    "tilt": report["machine"]["tilt"],
    "material": "no wetted alloy (duty section 3); conductors copper; "
                "structure carbon steel/aluminium class",
    "ca_mm": 0.0,
    "material_basis": "duty section 3; CA does not apply",
    "purchased": "PV modules and the inverter row (plan rule 6); ballasted "
                 "racking is the shop make (X-MFG-32 class)",
})
p["layout"] = {
    "frame": "origin at the envelope corner; roof-plane deck over the plinth; "
             "table section centred (860 x 480 at +10 deg, +Y edge raised - "
             "equator-facing, site north = +Y); hold-down posts at the corners",
    "supports": "plinth + hold-down frame + ballast feet (A-MACH anchor) + 8 "
                "slab anchors",
    "nozzle_spread": "the schedule gives face and height only; N1 on -Y at z 160, "
                     "N2 on +Y at z 600, drain at x 430, vent at x 570; per-tag "
                     "positions in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
