#!/usr/bin/env python3
"""Shared drawing primitives for the PFD sheets."""
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import params as P


def box(ax, x, y, w, h, fill, edge, title, sub="", lw=1.55, ts=None, ss=None):
    ts = P.FONT_BOX if ts is None else ts
    ss = P.FONT_BOX_SUB if ss is None else ss
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.10,rounding_size=0.26",
        facecolor=fill, edgecolor=edge, linewidth=lw, zorder=3,
    ))
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=P.INK, zorder=4, linespacing=1.1)
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                fontsize=ss, color=P.MUTED, zorder=4, linespacing=1.15)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=P.INK, zorder=4, linespacing=1.1)
    return (x, y, w, h)


def cx(b):
    return b[0] + b[2] / 2


def cy(b):
    return b[1] + b[3] / 2


def R(b):
    return (b[0] + b[2], cy(b))


def L(b):
    return (b[0], cy(b))


def T(b):
    return (cx(b), b[1] + b[3])


def B(b):
    return (cx(b), b[1])


def arrow(ax, p1, p2, color, lw=1.7, rad=0.0, ls="-"):
    ax.annotate(
        "", xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}",
            linestyle=ls, shrinkA=0.5, shrinkB=0.5,
        ),
        zorder=2,
    )


def slabel(ax, x, y, text, color=None, ha="center", va="bottom", size=None):
    ax.text(x, y, text, ha=ha, va=va,
            fontsize=P.FONT_LABEL if size is None else size,
            color=P.MUTED if color is None else color,
            zorder=5, fontstyle="italic")


def hx_diamond(ax, x, y, name, sub=""):
    s = 1.8
    ax.add_patch(Polygon(
        [(x, y + s), (x + s, y), (x, y - s), (x - s, y)],
        closed=True, facecolor=P.C_HX_F, edgecolor=P.C_HX, linewidth=1.35, zorder=6,
    ))
    ax.text(x, y + s + 0.36, name, ha="center", va="bottom",
            fontsize=10.8, fontweight="bold", color=P.C_HX, zorder=6)
    if sub:
        ax.text(x, y - s - 0.26, sub, ha="center", va="top",
                fontsize=9.3, color=P.C_HEAT, zorder=6)
    return (x, y)


def mem_bar(ax, x, y, w, h, kind):
    if kind == "CEM":
        ax.add_patch(Rectangle((x, y), w, h, facecolor=P.C_CEM_F, edgecolor=P.C_CEM,
                               linewidth=1.3, zorder=5))
        if h > 2.2:
            ax.text(x + w / 2, y + h / 2, "CEM", ha="center", va="center",
                    fontsize=12.7, fontweight="bold", color=P.C_CEM, rotation=90, zorder=6)
    elif kind == "AEM":
        ax.add_patch(Rectangle((x, y), w, h, facecolor=P.C_AEM_F, edgecolor=P.C_AEM,
                               linewidth=1.3, zorder=5))
        if h > 2.2:
            ax.text(x + w / 2, y + h / 2, "AEM", ha="center", va="center",
                    fontsize=12.7, fontweight="bold", color=P.C_AEM, rotation=90, zorder=6)
    elif kind == "BPM_BO":
        ax.add_patch(Rectangle((x, y), w / 2, h, facecolor=P.C_CEM_F, edgecolor=P.C_CEM,
                               linewidth=1.2, zorder=5))
        ax.add_patch(Rectangle((x + w / 2, y), w / 2, h, facecolor=P.C_AEM_F, edgecolor=P.C_AEM,
                               linewidth=1.2, zorder=5))
        if h > 2.4:
            ax.text(x + w / 2, y + h / 2, "BPM", ha="center", va="center",
                    fontsize=12.4, fontweight="bold", color=P.INK, rotation=90, zorder=6)
