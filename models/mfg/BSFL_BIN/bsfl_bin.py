"""BSFL_BIN manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the frame, y along the depth, z up, origin at the frame
corner. Every dimension is an authority figure or a named layout choice:

- Frame per the node: size_mm 2500 x 900 x 700, HDPE tray walls and floor 10 mm.
  The size_basis names "2 x 5 kg/d-class bins in one frame at the 8.21 kg/d wet
  feedstock (A-M-418 revision)": the rebuild draws the centre divider that makes
  the frame two bins (even split, study layout choice). The rebuild fills the box
  exactly (A-core 2; A-FARM: not shrunk to fit the block).
- Duty section 3 names the parts beside the tray: a PP larval self-harvest ramp
  and an SS316 mesh screen - one ramp per bin leaning on the +X wall (foot at the
  floor, top at the rim; study layout, hold W12), and the mesh drawn as a top
  screen panel per bin whose open area is the bin ventilation path (the hardware-
  cloth idiom: mesh carries ~0.15 of the drawn plate mass). No metal below the
  substrate line (duty section 3).
- Substrate: no depth is named on the node - the bin is drawn empty; the larvae
  and substrate inventory is process inventory, not BOM parts (the STOCK_OUT
  idiom; hold, W12).
- Nozzles: all 12 rows of docs-authority/nozzles/BSFL_BIN.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). Inlets N1,
  N2, N6, N7, N11 on -Y at z 160; outlets N3, N4, N5, N10, N12 on +Y at z 600;
  N8 drain flush at the envelope bottom; N9 vent flush at the envelope top (the
  schedule z 800 datum predates the 700 box - stale datum, hold W12). No flange
  is drawn (W4 110 % rule); the schedule rating column (Class 150) is carried
  verbatim as text.
"""
import math
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "BSFL_BIN"
T = 10.0
DIV_X = 1250.0                                  # centre divider (two-bin frame)
RAMP_DX, RAMP_DZ, RAMP_T = 340.0, 680.0, 10.0   # foot to rim lean (study, W12)
RAMP_Y0, RAMP_Y1 = 30.0, 870.0


def ramp(x_top):
    """A self-harvest ramp leaning on the +X wall: top edge laps 1 mm into the
    wall, the foot laps 2 mm into the floor - the volumetric-overlap idiom (the
    grow_bed fix: plates meeting faces edge-to-edge left the export non-manifold)."""
    slope = math.hypot(RAMP_DX, RAMP_DZ)
    ang = math.degrees(math.atan2(RAMP_DZ, RAMP_DX))
    p = cq.Workplane().box(slope, RAMP_Y1 - RAMP_Y0, RAMP_T, centered=False)
    p = p.rotate((0, 0, 0), (0, 1, 0), -ang).translate((x_top - RAMP_DX, RAMP_Y0, T - 2.0))
    return p


def bin_screen(x0, x1):
    """A top screen panel per bin, lapping 1 mm into the walls and the divider."""
    return farm_closeout.box(x0 - 1.0, T - 1.0, 686.0, x1 - x0 + 2.0,
                             900 - 2 * T + 2.0, 2.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"divider": "HDPE", "ramp_a": "PP", "ramp_b": "PP",
                "screen_a": "316L", "screen_b": "316L"},
    "drop_keys": (),
    "extras": {
        "divider": lambda P: farm_closeout.box(DIV_X - 5.0, T, T, 10.0, 900 - 2 * T, 700 - 2 * T),
        "ramp_a": lambda P: ramp(DIV_X - 5.0),
        "ramp_b": lambda P: ramp(2500.0 - T),
        "screen_a": lambda P: bin_screen(T, DIV_X - 5.0),
        "screen_b": lambda P: bin_screen(DIV_X + 5.0, 2500.0 - T),
    },
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 2500 x 900 x 700 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N2/N6/N7/N11 on -Y at z 160, outlets "
                    "N3/N4/N5/N10/N12 on +Y at z 600; N8 drain flush at the "
                    "envelope bottom; N9 vent flush at the envelope top (schedule "
                    "z 800 predates the 700 box - stale datum, hold W12); no "
                    "flange drawn (W4 110 % rule); the schedule rating column "
                    "(Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "black-soldier-fly larvae composting frame, 2 x 5 kg/d-class bins "
                "in one frame (A-M-418 revision): HDPE tray 2500 x 900 x 700 with "
                "a centre divider, one PP self-harvest ramp per bin leaning on "
                "the +X wall, and an SS316 mesh top screen per bin whose open "
                "area is the ventilation path",
        "a_farm": "the frame is drawn at the node box flush; the drain and the "
                  "sec3-named ramp and screen are drawn",
        "substrate": "no substrate depth is named on the node - the bins are "
                     "drawn empty; larvae and substrate are process inventory, "
                     "not BOM parts (the STOCK_OUT idiom; hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE tray basin: walls and floor 10 mm, 2500 x 900 x 700 outer", 1,
         "HDPE (duty section 3)", mass["basin_shell"], "make",
         "size_mm verbatim; A-FARM: drawn at the node box flush; CA does not "
         "apply to the polymer (AQS-STD-001)"],
        ["2", "Centre divider - the size_basis two-bin split (2 x 5 kg/d class, "
              "even split)", 1, "HDPE (duty section 3)", mass["divider"], "make",
         "the even per-bin duty split is a study layout choice (hold, WORK_ORDER "
         "W12); sheet cut and thermoplastic weld"],
        ["3", "PP larval self-harvest ramp per bin, foot at the floor, top at the "
              "rim", 2, "PP (duty section 3)", mass["ramp_a"] + mass["ramp_b"],
         "make", "ramp angle and foot are study layout choices (hold, WORK_ORDER "
         "W12); PP weld"],
        ["4", "SS316 mesh top screen per bin (the ventilation path; no metal "
              "below the substrate line)", 2, "SS316 mesh (duty section 3)",
         round((mass["screen_a"] + mass["screen_b"]) * 0.15, 1), "buy",
         "hardware-cloth panels cut to size; mesh carries ~0.15 of the drawn "
         "plate mass (the hardware-cloth idiom); buy panels, plan rule 6"],
        ["5", "Nozzle set per docs-authority/nozzles/BSFL_BIN.csv: 12 rows drawn "
              "as DN15 tube stubs (5 in z 160, 5 out z 600, drain, vent)", 12,
         "HDPE (duty section 3)", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M6 screen-frame clamp screw", "ISO 3506 A4-70", 8,
         "top screens to the tray rim, 4 per bin (study pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); SS316 "
         "above the substrate line per duty section 3; study pattern, confirmed "
         "at fabrication"],
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "frame plinth to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "bins": {"divider_x_mm": DIV_X, "split": "even (study)"},
        "ramps": {"dx_mm": RAMP_DX, "dz_mm": RAMP_DZ, "one_per_bin": True},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the frame corner; tray 2500 x 900 x 700 outer, walls "
                 "and floor 10 mm; centre divider at x 1250 splits the frame "
                 "into two 5 kg/d-class bins",
        "supports": "frame plinth to the slab on 4 base anchors; screens clamped "
                    "to the rim",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, outlet rows on the +Y wall at z "
                         "600, drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; no "
                          "metal below the substrate line",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
