"""BEE_HIVE manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the hive, y along the depth, z up, origin at the stand
corner. Every dimension is an authority figure or a named layout choice:

- Hive per the node: size_mm 600 x 500 x 1100 - "10-frame deep + medium + stand
  (A-M-424; TECHTREE beekeeping)". The Oct-31 build is confirmed as issued: stand
  laps the boxes by 25 mm a side, the telescoping lid laps 20 mm a side, and the
  box stack (stand 150 + deep 475 + medium 475 + screen 10 + lid 30) tops at
  z 1150. The assembly therefore leaves the node box (650.0 x 550.0 x 1150.0
  against 600 x 500 x 1100) - the MISFIT TO REPORT that section 7 already carries,
  by design and not resized (plan rule 3; the CRYO_ASU section 7 pattern). The
  node states no per-box heights, so fitting the stack under 1100 would invent
  dimensions; the hive-body envelope is the node box.
- Materials per duty section 3: untreated solid pine, SS316 screen bottom board,
  propolis-waxed interiors; NO copper-bearing alloys (no brass screws) and no
  treated lumber anywhere.
- Frames and foundation: the size_basis names the 10-frame deep + medium class;
  the frames are the buy woodenware (plan rule 6). Their count inside the boxes is
  not stated on the node (hold, W12).
- Nozzles: all 5 rows of docs-authority/nozzles/BEE_HIVE.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose; loop
  accounting rows on a hive - forage in, honey and evaporation out). N1 in on -Y
  at z 160; N2/N3 out on +Y at z 600; N4 drain flush at the envelope bottom; N5
  vent flush at the envelope top (the schedule z 800 datum predates the 1100 box
  - stale datum, hold W12). No flange is drawn (W4 110 % rule); the schedule
  rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "BEE_HIVE"

SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"screen_floor": "316L"},        # the SS316 screen bottom board
    "drop_keys": (),
    "cad_stl_envelope_box": True,               # no in-envelope module fills the node
                                                # box: the registry keeps the study
                                                # box (X-PAR-04 gate); the full build
                                                # lives in export/ and the STEP
    "cad_stl_scope": "study envelope box, metres (X-PAR-04 registry gate: the box "
                     "equals the node size_mm 600 x 500 x 1100; the full build "
                     "leaves the node box by the stand and lid laps and lives in "
                     "export/ and the STEP - the misfit is section-7-reported, "
                     "nothing resized)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose; loop accounting rows on a hive); N1 in on -Y at z 160, "
                    "N2/N3 out on +Y at z 600; N4 drain flush at the envelope "
                    "bottom; N5 vent flush at the envelope top (schedule z 800 "
                    "predates the 1100 box - stale datum, hold W12); no flange "
                    "drawn (W4 110 % rule); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "honey bee hive, 1 hive (A-M-424): pine stand lapping the boxes by "
                "25 mm a side, 10-frame deep + medium box stack, SS316 screen "
                "bottom board, telescoping lid lapping 20 mm a side; interiors "
                "propolis-waxed (duty section 3)",
        "misfit": {"export_bbox_mm": dims,
                   "size_mm": [float(v) for v in P["size_mm"]],
                   "note": "the assembly leaves the node box by the stand and lid "
                           "laps (stand +50, lid +40 a side) and the box stack "
                           "tops at z 1150 - the misfit is section-7-reported, "
                           "nothing resized (plan rule 3); the node states no "
                           "per-box heights, so fitting under 1100 would invent "
                           "dimensions"},
        "material": P.get("material"),
        "frames": "the size_basis names the 10-frame deep + medium class; frames "
                  "and foundation are the buy woodenware (plan rule 6), count not "
                  "stated on the node (hold, WORK_ORDER W12)",
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "Pine stand, laps the boxes by 25 mm a side, 150 high", 1,
         "untreated solid pine (duty section 3)", mass["stand"], "make",
         "no treated lumber anywhere on the hive (duty section 3)"],
        ["2", "Pine deep box (10-frame class), 475 high", 1,
         "untreated solid pine (duty section 3)", mass["box_deep"], "make",
         "interior propolis-waxed at assembly (duty section 3)"],
        ["3", "Pine medium box (10-frame class), 475 high", 1,
         "untreated solid pine (duty section 3)", mass["box_medium"], "make",
         "interior propolis-waxed at assembly (duty section 3)"],
        ["4", "Telescoping pine lid, laps 20 mm a side", 1,
         "untreated solid pine (duty section 3)", mass["lid"], "make",
         "cover laps by design - the section-7-reported misfit rides on it"],
        ["5", "Screen bottom board: SS316 hardware-cloth mesh on a pine frame", 1,
         "SS316 mesh + pine frame (duty section 3)",
         round(mass["screen_floor"] * 0.15, 1), "make",
         "drawn as its plate solid; the mesh open area carries ~0.15 of the plate "
         "mass - the mesh-class mass is the row value (hardware-cloth idiom)"],
        ["6", "Frames and foundation, deep + medium sets (10-frame class)", 2,
         "purchased woodenware + wax foundation", 0.0, "buy",
         "size_basis names the 10-frame deep + medium class (A-M-424); the frame "
         "count inside the boxes is not stated on the node (hold, WORK_ORDER W12); "
         "the charge is a buy row, plan rule 6"],
        ["7", "Nozzle set per docs-authority/nozzles/BEE_HIVE.csv: 5 rows drawn as "
              "DN15 tube stubs (forage in, honey and evaporation out, drain, vent)",
         5, "pine/SS316 hardware", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim (loop accounting rows); atmospheric "
         "per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M6 box-assembly screw", "ISO 3506 A4-70", 24,
         "box corner joints, 6 per box x 3 boxes + lid (study pattern)",
         "A4-70 stainless per the plan grade rule; NO copper-bearing alloys "
         "(no brass screws) and no treated lumber anywhere on the hive (duty "
         "section 3); study pattern, confirmed at fabrication"],
        [None, "M10 stand-to-pad anchor", "ISO 898-1 8.8", 4,
         "stand legs to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the grade rule (anchor is not hive material)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "stack": {"stand_z_mm": [0.0, 150.0], "screen_z_mm": [140.0, 150.0],
                  "boxes": "deep 475 + medium 475 at the +25 mm offset",
                  "lid_z_mm": [1120.0, 1150.0]},
        "measured_bbox_mm": dims,
        "misfit_note": "assembly leaves the node box (stand/lid laps + the box "
                       "stack) - section-7-reported, nothing resized",
    },
    "layout_block": lambda P: {
        "frame": "origin at the stand corner; stand 650 x 550 x 150, boxes 600 x "
                 "500 at the (25, 25) offset, lid 640 x 540 x 30 at z 1120",
        "supports": "stand legs to the pad on 4 anchors; the hive stands free on "
                    "the stand",
        "nozzle_spread": "the schedule gives face and height only; N1 in on -Y at "
                         "z 160, N2/N3 out on +Y at z 600, drain at the base, "
                         "vent at the top centreline; per-tag positions in "
                         "check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; SS "
                          "hardware only, no copper-bearing alloys",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
