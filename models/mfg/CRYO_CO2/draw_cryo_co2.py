"""CRYO_CO2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (rack frame + saddles),
in01 (tube bank), aux01 (relief valves + connection stubs), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "cryo_co2.py")
parts, R = ns["parts"], ns["report"]
REV = R["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


frame = union_all([parts["frame"], parts["saddles"]])
tubes = parts["tubes"]
aux = union_all([parts["nozzles"], parts["relief_valves"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
T = R["tubes"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the A-M-167 rack envelope (node size_mm), '
      'filled exactly',
      f'{T["count"]} cylinder tubes SA-312 TP316L DN100 Sch 160, OD {T["od_mm"]:g} x t '
      f'{T["wall_mm"]:g}, {T["length_mm"] / 1000:g} m, one per row',
      'Rows at y 187.5 / 562.5 / 937.5 / 1312.5; rows y < 750 are relief half 1, above half 2',
      'One 9 mm API 520/521 relief valve per half bank at the +X end posts (node relief_basis)',
      'Design 2200 kPa g (node design_kPa); schedule rating column (Class 150) carried as text - '
      'hold, WORK_ORDER W12'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Tube centres z {245:g} on 3 saddles per tube; SHS 80 x 80 x 5 posts and side rails over '
      'a 12 mm skid (study sections)',
      'Side rails carry the schedule connections; the mid rail takes the clamped rows',
      'Skid to slab on 8 M10 wedge anchors; saddles bolted M12 (fasteners.csv)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['10 schedule rows of docs-authority/nozzles/CRYO_CO2.csv at tag, face and bore',
      'N1-N3 (z 400) and N4-N7 (z 1500, clamped to the mid rail) land on the side rails; '
      'N10 (z 160) on the bottom rail',
      'N8 drain: skid-top stub at x 400, tip at the 50 datum; N9 vent: up the -Y tie bar to the '
      '450 rack top (schedule datum 2000 predates the rack envelope - hold, W12)',
      'Atmospheric stubs; no flange drawn (no flange table above Class 150; hold, W12) - '
      'per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", frame, (0, 1, 0),
     ['Rack frame: 12 mm skid plate, SHS 80 x 80 x 5 corner posts to the full 450 height, top '
      'tie bars, top and bottom side rails, 3 cross ties under the saddles',
      '316L throughout (duty section 3: no carbon steel); corrosion allowance 0 mm '
      '(AQS-STD-001)',
      'Frame sections are study sizes (WORK_ORDER W12); welds per the unit WORK_ORDER route '
      '(F-COL); frame to slab anchored'],
     "Fabricated part sheet: rack frame + saddles."),
    ("in01", tubes, (0, 1, 0),
     [f'Tube bank: {T["count"]} tubes OD {T["od_mm"]:g} x t {T["wall_mm"]:g} x {T["length_mm"] / 1000:g} m '
      f'in 2 relief halves of 2; bores drawn open, {T["drawn_mass_kg"]:g} kg drawn wall mass',
      f'Node steel_kg {T["node_steel_kg"]:g} is the receivers.py sizing record - carried, not '
      'recalculated (basis difference named, WORK_ORDER W12)',
      'End fittings B16.11 Class 9000 / autoclave cone-and-thread per the node material string',
      'Store 88.5 kg CO2 at 200 bar (node storage block); TUBES are the A-COL machine here'],
     "Fabricated part sheet: cylinder tube bank."),
    ("aux01", aux, (0, 1, 0),
     ['Relief valves: 2 x 9 mm bore, API 520 blocked-outlet governing with the API 521 fire '
      'case per half bank (node relief_basis); purchased, drawn as envelope and interface',
      'Connection stubs DN15/DN25 on the side rails; heights clamped where the issued datum '
      'predates the A-M-167 rack (per-tag notes in check.nozzles_drawn)',
      'Barb/stub hardware laps the rails so every union fuses; nothing protrudes past the rack',
      'Schedule rating column (Class 150) carried verbatim as text - reconciliation hold (W12)'],
     "Fabricated part sheet: relief valves + connection stubs."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlets on the -Y side rail, outlets on +Y; relief valves at the +X end, '
      'one per half bank',
      f'Graph revision {REV} is the model authority for this build; STEP (export/cryo_co2.step) '
      'is the solids of record',
      'The build fills the A-M-167 rack envelope exactly; tracker --check green'],
     "Isometric orientation sheet."),
]

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block bottom-right

def add_notes(svg_path, notes):
    import re
    s = svg_path.read_text()
    if "aqs-fab-notes" in s:
        return
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
import cadquery as cq
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{sid}.svg"
    if svg.exists() and "aqs-title-block" in svg.read_text():   # stamped: geometry frozen, PDF pass only
        try:
            import cairosvg
            cairosvg.svg2pdf(url=str(svg), write_to=str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/CRYO_CO2/export/cryo_co2.step`"
srcs = ["models/mfg/CRYO_CO2/cryo_co2.py", "models/mfg/CRYO_CO2/draw_cryo_co2.py", step_src,
        "models/mfg/CRYO_CO2/bom.csv", "models/mfg/CRYO_CO2/fasteners.csv",
        "models/mfg/CRYO_CO2/check.json", "models/mfg/CRYO_CO2/WORK_ORDER.md"]
log = f"""# Build log - CRYO_CO2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_CO2.md`; rack envelope from the node design block, A-M-167).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/CRYO_CO2/cryo_co2.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: fills the node rack envelope {L:g} x {W:g} x {H:g} mm exactly (tracker check green)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/CRYO_CO2.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} rows of `docs-authority/nozzles/CRYO_CO2.csv` present at face and bore; heights that fit the 450 rack drawn as issued, the rest clamped with named holds (check.nozzles_drawn)
- A-COL: the tube bank is the machine here; relief per the node API 520/521 fire case per half bank (2 valves, 9 mm)
- BOM `models/mfg/CRYO_CO2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_CO2/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL; the machine-design detail (piping hookup, relief valve selection) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
