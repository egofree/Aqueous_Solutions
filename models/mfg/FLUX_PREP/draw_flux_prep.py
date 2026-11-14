# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""FLUX_PREP drawing set (X-MFG close-out follow-on pass): 8 sheets from the accepted build.

The drawing-set driver, not the model: the model is `flux_prep.py` over the shared
close-out builder (`models/mfg/farm_closeout.py`). `farm_hab_draw.draw` rebuilds the
parts from the unit's own `parts()` and draws the sheet set; it writes nothing beside
the drawings. (The former routing through `bench_prep.py` re-manifested the withdrawn
bench build over the close-out outputs - removed 2026-11-14.) Run:
    <cq python> draw_flux_prep.py             # SVG source from the build
    python3 docs-authority/_drawings.py  # title block + register rows
    <cq python> draw_flux_prep.py             # PDF pass (now from stamped SVGs)
"""
import pathlib, sys
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
from models.mfg import farm_hab_draw
farm_hab_draw.draw("FLUX_PREP")
