"""WAX_PATTERN manufacturing model, AQS-PLAN-006 work order (shell-casting chain).

Graph revision AD. Study. Not a PE stamp. Reads the plant graph through the shared
reader (models/mfg/lib/graph_node.py) and rebuilds every solid through the shared
close-out builder (models/mfg/farm_closeout.py), the AQUA_TANK pattern.

Placement frame: x along the bench, y along the depth, z up, origin at the bench
corner. Every dimension is an authority figure or a named layout choice:

- The unit is the wax pattern injection bench feeding the investment-shell chain
  per the node size basis: "prep class study minimum; live on the wax make-up
  import + 90 % reclaim (A-M-286)". The build fills the node box 800 x 600 x 1200
  flush: a 5 mm SS304 sheet cabinet (walls, floor, top) carrying the duty section
  3 hardware as the params `extras_mm` envelopes - the 304L wax melt pot (the 10 L
  class the graph design names) on its steam/hot-water manifold at the -X floor,
  the 0.5 kW injector and the pattern die beside it, a PP-H storage bin and a PE
  drain pan. The injector/heater unit purchases at fabrication (WORK_ORDER W12);
  the extraction hood of the former bench_prep build is withdrawn - the N5 vent
  rides the cabinet top.
- Nozzles: all 6 rows of docs-authority/nozzles/WAX_PATTERN.csv drawn at tag, face
  and bore as atmospheric open-bore tube stubs flush at the envelope faces (duty
  section 4; the schedule rating column Class 150 carried verbatim as text; no
  flange drawn, W4 110 % rule). N1 wax patterns out on +Y at z 600; N2 condensate
  reclaim (DN15) and N3 make-up wax in (solids row, drawn DN15, bore not
  calculated) on -Y at z 160; N4 drain flush at the envelope bottom; N5 vent flush
  at the envelope top (the schedule z 800 datum sits below the 1200 build height);
  N6 power terminal is a cable schedule row - carried in the record, never drawn.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "WAX_PATTERN"

# The shared engine draws every schedule row as a stub (the AQUA_TANK-line
# schedules have no non-piped rows). The two row classes this schedule carries
# beside pipes are handled here, so geometry and record stay consistent: cable
# rows are carried, never drawn; solids rows keep their DN15 stub with the
# bore-not-calculated note.
_engine_draw_nozzles = farm_closeout.draw_nozzles


def _draw_nozzles(P, spec):
    noz, drawn = _engine_draw_nozzles(
        {**P, "nozzles": [r for r in P["nozzles"] if r["size"] != "cable"]}, spec)
    H = float(P["size_mm"][2])
    for r in P["nozzles"]:
        tag = r["tag"]
        if r["size"] == "cable":
            drawn[tag] = {"style": "carried", "dn": r["size"], "face": r["face"],
                          "height_mm": r["height_mm"], "schedule_rating": r["rating"],
                          "service": r["service"],
                          "note": "power terminal row - a cable schedule row: carried "
                                  "verbatim, never drawn"}
        else:
            if r["size"] == "solids":
                drawn[tag]["note"] += ("; the solids row is a non-piped transfer: "
                                       "drawn DN15, bore not calculated (duty "
                                       "section 4)")
            if r["face"] == "top" and float(r["height_mm"]) < H - 1.0:
                drawn[tag]["note"] = drawn[tag]["note"].replace(
                    "predates the build height", "sits below the build height")
    return noz, drawn


farm_closeout.draw_nozzles = _draw_nozzles


SPEC = {
    "unit": UNIT,
    "rho_map": {"cabinet_shell": "304", "top": "304", "steam_manifold": "304",
                "wax_pot": "304", "injector": "304", "pattern_die": "304",
                "wax_bin": "PP", "drain_pan": "HDPE", "nozzles": "304"},
    "drop_keys": ("layout_note",),
    "drain_xy": (110.0, 560.0),
    "vent_xy": (400.0, 300.0),
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the build "
                     "fills the node box 800 x 600 x 1200 flush)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4); N1 wax patterns out on +Y at z 600; N2 "
                    "condensate reclaim (DN15) and N3 make-up wax in on -Y at "
                    "z 160, the solids row drawn DN15 with the bore not "
                    "calculated; N4 drain flush at the envelope bottom; N5 vent "
                    "flush at the envelope top (the schedule z 800 datum sits "
                    "below the 1200 build height); N6 is a cable schedule row, "
                    "carried in the record, never drawn; no flange drawn (W4 "
                    "110 % rule); the schedule rating column (Class 150) "
                    "carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "wax pattern injection bench for the shell-casting chain: 304L "
                "wax melt tank on its steam/hot-water manifold, injection head "
                "and pattern die, PP-H storage bins and PE drain pans (duty "
                "section 3; graph design pot 10 L, injector 0.5 kW)",
        "a_farm": "the cabinet is drawn at the node box flush; the pot, manifold, "
                  "injector, die, bin and pan envelopes are drawn",
        "purchased": "the 0.5 kW injector/heater unit purchases with the pot at "
                     "fabrication (duty section 3 names the class, not a maker "
                     "figure) - plan rule 6 (hold, WORK_ORDER W12)",
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "SS304 sheet cabinet: 800 x 600 x 1200, 5 mm walls, floor and top "
              "(prep-class study box; A-M-286 wax split basis)", 1,
         "SS304 (duty section 3)", mass["cabinet_shell"] + mass["top"], "make",
         "size_basis verbatim; dry hydrocarbon service, no corrosive species "
         "(duty section 3)"],
        ["2", "304L wax melt pot envelope 250 x 250 x 160 (10 L class), wax "
              "reclaim returned to the pot", 1, "304L (duty section 3)",
         mass["wax_pot"], "make",
         "graph design pot_L 10; 304/316L hot-melt practice per duty section 3"],
        ["3", "Steam/hot-water manifold envelope 280 x 280 x 100 under the pot", 1,
         "SS304 (duty section 3)", mass["steam_manifold"], "make",
         "the melt-tank heat manifold duty section 3 names; loop hardware "
         "tie-in is plant scope (hold, WORK_ORDER W12)"],
        ["4", "Injection head envelope 200 x 200 x 600 with the 0.5 kW class", 1,
         "SS304 head (unit purchased)", mass["injector"], "make",
         "graph design injector_kW 0.5; the injector/heater unit purchases with "
         "the pot at fabrication (hold, WORK_ORDER W12)"],
        ["5", "Pattern die envelope 150 x 150 x 200", 1,
         "SS304 (die material study)", mass["pattern_die"], "make",
         "the pattern dies the work order names; die material and cavities are "
         "finished against the first shell run (hold, WORK_ORDER W12)"],
        ["6", "PP-H wax storage bin envelope 200 x 200 x 300", 1,
         "PP-H (duty section 3)", mass["wax_bin"], "make",
         "duty section 3 storage-bin class at the 80 C thermoplastic house limit"],
        ["7", "PE drain pan envelope 200 x 150 x 60 under the injector deck", 1,
         "PE (duty section 3)", mass["drain_pan"], "make",
         "duty section 3 drain-pan class"],
        ["8", "Nozzle set per docs-authority/nozzles/WAX_PATTERN.csv: 6 rows - "
              "2 solids rows drawn as DN15 stubs (bore not calculated), DN15 "
              "reclaim, drain, vent, and the N6 cable row carried, never drawn",
         5, "SS304", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 wedge anchor", "ISO 898-1 8.8", 4,
         "cabinet to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part); study embedment, confirmed at fabrication"],
        [None, "M8 socket bolt", "ISO 3506 A4-70", 8,
         "pot/manifold and injector hold-down to the cabinet floor, 4 each "
         "(study pattern)",
         "A4-70 on the SS304 joints per the grade rule; study pattern, "
         "confirmed at fabrication"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "bench_hardware_mm": {r[6]: r[:6] for r in P.get("extras_mm", [])},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the bench corner; 5 mm SS304 cabinet 800 x 600 x "
                 "1200; melt pot on its steam manifold at the -X floor, "
                 "injector and pattern die at the +X floor, PP-H bin and PE "
                 "drain pan along the +Y wall (the former extraction hood is "
                 "withdrawn - the vent rides the cabinet top)",
        "supports": "cabinet to the slab on 4 wedge anchors; pot and injector "
                    "hold-down bolts to the cabinet floor",
        "nozzle_spread": "the schedule gives face and height only; N1 on the +Y "
                         "wall at z 600, N2/N3 on the -Y wall at z 160, N4 drain "
                         "at the -X floor corner, N5 vent at the top centreline; "
                         "per-tag positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
