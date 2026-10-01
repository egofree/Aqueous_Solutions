#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""EW cascade cell-by-cell aisle — graph-bridged IA-EW-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
Layout/names remain params/drawlib. IA-EW-01…04 labeled from graph;
null rates stay null. No invented S##.
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
_IA = {e.stream_id: e for e in ia_edges("ew", _G)}
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(20.0, 28.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)


def ew_cell(x, y, w, h, tag, metal, e0, anode, cathode, vessel, product):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.22",
        facecolor="#fafaf9", edgecolor=P.INK, linewidth=1.45, zorder=3,
    ))
    ax.text(x + 0.45, y + h - 0.42, tag, ha="left", va="top",
            fontsize=P.EW_FONT_CELL, fontweight="bold", color=P.INK, zorder=4)
    ax.text(x + w - 0.45, y + h - 0.42, f"{metal}   E° {e0}", ha="right", va="top",
            fontsize=10.2, fontweight="bold", color=P.MUTED, zorder=4)

    inner_y = y + 0.95
    inner_h = h - 2.35
    aw = w * 0.28
    ax.add_patch(Rectangle((x + 0.35, inner_y), aw, inner_h,
                           facecolor=P.C_AN_F, edgecolor=P.C_AN, linewidth=1.2, zorder=4))
    ax.text(x + 0.35 + aw / 2, inner_y + inner_h * 0.70, "ANODE",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=P.C_AN, zorder=5)
    ax.text(x + 0.35 + aw / 2, inner_y + inner_h * 0.32, anode,
            ha="center", va="center", fontsize=P.EW_FONT_CELL_SUB, color=P.MUTED, zorder=5, linespacing=1.1)

    mw = 0.85
    mx = x + 0.35 + aw + 0.12
    mem_bar(ax, mx, inner_y, mw, inner_h, "CEM")

    cx0 = mx + mw + 0.12
    cw = x + w - 0.35 - cx0
    ax.add_patch(Rectangle((cx0, inner_y), cw, inner_h,
                           facecolor=P.C_CA_F, edgecolor=P.C_CEM, linewidth=1.2, zorder=4))
    ax.text(cx0 + cw / 2, inner_y + inner_h * 0.70, "CATHODE",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=P.C_CEM, zorder=5)
    ax.text(cx0 + cw / 2, inner_y + inner_h * 0.32, cathode,
            ha="center", va="center", fontsize=P.EW_FONT_CELL_SUB, color=P.MUTED, zorder=5, linespacing=1.1)

    ax.text(x + w / 2, y + 0.22, f"wall {vessel}     product {product}",
            ha="center", va="bottom", fontsize=8.8, color=P.INK, zorder=6)
    return (x, y, w, h)


ax.text(50, 99.35, "EW CASCADE  —  CELL-BY-CELL AISLE",
        ha="center", va="top", fontsize=P.EW_FONT_TITLE, fontweight="bold", color=P.INK)
ax.text(50, 97.55,
        "Leach at the head   ·   sequential electrowinning by E°   ·   polymer cell walls   ·   metals as powder or sheet",
        ha="center", va="top", fontsize=P.EW_FONT_SUBTITLE, color=P.MUTED)
ax.text(50, 96.15,
        f"Graph-bridged IA-EW-* from {_GP}  ·  null rates stay null  ·  no invented S##",
        ha="center", va="top", fontsize=9.0, color=P.MUTED)

oil = box(ax, 1.4, 92.15, 16.6, 4.55, P.C_OIL_F, P.C_OIL, P.NAME["oil"],
          "stub only   see oil sheet", ts=13.5, ss=9.2)
leach = box(ax, 19.6, 92.15, 60.8, 4.55, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
            f"{P.LEACH_CHEM}    {P.LEACH_T}    {P.LEACH_ORP}", ts=14.5, ss=9.6)
glass = box(ax, 81.8, 92.15, 16.8, 4.55, P.C_IN_F, P.C_INORG, P.NAME["glass"],
            "stub only   see glass sheet", ts=12.4, ss=8.8)
