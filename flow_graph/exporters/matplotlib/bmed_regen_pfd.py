#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""BMED REGEN detail sheet — graph-bridged IA-BMED-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
IA-BMED-01…04 from graph; null rates stay null. No invented S##.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
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
_IA = {e.stream_id: e for e in ia_edges("bmed", _G)}
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(20.0, 28.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 99.35, "BMED REGEN  —  BRINE  →  HCl  +  NaOH  +  CHLORATE",
        ha="center", va="top", fontsize=28.8, fontweight="bold", color=P.INK)
ax.text(50, 97.55,
        "3-compartment stack   ·   CEM blue   ·   AEM orange   ·   BPM blue|orange   ·   polymer chambers, not titanium",
        ha="center", va="top", fontsize=18, color=P.MUTED)
ax.text(50, 96.15,
        f"Graph-bridged IA-BMED-* from {_GP}  ·  null rates stay null  ·  no invented S##",
        ha="center", va="top", fontsize=14, color=P.MUTED)

# ── feed stubs ───────────────────────────────────────────
ew = box(ax, 2.0, 91.45, 23.6, 4.6, P.C_SOL_F, P.C_SOLID, P.NAME["ew"],
         "depleted catholyte / polish brine", ts=19.2, ss=13.3)
pol = box(ax, 26.8, 91.45, 22.4, 4.6, P.C_SOL_F, P.C_SOLID, P.NAME["polish"],
          "spent polish liquor", ts=19.2, ss=13.3)
gls = box(ax, 50.4, 91.45, 23.6, 4.6, P.C_IN_F, P.C_INORG, P.NAME["glass"],
          "Br- / HCl condensate", ts=19.2, ss=13.3)
rin = box(ax, 75.2, 91.45, 22.8, 4.6, P.C_LE_F, P.C_LEACH, P.NAME["wash"],
          "rinse liquor", ts=19.2, ss=13.3)

salt = box(ax, 18.0, 83.85, 64.0, 5.2, P.C_SOL_F, P.C_SOLID, P.NAME["salt_feed"],
           "NaCl + residual cations    wall PP / CPVC    Q4 condensate as makeup water",
           ts=21.7, ss=14.6)
arrow(ax, B(ew), (cx(salt) - 18, salt[1] + salt[3]), P.C_LEACH, lw=1.5)
arrow(ax, B(pol), (cx(salt) - 6, salt[1] + salt[3]), P.C_LEACH, lw=1.5)
arrow(ax, B(gls), (cx(salt) + 8, salt[1] + salt[3]), P.C_LEACH, lw=1.5)
arrow(ax, B(rin), (cx(salt) + 18, salt[1] + salt[3]), P.C_LEACH, lw=1.5)

# ── stack frame ──────────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (2.0, 52.15), 96.0, 29.3,
    boxstyle="round,pad=0.14,rounding_size=0.32",
    facecolor="#ecfdf5", edgecolor=P.C_LEACH, linewidth=1.7, zorder=2,
))
ax.text(50.0, 81.15, "ONE REPEATING UNIT",
        ha="center", va="top", fontsize=21.1, fontweight="bold", color=P.C_LEACH, zorder=4)
ax.text(50.0, 79.45, "n cells in series on a common DC bus     ·     Na+ left through CEM     ·     Cl- right through AEM",
        ha="center", va="top", fontsize=15.5, color=P.MUTED, zorder=4)

BY, BH = 54.85, 19.6
units = [
    ("cath", 8.4),
    ("bpm1", 3.2),
    ("base", 16.2),
    ("cem", 3.0),
    ("saltc", 18.0),
    ("aem", 3.0),
    ("acid", 16.2),
    ("bpm2", 3.2),
    ("anod", 8.4),
]
gap = 0.38
total_w = sum(w for _, w in units) + gap * (len(units) - 1)
x0 = 50.0 - total_w / 2
xs, x = [], x0
for name, w in units:
    xs.append((name, x, w))
    x += w + gap


