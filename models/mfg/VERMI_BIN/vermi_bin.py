"""VERMI_BIN manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the bin, y along the width, z up, origin at the bin
corner. Every dimension is an authority figure or a named layout choice:

- Bin per the node: size_mm 2100 x 1100 x 600 - "2 m2 bin at 300 mm bedding
  depth (A-M-425)". The rebuild fills the box exactly (A-core 2; A-FARM: not
  shrunk to fit the block). Area reading: the interior 2080 x 1080 = 2.25 m2
  against the node design bin_m2 2.0 - the registry box governs (hold, W12).
- Duty section 3 names the build-up: HDPE bin, coco-coir and shredded-paper
  bedding, PP working fork, SS316 harvest screen. The rebuild draws the SS316
  harvest screen as a false-floor mesh plate 2 mm over the bin floor (the worm
  tea drains below it to the N4 harvest row; laps 1 mm into the walls - the
  manifold idiom), and the bedding envelope at the 300 mm depth the size_basis
  names (the charge is a buy row, plan rule 6; no bedding density row exists in
  the material table, so the mass carries 0.0 - hold, W12). The PP working fork
  is a hand tool, not a bin part: not drawn.
- Nozzles: all 6 rows of docs-authority/nozzles/VERMI_BIN.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose). Inlets N1 (quail droppings), N2 (soft canopy residue) on -Y at z 160;
  outlets N3 (vermicompost to the growbed soil), N4 (worm tea to the growbed
  soil) at the schedule z 600 - the rim height, drawn with their tops flush at
  the envelope top (the schedule datum sits at the build height; hold W12); N5
  drain flush at the envelope bottom; N6 vent flush at the envelope top (the
  schedule z 800 datum predates the 600 box - stale datum, hold W12). No
  flange is drawn (W4 110 % rule); the schedule rating column (Class 150) is
  carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "VERMI_BIN"
T, BED_D, SCREEN_T = 10.0, 300.0, 2.0


def harvest_screen(P):
    L, W, H = (float(v) for v in P["size_mm"])
    ix, iy = L - 2 * T, W - 2 * T
    # laps 1 mm into the walls so the union fuses (the grow_bed idiom)
    return farm_closeout.box(T - 1.0, T - 1.0, T + T - 1.0,
                             ix + 2.0, iy + 2.0, SCREEN_T)


def bedding(P):
    L, W, H = (float(v) for v in P["size_mm"])
    ix, iy = L - 2 * (T + 1.0), W - 2 * (T + 1.0)
    return farm_closeout.box(T + 1.0 + 1.0, T + 1.0 + 1.0, T + SCREEN_T,
                             ix, iy, BED_D)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"harvest_screen": "316L", "bedding": None},   # no bedding density row
    "drop_keys": (),
    "extras": {"harvest_screen": harvest_screen, "bedding": bedding},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 2100 x 1100 x 600 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N2 on -Y at z 160; outlets N3/N4 at the "
                    "schedule z 600 rim height - drawn flush at the envelope "
                    "top (hold W12); N5 drain flush at the envelope bottom; N6 "
                    "vent flush at the envelope top (schedule z 800 predates "
                    "the 600 box - stale datum, hold W12); no flange drawn "
                    "(W4 110 % rule); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "vermiculture bin, Eisenia fetida (A-M-425): HDPE bin 2100 x "
                "1100 x 600 with the SS316 harvest screen as a false floor 2 mm "
                "over the bin floor (worm tea drains below to the N4 row) and "
                "the bedding envelope at the 300 mm depth the size_basis names",
        "a_farm": "bin area reading: interior 2080 x 1080 = 2.25 m2 at the "
                  "registry box, NOT shrunk to fit, against the node design "
                  "bin_m2 2.0 (hold, W12); the drain is drawn",
        "bedding": "coco-coir and shredded-paper bedding at 300 mm (size_basis); "
                   "held 70-80 % moisture near neutral pH (duty section 3); the "
                   "charge is a buy row - no bedding density row exists in the "
                   "material table, mass carries 0.0 (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE bin basin: walls and floor 10 mm, 2100 x 1100 x 600 outer", 1,
         "HDPE (duty section 3)", mass["basin_shell"], "make",
         "size_mm verbatim; A-FARM: drawn at the node box flush; CA does not "
         "apply to the polymer (AQS-STD-001)"],
        ["2", "SS316 harvest screen false floor 2 mm over the bin floor (the "
              "worm tea drains below it to the N4 row)", 1,
         "SS316 mesh (duty section 3)", round(mass["harvest_screen"] * 0.15, 1),
         "buy", "hardware-cloth panel cut to size (plan rule 6); mesh carries "
         "~0.15 of the drawn plate mass (the hardware-cloth idiom)"],
        ["3", "Bedding envelope: coco-coir and shredded-paper at 300 mm "
              "(size_basis) over the screen", 1,
         "coco-coir / paper bedding", 0.0, "buy",
         "the charge is a buy row (plan rule 6); no bedding density row exists "
         "in the material table, so the mass carries 0.0 (hold, WORK_ORDER W12)"],
        ["4", "Nozzle set per docs-authority/nozzles/VERMI_BIN.csv: 6 rows drawn "
              "as DN15 HDPE tube stubs (2 in z 160, 2 out at the rim line, "
              "drain, vent)", 6, "HDPE fittings", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; the z 600 rim rows and the z "
         "800 vent datum drawn at the envelope top (hold, WORK_ORDER W12); "
         "atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "bin plinth to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
        [None, "M6 screen-frame clamp screw", "ISO 3506 A4-70", 8,
         "harvest screen to the bin rim ledges, 4 per long wall (study pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); study "
         "pattern, confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": T, "bedding_depth_mm": BED_D, "screen_mm": SCREEN_T,
        "interior_mm": [2080, 1080], "interior_area_m2": 2.25,
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the bin corner; bin 2100 x 1100 x 600 outer, walls "
                 "and floor 10 mm; harvest screen false floor at z 19..21; "
                 "bedding to z 321; freeboard to the rim",
        "supports": "bin plinth to the slab on 4 anchors; screen on rim ledges",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, the z 600 rim rows at the top "
                         "line, drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
