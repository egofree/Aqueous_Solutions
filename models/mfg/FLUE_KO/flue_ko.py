"""FLUE_KO manufacturing model, AQS-PLAN-006 work order (X-MFG lane, tier 4).

Graph revision AD. Study. Not a PE stamp. Reads params.json only (W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned).

Placement frame: x along 1000 mm, y along 600 mm, z up, origin at the envelope corner.
Every dimension is an authority figure or a named layout choice:

- Envelope 1000 x 600 x 800 mm, node size_mm - the study registry box (params
  size_note records it as read back from the cad/stl registry; it matches the
  AQS-MFG-001 study page). The duty sheet section 4 still carries the unit-task-04
  line "Size 600 x 700 x 1100 mm": the node governs, that line is a named hold
  (WORK_ORDER W12). The build fills the node box.
- Body: vertical FRP knock-out drum - shell OD 540, wall 8 (study: no authority
  states an FRP thickness; duty section 3 names the material class), on a plinth
  with a laps-to-plinth base head and a top head, inside the envelope.
- Internals (duty section 3 names the hardware; the node internals row is none, so
  the tracker records no internal solid):
  * borosilicate glass 3.3 inlet spool - OD 110 x wall 3 horizontal tube from the
    -Y face into the shell at z 300; S67 at 300 C enters here and is spray-quenched
    by N8 (24.31 kg/d tower water, X-SAF-07) so the spool stays wetted and the gas
    leaves below the FRP limit (duty section 3). Spool dimensions study values.
  * PVDF mesh pad - OD 508 x 16 disc at z 620..636 on a PVDF support ring (OD 520 x
    ID 488 x 10 at z 610..620), under the top head; the pad is the demister duty
    section 3 names. Dimensions study values.
  * weir and launder - layout solids from the section 1/3 knock-out separation duty
    (the FLOAT_SINK idiom): FRP weir plate at the shell centreline (x 495..505, to
    z 360) dividing the settle zone from the overflow zone; FRP launder trough at
    the +X side (channel floor z 300..310, lip plate to an overflow lip top z 360).
    The separation duty behind the layout is unsized (duty section 8: no holdup
    basis) - named hold (W12).
- Material: FRP vinyl ester with C-veil liner (duty section 3, AQS-STD-002 section
  8 audit row) for shell, heads, weir and launder; borosilicate glass 3.3 for the
  inlet spool; PVDF for the mesh pad and support. No metal wetted part. CA does not
  apply to the polymers or the glass.
- Nozzles: all 8 rows of docs-authority/nozzles/FLUE_KO.csv drawn at tag, face,
  height and bore. Atmospheric tube or hose per duty section 4: hose barbs flush at
  the envelope faces (the shell stands 30 off the +/-Y faces, within the barb
  reach), the schedule rating column (Class 150) carried verbatim as text, no
  flange (W4 110 % rule - no process pressure stated). N6 drain boss on the base
  head, tip at its 50 datum; N7 vent flush at the top head - the 800 datum IS the
  envelope top, drawn exact. The duty sheet section 4 inline rows (550 heights) are
  unit-task-04 placeholders against the issued schedule (hold, W12).
- A-VES: the condensate sump volume below the weir lip is computed from the model
  and reported; the duty claims no holdup (section 8), so no residence time is
  derived from the model volume.
"""
import csv, json, math, pathlib, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import dn, fasteners, materials, nozzles          # noqa: E402

P = json.loads((HERE / "params.json").read_text())
L, W, H = (float(v) for v in P["size_mm"])                 # 1000 x 600 x 800, study registry box
REV = P["graph_revision"]

