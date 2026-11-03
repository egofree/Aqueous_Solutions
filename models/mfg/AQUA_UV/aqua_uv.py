"""AQUA_UV manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 9, A-core + A-FARM).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the cabinet, y along the depth, z up, origin at the cabinet
corner. Every dimension is an authority figure or a named layout choice:

- Cabinet per the node: size_mm 400 x 350 x 750 - "inline 254 nm reactor tube +
  control box at the 0.04 kW lamp class (A-M-428) (X-FARM sec3)". SS304 sheet 5 mm
  (walls and floor), top plate 5 mm. The rebuild fills the box exactly (A-core 2).
- Reactor train per duty section 3 ("SS304 reactor tube with a quartz UV sleeve"):
  the Oct-31 rectangular shell is redrawn as the tube the duty names - SS304 tube
  OD 90 x 280 long (wall 2 mm study, hold W12) on the cabinet centreline at z 250,
  quartz sleeve OD 60 x 260 inside it, and the 0.04 kW lamp as its envelope rod
  (purchased per plan rule 6: named with the rating from the node, drawn as its
  envelope - A-MACH practice; the cabinet is the guard). Sleeve and lamp diameters
  are study proportions of the tube class (hold, W12).
- The unit is NORMALLY BYPASSED (AQUA_BYPASS engaged; node design): the sanitizer is
  the optional food-safety/contingency path, so the wetted-time caveat reads on the
  duty sheet, not as a model claim.
- Nozzles: all 4 rows of docs-authority/nozzles/AQUA_UV.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15, no flange class, atmospheric tube or hose). N1 in on -Y at
  z 160; N2 out on +Y at z 600; N3 drain flush at the envelope bottom; N4 vent flush
  at the envelope top (the schedule z 800 datum predates the 750 box - stale datum,
  hold W12). PP loop fittings per duty section 3; no flange is drawn (W4 110 % rule);
  the schedule rating column (Class 150) is carried verbatim as text.
"""
import pathlib
import sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "AQUA_UV"
ZX = 250.0                                      # reactor centreline height (layout)
YX = 175.0                                      # cabinet centreline


def _along_x(od, wall, length, x0):
    s = cq.Workplane("XY").circle(od / 2)
    if wall:
        s = s.circle(od / 2 - wall)
    return s.extrude(length).rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, YX, ZX))


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"reactor_tube": "304", "quartz_sleeve": "borosilicate",
                "uv_lamp": "borosilicate"},
    "drop_keys": ("extras_mm",),                # the Oct-31 box shell -> the duty tube
    "extras": {
        "reactor_tube": lambda P: _along_x(90.0, 2.0, 280.0, 60.0),
        "quartz_sleeve": lambda P: _along_x(60.0, 1.5, 260.0, 70.0),
        "uv_lamp": lambda P: _along_x(30.0, 0.0, 300.0, 50.0),
    },
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the rebuild "
                     "fills the node box 400 x 350 x 750 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15, no flange class, atmospheric tube or "
                    "hose); N1 in on -Y at z 160, N2 out on +Y at z 600; N3 drain "
                    "flush at the envelope bottom; N4 vent flush at the envelope "
                    "top (schedule z 800 predates the 750 box - stale datum, hold "
                    "W12); no flange drawn (W4 110 % rule); the schedule rating "
                    "column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "optional UV-C 254 nm loop sanitizer between the biofilter and the "
                "growbeds (A-M-428; AQUA_BYPASS normally engaged): SS304 cabinet "
                "400 x 350 x 750 with the reactor train on the centreline - SS304 "
                "tube OD 90 x 280 (wall 2 mm study), quartz sleeve OD 60 x 260, and "
                "the 0.04 kW lamp as its envelope rod (purchased, plan rule 6)",
        "a_mach": "the purchased lamp is named with the rating from the node "
                  "(254 nm, 0.04 kW lamp class, A-M-428) and drawn as its envelope; "
                  "the cabinet is the guard and the base anchors are drawn",
        "modes": "normal = bypassed; food-safety mode = inline (A-M-427); "
                 "contamination response = inline (node design) - the duty sheet "
                 "carries the wetted-time caveat",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 cabinet: sheet 5 mm walls and floor, 5 mm top "
              "(control box + reactor housing)", 1, "SS304 (duty section 3)",
         mass["cabinet_shell"] + mass["top"], "make",
         "size_basis verbatim (A-M-428); CA does not apply to the stainless "
         "interior loop class at ambient aquaponic temperature (AQS-STD-001)"],
        ["2", "SS304 reactor tube OD 90 x 280, wall 2 mm, on the cabinet centreline "
              "at z 250", 1, "SS304 (duty section 3)", mass["reactor_tube"], "make",
         "tube diameter is a study proportion of the inline reactor class (hold, "
         "WORK_ORDER W12); tube wall is a study value"],
        ["3", "Quartz UV sleeve OD 60 x 260 inside the reactor tube", 1,
         "quartz (duty section 3)", mass["quartz_sleeve"], "buy",
         "catalogue sleeve cut to length; carried at the borosilicate table row "
         "until the supplier TDS (hold, WORK_ORDER W12); fouling is the duty "
         "maintenance item (X-FARM-12 dose validation)"],
        ["4", "UV-C lamp 254 nm, 0.04 kW lamp class, drawn as its envelope rod",
         1, "purchased lamp (envelope)", mass["uv_lamp"], "buy",
         "rating from the node (A-M-428 sizing: 30-100 mJ/cm2 class at the 40 kg/d "
         "loop); purchased per plan rule 6"],
        ["5", "Nozzle set per docs-authority/nozzles/AQUA_UV.csv: 4 rows drawn as "
              "DN15 PP tube stubs (in z 160, out z 600, drain, vent)", 4,
         "PP loop fittings (duty section 3)", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M8 cabinet base anchor", "ISO 898-1 8.8", 4,
         "cabinet to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted part)"],
        [None, "M6 reactor tube clamp bolt", "ISO 3506 A4-70", 4,
         "reactor tube saddle clamps to the cabinet back plate, 2 per saddle "
         "(study pattern)",
         "A4-70 on the SS304 joint per the grade rule; study pattern, confirmed at "
         "fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "reactor": {"centreline_z_mm": ZX, "tube_od_mm": 90.0, "tube_len_mm": 280.0,
                    "sleeve_od_mm": 60.0, "lamp_od_mm": 30.0},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the cabinet corner; shell 400 x 350 x 750 outer, sheet "
                 "5 mm; reactor train on the cabinet centreline at z 250, tube "
                 "x 60..340",
        "supports": "cabinet base anchors to the slab; reactor tube saddle clamps "
                    "to the cabinet back plate",
        "nozzle_spread": "the schedule gives face and height only; N1 in on -Y at "
                         "z 160, N2 out on +Y at z 600, drain at the base "
                         "centreline, vent at the top centreline; per-tag positions "
                         "in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces; the "
                          "lamp is serviced by lifting the top plate",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