arrow(ax, R(oil), L(leach), P.C_OIL, lw=1.5, ls="--")
arrow(ax, L(glass), R(leach), P.C_INORG, lw=1.5, ls="--")

vdf = box(ax, 19.6, 86.35, 60.8, 4.4, P.C_SOL_F, P.C_SOLID, P.NAME["vdf"],
          "solids → VIBRATORY SPLIT     liquor → EW header", ts=14.0, ss=9.5)
arrow(ax, B(leach), T(vdf), P.C_LEACH, lw=2.0)
slabel(ax, 50.0, 91.55, "pregnant liquor", P.C_LEACH, size=10.0)

CW, CH = 30.4, 6.55
XS = [2.0, 34.8, 67.6]
YS = [78.55, 70.85, 63.15]
drawn = []
for i, (tag, metal, e0, anode, cathode, wall_key, product) in enumerate(P.EW_CELLS):
    r, c = divmod(i, 3)
    drawn.append(ew_cell(XS[c], YS[r], CW, CH, tag, metal, e0, anode, cathode,
                         P.WALL[wall_key], product))

arrow(ax, (50.0, 86.35), (cx(drawn[0]), drawn[0][1] + drawn[0][3]), P.C_LEACH, lw=1.7)
slabel(ax, 17.6, 85.55, "catholyte header", P.C_LEACH, ha="left", size=9.2)
# Graph IA overlays (LEACH→EW-1, EW cascade, EW→polish)
if "IA-EW-04" in _IA:
    slabel(ax, 50.0, 88.85, edge_callout(_IA["IA-EW-04"]), P.C_LEACH, size=8.2)
if "IA-EW-01" in _IA:
    slabel(ax, cx(drawn[0]) + 8.0, cy(drawn[0]) + 0.15, edge_callout(_IA["IA-EW-01"]), P.C_LEACH, size=7.4)
if "IA-EW-02" in _IA:
    slabel(ax, 50.0, 68.55, edge_callout(_IA["IA-EW-02"]) + "  (stages 3–8 proxy)", P.C_LEACH, size=7.6)

for a, b in [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8)]:
    arrow(ax, R(drawn[a]), L(drawn[b]), P.C_LEACH, lw=1.55)

ax.annotate("", xy=(1.15, 63.4), xytext=(1.15, 85.0),
            arrowprops=dict(arrowstyle="<->", color=P.C_AN, lw=1.5, linestyle="--"))
ax.text(0.55, 74.2, "SALRIA ANOLYTE LOOP\nCl2 / chlorate regen   CRU",
        ha="center", va="center", fontsize=8.4, color=P.C_AN, rotation=90, zorder=5)

slabel(ax, 50.0, 62.35, "each cell harvests independently  →  METALS / ELEMENTS",
       P.C_LEACH, size=10.0)

ax.text(2.0, 61.35, "pH-SHIFT PRECIP   —   NaOH from BMED BASE chamber",
        ha="left", va="bottom", fontsize=13.2, fontweight="bold", color=P.C_CEM)

pal = box(ax, 2.0, 54.55, 23.6, 6.15, P.C_IN_F, P.C_INORG, P.PH_SHIFT[0][0],
          f"{P.PH_SHIFT[0][1]}\nwall {P.WALL[P.PH_SHIFT[0][2]]}", ts=12.8, ss=9.2)
pmg = box(ax, 27.2, 54.55, 23.6, 6.15, P.C_IN_F, P.C_INORG, P.PH_SHIFT[1][0],
          f"{P.PH_SHIFT[1][1]}\nwall {P.WALL[P.PH_SHIFT[1][2]]}", ts=12.8, ss=9.2)
pca = box(ax, 52.4, 54.55, 23.6, 6.15, P.C_IN_F, P.C_INORG, P.PH_SHIFT[2][0],
          f"{P.PH_SHIFT[2][1]}\nwall {P.WALL[P.PH_SHIFT[2][2]]}", ts=12.8, ss=9.2)
