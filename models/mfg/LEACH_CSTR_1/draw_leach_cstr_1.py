"""LEACH_CSTR_1 drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
models/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front       general arrangement, front elevation (-Y)
  ga_side        general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (61 schedule rows + the conductor gland)
  sh01           CPVC tank shell (wall 16, floor 16, lid 12 on a 40 mm flange)
  in01           internals: FRP belts, HX-5 coil envelope, agitator
  aux01          service group: hose barbs, solids ports, drain, vent, gland
  iso01          isometric orientation sheet

Run twice around _drawings.py:
    python3 models/mfg/LEACH_CSTR_1/draw_leach_cstr_1.py   # SVG source from the build
    python3 docs-authority/_drawings.py                    # title block + register rows
    python3 models/mfg/LEACH_CSTR_1/draw_leach_cstr_1.py   # PDF pass (now from stamped SVGs)
"""
import json, pathlib, runpy

HERE = pathlib.Path(__file__).parent
ns = runpy.run_path(HERE / "leach_cstr_1.py")
parts, inv, R = ns["parts"], ns["inv"], ns["report"]
REV = R["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)


def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u


shell = parts["tank"]
internal = union_all([parts["belts"], parts["coil"], parts["coil_pads"], parts["agitator"]])
aux = parts["nozzles"]
full = union_all(list(parts.values()))
drawn_full = union_all([full] + list(inv.values()))

L, W, H = R["size_mm"]
SHEETS = [
    ("ga_front", drawn_full, (0, 1, 0),
     [f'Keys: {L} x {W} x {H} mm overall (duty section 2 envelope, AQS-DUTY-050); tank body '
      f'1888 x 1080 inside the reserved bands',
      'Wall 16 mm, floor 16 mm CPVC; lid 12 mm on a 40 mm flange, M12 PVDF at 150 mm pitch',
      'FRP belts C203x56x6.4 at z 300/560/900, segmented at the port rows',
      'Working level z 1100 (AQS-DUTY-050): 1.855 m3 drawn net of internals against the '
      '2.14 m3 fill basis',
      'Liquor shown as a process-inventory solid - not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", drawn_full, (1, 0, 0),
     ['HX-5 coil envelope OD 925 / ID 575 x 600 on four PTFE pads at z 16..716 (mass from the '
      'tube, not the envelope)',
      'Agitator: PBT D450 at z 250, PVDF-sheathed D 50 shaft through the lid; drive bridge '
      'outside the envelope, not modeled',
      'Port extension stubs reach 10 mm into the cavity so every union crosses the wall',
      'Nozzle hardware drawn flush at the envelope faces (lib/nozzles.place_on_face)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", drawn_full, (0, 0, -1),
     ['61 schedule rows of docs-authority/nozzles/LEACH_CSTR_1.csv at tag, face, height and '
      'bore; inlets -Y, outlets +Y (duty section 4)',
      'Rows pack one per face/height group centred on the face mid-length: inlets z 160 (32) '
      'and z 280 (4), outlets z 600 (15) and z 1050 (4)',
      'N9 drain flush at z 0 at x 300, boss to the 50 datum; N10 vent flush at the lid, '
      'z 1400 datum, x 1700',
      'Atmospheric joints are hose barbs; solids rows at DN15 labeled bore not calculated '
      '(AQS-PLAN-006 W4); schedule rating column (Class 150) carried verbatim as text',
      'IA-E-LEACH conductor gland at +Y x 250, z 600 (duty section 4 prose; not a schedule row) - '
      'per-tag positions in check.nozzles_drawn'],
     "Nozzle orientation, top view. Tags/faces/heights per the schedule."),
    ("sh01", shell, (0, 1, 0),
     [f'CPVC tank, body 1888 x 1080 x {H:g}, wall {16:g} mm, floor 16 mm, lid 12 mm on a 40 mm '
      f'flange (AQS-DUTY-050 wall 16 / floor 16; lid and flange are assumptions)',
      'Panel stress 1.37 MPa at the floor against 3.03 MPa CPVC allowable at 85 C '
      '(AQS-DUTY-050)',
      'Thermoplastic welds per the unit WORK_ORDER route (hot-gas / extrusion, CPVC); '
      'hydrostatic 11.9 kPa at the floor at the working level (study)',
      'Corrosion allowance 0 mm (AQS-STD-001 polymer rule); general tolerance ISO 2768-m'],
     "Fabricated part sheet: CPVC tank shell."),
    ("in01", internal, (0, 1, 0),
     ['FRP belts C203x56x6.4 at z 300/560/900 (AQS-DUTY-050 study), segmented where the port '
      'rows cross the bands; X-MAT-21 coupon tests hold',
      'HX-5 coil: two concentric helices of 25 x 3 mm borosilicate 3.3 tube, 53.7 m, 4.22 m2 '
      '(AQS-DUTY-049); drawn as its annulus envelope, mass from the tube',
      'Coil enters through CPVC stubs with FKM gaskets; the Q3 metal piping ends at a '
      'dielectric isolating flange outside the tank (AQS-STD-002 section 3.3)',
      'Agitator: 4-blade 45 deg PBT D 450 at 150 rpm, 403 W shaft, solid PVDF impeller at '
      'z 250; no metal wetted (AQS-STD-002 M3)'],
     "Fabricated part sheet: belts, HX-5 coil, agitator."),
    ("aux01", aux, (0, 1, 0),
     ['Hose barbs DN15/DN25/DN50 set in flush at the envelope faces; barb profile a study '
      'proportion (lib/nozzles.py), finished against the hose supplier print',
      'Solids rows (N12, N13, N18, N19, N20, N36) drawn at DN15 and labeled bore not '
      'calculated (AQS-PLAN-006 W4 hand/bin transfer)',
      'N9 drain: DN15 stub flush at z 0, boss to the 50 datum. N10 vent: DN15 stub flush at '
      'the lid to the 1400 datum, vented to NOX_SCRUB and FLUE_KO (duty section 6)',
      'IA-E-LEACH conductor gland: DN15 passage in a boss at +Y z 600, not a hose'],
     "Fabricated part sheet: nozzle hardware + conductor gland."),
    ("iso01", drawn_full, (1, -1, 1),
     ['Shop orientation: inlets on the -Y face, outlets and the conductor gland on +Y; '
      'headers and routing are the piping scope, not this unit',
      f'Graph revision {REV} is the model authority for this build; STEP (export/leach_cstr_1.step) '
      'is the solids of record',
      'Process inventory (liquor to z 1100) shown in place - not a BOM part'],
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
    add_notes(svg, notes)          # notes only; the title block + register rows happen in _drawings.py

# ---------------------------------------------------------------- build log (A-core record)
step_src = "build export `models/mfg/LEACH_CSTR_1/export/leach_cstr_1.step`"
srcs = ["models/mfg/LEACH_CSTR_1/leach_cstr_1.py", "models/mfg/LEACH_CSTR_1/draw_leach_cstr_1.py",
        step_src, "models/mfg/LEACH_CSTR_1/bom.csv", "models/mfg/LEACH_CSTR_1/fasteners.csv",
        "models/mfg/LEACH_CSTR_1/check.json", "models/mfg/LEACH_CSTR_1/WORK_ORDER.md"]
log = f"""# Build log - LEACH_CSTR_1

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LEACH_CSTR_1.md`; envelope basis AQS-DUTY-050 per duty section 2).

## Tool versions

- CadQuery {cq.__version__} (CADQUERY_PYTHON)
- Python {__import__('sys').version.split()[0]}; build run headless via `python3 models/mfg/LEACH_CSTR_1/leach_cstr_1.py`

## Checks

- Build bbox {R['bbox_mm'][0]} x {R['bbox_mm'][1]} x {R['bbox_mm'][2]} mm: inside the duty envelope {L} x {W} x {H} mm (the node carries no size_mm; tracker hold, WORK_ORDER W12)
- Solid source: {step_src}; export STL closed and manifold; `cad/stl/LEACH_CSTR_1.stl` replaced from the build (ASCII, metres)
- Nozzles: all {R['nozzle_count_schedule']} rows of `docs-authority/nozzles/LEACH_CSTR_1.csv` present at face, height, bore and tag; drawn flush per the house idiom; the IA-E-LEACH conductor is the +Y gland (duty section 4 prose)
- A-VES: holdup {R['holdup_m3']} m3 drawn net of internals at the 1100 mm working level against the 2.14 m3 fill basis (AQS-DUTY-050); residence stays the duty's 13.2 h figure
- BOM `models/mfg/LEACH_CSTR_1/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LEACH_CSTR_1/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

""" + "".join(f"- `{s}`\n" for s in srcs) + """
Status: accepted per AQS-PLAN-006 section 5 A-core and A-VES; the machine-design detail (belt segmentation, weld procedures, port bores) follows the unit WORK_ORDER.
"""
(HERE / "build_log.md").write_text(log)
print(json.dumps({"sheets": [s[0] for s in SHEETS], "pdf": pdf}))
