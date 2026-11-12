# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Side-rail datum rule for the CRYO cylinder-rack units (CRYO_O2, CRYO_CO2).

Pure arithmetic, no CadQuery. Each rack builder draws its schedule side
connections inside the landing bands of the side rails its frame places; a
schedule height that fits no band is clamped to the centre of the unit's
clamp band, and the builder names the clamp in its check report. The band sets
below are the rail spans the frames draw, with the top band expressed against
the rack height H, so a rack-height change moves it.

`flow_graph/test_cryo_nozzle_datums.py` re-runs this rule against the committed
schedules (`docs-authority/nozzles/CRYO_O2.csv`, `CRYO_CO2.csv`), the graph node
envelopes and the committed check reports, so a stored datum that a geometry
change would silently re-clamp fails the gate instead.
"""

CLEAR_MM = 2.0    # axis keep-out from a band edge, both racks


def cryo_o2_bands(H):
    """The CRYO_O2 side-rail landing bands in mm at rack height H, with the
    index of the band clamped rows land on (the mid rail)."""
    rails = [(100.0, 200.0), (350.0, 450.0), (H - 130.0, H - 30.0)]
    return {"-Y": list(rails), "+Y": list(rails)}, 1


def cryo_co2_bands(H):
    """The CRYO_CO2 side-rail landing bands in mm at rack height H, with the
    index of the band clamped rows land on (the bottom rail)."""
    rails = [(100.0, 200.0), (H - 120.0, H - 20.0)]
    return {"-Y": list(rails), "+Y": list(rails)}, 0


def land_z(face, h, od, bands, clamp_band):
    """The datum a side connection is drawn at: the schedule height when it
    fits a side-rail band with CLEAR_MM of edge keep-out either side of the
    pipe axis, else the centre of bands[face][clamp_band] (clamped; the caller
    names the clamp in its report)."""
    for (z0, z1) in bands[face]:
        if z0 + od / 2 + CLEAR_MM <= h <= z1 - od / 2 - CLEAR_MM:
            return h, False
    return (bands[face][clamp_band][0] + bands[face][clamp_band][1]) / 2, True