pol = box(ax, 77.4, 54.55, 20.6, 6.15, P.C_SOL_F, P.C_SOLID, P.NAME["polish"],
          f"parallel CEM cells\nCo Mn Cr Li REE\nwall {P.WALL['polish']}", ts=12.6, ss=8.8)

arrow(ax, (cx(drawn[8]), drawn[8][1]), (cx(pal) + 8, pal[1] + pal[3]), P.C_LEACH, lw=1.6)
slabel(ax, 78.5, 62.0, "depleted catholyte", P.C_LEACH, ha="left", size=9.0)
if "IA-EW-03" in _IA:
    slabel(ax, 78.5, 60.75, edge_callout(_IA["IA-EW-03"]), P.C_LEACH, ha="left", size=7.6)

arrow(ax, R(pal), L(pmg), P.C_INORG, lw=1.5)
arrow(ax, R(pmg), L(pca), P.C_INORG, lw=1.5)
arrow(ax, R(pca), L(pol), P.C_SOLID, lw=1.4, ls="--")
slabel(ax, cx(pal), pal[1] - 0.15, "▼ Al(OH)3 cake", P.C_INORG, size=8.6, va="top")
slabel(ax, cx(pmg), pmg[1] - 0.15, "▼ Mg(OH)2 cake", P.C_INORG, size=8.6, va="top")
slabel(ax, cx(pca), pca[1] - 0.15, "▼ Ca cake", P.C_INORG, size=8.6, va="top")

hx = box(ax, 77.4, 49.55, 20.6, 3.85, P.C_HEAT_F, P.C_HEAT, P.NAME["hx8"],
         "ohmic reject to heat ladder", ts=12.4, ss=8.8)

ax.add_patch(FancyBboxPatch(
    (2.0, 27.15), 96.0, 21.7,
    boxstyle="round,pad=0.14,rounding_size=0.32",
    facecolor="#ecfdf5", edgecolor=P.C_LEACH, linewidth=1.7, zorder=2,
))
ax.text(50.0, 48.35, "BMED REGEN     NaCl brine  →  HCl  +  NaOH  +  chlorate makeup",
        ha="center", va="top", fontsize=15.0, fontweight="bold", color=P.C_LEACH, zorder=4)
ax.text(50.0, 46.55,
        f"3-compartment stack   ·   ACID {P.WALL['bmed_acid']}   ·   BASE {P.WALL['bmed_base']}   ·   membranes hot-swappable PS–PVC on PP felt",
        ha="center", va="top", fontsize=10.0, color=P.MUTED, zorder=4)

BY, BH = 30.55, 12.6
units = [
    ("cath", 8.8), ("bpm1", 2.4), ("base", 14.6), ("cem", 2.2), ("salt", 16.4),
    ("aem", 2.2), ("acid", 14.6), ("bpm2", 2.4), ("anod", 8.8),
]
gap = 0.35
total_w = sum(w for _, w in units) + gap * (len(units) - 1)
x0 = 50.0 - total_w / 2
xs, x = [], x0
for name, w in units:
    xs.append((name, x, w))
    x += w + gap


def ch_box(x, y, w, h, fill, edge, t1, t2, ts=11.5, ss=8.6):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge,
                           linewidth=1.35, zorder=4))
    ax.text(x + w / 2, y + h * 0.68, t1, ha="center", va="center",
            fontsize=ts, fontweight="bold", color=P.INK, zorder=5)
    ax.text(x + w / 2, y + h * 0.30, t2, ha="center", va="center",
            fontsize=ss, color=P.MUTED, zorder=5, linespacing=1.08)


