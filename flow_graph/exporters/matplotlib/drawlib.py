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


# Legend rows shared by the line sheets. Artists are not clipped so the
# strip may sit below the axes limits.
LEGEND_STREAMS = (
    ("solid / scrap", "C_SOLID"),
    ("leach / acid liquor", "C_LEACH"),
    ("organics / oil", "C_OIL"),
    ("inorganic utility", "C_INORG"),
    ("heat / grey / HVAC", "C_HEAT"),
    ("product", "C_PROD"),
    ("cathode / H2", "C_CA"),
    ("anode / oxidizer", "C_AN"),
)


def legend_strip(ax, x, y, w=160.0, include=("streams", "marks"), row=2.4, size=None):
    """Draw labelled legend rows from (x, y) downward. Returns the y below the last row."""
    fs = 8.6 if size is None else size
    head = 12.0
    span = max(w - head, 1.0)
    kw = dict(clip_on=False, zorder=7)

    def caption(yy, text):
        ax.text(x, yy, text, ha="left", va="center", fontsize=fs + 1.6,
                fontweight="bold", color=P.INK, **kw)

    yy = y
    for part in include:
        if part == "streams":
            caption(yy, "STREAMS")
            step = span / len(LEGEND_STREAMS)
            for i, (label, cname) in enumerate(LEGEND_STREAMS):
                x0 = x + head + i * step
                ax.plot([x0, x0 + 2.4], [yy, yy], color=getattr(P, cname), lw=2.0,
                        solid_capstyle="butt", **kw)
                ax.text(x0 + 3.0, yy, label, ha="left", va="center", fontsize=fs,
                        color=P.MUTED, **kw)
        elif part == "marks":
            caption(yy, "MARKS")
            step = span / 5.0
            h = row * 0.62
            x0 = x + head
            ax.add_patch(FancyBboxPatch((x0, yy - h / 2), 3.0, h,
                                        boxstyle="round,pad=0.05,rounding_size=0.2",
                                        facecolor=P.C_PROD_F, edgecolor=P.C_PROD, lw=1.0, **kw))
            ax.text(x0 + 3.6, yy, "unit (locked name)", ha="left", va="center",
                    fontsize=fs, color=P.MUTED, **kw)
            x0 += step
            ax.add_patch(FancyBboxPatch((x0, yy - h / 2), 3.0, h,
                                        boxstyle="round,pad=0.05,rounding_size=0.2",
                                        facecolor=P.C_HEAT_F, edgecolor=P.C_HEAT, lw=1.0, **kw))
            ax.text(x0 + 3.6, yy, "rule (not equipment)", ha="left", va="center",
                    fontsize=fs, color=P.MUTED, **kw)
            x0 += step
            s = h / 2
            ax.add_patch(Polygon([(x0 + s, yy + s), (x0 + 2 * s, yy), (x0 + s, yy - s), (x0, yy)],
                                 closed=True, facecolor=P.C_HX_F, edgecolor=P.C_HX, lw=1.0, **kw))
            ax.text(x0 + 2 * s + 0.8, yy, "HX  Q1–Q4", ha="left", va="center",
                    fontsize=fs, color=P.MUTED, **kw)
            x0 += step
            ax.text(x0, yy, "S01", ha="left", va="center", fontsize=fs + 0.6,
                    fontstyle="italic", color=P.MUTED, **kw)
            ax.text(x0 + 3.6, yy, "stream ID (register)", ha="left", va="center",
                    fontsize=fs, color=P.MUTED, **kw)
            x0 += step
            ax.text(x0, yy, "HDR_*", ha="left", va="center", fontsize=fs + 0.6,
                    fontweight="bold", color=P.INK, **kw)
            ax.text(x0 + 4.6, yy, "header, not a vessel", ha="left", va="center",
                    fontsize=fs, color=P.MUTED, **kw)
        elif part == "membranes":
            caption(yy, "MEMBRANES")
            step = span / 5.0
            h = row * 0.22
            items = (("CEM", "CEM  cations pass"), ("AEM", "AEM  anions pass"),
                     ("BPM", "BPM  CEL | AEL  water splits"))
            for i, (kind, label) in enumerate(items):
                x0 = x + head + i * step
                if kind == "BPM":
                    ax.add_patch(Rectangle((x0, yy - h / 2), 1.2, h, facecolor=P.C_CEM_F,
                                           edgecolor=P.C_CEM, lw=1.0, **kw))
                    ax.add_patch(Rectangle((x0 + 1.2, yy - h / 2), 1.2, h, facecolor=P.C_AEM_F,
                                           edgecolor=P.C_AEM, lw=1.0, **kw))
                else:
                    fill = P.C_CEM_F if kind == "CEM" else P.C_AEM_F
                    edge = P.C_CEM if kind == "CEM" else P.C_AEM
                    ax.add_patch(Rectangle((x0, yy - h / 2), 2.4, h, facecolor=fill,
                                           edgecolor=edge, lw=1.0, **kw))
                ax.text(x0 + 3.0, yy, label, ha="left", va="center", fontsize=fs,
                        color=P.MUTED, **kw)
        else:
            raise ValueError("legend_strip: unknown row %r" % part)
        yy -= row
    return yy
