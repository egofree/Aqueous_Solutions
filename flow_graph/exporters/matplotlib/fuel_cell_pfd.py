#!/usr/bin/env python3
"""AQS-PFD-FC-001 — PEM fuel cell on Sol-Ark BATT DC; heat → Q4.

Authority: AQS-FC-001, AQS-EQP-FC-001, ELECTRICAL.md (BATT DC 160–700 V),
POWER overview (legacy PEM narrative), AQS-STR-001 S49–S53/S64, AQS-VENT-001.
FC ≠ BACKUP_GEN (GEN port). REQ-FC-CONT ≈ 4 kW_dc; MeOH peer issued.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
import sector_style as S

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)


DOC = "AQS-PFD-FC-001"
FNAME = "fuel_cell_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("fuel_cell", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "PEM FUEL CELL",
        "Plant H₂ + O₂ → FUEL_CELL → Sol-Ark BATT DC  ·  heat → Q4 via FC_HX  ·  ≠ BACKUP_GEN  ·  L0 POWER yard",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  Chemistry = PEM (plant H₂ + O₂).  MeOH DMFC deferred.  "
           "FC → BATT DC only — not GEN port, not RECT process DC.  kW TBD.")

    ax.text(2, 59.0, "1   FUEL / OXIDIZER  (on-site streams)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    h2d = S.unit(ax, 2, 48, 16, 8.0, "H2_DRYER",
                 "process H₂\nS05 / S24",
                 fill="#dbeafe", edge="#1e3a8a")
    cryo_h = S.unit(ax, 20, 48, 16, 8.0, "CRYO_H2",
                    "product hold\n≠ HDR_H2",
                    fill="#dbeafe", edge="#1e3a8a")
    cryo_o = S.unit(ax, 38, 48, 16, 8.0, "CRYO_O2",
                    "oxidizer\nS02 class",
                    fill="#ffedd5", edge="#c2410c")
    man_h = S.unit(ax, 56, 49, 14, 6.5, "FC_H2_MANIFOLD",
                   "S49 + arrestor\nMAQ / NFPA 2",
                   fill="#e0f2fe", edge="#0369a1", ts=14.9, ss=10.5)
    man_o = S.unit(ax, 56, 41.5, 14, 6.0, "FC_O2_MANIFOLD",
                   "S50 oxidizer\nkeep ≠ H₂",
                   fill="#ffedd5", edge="#c2410c", ts=14.9, ss=10.5)
    fc = S.unit(ax, 74, 44, 24, 13.0, "FUEL_CELL",
                "PEM stack(s)\nH₂ + O₂ → DC + heat + H₂O\nkW TBD (≤ Sol-Ark / ZnBr2 class)",
                fill="#fef3c7", edge="#b45309", ts=17.7, ss=11.2)
    arrow(ax, R(h2d), L(man_h), S.C_H2, lw=1.4)
    arrow(ax, R(cryo_h), (man_h[0], cy(cryo_h)), S.C_H2, lw=1.4)
    arrow(ax, R(cryo_o), (man_o[0], cy(cryo_o)), S.C_OX, lw=1.4)
    arrow(ax, R(man_h), (fc[0], cy(man_h)), S.C_H2, lw=1.7)
    arrow(ax, R(man_o), (fc[0], cy(man_o)), S.C_OX, lw=1.7)
    slabel(ax, 16, 57.5, "S64", S.C_H2, size=7.0)
    slabel(ax, 50, 57.5, "S49", S.C_H2, size=7.4)
    slabel(ax, 50, 40.2, "S50", S.C_OX, size=7.4)

    ax.text(2, 39.5, "2   ELECTRICAL  (BATT DC — not GEN)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    dcdc = S.unit(ax, 2, 26, 20, 10.0, "FC_DCDC",
                  "DC/DC into\n160–700 V window\nS51",
                  fill="#dbeafe", edge="#1e3a8a", ts=17.1, ss=11.2)
    sol = S.unit(ax, 26, 26, 30, 10.0, "SOL-ARK  60K-3P-480V",
                 "BATT DC ← ZnBr2 + FC\nGEN port = BACKUP_GEN only (S47)\nGRID ↔  ·  LOAD → ATS",
                 fill="#dcfce7", edge="#15803d", ts=16.7, ss=10.8)
    znbr = S.iface(ax, 60, 27, 16, 8.0, "ZnBr2",
                   "peer on BATT DC\nunchanged",
                   fill="#ede9fe", edge="#6d28d9")
    gen = S.iface(ax, 80, 27, 18, 8.0, "BACKUP_GEN",
                  "≠ this sheet\nGEN AC S47\nAQS-PFD-GEN-001",
                  fill="#fff7ed", edge="#b45309")
    arrow(ax, L(fc), (dcdc[0] + dcdc[2], fc[1] + 2), S.C_PRODUCT, lw=1.2, ls=":")
    arrow(ax, (cx(fc), fc[1]), (cx(fc), 38), S.C_PRODUCT, lw=1.5)
    arrow(ax, (cx(fc), 38), (cx(dcdc), 38), S.C_PRODUCT, lw=1.5)
    arrow(ax, (cx(dcdc), 38), T(dcdc), S.C_PRODUCT, lw=1.5)
    slabel(ax, 48, 39.0, "S51  DC → BATT", S.C_PRODUCT, size=7.2)
    arrow(ax, R(dcdc), L(sol), "#1e3a8a", lw=1.6)
    arrow(ax, R(sol), L(znbr), "#1e3a8a", lw=1.2, ls="--")
    arrow(ax, R(znbr), L(gen), "#b45309", lw=1.0, ls=":")

    ax.text(2, 23.5, "3   HEAT → Q4  +  PRODUCT WATER  +  FORBIDDEN",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    hx = S.unit(ax, 2, 10, 24, 10.5, "FC_HX_Q4",
                "low-grade stack heat\n→ Q4 water (S53)\n< 80 °C life air",
                fill="#ffedd5", edge="#c2410c", ts=16.7, ss=10.8)
    q4 = S.iface(ax, 30, 11, 18, 9.0, "Q4 / HVAC",
                 "FARM + HAB\nS06 / S44 peers",
                 fill="#ffedd5", edge="#c2410c")
    h2o = S.unit(ax, 52, 10, 22, 10.5, "FC_PRODUCT_H2O",
                 "product water\n→ S13 condensate\nS52  ·  not potable",
                 fill="#e0f2fe", edge="#0369a1", ts=16.4, ss=10.8)
    S.callout(ax, 78, 10, 20, 10.5, "FORBIDDEN", [
        "FC → GEN port",
        "FC → RECT DC tee",
        "GEN exhaust → AHU",
        "Hard-code 100–200 kW",
        "Drop MeOH peer path",
    ], fill="#fee2e2", edge="#b91c1c")
    arrow(ax, B(fc), (cx(fc), 22), S.C_HVAC, lw=1.3)
    arrow(ax, (cx(fc), 22), (cx(hx), 22), S.C_HVAC, lw=1.3)
    arrow(ax, (cx(hx), 22), T(hx), S.C_HVAC, lw=1.3)
    arrow(ax, R(hx), L(q4), S.C_HVAC, lw=1.5)
    slabel(ax, 18, 23.0, "S53", S.C_HVAC, size=7.2)
    arrow(ax, (cx(fc), 22), (cx(h2o), 22), S.C_UTIL, lw=1.2, ls="--")
    arrow(ax, (cx(h2o), 22), T(h2o), S.C_UTIL, lw=1.2, ls="--")
    slabel(ax, 58, 23.0, "S52", S.C_UTIL, size=7.2)

    S.callout(ax, 2, 2.8, 96, 6.2, "MACHINE / DOC NAMES", [
        "FUEL_CELL · FC_H2_MANIFOLD · FC_O2_MANIFOLD · FC_DCDC · FC_HX_Q4 · FC_PRODUCT_H2O · FC_PURGE · FC_HUMIDIFIER",
        "AQS-FC-001 · AQS-EQP-FC-001 · ELECTRICAL.md · AQS-PWR-002 (GEN peer) · AQS-GAP-001 §7 item 3",
        "Placement: L0 POWER yard near SOL_ARK_60K / ZnBr2  ·  SCALE_M=1.0  ·  CERN-OHL-S-2.0",
    ], fill="#fafaf9", edge="#57534e")

    S.graph_bridge_note(ax, _GP, "S49–S53")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — fuel_cell", x=2.0, y=6.8)
    S.footer(ax, DOC, FNAME, "AQS-FC-001 / AQS-VENT-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
