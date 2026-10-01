#!/usr/bin/env python3
"""Flat patterns, 4x8 nest, cut list, assembly sketch.

    python3 generate.py
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from matplotlib.collections import PatchCollection

import params as P

OUT = Path(__file__).resolve().parent
BG = "#f3efe6"
INK = "#1c1917"
MUTED = "#44403c"
BOARD = "#e8e4d9"
MARK = "#1d4ed8"


def slant(top, bot, drop):
    return math.hypot((top - bot) / 2.0, drop)


def parts_one_cell():
    """Return list of (name, w, h, qty_note) for one cell. Tabs included."""
    sx = slant(P.OD_L, P.THROAT + 2 * P.T, P.FUNNEL_H)
    sy = slant(P.OD_W, P.THROAT + 2 * P.T, P.FUNNEL_H)
    return [
        ("BOTTOM", P.OD_L, P.OD_W, "open to funnel; 16 mm hole later"),
        ("WALL_Y+", P.OD_L, P.ID_H, "anode long wall; sits on 212-edge"),
        ("WALL_Y-", P.OD_L, P.ID_H, "cathode long wall; sits on 212-edge"),
        ("WALL_X+", P.ID_W, P.ID_H, "overflow end; notch after glue-up"),
        ("WALL_X-", P.ID_W, P.ID_H, "inlet end; sits between longs"),
        ("FUNNEL_X", P.OD_L + 2 * P.TAB, sx + P.TAB, "qty 2; side tabs"),
        ("FUNNEL_Y", P.OD_W + 2 * P.TAB, sy + P.TAB, "qty 2; side tabs"),
        ("THROAT", P.THROAT + 4 * P.T, P.THROAT + 4 * P.T, "16 mm hole at centre"),
        ("CEM_RIB", P.RIB_L, P.RIB_H, "qty 2"),
        ("WEIR", 50, 30, "glued on +X after notch"),
    ]


def explode_bom():
    rows = []
    for name, w, h, note in parts_one_cell():
        qty = 2 if name in ("FUNNEL_X", "FUNNEL_Y", "CEM_RIB") else 1
        qty *= P.N_CELLS
        rows.append(dict(name=name, w=w, h=h, qty=qty, note=note, group="cell"))
    # bund — one deck may exceed one sheet width; split into 2 planks
    plank_w = P.AISLE_W + 2 * P.T
    plank_l = P.AISLE_LEN + 2 * P.T
    if plank_l > P.SHEET_L - 2 * P.MARGIN:
        raise SystemExit("bund deck longer than 8 ft — drop scale")
    rows.append(dict(name="BUND_DECK", w=plank_l, h=plank_w, qty=1,
                     note="cells sit on this", group="bund"))
    rows.append(dict(name="BUND_LONG", w=plank_l, h=P.BUND_H, qty=2,
                     note="sits on deck", group="bund"))
    rows.append(dict(name="BUND_END", w=plank_w, h=P.BUND_H, qty=2,
                     note="inside longs", group="bund"))
    rows.append(dict(name="LABEL", w=80, h=28, qty=P.N_CELLS,
                     note="EW-n + metal", group="misc"))
    return rows


def instances(rows):
    inst = []
    for r in rows:
        for i in range(int(r["qty"])):
            inst.append(dict(name=r["name"], w=float(r["w"]), h=float(r["h"]),
                             i=i, group=r["group"]))
    return inst


def pack(inst):
    """Shelf pack onto 4x8 sheets. Rotate if the other orientation fits a gap better."""
    items = sorted(inst, key=lambda p: max(p["w"], p["h"]), reverse=True)
    sheets = []  # list of {used: [(x,y,w,h,name,i)], shelves: [(y, height, xcursor)]}

    def new_sheet():
        return dict(used=[], y=P.MARGIN, row_h=0, x=P.MARGIN)

    sheets.append(new_sheet())

    usable_w = P.SHEET_W - 2 * P.MARGIN
    usable_l = P.SHEET_L - 2 * P.MARGIN

    for p in items:
        cands = [(p["w"], p["h"], False), (p["h"], p["w"], True)]
        cands = [c for c in cands if c[0] <= usable_l and c[1] <= usable_w]
        if not cands:
            raise SystemExit("part %s %.0fx%.0f does not fit a 4x8" % (
                p["name"], p["w"], p["h"]))
        placed = False
        for s in sheets:
            for w, h, rot in sorted(cands, key=lambda c: c[1]):
                if s["x"] + w <= P.SHEET_L - P.MARGIN and (
                        s["row_h"] == 0 or h <= s["row_h"] or
                        s["x"] == P.MARGIN):
                    if s["row_h"] == 0:
                        s["row_h"] = h
                    if h > s["row_h"] and s["x"] == P.MARGIN:
                        s["row_h"] = h
                    if s["x"] + w <= P.SHEET_L - P.MARGIN and h <= max(s["row_h"], h):
                        if h <= s["row_h"] or s["x"] == P.MARGIN:
                            s["used"].append((s["x"], s["y"], w, h, p["name"], p["i"], rot))
                            s["x"] += w + P.KERF
                            s["row_h"] = max(s["row_h"], h)
                            placed = True
                            break
            if placed:
                break
            # new row on this sheet
            for w, h, rot in sorted(cands, key=lambda c: c[1]):
                ny = s["y"] + s["row_h"] + P.KERF
                if ny + h <= P.SHEET_W - P.MARGIN and w <= usable_l:
                    s["y"] = ny
                    s["x"] = P.MARGIN
                    s["row_h"] = h
                    s["used"].append((s["x"], s["y"], w, h, p["name"], p["i"], rot))
                    s["x"] += w + P.KERF
                    placed = True
                    break
            if placed:
                break
        if not placed:
            s = new_sheet()
            w, h, rot = min(cands, key=lambda c: c[1])
            s["row_h"] = h
            s["used"].append((s["x"], s["y"], w, h, p["name"],  p["i"], rot))
            s["x"] += w + P.KERF
            sheets.append(s)
    return sheets


def draw_sheet(s, n, path):
    fig, ax = plt.subplots(figsize=(16, 8.2), facecolor=BG)
    ax.set_facecolor(BG)
    ax.add_patch(Rectangle((0, 0), P.SHEET_L, P.SHEET_W,
                           facecolor=BOARD, edgecolor=INK, lw=1.2))
    ax.add_patch(Rectangle((P.MARGIN, P.MARGIN),
                           P.SHEET_L - 2 * P.MARGIN, P.SHEET_W - 2 * P.MARGIN,
                           fill=False, edgecolor="#a8a29e", lw=0.5, ls="--"))
    colors = {
        "BOTTOM": "#dcfce7", "WALL_Y+": "#dbeafe", "WALL_Y-": "#dbeafe",
        "WALL_X+": "#e0e7ff", "WALL_X-": "#e0e7ff",
        "FUNNEL_X": "#ffedd5", "FUNNEL_Y": "#fed7aa",
        "THROAT": "#fecaca", "CEM_RIB": "#93c5fd", "WEIR": "#fde68a",
        "BUND_DECK": "#e7e5e4", "BUND_LONG": "#d6d3d1", "BUND_END": "#d6d3d1",
        "LABEL": "#fef9c3",
    }
    used = 0.0
    for x, y, w, h, name, i, rot in s["used"]:
        ax.add_patch(Rectangle((x, y), w, h,
                               facecolor=colors.get(name, "#fff"),
                               edgecolor=INK, lw=0.5))
        label = "%s-%d" % (name, i + 1) if i else name
        if name.startswith("BUND") or name == "LABEL":
            label = "%s %d" % (name, i + 1)
        fs = 5.5 if min(w, h) > 40 else 4.5
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fs, color=INK, rotation=90 if rot and h > w else 0)
        used += w * h
    area = P.SHEET_L * P.SHEET_W
    ax.set_aspect("equal")
    ax.set_xlim(-20, P.SHEET_L + 20)
    ax.set_ylim(-20, P.SHEET_W + 40)
    ax.set_xlabel("mm along 8 ft")
    ax.set_ylabel("mm along 4 ft")
    ax.set_title("Sheet %d of foam PVC 4×8 ft  (%.0f%% area)" % (
        n, 100 * used / area), fontsize=13, color=INK, fontweight="bold")
    fig.text(0.01, 0.01,
             "AQS-FOAM-001  6 mm expanded PVC  kerf %d mm  walls on bottom" % P.KERF,
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(path, dpi=140)
    plt.close(fig)


def draw_cell_pattern(path):
    """One-cell unfolding so the glue sequence is obvious."""
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=BG)
    ax.set_facecolor(BG)
    # cross unfold: Y- | BOTTOM | Y+    and X walls above/below
    bx, by = 250, 200
    ax.add_patch(Rectangle((bx, by), P.OD_L, P.OD_W, facecolor="#dcfce7",
                           edgecolor=INK, lw=1))
    ax.text(bx + P.OD_L / 2, by + P.OD_W / 2, "BOTTOM\n%d×%d" % (P.OD_L, P.OD_W),
            ha="center", va="center", fontsize=9)
    ax.add_patch(Rectangle((bx, by + P.OD_W), P.OD_L, P.ID_H,
                           facecolor="#dbeafe", edgecolor=INK, lw=1))
    ax.text(bx + P.OD_L / 2, by + P.OD_W + P.ID_H / 2, "WALL_Y+\nanode",
            ha="center", va="center", fontsize=8)
    ax.add_patch(Rectangle((bx, by - P.ID_H), P.OD_L, P.ID_H,
                           facecolor="#dbeafe", edgecolor=INK, lw=1))
    ax.text(bx + P.OD_L / 2, by - P.ID_H / 2, "WALL_Y−\ncathode",
            ha="center", va="center", fontsize=8)
    ax.add_patch(Rectangle((bx - P.ID_W, by), P.ID_W, P.OD_W,
                           facecolor="#e0e7ff", edgecolor=INK, lw=1))
    ax.text(bx - P.ID_W / 2, by + P.OD_W / 2, "X−\ninlet",
            ha="center", va="center", fontsize=8, rotation=90)
    ax.add_patch(Rectangle((bx + P.OD_L, by), P.ID_W, P.OD_W,
                           facecolor="#e0e7ff", edgecolor=INK, lw=1))
    ax.text(bx + P.OD_L + P.ID_W / 2, by + P.OD_W / 2, "X+\noverflow",
            ha="center", va="center", fontsize=8, rotation=90)
    # funnel traps to the right
    sx = slant(P.OD_L, P.THROAT + 2 * P.T, P.FUNNEL_H)
    fx = bx + P.OD_L + P.ID_W + 40
    fy = 80
    top = P.OD_L
    bot = P.THROAT + 2 * P.T
    ax.add_patch(Polygon(
        [(fx, fy), (fx + top, fy),
         (fx + top - (top - bot) / 2, fy + sx),
         (fx + (top - bot) / 2, fy + sx)],
        closed=True, facecolor="#ffedd5", edgecolor=INK, lw=1))
    ax.text(fx + top / 2, fy + sx / 2, "FUNNEL_X  ×2", ha="center", va="center",
            fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlim(0, 900)
    ax.set_ylim(0, 650)
    ax.axis("off")
    ax.set_title("One cell — unfold (walls sit on BOTTOM)", fontsize=13,
                 fontweight="bold", color=INK)
    fig.text(0.02, 0.02,
             "Glue longs first, then ends, then funnel tabs to BOTTOM underside. "
             "CEM ribs last. Overflow notch after the box is square.",
             fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def draw_aisle(path):
    fig, ax = plt.subplots(figsize=(16, 5.2), facecolor=BG)
    ax.set_facecolor(BG)
    deck_l = P.AISLE_LEN + 2 * P.T
    deck_w = P.AISLE_W + 2 * P.T
    ax.add_patch(Rectangle((0, 0), deck_l, deck_w,
                           facecolor="#e7e5e4", edgecolor=INK, lw=1))
    ax.add_patch(Rectangle((P.T, P.T), P.AISLE_LEN, P.AISLE_W,
                           fill=False, edgecolor="#a8a29e", lw=0.6))
    for i, metal in enumerate(P.METALS):
        x = P.T + i * P.PITCH + (P.PITCH - P.OD_L) / 2
        y = P.T + P.BUND_PAD
        ax.add_patch(Rectangle((x, y), P.OD_L, P.OD_W,
                               facecolor="#f4f1ea", edgecolor=INK, lw=0.8))
        ax.plot([x + P.OD_L / 2, x + P.OD_L / 2],
                [y + P.T, y + P.OD_W - P.T], color="#1d4ed8", lw=1.2)
        ax.text(x + P.OD_L / 2, y + P.OD_W / 2,
                "EW-%d\n%s" % (i + 1, metal),
                ha="center", va="center", fontsize=8, color=INK)
        if i < P.N_CELLS - 1:
            ax.annotate("",
                        xy=(x + P.OD_L + (P.PITCH - P.OD_L) / 2 + 8,
                            y + P.OD_W * 0.7),
                        xytext=(x + P.OD_L - 4, y + P.OD_W * 0.7),
                        arrowprops=dict(arrowstyle="-|>", color="#166534", lw=1))
    ax.set_aspect("equal")
    ax.set_xlim(-30, deck_l + 30)
    ax.set_ylim(-40, deck_w + 50)
    ax.axis("off")
    ax.set_title("Foam EW CASCADE  1:3  overflow +X  CEM mid-plane  "
                 "pitch %d mm" % P.PITCH,
                 fontsize=13, fontweight="bold", color=INK)
    ax.text(deck_l / 2, -28,
            "Bund %d × %d mm OD  ·  cell ID %d × %d × %d  ·  6 mm foam PVC" % (
                deck_l, deck_w, P.ID_L, P.ID_W, P.ID_H),
            ha="center", fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def write_cut_list(rows, n_sheets, path):
    lines = [
        "# Foam EW cascade — cut list",
        "",
        "Document number: AQS-FOAM-001  ",
        "Revision: A  ",
        "Date: 2026-09-27",
        "",
        "Scale 1:3. Sheet 4×8 ft (1219 × 2438 mm). Thickness 6 mm expanded PVC.",
        "Duty: wet Salria coupon at bench temperature. Not the 70–85 °C plant wall.",
        "Kerf allowance in the nest: %d mm. Walls sit on BOTTOM." % P.KERF,
        "",
        "| Part | Qty | Blank mm | Notes |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append("| %s | %d | %.0f × %.0f | %s |" % (
            r["name"], r["qty"], r["w"], r["h"], r["note"]))
    cell_area = sum(r["w"] * r["h"] * r["qty"] for r in rows)
    sheet_area = P.SHEET_L * P.SHEET_W
    lines += [
        "",
        "## Buy",
        "",
        "- Expanded PVC foam board 6 mm, 4×8 ft × **%d** (plus one spare if the first sheet chips)." % n_sheets,
        "- PVC solvent for foam (Weld-On 4052 / equivalent) + 6 mm acrylic/PVC square as CEM stand-in.",
        "- PVC or CPVC tube OD ~16 mm for nine drain stubs (same family as the board).",
        "- Fine marker + straightedge + snap-off knife + sanding block.",
        "",
        "## Glue order (one cell)",
        "",
        "1. Square BOTTOM. Mark the inside of the four walls.",
        "2. Glue WALL_Y− and WALL_Y+ on the 212 mm edges of BOTTOM.",
        "3. Drop WALL_X− / WALL_X+ between them. Fillet every inside corner.",
        "4. Cut the overflow notch in WALL_X+ only after the box is square.",
        "5. Glue FUNNEL_X / FUNNEL_Y tabs to the underside of BOTTOM. Cap with THROAT.",
        "6. CEM ribs last, 6 mm gap on the mid-plane, blue toward cathode (−Y).",
        "7. Set the nine cells on BUND_DECK at 250 mm centres. Overflow points +X.",
        "8. Solvent-cure fully. Fillet both faces of every seam before Salria fill.",
        "",
        "Blank area %.2f m². %d sheets × %.2f m² = %.2f m². "
        "Nest figure is the buy count." % (
            cell_area / 1e6, n_sheets, sheet_area / 1e6,
            n_sheets * sheet_area / 1e6),
        "",
        "Foam-core PVC at bench T. Plant wet wall remains solid CPVC at 70–85 °C.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(rows, path):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "qty", "w_mm", "h_mm", "group", "note"])
        w.writeheader()
        for r in rows:
            w.writerow(dict(name=r["name"], qty=r["qty"], w_mm="%.1f" % r["w"],
                            h_mm="%.1f" % r["h"], group=r["group"], note=r["note"]))


def build():
    rows = explode_bom()
    inst = instances(rows)
    sheets = pack(inst)
    draw_cell_pattern(OUT / "cell_unfold.png")
    draw_aisle(OUT / "aisle.png")
    for i, s in enumerate(sheets, 1):
        draw_sheet(s, i, OUT / ("nest_sheet_%d.png" % i))
    write_cut_list(rows, len(sheets), OUT / "CUT_LIST.md")
    write_csv(rows, OUT / "cut_list.csv")
    print("parts", sum(r["qty"] for r in rows))
    print("sheets", len(sheets))
    for i, s in enumerate(sheets, 1):
        print(" sheet", i, "panels", len(s["used"]))


if __name__ == "__main__":
    build()
