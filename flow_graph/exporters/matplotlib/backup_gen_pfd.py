#!/usr/bin/env python3
"""AQS-PFD-GEN-001 — H₂ backup genset on Sol-Ark GEN port.

Authority: AQS-PWR-001, AQS-EQP-GEN-001, ELECTRICAL.md, POWER overview,
AQS-STR-001 S45–S47/S64, AQS-VENT-001. Fuel = plant H₂ via CRYO_H2. Rating TBD.
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


DOC = "AQS-PFD-GEN-001"
FNAME = "backup_gen_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("backup_gen", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "BACKUP GENERATOR",
        "Plant H₂ → BACKUP_GEN → Sol-Ark GEN port (closes spare)  ·  exhaust Claimed  ·  L0 POWER yard",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  Primary fuel = plant H₂ (S45).  Diesel = contingency only.  "
           "Genset AC → GEN port only — not RECT DC bus.  Rating TBD.")

    ax.text(2, 59.0, "1   FUEL  (on-site stream)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    h2d = S.unit(ax, 2, 48, 18, 8.0, "H2_DRYER",
                 "process H₂\nS05 / S24",
                 fill="#dbeafe", edge="#1e3a8a")
    cryo = S.unit(ax, 24, 48, 18, 8.0, "CRYO_H2",
                  "product hold\nnot HDR_H2",
                  fill="#dbeafe", edge="#1e3a8a")
    buf = S.unit(ax, 46, 48, 18, 8.0, "GEN_H2_BUFFER",
                 "manifold + arrestor\nMAQ / NFPA 2",
                 fill="#e0f2fe", edge="#0369a1")
    gen = S.unit(ax, 70, 46, 26, 11.0, "BACKUP_GEN",
                 "H₂ AC genset\n480 V 3φ\nkW TBD (≤ Sol-Ark class)",
                 fill="#fef3c7", edge="#b45309", ts=17.7, ss=11.5)
    arrow(ax, R(h2d), L(buf), S.C_H2, lw=1.5)
    arrow(ax, R(cryo), (buf[0], cy(cryo)), S.C_H2, lw=1.5)
    arrow(ax, R(buf), L(gen), S.C_H2, lw=1.8)
    slabel(ax, 20, 57.8, "S64", S.C_H2, size=7.2)
    slabel(ax, 42, 57.8, "S45", S.C_H2, size=7.4)

    ax.text(2, 43.5, "2   ELECTRICAL  (closes GEN spare)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    sol = S.unit(ax, 2, 28, 32, 12.0, "SOL-ARK  60K-3P-480V",
                 "GEN port WAS spare → now S47\nGRID ↔  ·  LOAD → ATS S2\nBATTERY ← ZnBr2  ·  PV DC in",
                 fill="#dcfce7", edge="#15803d", ts=17.4, ss=11.2)
    ats = S.iface(ax, 40, 31, 20, 8.0, "ATS 200 A",
                  "S1 utility bypass\nS2 Sol-Ark LOAD",
                  fill="#fff7ed", edge="#b45309")
    main = S.iface(ax, 66, 31, 16, 8.0, "PLANT MAIN",
                   "MCC + RECT\nunchanged",
                   fill="#fff7ed", edge="#b45309")
    znbr = S.iface(ax, 86, 31, 12, 8.0, "ZnBr2 / PV",
                   "unchanged\nfailover peer",
                   fill="#ede9fe", edge="#6d28d9")
    arrow(ax, L(gen), (cx(sol) + 8, gen[1]), S.C_PRODUCT, lw=1.2, ls=":")
    # GEN down to Sol-Ark
    arrow(ax, (cx(gen), gen[1]), (cx(gen), 42), S.C_PRODUCT, lw=1.6)
    arrow(ax, (cx(gen), 42), (sol[0] + sol[2], 42), S.C_PRODUCT, lw=1.6)
    arrow(ax, (sol[0] + sol[2], 42), (sol[0] + sol[2], sol[1] + sol[3]), S.C_PRODUCT, lw=1.6)
    slabel(ax, 55, 43.2, "S47  AC → GEN port", S.C_PRODUCT, size=7.2)
    arrow(ax, R(sol), L(ats), "#b45309", lw=1.5)
    arrow(ax, R(ats), L(main), "#b45309", lw=1.5)
    arrow(ax, R(main), L(znbr), S.C_H2, lw=1.1, ls="--")

    ax.text(2, 25.5, "3   EXHAUST  (Claimed)  +  FUEL OPTIONS",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    exh = S.unit(ax, 2, 12, 28, 10.5, "GEN_EXHAUST_HX",
                 "H₂ burn → H₂O primary\ncondensate → S13 class\nS46 liquid",
                 fill="#e0f2fe", edge="#0369a1", ts=16.7, ss=10.8)
    scrub = S.unit(ax, 36, 12, 28, 10.5, "SCRUBBER BRANCH",
                   "NOx / residual gas\n≠ CRU Cl₂ path\nS46 gas Claimed",
                   fill="#ffedd5", edge="#c2410c", ts=16.7, ss=10.8)
    fuel = S.callout(ax, 70, 12, 28, 10.5, "FUEL OPTIONS", [
        "PRIMARY: S64→CRYO_H2→S45",
        "S24 = H₂ roof contingency only",
        "CONTINGENCY fuel: diesel (external)",
        "DEFERRED: biogas S30",
        "NOT THIS SHEET: MeOH FC",
    ], fill="#fef3c7", edge="#b45309")
    arrow(ax, B(gen), (cx(gen), 24), S.C_HVAC, lw=1.4)
    arrow(ax, (cx(gen), 24), (cx(exh), 24), S.C_HVAC, lw=1.4)
    arrow(ax, (cx(exh), 24), T(exh), S.C_HVAC, lw=1.4)
    arrow(ax, (cx(exh), 24), (cx(scrub), 24), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, (cx(scrub), 24), T(scrub), S.C_HVAC, lw=1.2, ls="--")
    slabel(ax, 20, 25.0, "S46", S.C_HVAC, size=7.2)

    S.callout(ax, 2, 3.5, 96, 7.0, "MACHINE / DOC NAMES", [
        "BACKUP_GEN · GEN_H2_BUFFER · GEN_EXHAUST_HX · SOL_ARK_60K GEN · ATS · RECTIFIER* · ZNBR2* · PV_ARRAY*",
        "AQS-PWR-001 · AQS-EQP-GEN-001 · ELECTRICAL.md · POWER/Power_System_overview.md · AQS-GAP-001 §4",
        "Placement: L0 POWER yard beside SOL_ARK_60K  ·  SCALE_M=1.0  ·  CERN-OHL-S-2.0",
    ], fill="#fafaf9", edge="#57534e")

    S.graph_bridge_note(ax, _GP, "S45–S47")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — backup_gen", x=2.0, y=6.8)
    S.footer(ax, DOC, FNAME, "AQS-PWR-001 / AQS-VENT-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
