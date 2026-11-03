"""CHICKEN_COOP manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the coop, y along the depth, z up, origin at the frame
corner. Every dimension is an authority figure or a named layout choice:

- Frame per the node: size_mm 2500 x 1300 x 1900, hot-dip galvanised steel
  ("12 birds x 0.2 m2 floor + nest row + perch at the 0.12 kg/d ration house
  class (A-M-417)" - size_basis). The Oct-31 frame build is confirmed as issued:
  four 40 x 40 legs, drop board at z 100, wire floor at z 300, wire panel bands
  at z 300..550 and z 1650..1900, sheet roof at z 1800, nest-row envelope
  600 x 400 x 400 at (100, 100, 900). The rebuild fills the box exactly
  (A-core 2; A-FARM: not shrunk to fit the block).
- The perch the size_basis names is drawn: HDG rod OD 40 on two posts rising
  from the wire floor (study layout, hold W12). The HDPE drop-board liner duty
  section 3 names is drawn as a 5 mm sheet over the board.
- The nest row is the purchased envelope (plan rule 6): drawn as its box
  envelope, bought complete; the drawn-envelope mass is the HDG table-density
  figure, the purchase mass is the maker's (hold, W12). The SS316 feeders and
  waterers duty section 3 names have no rating on the node: not drawn (hold,
  W12).
- Nozzles: all 10 rows of docs-authority/nozzles/CHICKEN_COOP.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose). Inlets N1, N5, N6, N9, N10 on -Y at z 160; outlets N2, N3, N4 on +Y at
  z 600; N7 drain flush at the envelope bottom; N8 vent flush at the envelope
  top (the schedule z 800 datum predates the 1900 box - stale datum, hold W12).
  The duty notes the elevations are schedule placeholders (unit tasks 02/06);
  the coop wall is hardware cloth, so the wall backing for each stub is a
  fabrication detail (hold, W12). No flange is drawn (W4 110 % rule); the
  schedule rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "CHICKEN_COOP"
L, W = 2500.0, 1300.0
PERCH_Z = 640.0                                 # rod centreline (study layout, W12)


def perch(P):
    rod = (cq.Workplane("YZ", origin=(0, W / 2, PERCH_Z))
           .circle(20).extrude(L))              # +X rod, full length
    posts = None
    for px in (300.0, 2200.0):                  # posts lap through the wire floor and
                                                # 15 mm into the rod (volumetric
                                                # overlap - the grow_bed idiom)
        q = farm_closeout.box(px, W / 2 - 20, 295.0, 40.0, 40.0, PERCH_Z + 15.0 - 295.0)
        posts = q if posts is None else posts.union(q)
    return rod.union(posts)


def drop_liner(P):
    return farm_closeout.box(5.0, 5.0, 101.0, L - 10.0, W - 10.0, 5.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"drop_liner": "HDPE", "perch": "HDG_steel"},
    "drop_keys": (),
    "extras": {"perch": perch, "drop_liner": drop_liner},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 2500 x 1300 x 1900 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N5/N6/N9/N10 on -Y at z 160, outlets "
                    "N2/N3/N4 on +Y at z 600; N7 drain flush at the envelope "
                    "bottom; N8 vent flush at the envelope top (schedule z 800 "
                    "predates the 1900 box - stale datum, hold W12); the "
                    "elevations are schedule placeholders (duty tasks 02/06) and "
                    "the wall is hardware cloth - stub backing is a fabrication "
                    "detail (hold W12); no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "layer flock house, 12 birds (A-M-417): HDG frame 2500 x 1300 x "
                "1900 with wire floor and panel bands, drop board with the HDPE "
                "liner sheet duty section 3 names, nest-row envelope (purchased), "
                "and the perch the size_basis names on two posts",
        "a_farm": "the coop is drawn at the node box flush; the drain and the "
                  "drop-board liner are drawn",
        "purchased": "the nest row is the purchased envelope (plan rule 6) - "
                     "drawn as its box envelope, bought complete; the SS316 "
                     "feeders and waterers duty section 3 names have no rating "
                     "on the node: not drawn (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDG frame: 4 legs 40 x 40 to z 1800, sheet roof at z 1800", 1,
         "hot-dip galvanised steel (duty section 3)",
         mass["frame_legs"] + mass["roof"], "make",
         "size_basis verbatim (A-M-417); frame weldment, AQS-MOD-002 farm frame "
         "class"],
        ["2", "Drop board 3 mm at z 100 with the HDPE liner sheet 5 mm over it", 1,
         "HDG board + HDPE liner (duty section 3)",
         mass["drop_board"] + mass["drop_liner"], "make",
         "the liner sheet is the duty section 3 drop-board liner, drawn"],
        ["3", "Hardware cloth: wire floor at z 300 + panel bands at z 300..550 "
              "and z 1650..1900 (1 mm cloth class)", 1,
         "hot-dip galvanised hardware cloth (duty section 3)",
         mass["floor_wire"] + mass["wire_panels"], "buy",
         "drawn as plate solids; the mesh open area carries ~0.15 of the plate "
         "mass (the hardware-cloth idiom); buy panels cut to size, plan rule 6"],
        ["4", "Nest-row envelope 600 x 400 x 400 at the -X end", 1,
         "purchased nest boxes (envelope)", mass["nest_row"], "buy",
         "drawn as its box envelope, bought complete (plan rule 6); the drawn-"
         "envelope mass is the HDG table-density figure, the purchase mass is "
         "the maker's (hold, WORK_ORDER W12)"],
        ["5", "Perch: HDG rod OD 40 on two posts rising from the wire floor", 1,
         "hot-dip galvanised steel (duty section 3)", mass["perch"], "make",
         "the size_basis names the perch; rod height and post positions are "
         "study layout choices (hold, WORK_ORDER W12)"],
        ["6", "Nozzle set per docs-authority/nozzles/CHICKEN_COOP.csv: 10 rows "
              "drawn as DN15 tube stubs (5 in z 160, 3 out z 600, drain, vent)",
         10, "HDPE fittings", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; elevations are schedule "
         "placeholders, the cloth wall backing is a fabrication detail (hold, "
         "WORK_ORDER W12); atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 nest-row carriage bolt", "ISO 898-1 8.8", 8,
         "nest-row envelope to the frame rails, 4 per rail line (study pattern)",
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
        "frame": {"leg_mm": 40, "wire_floor_z_mm": 300.0, "roof_z_mm": 1800.0},
        "perch": {"rod_od_mm": 40.0, "centreline_z_mm": PERCH_Z, "posts_x_mm": [300.0, 2200.0]},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the frame corner; legs at the 4 corners, drop board "
                 "at z 100, wire floor at z 300, panel bands z 300..550 and "
                 "z 1650..1900, roof at z 1800; nest row at the -X end, perch "
                 "on the centreline at z 640",
        "supports": "frame legs to the slab on 4 anchors; nest row bolted to "
                    "the frame rails",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, outlet rows on the +Y wall at "
                         "z 600, drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; the "
                          "cloth wall takes a backing plate at each stub at "
                          "fabrication (hold W12)",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
