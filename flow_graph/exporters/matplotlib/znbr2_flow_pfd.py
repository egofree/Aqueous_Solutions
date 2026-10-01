#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""ZnBr2 flow battery PFD — graph-bridged IA-ESS-ZNBR2-* overlays.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
Charge/discharge IA-* labeled from graph; null rates stay null.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, mem_bar

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    load,
    znbr2_ess_bridge_edges,
)

_G = load()
_BR = znbr2_ess_bridge_edges(_G)
_GP = graph_path().name


C_AC = "#b45309"
C_DC = "#1e3a8a"
C_DC_F = "#dbeafe"
C_PV = "#15803d"
C_PV_F = "#dcfce7"
C_BR = "#6d28d9"
C_BR_F = "#ede9fe"
C_H2 = "#1e3a8a"

fig, ax = plt.subplots(figsize=(20.0, 26.0), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 99.2, "ZnBr2 FLOW BATTERY",
        ha="center", va="top", fontsize=18.0, fontweight="bold", color=P.INK)
ax.text(50, 97.0,
        f"Graph-bridged IA-ESS-ZNBR2-* from {_GP}  ·  null rates stay null",
        ha="center", va="top", fontsize=9.0, color=P.MUTED)
ax.text(50, 97.25,
        "330 cells  ·  600 V nom.  ·  100 A  ·  120 kWh   ·   SEM Tech CEM  ·   Br2 tower + regen (S69) · AQS-VENT-001",
        ha="center", va="top", fontsize=11.0, color=P.MUTED)

# inverter
inv = box(ax, 28.0, 88.4, 44.0, 6.6, C_PV_F, C_PV, "SOL-ARK  60K   BATTERY PORTS",
          "160-700 V DC    2 x 50 A    CAN BMS gateway", ts=13.0, ss=8.8)

# stack
stk = box(ax, 22.0, 68.2, 56.0, 16.4, C_DC_F, C_DC, "", "")
ax.text(50.0, 83.7, "STACK   330 cells series   0.25 m2   carbon-plastic bipolar",
        ha="center", va="top", fontsize=12.4, fontweight="bold", color=C_DC, zorder=4)

znc = box(ax, 24.0, 70.0, 20.0, 11.6, C_DC_F, C_DC, "Zn HALF",
          "charge: Zn2+ + 2e → Zn\ndischarge: reverse\ncarbon-plastic plate", ts=12.0, ss=8.2)
mem_bar(ax, 45.2, 70.0, 2.4, 11.6, "CEM")
aemstrip = box(ax, 47.6, 70.0, 1.6, 11.6, P.C_AEM_F, P.C_AEM, "", "")
ax.text(48.4, 75.8, "AEM", ha="center", va="center", fontsize=7.6,
        fontweight="bold", color=P.C_AEM, rotation=90, zorder=6)
brc = box(ax, 49.6, 70.0, 26.4, 11.6, C_BR_F, C_BR, "Br HALF",
          "charge: 2 Br- → Br2 + 2e\nBr2 + Br- → Br3- / complex\ncarbon felt", ts=12.0, ss=8.2)

arrow(ax, B(inv), T(stk), C_DC, lw=2.0)
slabel(ax, 51.2, 85.2, "100 A  at  60 kW", C_DC, ha="left", size=8.4)

# tanks
znt = box(ax, 3.0, 50.2, 28.0, 13.0, C_DC_F, C_DC, "Zn ANOLYTE TANK",
          "PP   1.2 m3\n2.1 M ZnBr2 + KCl\nfloating lid   H2 vent", ts=12.4, ss=8.4)
brt = box(ax, 69.0, 50.2, 28.0, 13.0, C_BR_F, C_BR, "Br CATHOLYTE TANK",
          "PVDF   1.2 m3\ncomplexed Br2 / Br3-\nfloating lid   Br2 vent", ts=12.4, ss=8.4)

pz = box(ax, 8.0, 40.6, 18.0, 6.8, C_DC_F, C_DC, "PUMP Zn",
         "PVDF mag-drive\n20 L/min", ts=11.4, ss=8.0)
pb = box(ax, 74.0, 40.6, 18.0, 6.8, C_BR_F, C_BR, "PUMP Br",
         "PVDF mag-drive\n20 L/min", ts=11.4, ss=8.0)

arrow(ax, B(znt), T(pz), C_DC, lw=1.5)
arrow(ax, B(brt), T(pb), C_BR, lw=1.5)
arrow(ax, R(pz), L(znc), C_DC, lw=1.5)
arrow(ax, L(pb), R(brc), C_BR, lw=1.5)
# returns
arrow(ax, L(znc), R(znt), C_DC, lw=1.2, ls="--")
arrow(ax, R(brc), L(brt), C_BR, lw=1.2, ls="--")
slabel(ax, 16.5, 64.6, "return", C_DC, size=8.0)
slabel(ax, 83.5, 64.6, "return", C_BR, size=8.0)