def ch_box(x, y, w, h, fill, edge, t1, t2, t3="", ts=18.9, ss=13.3):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge,
                           linewidth=1.4, zorder=4))
    ax.text(x + w / 2, y + h * 0.78, t1, ha="center", va="center",
            fontsize=ts, fontweight="bold", color=P.INK, zorder=5)
    ax.text(x + w / 2, y + h * 0.50, t2, ha="center", va="center",
            fontsize=ss, color=P.MUTED, zorder=5, linespacing=1.08)
    if t3:
        ax.text(x + w / 2, y + h * 0.22, t3, ha="center", va="center",
                fontsize=ss, color=P.MUTED, zorder=5, linespacing=1.08)


pos = {}
for name, x, w in xs:
    pos[name] = (x, w)
    if name == "cath":
        ch_box(x, BY, w, BH, P.C_CA_F, P.C_CEM, "CATHODE", P.BMED_CATHODE, "H2 out")
    elif name == "bpm1":
        mem_bar(ax, x, BY, w, BH, "BPM_BO")
    elif name == "base":
        ch_box(x, BY, w, BH, P.C_LE_F, P.C_LEACH, "BASE", "NaOH", f"wall {P.WALL['bmed_base']}")
    elif name == "cem":
        mem_bar(ax, x, BY, w, BH, "CEM")
    elif name == "saltc":
        ch_box(x, BY, w, BH, P.C_SOL_F, P.C_SOLID, "SALT", "NaCl brine", f"wall {P.WALL['bmed_salt']}")
    elif name == "aem":
        mem_bar(ax, x, BY, w, BH, "AEM")
    elif name == "acid":
        ch_box(x, BY, w, BH, P.C_AN_F, P.C_AN, "ACID", "HCl", f"wall {P.WALL['bmed_acid']}")
    elif name == "bpm2":
        mem_bar(ax, x, BY, w, BH, "BPM_BO")
    elif name == "anod":
        ch_box(x, BY, w, BH, P.C_AN_F, P.C_AN, "ANODE", "Ti Gr.2 / MMO", "O2 / Cl2")

# ion callouts under chambers
bx, bw = pos["base"]
sx, sw = pos["saltc"]
ax_, aw = pos["acid"]
ax.text(bx + bw / 2, BY - 0.55, "OH- from BPM  +  Na+ through CEM",
        ha="center", va="top", fontsize=13.3, color=P.C_LEACH, zorder=5)
ax.text(sx + sw / 2, BY - 0.55, "depleted brine recycled to SALT FEED",
        ha="center", va="top", fontsize=13.3, color=P.MUTED, zorder=5)
ax.text(ax_ + aw / 2, BY - 0.55, "H+ from BPM  +  Cl- through AEM",
        ha="center", va="top", fontsize=13.3, color=P.C_AN, zorder=5)

ax.text(50.0, 52.55,
        "BPM facing:  CEL (blue) toward cathode     ·     AEL (orange) toward anode     ·     H+ leaves CEL, OH- leaves AEL",
        ha="center", va="bottom", fontsize=14, color=P.MUTED, zorder=5)

# salt feed down into salt chamber
arrow(ax, B(salt), (sx + sw / 2, BY + BH), P.C_SOLID, lw=1.8)

# ── product tanks ────────────────────────────────────────
base_t = box(ax, 2.0, 39.55, 30.4, 8.6, P.C_LE_F, P.C_LEACH, P.NAME["base_tank"],
             f"from BASE chamber\nwall {P.WALL['bmed_base']}", ts=21.1, ss=14.6)
acid_t = box(ax, 34.8, 39.55, 30.4, 8.6, P.C_AN_F, P.C_AN, P.NAME["acid_tank"],
             f"from ACID chamber\nwall {P.WALL['bmed_acid']}", ts=21.1, ss=14.6)
cru = box(ax, 67.6, 39.55, 30.4, 8.6, P.C_HEAT_F, P.C_HEAT, P.NAME["cru"],
          "Cl2 (anode + EW anolyte)\nabsorbed into NaOH / brine\n→ NaClO3", ts=20.5, ss=14)

