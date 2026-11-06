#!/usr/bin/env python3
"""AQS-PFD-GEO-001 — Geothermal GHEX + heat pump; ORC electric stub.

Authority: AQS-PWR-002, AQS-EQP-GEO-001, POWER overview (100 kW narrative),
ELECTRICAL.md (Q4 HVAC). No invented M1 electric kW.
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


DOC = "AQS-PFD-GEO-001"
FNAME = "geothermal_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("geothermal", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "GEOTHERMAL LOOP",
        "Closed-loop GHEX → water-source heat pump → Q4  ·  binary ORC electric = TBD stub  ·  L0 POWER yard",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  S43 loop ≠ UPW / CATCH / Salria.  Q4 only into life air.  "
           "Do not claim legacy 100 kW electric on M1 yard — ORC rating TBD.")

    ax.text(2, 59.0, "1   GROUND LOOP  (closed)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    ghex = S.unit(ax, 2, 46, 22, 10.5, "GEO_GHEX",
                  "vertical bore field class\nclosed-loop\noff-plate site\ncount / depth TBD",
                  fill="#dcfce7", edge="#166534", ts=17.4, ss=11.2)
    pump = S.unit(ax, 28, 48, 16, 7.5, "GEO_LOOP_PUMP",
                  "S43 circulation\nrating TBD",
                  fill="#e0f2fe", edge="#0369a1")
    hp = S.unit(ax, 50, 46, 22, 10.5, "GEO_HP",
                "water-source heat pump\n→ Q4 thermal (S44)\nprimary M1 duty",
                fill="#bbf7d0", edge="#166534", ts=17.4, ss=11.2)
    arrow(ax, R(ghex), L(pump), S.C_UTIL, lw=1.7)
    arrow(ax, R(pump), L(hp), S.C_UTIL, lw=1.7)
    arrow(ax, L(pump), R(ghex), S.C_UTIL, lw=1.2, ls="--")
    slabel(ax, 24, 57.8, "S43", S.C_UTIL, size=7.4)
    slabel(ax, 40, 57.8, "S43", S.C_UTIL, size=7.4)

    q4 = S.iface(ax, 78, 46, 18, 10.5, "Q4 / HVAC",
                 "FARM + HAB\nheat < 80 °C\n(S06 class)",
                 fill="#ffedd5", edge="#c2410c")
    arrow(ax, R(hp), L(q4), S.C_HVAC, lw=1.8)
    slabel(ax, 73.5, 57.8, "S44", S.C_HVAC, size=7.4)

    ax.text(2, 43.0, "2   ELECTRIC PATH  (deferred)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    orc = S.tbd(ax, 2, 28, 36, 12.0, "GEO_ORC  —  BINARY ORC STUB (Claimed)",
                "Closure arch: S48 → Sol-Ark AC · rating TBD — no invent kW (AQS-VENT-001)")
    sol = S.iface(ax, 44, 30, 28, 9.0, "SOL-ARK AC couple",
                  "future S48\nnot wired at M1 issuance",
                  fill="#dcfce7", edge="#15803d")
    yard = S.iface(ax, 78, 30, 18, 9.0, "POWER YARD",
                   "L0 west of dock\nGEO_HDR keep-out",
                   fill="#fafaf9", edge="#57534e")
    arrow(ax, R(orc), L(sol), S.C_PRODUCT, lw=1.3, ls="--")
    slabel(ax, 40, 40.5, "S48 TBD", S.C_PRODUCT, size=7.0)
    arrow(ax, R(sol), L(yard), S.C_UTIL, lw=1.1, ls="--")

    ax.text(2, 25.5, "3   INTERFACES / FORBIDDEN",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    S.callout(ax, 2, 12, 46, 11.5, "INTERFACES", [
        "Thermal: GEO_HP → Q4 (S44) shared discipline with S06.",
        "Loop: GEO_GHEX ↔ GEO_HP (S43) dedicated fluid.",
        "Electric: GEO_ORC → Sol-Ark only when rating issued.",
        "Yard: GEO_HP / GEO_HDR on L0 POWER; bore field off-plate.",
        "Companion: BACKUP_GEN on AQS-PFD-GEN-001 (GEN port).",
    ], fill="#ecfdf5", edge="#166534")
    S.callout(ax, 52, 12, 44, 11.5, "FORBIDDEN", [
        "S43 → HDR_UPW / CATCH / ROOF_TANK / Salria.",
        "Raw ORC working fluid into life AHU.",
        "Geothermal wells as process-water makeup.",
        "Hard-coding 100 kW on M1 electrical_yard.",
        "Mixing ZnBr2 Br₂ tower with GEO pads.",
    ], fill="#fee2e2", edge="#b91c1c")

    S.callout(ax, 2, 3.5, 96, 7.0, "MACHINE / DOC NAMES", [
        "GEO_GHEX · GEO_LOOP_PUMP · GEO_HP · GEO_ORC (stub) · GEO_HDR",
        "AQS-PWR-002 · AQS-EQP-GEO-001 · ELECTRICAL.md HVAC 1.5 kW class",
        "SCALE_M=1.0  ·  no invented M1 electric kW  ·  CERN-OHL-S-2.0",
    ], fill="#fafaf9", edge="#57534e")

    S.graph_bridge_note(ax, _GP, "S06/S43–S44/S48")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — geothermal", x=2.0, y=6.8)
    S.footer(ax, DOC, FNAME, "AQS-PWR-001 / AQS-VENT-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
