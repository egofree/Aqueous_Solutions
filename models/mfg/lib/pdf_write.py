# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Byte-stable PDF pass for the drawing sets (AQS-PLAN-006 W7; F-20261110-12).

cairo stamps every PDF it writes with the wall-clock time in /CreationDate, so two
builds of the same sheet differed in bytes with identical text, and the committed
PDFs could not be gated. write_pdf renders the stamped SVG through cairosvg with the
creation date fixed to lib/stamp_date.py's inputs date and the document identifier
fixed to the sheet id, so the same source renders byte-identical bytes on any day.

    from lib.pdf_write import write_pdf
    write_pdf(svg_path, pdf_path)     # raises what cairosvg raises (callers report 'pdf skipped')
"""
import pathlib

_installed = False
_pending = {"date": None, "title": None}


def _install():
    """Patch the cairo PDF surface once per process: fixed creation date and title."""
    global _installed
    if _installed:
        return
    import cairocffi

    original = cairocffi.PDFSurface.__init__

    def patched(surface, target, width, height):
        original(surface, target, width, height)
        surface.set_metadata(cairocffi.PDF_METADATA_CREATE_DATE, _pending["date"])
        surface.set_metadata(cairocffi.PDF_METADATA_TITLE, _pending["title"])

    cairocffi.PDFSurface.__init__ = patched
    _installed = True


def write_pdf(svg, pdf, date=None):
    """Render `svg` to `pdf` with the fixed stamp date and the sheet id as title."""
    import cairosvg
    from lib.stamp_date import deterministic_date

    _pending["date"] = date or deterministic_date() + "T00:00:00Z"
    _pending["title"] = pathlib.Path(str(pdf)).stem
    _install()
    cairosvg.svg2pdf(url=str(svg), write_to=str(pdf))
