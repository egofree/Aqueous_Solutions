"""AFTERBURNER manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 6, F-HX).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the tracker;
the envelope, design and layout blocks beside them are builder-owned) and rebuilds
every solid.

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm (study default envelope box; the duty
  section 8 chamber sizing is the machine authority). The build stays inside it.
- Chamber per duty section 8 (AQS-DUTY-063 Rev B section 6, X-SAN-01): combustion
  chamber ID 200 x 600 mm, >= 850 C for >= 2 s (Directive 2010/75/EU Art. 50), feed
  7.03 kg/d including sanitation cake and biogas. The chamber is drawn horizontal
  along the run: steel shell wall 6 mm and refractory lining 50 mm are study values
  (duty section 8: "Refractory and burner detail open" - holds, W12). Material
  carbon steel per duty section 3, hydrocarbon service, CA 1.5 mm (AQS-STD-001).
- Purchased items as envelopes (plan rule 6), named with the rating from the node
  equipment list: burner with ignition transformer and BMS panel (0.05 kW) on the
  -X face, flue ID fan variable-speed high-temp class (0.1332 kW) on the +X face,
  dampers and flame monitor (0.01 kW) on the chamber top. The burner and refractory
  detail are open on the duty (holds, W12) - the envelopes carry the node ratings,
  no invented internals.
- Nozzles: all 12 rows of docs-authority/nozzles/AFTERBURNER.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the envelope
  faces (duty section 4: no duct bore, no flange class). The N12 solids row
  (dewatered digestate cake to incineration, barrier 2) is a non-piped transfer
  drawn DN15, bore not calculated (plan W4). Drain flush at the envelope bottom
  (50 datum); vent flush at the envelope top (800 datum is the box top). The
  schedule rating column (Class 150) is carried verbatim as text.
- A-HX report: the chamber volume and gas residence from the model are stated
  against the >= 2 s duty requirement at the AFTERBURNER_FLUE design flow
  (0.0018 m3/s flue class at 200 C, node design) - reported, not called a
  calculated design (the duty claims no heat rate for this unit).
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, materials, nozzles          # noqa: E402
from tracker import stl_bbox_mm                            # noqa: E402  (gate-consistent STL reader)

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0                                            # plinth, AQS-MOD-002 dry service
ID_CH, L_CH = 200.0, 600.0                                 # duty section 8 (X-SAN-01)
T_REF, T_STEEL = 50.0, 6.0                                 # study values (holds, W12)
OD_CH = ID_CH + 2 * (T_REF + T_STEEL)                      # 312
Y_C, Z_C = W / 2, 420.0                                    # chamber axis
X0 = (L - L_CH) / 2                                        # 200: chamber centred along x
T_C = 850.0                                                # duty section 8 class
T_RES_S = 2.0                                              # duty section 8 (EU IED Art. 50)
Q_FLUE_M3S = 0.0018                                        # AFTERBURNER_FLUE node design (200 C class)
MAT = "CS"                                                 # duty section 3
CA = materials.ca_for(MAT, "hydrocarbon")                  # 1.5, AQS-STD-001
RHO = materials.density(MAT)

assert L == 1000.0 and W == 600.0 and H == 800.0, "AFTERBURNER node envelope changed"
assert OD_CH <= W - 40.0 and L_CH <= L - 300.0, "chamber drawn to the envelope"
V_CH_M3 = math.pi / 4 * ID_CH ** 2 * L_CH / 1e9
T_RES_MODEL_S = V_CH_M3 / Q_FLUE_M3S                       # at the 200 C class flow


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def tube_z(dnl, length):
    od, wall = dn.pipe_od(dnl), dn.pipe_wall(dnl, 40)
    return cq.Workplane("XY").circle(od / 2).circle(od / 2 - wall).extrude(length)


parts = {}

# ---------------------------------------------------------------- plinth + saddles
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
saddle = None
for xs in (X0 + 70.0, X0 + L_CH - 70.0):
    # the saddle box tops pierce the shell annulus: tangent/line contacts leave
    # parts unfused (the GLASS_BURNOUT housing fix)
    s = box(xs - 90.0, Y_C - OD_CH / 2 - 20.0, T_PLINTH, 180.0, 2 * (OD_CH / 2 + 20.0),
            Z_C - (OD_CH / 2 - 30.0) - T_PLINTH)
    saddle = s if saddle is None else saddle.union(s)
parts["saddles"] = saddle

# ---------------------------------------------------------------- chamber (duty section 8)
ch = (cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
      .circle(OD_CH / 2).circle(OD_CH / 2 - T_STEEL).extrude(L_CH))
ends = None
for xe in (X0, X0 + L_CH - 10.0):                          # end heads (burner / flue ends)
    e = (cq.Workplane("YZ", origin=(xe, Y_C, Z_C))
         .circle(OD_CH / 2).circle(ID_CH / 2).extrude(10.0))
    ends = e if ends is None else ends.union(e)
parts["chamber"] = ch.union(ends)
# refractory press 3 mm into the steel shell: a tangent liner leaves coincident
# cylinder faces that do not fuse (same fix idiom)
refr = (cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
        .circle(OD_CH / 2 - T_STEEL + 3.0).circle(ID_CH / 2).extrude(L_CH))
parts["refractory"] = refr

# ---------------------------------------------------------------- purchased envelopes (node equipment list)
burner = (cq.Workplane("XY", origin=(X0 - 120.0, CYb := Y_C - 75.0, Z_C - 75.0))
          .box(120.0, 150.0, 150.0, centered=False))       # burner + ignition + BMS, 0.05 kW
burner = burner.union(cq.Workplane("YZ", origin=(X0, Y_C, Z_C))
                      .circle(ID_CH / 2 + 8.0).circle(ID_CH / 2 - 4.0).extrude(14.0))
parts["burner"] = burner
fan = (cq.Workplane("XY", origin=(X0 + L_CH + 6.0, Y_C - 80.0, Z_C - 80.0))
       .box(160.0, 160.0, 160.0, centered=False))          # flue ID fan, 0.1332 kW
fan = fan.union(cq.Workplane("YZ", origin=(X0 + L_CH, Y_C, Z_C))
                .circle(ID_CH / 2 + 8.0).circle(ID_CH / 2 - 4.0).extrude(14.0))
parts["fan"] = fan
parts["damper"] = (cq.Workplane("XY", origin=(X0 + L_CH / 2 - 60.0, Y_C - 60.0,
                                              Z_C + OD_CH / 2 - 20.0))
                   .box(120.0, 120.0, 80.0, centered=False))  # dampers + flame monitor, 0.01 kW
# the envelope sinks 20 mm into the shell: a tangent line contact does not fuse

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
    assert span <= L - 300.0, (face, z, span)
    x = X0 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    dnl_draw = dnl if dnl.startswith("DN") else "DN15"
    note = "atmospheric open-bore tube stub flush at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N7: drain flush at the envelope bottom
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N8: 800 datum is the box top
        s = tube_z("DN15", 50.0)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        if not dnl.startswith("DN"):
            note += (f"; {r['size']} row is a non-piped transfer: drawn DN15, bore "
                     "not calculated (plan W4)")
        s = tube_z(dnl_draw, 50.0)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
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
mass = {k: round(v.val().Volume() * ((RHO * 1.0) if k in ("chamber", "saddles", "nozzles", "plinth") else RHO) / 1e9, 2)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "chamber": {
        "type": "horizontal refractory-lined combustion chamber per duty section 8 "
                "(AQS-DUTY-063 Rev B section 6, X-SAN-01): ID 200 x 600, steel "
                "shell wall 6 and refractory lining 50 (study values - holds, W12), "
                "on two saddles over a 20 mm plinth",
        "id_mm": ID_CH, "length_mm": L_CH, "wall_mm": T_STEEL, "refractory_mm": T_REF,
        "wall_basis": "study values; duty section 8: refractory and burner detail "
                      "open (WORK_ORDER W12)",
        "class_C": T_C, "residence_req_s": T_RES_S,
        "v_chamber_m3": round(V_CH_M3, 5),
        "residence_at_flue_s": round(T_RES_MODEL_S, 1),
        "residence_basis": f"chamber volume / the AFTERBURNER_FLUE node design flow "
                           f"{Q_FLUE_M3S:g} m3/s (200 C flue class): "
                           f"{T_RES_MODEL_S:.1f} s against the >= 2 s requirement "
                           "(Directive 2010/75/EU Art. 50 via duty section 8); "
                           "reported, not called a calculated design (A-HX; the "
                           "duty claims no heat rate)",
        "feed_kg_d": 7.03,
        "material": MAT, "ca_mm": CA,
    },
    "purchased": {
        "burner": "burner + ignition transformer + BMS panel, 0.05 kW (node "
                  "equipment list) - envelope per plan rule 6; burner detail open "
                  "(duty section 8, hold W12)",
        "fan": "flue ID fan, variable-speed high-temp class, 0.1332 kW (node "
               "equipment list) - envelope per plan rule 6",
        "damper": "dampers and flame monitor, 0.01 kW (node equipment list) - "
                  "envelope per plan rule 6",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: no duct bore, no flange class); the N12 "
                    "solids row (dewatered digestate cake to incineration, barrier "
                    "2) drawn DN15, bore not calculated (plan W4); the schedule "
                    "rating column (Class 150) carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Combustion chamber ID {ID_CH:g} x {L_CH:g}, steel shell wall {T_STEEL:g} "
          f"(study) with two end heads, per duty section 8 (X-SAN-01)", 1,
     "carbon steel (duty section 3)", mass["chamber"], "make",
     "duty section 8 chamber sizing; wall a study value (hold, WORK_ORDER W12); CA "
     "1.5 mm (AQS-STD-001 hydrocarbon rule)"],
    ["2", f"Refractory lining t {T_REF:g} over the full chamber bore and ends", 1,
     "refractory (castable/class per duty - detail open)", mass["refractory"], "make",
     "duty section 8: refractory detail open - lining drawn as a study layer "
     "(hold, WORK_ORDER W12); nothing resized"],
    ["2", f"Saddles, 2 off (180 mm bases to the chamber bore) + plinth {L:g} x {W:g} x {T_PLINTH:g}", 1,
     "carbon steel (ASTM A500)", mass["saddles"] + mass["plinth"], "make",
     "AQS-MOD-002 dry service; saddle tops pierce the shell annulus (fuse idiom); "
     "anchors in fasteners.csv"],
    ["5", "Burner + ignition transformer + BMS panel envelope, 0.05 kW", 1,
     "purchased unit (envelope)", mass["burner"], "buy",
     "node equipment list; plan rule 6 envelope; burner detail open (hold, W12)"],
    ["6", "Flue ID fan envelope, variable-speed high-temp class, 0.1332 kW", 1,
     "purchased unit (envelope)", mass["fan"], "buy",
     "node equipment list; plan rule 6 envelope"],
    ["7", "Damper and flame monitor envelope, 0.01 kW", 1,
     "purchased unit (envelope)", mass["damper"], "buy",
     "node equipment list; plan rule 6 envelope"],
    ["8", "Nozzle set per docs-authority/nozzles/AFTERBURNER.csv: 11 open-bore tube "
          "stubs (DN15), the N12 solids row drawn DN15 bore not calculated",
     len(schedule), "carbon steel", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric tube per duty section 4"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M12 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per saddle station (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
    [None, "M12 saddle bolt + nut", fasteners.grade_for("CS"), 8,
     "saddle cradle to chamber, 4 per saddle (count from the model)",
     "8.8 on carbon steel; study pattern, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "chamber": {"id_mm": ID_CH, "length_mm": L_CH, "od_mm": OD_CH,
                "axis_mm": [None, Y_C, Z_C], "x0_mm": X0},
    "plinth_mm": T_PLINTH,
}
p["design"] = {
    "service": "AFTERBURNER: waste-gas and sanitation-cake combustion chamber, "
               ">= 850 C for >= 2 s (duty section 8, EU IED Art. 50), atmospheric",
    "material": MAT, "ca_mm": CA,
    "wall_mm": T_STEEL, "wall_basis": "study value (hold W12)",
    "refractory_mm": T_REF, "refractory_basis": "study layer; duty detail open "
    "(hold W12)",
    "class_C": T_C, "residence_req_s": T_RES_S,
    "residence_at_flue_s": round(T_RES_MODEL_S, 1),
    "purchased": {"burner_kW": 0.05, "fan_kW": 0.1332, "damper_kW": 0.01,
                  "basis": "node equipment list, envelopes per plan rule 6"},
}
p["layout"] = {
    "frame": "origin at the envelope corner; chamber axis along +x at y 300, z 420, "
             "chamber x 200..800; burner envelope on -X, fan envelope on +X, damper "
             "envelope on top",
    "supports": "plinth + two saddles + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack in one row "
                     "per face/height group from x 100, 8 mm clear at the bore; "
                     "drain at x 460, vent at x 540; per-tag positions in "
                     "check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
print(json.dumps({"residence_at_flue_s": round(T_RES_MODEL_S, 1)}))