base_x = salt_x = acid_x = 0
base_w = salt_w = acid_w = 0
for name, x, w in xs:
    if name == "cath":
        ch_box(x, BY, w, BH, P.C_CA_F, P.C_CEM, "CATHODE", P.BMED_CATHODE)
    elif name == "bpm1":
        mem_bar(ax, x, BY, w, BH, "BPM_BO")
    elif name == "base":
        ch_box(x, BY, w, BH, P.C_LE_F, P.C_LEACH, "BASE", f"NaOH   wall {P.WALL['bmed_base']}")
        base_x, base_w = x, w
    elif name == "cem":
        mem_bar(ax, x, BY, w, BH, "CEM")
    elif name == "salt":
        ch_box(x, BY, w, BH, P.C_SOL_F, P.C_SOLID, "SALT", f"NaCl   wall {P.WALL['bmed_salt']}")
        salt_x, salt_w = x, w
    elif name == "aem":
        mem_bar(ax, x, BY, w, BH, "AEM")
    elif name == "acid":
        ch_box(x, BY, w, BH, P.C_AN_F, P.C_AN, "ACID", f"HCl   wall {P.WALL['bmed_acid']}")
        acid_x, acid_w = x, w
    elif name == "bpm2":
        mem_bar(ax, x, BY, w, BH, "BPM_BO")
    elif name == "anod":
        ch_box(x, BY, w, BH, P.C_AN_F, P.C_AN, "ANODE", P.ANODE.split(" / ")[0] + " / MMO")

ax.text(base_x + base_w / 2, BY - 0.45, "OH- from BPM  +  Na+ through CEM",
        ha="center", va="top", fontsize=8.4, color=P.C_LEACH, zorder=5)
ax.text(salt_x + salt_w / 2, BY - 0.45, "depleted brine recycled",
        ha="center", va="top", fontsize=8.4, color=P.MUTED, zorder=5)
ax.text(acid_x + acid_w / 2, BY - 0.45, "H+ from BPM  +  Cl- through AEM",
        ha="center", va="top", fontsize=8.4, color=P.C_AN, zorder=5)
ax.text(50.0, 28.05,
        "BPM facing: CEL (blue) toward cathode     ·     AEL (orange) toward anode",
        ha="center", va="bottom", fontsize=8.6, color=P.MUTED, zorder=5)

arrow(ax, (base_x + base_w / 2, BY + BH), (cx(pal), pal[1]), P.C_LEACH, lw=1.7)
arrow(ax, (base_x + base_w / 2, BY + BH), (cx(pmg), pmg[1]), P.C_LEACH, lw=1.7)
arrow(ax, (base_x + base_w / 2, BY + BH), (cx(pca), pca[1]), P.C_LEACH, lw=1.7)
slabel(ax, base_x + base_w / 2 + 0.4, 44.15, "NaOH to precip", P.C_LEACH, size=9.4)
arrow(ax, (salt_x + 1.0, BY - 1.7), (salt_x + salt_w * 0.30, BY), P.C_LEACH, lw=1.4, ls="--")
slabel(ax, salt_x + 1.0, BY - 1.85, "brine in", P.C_LEACH, ha="left", size=8.8)

arrow(ax, (pol[0] + pol[2], cy(pol)), (98.2, cy(pol)), P.C_LEACH, lw=1.25, ls="--")
arrow(ax, (98.2, cy(pol)), (98.2, BY + BH * 0.55), P.C_LEACH, lw=1.25, ls="--")
arrow(ax, (98.2, BY + BH * 0.55), (salt_x + salt_w, BY + BH * 0.55), P.C_LEACH, lw=1.25, ls="--")

met = box(ax, 2.0, 16.35, 30.4, 8.55, P.C_PROD_F, P.C_PROD, P.NAME["metals"],
          "sheets:  Ag  Cu  Pb  Sn  Ni  Cd  Zn\npowder:  Au  Fe   (Sn optional)\neach EW cell harvests independently",
          ts=14.2, ss=9.4)
hyd = box(ax, 34.8, 16.35, 30.4, 8.55, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "Al(OH)3 from P-Al\nMg(OH)2 from P-Mg\nCa(OH)2 / CaCO3 from P-Ca\nto farm / metal line",
          ts=14.2, ss=9.4)
reg = box(ax, 67.6, 16.35, 30.4, 8.55, P.C_LE_F, P.C_LEACH, P.NAME["regen"],
          "HCl from BMED ACID chamber\nNaClO3 from anolyte / CRU loop\nback to LEACH CSTR 1",
          ts=14.2, ss=9.4)

