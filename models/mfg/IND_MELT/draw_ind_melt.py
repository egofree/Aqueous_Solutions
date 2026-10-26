"""IND_MELT drawing set (AQS-PLAN-006 W7): SVG/PDF sheets from the accepted build.

The SVGs are exported here as drawing content only; the AQS-DWG-001 title block
(content-hash revision per ISO_7200/ASME_Y14_35) and the DRAWING_REGISTER.md rows
are applied by docs-authority/_drawings.py (AQS-DWG-002), which stamps every
model/mfg/*/drawings/*.svg. Geometry and notes:

  ga_front     general arrangement, front elevation (-Y): furnace, coil zone, hood
  ga_side      general arrangement, side elevation (-X)
  nozzle_orient  nozzle orientation, top view (faces per the task-04 schedule)
  sh01         casing + lining + head plate (weld + tolerance notes)
  hd01         top group: hood plate, N17 vent riser, melt stubs, coil leads
  el01         melt zone: induction coil, crucible, pedestal, tilt cradle
  aux01        service group: charge chute, pour lip, slag spout, trunnions, drain
  iso01        isometric orientation sheet

Run twice around _drawings.py:
    <cq python> draw_ind_melt.py          # SVG source from the build
    python3 docs-authority/_drawings.py   # title block + register rows
    <cq python> draw_ind_melt.py          # PDF pass (now from stamped SVGs)
"""
import json, pathlib, re
import cadquery as cq

HERE = pathlib.Path(__file__).parent
ns = __import__("runpy").run_path(HERE / "ind_melt.py")
parts, inv, P = ns["parts"], ns["inv"], ns["P"]
REV = P["graph_revision"]
DRAW = HERE / "drawings"; DRAW.mkdir(exist_ok=True)

def union_all(shapes):
    u = None
    for s in shapes:
        u = s if u is None else u.union(s)
    return u

shell = union_all([parts[k] for k in ("casing", "fibre_lining", "hood")])
hood = union_all([parts[k] for k in ("vent_stub", "melt_stubs", "coil_leads")])
electrode = union_all([parts[k] for k in ("induction_coil", "crucible", "crucible_pedestal", "tilt_frame")])
aux = union_all([parts[k] for k in ("charge_chute", "pour_spout", "slag_spout", "trunnion_pins", "drain_well")])
full = union_all(list(parts.values()) + list(inv.values()))

SHEETS = [
    ("ga_front", union_all([shell, hood, electrode, aux]), (0, 1, 0),
     ['Keys: 1000 x 1000 casing, 1500 overall height; CS t4 casing with the t150 ceramic-fibre hot face',
      'Crucible D110 x 165 on its pedestal at (480,500); 12-turn induction coil z 320..800; hood z 850..880',
      'N1/N8/N13/N14 melt DN15 stubs +Y z 600; N9 slag spout +X z 600; N2..N7/N10..N12/N15 charge rows land on the -X chute at z 160',
      'N16 drain bottom (500,500) flush at z 0; N17 vent on the hood up to the z 800 datum',
      'Melt inventory drawn as a solid - process inventory, not a BOM part'],
     "General arrangement, front elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("ga_side", union_all([shell, hood, electrode, aux]), (1, 0, 0),
     ['Keys: tilt pour about the trunnion axis at z 500 (pins -X/+X); cradle under the shell band 470..530',
      'Lining package: casing t4 + ceramic-fibre hot face t150 (design lining row)',
      'Coil leads exit +X at z 360 to the medium-frequency supply (25 kW connected)',
      'General tolerance ISO 2768-m unless noted'],
     "General arrangement, side elevation. Shop, not stamped (AQS-STD-001 section 7)."),
    ("nozzle_orient", full, (0, 0, -1),
     ['N1/N8/N13/N14 melt DN15 stubs +Y z 600: pour lip sample, continuous caster, atomizer, investment pour',
      'N9 slag return +X z 600 (solids, bore not calculated)',
      'N2..N7/N10..N12/N15 charge rows -X z 160: the ten charge rows land on the common chute',
      'N16 drain bottom (500,500) flush at z 0; N17 vent on the hood at z 800',
      'Heights/bore/rating per docs-authority/nozzles/IND_MELT.csv; compass faces are the registered layout choice (params.json layout_note)'],
     "Nozzle orientation, top view. Heights per the task-04 schedule."),
    ("sh01", shell, (0, 1, 0),
     ['Casing CS t4: 6 mm fillet welds (ISO 2553 a6) along wall/wall and wall/roof seams',
      'Hot face t150 ceramic-fibre board, butted and stacked; chute throat recess as drawn',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: casing + hot face. Welds per ISO 2553; general tolerance ISO 2768-m."),
    ("hd01", hood, (0, 1, 0),
     ['Hood plate with the N17 vent pass; DN15 melt stubs +Y z 600 on the casing',
      'Coil leads +X z 360 through the casing pass; gasket faces per AQS-PIP-003 practice (AQS-STD-002 section 14)',
      'General tolerance ISO 2768-m unless noted'],
     "Fabricated part sheet: top group (hood, vent, melt stubs, coil leads)."),
    ("el01", electrode, (0, 1, 0),
     ['12-turn induction coil, Cu tube OD 20 t 2.5, z 320..800 around the crucible zone',
      'Crucible D110 x 165 graphite on its pedestal; tilt cradle under the shell band',
      'Coil water flow interlocked with the lid position (WO step 5); general tolerance ISO 2768-m'],
     "Fabricated part sheet: melt zone (coil, crucible, pedestal, cradle)."),
    ("aux01", aux, (0, 1, 0),
     ['Charge chute -X z 160: the ten charge rows land here (A-M-284 feedstock ruling)',
      'Tilt-pour lip +X z 600 and N9 slag-return spout; trunnion pins -X/+X at z 500',
      'N16 drain sump OD 60, DN15 bore, flush at z 0 (frozen-metal drain pig)',
      'General tolerance ISO 2768-m'],
     "Fabricated part sheet: service group (chute, pour, slag, trunnions, drain)."),
    ("iso01", full, (1, -1, 1),
     ['Shop orientation: +X face, y along depth, z up; coil, crucible and tilt gear in the lined furnace',
      'Graph revision AC is the model authority for this build; STEP (export/ind_melt.step) is the solids of record',
      'Melt inventory shown in place - not a BOM part'],
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
    if not svg.exists():
        pass   # fresh write below
    elif "aqs-title-block" in svg.read_text():   # already stamped by _drawings.py: geometry frozen, PDF pass only
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
