#!/usr/bin/env python3
"""AQS-PFD-FAB-UPW-001 — Wafer fab ultrapure water polish train.

Authority: AQS-WTR-001 §3, AQS-EQP-FAB-UPW-001, doc 03 rinse-station control,
STREAM_REGISTER S01/S09/S10/S21/S27. Pre-remin plant water only. No invented balances.
EW POLISH BANK (metal cells) ≠ FAB_UPW_*.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
import params as P
import sector_style as S

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)


DOC = "AQS-PFD-FAB-UPW-001"
FNAME = "fab_upw_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("fab_upw", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(19.0, 12.5)
    ax.set_ylim(0, 72)
    S.title_block(
        ax, DOC, "FAB UPW POLISH",
        "PRE → UF → IX/EDI → UV → FAB_UPW_TANK → WET_BENCH (S27)  ·  "
        "pre-remin feed only  ·  L0 WAFER_FAB util  ·  ≠ EW polish bank",
        y=70.0,
    )

    S.callout(ax, 2, 63.5, 96, 4.0, "INTERFACES (AQS-WTR-001 / AQS-STR-001)", [
        "IN:  S01 HDR_UPW and/or S21 roof (pre-remin)  ·  S09 acids/bases to bench only (not UPW minerals)  ·  S03 N₂ on tools",
        "OUT: S27 fab UPW → WET_BENCH  ·  clean reject → HDR_GREY / SALT / VCD_FEED  ·  etch-laden → HDR_ETCH (S10)",
        "Forbidden: S26 remineralized potable into this train  ·  sewer / Salria / farm beds for reject.",
    ], fill="#fffbeb", edge="#b45309")

    # Feed
    ax.text(2, 61.5, "1   FEED  (pre-remin plant water — minerals defeat resistivity)",
            fontsize=14.6, fontweight="bold", color=P.INK)
    roof = S.iface(ax, 2, 51.5, 14, 7.0, "ROOF TANK", "S21 gravity\nclean inventory", fill="#dbeafe", edge="#1d4ed8")
    hdr = S.iface(ax, 19, 51.5, 16, 7.0, "HDR_UPW / S01", "< 1 µS/cm class\nfrom HAB_ED_POLISH", fill="#e0f2fe", edge="#0369a1")
    no_pot = S.rule(ax, 38, 51.5, 22, 7.0,
                    "NO S26 POTABLE\nremin minerals defeat\n> 18 MΩ·cm target")
    hab = S.iface(ax, 64, 51.5, 16, 7.0, "HAB-WTR DETAIL", "AQS-PFD-HAB-WTR-001\nVCD → ED → S01", fill="#e0f2fe", edge="#0369a1")
    invent = S.iface(ax, 83, 51.5, 15, 7.0, "ROOF–CATCH", "AQS-PFD-WTR-001\ninventory ≠ regen", fill="#dbeafe", edge="#1d4ed8")

    arrow(ax, R(roof), L(hdr), S.C_UTIL, lw=1.3)
    slabel(ax, 17, 59.0, "S21", S.C_UTIL, size=7.0)
    arrow(ax, R(hab), (hab[0] + hab[2] + 1, cy(hab)), S.C_UTIL, lw=1.1, ls="--")

    # Polish train
    ax.text(2, 49.0, "2   POLISH TRAIN  (AQS-EQP-FAB-UPW-001 tags)",
            fontsize=14.6, fontweight="bold", color=P.INK)
    pre = S.unit(ax, 2, 38.0, 14, 7.5, "FAB_UPW_PRE", "particulate /\ncarbon prefilter", fill="#e0f2fe", edge="#0369a1")
    uf = S.unit(ax, 19, 38.0, 14, 7.5, "FAB_UPW_UF", "ultrafiltration", fill="#e0f2fe", edge="#0369a1")
    ix = S.unit(ax, 36, 38.0, 16, 7.5, "FAB_UPW_IX", "mixed-bed IX\nand/or EDI", fill="#bae6fd", edge="#0369a1")
    uv = S.unit(ax, 55, 38.0, 14, 7.5, "FAB_UPW_UV", "TOC / microbial\nUV", fill="#e0f2fe", edge="#0369a1")
    tank = S.unit(ax, 72, 38.0, 16, 7.5, "FAB_UPW_TANK", "recirc loop\n→ WET_BENCH S27", fill="#bae6fd", edge="#0369a1", ts=17.1)

    arrow(ax, B(hdr), (cx(hdr), 47), S.C_UTIL, lw=1.5)
    arrow(ax, (cx(hdr), 47), (cx(pre), 47), S.C_UTIL, lw=1.5)
    arrow(ax, (cx(pre), 47), T(pre), S.C_UTIL, lw=1.5)
    arrow(ax, R(pre), L(uf), S.C_UTIL, lw=1.6)
    arrow(ax, R(uf), L(ix), S.C_UTIL, lw=1.6)
    arrow(ax, R(ix), L(uv), S.C_UTIL, lw=1.6)
    arrow(ax, R(uv), L(tank), S.C_PRODUCT, lw=1.7)
    slabel(ax, 69, 46.2, "S27", S.C_PRODUCT, size=7.4)

    # Recirc note
    arrow(ax, B(tank), (cx(tank), 35.5), S.C_UTIL, lw=1.1)
    arrow(ax, (cx(tank), 35.5), (cx(uv), 35.5), S.C_UTIL, lw=1.1)
    arrow(ax, (cx(uv), 35.5), B(uv), S.C_UTIL, lw=1.1)
    slabel(ax, 64, 34.5, "recirc", S.C_UTIL, size=6.6)

    # Wet bench + reject
    ax.text(2, 33.0, "3   WET BENCH USE + REJECT SEGREGATION",
            fontsize=14.6, fontweight="bold", color=P.INK)
    wet = S.unit(ax, 36, 22.5, 18, 7.5, "WET_BENCH", "RCA / etch / rinse\ndoc 03 rinse control", fill="#e0f2fe", edge="#0369a1")
    rej = S.unit(ax, 58, 22.5, 16, 7.5, "FAB_UPW_REJECT", "segregated header\nclean vs etch-laden", fill="#fef3c7", edge="#b45309")
    etch = S.iface(ax, 78, 22.5, 14, 7.5, "HDR_ETCH / S10", "→ REGEN LEACH\nclosed · no drain", fill="#dcfce7", edge="#166534")
    grey = S.iface(ax, 18, 22.5, 14, 7.5, "HDR_GREY / SALT", "clean UF/IX reject\nor VCD_FEED", fill="#e0f2fe", edge="#0369a1")
    hcl = S.iface(ax, 2, 22.5, 13, 7.5, "HCl / NaOH", "S09 to bench\nnot UPW minerals", fill="#ffedd5", edge="#9a3412")

    arrow(ax, B(tank), (cx(tank), 31.5), S.C_PRODUCT, lw=1.5)
    arrow(ax, (cx(tank), 31.5), (cx(wet), 31.5), S.C_PRODUCT, lw=1.5)
    arrow(ax, (cx(wet), 31.5), T(wet), S.C_PRODUCT, lw=1.5)
    arrow(ax, R(wet), L(rej), S.C_LIQUOR, lw=1.4)
    arrow(ax, R(rej), L(etch), S.C_LIQUOR, lw=1.5)
    slabel(ax, 88, 30.5, "S10 etch", S.C_LIQUOR, size=7.0)
    arrow(ax, L(rej), R(grey), S.C_HVAC, lw=1.3, ls="--")
    slabel(ax, 40, 21.0, "clean reject", S.C_HVAC, size=6.6)
    arrow(ax, R(hcl), L(wet), S.C_OX, lw=1.2, ls="--")
    slabel(ax, 14, 27.0, "S09", S.C_OX, size=7.0)

    S.rule(ax, 2, 17.0, 96, 3.0,
           "RULE  ·  Etch / HF rinse never to HDR_GREY or floor drain.  Clean reject may re-enter VCD_FEED if conductivity allows.  "
           "EW POLISH BANK (after EW-9) is metal cells — not this train.")

    S.callout(ax, 2, 7.5, 52, 7.5, "QUALITY TARGETS (doc 03 — grounded)", [
        "Resistivity > 18 MΩ·cm   ·   TOC < 5 ppb   ·   particles > 0.5 µm < 100 / L",
        "Feed conductivity < 1 µS/cm class (S01).  Silica / boron / metals suite = TBD placeholder.",
        "Mass rates TBD — no invented balance.  Equip list: cad/process/FAB_UPW.md",
    ], fill="#fffbeb", edge="#b45309")

    S.callout(ax, 56, 7.5, 42, 7.5, "SHEETS / NAMING", [
        "Parent sector: AQS-PFD-FAB-001",
        "Authority: AQS-WTR-001 §3 · AQS-EQP-FAB-UPW-001",
        "Forge / cut / reagent forks remain open",
        "  on AQS-EQP-FAB-001 (next fab pass).",
        "Crystal forge detail ≠ this UPW sheet.",
    ], fill="#f8fafc", edge="#64748b")

    S.legend(ax, 2.0, 0.8)
    S.graph_bridge_note(ax, _GP, "S01/S09/S27")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — fab_upw", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-WTR-001 / AQS-EQP-FAB-UPW-001 / doc 03")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
