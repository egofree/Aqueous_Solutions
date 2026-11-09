"""POLY_FIBER manufacturing model, AQS-PLAN-006 work order (X-POLY melt-spin line).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the line, y along the depth, z up, origin at the cabinet
corner. Every dimension is an authority figure or a named layout choice:

- The unit is the bench-scale melt-spin line per the node size basis: "extruder +
  spinnerette + quench + winder at the 0.09 kg/d draw (A-M-429) (X-POLY sec3)
  (sheet-metal cabinet class, 5 mm)". The build fills the node box 3100 x 1300 x
  1900 flush: a 5 mm SS304 sheet cabinet (walls, floor, top) carrying the line the
  size_basis names as the params `extras_mm` envelopes - extruder trough and
  quench/winder housing (the registered envelopes, confirmed) plus the duty
  section 3 hardware the form lacked: melt heater-band envelope and spin-head
  (brass-free die plate) envelope inside the extruder trough, the PP quench-duct
  envelope beside the winder, and the phosphorus-FR dosing-skid envelope
  (PP/PTFE contact, duty section 3) at the free +X floor. The spin pump and
  drive set purchase at fabrication (plan rule 6; WORK_ORDER W12).
- Nozzles: all 7 rows of docs-authority/nozzles/POLY_FIBER.csv drawn at tag, face
  and bore as atmospheric open-bore tube stubs flush at the envelope faces (duty
  section 4; the schedule rating column Class 150 carried verbatim as text; no
  flange drawn, W4 110 % rule). N1 pellet draw and N2 FR finish in on -Y at
  z 160; N3 spin scrap and N4 fleece out on +Y at z 600; N5 drain flush at the
  envelope bottom; N6 vent flush at the envelope top (the schedule z 800 datum
  sits below the 1900 build height); N7 power terminal is a cable schedule row -
  carried in the record, never drawn.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "POLY_FIBER"

# The shared engine draws every schedule row as a stub (the AQUA_TANK-line
# schedules have no non-piped rows). The two row classes this schedule carries
# beside pipes are handled here, so geometry and record stay consistent: the
# cable row is carried, never drawn; DN15 pipe rows take the engine record.
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
        elif r["face"] == "top" and float(r["height_mm"]) < H - 1.0:
            drawn[tag]["note"] = drawn[tag]["note"].replace(
                "predates the build height", "sits below the build height")
    return noz, drawn


farm_closeout.draw_nozzles = _draw_nozzles


SPEC = {
    "unit": UNIT,
    "rho_map": {"cabinet_shell": "304", "top": "304", "extruder": "304",
                "quench_winder": "304", "melt_heater": "304", "spin_head": "304",
                "quench_duct": "PP", "fr_dose_skid": "PP", "nozzles": "304"},
    "drop_keys": (),
    "drain_xy": (300.0, 650.0),
    "vent_xy": (1550.0, 650.0),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the build "
                     "fills the node box 3100 x 1300 x 1900 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N1 pellet draw and N2 FR finish in on -Y at "
                    "z 160; N3 spin scrap and N4 fleece out on +Y at z 600; N5 "
                    "drain flush at the envelope bottom; N6 vent flush at the "
                    "envelope top (the schedule z 800 datum sits below the 1900 "
                    "build height); N7 is a cable schedule row, carried in the "
                    "record, never drawn; no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "PP melt-spin staple-fiber line to FR-finished fleece: SS304 sheet "
                "cabinet 3100 x 1300 x 1900 with the extruder trough, melt "
                "heater bands, spin head (brass-free die plate), quench/winder "
                "housing, PP quench duct and the FR finish dosing skid (size_"
                "basis A-M-429; duty section 3)",
        "a_farm": "the cabinet is drawn at the node box flush; the line housings "
                  "named by the size_basis and duty section 3 are drawn",
        "no_copper": "no copper alloys touch the melt (PP degrades against copper "
                     "at melt temperature, duty section 3): the die plate and "
                     "melt path are the 304 class",
        "fr_finish": "the phosphorus-FR dosing skid is PP/PTFE-contact (duty "
                     "section 3); the finish rides the D-DOCK reagent manifest, "
                     "the WS_SOLV reagent-import class (A-M-225)",
        "purchased": "the spin pump and drive set purchase at fabrication with "
                     "the 0.3 kW node duty class (plan rule 6; hold, WORK_ORDER "
                     "W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 sheet cabinet: 3100 x 1300 x 1900, 5 mm walls, floor and top "
              "(sheet-metal cabinet class per size_basis)", 1, "SS304",
         mass["cabinet_shell"] + mass["top"], "make",
         "size_basis verbatim (A-M-429); PP melt contact per duty section 3"],
        ["2", "Extruder trough housing 800 x 400 x 500 (sheet box, open top)", 1,
         "SS304 (duty section 3)", mass["extruder"], "make",
         "the melt vessel and screw housing; PP is non-wetting to the 304 class "
         "at the bench throughput (A-M-429)"],
        ["3", "Melt heater-band envelope 150 x 100 x 150 in the trough", 1,
         "SS304 band (duty section 3)", mass["melt_heater"], "make",
         "heater bands on the melt path; the band units purchase with the drive "
         "set (hold, WORK_ORDER W12)"],
        ["4", "Spin head (spinnerette) envelope 200 x 100 x 150, brass-free die "
              "plate", 1, "SS304 die (duty section 3)", mass["spin_head"], "make",
         "stainless die plate per duty section 3; a 316L die plate is the named "
         "alternative if FR-finish chemistry shows die corrosion"],
        ["5", "Quench/winder housing 1500 x 400 x 400 (sheet box, open top)", 1,
         "SS304 (duty section 3)", mass["quench_winder"], "make",
         "spin pump and winder purchased with the drive set (plan rule 6)"],
        ["6", "PP quench-duct envelope 1500 x 100 x 300 beside the winder", 1,
         "PP duct (duty section 3)", mass["quench_duct"], "make",
         "PP quench ducting per duty section 3"],
        ["7", "Phosphorus-FR finish dosing skid envelope 300 x 300 x 400", 1,
         "PP/PTFE contact (duty section 3)", mass["fr_dose_skid"], "make",
         "the ~2 % pick-up FR finish (A-M-225); skid contact PP/PTFE per duty "
         "section 3"],
        ["8", "Spin pump + drive set, purchased, 0.3 kW node duty class", 1,
         "purchased drive set (envelope)", 0.0, "buy",
         "node electrical duty 0.3 kW - the rating from the node; purchased per "
         "plan rule 6; the maker's mass governs (hold, WORK_ORDER W12)"],
        ["9", "Nozzle set per docs-authority/nozzles/POLY_FIBER.csv: 7 rows - 6 "
              "DN15 stubs (pellet, FR finish, scrap, fleece, drain, vent) and "
              "the N7 cable row carried, never drawn", 6, "SS304",
         mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M12 wedge anchor", "ISO 898-1 8.8", 4,
         "cabinet to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a melt-path "
         "part); study embedment, confirmed at fabrication"],
        [None, "M10 socket bolt", "ISO 3506 A4-70", 8,
         "extruder and quench/winder housings to the cabinet floor, 4 each "
         "(study pattern)",
         "A4-70 on the SS304 joints per the grade rule; study pattern, "
         "confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "line_housings_mm": {r[6]: r[:6] for r in P.get("extras_mm", [])},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the cabinet corner; 5 mm SS304 sheet cabinet 3100 x "
                 "1300 x 1900; extruder trough at the -X end with the heater-"
                 "band and spin-head envelopes inside, quench/winder housing "
                 "mid-line, quench duct along its +Y side, FR dose skid at the "
                 "+X floor",
        "supports": "cabinet to the slab on 4 wedge anchors; housings bolted to "
                    "the cabinet floor",
        "nozzle_spread": "the schedule gives face and height only; N1/N2 on the "
                         "-Y wall at z 160, N3/N4 on the +Y wall at z 600, drain "
                         "at the -X floor, vent at the top centreline; per-tag "
                         "positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; no "
                          "copper alloys on the melt path",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
