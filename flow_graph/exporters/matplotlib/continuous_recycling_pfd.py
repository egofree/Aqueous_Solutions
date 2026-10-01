#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Plant-level continuous recycling PFD — graph-bridged IA-REC-* / IA-WET-*.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
IA-REC-01 / IA-REC-Q3 + wet float/C29 recycles labeled from graph; null rates stay null.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, hx_diamond

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_edges,
    ia_register_lines,
    load,
)

_G = load()
_IA = {e.stream_id: e for e in ia_edges("rec", _G)}
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(17.5, 25.0), dpi=155)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 99.4, "CONTINUOUS CLOSED-LOOP RECYCLING CIRCUIT",
        ha="center", va="top", fontsize=P.FONT_TITLE, fontweight="bold", color=P.INK)
ax.text(50, 97.4,
        "Disassembly tree   ·   hopper at feed   ·   products at discharge   ·   heat exchangers as cross-links",
        ha="center", va="top", fontsize=P.FONT_SUBTITLE, color=P.MUTED)
ax.text(50, 96.05,
        f"Graph-bridged IA-REC-* / IA-WET-* from {_GP}  ·  null rates stay null",
        ha="center", va="top", fontsize=8.6, color=P.MUTED)

ax.add_patch(FancyBboxPatch(
    (1.3, 1.15), 97.4, 15.7,
    boxstyle="round,pad=0.16,rounding_size=0.35",
    facecolor="none", edgecolor=P.C_HEAT, linewidth=1.05,
    linestyle="--", alpha=0.55, zorder=0,
))
ax.text(2.0, 16.45, "HEAT LADDER   Q1 → Q4", ha="left", va="top",
        fontsize=8.4, fontweight="bold", color=P.C_HEAT, zorder=1)

ax.text(15.4, 73.15, "OIL BRANCH", ha="center", va="bottom",
        fontsize=8.6, fontweight="bold", color=P.C_OIL)
ax.text(84.5, 73.15, P.NAME["glass"], ha="center", va="bottom",
        fontsize=8.6, fontweight="bold", color=P.C_INORG)

# trunk
hop = box(ax, 38.5, 90.6, 23.0, 5.2, P.C_SOL_F, P.C_SOLID, P.NAME["hopper"], "bulk waste feed")
shred = box(ax, 38.5, 83.6, 23.0, 5.2, P.C_SOL_F, P.C_SOLID, P.NAME["shredder"], "continuous")
l1 = box(ax, 36.8, 76.4, 26.4, 5.4, P.C_LE_F, P.C_LEACH, P.NAME["leach1"],
         f"{P.LEACH_CHEM}    {P.LEACH_T}")
l2 = box(ax, 34.8, 68.85, 30.4, 5.7, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
         f"tau = V / flow    {P.LEACH_ORP}    float–sink")
arrow(ax, B(hop), T(shred), P.C_SOLID, lw=2.1)
arrow(ax, B(shred), T(l1), P.C_SOLID, lw=2.1)
arrow(ax, B(l1), T(l2), P.C_LEACH, lw=2.1)

# oil
flt = box(ax, 2.1, 65.55, 26.6, 5.2, P.C_OIL_F, P.C_OIL, P.NAME["float"], "weir / DAF skim")
dry = box(ax, 2.1, 57.85, 26.6, 5.2, P.C_OIL_F, P.C_OIL, P.NAME["dryer"],
          f"paddle / belt    {P.DRYER_T}")
pyro = box(ax, 2.1, 48.55, 26.6, 6.8, P.C_OIL_F, P.C_OIL, P.NAME["pyro"],
           f"{P.PYRO_HW}    {P.PYRO_T}")
quen = box(ax, 2.1, 40.65, 26.6, 5.2, P.C_OIL_F, P.C_OIL, P.NAME["quench"], "oil down    NCG across")
still = box(ax, 2.1, 32.55, 26.6, 5.4, P.C_OIL_F, P.C_OIL, P.NAME["still"], "continuous still")
cuts = box(ax, 2.1, 20.55, 26.6, 6.3, P.C_PROD_F, P.C_PROD, P.NAME["cuts"], "→ new polymers")

