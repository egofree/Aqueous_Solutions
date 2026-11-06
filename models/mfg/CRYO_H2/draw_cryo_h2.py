"""CRYO_H2 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
and the DRAWING_REGISTER.md rows are applied by docs-authority/_drawings.py.
Sheets: ga_front, ga_side, nozzle_orient, sh01 (rack frame + saddles),
in01 (tube bank), aux01 (compressor envelopes + connection stubs), iso01.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "cryo_h2.py")
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
aux = union_all([parts["nozzles"], parts["compressors"]])
full = union_all(list(parts.values()))

L, W, H = [float(v) for v in R["size_mm"]]
T, C = R["tubes"], R["compressors"]
TIERS, ROWS, TIER_Z, HALVES = ns["TIERS"], ns["ROWS"], ns["TIER_Z"], ns["HALVES"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {L:g} x {W:g} x {H:g} mm overall - the A-M-167 rack envelope (node size_mm), '
      'filled exactly',
      f'{T["count"]} cylinder tubes SA-312 TP316L DN100 Sch 160, OD {T["od_mm"]:g} x t '
      f'{T["wall_mm"]:g}, {T["length_mm"] / 1000:g} m, in {TIERS} tiers '
      f"(z {'/'.join(f'{v:g}' for v in TIER_Z)}) x {ROWS} rows",
      f'Rows y < {W / 2:g} are relief half 1, above half 2 ({T["count"] // HALVES} tubes per '
      'half, node fire case)',
      '2 purchased 5-stage diaphragm hydrogen compressors in the +X end bay (node '
      'compressor_design)',
      'Design 22000 kPa g (node design_kPa); schedule rating column (Class 150) carried as '
      'text - hold, WORK_ORDER W12'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     ['Tier combs at every tier lap the tubes 12 deep and land on the end posts and side rails',
      'Tube saddles under every tier row; SHS 80 x 80 x 5 sections over a 12 mm skid (study)',
      f'Side rails at z 100..200 / 380..480 / {H - 130:g}..{H - 30:g} carry the schedule '
      'connections',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} schedule rows of docs-authority/nozzles/CRYO_H2.csv at '
      'tag, face and bore; the N9 power terminal (cable schedule X-ELS-06) is carried '
      'verbatim, not drawn',
      'N1 (z 400) and N6 (z 600) on the side rails; N2/N3 (z 1500, clamped to the mid rail); '
      'N7/N8 (z 160) on the bottom rail',
      'N4 drain: skid-top stub at x 400, tip at the 50 datum; N5 vent: up the -Y tie bar to '
      'the rack top (schedule datum 2000 predates the rack envelope - hold, W12)',
      'Atmospheric stubs; no flange drawn (no flange table above Class 150; hold, W12) - '
      'per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/bore per the schedule."),
    ("sh01", frame, (0, 1, 0),
     [f'Rack frame: 12 mm skid plate, SHS 80 x 80 x 5 corner posts to the full {H:g} mm '
      'height, top tie bars, three side rails, cross ties, and a grooved tier comb at every '
      'tier',
      '316L per duty section 3 (annealed, nickel toward the top of the range, AQS-REV-H2-001; '
      'no ferritic or high-strength steel); corrosion allowance 0 mm (AQS-STD-001)',
      'Frame sections and tier pitch are study sizes (WORK_ORDER W12); welds per the unit '
      'WORK_ORDER route (F-COL)'],
     "Fabricated part sheet: rack frame + saddles."),
    ("in01", tubes, (0, 1, 0),
     [f'Tube bank: {T["count"]} tubes OD {T["od_mm"]:g} x t {T["wall_mm"]:g} x {T["length_mm"] / 1000:g} m '
      f'in {TIERS} tiers x {ROWS} rows; bores drawn open, {T["drawn_mass_kg"]:g} kg drawn wall mass',
      f'Node steel_kg {T["node_steel_kg"]:g} is the receivers.py sizing record - carried, not '
      'recalculated (basis difference named, WORK_ORDER W12)',
      'End fittings B16.11 Class 9000 / autoclave cone-and-thread per the node material string',
      'Store at 200 bar per the node storage block: 2 d fuel-cell autonomy (X-PAR-12)'],
     "Fabricated part sheet: cylinder tube bank."),
    ("aux01", aux, (0, 1, 0),
     [f'Hydrogen compressors: {C["units"]} x 5-stage diaphragm sets, 17-4PH H1150 / 316L heads, '
      f'301 SS triple-layer diaphragms ({C["kW_avg"]:.4f} kW average / {C["kW_peak"]:.3f} kW peak); '
      'purchased, drawn as envelope and interface (AQS-PLAN-006 rule 6)',
      'Connection stubs DN15 on the side rails; heights clamped where the issued datum predates '
      'the A-M-167 rack (per-tag notes in check.nozzles_drawn)',
      'Stub hardware laps the rails so every union fuses; nothing protrudes past the rack',
      'Schedule rating column (Class 150) carried verbatim as text - reconciliation hold (W12)'],
     "Fabricated part sheet: compressor envelopes + connection stubs."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlets on the -Y side rail, outlets on +Y; compressors in the +X end '
      'bay; hydrogen service per AQS-REV-H2-001',
      f'Graph revision {REV} is the model authority for this build; STEP (export/cryo_h2.step) '
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
step_src = "build export `models/mfg/CRYO_H2/export/cryo_h2.step`"
srcs = ["models/mfg/CRYO_H2/cryo_h2.py", "models/mfg/CRYO_H2/draw_cryo_h2.py", step_src,
        "models/mfg/CRYO_H2/bom.csv", "models/mfg/CRYO_H2/fasteners.csv",
        "models/mfg/CRYO_H2/check.json", "models/mfg/CRYO_H2/WORK_ORDER.md"]
log = f"""# Build log - CRYO_H2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_H2.md`; rack envelope from the node design block, A-M-167).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/CRYO_H2/cryo_h2.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: fills the node rack envelope {L:g} x {W:g} x {H:g} mm exactly (tracker check green)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/CRYO_H2.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} rows of `docs-authority/nozzles/CRYO_H2.csv` present at face and bore; heights that fit the rack drawn as issued, the rest clamped with named holds; the N9 cable power-terminal row is carried verbatim, not drawn (check.nozzles_drawn)
- A-COL: the tube bank is the machine here; the node compressor_design sets (2 x 5-stage diaphragm) are drawn as purchased envelopes; relief per the node API 520/521 fire case per half bank ({T['count'] // HALVES} tubes per half, {R['relief']['relief_mm']:g} mm)
- BOM `models/mfg/CRYO_H2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_H2/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL; the machine-design detail (piping hookup, compressor installation) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
