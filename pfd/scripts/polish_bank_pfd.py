#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""POLISH BANK detail sheet — graph-bridged IA-POL-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
IA-POL-01 / IA-POL-02 from graph; null rates stay null. No invented S##.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, mem_bar

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_edges,
    ia_register_lines,
    load,
)

_G = load()
_IA = {e.stream_id: e for e in ia_edges("polish", _G)}
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(20.0, 28.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)


def plate_cell(x, y, w, h, tag, metal, mode, anode, cathode, product):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.22",
        facecolor="#fafaf9", edgecolor=P.INK, linewidth=1.4, zorder=3,
    ))
    ax.text(x + 0.4, y + h - 0.38, tag, ha="left", va="top",
            fontsize=11.2, fontweight="bold", color=P.INK, zorder=4)
    ax.text(x + w - 0.4, y + h - 0.38, f"{metal}   {mode}", ha="right", va="top",
            fontsize=9.4, fontweight="bold", color=P.MUTED, zorder=4)

    inner_y = y + 1.05
    inner_h = h - 2.45
    aw = w * 0.28
    ax.add_patch(Rectangle((x + 0.32, inner_y), aw, inner_h,
                           facecolor=P.C_AN_F, edgecolor=P.C_AN, linewidth=1.15, zorder=4))
    ax.text(x + 0.32 + aw / 2, inner_y + inner_h * 0.70, "ANODE",
            ha="center", va="center", fontsize=9.6, fontweight="bold", color=P.C_AN, zorder=5)
    ax.text(x + 0.32 + aw / 2, inner_y + inner_h * 0.30, anode,
            ha="center", va="center", fontsize=7.8, color=P.MUTED, zorder=5, linespacing=1.08)

    mw = 0.78
    mx = x + 0.32 + aw + 0.10
    mem_bar(ax, mx, inner_y, mw, inner_h, "CEM")

    cx0 = mx + mw + 0.10
    cw = x + w - 0.32 - cx0
    ax.add_patch(Rectangle((cx0, inner_y), cw, inner_h,
                           facecolor=P.C_CA_F, edgecolor=P.C_CEM, linewidth=1.15, zorder=4))
    ax.text(cx0 + cw / 2, inner_y + inner_h * 0.70, "CATHODE",
            ha="center", va="center", fontsize=9.6, fontweight="bold", color=P.C_CEM, zorder=5)
    ax.text(cx0 + cw / 2, inner_y + inner_h * 0.30, cathode,
            ha="center", va="center", fontsize=7.8, color=P.MUTED, zorder=5, linespacing=1.08)

    ax.text(x + w / 2, y + 0.22, f"wall {P.WALL['polish']}     {product}",
            ha="center", va="bottom", fontsize=8.2, color=P.INK, zorder=6)
    return (x, y, w, h)


def precip_cell(x, y, w, h, tag, metal, mode, method, product):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.22",
        facecolor="#ecfdf5", edgecolor=P.C_LEACH, linewidth=1.4, zorder=3,
    ))
    ax.text(x + 0.4, y + h - 0.38, tag, ha="left", va="top",
            fontsize=11.2, fontweight="bold", color=P.INK, zorder=4)
    ax.text(x + w - 0.4, y + h - 0.38, f"{metal}   {mode}", ha="right", va="top",
            fontsize=9.4, fontweight="bold", color=P.MUTED, zorder=4)

    inner_y = y + 1.05
    inner_h = h - 2.45
    mem_bar(ax, x + 0.32, inner_y, 0.78, inner_h, "CEM")
    ax.add_patch(Rectangle((x + 1.22, inner_y), w - 1.54, inner_h,
                           facecolor=P.C_LE_F, edgecolor=P.C_LEACH, linewidth=1.15, zorder=4))
    ax.text(x + w / 2 + 0.3, inner_y + inner_h * 0.62, "CONCENTRATE + PRECIP",
            ha="center", va="center", fontsize=9.8, fontweight="bold", color=P.C_LEACH, zorder=5)
    ax.text(x + w / 2 + 0.3, inner_y + inner_h * 0.28, method,
            ha="center", va="center", fontsize=8.0, color=P.MUTED, zorder=5, linespacing=1.08)
    ax.text(x + w / 2, y + 0.22, f"wall {P.WALL['polish']}     {product}",
            ha="center", va="bottom", fontsize=8.2, color=P.INK, zorder=6)
    return (x, y, w, h)


