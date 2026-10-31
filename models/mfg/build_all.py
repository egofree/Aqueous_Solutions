# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Run every CadQuery manufacturing model under models/mfg (pipeline stage cad_mfg_models; needs CadQuery).

Discovery is by location, so a new model script joins the build without editing this file: the train scripts
directly under models/mfg/, then each unit folder's own model script, then its drawing scripts (draw_*.py), which
read the model the first script exported."""
import glob, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.join(ROOT, 'models', 'mfg')


def scripts():
    top = sorted(f for f in glob.glob(os.path.join(HERE, '*.py')) if os.path.basename(f) != 'build_all.py')
    unit = sorted(glob.glob(os.path.join(HERE, '*', '*.py')))
    models = [f for f in unit if not os.path.basename(f).startswith('draw_')]
    drawings = [f for f in unit if os.path.basename(f).startswith('draw_')]
    return top + models + drawings


if __name__ == '__main__':
    # Top-level train scripts that take per-unit argv are expanded once per unit;
    # everything else runs argless (foundry/polymers default to their own UNITS).
    # PYTHONPATH carries the repo root so unit draw_*.py scripts can import models.*.
    env = dict(os.environ, PYTHONPATH=ROOT + os.pathsep + os.environ.get('PYTHONPATH', ''))
    PER_UNIT = {'evap_mvr.py': ['EVAP_ACID', 'EVAP_BASE']}
    for f in scripts():
        base = os.path.basename(f)
        calls = [[f, u] for u in PER_UNIT[base]] if base in PER_UNIT else [[f]]
        for call in calls:
            print('build', os.path.relpath(call[0], ROOT), *call[1:], flush=True)
            subprocess.run([sys.executable, *call], cwd=ROOT, check=True, env=env)
