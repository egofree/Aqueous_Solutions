#!/usr/bin/env python3
"""OIL LINE detail sheet — graph-bridged IA-OIL-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
IA-OIL-01…03 / IA-OIL-Q1 + S67/S11 from graph; null rates stay null.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, hx_diamond

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
_IA = {e.stream_id: e for e in ia_edges("oil", _G)}
_SEC = sector_edge_map("oil", _G)
_GP = graph_path().name

fig, ax = plt.subplots(figsize=(20.0, 28.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 99.35, "OIL LINE  —  FLOAT · DRY · PYROLYZE · DISTILL",
        ha="center", va="top", fontsize=P.EW_FONT_TITLE, fontweight="bold", color=P.INK)
ax.text(50, 97.55,
        "Leach float + dense-plastic jumper at the head   ·   hydrocarbon cuts at the bottom   ·   NCG → AFTERBURNER → FLUE_CAP / CRYO (S67)",
        ha="center", va="top", fontsize=18.6, color=P.MUTED)
ax.text(50, 96.15,
        f"Graph-bridged IA-OIL-* from {_GP}  ·  null rates stay null  ·  no invented S##",
        ha="center", va="top", fontsize=14, color=P.MUTED)

# ── head stubs ───────────────────────────────────────────
leach = box(ax, 2.0, 91.35, 36.0, 4.7, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
            "FLOAT skim  →  this sheet", ts=20.5, ss=14.3)
split = box(ax, 62.0, 91.35, 36.0, 4.7, P.C_SOL_F, P.C_SOLID, P.NAME["screen"],
            "dense plastic jumper  →  DRYER", ts=20.5, ss=14.3)
ew = box(ax, 40.0, 91.35, 20.0, 4.7, P.C_SOL_F, P.C_SOLID, P.NAME["ew"],
         "stub only", ts=19.2, ss=13.6)

# ── trunk ────────────────────────────────────────────────
flt = box(ax, 22.0, 83.55, 56.0, 5.4, P.C_OIL_F, P.C_OIL, P.NAME["float"],
          "weir / DAF    light plastic · paper · wood · insulation fiber", ts=22, ss=14.9)
dry = box(ax, 22.0, 75.35, 56.0, 5.6, P.C_OIL_F, P.C_OIL, P.NAME["dryer"],
          f"paddle / belt    {P.DRYER_T} from HX-4 (Q3)    condensate → Q4", ts=22, ss=14.9)

arrow(ax, B(leach), (cx(flt) - 10, flt[1] + flt[3]), P.C_OIL, lw=1.9)
arrow(ax, B(split), (cx(flt) + 14, flt[1] + flt[3]), P.C_OIL, lw=1.9)
slabel(ax, 18.5, 89.55, "FLOAT", P.C_OIL, ha="left", size=9.4)
slabel(ax, 81.5, 89.55, "dense PE/PVC/PET", P.C_OIL, ha="right", size=9.4)
arrow(ax, B(flt), T(dry), P.C_OIL, lw=2.0)
if "IA-OIL-01" in _IA:
    slabel(ax, cx(dry), dry[1] - 0.55, edge_callout(_IA["IA-OIL-01"]), P.C_OIL, size=7.4)

# ── pyro internals ───────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (8.0, 55.15), 84.0, 17.6,
    boxstyle="round,pad=0.12,rounding_size=0.30",
    facecolor=P.C_OIL_F, edgecolor=P.C_OIL, linewidth=1.7, zorder=2,
))
ax.text(50.0, 72.15, P.NAME["pyro"], ha="center", va="top",
        fontsize=23.2, fontweight="bold", color=P.INK, zorder=4)
ax.text(50.0, 70.35, f"{P.PYRO_T}    coils heat the auger, not the charge directly    no FR-4 in this pipe",
        ha="center", va="top", fontsize=15.5, color=P.MUTED, zorder=4)

coil = box(ax, 10.2, 58.15, 16.4, 9.4, P.C_HEAT_F, P.C_HEAT, "INDUCTION\nCOILS",
           "outside Ti shell\npreferential coupling\nto iron auger", ts=18, ss=13.3)
shell = box(ax, 28.8, 58.15, 24.0, 9.4, P.C_SOL_F, P.C_SOLID, "Ti OUTER PIPE",
            "Grade 2 shell\nnot a liquor wall\ncharge is dry", ts=19.2, ss=13.6)
auger = box(ax, 55.0, 58.15, 24.0, 9.4, P.C_SOL_F, P.C_SOLID, "CAST-IRON\nCONICAL AUGER",
            "forced plug flow\nfractures polymer\n→ dirty crude", ts=18.9, ss=13.6)
outp = box(ax, 81.2, 58.15, 9.4, 9.4, P.C_OIL_F, P.C_OIL, "OUTLET\nPIPE",
           "smaller\nbore", ts=17.4, ss=13)
arrow(ax, R(coil), L(shell), P.C_HEAT, lw=1.5)
arrow(ax, R(shell), L(auger), P.C_SOLID, lw=1.5)
arrow(ax, R(auger), L(outp), P.C_OIL, lw=1.5)
arrow(ax, B(dry), (cx(shell), 72.75), P.C_OIL, lw=1.9)

# ── quench + still ───────────────────────────────────────
quen = box(ax, 8.0, 47.35, 40.0, 5.6, P.C_OIL_F, P.C_OIL, P.NAME["quench"],
           "direct oil quench    vapor down    NCG across", ts=21.1, ss=14.6)
dem = box(ax, 52.0, 47.35, 18.0, 5.6, P.C_SOL_F, P.C_SOLID, P.NAME["demister"],
          "mist to still", ts=19.5, ss=14)
ab = box(ax, 72.0, 47.35, 14.0, 5.6, P.C_HEAT_F, P.C_HEAT, P.NAME["afterburner"],
         "NCG + tars  Q1", ts=18.3, ss=13.3)
flue = box(ax, 87.5, 47.35, 10.5, 5.6, P.C_HEAT_F, P.C_HEAT, "FLUE_CAP",
           "S67→CRYO", ts=17.4, ss=12.7)

arrow(ax, (cx(outp), 58.15), (cx(quen) + 8, quen[1] + quen[3]), P.C_OIL, lw=1.8)
arrow(ax, R(quen), L(dem), P.C_OIL, lw=1.5)
arrow(ax, R(dem), L(ab), P.C_HEAT, lw=1.5, ls="--")
arrow(ax, R(ab), L(flue), P.C_HEAT, lw=1.4)
slabel(ax, 69.0, 50.15, P.NAME["ncg"], P.C_HEAT, size=8.6)
slabel(ax, 86.0, 53.5, "S67", P.C_HEAT, size=8.4)
if "IA-OIL-02" in _IA:
    slabel(ax, 50.0, 54.6, edge_callout(_IA["IA-OIL-02"]), P.C_OIL, size=7.2)
if "IA-OIL-03" in _IA:
    slabel(ax, cx(ab), ab[1] - 0.55, edge_callout(_IA["IA-OIL-03"]), P.C_HEAT, size=7.0)
if "IA-OIL-Q1" in _IA:
    slabel(ax, 86.0, 45.8, edge_callout(_IA["IA-OIL-Q1"]), P.C_HEAT, size=6.8)
if "S67" in _SEC:
    slabel(ax, 92.0, 54.2, edge_callout(_SEC["S67"]), P.C_HEAT, size=7.0)
if "S11" in _SEC:
    slabel(ax, 70.0, 54.2, edge_callout(_SEC["S11"]), P.C_OIL, size=6.8)

still = box(ax, 8.0, 32.55, 56.0, 12.2, P.C_OIL_F, P.C_OIL, "", "")
ax.text(36.0, 43.85, P.NAME["still"], ha="center", va="top",
        fontsize=22.3, fontweight="bold", color=P.INK, zorder=5)
ax.text(36.0, 42.05, "continuous packed / tray column    HX-3 reboiler from Q2",
        ha="center", va="top", fontsize=14.6, color=P.MUTED, zorder=5)

nap = box(ax, 10.2, 33.35, 12.2, 6.4, P.C_PROD_F, P.C_PROD, "C5–C10", "overhead", ts=18.6, ss=13.6)
mid = box(ax, 23.4, 33.35, 12.2, 6.4, P.C_PROD_F, P.C_PROD, "C11–C18", "side draw", ts=18.6, ss=13.6)
gas = box(ax, 36.6, 33.35, 12.2, 6.4, P.C_PROD_F, P.C_PROD, "C19–C28", "side draw", ts=18.6, ss=13.6)
res = box(ax, 49.8, 33.35, 12.2, 6.4, P.C_OIL_F, P.C_OIL, "C29+", "bottoms", ts=18.6, ss=13.6)

arrow(ax, B(quen), (cx(still), still[1] + still[3]), P.C_OIL, lw=1.8)
arrow(ax, B(dem), (still[0] + still[2] * 0.72, still[1] + still[3]), P.C_OIL, lw=1.4)

# heavies recycle
arrow(ax, (cx(res), res[1]), (5.2, res[1]), P.C_OIL, lw=1.35, ls="--")
arrow(ax, (5.2, res[1]), (5.2, 62.85), P.C_OIL, lw=1.35, ls="--")
arrow(ax, (5.2, 62.85), (8.0, 62.85), P.C_OIL, lw=1.35, ls="--")
slabel(ax, 5.4, 46.2, "heavies\nrecycle", P.C_OIL, ha="left", size=8.6)

# HX diamonds in the right gutter of still row
h4 = hx_diamond(ax, 93.4, 78.15, "HX-4", P.HX["HX-4"])
h1 = hx_diamond(ax, 93.4, 62.85, "HX-1", P.HX["HX-1"])
h2 = hx_diamond(ax, 93.4, 50.15, "HX-2", P.HX["HX-2"])
h3 = hx_diamond(ax, 93.4, 38.65, "HX-3", P.HX["HX-3"])
arrow(ax, (h4[0] - 1.8, h4[1]), R(dry), P.C_HEAT, lw=1.2, ls="--")
arrow(ax, (coil[0] + coil[2], cy(coil)), (h1[0] - 1.8, h1[1]), P.C_HEAT, lw=1.2, ls="--")
arrow(ax, B(ab), (cx(ab), 45.5), P.C_HEAT, lw=1.1, ls="--")
arrow(ax, (cx(ab), 45.5), (h2[0] - 1.8, h2[1]), P.C_HEAT, lw=1.1, ls="--")
arrow(ax, (h3[0] - 1.8, h3[1]), R(still), P.C_HEAT, lw=1.2, ls="--")

# ── products ─────────────────────────────────────────────
p1 = box(ax, 2.0, 19.35, 22.6, 9.4, P.C_PROD_F, P.C_PROD, P.NAME["naphtha"],
         "solvents\ncracking feed\n→ new monomers", ts=20.2, ss=14.3)
p2 = box(ax, 26.6, 19.35, 22.6, 9.4, P.C_PROD_F, P.C_PROD, P.NAME["midcut"],
         "diesel-range\n→ polymer oil\n→ resins", ts=20.2, ss=14.3)
p3 = box(ax, 51.2, 19.35, 22.6, 9.4, P.C_PROD_F, P.C_PROD, P.NAME["gasoil"],
         "wax / lube cut\n→ polyolefins\nfeed", ts=20.2, ss=14.3)
p4 = box(ax, 75.8, 19.35, 22.2, 9.4, P.C_SOL_F, P.C_SOLID, P.NAME["char"],
         "inorganics that\nrode the float\n→ GLASS BRANCH mill", ts=20.2, ss=14)

arrow(ax, B(nap), T(p1), P.C_PROD, lw=1.6)
arrow(ax, B(mid), T(p2), P.C_PROD, lw=1.6)
arrow(ax, B(gas), T(p3), P.C_PROD, lw=1.6)

# glass stub
gstub = box(ax, 75.8, 12.55, 22.2, 4.4, P.C_IN_F, P.C_INORG, P.NAME["glass"],
            "char / grit handoff", ts=18.6, ss=13.3)
arrow(ax, B(p4), T(gstub), P.C_INORG, lw=1.3, ls="--")

# notes
ax.text(2.0, 16.55, "HARDWARE  /  RULES", fontsize=18.9, fontweight="bold", color=P.INK)
ax.text(2.0, 15.65,
        "Shell is titanium because it is dry and hot — not because it sees Salria.  Liquor never enters this pipe.\n"
        "Cast-iron conical auger is the susceptor.  Induction coils sit on the outside of the Ti shell and couple to the iron.\n"
        "Paper, wood, and fiber insulation ride the float and are tolerated.  FR-4 and glass do not.  Those leave at VIBRATORY SPLIT.\n"
        "Afterburner flue jackets the glass-line BURNOUT ROTARY (HX-7).  Atmospheres stay separate — oil vapor does not enter the rotary.\n""Flue products → FLUE_CAP / CRYO (S67 extends S18); condensate S68 → S13 class.  Continuous outdoor dump is not design intent (AQS-VENT-001).\n"
        "HX-4 dryer takes Q3 (80–120 °C) including EW reject.  If pyro is down the dryer can still run on EW heat.",
        ha="left", va="top", fontsize=15.5, color=P.MUTED, linespacing=1.28)


_reg = ia_register_lines(list(_IA.values()) + [e for sid, e in sorted(_SEC.items()) if not sid.startswith("IA-")])
ax.text(2.0, 8.55, f"GRAPH IA-OIL-* / S##  ({_GP})", fontsize=14, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(2.0, 7.75 - i * 0.55, line, ha="left", va="top", fontsize=10.5, color=P.MUTED)

ax.text(50.0, 0.35, P.NAMING_FOOT + "    OIL LINE    graph-bridged", ha="center", va="bottom",
        fontsize=P.EW_FONT_FOOT, color=P.MUTED)

plt.tight_layout(pad=0.22)
fig.savefig(P.OUT_OIL, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_OIL)
