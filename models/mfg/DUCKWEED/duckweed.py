"""DUCKWEED manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the raceway, y along the width, z up, origin at the basin
corner. Every dimension is an authority figure or a named layout choice:

- Basin per the node: size_mm 30100 x 10100 x 700 - "300 m2 raceway at the A-M-420
  revision, 400 mm water + 100 freeboard + 200 berm: a lined civil basin, HDPE/EPDM
  (X-FARM sec3)". The rebuild fills the box exactly (A-core 2; A-FARM: not shrunk
  to fit the block - the raceway is drawn at the node box flush).
- Liner per duty section 3: HDPE/EPDM lined civil basin - the EPDM liner sheet
  (5 mm, liner_mm) is drawn floor plus four walls (the GROW_BED ponded-zone
  idiom), a buy roll (plan rule 6).
- The 400 mm water line is a duty figure reported on the duty sheet; the water and
  the duckweed mat are process inventory, not BOM parts. The raceway flow layout
  (baffles, paddlewheel) has no node layout: not drawn (hold, W12).
- Nozzles: all 17 rows of docs-authority/nozzles/DUCKWEED.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15/DN50, no flange class, atmospheric tube or hose). N1 in
  on -Y at z 80 (nutrient water) with N2 beside it (DN50, nitrate water); N9/N17
  in on -Y at z 160; harvest rows N3-N6 on +Y at z 300 (the water line class);
  N10-N16 out on +Y at z 600 (the ration/forage/galley rows); N7 drain flush at
  the envelope bottom; N8 vent flush at the envelope top (the schedule z 400
  datum predates the 700 box - stale datum, hold W12). No flange is drawn (W4
  110 % rule); the schedule rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "DUCKWEED"

SPEC = {
    "unit": UNIT,
    "liner_bag": True,
    "liner_top_clearance": 200.0,               # the berm band stays bare (size_note)
    "rho_map": {"liner": "EPDM"},
    "drop_keys": (),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 30100 x 10100 x 700 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15/DN50, no flange class, atmospheric "
                    "tube or hose); N1 in on -Y at z 80 with N2 beside it (DN50), "
                    "N9/N17 in on -Y at z 160; N3-N6 out on +Y at z 300 (the "
                    "water-line harvest class), N10-N16 out on +Y at z 600; N7 "
                    "drain flush at the envelope bottom; N8 vent flush at the "
                    "envelope top (schedule z 400 predates the 700 box - stale "
                    "datum, hold W12); no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "duckweed raceway (Lemna minor, azolla co-culture; A-M-420): "
                "30100 x 10100 x 700 HDPE civil basin with the EPDM liner sheet "
                "5 mm floor and walls, 400 mm water + 100 freeboard + 200 berm "
                "(size_note)",
        "a_farm": "the raceway is drawn at the node box flush; the liner and the "
                  "drain are drawn",
        "water_line": "400 mm is the size_note water line - the water and the "
                      "duckweed mat are process inventory, not BOM parts",
        "flow_layout": "the raceway flow layout (baffles, paddlewheel) has no "
                       "node layout - not drawn (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE civil basin: walls and floor 10 mm, 30100 x 10100 x 700 "
              "outer (300 m2 raceway class, A-M-420)", 1, "HDPE (duty section 3)",
         mass["basin_shell"], "make",
         "size_mm verbatim; A-FARM: drawn at the node box flush; CA does not "
         "apply to the polymer (AQS-STD-001)"],
        ["2", "EPDM liner sheet 5 mm: floor + four walls, berm band bare", 1,
         "EPDM (duty section 3)", mass["liner"], "buy",
         "A-FARM: liner drawn; sheet roll goods, buy roll (plan rule 6); "
         "supplier TDS at order (hold, WORK_ORDER W12)"],
        ["3", "Nozzle set per docs-authority/nozzles/DUCKWEED.csv: 17 rows drawn "
              "as DN15/DN50 tube stubs (in z 80/160, harvest z 300, ration rows "
              "z 600, drain, vent)", 17, "HDPE/CPVC tube", mass["nozzles"],
         "make", "schedule tags/faces/heights verbatim (N2 is the DN50 row); "
         "atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M12 batten strip bolt", "ISO 3506 A4-70", 24,
         "liner batten strips to the basin rim, 12 per long wall (study pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); the liner "
         "is held by batten strips, not adhesive; study pattern, confirmed at "
         "fabrication"],
        [None, "M12 base hold-down anchor", "ISO 898-1 8.8", 8,
         "basin rim to the pad, long-wall spacing (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"), "liner_mm": P.get("liner_mm"),
        "water_line_mm": 400, "freeboard_mm": 100, "berm_mm": 200,
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the basin corner; basin 30100 x 10100 x 700 outer, "
                 "walls and floor 10 mm; liner sheet floor + walls to the berm "
                 "base (z 500), berm band bare",
        "supports": "basin rim to the pad on long-wall anchors; liner held by "
                    "rim batten strips",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 80 and z 160, harvest rows on +Y at "
                         "z 300, ration/forage rows on +Y at z 600, drain at "
                         "the base centreline, vent at the top centreline; "
                         "per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