arrow(ax, (l2[0], l2[1] + l2[3] * 0.62), R(flt), P.C_OIL, lw=1.95)
slabel(ax, 30.6, 70.55, "FLOAT", P.C_OIL, size=7.6)
slabel(ax, 30.6, 69.55, "light plastic,\nwool, paper, wood", P.C_OIL, size=6.4, va="top")
arrow(ax, B(flt), T(dry), P.C_OIL, lw=1.95)
arrow(ax, B(dry), T(pyro), P.C_OIL, lw=1.95)
arrow(ax, B(pyro), T(quen), P.C_OIL, lw=1.95)
arrow(ax, B(quen), T(still), P.C_OIL, lw=1.95)
arrow(ax, B(still), T(cuts), P.C_PROD, lw=1.95)
slabel(ax, 15.4, 39.45, "oil", P.C_OIL)
arrow(ax, (still[0] + 1.15, still[1] + still[3]), (pyro[0] + 1.15, pyro[1]),
      P.C_OIL, lw=1.15, ls="--")
slabel(ax, 4.4, 39.7, "heavies", P.C_OIL, ha="left", size=6.5)

# metal
ew = box(ax, 38.3, 57.55, 23.4, 6.05, P.C_SOL_F, P.C_SOLID, P.NAME["ew"],
         "Au → Ag → Cu → Pb → Sn → Ni → Fe …")
bmed = box(ax, 38.3, 40.55, 23.4, 5.7, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "HCl / NaOH / chlorate + Br-")
metals = box(ax, 38.3, 20.55, 23.4, 6.3, P.C_PROD_F, P.C_PROD, P.NAME["metals"], "plated products")
ab = box(ax, 38.3, 29.15, 23.4, 5.5, P.C_HEAT_F, P.C_HEAT, P.NAME["afterburner"],
         "NCG + tars    Q1 source")

arrow(ax, B(l2), T(ew), P.C_LEACH, lw=1.95)
slabel(ax, 50.0, 64.55, "pregnant liquor", P.C_LEACH)

mx = 36.55
arrow(ax, (ew[0], ew[1] + 1.1), (mx, ew[1] + 1.1), P.C_SOLID, lw=1.7)
arrow(ax, (mx, ew[1] + 1.1), (mx, metals[1] + metals[3] * 0.55), P.C_SOLID, lw=1.7)
arrow(ax, (mx, metals[1] + metals[3] * 0.55), L(metals), P.C_SOLID, lw=1.7)
slabel(ax, 35.7, 37.3, "cathode\nmetals", P.C_SOLID, ha="right", size=6.5)
arrow(ax, (ew[0] + ew[2] * 0.70, ew[1]), (bmed[0] + bmed[2] * 0.70, bmed[1] + bmed[3]),
      P.C_LEACH, lw=1.55)

rx = 33.85
arrow(ax, L(bmed), (rx, cy(bmed)), P.C_LEACH, lw=1.2, ls="--")
arrow(ax, (rx, cy(bmed)), (rx, cy(l1)), P.C_LEACH, lw=1.2, ls="--")
arrow(ax, (rx, cy(l1)), L(l1), P.C_LEACH, lw=1.2, ls="--")
slabel(ax, 33.15, 72.4, "regen", P.C_LEACH, ha="right", size=6.6)
if "IA-REC-01" in _IA:
    slabel(ax, 33.15, 71.2, edge_callout(_IA["IA-REC-01"]), P.C_LEACH, ha="right", size=6.2)
if "IA-WET-FLOAT-01" in _IA:
    slabel(ax, 30.6, 68.35, edge_callout(_IA["IA-WET-FLOAT-01"]), P.C_OIL, size=6.0, va="top")
if "IA-WET-C29-01" in _IA:
    slabel(ax, 50.0, 66.85, edge_callout(_IA["IA-WET-C29-01"]), P.C_LEACH, size=6.2)


arrow(ax, (quen[0] + quen[2], quen[1] + 0.7), (ab[0], ab[1] + ab[3] * 0.35),
      P.C_HEAT, lw=1.3, ls="--")
