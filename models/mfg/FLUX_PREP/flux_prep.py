"""FLUX_PREP manufacturing model, AQS-PLAN-006 work order (X-FOUNDRY prep bench).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the bench length, y along the depth, z up, origin at the
bench corner. Every dimension is an authority figure or a named layout choice:

- The unit is the salt flux cover preparation bench per the node size basis: "prep
  class study minimum; live on the Kroll drag-out (A-M-284)". The build fills the
  node box 800 x 600 x 1200 flush: a 6 mm SS304 head-plate basin set as the open-top
  tray form (the mixing bench the duty section 3 names, kept dry), with the PP-H
  day-drum metering hopper envelope (the 20 L class the graph design names) at the
  -X floor and the 0.1 kW mixer stage envelope - the only powered part (duty
  section 3) - at the +X floor. The mixer drive purchases at fabrication (WORK_ORDER
  W12); the extraction hood of the former bench_prep build is withdrawn - the N5
  vent rides the basin rim.
- Nozzles: all 6 rows of docs-authority/nozzles/FLUX_PREP.csv drawn at tag, face and
  bore as atmospheric open-bore tube stubs flush at the envelope faces (duty section
  4; the schedule rating column Class 150 carried verbatim as text; no flange drawn,
  W4 110 % rule). N1 flux out on +Y at z 600; N2/N3 salt inlets on -Y at z 160
  (solids rows: drawn DN15, bore not calculated); N4 drain flush at the envelope
  bottom; N5 vent flush at the envelope top (the schedule z 800 datum sits below the
  1200 build height); N6 power terminal is a cable schedule row - carried in the
  record, never drawn.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "FLUX_PREP"


def _salt_hopper(P):
    # the 20 L PP-H day-drum metering hopper the graph design names (duty section 3)
    from farm_closeout import box
    return box(60.0, 150.0, 6.0, 300.0, 300.0, 300.0)


def _mixer(P):
    # the 0.1 kW mixer stage envelope: stand + shaft, the only powered part
    from farm_closeout import box
    return box(660.0, 260.0, 6.0, 80.0, 80.0, 500.0)


# The shared engine draws every schedule row as a stub (the GW_INTAKE schedule has
# no non-piped rows). The two row classes the duty schedule carries beside pipes
# are handled here, so geometry and record stay consistent: cable rows are carried,
# never drawn; solids rows keep their DN15 stub with the bore-not-calculated note.
_engine_draw_nozzles = farm_closeout.draw_nozzles


def _draw_nozzles(P, spec):
    noz, drawn = _engine_draw_nozzles(
        {**P, "nozzles": [r for r in P["nozzles"] if r["size"] != "cable"]}, spec)
    H = float(P["size_mm"][2])
    for r in P["nozzles"]:
        tag = r["tag"]
        if r["size"] == "cable":
            drawn[tag] = {"style": "carried", "dn": r["size"], "face": r["face"],
                          "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                          "service": r["service"],
                          "note": "power terminal row - a cable schedule row: carried "
                                  "verbatim, never drawn"}
        else:
            if r["size"] == "solids":
                drawn[tag]["note"] += ("; the solids row is a non-piped transfer: "
                                       "drawn DN15, bore not calculated (duty "
                                       "section 4)")
            if r["face"] == "top" and float(r["height_mm"]) < H - 1.0:
                drawn[tag]["note"] = drawn[tag]["note"].replace(
                    "predates the build height", "sits below the build height")
    return noz, drawn


farm_closeout.draw_nozzles = _draw_nozzles


SPEC = {
    "unit": UNIT,
    "extras": {"salt_hopper": _salt_hopper, "mixer": _mixer},
    "rho_map": {"basin_shell": "304", "salt_hopper": "PP", "mixer": "304",
                "nozzles": "304"},
    "drop_keys": ("layout_note",),
    "drain_xy": (110.0, 490.0),
    "vent_xy": (400.0, 300.0),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the build "
                     "fills the node box 800 x 600 x 1200 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N1 flux out on +Y at z 600; N2/N3 salt "
                    "inlets on -Y at z 160, solids rows drawn DN15 with the bore "
                    "not calculated; N4 drain flush at the envelope bottom; N5 "
                    "vent flush at the envelope top (the schedule z 800 datum "
                    "sits below the 1200 build height); N6 is a cable schedule "
                    "row, carried in the record, never drawn; no flange drawn "
                    "(W4 110 % rule); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "salt flux cover preparation bench: PP-H day-drum metering + 304L "
                "mixing basin kept dry, sealed anhydrous handling of the MgCl2-"
                "class drag-out (duty section 3; graph design); the 0.1 kW mixer "
                "is the only powered part",
        "a_farm": "the basin is drawn at the node box flush; the metering hopper "
                  "and the mixer stage are drawn",
        "purchased": "the 0.1 kW mixer drive purchases with the mixer stage at "
                     "fabrication (duty section 3 names the class, not a maker "
                     "figure) - plan rule 6 (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 mixing basin: 800 x 600 x 1200 mm open-top tray form, 6 mm "
              "plate (prep-class study box; A-M-284 Kroll drag-out basis)", 1,
         "SS304 (duty section 3)", mass["basin_shell"], "make",
         "size_basis verbatim; 304L wetted class at the dry salt service; the "
         "316L drum is the named alternative if the salt ever arrives as a "
         "slurry (duty section 3)"],
        ["2", "PP-H day-drum metering hopper envelope, 20 L class (300 x 300 x "
              "300)", 1, "PP-H (duty section 3)", mass["salt_hopper"], "make",
         "graph design hopper_L 20; anhydrous MgCl2-class handling: PP-H is the "
         "duty section 3 metering class"],
        ["3", "Mixer stage envelope 80 x 80 x 500 with the 0.1 kW drive class", 1,
         "SS304 stage (drive purchased)", mass["mixer"], "make",
         "graph design mixer_kW 0.1 - the only powered part (duty section 3); "
         "the drive purchases with the stage at fabrication (hold, WORK_ORDER "
         "W12)"],
        ["4", "Nozzle set per docs-authority/nozzles/FLUX_PREP.csv: 6 rows - 3 "
              "solids rows drawn as DN15 stubs (bore not calculated), drain, "
              "vent, and the N6 cable row carried, never drawn", 5, "SS304",
         mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 wedge anchor", "ISO 898-1 8.8", 4,
         "basin to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part); study embedment, confirmed at fabrication"],
        [None, "M8 socket bolt", "ISO 3506 A4-70", 8,
         "mixer stage and hopper hold-down to the basin floor, 4 each (study "
         "pattern)",
         "A4-70 on the 304/PP joints per the grade rule; study pattern, "
         "confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the bench corner; 6 mm SS304 basin 800 x 600 x 1200 "
                 "outer, open top; PP-H day-drum hopper at the -X floor, mixer "
                 "stage at the +X floor (the former extraction hood is "
                 "withdrawn - the vent rides the rim)",
        "supports": "basin to the slab on 4 wedge anchors; hopper and mixer "
                    "hold-down bolts to the basin floor",
        "nozzle_spread": "the schedule gives face and height only; N1 on the +Y "
                         "wall at z 600, N2/N3 on the -Y wall at z 160, N4 drain "
                         "at the -X floor corner, N5 vent at the top centreline; "
                         "per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
