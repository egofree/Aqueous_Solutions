"""WASHROOM manufacturing model, AQS-PLAN-006 work order (X-HAB habitation room).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the room length, y along the width, z up, origin at the room
corner. Every dimension is an authority figure or a named layout choice:

- The unit is the 8 m2 washroom fitout shell per the node size basis ("8 m2 fitout
  shell (A-M-419; AQS-HAB-001) (X-HAB sec3)"): the room-form shell 3000 x 2000 x 2400
  with 15 mm partition panels, a 900 x 2100 door opening in the -X end wall and the
  20 mm deck-finish build-down (the accepted form class). Nothing is resized.
- The fixture set duty section 3 names (SS304 fixtures) is drawn as three study
  sheet-metal envelopes in the +X wet zone: a shower tray in the +X/+Y corner, a WC
  pan beside it, and a basin hung on the -X wall segment clear of the 900 door swing.
  Ceramic tile wet zones are a finish on the FRP panels - no thickness is stated on
  the duty, so they are not drawn (WORK_ORDER hold).
- Nozzles: all 4 rows of docs-authority/nozzles/WASHROOM.csv drawn at tag, face and
  bore as atmospheric open-bore tube stubs flush at the envelope faces (duty section
  4; the schedule rating column Class 150 carried verbatim as text; no flange drawn,
  W4 110 % rule). N2 wash-water feed on -Y at z 160; N1 grey water out on +Y at z 600;
  N3 drain flush at the envelope bottom under the shower tray; N4 vent flush at the
  envelope top on the +Y wall line (the schedule z 800 datum predates the 2400 box -
  stale datum, hold W12).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "WASHROOM"

# Fixture envelopes (duty section 3 SS304 fixtures; arrangement is the layout choice,
# WORK_ORDER W12). (key, outer xyz dxdydz, inner cut xyz dxdydz)
FIXTURES = [
    ("shower_tray", (2450.0, 1565.0, 0.0, 530.0, 420.0, 100.0),
     (2456.0, 1571.0, 12.0, 518.0, 408.0, 88.0)),
    ("wc_pan", (2060.0, 1600.0, 0.0, 380.0, 385.0, 380.0),
     (2066.0, 1606.0, 6.0, 368.0, 373.0, 374.0)),
    ("basin", (15.0, 1500.0, 750.0, 480.0, 380.0, 200.0),
     (21.0, 1506.0, 756.0, 468.0, 368.0, 188.0)),
]
DRAIN_XY = (2715.0, 1775.0)                     # under the shower tray
VENT_XY = (1500.0, 1985.0)                      # on the +Y wall line


def _fixtures(P):
    from farm_closeout import box
    L, W, H = (float(v) for v in P["size_mm"])
    fix = None
    for (_k, (x, y, z, dx, dy, dz), (cx, cy, cz, cdx, cdy, cdz)) in FIXTURES:
        assert x >= 15.0 and x + dx <= L - 15.0, (_k, "inside the side walls")
        assert y >= 15.0 and y + dy <= W - 15.0, (_k, "inside the long walls")
        assert z + dz <= H - 20.0, (_k, "under the ceiling line")
        piece = box(x, y, z, dx, dy, dz).cut(box(cx, cy, cz, cdx, cdy, cdz))
        fix = piece if fix is None else fix.union(piece)
    return fix


SPEC = {
    "unit": UNIT,
    "extras": {"fixtures": _fixtures},
    "rho_map": {"floor": "FRP", "wall_long_a": "FRP", "wall_long_b": "FRP",
                "wall_end_solid": "FRP", "wall_end_door": "FRP",
                "fixtures": "304", "nozzles": "304"},
    "drop_keys": (),
    "drain_xy": DRAIN_XY,
    "vent_xy": VENT_XY,
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the room shell "
                     "fills the node box 3000 x 2000 x 2400, walls to the 2380 "
                     "ceiling line, vent flush at the 2400 top)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N2 wash-water feed on -Y at z 160, N1 grey "
                    "water out on +Y at z 600; N3 drain flush at the envelope bottom "
                    "under the shower tray; N4 vent flush at the envelope top on the "
                    "+Y wall line (the schedule z 800 datum predates the 2400 box - "
                    "stale datum, WORK_ORDER W12); no flange drawn (W4 110 % rule); "
                    "the schedule rating column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "habitation washroom fitout: FRP wet-wall room shell (8 m2, A-M-419; "
                "AQS-HAB-001) with the SS304 fixture set - shower tray, WC pan and "
                "wall-hung basin - in the +X wet zone (node size basis)",
        "a_farm": "the room shell is drawn at the node box per the room form class; "
                  "the fixture set and the nozzle set are drawn",
        "fixtures": "three study sheet-metal envelopes in the +X wet zone "
                    "(WORK_ORDER W12): shower tray 530 x 420, WC pan 380 x 385, "
                    "basin 480 x 380 hung on the -X wall segment clear of the door "
                    "swing; ceramic tile wet zones are a finish on the FRP panels - "
                    "no thickness stated, not drawn",
        "drainage": "the SS drainage duty section 3 names is the schedule nozzle "
                    "set: N3 floor drain under the shower tray, N1 grey water out "
                    "on +Y",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "FRP room shell: floor + four 15 mm partition walls, 3000 x 2000 x "
              "2400 outer, 900 x 2100 door opening in the -X end wall (8 m2 fitout "
              "shell, A-M-419; AQS-HAB-001)", 1, "FRP",
         round(sum(mass[k] for k in ("floor", "wall_long_a", "wall_long_b",
                                     "wall_end_solid", "wall_end_door")), 1), "make",
         "size_basis verbatim; ceramic tile wet zones are a finish on the FRP panels "
         "- no thickness stated on the duty, not drawn (WORK_ORDER W12); CA none "
         "(AQS-STD-001 shop rule polymer clause)"],
        ["2", "SS304 fixture set: shower tray, WC pan, wall-hung basin - study "
              "sheet-metal envelopes in the +X wet zone", 1, "SS304",
         mass["fixtures"], "buy",
         "catalogue sanitary ware; envelope + interface per plan rule 6 - study "
         "sheet envelopes at 304 density, maker prints govern at order; SS316 where "
         "sanitiser chemistry concentrates (duty section 3 alternative)"],
        ["3", "Nozzle set per docs-authority/nozzles/WASHROOM.csv: 4 rows drawn as "
              "DN15 tube stubs (grey water out, wash-water feed, drain, vent)", 4,
         "SS304", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4; the "
         "SS drainage duty section 3 names is this set; bores are the AQS-PIP-004 "
         "line DN, not recalculated (AQS-PIP-003)"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 fixture hold-down bolt", "ISO 3506 A4-70", 6,
         "fixture set to the slab and wall (study pattern)",
         "A4-70 stainless at the wet room (duty section 3 SS drainage class); "
         "study pattern, confirmed at fabrication"],
        [None, "M10 shell sill anchor", "ISO 3506 A4-70", 4,
         "room shell sill to the slab, 4 corners",
         "A4-70 on the FRP joint per the polymer-supplier-rule house practice; the "
         "anchor is not a wetted part"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the room corner; floor + four 15 mm partition walls per "
                 "the room form class, 900 x 2100 door opening in the -X end wall, "
                 "20 mm deck-finish build-down (walls to z 2380); fixture envelopes "
                 "in the +X wet zone (shower tray +X/+Y corner, WC pan beside it, "
                 "basin on the -X wall segment north of the door)",
        "supports": "shell on the slab on 4 sill anchors; fixtures bolted to the "
                    "slab and wall",
        "nozzle_spread": "the schedule gives face and height only; N1 on the +Y wall "
                         "at z 600, N2 on the -Y wall at z 160, N3 drain at "
                         "(2715, 1775) under the shower tray, N4 vent at (1500, "
                         "1985) on the +Y wall line through the top face; per-tag "
                         "positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