slabel(ax, 33.6, 33.15, "NCG", P.C_HEAT, size=6.6)

# glass
scr = box(ax, 71.4, 65.55, 26.5, 5.2, P.C_SOL_F, P.C_SOLID, P.NAME["screen"], "undissolved sink solids")
wash = box(ax, 71.4, 57.85, 26.5, 5.2, P.C_IN_F, P.C_INORG, P.NAME["wash"], "liquor back to leach")
burn = box(ax, 71.4, 48.85, 26.5, 6.15, P.C_IN_F, P.C_INORG, P.NAME["burnout"],
           f"{P.BURNOUT_T}\nindirect flue jacket — not the oil pipe")
mill = box(ax, 71.4, 40.65, 26.5, 5.2, P.C_IN_F, P.C_INORG, P.NAME["mill"], "< 300 um")
dig = box(ax, 71.4, 32.55, 26.5, 5.4, P.C_IN_F, P.C_INORG, P.NAME["digest"],
          f"{P.DIGEST_T}    BMED caustic")

sil = box(ax, 69.9, 20.55, 9.35, 6.3, P.C_PROD_F, P.C_PROD, P.NAME["silicate"], "farm Si / gel")
hyd = box(ax, 79.7, 20.55, 10.0, 6.3, P.C_PROD_F, P.C_PROD, "Ca / Al / Mg\nHYDROXIDES", "")
grit = box(ax, 90.15, 20.55, 8.35, 6.3, P.C_SOL_F, P.C_SOLID, "CERAMIC\nGRIT", "filler")

arrow(ax, (l2[0] + l2[2], l2[1] + l2[3] * 0.50), L(scr), P.C_SOLID, lw=1.95)
slabel(ax, 66.7, 70.55, "SINK", P.C_SOLID, size=7.6)
slabel(ax, 66.7, 69.55, "solids", P.C_SOLID, size=6.4, va="top")
arrow(ax, B(scr), T(wash), P.C_INORG, lw=1.95)
slabel(ax, 84.6, 63.85, "glass · ceramic · FR-4", P.C_INORG, size=6.7)
arrow(ax, B(wash), T(burn), P.C_INORG, lw=1.95)
arrow(ax, B(burn), T(mill), P.C_INORG, lw=1.95)
arrow(ax, B(mill), T(dig), P.C_INORG, lw=1.95)
arrow(ax, (dig[0] + 4.2, dig[1]), T(sil), P.C_INORG, lw=1.5)
arrow(ax, B(dig), T(hyd), P.C_INORG, lw=1.5)
arrow(ax, (dig[0] + dig[2] - 3.5, dig[1]), T(grit), P.C_SOLID, lw=1.5)

arrow(ax, (scr[0], scr[1] + scr[3] * 0.22), (scr[0] - 3.6, scr[1] + scr[3] * 0.22), P.C_OIL, lw=1.45)
slabel(ax, scr[0] - 3.8, scr[1] + scr[3] * 0.22 + 0.35, "dense plastic\n→ dryer",
       P.C_OIL, ha="right", size=6.5)

arrow(ax, (wash[0], wash[1] + 1.05), (bmed[0] + bmed[2], bmed[1] + bmed[3] * 0.78),
      P.C_LEACH, lw=1.15, ls="--")
slabel(ax, 66.5, 55.85, "rinse", P.C_LEACH, size=6.4)
arrow(ax, (burn[0], burn[1] + 1.05), (bmed[0] + bmed[2], bmed[1] + 1.15),
      P.C_LEACH, lw=1.15, ls="--")
slabel(ax, 66.5, 46.7, "Br- condensate", P.C_LEACH, size=6.4)