T_PLINTH = 20.0
T_WALL = 8.0                    # study FRP wall - no authority states one (WORK_ORDER W12)
D, CX, CY = min(L, W) - 60.0, L / 2, W / 2   # shell OD 540; 30 mm stand-off to the +/-Y faces
R_IN = D / 2 - T_WALL                                       # 262
Z_SH0, Z_SH1 = 40.0, H - 40.0                               # shell 40..760
T_HEAD = 20.0
SPOOL_OD, SPOOL_WALL = 110.0, 3.0                           # glass inlet spool (study)
SPOOL_Z, SPOOL_LEN = 300.0, 300.0                           # centreline, reach into the shell
PAD_OD, PAD_T = 508.0, 16.0                                 # PVDF mesh pad (study)
PAD_Z = 620.0
SUP_Z = 610.0                                              # support top laps the pad
SUP_OD, SUP_ID, SUP_T = 532.0, 488.0, 11.0                  # pad support ring (study):
# OD 532 laps 4 mm into the shell wall band (radius 262..270); top laps the pad 1 mm
WEIR_X, WEIR_T, WEIR_TOP = 420.0, 10.0, 360.0                # weir plate (layout, study;
# x 420..430: clear of the spool envelope x 445..555 and clear of the launder)
WEIR_HALF = 250.0                                           # +/- y half-width at the centre chord
CHAN_X0, CHAN_X1 = 660.0, 750.0                             # launder channel floor (study):
# x to 750 embeds the floor corners into the +X wall band at the +/-100 y edges
CHAN_HALF, CHAN_Z, LIP_TOP = 100.0, 300.0, 360.0
CA = 0.0                                                    # polymer/glass: AQS-STD-001
RHO_FRP = materials.density("FRP")                          # 1800, lib table
RHO_GLASS = materials.density("borosilicate")               # 2230, lib table row
RHO_PVDF = materials.density("PVDF")                        # 1780, lib table

assert L == 1000.0 and W == 600.0 and H == 800.0, "FLUE_KO node envelope changed"
assert RHO_GLASS, "lib materials table lacks the borosilicate row"


def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))


parts = {}

# ---------------------------------------------------------------- plinth + shell + heads
plinth = box(0, 0, 0, L, W, T_PLINTH)
parts["plinth"] = plinth
shell = (cq.Workplane("XY", origin=(CX, CY, Z_SH0)).circle(D / 2)
         .circle(R_IN).extrude(Z_SH1 - Z_SH0))
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, Z_SH1)).circle(D / 2)
                    .extrude(T_HEAD))                                        # top head 760..780
shell = shell.union(cq.Workplane("XY", origin=(CX, CY, 0)).circle(D / 2)
                    .extrude(T_PLINTH + T_HEAD))                             # base head laps plinth
parts["shell"] = shell

# ---------------------------------------------------------------- glass inlet spool (duty section 3)
spool = (cq.Workplane("XY").circle(SPOOL_OD / 2).circle(SPOOL_OD / 2 - SPOOL_WALL)
         .extrude(SPOOL_LEN))
spool = nozzles.place_on_face(spool, "-Y", SPOOL_Z, (CX, CY), (L, W, H))
parts["inlet_spool"] = spool

# ---------------------------------------------------------------- PVDF mesh pad + support
pad = (cq.Workplane("XY", origin=(CX, CY, PAD_Z)).circle(PAD_OD / 2).extrude(PAD_T))
support = (cq.Workplane("XY", origin=(CX, CY, SUP_Z)).circle(SUP_OD / 2)
           .circle(SUP_ID / 2).extrude(PAD_Z + 1.0 - SUP_Z))
parts["mesh_pad"] = pad.union(support)

# ---------------------------------------------------------------- weir + launder (layout solids)
weir = box(WEIR_X, CY - WEIR_HALF, 35.0, WEIR_T, 2 * WEIR_HALF,
           WEIR_TOP - 35.0 + 5)                            # laps the base head by 5
parts["weir"] = weir
launder = box(CHAN_X0, CY - CHAN_HALF, CHAN_Z, CHAN_X1 - CHAN_X0, 2 * CHAN_HALF, 10)
launder = launder.union(box(CHAN_X1 - 10.0, CY - CHAN_HALF, CHAN_Z,
                            10.0, 2 * CHAN_HALF, LIP_TOP - CHAN_Z + 5))
parts["launder"] = launder

# ---------------------------------------------------------------- nozzles (schedule verbatim)
Hose = {"DN15": 45.0, "DN25": 50.0, "DN50": 60.0}          # barb lengths, study proportions
FACE_OF = {"inlet": "-Y", "outlet": "+Y"}