ax.text(50, 99.35, "POLISH BANK  —  PARALLEL CEM CELLS AFTER EW-9",
        ha="center", va="top", fontsize=18.4, fontweight="bold", color=P.INK)
ax.text(50, 97.55,
        "Low-tenor leftovers   ·   not a second E° aisle   ·   Li and REE are concentrated then precipitated   ·   wall CPVC",
        ha="center", va="top", fontsize=11.6, color=P.MUTED)
ax.text(50, 96.15,
        f"Graph-bridged IA-POL-* from {_GP}  ·  null rates stay null  ·  no invented S##",
        ha="center", va="top", fontsize=9.0, color=P.MUTED)

ew = box(ax, 2.0, 91.45, 31.0, 4.6, P.C_SOL_F, P.C_SOLID, "EW-9  /  P-Ca",
         "depleted catholyte after Zn + pH-shift", ts=13.0, ss=8.8)
hdr = box(ax, 34.6, 91.45, 30.8, 4.6, P.C_LE_F, P.C_LEACH, P.NAME["polish_hdr"],
          "parallel bleed manifold", ts=13.2, ss=8.8)
bmed = box(ax, 67.0, 91.45, 31.0, 4.6, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "spent polish → SALT FEED", ts=13.0, ss=8.8)
arrow(ax, R(ew), L(hdr), P.C_LEACH, lw=1.7)

CW, CH = 30.4, 8.15
XS = [2.0, 34.8, 67.6]
YS = [81.55, 71.55, 61.55]
drawn = []
for i, spec in enumerate(P.POLISH_CELLS):
    r, c = divmod(i, 3)
    tag, metal, mode, anode, cathode, product = spec
    if tag in ("PK-4", "PK-5"):
        drawn.append(precip_cell(XS[c], YS[r], CW, CH, tag, metal, mode, cathode, product))
    else:
        drawn.append(plate_cell(XS[c], YS[r], CW, CH, tag, metal, mode, anode, cathode, product))

# manifold under the header, then a short drop into each cell
MY = 90.05
ax.plot([cx(drawn[0]), cx(drawn[2])], [MY, MY], color=P.C_LEACH, lw=1.4, zorder=2)
arrow(ax, B(hdr), (cx(hdr), MY), P.C_LEACH, lw=1.4)
for d in drawn:
    arrow(ax, (cx(d), MY), (cx(d), d[1] + d[3]), P.C_LEACH, lw=1.05)
slabel(ax, 18.5, 90.15, "parallel bleeds", P.C_LEACH, ha="left", size=8.8)

# spent to BMED from PK-9 and right column
arrow(ax, R(drawn[8]), (98.2, cy(drawn[8])), P.C_LEACH, lw=1.3, ls="--")
arrow(ax, (98.2, cy(drawn[8])), (98.2, cy(bmed)), P.C_LEACH, lw=1.3, ls="--")
arrow(ax, (98.2, cy(bmed)), R(bmed), P.C_LEACH, lw=1.3, ls="--")
slabel(ax, 97.4, 70.2, "spent\nbrine", P.C_LEACH, ha="right", size=8.4)
if "IA-POL-01" in _IA:
    slabel(ax, 82.5, 93.0, edge_callout(_IA["IA-POL-01"]), P.C_LEACH, size=7.6)
if "IA-POL-02" in _IA:
    slabel(ax, cx(hdr), hdr[1] - 0.55, edge_callout(_IA["IA-POL-02"]) + "  (series stub)", P.C_LEACH, size=7.4)


# products
met = box(ax, 2.0, 47.55, 30.4, 10.4, P.C_PROD_F, P.C_PROD, "POLISH METALS",
          "Co  Mn  Cr  Hg  Tl  Bi  Sb\npowder / sheet / MnO2\njoin METALS / ELEMENTS",
          ts=13.6, ss=9.4)
salts = box(ax, 34.8, 47.55, 30.4, 10.4, P.C_PROD_F, P.C_PROD, "Li  /  REE SALTS",
            "Li2CO3 or Li3PO4\nREE oxalate / hydroxide\nto farm / fab / metal line",
            ts=13.6, ss=9.4)
rad = box(ax, 67.6, 47.55, 30.4, 10.4, P.C_SOL_F, P.C_SOLID, P.NAME["rad_cell"],
          "isolated sump\nsludge vitrified into\nCERAMIC GRIT",
          ts=13.2, ss=9.2)

