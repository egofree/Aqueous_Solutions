"""CRYO_ASU drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002). Sheets:

  ga_front       general arrangement, front elevation (-Y)
  ga_side        general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (rows per docs-authority/nozzles/CRYO_ASU.csv)
  sh01           TSA bed set (shell, heads, grids, pedestals)
  in01           internals: 13X sorbent charges
  aux01          service group: purchased machinery envelopes, hose barbs, drain, vent
  iso01          isometric orientation sheet

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "cryo_asu.py")
parts, R = ns["parts"], ns["report"]
REV = R["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


beds = union_all([parts["beds"], parts["frame"]])
sorbent = parts["sorbent"]
aux = union_all([parts["nozzles"], parts["machinery"]])
full = union_all(list(parts.values()))

bx = R["beds"]["x_mm"]
BED_D = R["beds"]["bed_D_mm"]                 # node design block (AQS-PAR-001 sizing)
BED_L = R["beds"]["bed_L_mm"]
BED_PITCH = ns["BED_PITCH"]                   # model layout constant: bed_D + 100
N_PIPE = sum(1 for v in R["nozzles_drawn"].values() if v.get("style") != "carried")
N_SOLIDS = sum(1 for v in R["nozzles_drawn"].values() if v.get("style") == "solids")
M = R["machinery"]
SHEETS = [
    ("ga_front", full, (0, 1, 0),
     [f'Keys: {R["bbox_mm"][0]} x {R["bbox_mm"][1]} x {R["bbox_mm"][2]} mm overall (skid layout); '
      f'the node size_mm {R["size_mm"]} is the M0 study registry box (params size_note)',
      f'Misfit to report: the beds at the node design diameter {BED_D:.1f} mm cannot fit the '
      'study box; nothing is resized (AQS-PLAN-006 rule 3)',
      f'{R["beds"]["count"]} TSA beds D {BED_D:.1f} x {BED_L:.1f} on pedestals; CO2 compressor, '
      'condenser and Ar getter row at x 1700..2440',
      'Vent standpipe to the 2000 mm schedule datum on the bed 1 top head (API 2000 open vent)',
      'Liquor/process inventory: none - the noble-gas streams pass through (node internals row)'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", full, (1, 0, 0),
     [f'Bed axis band z {R["beds"]["axis_z_mm"][0]:g}..{R["beds"]["axis_z_mm"][1]:g} on 170 mm '
      'pedestals over a 200 mm plinth',
      'Support grids 20 mm under and over the 13X charge; grid laps the shell wall 3 mm',
      'Inlet rows on -Y, outlet rows on +Y (duty section 4 faces); hose makeup at the shell',
      'Purchased machinery drawn as envelope and interface (AQS-PLAN-006 rule 6)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     [f'{R["nozzle_count_schedule"]} scheduled interfaces of docs-authority/nozzles/CRYO_ASU.csv '
      f'at tag, face, height and bore; {N_PIPE} drawn rows, {N_SOLIDS} of them solids',
      'N1-N4 (z 400) and N5-N8 (z 1500) distributed across the beds in tag order, second row per '
      'bed offset 130 mm',
      'N11-N16 (z 160) are frame-level rows through the plinth: the datum sits below the bed '
      'shells; N13/N14/N15 are solids rows at DN15, bore not calculated',
      'N9 drain beside the bed 1 pedestal, tip at the 50 datum; N10 vent standpipe on bed 1 to '
      'the 2000 datum',
      'N17 (top, z 800) is the cable power terminal (cable schedule X-ELS-06): electrical, not '
      'piped - carried verbatim, not drawn',
      'Atmospheric per the API 2000 relief basis; schedule rating column (Class 150) carried '
      'verbatim as text - per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/heights per the schedule."),
    ("sh01", beds, (0, 1, 0),
     [f'{R["beds"]["count"]} bed assemblies: shell t 6 (house plate convention, study), flat '
      f'heads, grids t 20, on 200 x 200 pedestals at x {bx[0]:g} + {BED_PITCH:.1f}k',
      'Shell 316L per duty section 3; corrosion allowance 0 mm (AQS-STD-001); no carbon steel',
      f'Bed design from the node: bed_D_mm {BED_D:.3f}, bed_L_mm {BED_L:.3f} (AQS-PAR-001 sizing)',
      'Thermoplastic-free weldment: TIG welds per the unit WORK_ORDER route (F-COL); leak test '
      'of each bed'],
     "Fabricated part sheet: TSA bed set + base frame."),
    ("in01", sorbent, (0, 1, 0),
     [f'13X molecular-sieve charge per bed: {R["sorbent"]["kg_per_bed"]:g} kg booked '
      f'({R["sorbent"]["kg_drawn_total"]:g} kg drawn at the 700 kg/m3 study bulk density, '
      'capped by the bed length)',
      'The charge is the A-COL packing: a solid between the support grids, laps the lower grid '
      '5 mm so the union fuses',
      f'TSA regeneration {M["regen_kW"]:.2f} kW (node design regen_kW); blower '
      f'{M["blower_kW"]:.3f} kW',
      'Vendor TDS at order; replace per the duty service hours'],
     "Fabricated part sheet: 13X sorbent charges."),
    ("aux01", aux, (0, 1, 0),
     [f'CO2 two-stage compressor envelope 320 x 480 x 900 + motor bump ({M["co2_comp_kW"]:.3f} kW, '
      'node design); the design block comp_stages 4 vs the internals row two-stage - staging is '
      'a named hold',
      f'Condenser/chiller envelope with fan rings ({M["co2_chill_kW"]:.3f} kW) and the heated Ar '
      f'getter cartridge ({M["getter_kW"]:.2f} kW): purchased, drawn as envelope and interface '
      '(AQS-PLAN-006 rule 6)',
      'Hose barbs DN15/DN25/DN50 on the bed shells and plinth; barb profile a study proportion '
      '(lib/nozzles.py), finished against the hose supplier print',
      'Drain and vent standpipes DN15 to their schedule datums'],
     "Fabricated part sheet: machinery envelopes + nozzle hardware."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: inlets -Y, outlets +Y; the noble-gas inventories pass through (node '
      'internals row); CRYO_ASU is the tier 1 relief destination',
      f'Graph revision {REV} is the model authority for this build; STEP (export/cryo_asu.step) '
      'is the solids of record',
      'The build leaves the M0 study registry box on x and y: misfit reported on the tracker '
      'board, nothing resized'],
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
# No wall clock: the build-log Date is the inputs' own state date (lib/stamp_date
# policy); cryo_asu.py has already put models/mfg on sys.path for the shared lib.
import sys as _sys
if str(HERE.parent) not in _sys.path:
    _sys.path.insert(0, str(HERE.parent))
from lib.stamp_date import deterministic_date  # noqa: E402
for sid, shape, pdir, notes, _title in SHEETS:
    svg = DRAW / f"{sid}.svg"
    if svg.exists() and "aqs-title-block" in svg.read_text():   # stamped: geometry frozen, PDF pass only
        try:
            import cairosvg
            import sys as _aqs_sys
            import pathlib as _aqs_pl
            _aqs_sys.path.insert(0, str(_aqs_pl.Path(__file__).resolve().parent.parent))   # models/mfg, for lib
            from lib.pdf_write import write_pdf
            write_pdf(str(svg), str(DRAW / f"{sid}.pdf"))
            pdf = "pdf+svg current"
        except Exception as e:
            pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
        continue
    cq.exporters.export(shape.val(), str(svg), opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
    add_notes(svg, notes)

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/CRYO_ASU/export/cryo_asu.step`"
srcs = ["models/mfg/CRYO_ASU/cryo_asu.py", "models/mfg/CRYO_ASU/draw_cryo_asu.py", step_src,
        "models/mfg/CRYO_ASU/bom.csv", "models/mfg/CRYO_ASU/fasteners.csv",
        "models/mfg/CRYO_ASU/check.json", "models/mfg/CRYO_ASU/WORK_ORDER.md"]
log = f"""# Build log - CRYO_ASU

