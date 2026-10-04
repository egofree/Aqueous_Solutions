#!/usr/bin/env python3
"""AQS-PFD-MEOH-001 — Methanol train (graph-bridged S73–S82 + IA-ESS-MEOH-*).

Sole topology authority: flow_graph/plant_flow_graph.json for stream IDs/rates.

Authority: AQS-MeOH-001, AQS-EQP-MEOH-001, AQS-REQ-KW-001, AQS-FC-001 Rev B,
AQS-STR-001 S73–S82, AQS-VENT-001, DEPENDENCIES.md (SEM-Tech IEM).
SCALE_M = 1.0. Stand-ins labeled — not BOM.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
import sector_style as S

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    load,
    meoh_ess_bridge_edges,
    meoh_mass_claim_edges,
)

DOC = "AQS-PFD-MEOH-001"
FNAME = "meoh_train_pfd.png"


def main():
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "METHANOL TRAIN",
        "Air/CO₂→MeOH (IEM+catalytic) + farm/hab ferment  ·  IEM-DMFC → BATT DC  ·  peer to PEM FC  ·  L0 POWER / process",
    )

    g = load()
    gp = graph_path().name
    ess = meoh_ess_bridge_edges(g)
    mass = {e.stream_id: e for e in meoh_mass_claim_edges(g)}
    ax.text(
        50, 63.6,
        f"Graph-bridged MeOH S73–S82 + IA-ESS-MEOH-* from {gp}  ·  null rates stay null",
        ha="center", va="top", fontsize=12.7, color="#57534e",
    )


    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  MeOH gap FILLED (not deferred).  Prefer IEM membranes (SEM-Tech / open IEM).  "
           "PEM H₂ FC retained.  REQ-MEOH-FC-CONT 0.5–2 kW_dc.  Stand-ins ≠ BOM.")

    # --- 1 Sources ---
    ax.text(2, 59.0, "1   MeOH SOURCES  (diverse)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    co2 = S.unit(ax, 2, 48, 14, 8.0, "CRYO_CO2 / S67",
                 "CO₂ feed\nS73",
                 fill="#e0f2fe", edge="#0369a1", ts=14.6, ss=10.5)
    h2 = S.unit(ax, 18, 48, 12, 8.0, "CRYO_H2",
                "surplus H₂\nS74",
                fill="#dbeafe", edge="#1e3a8a", ts=14.6, ss=10.5)
    iem = S.unit(ax, 32, 49, 16, 7.0, "MEOH_IEM_CELL",
                 "IEM electrochem\nSEM-Tech preferred",
                 fill="#fce7f3", edge="#9d174d", ts=14.3, ss=10.2)
    syn = S.unit(ax, 50, 49, 16, 7.0, "MEOH_SYNTH",
                 "CO₂+3H₂→MeOH\nstand-in CRI/AirCo",
                 fill="#fce7f3", edge="#9d174d", ts=14.3, ss=10.2)
    cond = S.unit(ax, 68, 49, 14, 7.0, "MEOH_COND/DIST",
                  "crude → fuel\nS75",
                  fill="#fce7f3", edge="#9d174d", ts=14.3, ss=10.2)
    ferm = S.unit(ax, 32, 39.5, 20, 7.0, "MEOH_FERM_DIG/STILL",
                  "farm/hab waste ferment\nS78 → S77  Partial",
                  fill="#dcfce7", edge="#15803d", ts=14, ss=10.2)
    tank = S.unit(ax, 68, 39.5, 14, 7.0, "MEOH_TANK",
                  "50–200 L study\nPC-11 / NFPA 30",
                  fill="#fef3c7", edge="#b45309", ts=14.3, ss=10.2)
    arrow(ax, R(co2), L(iem), S.C_OX, lw=1.3)
    arrow(ax, R(h2), (syn[0], cy(h2)), S.C_H2, lw=1.3)
    arrow(ax, R(iem), L(cond), "#9d174d", lw=1.4)
    arrow(ax, R(syn), (cond[0], cy(syn)), "#9d174d", lw=1.4)
    arrow(ax, B(cond), T(tank), "#9d174d", lw=1.3)
    arrow(ax, R(ferm), L(tank), "#15803d", lw=1.2)
    slabel(ax, 10, 57.2, "S73", S.C_OX, size=7.0)
    slabel(ax, 24, 57.2, "S74", S.C_H2, size=7.0)
    slabel(ax, 62, 57.2, "S75", "#9d174d", size=7.0)
    slabel(ax, 55, 38.2, "S77 / S78", "#15803d", size=6.8)

    # --- 2 FC electrical ---
    ax.text(2, 36.5, "2   IEM-DMFC  →  BATT DC  (peer to PEM)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    day = S.unit(ax, 2, 24, 14, 9.0, "MEOH_DAY_TANK",
                 "20–50 L\nS76",
                 fill="#fef3c7", edge="#b45309", ts=14.6, ss=10.5)
    mfc = S.unit(ax, 20, 23, 22, 11.0, "MEOH_FC",
                 "IEM-DMFC bank\n0.5–2 kW_dc cont.\nSI-DMFC-01 class",
                 fill="#fce7f3", edge="#9d174d", ts=16.3, ss=10.8)
    dcdc = S.unit(ax, 46, 24, 16, 9.0, "MEOH_DCDC",
                  "→ 160–700 V\nS79",
                  fill="#dbeafe", edge="#1e3a8a", ts=15.5, ss=10.8)
    sol = S.unit(ax, 66, 24, 20, 9.0, "SOL-ARK BATT DC",
                 "peer: ZnBr2 + PEM FC\n≠ GEN port",
                 fill="#dcfce7", edge="#15803d", ts=15.2, ss=10.5)
    pem = S.iface(ax, 88, 25, 10, 7.0, "PEM FC",
                  "AQS-PFD-FC-001\nS51 peer",
                  fill="#fff7ed", edge="#b45309")
    arrow(ax, (cx(tank), tank[1]), (cx(tank), 34), "#b45309", lw=1.2)
    arrow(ax, (cx(tank), 34), (cx(day), 34), "#b45309", lw=1.2)
    arrow(ax, (cx(day), 34), T(day), "#b45309", lw=1.2)
    arrow(ax, R(day), L(mfc), "#b45309", lw=1.5)
    arrow(ax, R(mfc), L(dcdc), S.C_PRODUCT, lw=1.5)
    arrow(ax, R(dcdc), L(sol), "#1e3a8a", lw=1.5)
    arrow(ax, R(sol), L(pem), "#b45309", lw=1.0, ls=":")
    slabel(ax, 12, 22.5, "S76", "#b45309", size=7.0)
    slabel(ax, 40, 22.5, "S79 DC", S.C_PRODUCT, size=7.0)

    # --- 3 Heat / HSE / returns ---
    ax.text(2, 20.5, "3   Q4 HEAT  ·  RETURNS  ·  HSE",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    hx = S.unit(ax, 2, 8, 18, 9.5, "MEOH_HX_Q4",
                "stack heat → Q4\nS80  < 80 °C",
                fill="#ffedd5", edge="#c2410c", ts=15.5, ss=10.5)
    q4 = S.iface(ax, 24, 9, 14, 8.0, "Q4 / HVAC",
                 "FARM + HAB\nS53/S54 peers",
                 fill="#ffedd5", edge="#c2410c")
    h2o = S.unit(ax, 42, 8, 16, 9.5, "S81 condensate",
                 "→ S13 class\nnot potable",
                 fill="#e0f2fe", edge="#0369a1", ts=14.9, ss=10.5)
    co2r = S.unit(ax, 62, 8, 16, 9.5, "S82 CO₂ Claimed",
                  "→ CRYO_CO2 / FARM\nno outdoor dump",
                  fill="#e0f2fe", edge="#0369a1", ts=14.6, ss=10.2)
    S.callout(ax, 82, 8, 16, 9.5, "HSE / FORBIDDEN", [
        "MeOH toxicity + IB fire",
        "LEL trip → fuel isolate",
        "No GEN port / RECT tee",
        "No free MeOH vent dump",
        "Spill → HDR_ORG only",
    ], fill="#fee2e2", edge="#b91c1c")
    arrow(ax, (cx(mfc), mfc[1]), (cx(mfc), 18.5), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, (cx(mfc), 18.5), (cx(hx), 18.5), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, (cx(hx), 18.5), T(hx), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, R(hx), L(q4), S.C_HVAC, lw=1.3)
    arrow(ax, R(q4), L(h2o), S.C_LIQUOR, lw=1.0, ls=":")
    arrow(ax, R(h2o), L(co2r), S.C_OX, lw=1.0, ls=":")
    slabel(ax, 14, 18.8, "S80", S.C_HVAC, size=6.8)

    S.legend(ax, 2.0, 1.0)
    out = S.OUT_DIR / FNAME
    # Graph ESS + mass claim overlay (rates from graph only)
    ax.text(2.0, 4.8, f"GRAPH MeOH / ESS  ({gp})", fontsize=13.2, fontweight="bold", color="#1c1917")
    y = 3.9
    for sid in [f"S{i:02d}" for i in range(73, 83)]:
        e = mass.get(sid)
        if e is None:
            continue
        ax.text(
            2.0, y,
            f"{e.stream_id}  {e.from_unit_id} → {e.to_unit_id}  ·  {edge_callout(e)}",
            fontsize=9.6, color="#57534e",
        )
        y -= 0.55
        if y < 0.4:
            break
    y2 = 3.9
    for key in ("MEOH_CHG", "MEOH_DIS", "S79_MEOH_FC"):
        e = ess.get(key)
        if e is None:
            continue
        ax.text(55.0, y2, edge_callout(e), fontsize=10.2, color="#57534e")
        y2 -= 0.65

    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"wrote {out}", flush=True)


if __name__ == "__main__":
    main()