def hose_id(dnl):
    return round(dn.pipe_od(dnl) - 2 * dn.pipe_wall(dnl), 2)


schedule = [r for r in P["nozzles"]]
groups = {}
for r in schedule:
    face = FACE_OF.get(r["face"], r["face"])
    if face in ("-Y", "+Y"):
        groups.setdefault((face, float(r["height_mm"])), []).append(r)

layout_x = {}
for (face, z), rows in sorted(groups.items()):
    rows = sorted(rows, key=lambda r: (-dn.pipe_od(r["size"]), r["tag"]))
    span = sum(dn.pipe_od(r["size"]) + 8.0 for r in rows) - 8.0
    assert span <= L - 80.0, (face, z, span)
    x = CX - span / 2
    for r in rows:
        w = dn.pipe_od(r["size"]) / 2
        layout_x[r["tag"]] = round(x + w, 1)
        x += 2 * w + 8.0

noz, drawn = None, {}
for r in schedule:
    tag, dnl, h = r["tag"], r["size"], float(r["height_mm"])
    face = FACE_OF.get(r["face"], r["face"])
    od = dn.pipe_od(dnl)
    note = "atmospheric hose joint at the envelope face (duty section 4)"
    if r["face"] == "bottom":                             # N6: boss on the base head
        s = nozzles.stub(dnl, 50.0)
        s = nozzles.place_on_face(s, "bottom", 0.0, (CX + 60.0, CY), (L, W, H))
        note = "drain boss on the base head, tip at the 50 datum"
    elif r["face"] == "top":                              # N7: the 800 datum IS the envelope top
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, "top", 0.0, (CX + 80.0, CY), (L, W, H))
        note = "vent flush at the top head, the 800 envelope top"
    else:
        h_d = min(h, H - od / 2 - 5.0)
        if h_d < h:
            note += (f"; schedule datum {h:g} mm clamped to {round(h_d, 1)} mm "
                     "(barb radius rule) - WORK_ORDER W12")
        s = nozzles.hose_barb(hose_id(dnl), Hose[dnl], root_od=od)
        s = nozzles.place_on_face(s, face, h_d, (layout_x[tag], W / 2), (L, W, H))
    noz = s if noz is None else noz.union(s)
    drawn[tag] = {"style": "hose", "dn": dnl, "face": face, "height_mm": h,
                  "drawn_height_mm": round(min(h, H - od / 2 - 5.0), 1)
                  if face in ("-Y", "+Y") else (0.0 if r["face"] == "bottom" else H),
                  "x_mm": layout_x.get(tag), "schedule_rating": r["rating"], "note": note}
parts["nozzles"] = noz

# ---------------------------------------------------------------- sump volume (reported, A-VES)
z_floor = T_PLINTH + T_HEAD
v_settle = math.pi * R_IN ** 2 * (WEIR_TOP - z_floor) / 2 / 1e9      # half-drum settle zone
v_launder = (CHAN_X1 - CHAN_X0 - 10) * 2 * CHAN_HALF * 10 / 1e9
v_sump = round(v_settle, 4)

# ---------------------------------------------------------------- export
asm = cq.Assembly(name="FLUE_KO")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "flue_ko.step"))

solid = None
for k, v in parts.items():
    solid = v if solid is None else solid.union(v)