Date: {deterministic_date()}. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_ASU.md`; bed design from the node design block).
Run note (2026-11-05): rebuild against the Rev AD graph node. The builder now reads the graph node through `models/mfg/lib/graph_node.py`; the N17 power-terminal cable row (cable schedule X-ELS-06) is carried verbatim, not drawn; bed sizing follows the node design block (bed_D_mm 421.9, bed_L_mm 1265.8, sorbent 115.04 kg/bed), which grows the beds, shifts the bed axes one pitch and grows the sorbent charge; the M0 registry-box misfit hold is unchanged. Supersedes the 2026-11-01 run at Rev AC sizing.

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/CRYO_ASU/cryo_asu.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm against the node size_mm {R['size_mm']}: the node box is the M0 study registry envelope (params size_note) and the beds at their design diameter cannot fit it - misfit reported on the tracker board, nothing resized (AQS-PLAN-006 rule 3)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/CRYO_ASU.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} schedule rows of `docs-authority/nozzles/CRYO_ASU.csv` accounted for - {N_PIPE} drawn at face, height, bore and tag, and N17 the power terminal (cable schedule X-ELS-06, AQS-ELEC-010) carried verbatim, not drawn (electrical, not piped); vent to the 2000 datum; frame-level z 160 rows through the plinth
- A-COL: the 13X charges are solids between support grids ({R['sorbent']['kg_drawn_total']:g} kg drawn against {R['sorbent']['kg_booked_total']:g} kg booked); distributor and demister are not named on the node (hold, WORK_ORDER W12)
- BOM `models/mfg/CRYO_ASU/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_ASU/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL with the reported envelope misfit; the machine-design detail (TSA valve row, interconnect piping) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
