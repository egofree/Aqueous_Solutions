"""GW_INTAKE manufacturing model, AQS-PLAN-006 work order (X-LOC-13 well head).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the pad length, y along the width, z up, origin at the pad
corner. Every dimension is an authority figure or a named layout choice:

- The unit is the plant-side well head per the node size basis: "the wellhead hatch +
  pump discharge set (X-LOC-13 well head); the pump is downhole, not plant-side".
  The build fills the node box 800 x 800 x 600 flush: a 6 mm SS304 head plate set
  (the X-LOC-13 basis) as the open-top tray form, closed by a two-leaf hatch at
  z 590-600 that leaves a 20 mm centre gap for the vent. The submersible pump lives
  down the well and is not plant-side equipment - it is not drawn.
- The pump discharge head set is drawn as the DN168 study boss envelope on the floor
  at the -X corner (the discharge head the duty section 3 names); the HDPE potable
  discharge run is plant piping scope (AQS-PIP-004 line list), not a unit solid.
- Nozzles: all 3 rows of docs-authority/nozzles/GW_INTAKE.csv drawn at tag, face and
  bore as atmospheric open-bore tube stubs flush at the envelope faces (duty section
  4; the schedule rating column Class 150 carried verbatim as text; no flange drawn,
  W4 110 % rule). N1 discharge out on +Y at the z 600 rim; N2 drain flush at the
  envelope bottom; N3 vent flush at the envelope top through the hatch gap (the
  schedule z 800 datum predates the 600 box - stale datum, hold W12).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "GW_INTAKE"


def _hatch(P):
    from farm_closeout import box
    L, W, H = (float(v) for v in P["size_mm"])
    leaf_y, leaf_z = W - 20.0, 10.0
    left = box(5.0, 10.0, H - leaf_z, L / 2 - 15.0, leaf_y, leaf_z)
    right = box(L / 2 + 15.0, 10.0, H - leaf_z, L / 2 - 15.0, leaf_y, leaf_z)
    return left.union(right)


def _discharge_head(P):
    L, W, H = (float(v) for v in P["size_mm"])
    import cadquery as cq
    return cq.Workplane("XY").circle(84.0).extrude(60.0).translate((110.0, 110.0, 6.0))


SPEC = {
    "unit": UNIT,
    "extras": {"hatch": _hatch, "discharge_head": _discharge_head},
    "rho_map": {"basin_shell": "304", "hatch": "304", "discharge_head": "304",
                "nozzles": "304"},
    "drop_keys": (),
    "drain_xy": (110.0, 690.0),
    "vent_xy": (400.0, 400.0),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the build "
                     "fills the node box 800 x 800 x 600 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N1 discharge out on +Y at the z 600 rim; N2 "
                    "drain flush at the envelope bottom; N3 vent flush at the "
                    "envelope top through the hatch gap (schedule z 800 predates the "
                    "600 box - stale datum, hold W12); no flange drawn (W4 110 % "
                    "rule); the schedule rating column (Class 150) carried verbatim "
                    "as text",
    "machine": lambda P, dims, mass: {
        "type": "standby well head: wellhead hatch + pump discharge set (X-LOC-13); "
                "the submersible pump is downhole, not plant-side (node size basis)",
        "a_farm": "the head plate set is drawn at the node box flush; the hatch and "
                  "the discharge-head boss are drawn",
        "hatch": "two SS304 leaves at z 590-600 with a 20 mm centre gap for the vent",
        "discharge_head": "DN168 study boss envelope on the floor at the -X corner "
                          "(the discharge head duty section 3 names); the HDPE "
                          "potable discharge run is plant piping scope (AQS-PIP-004)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 wellhead head plate set: 800 x 800 x 600 mm tray form, 6 mm "
              "plate (X-LOC-13 well head)", 1, "SS304", mass["basin_shell"], "make",
         "size_basis verbatim; potable groundwater contact per duty section 3 "
         "(304 wetted at the chloride-light aquifer class); CA does not apply to the "
         "shop rule polymer clause and 304 carries none at this service (AQS-STD-001)"],
        ["2", "SS304 hatch, two leaves 390 x 780 x 10 at z 590-600, 20 mm centre "
              "vent gap", 1, "SS304", mass["hatch"], "make",
         "study plate stock; hinged at fabrication (WORK_ORDER W12)"],
        ["3", "SS304 pump discharge head, DN168 study boss envelope 60 mm on the "
              "floor", 1, "SS304", mass["discharge_head"], "make",
         "duty section 3 discharge head; the HDPE potable discharge run is plant "
         "piping scope (AQS-PIP-004), not a unit solid"],
        ["4", "Nozzle set per docs-authority/nozzles/GW_INTAKE.csv: 3 rows drawn as "
              "DN15 tube stubs (discharge, drain, vent)", 3, "SS304",
         mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 hatch hold-down clamp", "ISO 3506 A4-70", 4,
         "hatch leaves to the head plate rim, 4 corners (study pattern)",
         "SS316 hardware per duty section 3 wetted-class rule; study pattern, "
         "confirmed at fabrication"],
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "head plate set to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the pad corner; head plate set 800 x 800 x 600 outer, "
                 "6 mm plate; hatch leaves at z 590-600; discharge-head boss at the "
                 "-X floor corner",
        "supports": "head plate set to the slab on 4 base anchors; hatch clamped at "
                    "4 corners",
        "nozzle_spread": "the schedule gives face and height only; N1 on the +Y wall "
                         "at the z 600 rim, N2 drain at the -Y corner, N3 vent at "
                         "the top centreline through the hatch gap; per-tag positions "
                         "in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
