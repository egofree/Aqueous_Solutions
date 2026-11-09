"""QUAIL_CAGE manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only, and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the cage, y along the depth, z up, origin at the frame
corner. Every dimension is an authority figure or a named layout choice:

- Frame per the node: size_mm 1300 x 700 x 1700, hot-dip galvanised steel
  ("20-hen Coturnix battery, 4 tiers x 0.075 m2/cage at the 0.025 kg/d ration
  class (A-M-422; TECHTREE coturnix.md)" - size_basis). The Oct-31 frame build is
  confirmed as issued: four 40 x 40 legs, drop board at z 100, wire floor at
  z 300, wire panel bands at z 300..550 and z 1450..1700, sheet roof at z 1600.
  The rebuild fills the box exactly (A-core 2; A-FARM: not shrunk to fit the
  block).
- The hardware the duty section 3 names beside the form is drawn as named
  envelopes inside size_mm (plan rule 6): the PP feeders (feed-hopper envelope)
  and the SS316 nipple-waterer line. The drop board at z 100 is the manure tray
  the duty names: droppings feed the vermi bin direct.
- Nozzles: all 9 rows of docs-authority/nozzles/QUAIL_CAGE.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose; bores are not recalculated). Inlets N1, N2, N8, N9 on -Y at z 160
  (duckweed/larvae ration, water, formulated ration, calcium carbonate);
  outlets N3, N4, N5 on +Y at z 600 (eggs, droppings, evaporation); N6 drain
  flush at the envelope bottom (the 50 datum is the schedule placeholder at the
  base); N7 vent flush at the envelope top (the schedule z 800 datum predates
  the 1700 box - stale datum, hold W12). The duty notes the elevations are
  schedule placeholders (unit tasks 02/06); the wall is weld wire, so the wall
  backing for each stub is a fabrication detail (hold, W12). No flange is drawn
  (W4 110 % rule); the schedule rating column (Class 150) is carried verbatim
  as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "QUAIL_CAGE"


def feed_hoppers(P):
    """The PP feeder line duty section 3 names, one hopper per tier: drawn as one
    named envelope along the -Y front above the wire floor (plan rule 6)."""
    return farm_closeout.box(120.0, 40.0, 360.0, 480.0, 120.0, 220.0)


def waterers(P):
    """The SS316 nipple-waterer line duty section 3 names, one nipple per tier:
    drawn as one named envelope on the -Y front beside the feed line (plan rule 6)."""
    return farm_closeout.box(820.0, 40.0, 360.0, 300.0, 60.0, 200.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"feed_hoppers": "PP", "waterers": "316L"},
    "drop_keys": (),
    "extras": {"feed_hoppers": feed_hoppers, "waterers": waterers},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 1300 x 700 x 1700 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N2/N8/N9 on -Y at z 160, outlets N3/N4/N5 "
                    "on +Y at z 600; N6 drain flush at the envelope bottom (the "
                    "50 datum is the schedule placeholder at the base); N7 vent "
                    "flush at the envelope top (schedule z 800 predates the 1700 "
                    "box - stale datum, hold W12); the elevations are schedule "
                    "placeholders (duty tasks 02/06) and the weld-wire wall takes "
                    "a backing plate at each stub at fabrication (hold W12); no "
                    "flange drawn (W4 110 % rule); the schedule rating column "
                    "(Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "coturnix quail cage battery, 20 hens (A-M-422; X-FARM-06): HDG weld-wire "
                "frame 1300 x 700 x 1700, 4 tiers x 0.075 m2/cage, drop board at "
                "z 100 (the manure tray - droppings feed the vermi bin direct), "
                "wire floor at z 300, PP feeders and SS316 nipple waterers drawn "
                "as named envelopes",
        "a_farm": "the cage is drawn at the node box flush; the feed and water "
                  "envelopes, the manure tray and the nozzles are drawn",
        "tiers": "the form carries the 4-tier ration basis in the size and the "
                 "feeder count; the tier rails are a fabrication detail (hold, "
                 "WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDG frame: 4 legs 40 x 40 to z 1600, sheet roof at z 1600", 1,
         "hot-dip galvanised steel (duty section 3)",
         mass["frame_legs"] + mass["roof"], "make",
         "size_basis verbatim (A-M-422); frame weldment, AQS-MOD-002 farm frame "
         "class"],
        ["2", "Drop board 3 mm at z 100 - the manure tray feeding the vermi bin "
              "direct (duty section 3)", 1, "HDG sheet (duty section 3)",
         mass["drop_board"], "make",
         "the droppings outlet N4 lands on this tray; the tray is the wetted "
         "surface, HDG per the duty dry-tray basis"],
        ["3", "Weld-wire cage panels: wire floor at z 300 + panel bands at "
              "z 300..550 and z 1450..1700 (1 mm wire class)", 1,
         "hot-dip galvanised weld wire (duty section 3)",
         mass["floor_wire"] + mass["wire_panels"], "buy",
         "drawn as plate solids; the mesh open area carries ~0.15 of the plate "
         "mass (the hardware-cloth idiom); buy panels cut to size, plan rule 6"],
        ["4", "PP feeder envelope 480 x 120 x 220 at (120, 40, 360) - one hopper "
              "per tier", 1, "PP (duty section 3)", mass["feed_hoppers"], "buy",
         "drawn as its box envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the PP table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["5", "SS316 nipple-waterer line envelope 300 x 60 x 200 at (820, 40, "
              "360) - one nipple per tier", 1, "SS316 (duty section 3)",
         mass["waterers"], "buy",
         "drawn as its box envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the SS316 table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["6", "Nozzle set per docs-authority/nozzles/QUAIL_CAGE.csv: 9 rows "
              "drawn as DN15 tube stubs (4 in z 160, 3 out z 600, drain, vent)",
         9, "galvanised fittings stock", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; bores not recalculated (duty "
         "section 4); atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M8 cage-section joint bolt", "ISO 898-1 8.8", 12,
         "frame and tier joints, 3 per leg line (study pattern)",
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
        "frame": {"leg_mm": 40, "wire_floor_z_mm": 300.0, "roof_z_mm": 1600.0},
        "feed_hoppers": {"box_mm": [480.0, 120.0, 220.0], "at_mm": [120.0, 40.0, 360.0]},
        "waterers": {"box_mm": [300.0, 60.0, 200.0], "at_mm": [820.0, 40.0, 360.0]},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the frame corner; legs 40 x 40 at the 4 corners to "
                 "z 1600, drop board 3 mm at z 100, wire floor at z 300, panel "
                 "bands z 300..550 and z 1450..1700, roof at z 1600; the feeder "
                 "and waterer envelopes sit on the -Y front above the wire "
                 "floor",
        "supports": "frame legs to the slab on 4 base anchors; cage sections "
                    "bolted at the legs (fasteners.csv)",
        "nozzle_spread": "the schedule gives face and height only; inlet rows "
                         "N1/N2/N8/N9 on the -Y wall at z 160, outlet rows "
                         "N3/N4/N5 on the +Y wall at z 600, drain at the base "
                         "centreline, vent at the top centreline; per-tag "
                         "positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; the "
                          "weld-wire wall takes a backing plate at each stub at "
                          "fabrication (hold W12)",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
