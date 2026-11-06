# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Derived tier/row grid for the SA-312 tube-rack units (A-M-167).

The booked tube count, the bank split and the rack envelope come from the graph
node design block (written by ``flow_graph/param/receivers.py``); the grid
drivers (tubes per rack row, row pitch, rack allowance, manifolded halves) come
from ``flow_graph/param/drivers.json``, register A-M-167. The grid fills the
booked tube count exactly, so the drawn solids equal the booked tubes, and it
balances the manifolded relief halves at every tier. There is no hard-coded
tier or row arithmetic left in the builders.

The fill rule: banks in the graph design block's order, tier by tier from the
lower tier, the two halves interleaved station by station (half 1 station 1,
half 2 station 1, half 1 station 2, ...). A single bank therefore spreads every
tier evenly across the halves, and a second bank (the CRYO_O2 crew reserve)
takes the tail slots of the highest tier it reaches, at the +y end of each
half, where the builder places its divider plate.

The envelope consistency is asserted: the rack height minus its allowance must
equal the derived tier count times the row pitch, and the rack width minus its
allowance must equal the tubes-per-row driver times the row pitch, exactly as
``receivers.py`` sized them.
"""
import json, math, os

_LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_LIB)))
_DRV = os.path.join(ROOT, "flow_graph", "param", "drivers.json")
_KEY = "CRYO.cold-box-asu-recovery-train.cold-box."


def _val(drv, key):
    return drv[key]["value"]


def rack_grid(design, size_mm, skid_t_mm=12.0):
    """The derived grid for one unit.

    Returns a dict with ``per_row``, ``pitch_mm``, ``halves``, ``rows_z``,
    ``stations_y``, ``tiers_z``, ``fill`` (a list of ``(y_mm, z_mm, bank)``
    tuples, lower tier first), ``per_half_tubes`` and ``drawn`` (the fill
    length, equal to the booked tube count).
    """
    L, W, H = (float(v) for v in size_mm)
    with open(_DRV) as fh:
        drv = json.load(fh)
    per_row = int(_val(drv, _KEY + "rcv_tubes_per_row"))
    pitch = float(_val(drv, _KEY + "rcv_row_pitch_mm"))
    allow = float(_val(drv, _KEY + "rcv_rack_allow_mm"))
    halves = int(_val(drv, _KEY + "rcv_manifold_halves"))
    nt = int(design["tubes"])

    rows_z = math.ceil(nt / per_row)                       # the receivers.py rack rows
    assert H - allow == rows_z * pitch, f"rack height {H} vs {rows_z} tiers x {pitch} + {allow}"
    assert W - allow == per_row * pitch, f"rack width {W} vs {per_row} rows x {pitch} + {allow}"

    band0 = (W - per_row * pitch) / 2.0                    # stations centred in the tube band
    stations_y = [band0 + pitch / 2.0 + k * pitch for k in range(per_row)]
    margin = (H - skid_t_mm - rows_z * pitch) / 2.0
    tiers_z = [skid_t_mm + margin + pitch / 2.0 + i * pitch for i in range(rows_z)]

    banks = design.get("banks") or [{"bank": "main", "tubes": nt, "halves": halves}]
    remaining = [(b["bank"], int(b["tubes"])) for b in banks]
    interleave = [(h, s) for s in range(per_row // halves) for h in range(halves)]
    fill = []
    for z in tiers_z:
        for h, s in interleave:
            if not remaining:
                break
            bank, n = remaining[0]
            fill.append((stations_y[h * per_row // halves + s], z, bank))
            if n == 1:
                remaining.pop(0)
            else:
                remaining[0] = (bank, n - 1)
        if not remaining:
            break
    assert not remaining, f"grid holds {per_row * rows_z} slots for {nt} booked tubes"

    per_half = [sum(1 for y, _, _ in fill
                    if (y < W / 2.0) == (h == 0)) for h in range(halves)]
    return {"per_row": per_row, "pitch_mm": pitch, "allow_mm": allow, "halves": halves,
            "rows_z": rows_z, "stations_y": stations_y, "tiers_z": tiers_z,
            "fill": fill, "per_half_tubes": per_half, "drawn": len(fill)}
