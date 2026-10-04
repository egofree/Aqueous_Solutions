#!/usr/bin/env python3
"""AQS-PFD-TRR-001 — Terrace irrigation / open vs enclosed greenhouse.

Authority: AQS-TRR-001, AQS-SCALE-001 §6–7, AQS-WTR-001, AQS-STR-001 S40–S42,
AQS-EQP-FRM-001. No invented mass rates.
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


DOC = "AQS-PFD-TRR-001"
FNAME = "terrace_irrigation_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("terrace", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "TERRACE IRRIGATION",
        "OVERFLOW surplus → open terrace  OR  enclosed greenhouse  ·  drain to CATCH (clean) / HDR_GREY (fertigated)",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  Clean overflow only for landscape (S40).  No FARM_SUMP liquor.  No potable S26.  Fertigation drain ≠ CATCH.")

    # ── Source ──
    ax.text(2, 59.0, "1   CLEAN SURPLUS SOURCE  (AQS-SCALE-001 §6–7)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    roof = S.unit(ax, 2, 48, 16, 7.5, "ROOF TANK", "clean tower\nS21–S23 inventory", fill="#e0f2fe", edge="#0369a1")
    znbr = S.iface(ax, 20, 48, 14, 7.5, "ZnBr2 FULL", "batteries accept\nno more charge", fill="#f3e8ff", edge="#6b21a8")
    spill = S.unit(ax, 37, 48, 18, 7.5, "OVERFLOW SPILL", "OVERFLOW_SPILL_ROOF\n→ DOWNCOMER / OUTFALL", fill="#dcfce7", edge="#166534")
    arrow(ax, R(roof), L(spill), S.C_UTIL, lw=1.6)
    arrow(ax, R(znbr), (spill[0], cy(znbr)), S.C_HVAC, lw=1.2, ls="--")
    slabel(ax, 30.5, 56.2, "when both full", S.C_UTIL, size=6.8)

    irrig = S.unit(ax, 60, 48, 16, 7.5, "TERRACE IRRIG", "drip / flood headers\nS40 clean feed", fill="#bbf7d0", edge="#166534")
    arrow(ax, R(spill), L(irrig), S.C_UTIL, lw=1.7)
    slabel(ax, 56.5, 56.2, "S40", S.C_UTIL, size=7.4)

    makeup = S.iface(ax, 80, 48, 16, 7.5, "S21 MAKEUP", "optional trickle\nstill clean tower", fill="#e0f2fe", edge="#0369a1")
    arrow(ax, L(makeup), R(irrig), S.C_UTIL, lw=1.2, ls="--")
    slabel(ax, 77, 56.2, "sec.", S.C_UTIL, size=6.6)

    # ── Climate split ──
    ax.text(2, 45.0, "2   CLIMATE OPTION  (AQS-TRR-001 §3)  ·  equator-facing + E/W wrap per SITE_LAT_DEG",
            fontsize=14.3, fontweight="bold", color="#1c1917")

    open_t = S.unit(ax, 2, 28, 42, 13.5, "OPTION A — OPEN TERRACE",
                    "Prefer when frost-free window + moderate wind + rain/S40 meet ET\n"
                    "Bands: B1 access/header · mid perennial/cover · outer apron buffer\n"
                    "Duty: landscape / soil-build / surplus-water buffer\n"
                    "N-hem default (SITE_LAT_DEG=33): S + E + W open",
                    fill="#dcfce7", edge="#166534", ts=17.1, ss=10.8)
    gh = S.unit(ax, 50, 28, 46, 13.5, "OPTION B — ENCLOSED GREENHOUSE",
                "Prefer when freeze · high |lat| / low DLI · arid ET · high wind/salt · food-grade outdoor\n"
                "May enclose equator-facing band only; E/W wrap can stay open\n"
                "Optional dilute fertigation from NUTRIENT_DOSE (not S40)\n"
                "Q4 heat · S04 CO₂ · optional LED — no process gas headers",
                fill="#fef3c7", edge="#b45309", ts=17.1, ss=10.8)

    arrow(ax, B(irrig), (cx(irrig), 44), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(irrig), 44), (cx(open_t), 44), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(open_t), 44), T(open_t), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(irrig), 44), (cx(gh), 44), S.C_PRODUCT, lw=1.4)
    arrow(ax, (cx(gh), 44), T(gh), S.C_PRODUCT, lw=1.4)
    slabel(ax, 28, 45.5, "S40 → open", S.C_UTIL, size=7.0)
    slabel(ax, 68, 45.5, "S40 + optional fert", S.C_PRODUCT, size=7.0)

    # Dose stub into greenhouse only
    dose = S.iface(ax, 80, 22, 16, 5.0, "NUTRIENT DOSE", "dilute tote branch\nenclosed only", fill="#fef3c7", edge="#b45309")
    arrow(ax, L(dose), (gh[0] + gh[2], cy(dose)), S.C_PRODUCT, lw=1.2, ls="--")
    slabel(ax, 78, 27.2, "fert.", S.C_PRODUCT, size=6.6)

    # ── Returns ──
    ax.text(2, 25.5, "3   DRAINAGE RETURN",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    catch = S.unit(ax, 2, 12, 28, 10.0, "CATCH / DRAIN_SEC",
                   "S41 clean underdrain + apron\nrain + overflow only\nnever L-1 process bund",
                   fill="#e0f2fe", edge="#0369a1", ts=17.1, ss=11.2)
    grey = S.unit(ax, 36, 12, 28, 10.0, "HDR_GREY → TREAT",
                  "S42 fertigated greenhouse drain\n→ GREY / VCD_FEED class\nkeep off roof–catch",
                  fill="#ffedd5", edge="#c2410c", ts=17.1, ss=11.2)
    forbid = S.unit(ax, 70, 12, 26, 10.0, "FORBIDDEN",
                    "FARM_SUMP → terrace\nS26 potable → terrace\nSalria / etch → bands\nfertigation → CATCH",
                    fill="#fee2e2", edge="#b91c1c", ts=17.1, ss=11.2)

    arrow(ax, B(open_t), (cx(open_t), 23.5), S.C_UTIL, lw=1.5)
    arrow(ax, (cx(open_t), 23.5), (cx(catch), 23.5), S.C_UTIL, lw=1.5)
    arrow(ax, (cx(catch), 23.5), T(catch), S.C_UTIL, lw=1.5)
    slabel(ax, 18, 24.3, "S41", S.C_UTIL, size=7.2)

    arrow(ax, B(gh), (cx(gh), 23.5), S.C_HVAC, lw=1.5)
    arrow(ax, (cx(gh), 23.5), (cx(grey), 23.5), S.C_HVAC, lw=1.5)
    arrow(ax, (cx(grey), 23.5), T(grey), S.C_HVAC, lw=1.5)
    slabel(ax, 55, 24.3, "S42", S.C_HVAC, size=7.2)

    S.callout(ax, 2, 3.5, 54, 7.0, "MACHINE / MASSING NAMES", [
        "OVERFLOW_SPILL_ROOF · OVERFLOW_DOWNCOMER_* · OVERFLOW_OUTFALL_*",
        "OVERFLOW_TERRACE_{S|N|E|W}_B{n} · OVERFLOW_APRON_*",
        "Detail: cad/TERRACE_LANDSCAPE.md (AQS-TRR-001)  ·  Farm: AQS-EQP-FRM-001",
        "FreeCAD solids for beds / greenhouse = later pass (REMAINING_BLD).",
    ], fill="#f0fdf4", edge="#166534")

    S.callout(ax, 58, 3.5, 38, 7.0, "QUALITATIVE ONLY", [
        "No invented L/d or kg/d on this sheet.",
        "S40 / S41 Closed · S42 Closed/Claimed when used.",
        "Indoor FARM remains primary food loop.",
        "SCALE_M unchanged this pass.",
    ], fill="#f8fafc", edge="#64748b")

    S.legend(ax, 2.0, -0.2)
    S.graph_bridge_note(ax, _GP, "S40–S42")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — terrace", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-TRR-001 / AQS-SCALE-001 / AQS-WTR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
