#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""GLASS / CERAMIC BRANCH — graph-bridged IA-GLASS-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
IA-GLASS-01…03 + IA-GLASS-Q2 from graph; null rates stay null. No invented S##.
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
_IA = {e.stream_id: e for e in ia_edges("glass", _G)}
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(20.0, 28.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 99.35, "GLASS / CERAMIC BRANCH  —  SPLIT · RINSE · BURNOUT · DIGEST",
        ha="center", va="top", fontsize=18.5, fontweight="bold", color=P.INK)
ax.text(50, 97.55,
        "Undissolved sink solids at the head   ·   silicate / hydroxides / grit at the bottom   ·   no FR-4 in the oil auger",
        ha="center", va="top", fontsize=12.0, color=P.MUTED)
ax.text(50, 96.15,
        f"Graph-bridged IA-GLASS-* from {_GP}  ·  null rates stay null  ·  no invented S##",
        ha="center", va="top", fontsize=9.0, color=P.MUTED)

# head
leach = box(ax, 2.0, 91.35, 38.0, 4.7, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
            "undissolved sink  →  VDF", ts=13.2, ss=9.2)
vdf = box(ax, 42.0, 91.35, 27.0, 4.7, P.C_SOL_F, P.C_SOLID, P.NAME["vdf"],
          "cake to this sheet", ts=13.0, ss=9.0)
oil = box(ax, 71.0, 91.35, 27.0, 4.7, P.C_OIL_F, P.C_OIL, P.NAME["oil"],
          "dense-plastic handoff", ts=13.0, ss=9.0)
arrow(ax, R(leach), L(vdf), P.C_LEACH, lw=1.5)

scr = box(ax, 18.0, 82.55, 64.0, 6.0, P.C_SOL_F, P.C_SOLID, P.NAME["screen"],
          "wet classification    glass · ceramic · FR-4 down    dense thermoplastic across",
          ts=14.4, ss=9.8)
arrow(ax, B(vdf), T(scr), P.C_SOLID, lw=2.0)

# plastic jumper to oil
arrow(ax, R(scr), (scr[0] + scr[2] + 6.5, cy(scr)), P.C_OIL, lw=1.7)
arrow(ax, (scr[0] + scr[2] + 6.5, cy(scr)), (scr[0] + scr[2] + 6.5, cy(oil)), P.C_OIL, lw=1.7)
arrow(ax, (scr[0] + scr[2] + 6.5, cy(oil)), L(oil), P.C_OIL, lw=1.7)
slabel(ax, 86.5, 80.15, "dense PE / PVC / PET\n→ DRYER", P.C_OIL, ha="center", size=9.0)

wash = box(ax, 18.0, 73.35, 64.0, 6.0, P.C_IN_F, P.C_INORG, P.NAME["wash"],
           "countercurrent    liquor and fines → REGEN LEACH / BMED SALT", ts=14.4, ss=9.8)
arrow(ax, B(scr), T(wash), P.C_INORG, lw=2.0)

# burnout + afterburner pair
ax.add_patch(FancyBboxPatch(
    (8.0, 54.55), 84.0, 16.2,
    boxstyle="round,pad=0.12,rounding_size=0.30",
    facecolor="#eff6ff", edgecolor=P.C_INORG, linewidth=1.7, zorder=2,
))
ax.text(50.0, 70.15, P.NAME["burnout"], ha="center", va="top",
        fontsize=15.0, fontweight="bold", color=P.INK, zorder=4)
ax.text(50.0, 68.35, f"{P.BURNOUT_T}    jacketed by AFTERBURNER flue    not the oil auger    atmospheres isolated",
        ha="center", va="top", fontsize=10.0, color=P.MUTED, zorder=4)

rot = box(ax, 10.2, 56.55, 36.6, 9.0, P.C_IN_F, P.C_INORG, "INDIRECT-FIRED\nROTARY",
          "SiC / high-Ni tube\norganics + epoxy out\nglass / ceramic stay", ts=13.0, ss=9.0)
