"""RABBIT_HUTCH manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only, and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the hutch, y along the depth, z up, origin at the frame
corner. Every dimension is an authority figure or a named layout choice:

- Frame per the node: size_mm 1900 x 700 x 1600, hot-dip galvanised steel
  ("3 rabbitry positions x 0.5 m2 with rest mats (A-M-423; TECHTREE rabbits.md)"
  - size_basis). The Oct-31 frame build is confirmed as issued: four 40 x 40
  legs, drop board at z 100, wire floor at z 300, wire panel bands at
  z 300..550 and z 1350..1600, sheet roof at z 1500. The rebuild fills the box
  exactly (A-core 2; A-FARM: not shrunk to fit the block).
- The hardware the duty section 3 names beside the form is drawn as named
  envelopes inside size_mm (plan rule 6): three HDPE rest mats on the wire
  floor (one per position, the welfare contact surface against sore hocks),
  the PP nest boxes (one per doe) and the SS316 waterer line. The drop board
  at z 100 is the manure board the duty names: cold manure goes direct to the
  mineralisation zone.
- Nozzles: all 6 rows of docs-authority/nozzles/RABBIT_HUTCH.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose; bores are not recalculated). Inlet N1 on -Y at z 160 (canopy
  thinnings/greens forage); outlets N2, N3, N4 on +Y at z 600 (dressed meat,
  manure, evaporation); N5 drain flush at the envelope bottom (the 50 datum is
  the schedule placeholder at the base); N6 vent flush at the envelope top
  (the schedule z 800 datum predates the 1600 box - stale datum, hold W12).
  The duty notes the elevations are schedule placeholders (unit tasks 02/06);
  the wall is wire, so the wall backing for each stub is a fabrication detail
  (hold, W12). No flange is drawn (W4 110 % rule); the schedule rating column
  (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "RABBIT_HUTCH"


def rest_mats(P):
    """The HDPE rest mats duty section 3 names, one per rabbitry position, laid
    on the wire floor (the welfare contact surface against sore hocks)."""
    m = None
    for px in (280.0, 760.0, 1240.0):
        q = farm_closeout.box(px, 140.0, 299.0, 380.0, 420.0, 12.0)   # laps the
                                                                      # wire floor
        m = q if m is None else m.union(q)
    return m


def nest_boxes(P):
    """The PP nest boxes duty section 3 names (one per doe): drawn as one named
    envelope at the +X end above the wire floor (plan rule 6)."""
    return farm_closeout.box(1550.0, 180.0, 360.0, 290.0, 340.0, 320.0)


def waterers(P):
    """The SS316 waterer line duty section 3 names: drawn as one named envelope
    on the -Y front beside the nest boxes (plan rule 6)."""
    return farm_closeout.box(1150.0, 40.0, 360.0, 260.0, 60.0, 180.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"rest_mats": "HDPE", "nest_boxes": "PP", "waterers": "316L"},
    "drop_keys": (),
    "extras": {"rest_mats": rest_mats, "nest_boxes": nest_boxes,
               "waterers": waterers},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 1900 x 700 x 1600 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlet N1 on -Y at z 160, outlets N2/N3/N4 on +Y at "
                    "z 600; N5 drain flush at the envelope bottom (the 50 datum "
                    "is the schedule placeholder at the base); N6 vent flush at "
                    "the envelope top (schedule z 800 predates the 1600 box - "
                    "stale datum, hold W12); the elevations are schedule "
                    "placeholders (duty tasks 02/06) and the wire wall takes a "
                    "backing plate at each stub at fabrication (hold W12); no "
                    "flange drawn (W4 110 % rule); the schedule rating column "
                    "(Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "rabbitry, 2 does + 1 buck (A-M-423; X-FARM-07): HDG wire-frame hutch "
                "1900 x 700 x 1600, 3 positions x 0.5 m2, drop board at z 100 "
                "(cold manure direct to the mineralisation zone), wire floor at "
                "z 300, 3 HDPE rest mats, PP nest boxes and an SS316 waterer "
                "line drawn as named envelopes",
        "a_farm": "the hutch is drawn at the node box flush; the rest-mat, "
                  "nest-box and waterer envelopes, the manure board and the "
                  "nozzles are drawn",
        "positions": "the form carries the 3-position floor basis in the size "
                     "and the mat count; the position dividers are a fabrication "
                     "detail (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDG frame: 4 legs 40 x 40 to z 1500, sheet roof at z 1500", 1,
         "hot-dip galvanised steel (duty section 3)",
         mass["frame_legs"] + mass["roof"], "make",
         "size_basis verbatim (A-M-423); frame weldment, AQS-MOD-002 farm frame "
         "class"],
        ["2", "Drop board 3 mm at z 100 - the manure board; cold manure goes "
              "direct to the mineralisation zone (duty section 3)", 1,
         "HDG sheet (duty section 3)", mass["drop_board"], "make",
         "the manure outlet N3 lands on this board; the board is the wetted "
         "surface, HDG per the duty dry-pellet basis"],
        ["3", "Weld-wire floor at z 300 + panel bands at z 300..550 and "
              "z 1350..1600 (1 mm wire class)", 1,
         "hot-dip galvanised wire (duty section 3)",
         mass["floor_wire"] + mass["wire_panels"], "buy",
         "drawn as plate solids; the mesh open area carries ~0.15 of the plate "
         "mass (the hardware-cloth idiom); buy panels cut to size, plan rule 6"],
        ["4", "HDPE rest-mat envelope: 3 mats 380 x 420 x 12 on the wire floor, "
              "one per position", 1, "HDPE (duty section 3)", mass["rest_mats"],
         "buy",
         "drawn as its envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the HDPE table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["5", "PP nest-box envelope 290 x 340 x 320 at (1550, 180, 360) - one "
              "box per doe", 1, "PP (duty section 3)", mass["nest_boxes"],
         "buy",
         "drawn as its box envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the PP table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["6", "SS316 waterer line envelope 260 x 60 x 180 at (1150, 40, 360)",
         1, "SS316 (duty section 3)", mass["waterers"], "buy",
         "drawn as its box envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the SS316 table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["7", "Nozzle set per docs-authority/nozzles/RABBIT_HUTCH.csv: 6 rows "
              "drawn as DN15 tube stubs (1 in z 160, 3 out z 600, drain, vent)",
         6, "galvanised fittings stock", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; bores not recalculated (duty "
         "section 4); atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M8 frame-section joint bolt", "ISO 898-1 8.8", 12,
         "frame and position-rail joints, 3 per leg line (study pattern)",
         "8.8 on carbon steel per the plan grade rule (galvanised frame joint); "
         "study pattern, confirmed at fabrication"],
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "frame legs to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "frame": {"leg_mm": 40, "wire_floor_z_mm": 300.0, "roof_z_mm": 1500.0},
        "rest_mats": {"mat_mm": [380.0, 420.0, 12.0], "at_x_mm": [280.0, 760.0, 1240.0],
                      "at_y_mm": 140.0},
        "nest_boxes": {"box_mm": [290.0, 340.0, 320.0], "at_mm": [1550.0, 180.0, 360.0]},
        "waterers": {"box_mm": [260.0, 60.0, 180.0], "at_mm": [1150.0, 40.0, 360.0]},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the frame corner; legs 40 x 40 at the 4 corners to "
                 "z 1500, drop board 3 mm at z 100, wire floor at z 300, panel "
                 "bands z 300..550 and z 1350..1600, roof at z 1500; the rest "
                 "mats lie on the wire floor, the nest boxes at the +X end, "
                 "the waterer line on the -Y front",
        "supports": "frame legs to the slab on 4 base anchors; frame sections "
                    "bolted at the legs (fasteners.csv)",
        "nozzle_spread": "the schedule gives face and height only; inlet N1 on "
                         "the -Y wall at z 160, outlet rows N2/N3/N4 on the +Y "
                         "wall at z 600, drain at the base centreline, vent at "
                         "the top centreline; per-tag positions in "
                         "check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; the "
                          "wire wall takes a backing plate at each stub at "
                          "fabrication (hold W12)",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