# charge / discharge notes
chg = box(ax, 34.0, 54.6, 32.0, 8.6, P.C_PROD_F, P.C_PROD, "CYCLE",
          "CHARGE  CC 100 A → CV 2.05 V/cell\nDISCHARGE  to 1.50 V/cell\nSTRIP  weekly to the floor",
          ts=12.2, ss=8.4)

# gas
brsc = box(ax, 69.0, 24.8, 28.0, 11.8, C_BR_F, C_BR, "Br2 SCRUB+REGEN",
           "PVDF packed tower\nBMED NaOH  5-10 L/min\nNaBr / NaOBr hold tank\nback to Br tank — not CRU",
           ts=12.0, ss=8.2)
h2d = box(ax, 3.0, 24.8, 28.0, 11.8, C_DC_F, C_DC, "H2 HEADER",
          "Zn-tank vent\nflame arrester\nto plant H2 tote\nN2 purge on alarm",
          ts=12.0, ss=8.2)
hold = box(ax, 36.5, 24.8, 27.0, 11.8, P.C_LE_F, P.C_LEACH, "DO NOT TIE",
           "Battery Br2 tower ≠ plant Cl2 tower\nShared NaOH supply only\nNo Salria in these tanks",
           ts=12.0, ss=8.2)

arrow(ax, B(brt), T(brsc), C_BR, lw=1.6)
arrow(ax, B(znt), T(h2d), C_DC, lw=1.6)
arrow(ax, L(brsc), (64.0, cy(brsc)), C_BR, lw=1.2, ls="--")
arrow(ax, (64.0, cy(brsc)), (64.0, brt[1]), C_BR, lw=1.2, ls="--")
arrow(ax, (64.0, brt[1]), B(brt), C_BR, lw=1.2, ls="--")
slabel(ax, 66.5, 38.5, "S69", C_BR, size=9.0)

# makeup
mk = box(ax, 3.0, 13.4, 28.0, 8.4, P.C_PROD_F, P.C_PROD, "MAKEUP",
         "Zn from EW-9\nQ4 water\nNaOH from BMED BASE", ts=11.8, ss=8.2)
bms = box(ax, 36.5, 13.4, 27.0, 8.4, P.C_SOL_F, P.C_SOLID, "BMS GATEWAY",
          "V, I, SOC, ORP, H2, Br2\nCAN to Sol-Ark\nflow-prove interlock", ts=11.8, ss=8.2)
intk = box(ax, 69.0, 13.4, 28.0, 8.4, P.C_SOL_F, P.C_SOLID, "INTERLOCKS OPEN DC",
           "no flow  ·  V out of 495-677\nBr2 high  ·  H2 high\nbund leak  ·  CEM dP",
           ts=11.4, ss=8.0)

arrow(ax, T(mk), B(h2d), C_DC, lw=1.1, ls="--")

ax.text(3.0, 11.3, "CHARGE / DISCHARGE / GAS", fontsize=12.2, fontweight="bold", color=P.INK)
ax.text(3.0, 10.2,
        "Charge plates zinc and stores bromine as Br3- plus the amine complex. Discharge dissolves the zinc and reduces the bromine.\n"
        "Capacity is the plated zinc (80 mAh/cm2 cap), not tank volume. Weekly strip to 1.50 V/cell so dendrites do not punch the CEM.\n"
        "Br2 vapour is an overcharge / hot-tank signal. It goes to its own PVDF tower on BMED NaOH; liquor returns as bromide.\n"
        "H2 is a corrosion / over-discharge signal on the zinc tank. Flame arrester, then the plant H2 header. Not the Br2 tower.\n"
        "Do not pulse this stack. Do not share liquor with Salria. CEM faces zinc; a thin AEM only wets the bromine face. Br2 end state = regen → pos. tank (S69, AQS-VENT-001); continuous outdoor dump is not design intent.",
        ha="left", va="top", fontsize=9.6, color=P.MUTED, linespacing=1.24)

ax.text(50.0, 0.35, P.NAMING_FOOT, ha="center", va="bottom", fontsize=7.4, color=P.MUTED)


_e_chg = _BR.get("ZNBR2_CHG")
_e_dis = _BR.get("ZNBR2_DIS")
ax.text(2.0, 5.4, f"GRAPH IA-ESS-ZNBR2-*  ({_GP})", fontsize=9.0, fontweight="bold", color=P.INK)
y = 4.5
for key in ("ZNBR2_CHG", "ZNBR2_DIS", "S69_BR2"):
    e = _BR.get(key)
    if e is None:
        continue
    ax.text(2.0, y, f"{e.stream_id}  {e.from_unit_id} → {e.to_unit_id}  ·  {edge_callout(e)}",
            fontsize=7.2, color=P.MUTED)
    y -= 0.85
if _e_chg is not None:
    slabel(ax, 70.0, 5.0, edge_callout(_e_chg), C_DC, size=7.4)
if _e_dis is not None:
    slabel(ax, 70.0, 3.6, edge_callout(_e_dis), C_DC, size=7.4)

plt.tight_layout(pad=0.25)
out = getattr(P, "OUT_BATTERY", P.ROOT / "znbr2_flow_pfd.png")
fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