arrow(ax, (bx + bw / 2, BY), T(base_t), P.C_LEACH, lw=1.8)
arrow(ax, (ax_ + aw / 2, BY), T(acid_t), P.C_AN, lw=1.8)
if "IA-BMED-02" in _IA:
    slabel(ax, cx(base_t), base_t[1] + base_t[3] + 0.35, edge_callout(_IA["IA-BMED-02"]), P.C_LEACH, size=7.4)
if "IA-BMED-01" in _IA:
    slabel(ax, cx(acid_t), acid_t[1] + acid_t[3] + 0.35, edge_callout(_IA["IA-BMED-01"]), P.C_AN, size=7.4)

arrow(ax, (pos["anod"][0] + pos["anod"][1] / 2, BY), (cx(cru), cru[1] + cru[3]), P.C_HEAT, lw=1.5, ls="--")
slabel(ax, 88.4, 51.15, "Cl2", P.C_HEAT, ha="left", size=9.0)

# NaOH tap to CRU
arrow(ax, (base_t[0] + base_t[2], base_t[1] + 1.1), (cru[0], cru[1] + 1.1), P.C_LEACH, lw=1.3, ls="--")
slabel(ax, 66.0, 40.15, "NaOH → CRU", P.C_LEACH, size=8.4)
if "IA-BMED-03" in _IA:
    slabel(ax, cx(cru), cru[1] - 0.45, edge_callout(_IA["IA-BMED-03"]), P.C_HEAT, size=7.2)
if "IA-BMED-04" in _IA:
    slabel(ax, cx(cru) + 10.0, cru[1] - 0.45, edge_callout(_IA["IA-BMED-04"]), P.C_HEAT, size=7.2)


# ── destinations ─────────────────────────────────────────
pal = box(ax, 2.0, 26.55, 15.0, 9.4, P.C_IN_F, P.C_INORG, "P-Al",
          "pH 5.0–5.5", ts=19.5, ss=13.6)
pmg = box(ax, 18.2, 26.55, 15.0, 9.4, P.C_IN_F, P.C_INORG, "P-Mg",
          "pH 10.5–11", ts=19.5, ss=13.6)
pca = box(ax, 34.4, 26.55, 15.0, 9.4, P.C_IN_F, P.C_INORG, "P-Ca",
          "pH 12–12.5", ts=19.5, ss=13.6)
dig = box(ax, 50.6, 26.55, 15.0, 9.4, P.C_IN_F, P.C_INORG, P.NAME["digest"],
          "glass line", ts=18, ss=13.3)
reg = box(ax, 67.6, 26.55, 15.0, 9.4, P.C_LE_F, P.C_LEACH, P.NAME["regen"],
          "HCl + chlorate", ts=18.3, ss=13.3)
l1 = box(ax, 83.8, 26.55, 14.2, 9.4, P.C_LE_F, P.C_LEACH, P.NAME["leach1"],
         "oxidative leach", ts=18, ss=13.3)

arrow(ax, (cx(base_t) - 8, base_t[1]), T(pal), P.C_LEACH, lw=1.45)
arrow(ax, (cx(base_t), base_t[1]), T(pmg), P.C_LEACH, lw=1.45)
arrow(ax, (cx(base_t) + 8, base_t[1]), T(pca), P.C_LEACH, lw=1.45)
arrow(ax, (base_t[0] + base_t[2] * 0.85, base_t[1]), T(dig), P.C_LEACH, lw=1.45)
arrow(ax, B(acid_t), T(reg), P.C_AN, lw=1.55)
arrow(ax, B(cru), T(reg), P.C_HEAT, lw=1.35, ls="--")
arrow(ax, R(reg), L(l1), P.C_LEACH, lw=1.45)

