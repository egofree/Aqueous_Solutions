# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Make STEP exports byte-stable across runs.

The Open CASCADE STEP writer names each product 'Open CASCADE STEP translator <version> <n>',
where <n> counts the exports made so far in the writing process. The same model therefore
exports different bytes depending on how many exports ran before it in that process, and a
rebuild of one unit rewrote the STEP files of unrelated units. This module removes the counter.
Geometry and every other record are left untouched.

    python3 models/mfg/lib/step_normalize.py              # every models/mfg/*/export/*.step
    python3 models/mfg/lib/step_normalize.py FILE ...     # the named files

models/mfg/build_all.py runs it after the builds. Run it after a single unit builder too.
"""
import glob, os, re, sys

_COUNTER = re.compile(rb"('Open CASCADE STEP translator [0-9.]+) [0-9]+'")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def normalize_bytes(data: bytes) -> bytes:
    """STEP text with the per-process product counter removed."""
    return _COUNTER.sub(rb"\1'", data)


def normalize(path: str) -> bool:
    """Rewrite `path` in place if it carries the counter. Returns True when the file changed."""
    with open(path, 'rb') as f:
        data = f.read()
    out = normalize_bytes(data)
    if out == data:
        return False
    with open(path, 'wb') as f:
        f.write(out)
    return True


def main(argv):
    files = argv or sorted(glob.glob(os.path.join(ROOT, 'models', 'mfg', '*', 'export', '*.step')))
    changed = [f for f in files if normalize(f)]
    print(f'step_normalize: {len(changed)} of {len(files)} STEP files normalized')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
