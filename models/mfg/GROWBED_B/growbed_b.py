"""GROWBED_B manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Sizes and counts come from the plant graph through the shared reader (models/mfg/lib/graph_node.py via farm_closeout.py); the params.json write-back merges the builder-owned blocks only. and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the bed, y along the width, z up, origin at the bed
corner. Every dimension is an authority figure or a named layout choice:

- Bed per the node: size_mm 3600 x 2100 x 500 - "media bed 7 m2, the anaerobic
  mineralisation half (A-M-415; A-M-229)". The rebuild fills the box exactly
  (A-core 2). A-FARM governs: the bed is drawn at the node box, NOT shrunk to
  fit; the interior 3580 x 2080 = 7.45 m2 is the media-bed area the box yields,
  reported against the size_note's 7 m2 class and the design block's 14.56 m2
  dual-root-zone pair (the A+B beds share that duty; the registry box governs
  - hold, W12).
- Duty section 3 names the build-up: HDPE tray, EPDM liner, LECA media on a
  geotextile separation cloth, CPVC loop piping - the anaerobic mineralisation
  root zone (the bed runs sulfidic at depth, duty section 3 basis). The rebuild
  draws the liner sheet (5 mm, floor + walls - the GROW_BED ponded-zone idiom),
  the geotextile cloth (2 mm, buy roll) and the LECA media envelope at the
  300 mm depth GROWBED_A's size_note names for the pair (the charge is a buy
  row; plan rule 6).
- Nozzles: all 9 rows of docs-authority/nozzles/GROWBED_B.csv drawn at tag,
  face, height and bore as atmospheric open-bore tube stubs flush at the
  envelope faces (duty section 4: DN15, no flange class, atmospheric tube or
  hose). Inlets N3 (cold rabbit manure direct to the mineralisation zone), N6
  (press water back to the loop), N9 (mineral nitrate solution) on -Y at
  z 160; the schedule z 600 rows - inlet N1 (nitrate water through the aerobic
  root zone) and outlets N2 (loop water to the duckweed raceway), N7 (media-bed
  greens to the reserve), N8 (growbed evapotranspiration) - sit at or above the
  500 box: drawn with their tops flush at the envelope top (the GLASS_BURNOUT
  stale-datum idiom; hold W12); N4 drain flush at the envelope bottom; N5 vent
  flush at the envelope top (the schedule z 800 datum predates the box - stale
  datum, hold W12). No flange is drawn (W4 110 % rule); the schedule rating
  column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "GROWBED_B"
T, LT, MEDIA_D, CLOTH_T = 10.0, 5.0, 300.0, 2.0
BUILD_UP = T + LT                               # liner top: z 15


def media_envelope(P):
    L, W, H = (float(v) for v in P["size_mm"])
    ix, iy = L - 2 * (T + LT), W - 2 * (T + LT)
    return farm_closeout.box(T + LT, T + LT, BUILD_UP + CLOTH_T,
                             ix, iy, MEDIA_D)


def cloth(P):
    L, W, H = (float(v) for v in P["size_mm"])
    ix, iy = L - 2 * T, W - 2 * T
    # laps 1 mm into the walls so the union fuses (the grow_bed idiom)
    return farm_closeout.box(T - 1.0, T - 1.0, BUILD_UP - 1.0,
                             ix + 2.0, iy + 2.0, CLOTH_T)


SPEC = {
    "unit": UNIT,
    "liner_bag": True,
    "liner_top_clearance": 20.0,
    "rho_map": {"liner": "EPDM", "geotextile_cloth": "PP", "media": "LECA"},
    "drop_keys": (),
    "extras": {"geotextile_cloth": cloth, "media": media_envelope},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 3600 x 2100 x 500 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N3/N6/N9 on -Y at z 160; the schedule z 600 "
                    "rows (N1 in, N2/N7/N8 out) and vent N5 (z 800) sit at or "
                    "above the 500 box - drawn flush at the envelope top (stale "
                    "datum, hold W12); N4 drain flush at the envelope bottom; "
                    "no flange drawn (W4 110 % rule); the schedule rating "
                    "column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "aquaponic root zone B - anaerobic mineralisation media bed "
                "(A-M-415; A-M-229): HDPE tray 3600 x 2100 x 500 with the EPDM "
                "liner sheet 5 mm, geotextile separation cloth, and the LECA "
                "media envelope at the 300 mm depth, 184 mm freeboard to the rim",
        "a_farm": "bed area matches the node box - interior 3580 x 2080 = 7.45 "
                  "m2, drawn at the registry box and NOT shrunk to fit; the "
                  "liner and the drain are drawn",
        "area_reading": "the size_note names the 7 m2 anaerobic half; the "
                        "design block area_m2 14.56 is the A+B pair - the "
                        "registry box governs (hold, W12)",
        "zone": "anaerobic mineralisation at depth (duty section 3: the bed "
                "runs sulfidic); cold rabbit manure lands direct on the media "
                "(node design, N3)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE tray basin: walls and floor 10 mm, 3600 x 2100 x 500 outer", 1,
         "HDPE (duty section 3)", mass["basin_shell"], "make",
         "size_mm verbatim; A-FARM: drawn at the node box flush; CA does not "
         "apply to the polymer (AQS-STD-001)"],
        ["2", "EPDM liner sheet 5 mm: floor + four walls", 1,
         "EPDM (duty section 3)", mass["liner"], "buy",
         "A-FARM: liner drawn; sheet roll goods, buy roll (plan rule 6)"],
        ["3", "Geotextile separation cloth 2 mm over the liner", 1,
         "geotextile, PP class (duty section 3)", mass["geotextile_cloth"], "buy",
         "duty section 3 separation cloth; roll goods cut to size, plan rule 6"],
        ["4", "LECA media envelope at 300 mm depth over the cloth", 1,
         "expanded clay (LECA)", mass["media"], "buy",
         "the charge is a buy row (plan rule 6) at the LECA table bulk density; "
         "supplier TDS at order (hold, WORK_ORDER W12)"],
        ["5", "Nozzle set per docs-authority/nozzles/GROWBED_B.csv: 9 rows drawn "
              "as DN15 CPVC tube stubs (3 in z 160, the z 600 rows and vent at "
              "the top line, drain)", 9, "CPVC loop fittings (duty section 3)",
         mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; the z 600/z 800 datums predate "
         "the 500 box - drawn flush at the envelope top (hold, WORK_ORDER W12); "
         "atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "bed plinth to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
        [None, "M8 liner batten bolt", "ISO 3506 A4-70", 8,
         "liner batten strips to the bed rim, 2 per wall line (study pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); study "
         "pattern, confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": T, "liner_mm": LT, "media_depth_mm": MEDIA_D,
        "cloth_mm": CLOTH_T,
        "interior_mm": [3580, 2080], "interior_area_m2": 7.45,
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the bed corner; tray 3600 x 2100 x 500 outer, walls "
                 "and floor 10 mm; liner sheet floor + walls to z 480; cloth at "
                 "z 14..16; media to z 316; 184 mm freeboard to the rim",
        "supports": "bed plinth to the slab on 4 anchors; liner held by rim "
                    "batten strips",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, the z 600 rows at the top line, "
                         "drain at the base centreline, vent at the top "
                         "centreline; per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