# ── products ─────────────────────────────────────────────
hyd = box(ax, 2.0, 14.15, 30.4, 9.2, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "Al / Mg / Ca cakes\nfrom pH-shift + digest", ts=21.1, ss=14.6)
hcl = box(ax, 34.8, 14.15, 30.4, 9.2, P.C_PROD_F, P.C_PROD, "HCl  +  NaClO3",
          "REGEN LEACH\nback to LEACH CSTR 1", ts=21.1, ss=14.6)
h2 = box(ax, 67.6, 14.15, 30.4, 9.2, P.C_PROD_F, P.C_PROD, "H2  /  O2",
         "cathode H2    anode O2\nto gas / cryo sheet", ts=21.1, ss=14.6)

arrow(ax, B(pal), (hyd[0] + 5, hyd[1] + hyd[3]), P.C_INORG, lw=1.3)
arrow(ax, B(pmg), T(hyd), P.C_INORG, lw=1.3)
arrow(ax, B(pca), (hyd[0] + hyd[2] - 5, hyd[1] + hyd[3]), P.C_INORG, lw=1.3)
arrow(ax, B(reg), T(hcl), P.C_LEACH, lw=1.5)
arrow(ax, (98.2, 65.5), (98.2, cy(h2)), P.C_CA, lw=1.15, ls="--")
arrow(ax, (98.2, cy(h2)), R(h2), P.C_CA, lw=1.15, ls="--")
slabel(ax, 97.4, 65.7, "H2", P.C_CA, ha="right", size=8.4)

# ── notes ────────────────────────────────────────────────
ax.text(2.0, 12.35, "MEMBRANES  /  WALLS  /  RULES", fontsize=18.9, fontweight="bold", color=P.INK)
ax.add_patch(Rectangle((2.0, 9.85), 3.2, 1.55, facecolor=P.C_CEM_F, edgecolor=P.C_CEM, lw=1.2))
ax.text(5.5, 10.62, "CEM   sulfonated PS–PVC on PP felt, double-layer, hot-swap",
        ha="left", va="center", fontsize=15.5, color=P.MUTED)
ax.add_patch(Rectangle((2.0, 7.85), 3.2, 1.55, facecolor=P.C_AEM_F, edgecolor=P.C_AEM, lw=1.2))
ax.text(5.5, 8.62, "AEM   aminated PS–PVC on PP felt",
        ha="left", va="center", fontsize=15.5, color=P.MUTED)
ax.add_patch(Rectangle((2.0, 5.85), 1.6, 1.55, facecolor=P.C_CEM_F, edgecolor=P.C_CEM, lw=1.2))
ax.add_patch(Rectangle((3.6, 5.85), 1.6, 1.55, facecolor=P.C_AEM_F, edgecolor=P.C_AEM, lw=1.2))
ax.text(5.5, 6.62, "BPM   CEL left (cathode) | AEL right (anode).  Water splits at the junction.",
        ha="left", va="center", fontsize=15.5, color=P.MUTED)

ax.text(2.0, 4.85,
        f"BASE chambers: {P.WALL['bmed_base']}.  ACID chambers: {P.WALL['bmed_acid']}.  "
        f"SALT: {P.WALL['bmed_salt']}.  PVDF is wrong for hot NaOH; PP is wrong for hot oxidizer.\n"
        "Chlorate is not made inside the BMED stack.  Cl2 from the BMED anode and the EW SALRIA ANOLYTE LOOP is absorbed in the CRU.\n"
        "Q4 condensate is the water that BPM splits.  Do not feed Salria solids into this stack — brine is filtered first.",
        ha="left", va="top", fontsize=15.2, color=P.MUTED, linespacing=1.26)

_reg = ia_register_lines(_IA.values())
ax.text(50.0, 3.85, f"GRAPH IA-BMED-*  ({_GP})", ha="center", fontsize=14, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(50.0, 3.15 - i * 0.55, line, ha="center", va="top", fontsize=10.5, color=P.MUTED)

ax.text(50.0, 0.35, P.NAMING_FOOT, ha="center", va="bottom",
        fontsize=P.EW_FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.22)
fig.savefig(P.OUT_BMED, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_BMED)
