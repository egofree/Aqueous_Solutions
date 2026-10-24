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
    for f in scripts():
        print('build', os.path.relpath(f, ROOT), flush=True)
        subprocess.run([sys.executable, f], cwd=ROOT, check=True)
