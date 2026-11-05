"""CRYO_AHU_COND_CONDENSABLE manufacturing model, AQS-PLAN-006 work order
(M0 lane, tier 6, route hold).

Graph revision AD. Study. Not a PE stamp. Reads params.json (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned)
and rebuilds every solid. The weir/launder vessel idiom is the FLUE_KO accepted
model's (AQS-PLAN-006, FLOAT_SINK/FLUE_KO family).

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope
corner. Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (params
  size_note records it as read back from the cad/stl registry). The duty sheet
  section 4 still carries the unit-task-04 line "Size 600 x 400 x 600 mm" and
  the placement seed seats a 600 x 400 x 600 box: the node governs, the older
  figures are named holds (WORK_ORDER W12; the FLUE_KO precedent). The build
  fills the node box.
- Vessel per the unit's own duty sheet section 3 ("316L. Condensation. No
  carbon steel"): a vertical 316L knock-out drum - shell OD 540, wall 8 (study:
  no authority states a shell thickness; the material class is the duty row),
  on a plinth with a laps-to-plinth base head and a top head, inside the
  envelope. The condensable slip (IA-AHU-POT, 0.0521 kg/d) condenses against
  the cooled shell; the S70 condensables leave above the weir.
- Weir and launder - the layout solids of the knock-out separation duty (the
  FLUE_KO idiom): 316L weir plate at the shell centreline (x 420..430, to
  z 360) dividing the settle zone from the overflow zone; 316L launder trough
  at the +X side (channel floor z 300..310, lip plate to an overflow lip top
  z 360). The separation duty behind the layout is unsized (duty section 8: no
  holdup basis) - named hold (W12); the sump volume below the weir lip is
  computed from the model and reported (A-VES-style report; the unit's
  acceptance set is A-core - the duty claims no holdup, so no residence time
  is derived from the model volume).
- Nozzles: all 4 rows of docs-authority/nozzles/CRYO_AHU_COND_CONDENSABLE.csv
  drawn at tag, face, height and bore as atmospheric hose barbs flush at the
  envelope faces (duty section 4: "Atmospheric joints are hose. DN is copied
  from the edge and is not recalculated"; the rows read "Bore not calculated.
  Rating hose, atmospheric"). N1 condensable slip in on -Y at z 160; N2
  condensables out on +Y at z 600; N3 drain flush at the envelope bottom (50
  datum); N4 vent flush at the envelope top (800 datum is the box top). The
  schedule rating column carried verbatim as text; no flange (W4 110 % rule -
  no process pressure stated).
- Route hold: the node class is blank (the tracker row says what is known) -
  no AQS-PLAN-006 section 4 class; acceptance A-core with the route hold named
  (W12), the AFTERBURNER_FLUE/REE_RECOVER precedent.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))                      # models/mfg, for the shared lib
from lib import dn, fasteners, graph_node, materials, nozzles  # noqa: E402
from tracker import stl_bbox_mm                           # noqa: E402  (gate-consistent STL reader)

GN = graph_node.graph_node("CRYO_AHU_COND_CONDENSABLE")        # the plant graph is the sole authority
P = GN.as_params()                            # W2 keys (size_mm, graph_revision, unit_id, nozzles, design)
P.update({k: v for k, v in json.loads((HERE / "params.json").read_text()).items() if k not in P})   # builder-owned blocks only (assumptions/form/material class do not live on the graph)
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800
REV = P["graph_revision"]
UNIT = P["unit_id"]

T_PLINTH = 20.0
T_WALL = 8.0                    # study 316L shell - no authority states one (W12)
D, CX, CY = min(L, W) - 60.0, L / 2, W / 2   # shell OD 540; 30 mm stand-off to the +/-Y faces
R_IN = D / 2 - T_WALL
Z_SH0, Z_SH1 = 40.0, H - 40.0                               # shell 40..760
T_HEAD = 20.0
WEIR_X, WEIR_T, WEIR_TOP = 420.0, 10.0, 360.0                # weir plate (layout, study; W12)
WEIR_HALF = 250.0                                           # +/- y half-width at the centre chord
CHAN_X0, CHAN_X1 = 660.0, 750.0                             # launder channel floor (study, W12)
CHAN_HALF, CHAN_Z, LIP_TOP = 100.0, 300.0, 360.0
MAT = "316L"                                                # duty section 3
CA = materials.ca_for(MAT)                                  # 0.0, AQS-STD-001
RHO = materials.density(MAT)

# Envelope and design both come from the graph node; no hard-coded duplicate stays.
assert WEIR_X > CX - R_IN and WEIR_X < CX + R_IN, "weir inside the shell"
assert CHAN_X1 < CX + R_IN, "launder inside the shell"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


def ring_z(cx_, cy_, r_out, r_in, z0, z1):
    return (cq.Workplane("XY", origin=(cx_, cy_, z0)).circle(r_out).circle(r_in)
            .extrude(z1 - z0))


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


parts = {}

# ---------------------------------------------------------------- plinth + shell + heads
parts["plinth"] = box(0, 0, 0, L, W, T_PLINTH)
shell = ring_z(CX, CY, D / 2, R_IN, Z_SH0, Z_SH1)
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
                    .extrude(T_HEAD))                                        # top head 760..780
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(D / 2)
                    .extrude(T_PLINTH + T_HEAD))                             # base head laps plinth
parts["shell"] = shell

# ---------------------------------------------------------------- weir plate (layout solids)
parts["weir"] = box(WEIR_X, CY - WEIR_HALF, 35.0, WEIR_T, 2 * WEIR_HALF,
                    WEIR_TOP - 35.0 + 5)                            # laps the base head by 5

# ---------------------------------------------------------------- launder trough (layout solids)
launder = box(CHAN_X0, CY - CHAN_HALF, CHAN_Z, CHAN_X1 - CHAN_X0, 2 * CHAN_HALF,
              10.0)                                                 # channel floor
launder = launder.union(box(CHAN_X0, CY - CHAN_HALF, CHAN_Z,
                            CHAN_X1 - CHAN_X0, 10.0, LIP_TOP - CHAN_Z))   # -y lip
launder = launder.union(box(CHAN_X0, CY + CHAN_HALF - 10.0, CHAN_Z,
                            CHAN_X1 - CHAN_X0, 10.0, LIP_TOP - CHAN_Z))   # +y lip
parts["launder"] = launder

# ---------------------------------------------------------------- nozzles (schedule verbatim)
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}
Hose = {"DN15": 45.0, "DN25": 50.0}                                 # barb lengths, study proportions


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
    assert span <= L - 80.0, (face, z, span)
    x = L / 2 - span / 2
    for r in rows:
        w = od_of(r) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = od_of(r)
    note = "atmospheric hose joint at the envelope face (duty section 4; bore not calculated, hose, atmospheric)"
    if r["face"] == "bottom":                             # N3: drain flush at the envelope bottom
        s = nozzles.stub("DN15", 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (L / 2 - 40.0, W / 2), (L, W, H))
        note = "drain flush at the envelope bottom; 50 datum is the schedule placeholder"
    elif r["face"] == "top":                              # N4: 800 datum is the box top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (L / 2 + 40.0, W / 2), (L, W, H))
        note = "vent flush at the envelope top; schedule datum 800 mm is the box top"
    else:
        assert h <= H - od / 2 - 5.0, (tag, h)
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
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
RHO_OF = {"plinth": materials.density("CS")}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO) / 1e9, 2) for k, v in parts.items()}
# sump volume below the weir lip (A-VES-style report; no residence time derived)
R_SUMP = R_IN
WEIR_CHORD = 2 * math.sqrt(max(R_SUMP ** 2 - (WEIR_X - CX) ** 2, 0.0))
V_SUMP_L = math.pi * R_SUMP ** 2 * (LIP_TOP - Z_SH0) / 1e6 * 0.5   # half-shell to the lip (study)
report = {
    "bbox_mm": dims, "inside_size_mm": inside, "size_mm": [L, W, H],
    "size_basis": P.get("size_basis"),
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "machine": {
        "type": "condensable knock-out vessel per the duty section 3 material "
                "row (316L, condensation, no carbon steel), in the FLUE_KO "
                "weir/launder idiom (FLOAT_SINK/FLUE_KO family): vertical 316L "
                f"drum OD {D:g} (wall {T_WALL:g}, study) with a laps-to-plinth "
                "base head and a top head, weir plate at the shell centreline "
                f"(to z {WEIR_TOP:g}) dividing settle from overflow, launder "
                "trough at the +X side (lip top z 360); the IA-AHU-POT "
                "condensable slip (0.0521 kg/d) condenses against the cooled "
                "shell and the S70 condensables leave above the weir",
        "node_class": "blank on the node - the tracker row says what is known; "
                      "route hold carried by name (no AQS-PLAN-006 section 4 "
                      "class; AFTERBURNER_FLUE/REE_RECOVER precedent)",
        "material": MAT,
        "ca_mm": CA,
        "study_dims": "shell OD/wall, weir and launder dimensions are study "
                      "values (hold, WORK_ORDER W12)",
        "sump_report": {"v_half_shell_to_lip_l": round(V_SUMP_L, 3),
                        "weir_chord_mm": round(WEIR_CHORD, 1),
                        "note": "A-VES-style report from the model; the duty "
                                "claims no holdup (section 8) - no residence "
                                "time is derived from the model volume"},
        "superseded_figures": "the duty section 4 line 'Size 600 x 400 x 600 "
                              "mm' and the placement seed 600 x 400 x 600 box "
                              "predate the node size_mm study box - the node "
                              "governs, the older figures are named holds (W12; "
                              "the FLUE_KO precedent)",
    },
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (duty "
                    "section 4: atmospheric joints are hose; the rows read "
                    "'Bore not calculated. Rating hose, atmospheric'); N1 "
                    "condensable slip in on -Y at z 160; N2 condensables out on "
                    "+Y at z 600; drain flush at the envelope bottom (50 "
                    "datum); vent flush at the envelope top (800 datum is the "
                    "box top); no flange (W4 110 % rule); the schedule rating "
                    "column carried verbatim as text",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Knock-out shell OD {D:g} (wall {T_WALL:g}, study) with laps-to-plinth "
           "base head and top head", 1, "316L (duty section 3: condensation, no "
     "carbon steel)", mass["shell"], "make",
     "shell dimensions study (hold, WORK_ORDER W12); CA 0 mm (AQS-STD-001 316L "
     "rule)"],
    ["2", f"Weir plate at the shell centreline (to z {WEIR_TOP:g}) and launder "
           "trough at the +X side (lip top z 360)", 1, "316L", mass["weir"] + mass["launder"],
     "make", "FLUE_KO weir/launder idiom; layout solids of the knock-out duty; "
     "dimensions study (hold, WORK_ORDER W12)"],
    ["3", f"Plinth {L:g} x {W:g} x {T_PLINTH:g}", 1, "carbon steel (ASTM A500)",
     mass["plinth"], "make", "AQS-MOD-002 dry service; anchors in fasteners.csv"],
    ["4", "Nozzle set per docs-authority/nozzles/CRYO_AHU_COND_CONDENSABLE.csv: "
           "4 hose barbs (DN15) flush at the envelope faces", len(schedule),
     "316L", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim (rows read 'Bore not calculated. "
     "Rating hose, atmospheric'); atmospheric hose per duty section 4; barb "
     "profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("CS"), 8,
     "plinth to slab, 4 per side (count from the model)",
     "grade rule AQS-PLAN-006 W5: 8.8 on carbon steel; study length, confirmed at "
     "fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": P.get("size_basis"),
    "plinth_mm": T_PLINTH,
    "shell": {"od_mm": D, "wall_mm": T_WALL, "z_mm": [Z_SH0, Z_SH1], "pos_mm": [CX, CY]},
    "weir": {"x_mm": WEIR_X, "top_mm": WEIR_TOP},
    "launder": {"x_mm": [CHAN_X0, CHAN_X1], "lip_mm": LIP_TOP},
}
p["design"] = {
    "service": "CRYO_AHU_COND_CONDENSABLE: the AHU condensable slip knocked out "
               "against the cooled shell; condensables leave above the weir to "
               "the S70 line (duty sections 1 and 4)",
    "node_class": "blank on the node (the tracker row says what is known); "
                  "route hold named (W12)",
    "material": MAT, "ca_mm": CA,
    "material_basis": "duty section 3: 316L, condensation, no carbon steel; "
                      "CA 0 mm (AQS-STD-001)",
    "superseded": "duty section 4 / seed 600 x 400 x 600 figures predate the "
                  "node study box; the node governs (W12)",
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell centred with a 30 mm stand-off "
             "to the +/-Y faces; weir at x 420..430 to z 360; launder at x "
             "660..750, lip top z 360 (the FLUE_KO idiom)",
    "supports": "plinth + base head lap + 8 slab anchors",
    "nozzle_spread": "the schedule gives face and height only; ports pack one row "
                     "per face/height group at the envelope face, 8 mm clear at "
                     "the bore; drain at x 460, vent at x 540; per-tag positions "
                     "in check.nozzles_drawn",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox inside the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "nozzle_count_schedule", "part_mass_kg")}),
      flush=True)