ab = box(ax, 50.0, 56.55, 20.0, 9.0, P.C_HEAT_F, P.C_HEAT, P.NAME["afterburner"],
         "oil-line NCG\n+ burnout off-gas\nQ1 source", ts=12.6, ss=8.8)
jkt = box(ax, 73.2, 56.55, 16.6, 9.0, P.C_HEAT_F, P.C_HEAT, "FLUE\nJACKET",
          "HX-7\nQ2 to rotary\nno mixing", ts=12.6, ss=8.8)
arrow(ax, R(ab), L(jkt), P.C_HEAT, lw=1.6)
arrow(ax, L(jkt), R(rot), P.C_HEAT, lw=1.4, ls="--")
arrow(ax, B(wash), T(rot), P.C_INORG, lw=1.9)
if "IA-GLASS-01" in _IA:
    slabel(ax, cx(wash), wash[1] - 0.55, edge_callout(_IA["IA-GLASS-01"]), P.C_INORG, size=8.0)


# Br- to BMED
bmed = box(ax, 73.2, 47.55, 16.6, 5.4, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "Br- condensate in", ts=12.2, ss=8.6)
arrow(ax, B(rot), (cx(rot) + 18, bmed[1] + bmed[3]), P.C_LEACH, lw=1.3, ls="--")
arrow(ax, (cx(rot) + 18, bmed[1] + bmed[3]), L(bmed), P.C_LEACH, lw=1.3, ls="--")
slabel(ax, 62.0, 52.55, "Br- / HCl vapor\ncondensate", P.C_LEACH, size=8.8)

mill = box(ax, 10.2, 47.55, 36.6, 5.4, P.C_IN_F, P.C_INORG, P.NAME["mill"],
           "< 300 µm    dry mill after burnout", ts=13.6, ss=9.4)
arrow(ax, B(rot), T(mill), P.C_INORG, lw=1.9)
if "IA-GLASS-02" in _IA:
    slabel(ax, cx(mill), mill[1] + mill[3] + 0.35, edge_callout(_IA["IA-GLASS-02"]), P.C_INORG, size=8.0)


# digest
dig = box(ax, 10.2, 32.55, 62.6, 12.4, P.C_IN_F, P.C_INORG, "", "")
ax.text(41.5, 44.15, P.NAME["digest"], ha="center", va="top",
        fontsize=14.6, fontweight="bold", color=P.INK, zorder=5)
ax.text(41.5, 42.35, f"{P.DIGEST_T}    BMED NaOH    glass → silicate    Al/Ca/Mg → hydroxides",
        ha="center", va="top", fontsize=9.6, color=P.MUTED, zorder=5)

d1 = box(ax, 12.2, 33.35, 18.0, 6.4, P.C_LE_F, P.C_LEACH, "NaOH FEED",
         f"from BMED BASE\nwall {P.WALL['bmed_base']}", ts=12.0, ss=8.8)
d2 = box(ax, 32.4, 33.35, 18.0, 6.4, P.C_IN_F, P.C_INORG, "DIGESTOR",
         "stirred PP or Ni\n80–90 °C", ts=12.0, ss=8.8)
d3 = box(ax, 52.6, 33.35, 18.0, 6.4, P.C_SOL_F, P.C_SOLID, "FILTER",
         "silicate liquor\nvs  grit cake", ts=12.0, ss=8.8)
arrow(ax, R(d1), L(d2), P.C_LEACH, lw=1.5)
arrow(ax, R(d2), L(d3), P.C_INORG, lw=1.5)
arrow(ax, B(mill), T(d2), P.C_INORG, lw=1.7)
if "IA-GLASS-03" in _IA:
    slabel(ax, cx(mill) - 8.0, mill[1] - 0.55, edge_callout(_IA["IA-GLASS-03"]), P.C_INORG, size=8.0)


