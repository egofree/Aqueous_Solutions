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
lane's byte-stable STEP export (models/mfg/lib/step_export.py):

  - every entry kept is stamped with the deterministic stamp date from
    models/mfg/lib/stamp_date.py (the plant graph's own date field, never
    the wall clock),
  - Document.xml has its LastModifiedDate/LastModifiedBy values normalised
    to that stamp,
  - the per-shape *.Shape.Map.txt element-map sidecars are dropped. FreeCAD
    writes the same logical map in a different entry order — and renumbers
    the :1.b.<n> child names to match — on every run (FB_HAB_CORE, the FR_*
    imported units, PK_1 and 11 more oscillated across the 2026-11-15
    instrumented passes). The sidecars are derived data: SaveElementMaps
    saves them as a cache and a loader re-derives the map from the BRep
    when they are absent, so dropping them loses nothing and stabilises
    the file.

The same document content therefore writes identical bytes in any pass, on
any day, by any user. View content itself (Document.xml shapes,
GuiDocument.xml view providers) is produced by the generators and the
patchers, not here.
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
    and the *.Shape.Map.txt element-map sidecars are dropped (loaders re-derive them)."""
    tmp = Path(path).with_suffix('.fcstd.tmp')
    with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries:
            if name.endswith('.Shape.Map.txt'):
                continue                                     # derived data; a loader re-derives the map
            zi = zipfile.ZipInfo(name, date_time=det_date())
            zi.compress_type = zipfile.ZIP_DEFLATED
            if name == 'Document.xml':
                data = scrub_document_xml(data)
            zout.writestr(zi, data)
    tmp.replace(path)