arrow(ax, (acid_x + acid_w / 2, BY), (reg[0] + reg[2] * 0.45, reg[1] + reg[3]), P.C_AN, lw=1.7)
slabel(ax, acid_x + acid_w / 2 + 3.2, 26.55, "HCl", P.C_AN, size=9.6)

ax.text(2.0, 14.35, "MEMBRANES", fontsize=12.2, fontweight="bold", color=P.INK)
ax.add_patch(Rectangle((2.0, 11.85), 3.4, 1.7, facecolor=P.C_CEM_F, edgecolor=P.C_CEM, lw=1.3))
ax.text(5.7, 12.7, "CEM   sulfonated PS–PVC on PP felt, double-layer hot-swap",
        ha="left", va="center", fontsize=10.0, color=P.MUTED)
ax.add_patch(Rectangle((2.0, 9.65), 3.4, 1.7, facecolor=P.C_AEM_F, edgecolor=P.C_AEM, lw=1.3))
ax.text(5.7, 10.5, "AEM   aminated PS–PVC on PP felt",
        ha="left", va="center", fontsize=10.0, color=P.MUTED)
ax.add_patch(Rectangle((2.0, 7.45), 1.7, 1.7, facecolor=P.C_CEM_F, edgecolor=P.C_CEM, lw=1.2))
ax.add_patch(Rectangle((3.7, 7.45), 1.7, 1.7, facecolor=P.C_AEM_F, edgecolor=P.C_AEM, lw=1.2))
ax.text(5.7, 8.3, "BPM   double line  blue CEL | orange AEL     CEL faces cathode, AEL faces anode",
        ha="left", va="center", fontsize=10.0, color=P.MUTED)

ax.text(2.0, 6.35, "WALLS, ELECTRODES, SOLVENT", fontsize=12.2, fontweight="bold", color=P.INK)
ax.text(2.0, 5.55,
        "Walls are polymer.  Bare Ti and 316L are not cell walls in Salria — hot pH 0 chloride + high ORP strips the Ti oxide; 316L pits.\n"
        f"Default aisle wall: solid CPVC sheet (not foam-core expanded PVC), solvent-welded with {P.CEMENT}\n"
        f"Anolyte / Salria / EW-1–2 / CRU: {P.WALL['anolyte']}.  HDPE and PP fail in hot oxidizer.  "
        f"BMED BASE: {P.WALL['bmed_base']}.  BMED ACID: {P.WALL['bmed_acid']}.\n"
        f"Anodes: {P.ANODE} — the coating is the barrier; the substrate is not a tank wall.\n"
        "Cathodes: Ti Gr.2 blanks on Au / Ag / Ni;  316L starter sheets on Cu / Pb / Sn / Cd / Fe;  Ti or Al starter on Zn.\n"
        "PVC cement solvents weld PVC and CPVC only.  They do not weld PE, PP, or PVDF.  Cure fully before Salria fill.",
        ha="left", va="top", fontsize=9.6, color=P.MUTED, linespacing=1.26)

# Graph IA-* register (honest null rates)
_reg = ia_register_lines(_IA.values())
ax.add_patch(FancyBboxPatch(
    (52.0, 6.85), 46.0, 7.2,
    boxstyle="round,pad=0.10,rounding_size=0.22",
    facecolor="#f8fafc", edgecolor=P.MUTED, linewidth=1.1, zorder=2,
))
ax.text(53.0, 13.55, f"GRAPH IA-EW-*  ({_GP})",
        ha="left", va="top", fontsize=9.2, fontweight="bold", color=P.INK, zorder=4)
for i, line in enumerate(_reg):
    ax.text(53.0, 12.35 - i * 1.15, line, ha="left", va="top",
            fontsize=7.2, color=P.MUTED, zorder=4)

ax.text(50.0, 0.35, P.NAMING_FOOT, ha="center", va="bottom", fontsize=P.EW_FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.22)
fig.savefig(P.OUT_EW, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_EW)
