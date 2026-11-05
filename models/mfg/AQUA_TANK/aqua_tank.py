"""AQUA_TANK manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the tank length, y along the width, z up, origin at the tank
corner. Every dimension is an authority figure or a named layout choice:

- Tank per the node: size_mm 2100 x 1100 x 1100 - "2.0 m3 working volume at the 60 kg
  stock / 30 kg-per-m3 class (TECHTREE tilapia glossary; A-M-415): 2000 x 1000 x 1000
  ID + 50 walls, EPDM-lined HDPE (X-FARM sec3)". The shell is the node box flush: the
  rebuild fills it exactly (A-core 2). HDPE walls and floor 15 mm, lid 15 mm.
- Liner per duty section 3: "a food-grade LDPE aquaculture liner" - drawn as the
  sheet the params name (floor 5 mm plus four wall plates, the GROW_BED ponded-zone
  idiom), replacing the Oct-31 solid-block liner envelope; the liner class is carried
  at the HDPE table density until the supplier TDS (hold, W12).
- The aeration the design block names (the air stones are the O2 source) has no
  position or rating on the node: not drawn, held in W12.
- Nozzles: all 8 rows of docs-authority/nozzles/AQUA_TANK.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1-N3 out on +Y
  at z 600; N4-N6 in on -Y at z 160; N7 drain flush at the envelope bottom; N8 vent
  flush at the envelope top (the schedule z 800 datum predates the 1100 box - stale
  datum, hold W12). CPVC loop fittings per duty section 3; no flange is drawn (W4
  110 % rule); the schedule rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "AQUA_TANK"

SPEC = {
    "unit": UNIT,
    "liner_bag": True,
    "liner_top_clearance": 10.0,
    "rho_map": {"liner": "HDPE"},               # LDPE class carried at the HDPE table
    "drop_keys": (),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 2100 x 1100 x 1100 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1-N3 out on +Y at z 600, N4-N6 in on -Y at z 160; N7 "
                    "drain flush at the envelope bottom; N8 vent flush at the "
                    "envelope top (schedule z 800 predates the 1100 box - stale "
                    "datum, hold W12); no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "aquaponic fish tank, 60 kg standing stock (A-M-415): HDPE shell "
                "2000 x 1000 x 1000 ID with 15 mm walls and floor, 15 mm lid, "
                "food-grade LDPE liner sheet 5 mm (floor + walls, the GROW_BED "
                "ponded-zone idiom); the fish are the ammonia SOURCE and the O2 SINK "
                "of the aquaponic loop (node design)",
        "a_farm": "the tank is drawn at the node box flush; the liner and the drain "
                  "are drawn",
        "liner": "the Oct-31 liner was a solid-block envelope filling the cavity "
                 "(2230.4 kg); the rebuild draws the 5 mm sheet the params name "
                 "(liner_mm 5, duty section 3 LDPE liner class)",
        "aeration": "the air stones the design block names are the O2 source; no "
                    "position or rating on the node - not drawn (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE tank shell: 2000 x 1000 x 1000 ID + 15 mm walls and floor "
              "(2.0 m3 working volume, A-M-415 60 kg stock class)", 1, "HDPE",
         mass["vessel_shell"], "make",
         "size_basis verbatim; A-FARM: drawn at the node box flush; CA does not "
         "apply to the polymer (AQS-STD-001)"],
        ["2", "HDPE lid 15 mm on the tank rim", 1, "HDPE", mass["lid"], "make",
         "lid thickness follows the shell wall (study, hold WORK_ORDER W12)"],
        ["3", "Food-grade aquaculture liner sheet 5 mm: floor + four walls", 1,
         "LDPE liner class (duty section 3)", mass["liner"], "make",
         "sheet goods; carried at the HDPE table density (950 kg/m3) until the "
         "supplier TDS - the table has no LDPE row (hold, WORK_ORDER W12)"],
        ["4", "Nozzle set per docs-authority/nozzles/AQUA_TANK.csv: 8 rows drawn as "
              "DN15 CPVC tube stubs (3 out z 600, 3 in z 160, drain, vent)", 8,
         "CPVC loop fittings (duty section 3)", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 lid hold-down bolt + nut", "ISO 3506 A4-70", 8,
         "lid clamp hardware to the tank rim, 8 around the perimeter (study pattern)",
         "SS316 hardware above the waterline per duty section 3; polymer joint to "
         "the polymer supplier rule; study pattern, confirmed at fabrication"],
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "tank plinth to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"), "liner_mm": P.get("liner_mm"),
        "liner_scope": "floor + four wall plates 5 mm (duty section 3 liner sheet "
                       "class), not the Oct-31 solid block",
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the tank corner; shell 2100 x 1100 x 1100 outer, cavity "
                 "2000 x 1000 x 1000 ID; lid on the rim at z 1085",
        "supports": "tank plinth to the slab on 4 base anchors; lid clamped to the "
                    "rim by 8 hold-downs",
        "nozzle_spread": "the schedule gives face and height only; outlet rows N1-N3 "
                         "on the +Y wall at z 600, inlet rows N4-N6 on the -Y wall at "
                         "z 160, drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
