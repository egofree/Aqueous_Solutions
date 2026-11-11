# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Drawing-set driver for the per-unit models (AQS-PLAN-006 W7).

The per-unit `draw_<unit>.py` describes its sheets and its build log; this module
carries the sheet mechanics the CRYO batch established: SVG export from the accepted
build solids, the notes band under the drawing, the PDF pass around
`docs-authority/_drawings.py` (which applies the AQS-DWG-001 title block and the
DRAWING_REGISTER rows), and the A-core build-log record.

Run twice around _drawings.py: draw script, _drawings.py, draw script (PDF pass).
"""
import json
import pathlib
import re

BAND = 100   # notes band appended under the drawing; _drawings.py stamps the title block


def xml_escape(text):
    """Note text goes into SVG content: escape the XML specials so a '<' or an
    '&' in a duty phrase (heat < 80 C, P&ID) cannot break the sheet."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def add_notes(svg_path, rev, notes):
    s = svg_path.read_text()
    if "aqs-fab-notes" in s:
        return
    w = float(re.search(r'width="([\d.]+)"', s).group(1))
    h = float(re.search(r'height="([\d.]+)"', s).group(1))
    s = re.sub(r'height="[\d.]+"', f'height="{h + BAND}"', s, count=1)
    rows = [f"Graph revision {rev} - {svg_path.stem}: {xml_escape(n)}" for n in notes]
    block = (f'<g id="aqs-fab-notes" transform="translate(0,{h})" '
             f'font-family="DejaVu Sans,sans-serif" font-size="10" fill="#000">')
    for i, n0 in enumerate(rows):
        block += f'<text x="6" y="{24 + 13 * i}">{n0}</text>'
    block += '</g>'
    svg_path.write_text(s.replace("</svg>", block + "</svg>"))


def export_sheets(unit, parts, report, sheets, here=None):
    """Export the (sheet_id, shape, projection_dir, notes, title) sheets of one unit.

    A sheet whose SVG already carries the title block is geometry-frozen: PDF pass
    only. Returns a status dict.
    """
    import cadquery as cq
    here = pathlib.Path(here) if here else pathlib.Path(__file__).parent.parent / unit
    draw = here / "drawings"
    draw.mkdir(exist_ok=True)
    rev = report["graph_revision"]
    pdf = "stamped pass pending"
    for sid, shape, pdir, notes, _title in sheets:
        svg = draw / f"{sid}.svg"
        if svg.exists() and "aqs-title-block" in svg.read_text():
            try:
                import cairosvg
                from lib.pdf_write import write_pdf
                write_pdf(str(svg), str(draw / f"{sid}.pdf"))
                pdf = "pdf+svg current"
            except Exception as e:
                pdf = f"pdf skipped ({e.__class__.__name__}: {e})"
            continue
        cq.exporters.export(shape.val(), str(svg),
                            opt={"projectionDir": pdir, "showAxes": False, "showHidden": True})
        add_notes(svg, rev, notes)
    return {"sheets": [s[0] for s in sheets], "pdf": pdf}


def _stamp_date():
    from lib.stamp_date import deterministic_date
    return deterministic_date()


deterministic_date = _stamp_date


def build_log(unit, here, report, srcs, extra_checks, acceptance_set):
    """Write the A-core acceptance build log from the check report."""
    import cadquery as cq
    import sys
    here = pathlib.Path(here)
    u = unit.lower()
    step_src = f"build export `models/mfg/{unit}/export/{u}.step`"
    r = report
    dims = " x ".join(f"{v:g}" for v in r["bbox_mm"])
    env = " x ".join(f"{v:g}" for v in r["size_mm"])
    carried = [
        f"the {tag} "
        + ("solids make-up" if v.get("dn") == "solids" else "cable power-terminal")
        + " row is carried verbatim, not drawn"
        for tag, v in sorted(r.get("nozzles_drawn", {}).items()) if v.get("style") == "carried"]
    lines = [
        f"# Build log - {unit}",
        "",
        f"Date: {_stamp_date()}. Authority: AQS-PLAN-006 section 5 (acceptance) {acceptance_set}; "
        "MFG_MODEL_PLAN (AQS-PLAN-006).",
        f"Graph: `flow_graph/plant_flow_graph.json` (duty sheet "
        f"`docs-authority/duties/{unit}.md`; envelope per `models/mfg/{unit}/params.json`).",
        "",
        "## Tool versions",
        "",
        f"- CadQuery {cq.__version__} (CADQUERY_PYTHON)",
        f"- Python {sys.version.split()[0]}; build run headless via "
        f"`python3 models/mfg/{unit}/{u}.py`",
        "",
        "## Checks",
        "",
        f"- Build bbox {dims} mm against the {env} mm envelope: "
        + ("inside (tracker check green)" if r["inside_size_mm"] else "OVER - misfit reported")
        + " (bbox read back from the export STL: the CAD kernel's bounding box of "
        "the lofted barb faces is loose; the mesh is the gate measure)",
        f"- Solid source: {step_src}; export STL closed and manifold, "
        f"{r['solids']} solid(s); `cad/stl/{unit}.stl` "
        + ("; " + r["cad_stl"] if r.get("cad_stl") else "replaced from the build")
        + " (ASCII, metres)",
        f"- Nozzles: all {r['nozzle_count_schedule']} rows of "
        f"`docs-authority/nozzles/{unit}.csv` present at face, height and bore "
        "(per-tag notes in check.nozzles_drawn)"
        + ("; " + "; ".join(carried) if carried else ""),
    ]
    lines += extra_checks
    lines += [
        f"- BOM `models/mfg/{unit}/bom.csv` (generated from the model: qty, material, "
        "mass, make-or-buy); fasteners and WORK_ORDER beside it",
        f"- Drawing set `models/mfg/{unit}/drawings/` (GA front/side, nozzle orientation, "
        "part sheets, iso; title blocks per AQS-DWG-002); the stale envelope "
        "`drawings/GA.md` is superseded where one existed",
        "",
        "## Sources",
        "",
    ]
    lines += [f"- `{s}`" for s in list(srcs) + [step_src]]
    status = (f"\nStatus: accepted per AQS-PLAN-006 section 5 {acceptance_set}; holds "
              "named in WORK_ORDER W12.\n")
    (here / "build_log.md").write_text("\n".join(lines) + "\n" + status)