solid = solid.val()
assert len(solid.Solids()) == 1, f"assembly split into {len(solid.Solids())} solids"
solid.exportStl(str(out / "flue_ko.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
# cad/stl is the envelope registry in metres (X-PAR-04), ASCII like every registered unit.
solid.scale(0.001).exportStl(str(HERE.parents[2] / "cad" / "stl" / "FLUE_KO.stl"),
                             tolerance=0.0005, angularTolerance=0.4, ascii=True)

# ---------------------------------------------------------------- checks + report
# the bounding box is read back from the exported STL - the same measure the tracker
# gate reads - because the OCC Bnd_Box of the lofted barb faces is loose
from tracker import stl_bbox_mm   # noqa: E402  (gate-consistent STL reader, models/mfg)

dims = stl_bbox_mm(str(out / "flue_ko.stl"))
inside = all(d <= s + 1.0 for d, s in zip(dims, [L, W, H]))
RHO_OF = {"shell": RHO_FRP, "plinth": RHO_FRP, "weir": RHO_FRP, "launder": RHO_FRP,
          "inlet_spool": RHO_GLASS, "mesh_pad": RHO_PVDF, "nozzles": RHO_PVDF}
mass = {k: round(v.val().Volume() * RHO_OF.get(k, RHO_FRP) / 1e9, 1)
        for k, v in parts.items()}
report = {
    "bbox_mm": dims, "inside_size_mm": inside,
    "size_mm": [L, W, H],
    "size_basis": "study registry box (params size_note; matches the fab study "
    "page); the duty sheet section 4 still carries the unit-task-04 line "
    "600 x 700 x 1100 (WORK_ORDER W12)",
    "graph_revision": REV,
    "solids": len(solid.Solids()), "all_parts_valid": all(v.val().isValid() for v in parts.values()),
    "holdup_m3": v_sump,
    "holdup_basis": "reported, no residence derived: the duty claims no holdup for "
    "this class (section 8) (A-VES)",
    "ko_drum": {"wall_mm": T_WALL, "wall_basis": "study value - no authority states "
                "an FRP thickness (WORK_ORDER W12)",
                "internals": {"source": "duty section 3 (glass inlet spool, PVDF mesh "
                              "pad) and the section 1/3 knock-out separation duty "
                              "(weir and launder layout solids, the FLOAT_SINK idiom)",
                              "inlet_spool": {"od_mm": SPOOL_OD, "wall_mm": SPOOL_WALL,
                                              "z_mm": SPOOL_Z, "reach_mm": SPOOL_LEN,
                                              "note": "S67 at 300 C quenched by N8 "
                                              "(X-SAF-07) so the spool stays wetted"},
                              "mesh_pad": {"od_mm": PAD_OD, "t_mm": PAD_T, "z_mm": [PAD_Z, PAD_Z + PAD_T],
                                           "support": {"od_mm": SUP_OD, "id_mm": SUP_ID,
                                                       "t_mm": SUP_T, "z_mm": [SUP_Z, PAD_Z + 1]}},
                              "weir": {"x_mm": [WEIR_X, WEIR_X + WEIR_T],
                                       "top_z_mm": WEIR_TOP},
                              "launder": {"channel_x_mm": [CHAN_X0, CHAN_X1],
                                          "floor_z_mm": [CHAN_Z, CHAN_Z + 10],
                                          "lip_top_z_mm": LIP_TOP},
                              "basis": "internals named by the duty section 3 or "
                              "layout solids from the separation duty; dimensions "
                              "study values (WORK_ORDER W12); node internals row "
                              "none, so the tracker records no internal solid"}},
    "material": {"class": "FRP vinyl ester + borosilicate 3.3 + PVDF", "ca_mm": CA,
                 "basis": "duty section 3 (AQS-STD-002 section 8 audit row): FRP "
                 "vessel with C-veil liner, PVDF mesh pad, borosilicate glass 3.3 "
                 "inlet spool; no metal wetted part; corrosion allowance does not "
                 "apply"},
    "nozzles_drawn": drawn,
    "nozzle_count_schedule": len(schedule),
    "nozzle_idiom": "atmospheric hose barbs flush at the envelope faces (the shell "
    "stands 30 off the +/-Y faces, within the barb reach); the schedule rating "
    "column (Class 150) is carried verbatim as text, no flange drawn",
    "part_mass_kg": mass, "cadquery": cq.__version__,
}
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")

# ---------------------------------------------------------------- BOM (generated from the model)
rows = [
    ["1", f"Shell OD {D:g}, wall {T_WALL:g} mm FRP vinyl ester with C-veil liner, "
          f"z {Z_SH0:g}..{Z_SH1:g}, with heads, on a {L:g} x {W:g} plinth", 1,
     "FRP vinyl ester", round(mass["shell"] + mass["plinth"], 1), "make",
     "duty section 3 (AQS-STD-002 section 8 audit row); wall a study value "
     "(WORK_ORDER W12); CA does not apply"],
    ["2", f"Borosilicate glass 3.3 inlet spool, OD {SPOOL_OD:g} x wall {SPOOL_WALL:g}, "
          f"z {SPOOL_Z:g}, reach {SPOOL_LEN:g} mm into the shell", 1, "borosilicate 3.3",
     mass["inlet_spool"], "make",
     "duty section 3: the 300 C S67 spool is quenched by N8 (X-SAF-07) and stays "
     "wetted; dimensions study values (WORK_ORDER W12)"],
    ["3", f"PVDF mesh pad, OD {PAD_OD:g} x {PAD_T:g} at z {PAD_Z:g}, on a support "
          f"ring OD {SUP_OD:g} x ID {SUP_ID:g}", 1, "PVDF", mass["mesh_pad"], "make",
     "duty section 3 mesh pad; dimensions study values (WORK_ORDER W12)"],
    ["4", f"Weir plate at the shell centreline to z {WEIR_TOP:g} and launder trough "
          f"(channel floor z {CHAN_Z:g}, overflow lip z {LIP_TOP:g})", 1,
     "FRP vinyl ester", round(mass["weir"] + mass["launder"], 1), "make",
     "layout solids from the section 1/3 knock-out separation duty (FLOAT_SINK "
     "idiom); the separation duty is unsized (duty section 8, hold WORK_ORDER W12); "
     "node internals row none"],
    ["5", "Nozzle set per docs-authority/nozzles/FLUE_KO.csv: 6 hose barbs "
          "(DN15/DN25/DN50), 1 drain boss, 1 vent at the top head", len(schedule),
     "PVDF", mass["nozzles"], "make",
     "schedule tags/faces/heights verbatim; atmospheric hose per duty section 4; "
     "barb profile a study proportion (lib/nozzles.py)"],
]
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "description", "qty", "material", "mass_kg", "make_or_buy", "basis"])
    w.writerows(rows)