# HX gutters
GX_L, GX_R = 31.25, 67.65
h4 = hx_diamond(ax, GX_L, 60.45, "HX-4", P.HX["HX-4"])
h1 = hx_diamond(ax, GX_L, 52.05, "HX-1", P.HX["HX-1"])
h2 = hx_diamond(ax, GX_L, 45.85, "HX-2", P.HX["HX-2"])
h3 = hx_diamond(ax, GX_L, 35.25, "HX-3", P.HX["HX-3"])
h5 = hx_diamond(ax, GX_R, 79.15, "HX-5", P.HX["HX-5"])
h8 = hx_diamond(ax, GX_R, 60.55, "HX-8", P.HX["HX-8"])
h7 = hx_diamond(ax, GX_R, 51.95, "HX-7", P.HX["HX-7"])
h6 = hx_diamond(ax, GX_R, 35.25, "HX-6", P.HX["HX-6"])

arrow(ax, (h4[0] - 1.8, h4[1]), R(dry), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, R(pyro), (h1[0] - 1.8, h1[1]), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (ab[0], ab[1] + ab[3]), (h2[0] + 1.8, h2[1]), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (h3[0] - 1.8, h3[1]), R(still), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (h5[0] - 1.8, h5[1]), R(l1), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, R(ew), (h8[0] - 1.8, h8[1]), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (h7[0] + 1.8, h7[1]), L(burn), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (h6[0] + 1.8, h6[1]), L(dig), P.C_HEAT, lw=1.15, ls="--")
arrow(ax, (ab[0] + ab[2], ab[1] + ab[3] * 0.72), (h7[0] - 1.8, h7[1] - 0.9),
      P.C_HEAT, lw=1.15, ls="--")

q1 = box(ax, 2.4, 2.95, 22.4, 11.3, P.C_HEAT_F, P.C_HEAT, P.HEAT["Q1"]["label"],
         P.HEAT["Q1"]["sub"], ts=10.3, ss=7.2)
q2 = box(ax, 26.6, 2.95, 22.4, 11.3, P.C_HEAT_F, P.C_HEAT, P.HEAT["Q2"]["label"],
         P.HEAT["Q2"]["sub"], ts=10.3, ss=7.2)
q3 = box(ax, 50.8, 2.95, 22.4, 11.3, P.C_HEAT_F, P.C_HEAT, P.HEAT["Q3"]["label"],
         P.HEAT["Q3"]["sub"], ts=10.3, ss=7.2)
q4 = box(ax, 75.0, 2.95, 22.6, 11.3, P.C_HEAT_F, P.C_HEAT, P.HEAT["Q4"]["label"],
         P.HEAT["Q4"]["sub"], ts=10.3, ss=7.2)
arrow(ax, R(q1), L(q2), P.C_HEAT, lw=2.4)
arrow(ax, R(q2), L(q3), P.C_HEAT, lw=2.4)
arrow(ax, R(q3), L(q4), P.C_HEAT, lw=2.4)
if "IA-REC-Q3" in _IA:
    slabel(ax, cx(q3), q3[1] + q3[3] + 0.35, edge_callout(_IA["IA-REC-Q3"]), P.C_HEAT, size=6.4)


ax.text(2.0, 18.55, "STREAMS", fontsize=P.FONT_LEGEND, fontweight="bold", color=P.INK)
items = [
    (P.C_SOLID, "solids / shred"),
    (P.C_LEACH, "aqueous / leach / brine"),
    (P.C_OIL, "organics / oil"),
    (P.C_INORG, "glass–ceramic"),
    (P.C_HEAT, "heat (dashed = HX)"),
    (P.C_PROD, "products"),
]
for i, (col, name) in enumerate(items):
    xx = 14.0 + i * 14.1
    ax.plot([xx, xx + 2.2], [18.55, 18.55], color=col, lw=3.15, solid_capstyle="butt")
    ax.text(xx + 2.55, 18.55, name, ha="left", va="center", fontsize=7.2, color=P.MUTED)

_reg = ia_register_lines(_IA.values())
ax.text(2.0, 17.55, f"GRAPH IA-*  ({_GP})", fontsize=7.6, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(2.0, 16.75 - i * 0.72, line, ha="left", va="top", fontsize=6.0, color=P.MUTED)

ax.text(50.0, 0.35, P.RULES_FOOT, ha="center", va="bottom", fontsize=P.FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.2)
fig.savefig(P.OUT_PLANT, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_PLANT)
