# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""DUCK_PEN drawing set (X-FARM M3 follow-on pass): 8 sheets from the accepted build."""
import pathlib, sys
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
from models.mfg import farm_hab_draw
farm_hab_draw.draw("DUCK_PEN")