# HX
h7 = hx_diamond(ax, 93.2, 61.05, "HX-7", P.HX["HX-7"])
h6 = hx_diamond(ax, 93.2, 38.65, "HX-6", P.HX["HX-6"])
arrow(ax, R(jkt), (h7[0] - 1.8, h7[1]), P.C_HEAT, lw=1.2, ls="--")
if "IA-GLASS-Q2" in _IA:
    slabel(ax, 88.5, 66.55, edge_callout(_IA["IA-GLASS-Q2"]), P.C_HEAT, size=7.4)

arrow(ax, (h6[0] - 1.8, h6[1]), R(dig), P.C_HEAT, lw=1.2, ls="--")

# products
sil = box(ax, 2.0, 18.55, 30.4, 10.2, P.C_PROD_F, P.C_PROD, P.NAME["silicate"],
          "Na-silicate liquor\nfarm Si / silica gel\nwafer-fab slurries", ts=14.0, ss=9.6)
hyd = box(ax, 34.8, 18.55, 30.4, 10.2, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "Ca / Al / Mg cakes\njoin pH-SHIFT PRECIP\n→ farm / metal line", ts=14.0, ss=9.6)
grit = box(ax, 67.6, 18.55, 30.4, 10.2, P.C_SOL_F, P.C_SOLID, P.NAME["grit"],
           "undigested ceramic\nAl2O3 / SiC / filler\nmedia / aggregate", ts=14.0, ss=9.6)

arrow(ax, B(d3), (cx(sil), sil[1] + sil[3]), P.C_PROD, lw=1.6)
arrow(ax, B(d3), T(hyd), P.C_INORG, lw=1.6)
arrow(ax, B(d3), (cx(grit), grit[1] + grit[3]), P.C_SOLID, lw=1.6)

# leach regen stub
reg = box(ax, 2.0, 12.15, 30.4, 4.5, P.C_LE_F, P.C_LEACH, P.NAME["regen"],
          "rinse liquor returns here", ts=12.4, ss=8.8)
arrow(ax, (wash[0], cy(wash)), (3.4, cy(wash)), P.C_LEACH, lw=1.2, ls="--")
arrow(ax, (3.4, cy(wash)), (3.4, cy(reg)), P.C_LEACH, lw=1.2, ls="--")
arrow(ax, (3.4, cy(reg)), L(reg), P.C_LEACH, lw=1.2, ls="--")

ax.text(2.0, 10.55, "HARDWARE  /  RULES", fontsize=12.2, fontweight="bold", color=P.INK)
ax.text(2.0, 9.65,
        "This branch exists because FR-4, glass, and ceramic must not enter the Ti / cast-iron auger.  The fork pays for itself by protecting the oil line.\n"
        "Burnout is a small indirect rotary jacketed by afterburner flue (HX-7).  Oil vapor and burnout off-gas share the afterburner, not the kiln atmosphere.\n"
        "Rinse returns chloride and residual metals to REGEN LEACH.  Brominated FR-4 off-gas is condensed into BMED, not vented.\n"
        "Digest uses BMED NaOH, not purchased caustic.  Silicate liquor is the silicon-cycle return; hydroxide cakes join the EW pH-shift products.\n"
        "Grit that will not digest is product, not waste — media, filler, or aggregate.",
        ha="left", va="top", fontsize=10.0, color=P.MUTED, linespacing=1.28)

_reg = ia_register_lines(_IA.values())
ax.text(2.0, 3.55, f"GRAPH IA-GLASS-*  ({_GP})", fontsize=9.2, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(2.0, 2.75 - i * 0.55, line, ha="left", va="top", fontsize=7.0, color=P.MUTED)

ax.text(50.0, 0.35, P.NAMING_FOOT, ha="center", va="bottom",
        fontsize=P.EW_FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.22)
fig.savefig(P.OUT_GLASS, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_GLASS)