# ---------------------------------------------------------------- fasteners (W5)
fasteners.write_fasteners(HERE / "fasteners.csv", [
    [None, "M10 wedge anchor", fasteners.grade_for("FRP", joint="polymer"), 4,
     "plinth to slab, one per corner (count from the model)",
     "polymer joint to the supplier rule (A4-70 hardware per house practice); study "
     "length, confirmed at fabrication"],
])

# ---------------------------------------------------------------- builder-owned params blocks
p = json.loads((HERE / "params.json").read_text())
p.pop("graph", None)
p["envelope"] = {
    "size_mm": [L, W, H],
    "basis": "study registry box (params size_note; matches the fab study page); "
             "the duty sheet section 4 line is a unit-task-04 placeholder (W12)",
    "shell": {"od_mm": D, "z_mm": [Z_SH0, Z_SH1]},
}
p["design"] = {
    "service": "flue knock-out: 300 C S67 quenched in the glass spool to below the "
               "FRP limit, condensate knocked out, gas to the NOx scrubber "
               "(duty sections 1, 3 and 6)",
    "wall_mm": T_WALL, "wall_basis": "study value", "ca_mm": CA,
    "internals": "glass inlet spool + PVDF mesh pad (duty section 3); weir + "
                 "launder layout solids from the separation duty",
}
p["layout"] = {
    "frame": "origin at the envelope corner; shell axis at x 500, y 300, z up",
    "nozzle_spread": "the schedule gives face and height only; ports pack centred on "
                     "the face mid-length; per-tag positions in check.nozzles_drawn",
    "vent_drain": "N7 vent flush at the top head (the 800 datum IS the box top); "
                  "N6 drain boss on the base head, tip at the 50 datum",
    "hardware_idiom": "connection hardware flush at the envelope faces; nothing "
                      "protrudes, bbox within the node envelope",
}
(HERE / "params.json").write_text(json.dumps(p, indent=1) + "\n")

print(json.dumps({k: report[k] for k in ("bbox_mm", "inside_size_mm", "solids",
                                         "holdup_m3", "nozzle_count_schedule",
                                         "part_mass_kg")}), flush=True)
