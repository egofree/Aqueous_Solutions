#!/usr/bin/env python3
"""AQS-PFD-FAB-PV-001 — solar-cell branch (polished wafer → cell).

Authority: AQS-EQP-FAB-PV-001, AQS-EQP-FAB-001, AQS-EQP-FAB-RGN-001
(WS_KOH / WS_SOLV / WS_DOPE), AQS-WTR-001 / FAB UPW (S27), AQS-VENT-001,
AQS-ELC-001 (PV offtake narrative only). No invented kW / PECVD power /
belt-furnace duty.
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


DOC = "AQS-PFD-FAB-PV-001"
FNAME = "solar_cell_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("solar_cell", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(19.0, 13.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 78)
    S.title_block(
        ax, DOC, "SOLAR-CELL BRANCH",
        "PRE_CLEAN wafers → PV_TEXTURE → EMITTER → PSG_ETCH → ARC → CONTACT → FIRE → IV  ·  "
        "S27 / WS_KOH / S10  ·  kW TBD",
        y=76.0,
    )

    S.rule(ax, 2, 70.5, 96, 3.4,
           "RULE  ·  Separate train from FAB_TOOL IC litho/implant.  Share UPW, KOH, etch return, N₂.  "
           "No free outdoor dump (AQS-VENT-001).  PECVD / belt kW = vendor TBD — do not invent.")

    ax.text(2, 68.0, "1   FEED  (from AQS-PFD-FAB-001 polish path)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    preclean = S.iface(ax, 2, 57.5, 16, 7.5, "PRE_CLEAN",
                       "polished wafers\nAQS-PFD-FAB-001",
                       fill="#e0f2fe", edge="#0369a1")
    upw = S.iface(ax, 21, 57.5, 14, 7.5, "FAB UPW",
                  "S27 rinse",
                  fill="#e0f2fe", edge="#0369a1")
    koh = S.iface(ax, 38, 57.5, 14, 7.5, "WS_KOH",
                  "S35 texture",
                  fill="#fef3c7", edge="#b45309")
    n2 = S.iface(ax, 55, 57.5, 14, 7.5, "CRYO N2/O2",
                 "S03 / S02\npurge / oxidize",
                 fill="#dbeafe", edge="#1d4ed8")
    fab = S.iface(ax, 72, 57.5, 26, 7.5, "L0 FAB ENVELOPE",
                  "south/east strip\nAQS-EQP-FAB-PV-001 §5",
                  fill="#fafaf9", edge="#57534e")

    ax.text(2, 55.0, "2   CELL TRAIN  (AQS-EQP-FAB-PV-001 tags)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    tex = S.unit(ax, 2, 42.0, 12, 9.5, "PV_TEXTURE",
                 "alkaline\npyramid\nWS_KOH",
                 fill="#fef3c7", edge="#b45309", ts=15.2, ss=10.2)
    emit = S.unit(ax, 16, 42.0, 12, 9.5, "PV_EMITTER",
                  "POCl₃\ndiffusion\nfurnace",
                  fill="#ffedd5", edge="#c2410c", ts=15.2, ss=10.2)
    psg = S.unit(ax, 30, 42.0, 12, 9.5, "PV_PSG_ETCH",
                 "PSG / edge\nisolation\n→ S10",
                 fill="#e0f2fe", edge="#0369a1", ts=15.2, ss=10.2)
    arc = S.unit(ax, 44, 42.0, 12, 9.5, "PV_ARC",
                 "SiNₓ ARC\nPECVD class\ngas TBD",
                 fill="#e0f2fe", edge="#0369a1", ts=15.2, ss=10.2)
    contact = S.unit(ax, 58, 42.0, 12, 9.5, "PV_CONTACT",
                     "Ag front\nAl rear\nscreen",
                     fill="#e4e4e7", edge="#3f3f46", ts=15.2, ss=10.2)
    fire = S.unit(ax, 72, 42.0, 12, 9.5, "PV_FIRE",
                  "belt fire\nfurnace\nkW TBD",
                  fill="#ffedd5", edge="#c2410c", ts=15.2, ss=10.2)
    iv = S.unit(ax, 86, 42.0, 12, 9.5, "PV_IV",
                "IV / flash\nsort",
                fill="#dcfce7", edge="#166534", ts=15.2, ss=10.2)

    arrow(ax, B(preclean), (cx(preclean), 53.5), S.C_PRODUCT, lw=1.4)
    arrow(ax, (cx(preclean), 53.5), (cx(tex), 53.5), S.C_PRODUCT, lw=1.4)
    arrow(ax, (cx(tex), 53.5), T(tex), S.C_PRODUCT, lw=1.4)
    for a, b in [(tex, emit), (emit, psg), (psg, arc), (arc, contact),
                 (contact, fire), (fire, iv)]:
        arrow(ax, R(a), L(b), S.C_PRODUCT, lw=1.45)

    arrow(ax, B(upw), (cx(upw), 53.5), S.C_UTIL, lw=1.05, ls="--")
    arrow(ax, B(koh), (cx(tex), 53.5), S.C_OX, lw=1.1, ls="--")
    arrow(ax, B(n2), (cx(emit), 53.5), S.C_UTIL, lw=1.05, ls="--")
    slabel(ax, 10, 54.2, "wafers", S.C_PRODUCT, size=6.6)
    slabel(ax, 28, 54.2, "S35", S.C_OX, size=6.6)

    ax.text(2, 39.5, "3   RETURNS  ·  HEAT  ·  OFFTAKE",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    etch = S.iface(ax, 2, 26.5, 16, 9.0, "ETCH RETURN",
                   "S10 → REGEN\nLEACH closed",
                   fill="#dcfce7", edge="#166534")
    scrub = S.iface(ax, 21, 26.5, 16, 9.0, "LEV → SCRUB",
                    "emitter / ARC\nexhaust\nAQS-VENT-001",
                    fill="#ffedd5", edge="#9a3412")
    hx = S.unit(ax, 40, 26.5, 16, 9.0, "PV_HX_Q4",
                "fire heat reject\n→ Q4 water\n≠ Q1 flue",
                fill="#fce7f3", edge="#9d174d", ts=15.5, ss=10.5)
    solv = S.iface(ax, 59, 26.5, 16, 9.0, "WS_SOLV path",
                   "screen wipe\n→ S38 / OIL",
                   fill="#ffedd5", edge="#9a3412")
    offtake = S.iface(ax, 78, 26.5, 20, 9.0, "PV_MODULE_OFFTAKE",
                      "cells → campus PV\nnarrative only\nPV_COUNT unchanged",
                      fill="#fef3c7", edge="#b45309")

    arrow(ax, B(psg), (cx(psg), 37.5), S.C_LIQUOR, lw=1.3)
    arrow(ax, (cx(psg), 37.5), (cx(etch), 37.5), S.C_LIQUOR, lw=1.3)
    arrow(ax, (cx(etch), 37.5), T(etch), S.C_LIQUOR, lw=1.3)
    slabel(ax, 14, 38.2, "S10", S.C_LIQUOR, size=7.0)
    arrow(ax, B(emit), (cx(emit), 37.0), S.C_ORG, lw=1.05, ls="--")
    arrow(ax, (cx(emit), 37.0), (cx(scrub), 37.0), S.C_ORG, lw=1.05, ls="--")
    arrow(ax, (cx(scrub), 37.0), T(scrub), S.C_ORG, lw=1.05, ls="--")
    arrow(ax, B(fire), (cx(fire), 37.0), S.C_HVAC, lw=1.15, ls="--")
    arrow(ax, (cx(fire), 37.0), (cx(hx), 37.0), S.C_HVAC, lw=1.15, ls="--")
    arrow(ax, (cx(hx), 37.0), T(hx), S.C_HVAC, lw=1.15, ls="--")
    arrow(ax, B(contact), (cx(contact), 36.5), S.C_ORG, lw=1.0, ls="--")
    arrow(ax, (cx(contact), 36.5), (cx(solv), 36.5), S.C_ORG, lw=1.0, ls="--")
    arrow(ax, (cx(solv), 36.5), T(solv), S.C_ORG, lw=1.0, ls="--")
    arrow(ax, B(iv), (cx(iv), 36.5), S.C_PRODUCT, lw=1.25)
    arrow(ax, (cx(iv), 36.5), (cx(offtake), 36.5), S.C_PRODUCT, lw=1.25)
    arrow(ax, (cx(offtake), 36.5), T(offtake), S.C_PRODUCT, lw=1.25)

    S.callout(ax, 2, 8.5, 58, 15.5, "MACHINE / PROCESS LIST", [
        "PV_TEXTURE · PV_EMITTER · PV_PSG_ETCH · PV_ARC ·",
        "  PV_CONTACT · PV_FIRE · PV_IV · PV_HX_Q4 stub",
        "CAD envelopes: freecad/wafer_fab.py (PV_* east strip)",
        "Reagents: WS_KOH (S35) · WS_SOLV · POCl₃ via WS_DOPE class",
        "Detail: cad/process/SOLAR_CELL_EQUIPMENT.md (AQS-EQP-FAB-PV-001)",
        "Parent fab: AQS-PFD-FAB-001 §5 points here",
    ], fill="#fffbeb", edge="#b45309")

    S.callout(ax, 62, 8.5, 36, 15.5, "OPEN / STUDY", [
        "PECVD SiH₄/NH₃ vendor gas TBD",
        "Belt-furnace nameplate kW TBD",
        "Cell offtake ≠ resize PV_COUNT",
        "AHJ / MAWP / WPS unchanged",
        "Status = Partial architecture",
    ], fill="#f8fafc", edge="#64748b")

    S.legend(ax, 2.0, 1.2)
    S.graph_bridge_note(ax, _GP, "S10/S27/S35; SOLAR_PV_CELL node has no dedicated edges yet")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — solar_cell", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME,
             "AQS-EQP-FAB-PV-001 / AQS-EQP-FAB-001 / AQS-EQP-FAB-RGN-001 / AQS-VENT-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
