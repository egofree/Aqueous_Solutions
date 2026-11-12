# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""The committed CRYO_O2 and CRYO_CO2 nozzle datums still land where they are
drawn (F-20261109-10).

The schedule CSVs (`docs-authority/nozzles/CRYO_O2.csv`, `CRYO_CO2.csv`) store
each connection's datum as a fixed number. The rack builders draw a side
connection at that datum only while it fits a side-rail band of the rack
(`models/mfg/lib/nozzle_bands.py`); the vent draws flush at the rack top and
the drain stub tips at the 50 mm skid datum. A rack-height change moves the
bands without touching the CSVs, so a stored datum could silently re-clamp.
This gate re-runs the builders' own datum rule - the same shared module, the
same graph reader, the same band sets - against every committed row and the
committed check reports, and fails naming the unit and the tag when a datum
would no longer be drawn as issued or when the build records no longer match
the schedule.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "models", "mfg"))

from lib import dn, graph_node, nozzle_bands  # noqa: E402

# the house face mapping the builders apply to the schedule CSV (lib FACE_OF)
SIDE_FACE = {"inlet": "-Y", "outlet": "+Y"}
SKID_DATUM_MM = 50.0          # the bottom-stub tip datum both builders draw
UNITS = {"CRYO_O2": nozzle_bands.cryo_o2_bands, "CRYO_CO2": nozzle_bands.cryo_co2_bands}


def _problems(unit):
    bands_fn = UNITS[unit]
    gn = graph_node.graph_node(unit)          # the same reader the builders use
    H = float(gn.size_mm[2])
    bands, clamp_band = bands_fn(H)
    built = json.load(open(os.path.join(ROOT, "models", "mfg", unit, "check.json")))["nozzles_drawn"]
    bad = []
    for row in gn.nozzles:
        tag, h, face = row["tag"], row["height_mm"], row["face"]
        if h is None:
            bad.append(f"{unit} {tag}: the schedule row carries no height_mm")
            continue
        side = SIDE_FACE.get(face)
        if side:
            od = dn.pipe_od("DN15") if row["size"] == "solids" else dn.pipe_od(row["size"])
            z, clamped = nozzle_bands.land_z(side, h, od, bands, clamp_band)
            if clamped:
                bad.append(
                    f"{unit} {tag} ({row['size']} {face} at {h:g} mm): the datum no longer "
                    f"fits a side-rail band of the {H:g} mm rack, so the builder would draw "
                    f"it clamped at {z:g} mm - revise the committed datum with the rack "
                    "change instead of re-clamping it silently")
        elif face == "top":
            z, clamped = H, True          # flush at the rack top, clamp note by template
            if h != z:
                bad.append(f"{unit} {tag} (top at {h:g} mm): the builder draws the vent "
                           f"flush at the {H:g} mm rack top; the committed datum must name "
                           "that figure")
        elif face == "bottom":
            z, clamped = SKID_DATUM_MM, False
            if h != z:
                bad.append(f"{unit} {tag} (bottom at {h:g} mm): the builder tips the drain "
                           f"stub at the {SKID_DATUM_MM:g} mm skid datum; the committed "
                           "datum must name that figure")
        else:
            bad.append(f"{unit} {tag}: the schedule row names no builder face ({face!r})")
            continue
        record = built.get(tag)
        if record is None:
            bad.append(f"{unit} {tag}: the committed check report records no build for this "
                       "row - run the builder so the records move with the schedule")
            continue
        if record["height_mm"] != h:
            bad.append(f"{unit} {tag}: the committed check report consumed height_mm "
                       f"{record['height_mm']:g}, but the schedule CSV datum is {h:g} mm - "
                       "run the builder so the records move with the schedule")
        if record["z_drawn_mm"] != z:
            bad.append(f"{unit} {tag}: the rule draws the connection at {z:g} mm, but the "
                       f"committed check report records {record['z_drawn_mm']:g} mm - run "
                       "the builder so the records move with the schedule")
        if clamped and "clamped" not in record["note"]:
            bad.append(f"{unit} {tag}: the row is drawn clamped, so its check-report note "
                       "must say so")
    return bad


def test_cryo_o2_datums_drawn_as_issued():
    assert _problems("CRYO_O2") == []


def test_cryo_co2_datums_drawn_as_issued():
    assert _problems("CRYO_CO2") == []


def test_rule_still_clamps_across_a_rack_height_change():
    """The land_z behavior the builders use: the committed top-band datum lands
    as issued at the built rack height and clamps to the clamp-band centre when
    a shorter rack moves the top band below it."""
    z, clamped = nozzle_bands.land_z("+Y", 520.0, dn.pipe_od("DN25"),
                                     *nozzle_bands.cryo_o2_bands(600.0))
    assert (z, clamped) == (520.0, False)
    z, clamped = nozzle_bands.land_z("+Y", 520.0, dn.pipe_od("DN25"),
                                     *nozzle_bands.cryo_o2_bands(540.0))
    assert (z, clamped) == (400.0, True)
