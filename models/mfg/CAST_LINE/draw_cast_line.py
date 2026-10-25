"""CAST_LINE drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
models/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front       general arrangement, front elevation (-Y)
  ga_side        general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  fr01           bench frame + mould-table deck + runout roller table + scrap chute
  mt01           mould stations: backing platens, jackets, fine-graphite inserts
  ps01           melt path: refractory trough, risers, drain well, pour station,
                 vent hood plenum + N6 tap
  gd01           guards, static shear/stop block, discharge lane guides, mould-change
                 gantry
  iso01          isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_cast_line.py           # SVG source from the build
    python3 docs-authority/_drawings.py     # title block + register rows
    python3 docs-authority/_pid_sheets.py   # re-appends the AQS-PID-001 register section
    <cq python> draw_cast_line.py           # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "cast_line.py")
parts, P = ns["parts"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

frame_group = union_all([parts[k] for k in ("frame", "deck", "roller_table", "scrap_chute")])
mould_group = union_all([parts[k] for k in ("mould_seats", "mould_inserts")])
pour_group = union_all([parts[k] for k in ("pour_station", "launder_group", "n1_port", "n5_port", "vent_hood", "n6_port")])
guard_group = union_all([parts[k] for k in ("guards", "shear_block", "gantry", "lane_guides")])
full = union_all(list(parts.values()))

SHEETS = [
    ("ga_front", full, (0, 1, 0),
     ['Keys: 1500 overall length (line axis +X: melt-in tail at 0, discharge head at 1500); 800 overall width (-Y guard plane to the +Y operator guide rail); 1500 overall height (gantry beam top)',
      'Deck plane z 600 (task-04 schedule outlet datum); roller-table roller tops at z 600; gantry beam z 1460..1500',
      'Connection heights per the task-04 schedule: N1 -X z 160, N2 -Y mouth top edge z 600, N3/N4 +X mouth top edges z 600, N5 bottom z 50, N6 top z 800',
      'Vent hood plenum z 720..792 over the pour zone; static shear/stop block with a floor pedestal at the line end',
      'Manual line: hand-tilt ladle and hand-fed rollers; no actuator or electrical view claimed (0 kW node duty)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Keys: 800 overall depth (-Y rear guard plane at 0, +Y guide rail outer face at 800); deck spans x 60..800',
      'Mould seats under the deck: backing platen z 502..548, jacket shell t6 z 486..602, insert cavity opens into the seat from above',
      'Melt path below the deck: refractory trough invert z 100 (inversion 100 mm), distribution header feeding both bottom-fill risers, drain well under the deck at x 340',
      'Pour station: ladle shell OD280 x 240 (top z 850), tilt post and arm above the deck, trunnion lugs bolted under the arm saddle',
      'Runout roller table x 800..1500: solid rollers D70 x 520 on D20 end shafts in 2-bolt pillow blocks; bearer rails overlap the frame rails',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1 -X face, y 400, z 160: DN15 Class 150, molten-metal inlet to the under-deck trough (schedule face: inlet)',
      'N2 -Y face, x 650..750, mouth top edge z 600: solids (scrap drop) chute into the mould-table zone (schedule face: outlet)',
      'N3 +X face, y 250..350, mouth top edge z 600: discharge lane guide (schedule face: outlet)',
      'N4 +X face, y 550..650, mouth top edge z 600: second discharge lane guide (schedule face: outlet)',
      'N5 bottom face, (340,400): DN15 Class 150 drain flange, sump face z 50 (schedule face: bottom)',
      'N6 top face, (420,400): DN15 Class 150 vent tap on the hood plenum, face z 800 (schedule face: top)',
      'Heights/bore/rating per docs-authority/nozzles/CAST_LINE.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("fr01", frame_group, (0, 1, 0),
     ['Bench weldment: 6 legs SHS 80 x 80 to z 580 welded into the longitudinal rails (100 wide x 30, z 570..600); feet 160 x 160 x 12 with 4 x M12 anchor holes each (fasteners.csv item 2)',
      'Cross members 60 x 48 under all three rail lines (z 552..600, welded into legs and rails)',
      'Mould-table deck t10 over the seats: seat passes 190 x 150, pour pocket x 50..190 y 360..440, drain-well pass at x 340',
      'Tail plate 60 x 520 x 30 closing the -X end under the trough head; the deck plane z 600 is the schedule outlet datum',
      'Runout table: bearer rails 110 wide (y 100..210 and 590..700, z 540..580) overlap the frame rails; guide-rail posts overlap the cross members',
      'Scrap chute: box 100 x 200 x 80 welded off the -Y face; general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: bench frame, deck, runout roller table, scrap chute."),
    ("mt01", mould_group, (0, 1, 0),
     ['Mould seats x2 at y 250 and y 550: steel backing platen 240 x 180 x 46 with a 170 x 130 cavity; seat frame bolted under the deck (4 x M12 per seat, fasteners.csv item 3)',
      'Water jacket assemblies x2: shell t6 (z 486..602) with 170 x 132 cavity; CW stubs run toward the machine-side manifold; the cooling-water loop is a utility circuit without a graph edge, sized at the task 12 first articles (params.json holds)',
      'Fine-graphite inserts x2, 160 x 120 x 110: hot faces per duty section 3 (X-MAT-22 graphite class); open-top cavity 110 x 70 x 60 (0.462 L, about 3.7 kg Cu class per params.json assumptions)',
      'Bottom-fill riser pass D24 through each insert floor into the cavity floor; the riser head D28 (ps01) seats into this pass',
      'Insert change-out is the unit task 12 work order; general tolerance ISO 2768-m'],
     "Fabricated part sheet: mould seats, water jackets, fine-graphite inserts."),
    ("ps01", pour_group, (0, 1, 0),
     ['Melt path: refractory trough x 40..600 (invert z 100, bore 48 high) in a steel channel base; distribution header along x 280 y 246..546 feeding both risers',
      'Graphite bottom-fill risers x2: D28 x 350 from the header up into each insert floor (melt bore class D20); the N5 drain well at x 340 is an OD75 frozen-slug pig tube',
      'N1 DN15 Class 150 flange at the -X face z 160 (OD95 class per AQS-PIP-003) with an OD21.3 spigot reaching the trough head; N5 DN15 flange face z 50 down-facing',
      'Pour station: 12 kg-class ladle (shell OD280 x 240 t25 + D115 x t25 alumina ram lining, relining is a buy item) between two trunnion lug plates bolted under the tilt-arm saddle (2 x M16 T-bolts, fasteners.csv item 1); hand tilt, no actuator',
      'Vent hood plenum 500 x 200 over the pour zone (top plate t6); N6 DN15 Class 150 flanged tap at top z 800 ties to the plant vent header at detail design',
      'Gasket faces per AQS-PIP-003 class practice (AQS-STD-002 section 14); general tolerance ISO 2768-m'],
     "Fabricated part sheet: melt path, pour station, vent hood + N6 tap."),
    ("gd01", guard_group, (0, 1, 0),
     ['Rear hot-zone guard: panel frame 780 x 860 on floor posts (40 x 12) and a floor channel, anchored to the frame feet; mesh opening 748 x 832 fitted at fabrication (AQS-BLD-012 class)',
      'Static shear / stop block: pedestal to the floor (80 x 160), block head z 600..800, tool-steel knife insert at the -X face, strike bar top; knife + strike surfaces are the +X face pick at x 1500',
      'Sprue/runner shear campaign is a task 12 traveller item; no rate is claimed (params.json holds)',
      'Discharge lane guides x2 at the +X face (20 x 100 x 40 each) pick the N3/N4 mouth edges at z 600',
      'Mould-change gantry: 2 columns SHS 80 x 80 (x 260..340) to z 1500, top beam, trolley body, hook lug; SWL 250 kg manual chain hoist = purchase item named with the rating (A-MACH); no load calc claimed (params.json holds)',
      'Fixed cover over the knife zone (t6 plate + side ribs); general tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: guards, static shear, lane guides, mould-change gantry."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X line axis toward the discharge head, y across to the operator guide rail, z up',
      'Graph revision AC is the model authority for this build; STEP (export/cast_line.step) is the solids of record',
      'The whole machine is one manifold build solid (AQS-PLAN-006 A-core 4): bolted/press-fitted interfaces are modeled touching or with 0.1 mm interference',
      'No machine cooling-water rate, ladle residence time or mould output rate is drawn or claimed'],
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
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{sid}.svg"
    if svg.exists() and "aqs-title-block" in svg.read_text():   # already stamped by _drawings.py: geometry frozen, PDF pass only
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)          # notes only; the title block + register rows happen in _drawings.py
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
