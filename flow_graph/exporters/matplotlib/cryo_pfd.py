#!/usr/bin/env python3
"""AQS-PFD-CRY-001 — CRYO / ALCRM cold-box internals + Q4/HVAC hooks.

Authority: AQS-CRY-002, AQS-EQP-CRY-001, doc 09, freecad/cryo.py,
STREAM_REGISTER S02–S05/S18/S24/S45/S49–S50/S54–S56/S64/S67/S70. AQS-VENT-001.
COLD BOX internals on L-1 east of CORE. Not the ZnBr2 Br₂ tower.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
from matplotlib.patches import FancyBboxPatch
import sector_style as S

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)


DOC = "AQS-PFD-CRY-001"
FNAME = "cryo_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("cryo", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 13.5)
    S.title_block(
        ax, DOC, "CRYO  /  ALCRM  COLD BOX",
        "Intake → Stirling 77–90 K + distillation  →  CRYO H2/O2/N2/CO2  ·  "
        "Q4 / dedicated cool / AHU condensable return  ·  L-1 east of CORE",
    )

    S.rule(ax, 2, 64.5, 96, 3.0,
           "RULE  ·  CRYO H2 ≠ HDR_H2.  Acid-gas / oil / Br₂ never enter COLD BOX.  "
           "No shared HVAC return HAB↔CRYO.  Doc 09 kW = narrative only (duties TBD).")

    # ---- Intake train ----
    ax.text(2, 62.0, "1   INTAKE  (doc 09 §2.2)",
            fontsize=14, fontweight="bold", color="#1c1917")
    intake = S.unit(ax, 2, 52, 13, 7.5, "AIR_INTAKE",
                    "centrifugal +\ndemister", fill="#e4e4e7", edge="#3f3f46")
    sieve = S.unit(ax, 17, 52, 13, 7.5, "MOL_SIEVE",
                   "CO₂ / H₂O\n5Å TSA", fill="#e0f2fe", edge="#0369a1")
    hepa = S.unit(ax, 32, 52, 12, 7.5, "HEPA_BANK",
                  "final polish\nparticulate", fill="#e0f2fe", edge="#0369a1")
    arrow(ax, R(intake), L(sieve), S.C_SCRAP, lw=1.5)
    arrow(ax, R(sieve), L(hepa), S.C_UTIL, lw=1.5)
    slabel(ax, 15.5, 60.2, "ambient", S.C_SCRAP, size=6.6)

    # Side feeds
    h2d = S.iface(ax, 2, 41, 13, 6.5, "H2_DRYER",
                  "S05 process H₂\ndried · arrestor", fill="#dbeafe", edge="#1e3a8a")
    flue = S.iface(ax, 17, 41, 13, 6.5, "FLUE CAP",
                   "S18 / S67 CO₂\nclosure path", fill="#ffedd5", edge="#9a3412")

    # ---- Cold box parent with internals ----
    ax.text(47, 62.0, "2   COLD BOX INTERNALS",
            fontsize=14, fontweight="bold", color="#1c1917")
    # Parent outline
    ax.add_patch(FancyBboxPatch(
        (46, 38.5), 30, 22.5,
        boxstyle="round,pad=0.1,rounding_size=0.25",
        facecolor="#f0f9ff", edgecolor="#0284c7", linewidth=2.0, zorder=2,
        linestyle="-"))
    ax.text(61, 59.8, "COLD_BOX", ha="center", fontsize=16.3,
            fontweight="bold", color="#0369a1", zorder=4)

    stir = S.unit(ax, 47.5, 51.5, 13, 6.5, "STIRLING",
                  "cold-head\n77–90 K", fill="#dbeafe", edge="#1e40af", ts=14.7, ss=10.5)
    dist = S.unit(ax, 62, 51.5, 12.5, 6.5, "DIST COLS",
                  "PRI / SEC / TER\n+ PSA class", fill="#e0f2fe", edge="#0369a1", ts=14.7, ss=10.5)
    reb = S.unit(ax, 47.5, 43.5, 13, 6.0, "REBOILER_COND",
                 "HX integration\nduty TBD", fill="#ffedd5", edge="#c2410c", ts=14, ss=10.2)
    comp = S.unit(ax, 62, 43.5, 12.5, 6.0, "COMP_EXPAND",
                  "VFD compressors\n+ expanders", fill="#e0f2fe", edge="#0369a1", ts=14, ss=10.2)

    # Feeds into cold box
    arrow(ax, R(hepa), (45.5, cy(hepa)), S.C_UTIL, lw=1.6)
    arrow(ax, (45.5, cy(hepa)), (46, cy(stir)), S.C_UTIL, lw=1.6)
    arrow(ax, R(h2d), (45.5, cy(h2d)), S.C_H2, lw=1.5)
    arrow(ax, (45.5, cy(h2d)), (46, cy(reb) + 1), S.C_H2, lw=1.5)
    slabel(ax, 40, 48.5, "S05 / S64", S.C_H2, size=7.0)
    arrow(ax, R(flue), (45.5, cy(flue) - 1), S.C_ORG, lw=1.2, ls="--")
    arrow(ax, (45.5, cy(flue) - 1), (46, reb[1] + 0.8), S.C_ORG, lw=1.2, ls="--")
    slabel(ax, 39, 40.5, "S18/S67", S.C_ORG, size=6.4)

    # ---- Product receivers ----
    ax.text(78, 62.0, "3   RECEIVERS",
            fontsize=14, fontweight="bold", color="#1c1917")
    o2 = S.unit(ax, 79, 55, 18, 5.0, "CRYO_O2",
                "→ HDR_O2 S02 · FC S50", fill="#ccfbf1", edge="#115e59", ts=14.7, ss=10.2)
    n2 = S.unit(ax, 79, 48.5, 18, 5.0, "CRYO_N2",
                "→ HDR_N2 · S03", fill="#dbeafe", edge="#1d4ed8", ts=14.7, ss=10.2)
    co2 = S.unit(ax, 79, 42, 18, 5.0, "CRYO_CO2",
                 "→ HDR_CO2 · S04", fill="#ffedd5", edge="#c2410c", ts=14.7, ss=10.2)
    h2 = S.unit(ax, 79, 35.5, 18, 5.0, "CRYO_H2",
                "hold / fuel · ≠ HDR_H2", fill="#dbeafe", edge="#1e3a8a", ts=14.7, ss=10.2)

    for dst, col in ((o2, S.C_PRODUCT), (n2, S.C_UTIL), (co2, S.C_HVAC), (h2, S.C_H2)):
        arrow(ax, (76.5, cy(dst)), L(dst), col, lw=1.35)

    # VJ note
    slabel(ax, 70, 39.0, "VJ_LINES", S.C_UTIL, size=6.4)

    # ---- Consumers from CRYO_H2 ----
    ax.text(2, 37.5, "4   CRYO_H2 CONSUMERS  (size hold for all three)",
            fontsize=14, fontweight="bold", color="#1c1917")
    gen = S.iface(ax, 2, 28, 16, 6.5, "BACKUP_GEN",
                  "S45 · GEN port\nAQS-PWR-001", fill="#fef3c7", edge="#b45309")
    fc = S.iface(ax, 21, 28, 16, 6.5, "FUEL_CELL",
                 "S49 · BATT DC\nAQS-FC-001", fill="#dbeafe", edge="#1e3a8a")
    vent = S.iface(ax, 40, 28, 16, 6.5, "S24 CONTINGENCY",
                   "roof relief only\nnot design dump", fill="#fee2e2", edge="#b91c1c")
    # From CRYO_H2 down
    arrow(ax, (cx(h2), h2[1]), (cx(h2), 35.0), S.C_H2, lw=1.3)
    arrow(ax, (cx(h2), 35.0), (cx(gen), 35.0), S.C_H2, lw=1.2, ls="--")
    arrow(ax, (cx(gen), 35.0), T(gen), S.C_H2, lw=1.3)
    arrow(ax, (cx(h2), 35.0), (cx(fc), 35.0), S.C_H2, lw=1.2)
    arrow(ax, (cx(fc), 35.0), T(fc), S.C_H2, lw=1.3)
    arrow(ax, (cx(h2), 35.0), (cx(vent), 35.0), S.C_H2, lw=1.1, ls=":")
    arrow(ax, (cx(vent), 35.0), T(vent), S.C_H2, lw=1.2, ls=":")
    slabel(ax, 70, 33.2, "S64→S45/S49; S24 relief", S.C_H2, size=6.4)
    # O2 to FC
    arrow(ax, (o2[0] - 1.5, cy(o2)), (o2[0] - 1.5, 34.5), S.C_PRODUCT, lw=1.0, ls="--")
    arrow(ax, (o2[0] - 1.5, 34.5), (fc[0] + fc[2], cy(fc) + 1.5), S.C_PRODUCT, lw=1.0, ls="--")
    slabel(ax, 55, 33.2, "S50 O₂→FC", S.C_PRODUCT, size=6.2)

    # ---- Heat / HVAC ----
    ax.text(58, 37.5, "5   HEAT REJECTION / HVAC",
            fontsize=14, fontweight="bold", color="#1c1917")
    hx = S.unit(ax, 58, 28, 14, 6.5, "CRYO_HX_Q4",
                "warm residual\n→ Q4  S54", fill="#ffedd5", edge="#c2410c", ts=14.7, ss=10.2)
    ded = S.unit(ax, 74, 28, 12, 6.5, "CRYO_DED_COOL",
                 "Stirling/deep\nS55 dedicated", fill="#e0f2fe", edge="#0369a1", ts=14, ss=9.9)
    ahu = S.unit(ax, 88, 28, 10, 6.5, "CRYO_AHU",
                 "COND→S70\nS56 residual", fill="#e0f2fe", edge="#0369a1", ts=14, ss=9.9)
    q4 = S.iface(ax, 58, 18.5, 14, 6.0, "Q4 HEADER",
                 "S06 / S44 / S53\n+ S54 peer", fill="#ffedd5", edge="#9a3412")
    arrow(ax, B(hx), T(q4), S.C_HVAC, lw=1.6)
    slabel(ax, 66, 26.5, "S54", S.C_HVAC, size=7.0)
    # From cold box heat sources
    arrow(ax, B(reb), (cx(hx), 38.5), S.C_HVAC, lw=1.1, ls="--")
    arrow(ax, (cx(hx), 38.5), T(hx), S.C_HVAC, lw=1.1, ls="--")
    arrow(ax, B(stir), (cx(ded), 38.5), S.C_UTIL, lw=1.1, ls="--")
    arrow(ax, (cx(ded), 38.5), T(ded), S.C_UTIL, lw=1.1, ls="--")

    # ZnBr2 keep-out
    S.iface(ax, 2, 18.5, 20, 6.0, "ZNBR2 Br₂ TOWER",
            "outdoor · regen S69 · NOT this skid", fill="#e4e4e7", edge="#57534e")

    # Callouts
    S.callout(ax, 24, 10.5, 36, 14.5, "HVAC / GEO / Q4 SPLIT (AQS-CRY-002)", [
        "S54 CRYO_HX_Q4 → Q4: warm residual < 80 °C only.",
        "S55 CRYO_DED_COOL: Stirling + deep reject (not life air).",
        "S70 CRYO_AHU_COND → COLD_BOX; S56 residual only; no HAB return.",
        "Peers: GEO_HP S44, FC_HX_Q4 S53, HVAC S06.",
        "FB_CRYO_PROCESS 2 h; no process-air duct through.",
    ], fill="#fff7ed", edge="#c2410c")
    S.callout(ax, 62, 10.5, 36, 14.5, "MACHINE LIST / LOCATION", [
        "COLD_BOX children: STIRLING, DIST_COL_*, REBOILER_COND,",
        "  COMP_EXPAND, MOL_SIEVE, HEPA, CRYO_HX_Q4, CRYO_DED_COOL, CRYO_AHU_COND",
        "Receivers: CRYO_H2/O2/N2/CO2  (freecad/cryo.py stubs)",
        "Detail: docs-authority/CRYO_COLD_BOX.md + process/CRYO_EQUIPMENT.md",
        "L-1 east of CORE; plant.FCStd rebuild to show children.",
    ], fill="#e0f2fe", edge="#0284c7")

    S.legend(ax, 2.0, 1.5)
    S.graph_bridge_note(ax, _GP, "S02–S05/S18/S54–S56/S64/S67–S68/S70")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — cryo", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-CRY-002 / AQS-VENT-001 / AQS-EQP-CRY-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
