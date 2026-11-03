"""DUCK_PEN manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the pen, y along the depth, z up, origin at the frame
corner. Every dimension is an authority figure or a named layout choice:

- Frame per the node: size_mm 2500 x 1300 x 1300 - "6 ducks x 0.3 m2 + wallow
  strip (A-M-421; TECHTREE ducks.md)". The Oct-31 frame build is confirmed as
  issued: four 40 x 40 legs, drop board at z 100, wire floor at z 300, wire
  panel bands at z 300..550 and z 1050..1300, sheet roof at z 1200. The rebuild
  fills the box exactly (A-core 2; A-FARM: not shrunk to fit the block).
- The wallow the size_basis names is drawn as the liner duty section 3 names:
  an EPDM-lined wash strip at the -X end of the drop board (800 x 600 patch,
  5 mm; position and size are study layout choices, hold W12) - "permanently
  wet pen with a wallow: standing water governs" (duty section 3 basis).
- Nozzles: all 9 rows of docs-authority/nozzles/DUCK_PEN.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope
  faces (duty section 4: DN15, no flange class, atmospheric tube or hose).
  Inlets N1 (drinking/washing water), N5 (fresh duckweed forage), N9 (pressed
  duckweed mash) on -Y at z 160; outlets N2 (eggs), N3 (manure to the larvae
  bin), N4 (pen evaporation), N6 (wash water) on +Y at z 600; N7 drain flush at
  the envelope bottom over the wallow end; N8 vent flush at the envelope top
  (the schedule z 800 datum predates the 1300 box - stale datum, hold W12).
  The duty notes the elevations are schedule placeholders (unit tasks 02/06);
  the pen wall is hardware cloth, so the wall backing for each stub is a
  fabrication detail (hold, W12). No flange is drawn (W4 110 % rule); the
  schedule rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "DUCK_PEN"
L, W = 2500.0, 1300.0
WALLOW = (5.0, 5.0, 800.0, 600.0)               # x0, y0, dx, dy of the wash strip


def wallow_liner(P):
    x0, y0, dx, dy = WALLOW
    # laps 1 mm into the board sheet (z 100..103) so the union fuses
    return farm_closeout.box(x0, y0, 101.0, dx, dy, 5.0)


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"wallow_liner": "EPDM"},
    "drop_keys": (),
    "extras": {"wallow_liner": wallow_liner},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 2500 x 1300 x 1300 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); inlets N1/N5/N9 on -Y at z 160, outlets N2/N3/N4/N6 "
                    "on +Y at z 600; N7 drain flush at the envelope bottom over "
                    "the wallow end; N8 vent flush at the envelope top (schedule "
                    "z 800 predates the 1300 box - stale datum, hold W12); the "
                    "elevations are schedule placeholders (duty tasks 02/06) and "
                    "the wall is hardware cloth - stub backing is a fabrication "
                    "detail (hold W12); no flange drawn (W4 110 % rule); the "
                    "schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "duck pen, 6 Khaki Campbell ducks (A-M-421): HDG frame 2500 x "
                "1300 x 1300 with wire floor and panel bands, drop board, and "
                "the EPDM-lined wallow strip the size_basis names at the -X end",
        "a_farm": "the pen is drawn at the node box flush; the wallow liner and "
                  "the drain are drawn",
        "wallow": "EPDM liner patch 800 x 600 x 5 on the drop board (duty "
                  "section 3: permanently wet pen, standing water governs); "
                  "position and size are study layout choices (hold, W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDG frame: 4 legs 40 x 40 to z 1200, sheet roof at z 1200", 1,
         "hot-dip galvanised steel (duty section 3)",
         mass["frame_legs"] + mass["roof"], "make",
         "size_basis verbatim (A-M-421); frame weldment, AQS-MOD-002 farm frame "
         "class"],
        ["2", "Drop board 3 mm at z 100", 1,
         "hot-dip galvanised steel (duty section 3)", mass["drop_board"], "make",
         "board under the wire floor; wash-down class"],
        ["3", "Hardware cloth: wire floor at z 300 + panel bands at z 300..550 "
              "and z 1050..1300 (1 mm cloth class)", 1,
         "hot-dip galvanised hardware cloth (duty section 3)",
         mass["floor_wire"] + mass["wire_panels"], "buy",
         "drawn as plate solids; the mesh open area carries ~0.15 of the plate "
         "mass (the hardware-cloth idiom); buy panels cut to size, plan rule 6"],
        ["4", "EPDM wallow liner patch 800 x 600 x 5 on the drop board, -X end",
         1, "EPDM (duty section 3)", mass["wallow_liner"], "buy",
         "the size_basis wallow strip, lined per duty section 3 (permanently "
         "wet; standing water governs); liner sheet is a buy good, plan rule 6; "
         "patch size and position are study layout choices (hold, WORK_ORDER W12)"],
        ["5", "Nozzle set per docs-authority/nozzles/DUCK_PEN.csv: 9 rows drawn "
              "as DN15 tube stubs (3 in z 160, 4 out z 600, drain, vent)", 9,
         "HDPE fittings", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; elevations are schedule "
         "placeholders, the cloth wall backing is a fabrication detail (hold, "
         "WORK_ORDER W12); atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "frame legs to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
        [None, "M6 wallow batten screw", "ISO 3506 A4-70", 8,
         "wallow liner batten strips to the drop board, 4 per long edge (study "
         "pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); study "
         "pattern, confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "frame": {"leg_mm": 40, "wire_floor_z_mm": 300.0, "roof_z_mm": 1200.0},
        "wallow_patch_mm": list(WALLOW) + [5.0],
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the frame corner; legs at the 4 corners, drop board "
                 "at z 100, wire floor at z 300, panel bands z 300..550 and "
                 "z 1050..1300, roof at z 1200; wallow patch at the -X end of "
                 "the drop board",
        "supports": "frame legs to the slab on 4 anchors; wallow liner held by "
                    "batten strips",
        "nozzle_spread": "the schedule gives face and height only; inlet rows on "
                         "the -Y wall at z 160, outlet rows on the +Y wall at "
                         "z 600, drain at the base over the wallow end, vent at "
                         "the top centreline; per-tag positions in "
                         "check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; the "
                          "cloth wall takes a backing plate at each stub at "
                          "fabrication (hold W12)",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
