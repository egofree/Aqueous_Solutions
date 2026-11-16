# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Byte-stable FCStd zip writing for the FreeCAD generators.

A .FCStd is a zip container. FreeCAD stamps every entry with the wall-clock
save time, and Python zipfile.writestr stamps fresh entries with the wall
clock too, so the same document saved by two regen passes carried different
bytes and the CAD doc stage never converged (site regeneration, 2026-11-15).
FreeCAD also records the save time inside Document.xml as LastModifiedDate
and the OS user as LastModifiedBy, both wall-clock/user dependent.

write_entries carries the whole rewrite instead, mirroring the manufacturing
lane's byte-stable STEP export (models/mfg/lib/step_export.py): every entry is
stamped with the deterministic stamp date from models/mfg/lib/stamp_date.py
(the plant graph's own date field, never the wall clock), and Document.xml has
its LastModifiedDate/LastModifiedBy values normalised to that stamp. The same
document content therefore writes identical bytes in any pass, on any day, by
any user. View content itself (Document.xml shapes, GuiDocument.xml view
providers) is produced by the generators and the patchers, not here.
"""
import re, sys, zipfile
from pathlib import Path

_MFG = str(Path(__file__).resolve().parent.parent / 'mfg')
if _MFG not in sys.path:
    sys.path.insert(0, _MFG)
try:
    from lib.stamp_date import deterministic_date
except Exception:                                            # pragma: no cover
    deterministic_date = None

_LAST_MODIFIED_DATE = re.compile(
    r'(<Property name="LastModifiedDate"[^>]*>\s*<String value=")[^"]*(")')
_LAST_MODIFIED_BY = re.compile(
    r'(<Property name="LastModifiedBy"[^>]*>\s*<String value=")[^"]*(")')

# FreeCAD 1.0 gives every freshly built TopoShape a random per-process Tag and
# embeds it in the subshape element-map keys (the `D<hex>` / `H<hex>` tokens of
# the per-shape *.Shape.Map.txt entries). The same build therefore wrote
# different map bytes every pass. The tokens are opaque key components: on load
# FreeCAD re-derives the keys, so renumbering them consistently preserves the
# map. The rewrite maps each distinct tag value to its first-appearance index,
# a deterministic function of the file content.
_SHAPE_MAP_TAG = re.compile(rb'(?<=[;:])([DH])([0-9a-f]{2,})')


def canonicalize_shape_map(data):
    """Renumber the random shape Tags inside a *.Shape.Map.txt entry deterministically."""
    seen = {}

    def repl(m):
        pfx, tag = m.group(1), m.group(2)
        if tag not in seen:
            seen[tag] = b'%x' % (len(seen) + 1)
        return pfx + seen[tag]

    return _SHAPE_MAP_TAG.sub(repl, data)


def det_date():
    """The deterministic zip stamp: (y, m, d, 0, 0, 0) from stamp_date, clamped to the
    DOS date range a zip container can hold (1980+; the 1970 fallback becomes 1980)."""
    day = deterministic_date() if deterministic_date else ''
    try:
        y, m, d = (int(x) for x in day.split('-'))
    except Exception:
        y, m, d = 1980, 1, 1
    if y < 1980:
        y, m, d = 1980, 1, 1
    return (y, m, d, 0, 0, 0)


def scrub_document_xml(data):
    """Normalise the wall-clock / user properties FreeCAD records inside Document.xml."""
    y, m, d, _, _, _ = det_date()
    stamp = '%04d-%02d-%02dT00:00:00Z' % (y, m, d)
    txt = data.decode('utf-8', errors='replace')
    txt = _LAST_MODIFIED_DATE.sub(lambda mo: mo.group(1) + stamp + mo.group(2), txt, count=1)
    txt = _LAST_MODIFIED_BY.sub(lambda mo: mo.group(1) + mo.group(2), txt, count=1)
    return txt.encode('utf-8')


def write_entries(path, entries):
    """Rewrite the FCStd at `path` with `entries` (a (name, bytes) list in zip order),
    every entry stamped with det_date(); Document.xml is scrubbed on the way through
    and *.Shape.Map.txt entries have their random shape Tags renumbered."""
    tmp = Path(path).with_suffix('.fcstd.tmp')
    with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries:
            zi = zipfile.ZipInfo(name, date_time=det_date())
            zi.compress_type = zipfile.ZIP_DEFLATED
            if name == 'Document.xml':
                data = scrub_document_xml(data)
            elif name.endswith('.Shape.Map.txt'):
                data = canonicalize_shape_map(data)
            zout.writestr(zi, data)
    tmp.replace(path)
