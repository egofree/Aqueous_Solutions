"""BIOFILTER manufacturing model, AQS-PLAN-006 work order (X-FARM lane, tier 3, A-core).

Graph revision AD. Study. Not a PE stamp. Reads params.json (the W2 fields by the
tracker; the envelope, design and layout blocks beside them are builder-owned) and
rebuilds every solid through the shared close-out builder (`models/mfg/farm_closeout.py`).

Placement frame: x along the vessel, y along the width, z up, origin at the vessel
corner. Every dimension is an authority figure or a named layout choice:

- Vessel per the node: size_mm 1100 x 900 x 1000, HDPE walls and floor 15 mm, lid
  15 mm. The Oct-31 section-7 overshoot (bbox z 1012.1) does not survive the flush
  rebuild: the lid, the drawn media and every connection close inside the box
  (measured 1100.0 x 900.0 x 1000.0 mm, flush on all six faces) - the stale report
  clears from section 7, nothing resized.
- Media per the node size_basis ("moving-bed vessel 0.55 m3 at the 0.9 kg/d feed
  ammonia load, K1 media 0.2 m3"): the K1 moving-bed carrier envelope is drawn at
  0.2 m3 over the vessel floor - the media internal the node names, as a solid
  (A-core 4). The carrier charge is a buy row (plan rule 6), carried at the HDPE
  table density until the supplier TDS. The 0.55 m3 moving-bed volume is a duty
  figure reported on the duty sheet, not a model claim. The Oct-31 `stubs_mm`
  pair (two +X studs at z 20) is superseded by the schedule rows and leaves the
  params file.
- Nozzles: all 12 rows of docs-authority/nozzles/BIOFILTER.csv drawn at tag, face,
  height and bore as atmospheric open-bore tube stubs flush at the envelope faces
  (duty section 4: DN15/DN50, no flange class, atmospheric tube or hose). N1/N2 in
  on -Y at z 240 (N2 DN50); N9 in on -Y at z 160; N3/N4/N5 out on +Y at z 900 (DN50)
  with N6 bleed beside them; N10/N11/N12 out on +Y at z 600; N7 drain flush at the
  envelope bottom; N8 vent flush at the envelope top (the schedule z 1200 datum
  predates the 1000 box - stale datum, hold W12). HDPE/PVC per duty section 3; no
  flange is drawn (W4 110 % rule); the schedule rating column (Class 150) is
  carried verbatim as text.
- Duty section 7 repair: the sheet's "The unit is retired from the graph" sentence
  predates the node's return to `present`; the line is brought back to the
  generator's present-unit wording (the envelope is `cad/stl/BIOFILTER.stl`).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))            # models/mfg: lib, tracker, farm_hab
sys.path.insert(0, str(HERE.parents[2]))        # repo root: models.*

from models.mfg import farm_closeout            # noqa: E402

UNIT = "BIOFILTER"
T = 15.0                                        # wall/floor
MEDIA_VOL = 0.2e9                               # mm3 - node size_basis: K1 media 0.2 m3


def media_envelope(P):
    L, W, H = (float(v) for v in P["size_mm"])
    ix, iy = L - 2 * T, W - 2 * T
    d = MEDIA_VOL / (ix * iy)                   # 214.8 mm over the floor
    return farm_closeout.box(T, T, T, ix, iy, round(d, 1))


SPEC = {
    "unit": UNIT,
    "liner_bag": False,
    "rho_map": {"media": "HDPE"},               # K1 PE carrier class at the HDPE row
    "drop_keys": ("stubs_mm",),                 # superseded by the schedule rows
    "extras": {"media": media_envelope},
    "cad_stl_scope": "build solid, metres (X-PAR-04 envelope registry; the flush "
                     "rebuild fills the node box 1100 x 900 x 1000)",
    "nozzle_idiom": "atmospheric open-bore tube stubs flush at the envelope faces "
                    "(duty section 4: DN15/DN50, no flange class, atmospheric tube "
                    "or hose); N1/N2 in on -Y at z 240 (N2 DN50), N9 in on -Y at "
                    "z 160; N3/N4/N5 out on +Y at z 900 (DN50) with N6 bleed "
                    "beside them, N10/N11/N12 out on +Y at z 600; N7 drain flush "
                    "at the envelope bottom; N8 vent flush at the envelope top "
                    "(schedule z 1200 predates the 1000 box - stale datum, hold "
                    "W12); no flange drawn (W4 110 % rule); the schedule rating "
                    "column (Class 150) carried verbatim as text",
    "machine": lambda P, dims, mass: {
        "type": "nitrifying moving-bed biofilter (Nitrosomonas + Nitrobacter "
                "biofilm on moving-bed media, node design): HDPE vessel 1100 x "
                "900 x 1000 with 15 mm walls and floor, 15 mm lid, and the K1 "
                "carrier envelope drawn at the node's 0.2 m3 over the floor",
        "media": "K1 moving-bed carrier envelope 0.2 m3 (node size_basis) drawn "
                 "as a solid; the charge is a buy row (plan rule 6) carried at "
                 "the HDPE table density until the supplier TDS (hold, W12); the "
                 "0.55 m3 moving-bed volume is a duty figure, not a model claim",
        "o2": "aerobic: 2 mol O2 per mol NH4+ nitrified (node design) - the "
              "aeration hardware has no position or rating on the node, not "
              "drawn (hold, WORK_ORDER W12)",
        "misfit": None,
        "material": P.get("material"),
        "ca_mm": 0.0,
    },
    "bom": lambda P, mass, dims: [
        ["1", "HDPE vessel: walls and floor 15 mm, 1100 x 900 x 1000 outer, lid "
              "15 mm", 1, "HDPE (duty section 3)",
         mass["vessel_shell"] + mass["lid"], "make",
         "size_mm verbatim; CA does not apply to the polymer (AQS-STD-001)"],
        ["2", "K1 moving-bed carrier envelope, 0.2 m3 over the vessel floor "
              "(node size_basis)", 1, "PE carrier class (K1)",
         round(mass["media"] * 0.15, 1), "buy",
         "the drawn envelope carries ~0.15 of its solid volume as bare carrier "
         "PE (the hardware-cloth idiom for open media); the charge is a buy row "
         "(plan rule 6); supplier TDS at order (hold, WORK_ORDER W12)"],
        ["3", "Nozzle set per docs-authority/nozzles/BIOFILTER.csv: 12 rows drawn "
              "as DN15/DN50 HDPE tube stubs (4 DN50, 8 DN15)", 12,
         "HDPE/PVC (duty section 3)", mass["nozzles"], "make",
         "schedule tags/faces/heights verbatim; atmospheric per duty section 4"],
    ],
    "fastener_rows": lambda P: [
        [None, "M10 lid hold-down bolt + nut", "ISO 3506 A4-70", 8,
         "lid clamp hardware to the vessel rim, 8 around the perimeter (study "
         "pattern)",
         "polymer joint to the polymer supplier rule (A4-70 hardware); study "
         "pattern, confirmed at fabrication"],
        [None, "M10 base hold-down anchor", "ISO 898-1 8.8", 4,
         "vessel plinth to the slab, 4 corners (count from the model)",
         "8.8 on carbon steel per the plan grade rule (anchor is not a wetted "
         "part)"],
    ],
    "envelope_block": lambda P, dims: {
        "size_mm": P["size_mm"],
        "basis": P.get("size_basis"),
        "wall_mm": P.get("wall_mm"),
        "media": {"volume_m3": 0.2, "depth_mm": round(0.2e9 / ((1100 - 30) * (900 - 30)), 1),
                  "note": "node size_basis K1 media 0.2 m3, drawn over the floor"},
        "measured_bbox_mm": dims,
    },
    "layout_block": lambda P: {
        "frame": "origin at the vessel corner; shell 1100 x 900 x 1000 outer, "
                 "cavity 1070 x 870, media envelope to z ~230; lid on the rim at "
                 "z 985",
        "supports": "vessel plinth to the slab on 4 base anchors; lid clamped to "
                    "the rim by 8 hold-downs",
        "nozzle_spread": "the schedule gives face and height only; DN50 rows "
                         "centred on the +Y wall at z 900, inlets on -Y at z 240/"
                         "160, the z 600 outlet rows beside them, drain at the "
                         "base centreline, vent at the top centreline; per-tag "
                         "positions in check.nozzles_drawn",
        "hardware_idiom": "connection hardware flush at the envelope faces",
    },
}


def parts(P):
    return farm_closeout.unit_parts(P, SPEC)


if __name__ == "__main__":
    farm_closeout.build_and_export(HERE, SPEC)