arrow(ax, B(drawn[0]), (met[0] + 6, met[1] + met[3]), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[1]), T(met), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[2]), (met[0] + met[2] - 4, met[1] + met[3]), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[5]), (met[0] + 10, met[1] + met[3]), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[6]), (met[0] + 16, met[1] + met[3]), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[7]), (met[0] + 22, met[1] + met[3]), P.C_PROD, lw=1.25)
arrow(ax, B(drawn[3]), (salts[0] + 8, salts[1] + salts[3]), P.C_LEACH, lw=1.25)
arrow(ax, B(drawn[4]), T(salts), P.C_LEACH, lw=1.25)
arrow(ax, B(drawn[8]), T(rad), P.C_SOLID, lw=1.35)

# grit handoff
grit = box(ax, 67.6, 39.55, 30.4, 5.4, P.C_IN_F, P.C_INORG, P.NAME["grit"],
           "glass-branch grit is the host matrix", ts=12.6, ss=8.8)
arrow(ax, B(rad), T(grit), P.C_SOLID, lw=1.25, ls="--")

hx = box(ax, 2.0, 39.55, 30.4, 5.4, P.C_HEAT_F, P.C_HEAT, "HX-8b   POLISH → Q3",
         "small ohmic reject onto the EW heat tap", ts=12.4, ss=8.8)

ax.text(2.0, 36.85, "WHY PARALLEL, AND WHAT DOES NOT GET PLATED",
        fontsize=12.4, fontweight="bold", color=P.INK)
ax.text(2.0, 35.75,
        "The main aisle already took Au through Zn by E°.  What remains is milligrams-to-grams per litre.  A second series cascade\n"
        "would idle most of the time and still miss Li and the REEs, which do not plate from this chloride liquor at a useful current efficiency.\n"
        "Header feeds every cell at once.  Dashed risers are depleted liquor leaving that cell, not a plating sequence.\n"
        "\n"
        "PK-4 Li: aqueous EW of lithium is not a process.  CEM concentrates Li+, then Na2CO3 (BMED) or phosphate drops Li2CO3 / Li3PO4.\n"
        "PK-5 REE: same idea — CEM upgrade, then oxalate or hydroxide.  Do not put a dummy cathode in that box.\n"
        "PK-2 Mn: chloride EW of Mn metal is fussy.  Anodic MnO2 on the MMO is the honest fallback when the cathode current efficiency collapses.\n"
        "PK-6 Hg and PK-9 radionuclides are sealed.  Hg vapor and alpha-bearing mist do not share a headspace with Co/Mn.\n"
        "PK-9 sludge is dissolved into the glass-branch grit melt.  That is the silicon / ceramic sink for activity, not a drum in a closet.\n"
        "Spent combined brine is the BMED SALT FEED.  No polish liquor returns to LEACH CSTR 1 until BMED has split it.",
        ha="left", va="top", fontsize=10.0, color=P.MUTED, linespacing=1.26)

ax.text(2.0, 14.15, "MEMBRANES  /  WALLS", fontsize=12.2, fontweight="bold", color=P.INK)
ax.add_patch(Rectangle((2.0, 11.65), 3.2, 1.55, facecolor=P.C_CEM_F, edgecolor=P.C_CEM, lw=1.2))
ax.text(5.5, 12.42, "CEM   sulfonated PS–PVC on PP felt    every polish cell    blue",
        ha="left", va="center", fontsize=10.0, color=P.MUTED)
ax.text(2.0, 10.35,
        f"Walls: {P.WALL['polish']} sheet, same cement spec as the EW aisle.  "
        "PK-6 and PK-9 get a welded lid and a dedicated ventilation stub to the alkaline scrubber.\n"
        f"Anodes that plate: {P.ANODE}.  Li / REE boxes have no anode.",
        ha="left", va="top", fontsize=10.0, color=P.MUTED, linespacing=1.26)

_reg = ia_register_lines(_IA.values())
ax.text(2.0, 3.55, f"GRAPH IA-POL-*  ({_GP})", fontsize=9.2, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(2.0, 2.75 - i * 0.55, line, ha="left", va="top", fontsize=7.2, color=P.MUTED)

ax.text(50.0, 0.35, P.NAMING_FOOT + "    POLISH BANK    POLISH HEADER",
        ha="center", va="bottom", fontsize=P.EW_FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.22)
fig.savefig(P.OUT_POLISH, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_POLISH)
