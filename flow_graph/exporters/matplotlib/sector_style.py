#!/usr/bin/env python3
"""Shared helpers for sector / block PFDs (AQS-PFD-*-001 sheets)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent if _HERE.name in ("pfd_scripts", "scripts") else _HERE
OUT_DIR = ROOT / "images" if (ROOT / "images").is_dir() else ROOT

# Stream palette aliases matching orphan Wave-2 legend language
C_SCRAP = P.C_SOLID
C_LIQUOR = P.C_LEACH
C_ORG = P.C_OIL
C_UTIL = P.C_INORG
C_HVAC = P.C_HEAT
C_PRODUCT = P.C_PROD
C_H2 = P.C_CA
C_OX = P.C_AN

UNIT_F, UNIT_E = "#e0f2fe", "#0369a1"
IFACE_F, IFACE_E = "#fafaf9", "#57534e"
RULE_F, RULE_E = "#fff7ed", "#c2410c"
STUB_F, STUB_E = "#f5f5f4", "#78716c"
TBD_F, TBD_E = "#fef3c7", "#b45309"


def new_fig(w=18.0, h=12.0, dpi=140):
    fig, ax = plt.subplots(figsize=(w, h), dpi=dpi)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(P.BG)
    ax.set_facecolor(P.BG)
    return fig, ax


def title_block(ax, doc_no, name, subtitle, x=50, y=68.2):
    ax.text(x, y, f"{doc_no}  ·  {name}", ha="center", va="top",
            fontsize=25.6, fontweight="bold", color=P.INK)
    ax.text(x, y - 2.0, subtitle, ha="center", va="top",
            fontsize=14.3, color=P.MUTED)


def unit(ax, x, y, w, h, title, sub="", fill=None, edge=None, ts=16.3, ss=11.5):
    return box(ax, x, y, w, h,
               UNIT_F if fill is None else fill,
               UNIT_E if edge is None else edge,
               title, sub, ts=ts, ss=ss)


def iface(ax, x, y, w, h, title, sub="", fill=None, edge=None):
    return box(ax, x, y, w, h,
               IFACE_F if fill is None else fill,
               IFACE_E if edge is None else edge,
               title, sub, ts=15.5, ss=11.2)


def stub(ax, x, y, w, h, title, sub="STUB — next pass"):
    """Dashed stub for upcoming design (water purification, terrace, etc.)."""
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.2",
        facecolor=STUB_F, edgecolor=STUB_E, linewidth=1.35,
        linestyle="--", zorder=3,
    ))
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
            fontsize=15.2, fontweight="bold", color=P.INK, zorder=4)
    ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
            fontsize=10.8, color=P.MUTED, zorder=4, style="italic")
    return (x, y, w, h)


def tbd(ax, x, y, w, h, title, sub="TBD — next pass"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.2",
        facecolor=TBD_F, edgecolor=TBD_E, linewidth=1.45,
        linestyle="--", zorder=3,
    ))
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
            fontsize=14.9, fontweight="bold", color=TBD_E, zorder=4)
    ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
            fontsize=10.8, color=P.MUTED, zorder=4, style="italic")
    return (x, y, w, h)


def rule(ax, x, y, w, h, text):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.06,rounding_size=0.14",
        facecolor=RULE_F, edgecolor=RULE_E, linewidth=1.25, zorder=3,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=11.8, color=RULE_E, zorder=4, fontweight="bold")
    return (x, y, w, h)


def callout(ax, x, y, w, h, title, lines, fill="#fafaf9", edge=P.MUTED):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.18",
        facecolor=fill, edgecolor=edge, linewidth=1.1, zorder=3,
    ))
    ax.text(x + 0.6, y + h - 0.55, title, ha="left", va="top",
            fontsize=13, fontweight="bold", color=P.INK, zorder=4)
    ax.text(x + 0.6, y + h - 1.55, "\n".join(lines), ha="left", va="top",
            fontsize=10.5, color=P.MUTED, zorder=4, linespacing=1.25)
    return (x, y, w, h)


def legend(ax, x=2.0, y=1.2):
    streams = [
        (C_SCRAP, "solid / scrap"),
        (C_LIQUOR, "leach / liquor"),
        (C_ORG, "organics / oil"),
        (C_UTIL, "inorganic util"),
        (C_HVAC, "heat / grey / HVAC"),
        (C_PRODUCT, "product"),
        (C_H2, "cathode / H2"),
        (C_OX, "anode / oxidizer"),
    ]
    ax.text(x, y + 2.6, "STREAMS", fontsize=11.5, fontweight="bold", color=P.INK)
    for i, (c, lab) in enumerate(streams):
        xx = x + (i % 4) * 12.5
        yy = y + 1.5 - (i // 4) * 1.15
        ax.plot([xx, xx + 2.2], [yy, yy], color=c, lw=2.2)
        ax.text(xx + 2.6, yy, lab, va="center", fontsize=9.9, color=P.MUTED)

    ax.text(x + 52, y + 2.6, "MARKS", fontsize=11.5, fontweight="bold", color=P.INK)
    marks = [
        (UNIT_F, UNIT_E, "-", "unit"),
        (RULE_F, RULE_E, "-", "rule"),
        (STUB_F, STUB_E, "--", "stub (next pass)"),
        (TBD_F, TBD_E, "--", "TBD interface"),
    ]
    for i, (f, e, ls, lab) in enumerate(marks):
        xx = x + 52 + (i % 2) * 18
        yy = y + 1.5 - (i // 2) * 1.15
        ax.add_patch(Rectangle((xx, yy - 0.35), 1.6, 0.7,
                               facecolor=f, edgecolor=e, lw=1.0, linestyle=ls))
        ax.text(xx + 2.0, yy, lab, va="center", fontsize=9.9, color=P.MUTED)

    ax.text(x + 88, y + 1.0, "S01 = stream ID\nHDR_* = header",
            ha="left", va="center", fontsize=9.6, color=P.MUTED)


def footer(ax, doc_no, fname, authority="AQS-STR-001 / AQS-MF-001 / AQS-CMP-001"):
    ax.text(50, 0.35,
            f"{doc_no}  ·  {authority}  ·  CERN-OHL-S  ·  {fname}  ·  regenerate: python3 pfd_scripts/{fname.replace('.png', '.py')}",
            ha="center", va="bottom", fontsize=9.6, color=P.MUTED)


def graph_bridge_note(ax, gp_name, note, y=65.8):
    """Subtitle line under title_block for graph-bridged sector sheets."""
    ax.text(50, y, f"Graph-bridged from {gp_name}  ·  {note}",
            ha="center", va="top", fontsize=11.8, color=P.MUTED)


def graph_register(ax, lines, title, x=2.0, y=7.5, max_lines=14):
    """Compact graph edge register (null rates stay null)."""
    ax.text(x, y, title, fontsize=11.8, fontweight="bold", color=P.INK, zorder=5)
    for i, line in enumerate(lines[:max_lines]):
        ax.text(x, y - 0.85 - i * 0.55, line, ha="left", va="top",
                fontsize=9, color=P.MUTED, zorder=5)
    if len(lines) > max_lines:
        ax.text(x, y - 0.85 - max_lines * 0.55,
                f"… +{len(lines) - max_lines} more (see plant_flow_graph.json)",
                ha="left", va="top", fontsize=8.7, color=P.MUTED, zorder=5)


def save(fig, fname):
    out = OUT_DIR / fname
    fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)
    return out
