"""engine v2: the declared input payload.

One builder for the payload every solve, check, update and renderer consumes:
the drivers, the baseline site profile, and the declared auxiliary data files.
Families declare the auxiliary files they read in AUXILIARY (path, loader) rows
here — data files are declared, never opened ad hoc inside solve functions.
Loading is the I/O boundary: callers load once and pass the payload down.
"""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_json(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return json.load(f)


def _read_csv_rows(path):
    """A CSV as a list of dicts (string values), header-keyed."""
    with open(os.path.join(ROOT, path), encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def load(extra=()):
    """The canonical payload: drivers, site_profile, and every declared auxiliary
    file. extra: (key, loader-result) pairs a caller adds (e.g. a site profile
    variant for a locale check)."""
    payload = {
        'drivers': _read_json('flow_graph/param/drivers.json'),
        'site_profile': _read_json('flow_graph/param/sites/baseline.json'),
    }
    for key, value in extra:
        payload[key] = value
    return payload
