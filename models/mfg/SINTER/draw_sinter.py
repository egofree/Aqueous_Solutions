"""SINTER drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, shell01 (water-cooled jacket + charge
door + fibre lining), muffle01 (alumina muffle + lid + hearth + graphite element
racks), aux01 (controls bay + plinth + connection hardware), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy, sys

import cadquery as cq

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from lib import sheets                                       # noqa: E402

ns = runpy.run_path(HERE / "sinter.py")
parts, R = ns["parts"], ns["report"]
unit = "SINTER"
REV = R["graph_revision"]


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = union_all([parts["jacket_outer"], parts["jacket_inner"], parts["door_face"],
                   parts["fibre_lining"]])
muffle = union_all([parts["muffle"], parts["muffle_lid"], parts["hearth_plate"],
                    parts["element_racks"]])
aux = union_all([parts["plinth"], parts["controls_cabinet"], parts["N1_stock_chute"],
                 parts["N2_drain"], parts["N3_vent_riser"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
M = R["machine"]
S = R["standby"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the node N+1 rated envelope (A-M-282), filled exactly',
      'Ti/Mo/Cr powder sinter furnace, N+1 consolidation standby of ROLL: ' + S["state"],
      'Water-cooled steel jacket (double wall + water annulus) with the charge door on -X',
      '95 % alumina muffle with graphite element racks; 8 kW controls bay on +X'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Jacket walls t{M["jacket"]["wall_mm"]:g} with the {M["jacket"]["water_gap_mm"]:g} mm cooling-water '
      'annulus (study fab-page value - hold, W12); the water circuit is loop hardware, not modeled',
      'Ceramic-fibre board between jacket and hot zone (study construction); 1300 C hot zone per the node design',
      'Jacket z 60..1160 on the plinth; door clamp studs in fasteners.csv; controls bay x 660..1000',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/SINTER.csv at tag, face and bore',
      'N1 solids stock chute +X at z 600, bore not calculated (W4 rule); N2 drain through the plinth flush at the bottom',
      'N3 vent riser on the jacket roof flush at the envelope top (the 800 datum is the schedule placeholder - hold, W12)',
      'Heights/bore/rating per the schedule; compass faces are the registered layout choice (params.json layout block)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("shell01", shell, (0, 1, 0),
     ['Water-cooled nickel-free steel jacket: double wall t4, 15 mm water annulus; the hot zone stays nickel-free (CRC_TI class)',
      'Charge door flush at the -X face over a through opening (clamp studs, fasteners.csv item 2)',
      'Ceramic-fibre board lining with the door throat; wall and lining thicknesses are study values (hold, W12)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: jacket + door + lining. Welds per ISO 2553."),
    ("muffle01", muffle, (0, 1, 0),
     [f'95 % alumina muffle OD {M["muffle"]["od_mm"]:g} x {M["muffle"]["h_mm"]:g} with lid, on the alumina hearth (buy consumable set, change-out per campaign)',
      'Graphite resistance elements OD 24, wall racks and crown (13 rods; buy consumable set) - duty section 3 element class at 1300 C',
      'Inert/vacuum atmosphere inside the muffle; the atmosphere package purchases at fabrication (hold, W12)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: muffle + elements + hearth."),
    ("aux01", aux, (0, 1, 0),
     ['Controls cabinet 8 kW connected (node design) on the +X bay, purchased envelope per plan rule 6',
      'Plinth 1000 x 1000 x 60 with 8 M12 slab anchors (fasteners.csv item 1)',
      'N1 stock chute and N2/N3 schedule hardware flush at the envelope faces',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: controls bay + plinth + connection hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; jacket, muffle and controls bay in place over the 1000 x 1000 x 1500 envelope',
      'The live graph revision in params.json is the model authority for this build; STEP (export/sinter.step) is the solids of record',
      'The powder charge is drawn as a process-inventory solid - not a BOM part'],
     "Isometric orientation sheet."),
]

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block bottom-right

def add_notes(svg_path, notes):
    s = svg_path.read_text()
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{h + BAND}"', s, count=1)
    rows = [f"Graph revision {REV} - {svg_path.stem}: {n}" for n in notes]
    block = f'<g id="aqs-fab-notes" transform="translate(0,{h})" font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">'
    for i, n0 in enumerate(rows):
        block += f'<text x="6" y="{24 + 13 * i}">{n0}</text>'
    block += '</g>'
    svg_path.write_text(s.replace("</svg>", block + "</svg>"))

pdf = "stamped pass pending"
import re  # noqa: E402
for sid, shape, pdir, notes, _title in SHEETS:
    svg = HERE / "drawings" / f"{sid}.svg"
    if not svg.exists():
        pass   # fresh write below
    elif "aqs-title-block" in svg.read_text():   # already stamped by _drawings.py: geometry frozen, PDF pass only
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(HERE / "drawings" / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)          # notes only; the title block + register rows happen in _drawings.py
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
