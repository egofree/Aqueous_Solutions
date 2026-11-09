"""LEACH_CSTR_1 manufacturing model, AQS-PLAN-006 work order (X-MFG lane).

Graph revision AC. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 2000 mm, y along 1200 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Envelope 2000 x 1200 x 1400 mm per duty section 2 (AQS-DUTY-050: working level
  1100 mm, 2.14 m3 at 1100 kg/m3). The node carries no size_mm (tracker hold "no
  size on the node"); the duty envelope is the claimed box and nothing exceeds it.
  Tank body 1888 x 1080 x 1400 inside 56 mm X-end and 60 mm Y-face reserved bands;
  wall 16 mm, floor 16 mm CPVC (AQS-DUTY-050), lid 12 mm on a 40 mm flange.
- Three FRP belts C203x56x6.4 at z 300/560/900 (AQS-DUTY-050 study). The issued
  nozzle schedule puts port rows at z 160/280/600 inside the belt bands on the Y
  faces, so the belts are segmented with a notch at every port the band crosses;
  the segmentation is a layout choice recorded in check.json, not a resize of
  either authority figure.
- HX-5 coil: borosilicate 3.3, 4.22 m2, two concentric helices of 25 x 3 mm tube,
  53.7 m (AQS-DUTY-049 natural-convection case; AQS-STD-002 section 3.3). Drawn as
  its annulus envelope OD 925 / ID 575 x 600 on four PTFE pads; the mass is taken
  from the tube, not the envelope (params.hx5_coil).
- Agitator per AQS-DUTY-050 (study): 4-blade 45 deg PBT D 450 at 150 rpm, 403 W
  shaft, 0.75 kW gearmotor. PVDF-sheathed D 50 shaft through the lid, solid PVDF
  impeller at z 250 inside the coil. The drive bridge sits about 400 mm above the
  lid, outside the envelope, and is not modeled.
- Nozzles: all rows of docs-authority/nozzles/LEACH_CSTR_1.csv drawn at tag,
  face, height and bore (tracker W2). Inlets are the -Y face, outlets the +Y face
  (duty section 4); the along-face x positions are the registered layout choice.
  Atmospheric joints are hose barbs (duty sections 4 and 6); solids rows are DN15
  stubs labeled bore not calculated (AQS-PLAN-006 W4); the schedule rating column
  reads Class 150 and is carried verbatim as text - no flange is drawn because no
  process pressure is stated (duty section 6). The IA-E-LEACH conductor (duty
  section 4 prose; an electrical edge, so not a schedule row) is the gland boss
  on +Y, not a hose.

Materials per docs-authority/duties/LEACH_CSTR_1.md section 3: CPVC wetted
(AQS-STD-002 Rev F rules M2 and M5; liquor 70-85 C), no metal wetted part,
corrosion allowance 0 mm (AQS-STD-001 polymer rule).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = (2000.0, 1200.0, 1400.0)                        # duty section 2 envelope
REV = P["graph_revision"]
A = P["assumptions"]

# ------------------------------------------------------------------ cited constants
T_WALL = A["wall_mm"]["value"]            # 16, AQS-DUTY-050
T_FLOOR = A["floor_mm"]["value"]          # 16
T_LID = A["lid_mm"]["value"]              # 12
FL_W = A["lid_flange_w_mm"]["value"]      # 40
ZX = A["header_zone_mm"]["value"]         # 60 reserved band each Y face
BX = A["header_zone_mm"]["value"] - 4     # 56 belt depth on the X ends
Z_LIQ = A["level_mm"]["value"]            # 1100 working level, AQS-DUTY-050
RHO_LIQ = A["liquor_density_kg_m3"]["value"]
BELTS = A["belts"]                        # z 300/560/900, C203x56x6.4, FRP 1900 (study)
COIL = P["hx5_coil"]                      # 4.22 m2 glass 3.3 coil, 53.7 m of 25 x 3
AG = P["agitator"]                        # PBT D450, 150 rpm, 403 W, 0.75 kW motor
CA = materials.ca_for("CPVC")             # 0.0, polymers: AQS-STD-001 shop rule

# tank body inside the reserved bands (belts and port hardware live in the bands)
TX0, TX1 = BX, L - BX                     # 56 .. 1944
TY0, TY1 = ZX, W - ZX                     # 60 .. 1140
IMBED = TY0 + T_WALL + 10.0               # port extension reaches 10 mm into the cavity

RHO = {"CPVC": materials.density("CPVC"), "FRP": BELTS["density_kg_m3"],
       "PTFE": 2200.0, "PVDF": materials.density("PVDF"), "glass": 2230.0}


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def rod(r, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    return cq.Workplane(cq.Plane(origin=p, xDir=d[1], normal=d[0])).circle(r).extrude(ln)


parts = {}

# ---------------------------------------------------------------- tank: CPVC shell, flange, lid
shell = box(TX0, TY0, 0, TX1 - TX0, TY1 - TY0, H - T_LID).cut(
    box(TX0 + T_WALL, TY0 + T_WALL, T_FLOOR, TX1 - TX0 - 2 * T_WALL,
        TY1 - TY0 - 2 * T_WALL, H))
flange = box(TX0, TY0, H - T_LID - 10, TX1 - TX0, TY1 - TY0, 10).cut(
    box(TX0 + T_WALL + FL_W, TY0 + T_WALL + FL_W, H - T_LID - 10,
        TX1 - TX0 - 2 * (T_WALL + FL_W), TY1 - TY0 - 2 * (T_WALL + FL_W), 10))
lid = box(TX0, TY0, H - T_LID, TX1 - TX0, TY1 - TY0, T_LID)
tank = shell.union(flange).union(lid)

# lid bolt holes: M12 PVDF at 150 mm pitch (params.lid_bolt), counted from the model
pb = A["lid_bolt"]["pitch_mm"]
nx = int((TX1 - TX0 - 2 * T_WALL - 2 * FL_W) // pb)
ny = int((TY1 - TY0 - 2 * T_WALL - 2 * FL_W) // pb)
holes = []
for i in range(nx + 1):
    x = TX0 + T_WALL + FL_W / 2 + i * (TX1 - TX0 - 2 * (T_WALL + FL_W)) / nx
    holes += [(x, TY0 + T_WALL + FL_W / 2), (x, TY1 - T_WALL - FL_W / 2)]
for j in range(1, ny):
    y = TY0 + T_WALL + FL_W / 2 + j * (TY1 - TY0 - 2 * (T_WALL + FL_W)) / ny
    holes += [(TX0 + T_WALL + FL_W / 2, y), (TX1 - T_WALL - FL_W / 2, y)]
for (x, y) in holes:
    tank = tank.cut(rod(6.5, (x, y, H - T_LID - 10), "Z", T_LID + 10))
parts["tank"] = tank

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
SOLIDS_NOTE = "solids hand transfer - bore not calculated (AQS-PLAN-006 W4)"
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}   # duty section 4: inlets -Y, outlets +Y


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


def od_of(row):
    """Port outside diameter from the schedule bore; solids rows drawn at DN15."""
    return dn.pipe_od("DN15") if row["size"] == "solids" else dn.pipe_od(row["size"])


schedule = [r for r in P["nozzles"]]
groups = {}                                               # (face, height) -> rows
for r in schedule:
    if r["size"] == "cable":                              # carried, never drawn: no pack slot
        continue
    groups.setdefault((FACE_OF.get(r["face"], r["face"]), float(r["height_mm"])), []).append(r)

# single-row packing per face/height group, centred on the face mid-length (the
# along-face positions are the registered layout choice; the schedule gives face
# and height only). Deterministic: largest bore first, then tag order.
layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-od_of(r), r["tag"]))
    span = sum(od_of(r) + 8.0 for r in rows) - 8.0
    assert span <= (TX1 - TX0) - 80.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn, conducted = None, {}, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    if dnl == "cable":                                    # power terminal row: carried, never drawn
        drawn[tag] = {"style": "carried", "dn": dnl, "face": r["face"],
                      "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                      "service": r["service"],
                      "note": "power terminal row - a cable schedule row: carried "
                              "verbatim, never drawn"}
        continue
    face = FACE_OF.get(r["face"], r["face"])
    dnl_hw = "DN15" if dnl == "solids" else dnl
    if r["face"] == "bottom":                             # N9: flush at z 0, boss to the datum
        s = nozzles.stub(dnl_hw, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (300.0, W / 2), (L, W, H))
    elif r["face"] == "top":                              # N10: flush at the lid, z 1400 datum
        s = nozzles.stub(dnl_hw, 40.0)
        s = nozzles.place_on_face(s, "top", 0.0, (1700.0, W / 2), (L, W, H))
    else:
        if dnl == "solids":
            s = nozzles.stub("DN15", 50.0)
            note = SOLIDS_NOTE
        else:
            s = nozzles.hose_barb(hose_id(dnl_hw), Hose[dnl_hw], root_od=dn.pipe_od(dnl_hw))
            note = "atmospheric hose joint at the envelope face (duty sections 4 and 6)"
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
        # extension stub: barb shank to 10 mm inside the cavity wall, so the union
        # crosses the reserved band and the tank wall instead of floating in it
        y0 = 40.0 if face == "-Y" else W - 86.0
        s = s.union(rod(od_of(r) / 2, (layout_x[tag], y0, h), "Y", 46.0))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "solids" if dnl == "solids" else "hose",
                  "dn": dnl_hw if dnl != "solids" else "DN15",
                  "face": face, "height_mm": h, "x_mm": layout_x[tag],
                  "schedule_rating": r["rating"], "note": note}

# IA-E-LEACH conductor gland (duty section 4 prose; electrical edge, not a schedule
# row): DN15 passage in a boss on +Y at the 600 mm row height, clear of the ports
gx = 250.0
gland = rod(16.0, (gx, W - 46.0, 600.0), "Y", 46.0).cut(
    rod(dn.pipe_od("DN15") / 2 - dn.pipe_wall("DN15"), (gx, W - 96.0, 600.0), "Y", 60.0))
noz = noz.union(gland)
conducted["IA-E-LEACH"] = {"style": "gland", "dn": "DN15", "face": "+Y", "height_mm": 600,
                       "x_mm": gx, "note": "conductor gland, not a hose (duty section 4 prose; "
                       "electrical edge IA-E-LEACH, not a schedule row)"}
parts["nozzles"] = noz

# ---------------------------------------------------------------- FRP belts, segmented at ports
def belt_notches(zb, bh):
    """Port positions whose bore crosses this belt band, per face."""
    cuts = []
    for r in schedule:
        face = FACE_OF.get(r["face"])
        if face is None:
            continue
        z = float(r["height_mm"])
        if abs(z - zb) <= bh / 2 + od_of(r) / 2 + 2.0:
            cuts.append((layout_x[r["tag"]], 0.0 if face == "-Y" else W, z, od_of(r) / 2 + 6.0))
    return cuts


belts = None
notched = 0
for zb in BELTS["z_mm"]:
    bh = BELTS["height_mm"]
    ring = box(0, TY0 - BELTS["depth_mm"], zb - bh / 2, L, (TY1 - TY0) + 2 * BELTS["depth_mm"], bh)
    ring = ring.cut(box(TX0, TY0, zb - bh / 2, TX1 - TX0, TY1 - TY0, bh))
    for (x, yface, z, r) in belt_notches(zb, bh):
        y0 = yface - BELTS["depth_mm"] - 2 if yface == 0 else TY1
        ring = ring.cut(rod(r, (x, y0, z), "Y", BELTS["depth_mm"] + 4.0))
        notched += 1
    belts = ring if belts is None else belts.union(ring)
parts["belts"] = belts

# ---------------------------------------------------------------- HX-5 coil envelope + pads
cx, cy = L / 2, W / 2
coil = cq.Workplane("XY", origin=(cx, cy, T_FLOOR + 100)).circle(462.5).circle(287.5).extrude(600)
pads = None
for (dx, dy) in ((375, 0), (-375, 0), (0, 375), (0, -375)):
    p = rod(30, (cx + dx, cy + dy, T_FLOOR), "Z", 100)
    pads = p if pads is None else pads.union(p)
parts["coil"] = coil
parts["coil_pads"] = pads

# ---------------------------------------------------------------- agitator (study, AQS-DUTY-050)
shaft = rod(AG["shaft_od_mm"] / 2, (cx, cy, AG["impeller_z_mm"] - 10), "Z",
            H - T_LID - AG["impeller_z_mm"] + 10)
imp = rod(AG["D_mm"] / 2, (cx, cy, AG["impeller_z_mm"] - 10), "Z", 20)
parts["agitator"] = shaft.union(imp)

# ---------------------------------------------------------------- process inventory (not a BOM part)
liq = box(TX0 + T_WALL, TY0 + T_WALL, T_FLOOR, TX1 - TX0 - 2 * T_WALL,
          TY1 - TY0 - 2 * T_WALL, Z_LIQ - T_FLOOR)
for k in ("coil", "coil_pads", "agitator"):
    liq = liq.cut(parts[k])
inv = {"liquor": liq}

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="LEACH_CSTR_1")
for k, v in list(parts.items()) + list(inv.items()):
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "leach_cstr_1.step"))

body = None
for k, v in parts.items():
    body = v if body is None else body.union(v)
solid = body.val()
solid.exportStl(str(out / "leach_cstr_1.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "LEACH_CSTR_1.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
bb = solid.BoundingBox()
dims = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
v_liq = inv["liquor"].val().Volume() / 1e9
mass = {k: round(v.val().Volume() * RHO[{"tank": "CPVC", "nozzles": "CPVC", "belts": "FRP",
                                         "coil": "glass", "coil_pads": "PTFE",
                                         "agitator": "PVDF"}[k]] / 1e9, 1)
        for k, v in parts.items()}
coil_tube_kg = math.pi / 4 * (COIL["tube_od_mm"] ** 2 - (COIL["tube_od_mm"] - 2 * COIL["tube_wall_mm"]) ** 2) \
    * COIL["tube_length_m"] * 1e3 * RHO["glass"] / 1e9
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H], "size_basis": "duty section 2 envelope (AQS-DUTY-050); the graph node "
    "carries no size_mm (tracker hold, WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": round(v_liq, 3), "holdup_basis_m3": 2.14,
    "holdup_basis": "AQS-DUTY-050: 2.14 m3 at the 1100 mm working level, 1100 kg/m3 (study); "
    "residence 13.2 h on IA-EW-04 (duty section 2)",
    "wall": {"wall_mm": T_WALL, "floor_mm": T_FLOOR, "lid_mm": T_LID,
             "panel_stress_basis": "AQS-DUTY-050: 1.37 MPa at the floor against 3.03 MPa CPVC "
             "allowable at 85 C; belts 17.1 MPa against 50 MPa FRP, deflection L/490"},
    "belts": {"z_mm": BELTS["z_mm"], "section": BELTS["section"], "port_notches": notched,
              "note": "the issued schedule puts port rows at z 160/280/600 inside the belt bands; "
              "the belts are segmented with a notch at each crossing port (layout choice, "
              "WORK_ORDER W12)"},
    "coil": {"area_m2": COIL["area_m2"], "tube": "25 x 3 mm borosilicate 3.3",
             "tube_length_m": COIL["tube_length_m"], "tube_mass_kg": round(coil_tube_kg, 1),
             "drawn_as": "annulus envelope OD 925 / ID 575 x 600 (params.hx5_coil)",
             "basis": "AQS-DUTY-049 natural-convection case, 7.941 kW rated"},
    "agitator": {"type": AG["type"], "D_mm": AG["D_mm"], "rpm": AG["rpm"],
                 "shaft_W": AG["shaft_W"], "motor_kW": AG["motor_kW"],
                 "impeller_z_mm": AG["impeller_z_mm"],
                 "note": "drive bridge and lid seal outside the envelope, not modeled"},
    "nozzles_drawn": drawn,
    "conductors_drawn": conducted,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "hose barbs flush at the envelope faces per the atmospheric duty "
    "(lib/nozzles.place_on_face); solids rows DN15 labeled bore not calculated; schedule rating "
    "column (Class 150) carried verbatim as text, no flange drawn (duty section 6)",
    "conductor": "IA-E-LEACH gland boss on +Y at z 600 (duty section 4 prose)",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
n_barb = sum(1 for r in schedule if str(r["size"]).startswith("DN"))
n_solid = sum(1 for r in schedule if r["size"] == "solids")
rows = [
    ["1", f"CPVC tank shell, body {TX1 - TX0:g} x {TY1 - TY0:g} x {H:g} mm inside the reserved "
          f"bands, wall {T_WALL:g} mm, floor {T_FLOOR:g} mm, lid {T_LID:g} mm on a {FL_W:g} mm "
          f"flange", 1, "CPVC", mass["tank"], "make",
     "AQS-DUTY-050 wall 16 / floor 16; lid and flange are assumptions (WORK_ORDER W2); "
     "CA 0 mm (AQS-STD-001 polymer rule)"],
    ["2", f"Nozzle set per docs-authority/nozzles/LEACH_CSTR_1.csv: {n_barb} hose barbs, "
          f"{n_solid} solids ports at DN15 (bore not calculated)", len(schedule), "CPVC",
     mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty sections 4 and 6; "
     "barb profile a study proportion (lib/nozzles.py); the two cable schedule rows "
     "are carried, never drawn"],
    ["3", "IA-E-LEACH conductor gland boss, DN15 passage", 1, "CPVC", "", "make",
     "duty section 4 prose (electrical edge, not a schedule row); conductor, not a hose"],
    ["4", f"FRP belt set, pultruded channel {BELTS['section']}, segmented at the port rows "
          f"({notched} notches)", 3, "FRP vinyl ester", mass["belts"], "make",
     "AQS-DUTY-050 (study): z 300/560/900; density and allowable pending the pultrusion "
     "vendor sheet; X-MAT-21 coupon tests"],
    ["5", f"HX-5 coil, two concentric helices 25 x 3 mm tube, {COIL['tube_length_m']:g} m, "
          f"{COIL['area_m2']:g} m2", 1, "borosilicate glass 3.3", round(coil_tube_kg, 1), "buy",
     "AQS-DUTY-049 natural-convection case (7.941 kW rated); AQS-STD-002 section 3.3; dielectric "
     "isolating flange on the Q3 side outside the tank; mass from the tube"],
    ["6", "HX-5 coil support pad", 4, "PTFE", mass["coil_pads"], "make",
     "AQS-STD-002 section 3.3 (PTFE pads); study size"],
    ["7", f"Agitator: {AG['type']}, D {AG['D_mm']:g} mm at {AG['rpm']:g} rpm, "
          f"{AG['shaft_W']:g} W shaft", 1, "PVDF (sheath and impeller)", mass["agitator"], "make",
     "AQS-DUTY-050 (study); no metal wetted (AQS-STD-002 M3); in-house Zwietering "
     "just-suspended test is a named hold"],
    ["8", f"Gearmotor {AG['motor_kW']:g} kW, {AG['rpm']:g} rpm output, on the lid bridge", 1,
     "purchase item", "", "buy",
     "AQS-DUTY-050 (study); the lid bridge is outside the envelope and not modeled"],
    ["9", "Lid shaft seal", 1, "PTFE lip", "", "buy",
     "assumption; seal detail follows the drive supplier print (WORK_ORDER W12)"],
    ["10", f"Lid gasket, {FL_W:g} mm wide full-face", 1, "FKM", "", "buy",
     "AQS-NZ-001 names FKM; compatibility across the assay envelope held (WORK_ORDER W12)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 x 60 hex bolt + nut + 2 washers", "PVDF (non-metallic)", len(holes),
     "lid flange, 150 mm pitch (count from the model)",
     "non-metallic fasteners in the acid-gas head space (AQS-STD-002 M4); study lengths, "
     "confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)                      # legacy M2 block; superseded by envelope + layout
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "duty section 2 (AQS-DUTY-050): working level 1100 mm, 2.14 m3; the graph node "
             "carries no size_mm (tracker hold)",
    "tank_body_mm": [TX1 - TX0, TY1 - TY0, H],
    "reserved_bands": {"y_face_mm": ZX, "x_end_mm": BX,
                       "note": "port hardware and belts sit inside the bands"},
}
p["design"] = {
    "service": "leach CSTR, dilute HCl with metal chlorides, 70-85 C, atmospheric "
               "(duty sections 3 and 6)",
    "wall_mm": T_WALL, "floor_mm": T_FLOOR, "lid_mm": T_LID,
    "belts": BELTS, "level_mm": Z_LIQ, "liquor_density_kg_m3": RHO_LIQ,
    "coil_area_m2": COIL["area_m2"], "agitator": {k: AG[k] for k in
                                                  ("type", "D_mm", "rpm", "shaft_W", "motor_kW")},
    "design_kPa_note": "params design_kPa 25.1 is the old head-plus-10 figure, not a set point "
                       "(duty section 6)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; x along 2000, y along 1200, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row per "
                     "face/height group, centred on the face mid-length, 8 mm clear at the "
                     "bore; per-tag positions recorded in check.nozzles_drawn",
    "vent_drain": "N10 flush at the lid on the x 1700 centreline (datum 1400); N9 flush at "
                  "z 0 at x 300, boss to the 50 datum",
    "belt_segmentation": "port rows at z 160/280/600 cross the belt bands; each crossing "
                         f"port is notched out of the band ({notched} notches)",
    "conductor": "IA-E-LEACH gland at +Y x 250, z 600 (duty section 4 prose)",
    "hardware_idiom": "connection hardware flush at the envelope faces, extension stubs "
                      "10 mm into the cavity (lib/nozzles.place_on_face); nothing protrudes, "
                      "bbox within the duty envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}))
