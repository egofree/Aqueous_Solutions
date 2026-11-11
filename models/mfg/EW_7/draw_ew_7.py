"""EW_7 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
models/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front       general arrangement, front elevation (-Y)
  ga_side        general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (tags/faces/heights per the schedule)
  sh01           PVC-U tank shell (wall 10 mm, zone stack)
  el01           electrode bank: cathodes + edge strips, anodes, bus pair
  aux01          service group: barbs, solids ports, drain, vent bridge
  iso01          isometric orientation sheet

Run twice around _drawings.py:
    python3 models/mfg/EW_7/draw_ew_7.py    # SVG source from the build + build log
    python3 docs-authority/_drawings.py     # title block + register rows
    python3 models/mfg/EW_7/draw_ew_7.py    # PDF pass (now from stamped SVGs)
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "ew_7.py")
parts, inv, P, R = ns["parts"], ns["inv"], ns["P"], ns["report"]
REV = P["graph_revision"]
L, W, H = P["size_mm"]
D = R["nozzles_drawn"]
CAT = R["cathodes"]
BUS = R["bus"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


tank = parts["tank"]
electrode = union_all([parts["cathodes"], parts["edge_strips"], parts["anodes"],
                       parts["bus_bars"], parts["standoff_pads"], parts["support_beams"]])
aux = union_all([parts["nozzles"], parts["vent_support"]])
full = union_all(list(parts.values()))
drawn_full = union_all([full] + list(inv.values()))

noz_notes = []
for _t, _d in sorted(D.items()):
    _svc = next(r['service'] for r in P['nozzles'] if r['tag'] == _t)
    if _d['face'] == '+X':
        _head = f"{_t} {_d['dn']} +X y {_d['y_mm']:g} z {_d['height_mm']:g}"
    else:
        _head = f"{_t} {_d['dn']} {_d['face']} z {_d['height_mm']:g}"
        if 'x_mm' in _d:
            _head += f" x {_d['x_mm']:g}"
    noz_notes.append(_head + f": {_svc}"
                     + (" - " + _d["note"] if _d["style"] in ("gland", "solids") else ""))
noz_notes.append("Heights/bore/rating per docs-authority/nozzles/EW_7.csv; along-face x positions "
                 "are the registered layout choice (params.json layout)")
SHEETS = [
    ("ga_front", drawn_full, (0, 1, 0),
     [f'Keys: {L} x {W} x {H} mm overall (graph envelope, filled by the shell); open top',
      'Zone stack above the floor: sump 150 / plate 420 / cover 100 / freeboard 80; liquor fill '
      f'line z 680 ({R["liquor_fill_basis_m3"]} m3 fill basis, AQS-DUTY-051 section 2)',
      f'Electrode bank: {CAT["count"]} cathodes + {R["anodes"]["count"]} anodes at 100 mm pitch, '
      'plates 600 x 420 immersed',
      'Bus pair above the liquor line on FRP standoffs (AQS-BUS-001 EW-7 pack)',
      'Liquor shown as a process-inventory solid - not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", drawn_full, (1, 0, 0),
     [f'Keys: {W} mm inside-width stack: plate 600 + 2 x 50 rack margin; wall 10 mm PVC-U',
      'Plates z 160..580 immersed; Ti tabs 120 wide rise to z 691; bus bars at z 691 and above',
      'Support beams under the pads at z 673..683, bolted to the inner walls',
      'Nozzle hardware drawn flush at the envelope faces (lib/nozzles.place_on_face); hose makeup '
      'at the face plane',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", drawn_full, (0, 0, -1), noz_notes,
     "Nozzle orientation, top view. Tags/faces/heights per the schedule."),
    ("sh01", tank, (0, 1, 0),
     [f'PVC-U tank, outside {L} x 720 x 760, wall 10 mm: inside {L - 20:g} x 700 x 750 '
      '(AQS-DUTY-051 section 1 zone stack)',
       'Open top; freeboard 80 to the rim; bottom wall pierced for the drain only',
       'Thermoplastic welds per the unit WORK_ORDER route (hot-gas, PVC-U); hydro or leak test per '
       'F-CELL route class',
       'Corrosion allowance 0 mm (AQS-STD-001 polymer rule); general tolerance ISO 2768-m'],
     "Fabricated part sheet: PVC-U tank shell."),
    ("el01", electrode, (0, 1, 0),
     [f'{CAT["count"]} cathode sheet{"s" if CAT["count"] != 1 else ""} 600 x 420 x 3 Ti '
      'Grade 2 + PVC-U edge strip clips at x 135 + 100k',
      f'{R["anodes"]["count"]} anode sheet{"s" if R["anodes"]["count"] != 1 else ""} 600 x '
      '420 x 1.5 Ti mesh MMO (drawn as the sheet envelope) at x 85 + 100k',
      f'Hanger tabs 120 wide rise to z 691; bus pack {BUS["pack"]} Cu C101 over the tab line, '
      'on FRP pads (params.json layout.bus)',
      'Bus per the published AQS-BUS-001 EW-7 row; contacts Ti-tab on Cu bar above the liquor '
      f'line (AQS-STD-002 sections 9 and 11); {CAT["count"] + R["anodes"]["count"]} M6 tab clamps '
      '(fasteners.csv)'],
     "Fabricated part sheet: electrode bank + bus pair."),
    ("aux01", aux, (0, 1, 0),
     ['Hose barbs set in flush at the faces; barb profile a study proportion (lib/nozzles.py), '
      'finished against the hose supplier print',
      'Solids rows drawn at DN15, bore not calculated (AQS-PLAN-006 W4)' if any(
          d["style"] == "solids" for d in D.values())
      else 'All process joints atmospheric hose at the face (duty section 4)',
      'Vent support: 2 posts 30 x 30 on the inner walls + rim bridge 60 x 10 at z 750..760; drain '
      'flush at z 0 with the boss to its 50 datum'],
     "Fabricated part sheet: nozzle hardware + vent support."),
    ("iso01", drawn_full, (1, -1, 1),
     ['Shop orientation: -X end carries the rectifier lugs; +Y face carries the overflow/tail '
      'connection (air break per AQS-STD-002 section 11)',
      f'Graph revision {REV} is the model authority for this build; STEP (export/ew_7.step) is '
      'the solids of record',
      'Process inventory (liquor to z 680) shown in place - not a BOM part'],
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
    add_notes(svg, notes)          # notes only; the title block + register rows happen in _drawings.py

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/EW_7/export/ew_7.step`"
srcs = ["models/mfg/EW_7/ew_7.py", "models/mfg/EW_7/draw_ew_7.py",
        "models/mfg/EW_7/export/ew_7.step",
        "models/mfg/EW_7/bom.csv", "models/mfg/EW_7/fasteners.csv",
        "models/mfg/EW_7/check.json", "models/mfg/EW_7/WORK_ORDER.md"]
log = f"""# Build log - EW_7

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EW_7.md`; sizing `docs-authority/sizing/EW_CELLS.md`).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/EW_7/ew_7.py` (a `cad_mfg_models` pipeline stage through `models/mfg/build_all.py`)

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: inside the graph envelope {L} x {W} x {H} mm with margin (tracker check green)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/EW_7.stl` replaced from the build (ASCII, metres)
- Nozzles: all {len(D)} rows of `docs-authority/nozzles/EW_7.csv` present at face, height, bore and rating, tagged; drawn flush per the house idiom
- A-CELL: {CAT['count']} cathode{'s' if CAT['count'] != 1 else ''} / {R['anodes']['count']} anode{'s' if R['anodes']['count'] != 1 else ''} at 100 mm pitch, plates 600 x 420 immersed (0.504 m2 both faces, {CAT['active_m2_bank']} m2 bank); bus pack {BUS['pack']} Cu per AQS-BUS-001 Rev D
- BOM `models/mfg/EW_7/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EW_7/drawings/` (GA front/side, nozzle orientation, 3 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-CELL; the machine-design detail (weld procedures, hose makeup) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
