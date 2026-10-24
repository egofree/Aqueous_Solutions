#!/usr/bin/env python3
"""AQS-PFD-HAB-WTR-001 — Habitation water purification (grey / black / VCD / ED / remin).

Authority: AQS-WTR-001, AQS-EQP-HAB-001, STREAM_REGISTER S01/S12/S13/S21/S25–S30,
07-water-air-habitation.md, SLINGSHOT Water_Cycle (kept/adapted).
Roof–catch inventory is AQS-PFD-WTR-001 — not regeneration. No invented mass balances.
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


DOC = "AQS-PFD-HAB-WTR-001"
FNAME = "hab_water_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("hab_water", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(19.0, 13.5)
    ax.set_ylim(0, 76)
    S.title_block(
        ax, DOC, "HABITATION WATER PURIFICATION",
        "GREY / BLACK treat → VCD regeneration → ED polish → REMIN potable  ·  "
        "roof–catch = inventory (AQS-PFD-WTR-001)  ·  L1 west + CORE util",
        y=74.0,
    )

    S.callout(ax, 2, 67.5, 96, 4.0, "INTERFACES (AQS-WTR-001 / AQS-STR-001)", [
        "IN:  S13 condensate (farm / HVAC)  ·  S21 roof gravity  ·  S12 collect from HAB_WASTE / WETROOM",
        "OUT: S26 potable → HAB taps  ·  S01 / HDR_UPW pre-remin (farm / fab feed)  ·  S28 brine → leach / salt  ·  S30 → NUTRIENT DOSE",
        "Forbidden: dirty solids into VCD evaporators  ·  S26 into wet bench  ·  Salria / sewer / storm on treated grey.",
    ], fill="#e0f2fe", edge="#0369a1")

    # ── 1 Grey / black ──────────────────────────────────────
    ax.text(2, 65.5, "1   GREY / BLACK COLLECT  (dirty → treat; not VCD-primary)",
            fontsize=14.6, fontweight="bold", color=P.INK)
    waste = S.unit(ax, 2, 55.5, 12, 7.0, "HAB WASTE", "S12 collect\nCAD stub", fill="#e4e4e7", edge="#3f3f46")
    wetrm = S.iface(ax, 2, 46.5, 12, 6.5, "WETROOM / GALLEY", "rinse + toilet\nIBC clearances", fill="#ffedd5", edge="#c2410c")

    gs = S.unit(ax, 17, 55.5, 12, 7.0, "GREY_SCREEN", "solids / grease", fill="#e0f2fe", edge="#0369a1")
    gb = S.unit(ax, 31, 55.5, 12, 7.0, "GREY_BIO", "BOD / FOG\nHAB_AIR air", fill="#e0f2fe", edge="#0369a1")
    gm = S.unit(ax, 45, 55.5, 12, 7.0, "GREY_MED", "membrane ED\nroot-07 MED", fill="#e0f2fe", edge="#0369a1")
    gbuf = S.unit(ax, 59, 55.5, 14, 7.0, "GREY_BUFF", "S29 buffer\n→ VCD or salt", fill="#bae6fd", edge="#0369a1")

    bc = S.unit(ax, 17, 46.5, 12, 6.5, "BLACK_COLLECT", "toilet / urine\ndiversion opt.", fill="#fef3c7", edge="#b45309")
    bd = S.unit(ax, 31, 46.5, 12, 6.5, "BLACK_DIGEST", "solids → HDR_ORG\nHOPPER", fill="#fef3c7", edge="#b45309")
    bm = S.unit(ax, 45, 46.5, 12, 6.5, "BLACK_MED", "liquor polish\n→ S30", fill="#fef3c7", edge="#b45309")
    nut = S.iface(ax, 59, 46.5, 14, 6.5, "NUTRIENT / SALT", "S30 → S07 path\nnot VCD solids", fill="#dcfce7", edge="#166534")

    arrow(ax, R(waste), L(gs), S.C_HVAC, lw=1.3)
    arrow(ax, R(wetrm), L(bc), S.C_ORG, lw=1.2)
    arrow(ax, T(wetrm), B(gs), S.C_HVAC, lw=1.2)
    arrow(ax, R(gs), L(gb), S.C_HVAC, lw=1.4)
    arrow(ax, R(gb), L(gm), S.C_HVAC, lw=1.4)
    arrow(ax, R(gm), L(gbuf), S.C_UTIL, lw=1.5)
    slabel(ax, 57, 63.0, "S29", S.C_UTIL, size=7.2)
    arrow(ax, R(bc), L(bd), S.C_ORG, lw=1.3)
    arrow(ax, R(bd), L(bm), S.C_ORG, lw=1.3)
    arrow(ax, R(bm), L(nut), S.C_PRODUCT, lw=1.4)
    slabel(ax, 57, 53.5, "S30", S.C_PRODUCT, size=7.2)

    S.rule(ax, 75, 46.5, 23, 16.0,
           "RULE\nDirty solids never\nenter VCD_EVAP.\nBlack solids →\nHDR_ORG / HOPPER.\nGrey backup to VCD\n= contingency only\nvia GREY_BUFF.")

    # ── 2 VCD regeneration ──────────────────────────────────
    ax.text(2, 44.0, "2   VCD REGENERATION  (SLINGSHOT kept — distillate into clean inventory)",
            fontsize=14.6, fontweight="bold", color=P.INK)

    s13 = S.iface(ax, 2, 33.5, 12, 7.0, "S13 CONDENSATE", "farm sump + HVAC\nclean primary feed", fill="#dbeafe", edge="#1d4ed8")
    feed = S.unit(ax, 17, 33.5, 12, 7.0, "VCD_FEED", "S13 + S29\nclean buffer", fill="#bae6fd", edge="#0369a1")
    hx = S.unit(ax, 31, 33.5, 11, 7.0, "VCD_HX", "feed / distillate\nheat recovery", fill="#e0f2fe", edge="#0369a1")
    evap = S.unit(ax, 44, 33.5, 11, 7.0, "VCD_EVAP", "vapor out\nbrine S28", fill="#e0f2fe", edge="#0369a1")
    comp = S.unit(ax, 57, 33.5, 11, 7.0, "VCD_COMP", "vapor compress\nmodule bus (kW TBD)", fill="#e0f2fe", edge="#0369a1")
    cond = S.unit(ax, 70, 33.5, 12, 7.0, "VCD_COND", "distillate S25\nnot yet potable", fill="#bae6fd", edge="#0369a1")
    brine = S.iface(ax, 84, 33.5, 14, 7.0, "REGEN LEACH", "S28 brine\n→ salt / leach", fill="#dcfce7", edge="#166534")

    arrow(ax, R(s13), L(feed), S.C_UTIL, lw=1.5)
    arrow(ax, B(gbuf), (cx(gbuf), 42), S.C_UTIL, lw=1.2)
    arrow(ax, (cx(gbuf), 42), (cx(feed), 42), S.C_UTIL, lw=1.2)
    arrow(ax, (cx(feed), 42), T(feed), S.C_UTIL, lw=1.2)
    slabel(ax, 40, 42.5, "S29 preferred", S.C_UTIL, size=6.6)
    arrow(ax, R(feed), L(hx), S.C_UTIL, lw=1.5)
    arrow(ax, R(hx), L(evap), S.C_UTIL, lw=1.5)
    arrow(ax, R(evap), L(comp), S.C_HVAC, lw=1.5)
    arrow(ax, R(comp), L(cond), S.C_UTIL, lw=1.5)
    arrow(ax, R(evap), (evap[0] + evap[2] + 1.2, cy(evap) - 2.2), S.C_LIQUOR, lw=1.3)
    arrow(ax, (evap[0] + evap[2] + 1.2, cy(evap) - 2.2), L(brine), S.C_LIQUOR, lw=1.3)
    slabel(ax, 80, 36.0, "S28", S.C_LIQUOR, size=7.2)

    # ── 3 ED / remin / potable ──────────────────────────────
    ax.text(2, 31.0, "3   ED POLISH + REMINERALIZATION  (drinking only — not farm S07)",
            fontsize=14.6, fontweight="bold", color=P.INK)

    ed = S.unit(ax, 17, 20.0, 16, 7.5, "HAB_ED_POLISH", "UPW POLISH\n< 1 µS/cm class · S01\nBMED middle assist", fill="#bae6fd", edge="#0369a1")
    remin = S.unit(ax, 37, 20.0, 14, 7.5, "REMIN", "Ca²⁺ Mg²⁺ K⁺\ncore salts · drink only", fill="#fef3c7", edge="#b45309")
    pot = S.unit(ax, 54, 20.0, 14, 7.5, "POTABLE_TANK", "S26 holdup\nremineralized", fill="#bbf7d0", edge="#166534")
    habw = S.unit(ax, 71, 20.0, 13, 7.5, "HAB_WATER", "UV ≥ 40 mJ/cm²\n+ HAB_BOOST", fill="#dcfce7", edge="#166534")
    roof = S.iface(ax, 2, 20.0, 12, 7.5, "ROOF / CATCH", "S21 gravity\ninventory ≠ regen", fill="#dbeafe", edge="#1d4ed8")
    fabf = S.iface(ax, 86, 20.0, 12, 7.5, "FAB / FARM", "S01 pre-remin\nno S26 to bench", fill="#ffedd5", edge="#c2410c")

    arrow(ax, B(cond), (cx(cond), 29), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(cond), 29), (cx(ed), 29), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(ed), 29), T(ed), S.C_UTIL, lw=1.4)
    slabel(ax, 55, 29.5, "S25 distillate", S.C_UTIL, size=7.0)
    arrow(ax, R(ed), L(remin), S.C_UTIL, lw=1.5)
    arrow(ax, R(remin), L(pot), S.C_PRODUCT, lw=1.5)
    arrow(ax, R(pot), L(habw), S.C_PRODUCT, lw=1.5)
    slabel(ax, 68, 28.0, "S26", S.C_PRODUCT, size=7.4)
    arrow(ax, R(roof), L(ed), S.C_UTIL, lw=1.2, ls="--")
    slabel(ax, 12, 24.5, "S21", S.C_UTIL, size=6.8)
    arrow(ax, B(ed), (cx(ed), 17.5), S.C_UTIL, lw=1.3)
    arrow(ax, (cx(ed), 17.5), (cx(fabf), 17.5), S.C_UTIL, lw=1.3)
    arrow(ax, (cx(fabf), 17.5), B(fabf), S.C_UTIL, lw=1.3)
    slabel(ax, 55, 16.5, "S01 HDR_UPW (pre-remin)", S.C_UTIL, size=6.8)

    S.rule(ax, 2, 12.5, 62, 3.2,
           "RULE  ·  REMIN ≠ S07 farm dose.  S26 never feeds WET_BENCH.  Distillate not potable until ED + remin + UV.  "
           "RPZ / air gap on potable branch (AQS-HSE-001).")

    S.callout(ax, 66, 8.0, 32, 10.5, "SHEETS / QUALITY", [
        "Parent sector: AQS-PFD-HAB-001",
        "Inventory: AQS-PFD-WTR-001 (roof–catch)",
        "Equip: AQS-EQP-HAB-001",
        "Authority: AQS-WTR-001 Rev A",
        "Pre-remin: < 1 µS/cm (S01)",
        "Potable TDS: < 50 mg/L class",
        "Turbidity < 0.1 NTU · pH 6.5–8.5",
        "Mass rates: TBD — not invented",
    ], fill="#f8fafc", edge="#64748b")

    S.callout(ax, 2, 5.5, 60, 5.5, "MACHINE / PROCESS LIST (locked tags)", [
        "GREY_SCREEN · GREY_BIO · GREY_MED · GREY_BUFF · BLACK_COLLECT · BLACK_DIGEST · BLACK_MED",
        "VCD_FEED · VCD_HX · VCD_EVAP · VCD_COMP · VCD_COND · HAB_ED_POLISH · REMIN · POTABLE_TANK · HAB_UV · HAB_BOOST",
        "CAD rooms: HAB_WATER · HAB_WASTE · WETROOM_HAB_NW  ·  Detail: docs-authority/HAB_WATER.md",
    ], fill="#e0f2fe", edge="#0369a1")

    S.legend(ax, 2.0, 0.6)
    S.graph_bridge_note(ax, _GP, "S01/S12/S21/S25–S29")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — hab_water", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-WTR-001 / AQS-EQP-HAB-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
