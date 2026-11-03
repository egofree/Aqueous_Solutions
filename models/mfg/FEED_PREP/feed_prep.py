"""FEED_PREP manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the cabinet, y along the depth, z up, origin at the
cabinet corner. Every dimension is an authority figure or a named layout choice:

- Cabinet per the node: size_mm 1300 x 900 x 1700 - "mixer + grinder + HP drier
  cabinet at the 0.6 kW duty (A-M-426) (X-FARM sec3) (sheet-metal cabinet class,
  5 mm)". SS304 sheet 5 mm (walls and floor), top plate 5 mm. The rebuild fills
  the box exactly (A-core 2; A-FARM: not shrunk to fit the block).
- The machine the size_basis names is drawn as its housings: the mixer trough
  and the drier stack (the Oct-31 `extras_mm` hollow boxes, confirmed), plus the
  grinder housing the size_basis names (SS304 hollow box between mixer and drier
  at x 510..690; study layout, hold W12). The drives are purchased per plan
  rule 6: the 0.6 kW duty class is the node rating (A-M-426) and the HP drier
  runs on the storage draw only (node design).
- Duty section 3: "SS304 contact surfaces and mixing troughs, PP feed bins,
  quartz-sleeve drier ducting; no copper-bearing alloys on any feed path" - the
  drier stack is the quartz-sleeve duct housing (material note).
- Nozzles: all 13 rows of docs-authority/nozzles/FEED_PREP.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose). Inlets N1 (fresh duckweed), N2 (dried larvae meal), N3 (eggshell
  return), N11 (fresh larvae to the drier) on -Y at z 160; outlets N4 (layer
  ration), N5 (quail ration), N6 (dry reserve), N7 (screenings return), N8
  (drying evaporation), N12 (duck mash), N13 (press water) on +Y at z 600; N9
  drain flush at the envelope bottom; N10 vent flush at the envelope top (the
  schedule z 800 datum predates the 1700 box - stale datum, hold W12). No
  flange is drawn (W4 110 % rule); the schedule rating column (Class 150) is
  carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "FEED_PREP"


def hollow_box(x, y, z, dx, dy, dz, wall=5.0):
    """The cabinet-extras housing idiom: box with an open-top inner cut."""
    b = farm_closeout.box(x, y, z, dx, dy, dz)
    return b.cut(farm_closeout.box(x + wall, y + wall, z, dx - 2 * wall,
                                   dy - 2 * wall, dz - wall))


def grinder_housing(P):
    return hollow_box(510.0, 100.0, 100.0, 180.0, 400.0, 400.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"grinder_housing": "304"},
    "drop_keys": (),
    "extras": {"grinder_housing": grinder_housing},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 1300 x 900 x 1700 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N2/N3/N11 on -Y at z 160, outlets "
                    "N4/N5/N6/N7/N8/N12/N13 on +Y at z 600; N9 drain flush at "
                    "the envelope bottom; N10 vent flush at the envelope top "
                    "(schedule z 800 predates the 1700 box - stale datum, hold "
                    "W12); no flange drawn (W4 110 % rule); the schedule rating "
                    "column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "ration formulation cabinet (A-M-426; A-M-416 no imported grain): "
                "SS304 cabinet 1300 x 900 x 1700 with the mixer trough, the "
                "grinder housing the size_basis names, and the HP drier stack - "
                "housings drawn, drives purchased per plan rule 6",
        "a_farm": "the cabinet is drawn at the node box flush; the drain and the "
                  "sec3-named housings are drawn",
        "purchased": "the mixer/grinder drive set and the HP drier unit are the "
                     "purchased items, named with the node rating (0.6 kW duty "
                     "class, A-M-426; the drier runs on the storage draw only, "
                     "node design) - plan rule 6",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 cabinet: sheet 5 mm walls and floor, 5 mm top "
              "(1300 x 900 x 1700)", 1, "SS304 (duty section 3)",
         mass["cabinet_shell"] + mass["top"], "make",
         "size_basis verbatim (A-M-426); food-contact sanitation class; no "
         "copper-bearing alloys on any feed path (duty section 3)"],
        ["2", "Mixer trough housing 400 x 400 x 500 (hollow sheet box)", 1,
         "SS304 (duty section 3)", mass["mixer_housing"], "make",
         "housing drawn; the drive is the purchased item below (plan rule 6)"],
        ["3", "Grinder housing 180 x 400 x 400 between mixer and drier", 1,
         "SS304 (duty section 3)", mass["grinder_housing"], "make",
         "the size_basis names the grinder; housing position is a study layout "
         "choice (hold, WORK_ORDER W12); the drive is the purchased item below"],
        ["4", "HP drier stack housing 400 x 400 x 900 with the quartz-sleeve "
              "duct class", 1, "SS304 + quartz sleeve (duty section 3)",
         mass["drier_stack"], "make",
         "duty section 3 quartz-sleeve ducting; the drier unit is the purchased "
         "item below"],
        ["5", "Mixer + grinder drive set, purchased, 0.6 kW duty class", 1,
         "purchased drive set (envelope)", 0.0, "buy",
         "node duty class 0.6 kW (A-M-426) - the rating from the node; purchased "
         "per plan rule 6; the maker's mass governs (hold, WORK_ORDER W12)"],
        ["6", "HP drier unit, purchased, on the storage draw only", 1,
         "purchased drier (envelope)", 0.0, "buy",
         "node design: drying serves only the A-M-270 dry-reserve draw "
         "(0.5 kg/d); purchased per plan rule 6 (hold, WORK_ORDER W12)"],
        ["7", "Nozzle set per docs-authority/nozzles/FEED_PREP.csv: 13 rows drawn "
              "as DN15 tube stubs (4 in z 160, 7 out z 600, drain, vent)", 13,
         "PP fittings (duty section 3)", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M8 cabinet base anchor", "ISO 898-1 8.8", 4,
         "cabinet to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a feed-path "
         "part)"],
        [None, "M6 drive-plate bolt", "ISO 3506 A4-70", 8,
         "mixer/grinder drive plates to their housings, 4 per drive (study "
         "pattern)",
         "A4-70 on the SS304 joint per the grade rule; NO copper-bearing alloys "
         "on any feed path (duty section 3); study pattern, confirmed at "
         "fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "housings": {"mixer_mm": [100.0, 100.0, 100.0, 400.0, 400.0, 500.0],
                     "grinder_mm": [510.0, 100.0, 100.0, 180.0, 400.0, 400.0],
                     "drier_mm": [700.0, 100.0, 100.0, 400.0, 400.0, 900.0]},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the cabinet corner; shell 1300 x 900 x 1700 outer, "
                 "sheet 5 mm; mixer trough at the -X end, grinder beside it, "
                 "drier stack at the +X end (all hollow housings to z 600/500)",
        "supports": "cabinet base anchors to the slab; drives bolted to their "
                    "housings",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, outlet rows on the +Y wall at "
                         "z 600, drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; no "
                          "copper-bearing alloys on any feed path",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
