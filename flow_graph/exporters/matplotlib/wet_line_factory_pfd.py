#!/usr/bin/env python3
"""Factory wet line — one leach vessel, weir + in-tank auger, funnel EW aisle."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, FancyArrowPatch
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, mem_bar

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_edges,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)

_G = load()
_SEC = sector_edge_map("wet", _G)
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(32.0, 26.0), dpi=140)
ax.set_xlim(0, 164)
ax.set_ylim(-24.0, 118)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

# graph bridge banner placed after title texts below

ax.text(82, 116.6, "DISASSEMBLY LINE",
        ha="center", va="top", fontsize=31, fontweight="bold", color=P.INK)
ax.text(82, 114.55,
        "HOPPER above the tank.  No filter before leach.  "
        "CSTR 2 = weir on CSTR 1.  CSTR 3 = PVC / FG sink auger in the floor of CSTR 1.  "
        "EW liquor overflows cell to cell.  Metal leaves the funnel.",
        ha="center", va="top", fontsize=17.4, color=P.MUTED)

# ── gas rail ─────────────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (2.0, 109.4), 160.0, 4.15,
    boxstyle="round,pad=0.06,rounding_size=0.16",
    facecolor="#f5f5f4", edgecolor=P.C_SOLID, linewidth=1.05, zorder=2,
))
ax.text(82.0, 113.15, "GAS  —  FOUR HEADERS    hall held negative",
        ha="center", va="top", fontsize=17.4, fontweight="bold", color=P.INK)
ax.text(82.0, 111.35,
        "DUST (grey)  shredder throat → baghouse     "
        "ACID GAS (green)  CSTR 1 lid + every EW / PK anode hood → DEMISTER → ALK SCRUBBER     "
        "H2 (blue)  cathode headspace → own tote     "
        "OIL VAPOR stays on OIL LINE",
        ha="center", va="top", fontsize=13.3, color=P.MUTED)


def funnel_cell(x, y, w, h, tag, metal, product):
    ax.add_patch(FancyBboxPatch(
        (x, y + h * 0.36), w, h * 0.64,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        facecolor="#fafaf9", edgecolor=P.INK, linewidth=1.15, zorder=3,
    ))
    ax.text(x + w / 2, y + h - 0.16, f"{tag}  {metal}",
            ha="center", va="top", fontsize=14.3, fontweight="bold", color=P.INK, zorder=5)
    inner_y = y + h * 0.44
    inner_h = h * 0.38
    pad = 0.20
    aw = (w - 2 * pad - 0.40) * 0.34
    ax.add_patch(Rectangle((x + pad, inner_y), aw, inner_h,
                           facecolor=P.C_AN_F, edgecolor=P.C_AN, lw=0.9, zorder=4))
    ax.text(x + pad + aw / 2, inner_y + inner_h / 2, "A",
            ha="center", va="center", fontsize=11.8, fontweight="bold", color=P.C_AN, zorder=5)
    mx = x + pad + aw + 0.05
    mem_bar(ax, mx, inner_y, 0.30, inner_h, "CEM")
    cx0 = mx + 0.36
    cw = x + w - pad - cx0
    ax.add_patch(Rectangle((cx0, inner_y), cw, inner_h,
                           facecolor=P.C_CA_F, edgecolor=P.C_CEM, lw=0.9, zorder=4))
    ax.text(cx0 + cw / 2, inner_y + inner_h / 2, "C",
            ha="center", va="center", fontsize=11.8, fontweight="bold", color=P.C_CEM, zorder=5)
    fy = y + h * 0.36
    ax.add_patch(Polygon(
        [(x + pad, fy), (x + w - pad, fy),
         (x + w / 2 + 0.55, y + 1.20), (x + w / 2 - 0.55, y + 1.20)],
        closed=True, facecolor=P.C_CA_F, edgecolor=P.C_CEM, lw=1.0, zorder=4,
    ))
    ax.add_patch(Rectangle((x + w / 2 - 0.38, y + 0.52), 0.76, 0.68,
                           facecolor="#fafaf9", edgecolor=P.INK, lw=1.05, zorder=5))
    ax.plot([x + w / 2 - 0.22, x + w / 2 + 0.22], [y + 0.86, y + 0.86],
            color=P.INK, lw=1.15, zorder=6)
    ax.text(x + w / 2, y + 0.08, product, ha="center", va="bottom",
            fontsize=10.5, color=P.MUTED, zorder=5)
    return (x, y, w, h)


# ── mezzanine feed ───────────────────────────────────────
ax.text(2.0, 107.55, "1   FEED  (mezzanine)", fontsize=18.6, fontweight="bold", color=P.INK)
hop = box(ax, 2.0, 100.4, 24.0, 6.3, P.C_SOL_F, P.C_SOLID,
          "HOPPER / SHREDDER", "elevated   dust hood at throat", ts=18.9, ss=12.7)
conv = box(ax, 28.5, 100.4, 26.0, 6.3, P.C_SOL_F, P.C_SOLID,
           "VIBRATORY CONVEYOR", "no filter   dumps into CSTR 1", ts=18.6, ss=12.7)
arrow(ax, R(hop), L(conv), P.C_SOLID, lw=1.9)
slabel(ax, 27.25, 107.05, "shred", P.C_SOLID, size=8.2)

# ── LEACH CSTR 1 as one vessel with weir + floor auger ───
tank_x, tank_y, tank_w, tank_h = 57.0, 92.6, 62.0, 14.1
ax.add_patch(FancyBboxPatch(
    (tank_x, tank_y), tank_w, tank_h,
    boxstyle="round,pad=0.10,rounding_size=0.28",
    facecolor=P.C_LE_F, edgecolor=P.C_LEACH, linewidth=1.7, zorder=3,
))
ax.text(tank_x + 28.0, tank_y + tank_h - 0.35, P.NAME["leach1"],
        ha="center", va="top", fontsize=20.8, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 28.0, tank_y + tank_h - 2.15,
        f"{P.LEACH_CHEM}    {P.LEACH_T}    {P.LEACH_ORP}\n"
        "lidded mixer    acid-gas takeoff    CPVC / PVDF wall",
        ha="center", va="top", fontsize=12.4, color=P.MUTED, zorder=5, linespacing=1.15)

# floor auger drawn inside the tank
ax.add_patch(FancyBboxPatch(
    (tank_x + 2.2, tank_y + 0.7), 36.5, 4.6,
    boxstyle="round,pad=0.04,rounding_size=0.12",
    facecolor=P.C_SOL_F, edgecolor=P.C_SOLID, linewidth=1.15, zorder=4,
))
ax.text(tank_x + 20.45, tank_y + 3.95, "CSTR 3  AUGER   (in floor)",
        ha="center", va="center", fontsize=14.9, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 20.45, tank_y + 2.15, "injection-molded PVC / FG    lifts sink solids",
        ha="center", va="center", fontsize=11.5, color=P.MUTED, zorder=5)

# weir lip on the right wall of the same tank
ax.add_patch(FancyBboxPatch(
    (tank_x + 41.0, tank_y + 6.6), 19.2, 4.6,
    boxstyle="round,pad=0.04,rounding_size=0.12",
    facecolor=P.C_OIL_F, edgecolor=P.C_OIL, linewidth=1.2, zorder=4,
))
ax.text(tank_x + 50.6, tank_y + 9.85, "CSTR 2  WEIR",
        ha="center", va="center", fontsize=15.5, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 50.6, tank_y + 8.05, "float overflows here",
        ha="center", va="center", fontsize=11.5, color=P.MUTED, zorder=5)

ax.text(tank_x + tank_w / 2, tank_y + tank_h + 0.35,
        P.NAME["leach_fork"] + "  =  weir + in-tank auger   (one vessel)",
        ha="center", va="bottom", fontsize=14.6, fontweight="bold", color=P.C_LEACH)

leach = (tank_x, tank_y, tank_w, tank_h)
arrow(ax, R(conv), (tank_x, tank_y + tank_h - 2.2), P.C_SOLID, lw=1.9)
slabel(ax, 55.4, 107.2, "drop", P.C_SOLID, size=8.0)

# liquor pump, then CONC-ED, then the aisle. No drum on this path.
pump = box(ax, 2.0, 94.0, 16.4, 5.2, P.C_LE_F, P.C_LEACH,
           "LEACHATE PUMP",
           "CSTR 1 discharge",
           ts=16.1, ss=11.2)
conc = box(ax, 20.0, 94.0, 34.5, 5.2, P.C_LE_F, P.C_LEACH,
           "CONC-ED",
           "0.2 µm · 3 m/s · CEM · Ti/PbO2\n"
           "2 → 0.17 m³/h    pH < 1.5",
           ts=16.1, ss=10.2)
arrow(ax, (tank_x, tank_y + 8.4), R(pump), P.C_LEACH, lw=1.7)
arrow(ax, R(pump), L(conc), P.C_LEACH, lw=1.55)

# ── float / sink handling ────────────────────────────────
ax.text(2.0, 90.9, "2   SOLIDS FORK", fontsize=18.6, fontweight="bold", color=P.INK)
float_dw = box(ax, 121.5, 100.4, 20.0, 6.3, P.C_OIL_F, P.C_OIL,
               "FLOAT DEWATER", "liquor pumped back to CSTR 1", ts=17.1, ss=11.8)
oil = box(ax, 144.0, 100.4, 18.0, 6.3, P.C_OIL_F, P.C_OIL,
          P.NAME["oil"], "DRYER → PYRO   stub", ts=17.7, ss=12.4)
arrow(ax, (tank_x + tank_w, tank_y + 8.9), L(float_dw), P.C_OIL, lw=1.6)
arrow(ax, R(float_dw), L(oil), P.C_OIL, lw=1.5)
arrow(ax, (float_dw[0], float_dw[1] + 1.2), (tank_x + tank_w, tank_y + 12.4),
      P.C_LEACH, lw=1.15, ls="--")
slabel(ax, 120.6, 99.55, "liquor return", P.C_LEACH, size=7.4)

sink_dw = box(ax, 57.0, 84.4, 28.0, 5.4, P.C_SOL_F, P.C_SOLID,
              "SINK DEWATER", "drain → CSTR 1", ts=17.7, ss=12.1)
split = box(ax, 88.0, 84.4, 31.0, 5.4, P.C_SOL_F, P.C_SOLID,
            P.NAME["screen"], "undissolved sink solids", ts=18, ss=12.1)
glass = box(ax, 122.0, 84.4, 20.0, 5.4, P.C_IN_F, P.C_INORG,
            P.NAME["glass"], "rinse · burnout · mill   stub", ts=16.4, ss=11.8)
dense = box(ax, 144.5, 84.4, 17.5, 5.4, P.C_OIL_F, P.C_OIL,
            "DENSE PLASTIC", "jumper → " + P.NAME["oil"], ts=16.1, ss=11.8)
arrow(ax, (tank_x + 20.5, tank_y), T(sink_dw), P.C_SOLID, lw=1.5)
arrow(ax, R(sink_dw), L(split), P.C_SOLID, lw=1.4)
arrow(ax, R(split), L(glass), P.C_INORG, lw=1.4)
arrow(ax, (split[0] + split[2], split[1] + 1.3), L(dense), P.C_OIL, lw=1.35)
arrow(ax, T(dense), B(oil), P.C_OIL, lw=1.25)
arrow(ax, (sink_dw[0] + 6.0, sink_dw[1] + sink_dw[3]),
      (tank_x + 8.0, tank_y), P.C_LEACH, lw=1.1, ls="--")
slabel(ax, 68.0, 90.35, "drain", P.C_LEACH, size=7.4)

# ── EW aisle ─────────────────────────────────────────────
ax.text(2.0, 81.9,
        "3   EW CASCADE    overflow train    metal leaves the funnel    liquor overflows each cell weir into the next",
        fontsize=18.6, fontweight="bold", color=P.INK)

cells_meta = [
    ("EW-1", "Au", "powder"),
    ("EW-2", "Ag", "sheet / pwd"),
    ("EW-3", "Cu", "sheet"),
    ("EW-4", "Pb", "sheet"),
    ("EW-5", "Sn", "sheet / pwd"),
    ("EW-6", "Ni", "sheet"),
    ("EW-7", "Fe", "powder"),
    ("EW-8", "Cd", "sheet"),
    ("EW-9", "Zn", "sheet"),
]
funnels = []
x0, y0, cw, ch = 2.0, 67.6, 15.2, 12.4
for i, (tag, metal, prod) in enumerate(cells_meta):
    f = funnel_cell(x0 + i * 16.0, y0, cw, ch, tag, metal, prod)
    funnels.append(f)
    if i:
        arrow(ax, R(funnels[i - 1]), L(f), P.C_LEACH, lw=1.3)
        slabel(ax, (funnels[i - 1][0] + funnels[i - 1][2] + f[0]) / 2,
               y0 + ch + 0.12, "overflow", P.C_LEACH, size=7.0)

arrow(ax, B(conc), (cx(funnels[0]), funnels[0][1] + funnels[0][3]), P.C_LEACH, lw=1.9)
slabel(ax, 12.5, 92.7, "concentrate → EW-1", P.C_LEACH, size=8.0)
arrow(ax, (cx(conc) + 8.0, conc[1]), (tank_x + 10.0, tank_y), P.C_LEACH, lw=1.05, ls="--")
slabel(ax, 48.2, 93.35, "diluate + dP bypass → CSTR 1", P.C_LEACH, size=7.6)

# sloped bund under the aisle
ax.add_patch(FancyBboxPatch(
    (2.0, 63.6), 146.0, 3.2,
    boxstyle="round,pad=0.04,rounding_size=0.10",
    facecolor="#e7e5e4", edgecolor=P.C_SOLID, linewidth=1.0, zorder=2,
))
ax.text(75.0, 65.2, "SLOPED BUND  /  CATCHMENT    spills + valve drips drain to HARVEST sump    liquor back to CSTR 1",
        ha="center", va="center", fontsize=13.3, color=P.MUTED, zorder=4)

bmed = box(ax, 148.5, 67.6, 13.5, 15.6, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "spent liquor\nin\nHCl + NaOH\nout\n" + P.NAME["regen"],
           ts=16.4, ss=11.5)
arrow(ax, R(funnels[-1]), L(bmed), P.C_LEACH, lw=1.35)
slabel(ax, 147.6, 80.7, "spent", P.C_LEACH, size=7.4)

# anode ticks
for f in funnels:
    ax.plot([f[0] + f[2] * 0.22, f[0] + f[2] * 0.22],
            [f[1] + f[3], f[1] + f[3] + 0.55], color=P.C_AN, lw=0.95, zorder=4)
ax.text(75.0, 81.05, "anode hoods → acid-gas header", ha="center", va="bottom",
        fontsize=12.4, color=P.C_AN)

# ── harvest ──────────────────────────────────────────────
ax.text(2.0, 62.05, "4   HARVEST", fontsize=18.6, fontweight="bold", color=P.INK)
man = box(ax, 2.0, 54.2, 72.0, 6.6, P.C_SOL_F, P.C_SOLID,
          "MANUAL / STARTUP",
          "funnel valve → lidded pail in the bund  →  one shared HARVEST " + P.NAME["vdf"],
          ts=18.6, ss=12.7)
auto = box(ax, 77.0, 54.2, 72.0, 6.6, P.C_PROD_F, P.C_PROD,
           "AUTO  (full scale)",
           "each cell → own drum filter  →  induction or oil-gas melt\n"
           "melt gas from OIL LINE    same header as AFTERBURNER",
           ts=18.6, ss=12.4)
vdf = box(ax, 2.0, 47.4, 36.0, 5.2, P.C_SOL_F, P.C_SOLID,
          "HARVEST " + P.NAME["vdf"], "shared drum   startup / manual", ts=17.1, ss=12.1)
melt = box(ax, 113.0, 47.4, 36.0, 5.2, P.C_HEAT_F, P.C_HEAT,
           "MELT", "induction or oil-gas    from OIL LINE", ts=17.7, ss=12.1)
met = box(ax, 40.5, 47.4, 70.0, 5.2, P.C_PROD_F, P.C_PROD,
          P.NAME["metals"],
          "powder, sheet, or melt    Au Ag Cu Pb Sn Ni Fe Cd Zn", ts=18.9, ss=12.7)
for f in funnels:
    arrow(ax, (f[0] + f[2] / 2, f[1]), (f[0] + f[2] / 2, 66.8), P.C_CEM, lw=0.85)
arrow(ax, (38.0, 63.6), T(man), P.C_SOLID, lw=1.25)
arrow(ax, (113.0, 63.6), T(auto), P.C_PROD, lw=1.25)
arrow(ax, B(man), T(vdf), P.C_SOLID, lw=1.2)
arrow(ax, B(auto), T(melt), P.C_HEAT, lw=1.2)
arrow(ax, R(vdf), L(met), P.C_PROD, lw=1.3)
arrow(ax, L(melt), R(met), P.C_PROD, lw=1.3)

# ── pH shift ─────────────────────────────────────────────
ax.text(2.0, 45.55, "5   pH-SHIFT PRECIP    NaOH from " + P.NAME["bmed"],
        fontsize=18.6, fontweight="bold", color=P.INK)
p1 = box(ax, 2.0, 39.2, 32.0, 5.2, P.C_IN_F, P.C_INORG, "P-Al   pH 5.0–5.5", "Al(OH)3 cake", ts=17.7, ss=12.4)
p2 = box(ax, 36.5, 39.2, 32.0, 5.2, P.C_IN_F, P.C_INORG, "P-Mg   pH 10.5–11", "Mg(OH)2 cake", ts=17.7, ss=12.4)
p3 = box(ax, 71.0, 39.2, 32.0, 5.2, P.C_IN_F, P.C_INORG, "P-Ca   pH 12–12.5", "Ca(OH)2 / CaCO3", ts=17.7, ss=12.4)
hyd = box(ax, 106.0, 39.2, 56.0, 5.2, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "filter cakes", ts=18.9, ss=12.4)
arrow(ax, R(p1), L(p2), P.C_INORG, lw=1.25)
arrow(ax, R(p2), L(p3), P.C_INORG, lw=1.25)
arrow(ax, R(p3), L(hyd), P.C_PROD, lw=1.4)
arrow(ax, B(bmed), (155.2, 44.4), P.C_LEACH, lw=1.05, ls="--")
slabel(ax, 155.6, 45.7, "NaOH", P.C_LEACH, size=7.4)

# ── polish ───────────────────────────────────────────────
ax.text(2.0, 37.45, P.NAME["polish"] + "   parallel tap after EW-9",
        fontsize=18.6, fontweight="bold", color=P.INK)
pks = [("PK-1", "Co", "pwd"), ("PK-2", "Mn", "pwd"), ("PK-3", "Cr", "pwd"),
       ("PK-6", "Hg", "sealed"), ("PK-7", "Tl", "pwd"), ("PK-8", "Bi/Sb", "pwd"),
       ("PK-9", "rad", "sealed")]
pkf = []
for i, (tag, metal, prod) in enumerate(pks):
    pkf.append(funnel_cell(2.0 + i * 16.0, 24.6, 15.2, 11.2, tag, metal, prod))
li = box(ax, 115.5, 27.0, 46.5, 8.8, P.C_IN_F, P.C_INORG,
         "PK-4 Li    PK-5 REE", "CEM concentrate   not plated", ts=18.6, ss=12.7)
arrow(ax, R(pkf[-1]), L(li), P.C_INORG, lw=1.2)

# ── regen + air ──────────────────────────────────────────
ax.text(2.0, 22.7, "6   REGEN  +  AIR", fontsize=18.6, fontweight="bold", color=P.INK)
scrub = box(ax, 2.0, 16.0, 32.0, 5.6, P.C_SOL_F, P.C_SOLID,
            "DEMISTER + ALK SCRUBBER",
            "HDR_ACID_GAS   lean NaOH", ts=17.1, ss=12.1)
polish = box(ax, 36.0, 16.0, 32.0, 5.6, P.C_SOL_F, P.C_SOLID,
             "ACID_POLISH_SCRUB",
             "S65 residual → S66 liquor → CRU", ts=17.1, ss=12.1)
regen = box(ax, 70.0, 16.0, 42.0, 5.6, P.C_LE_F, P.C_LEACH, P.NAME["regen"],
            "bund rinse + BMED acid + CRU chlorate  →  CSTR 1", ts=17.1, ss=12.1)
cru = box(ax, 114.0, 16.0, 48.0, 5.6, P.C_AN_F, P.C_AN, P.NAME["cru"],
          "S66 SCRUBBER_TO_CRU  ·  Cl2 ≠ H2", ts=17.7, ss=12.1)
arrow(ax, R(scrub), L(polish), P.C_AN, lw=1.3)
arrow(ax, R(polish), (cru[0], cy(polish)), P.C_LEACH, lw=1.2, ls="--")
slabel(ax, 34.5, 22.2, "S65", P.C_AN, size=8.0)
slabel(ax, 100.0, 22.2, "S66", P.C_LEACH, size=8.0)

ax.text(2.0, 14.5, "GEOMETRY", fontsize=18, fontweight="bold", color=P.INK)
ax.text(2.0, 13.15,
        "HOPPER / SHREDDER sits on a mezzanine above LEACH CSTR 1. Vibratory conveyor dumps shred straight into the tank. No filter on that drop. The tank lid is the first acid-gas hood.\n"
        "CSTR 2 is a weir on CSTR 1, not a second tank. Float goes over the weir onto FLOAT DEWATER; liquor from that conveyor is pumped back into CSTR 1; solids go DRYER → INDUCTION PYROLYZER (OIL LINE stub).\n"
        "CSTR 3 is an injection-molded PVC / fiberglass auger in the floor of CSTR 1. It lifts undissolved sink onto SINK DEWATER (drain returns to CSTR 1) then VIBRATORY SPLIT: dense plastic jumper to OIL LINE, grit to GLASS / CERAMIC BRANCH.\n"
        "Pregnant liquor is pumped from CSTR 1 through CONC-ED (alumina crossflow, then CEM) into EW-1. Diluate and a high-dP bypass return to CSTR 1. Au plates and drops the EW-1 funnel. Liquor overflows EW-1 → EW-2 (Ag) → … → EW-9 (Zn). Spent liquor to BMED REGEN.\n"
        "Each EW / PK cell is a funnel-bottom CPVC tank with a center CEM divider (A | CEM | C). Powder or loose sheet leaves through the bottom valve. A sloped bund under the aisle catches drips; bund liquor returns to CSTR 1.\n"
        "Manual / startup: valve into a lidded pail in the bund, then one shared HARVEST VACUUM DRUM FILTER. Auto: each cell has its own drum, then induction or oil-gas melt fired from the OIL LINE header that also feeds AFTERBURNER.\n"
        "Dust, acid gas, H2, and oil vapor never share a header.\n""Acid-gas end state (AQS-VENT-001): ALK + ACID_POLISH → CRU; upset stack residual only — not continuous outdoor dump.",
        ha="left", va="top", fontsize=13.6, color=P.MUTED, linespacing=1.22)

# ── machine / process list callout ───────────────────────
ax.add_patch(FancyBboxPatch(
    (2.0, 1.2), 160.0, 9.8,
    boxstyle="round,pad=0.08,rounding_size=0.18",
    facecolor="#fafaf9", edgecolor=P.MUTED, linewidth=1.15, zorder=3,
))
ax.text(4.0, 10.3, "MACHINE / PROCESS LIST  ·  AQS-PFD-WET-001  ·  locked names",
        ha="left", va="top", fontsize=15.5, fontweight="bold", color=P.INK, zorder=4)
ax.text(4.0, 8.7,
        "FEED: HOPPER / SHREDDER · VIBRATORY CONVEYOR\n"
        "LEACH: LEACH CSTR 1 (+ CSTR 2 WEIR · CSTR 3 AUGER) · LEACHATE PUMP · CONC-ED\n"
        "SOLIDS: FLOAT DEWATER · DRYER → INDUCTION PYROLYZER (OIL LINE) · SINK DEWATER · VIBRATORY SPLIT · GLASS / CERAMIC BRANCH\n"
        "EW: EW-1…EW-9 funnel cells · SLOPED BUND · HARVEST VDF / MELT · METALS / ELEMENTS\n"
        "PRECIP: P-Al · P-Mg · P-Ca → Ca / Al / Mg HYDROXIDES\n"
        "POLISH: PK-1…PK-9 · PK-4 / PK-5 bleed before P-Al · PK-5B split · PK-10 As sealed\n"
        "ANIONS / METAL: AEM BANK · K SPLIT · N SCRUB · MOLTEN-SALT CELLS · Si / B REDUCE\n"
        "REGEN / AIR: BMED REGEN · DEMISTER + ALK SCRUBBER · ACID_POLISH_SCRUB (S65–S66) · REGEN LEACH · CRU / CHLORATE\n"
        "GAS HEADERS: DUST · ACID GAS · H2 · OIL VAPOR (never shared)\n"
        "FAB REAGENT FORKS (detail AQS-PFD-FAB-RGN-001): existing HCl/NaOH PRODUCT + CRU; "
        "NEW WS_HF_ED · WS_PEROX · WS_AMMONIA · WS_NITRIC · WS_PHOS · WS_KOH · WS_DOPE · WS_SLURRY · WS_SOLV "
        "(S31–S39 → WAFER FAB)",
        ha="left", va="top", fontsize=11.5, color=P.MUTED, zorder=4, linespacing=1.18)

ax.text(82.0, 0.30, P.NAMING_FOOT + "    DOC  AQS-PFD-WET-001",
        ha="center", va="bottom", fontsize=11.5, color=P.MUTED)


_reg = ia_register_lines(_SEC.values())
ax.text(2.0, -14.6, "7   ANIONS · SPLIT · MOLTEN · REDUCE    vessel / acid / return",
        fontsize=14.5, fontweight="bold", color=P.INK)
ax.text(2.0, -16.0,
        "AEM BANK: PP frame, AEM-CAST film stub. No acid in the cut. HCl CIP only. Borate/phosphate/sulfate/fluoride concentrate → farm. Diluate → BMED salt. As is not this cut.\n"
        "K SPLIT: cooled PP crystallizer. No acid. KCl → farm. NaCl brine → BMED.\n"
        "N SCRUB: packed tower on burnout and pyro headers. Wall waits on POL-VCM. BMED HCl. NH4 salt → farm.\n"
        "PK-5B: PP lot tank, not a flow cell. Oxalic / HCl redissolve. Nd/Pr/Dy/Tb and La–Ce lots → molten cells. Mother liquor → CSTR 1.\n"
        "MOLTEN-SALT: dry chloride cell, graphite shell. No aqueous acid. Metal out. Cl2 → alk scrubber.\n"
        "Si / B REDUCE: arc furnace. Char pipe from OIL LINE pyro. No aqueous EW. Si → FAB PREP. Slag → alkali fusion.\n"
        "AEM-CAST and POL-VCM are the first copy-stoppers. Neither is on site.",
        ha="left", va="top", fontsize=11.2, color=P.MUTED, linespacing=1.18)
ax.text(2.0, -22.4, f"GRAPH WET/REC  ({_GP})  ·  null rates stay null", fontsize=10.8, fontweight="bold", color=P.INK)
for i, line in enumerate(list(_reg)[:6]):
    ax.text(2.0, -23.2 - i * 0.28, line, ha="left", va="top", fontsize=8.1, color=P.MUTED)
if "IA-WET-FLOAT-01" in _SEC:
    slabel(ax, 20.0, 88.0, edge_callout(_SEC["IA-WET-FLOAT-01"]), P.C_LEACH, size=6.8)
if "IA-WET-C29-01" in _SEC:
    slabel(ax, 40.0, 88.0, edge_callout(_SEC["IA-WET-C29-01"]), P.C_LEACH, size=6.8)
if "S09" in _SEC:
    slabel(ax, 120.0, 70.0, edge_callout(_SEC["S09"]), P.C_LEACH, size=6.6)
if "S10" in _SEC:
    slabel(ax, 120.0, 66.0, edge_callout(_SEC["S10"]), P.C_LEACH, size=6.6)

plt.tight_layout(pad=0.18)
out = getattr(P, "OUT_WET", P.ROOT / "wet_line_factory_pfd.png")
fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
