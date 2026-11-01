# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""The material table: alloys and polymers the shop builds from, their densities, and the
corrosion-allowance shop rule.

Authorities. `tables/materials.csv` is the material authority for the plant: this module
carries the per-class density values that file and the built models state, and
`unit_rows()` reads the file itself. The corrosion-allowance rule is the AQS-STD-001 shop
rule: polymer none, carbon steel in hydrocarbon service 1.5 mm, 316L, titanium and
graphite 0 mm. It is not a measured pit rate.

Where two built models state different densities for one class (PP: 905 kg/m3 in
`models/mfg/farm_hab.py`, 910 kg/m3 in `tables/materials.csv`), the authority file wins
for new work; the masses already recorded in those builds keep their own basis.
"""

# material class -> (density kg/m3, source)
DENSITY = {
    'CS': (7850.0, 'tables/materials.csv (A36 / S235 plate)'),
    'steel': (7850.0, 'models/mfg/farm_hab.py RHO'),
    '304': (8000.0, 'tables/materials.csv'),
    '316L': (8000.0, 'models/mfg/farm_hab.py RHO (SS316)'),
    'Ti_G2': (4510.0, 'tables/materials.csv (SB-338)'),
    'graphite': (1550.0, 'models/mfg/AL_POT/params.json ramming paste (wetted liner class)'),
    'Cu': (8960.0, 'tables/materials.csv'),
    'CPVC': (1550.0, 'tables/materials.csv (Corzan / GF sheet)'),
    'PVC_U': (1400.0, 'published rigid-PVC (PVC-U) data, AQS-STD-002 M5 class (60 C limit); '
                      'band 1350-1450, midpoint carried; confirm per the supplier TDS at order'),
    'PP': (910.0, 'tables/materials.csv; farm_hab.py used 905 in built masses'),
    'PVDF': (1780.0, 'tables/materials.csv (GF SYGEF)'),
    'HDPE': (950.0, 'models/mfg/farm_hab.py RHO'),
    'EPDM': (1150.0, 'models/mfg/farm_hab.py RHO'),
    'FRP': (1800.0, 'models/mfg/farm_hab.py RHO'),
    'acrylic': (1180.0, 'models/mfg/farm_hab.py RHO'),
    'aluminium': (2700.0, 'models/mfg/farm_hab.py RHO'),
    'pine': (500.0, 'models/mfg/farm_hab.py RHO'),
    'LECA': (450.0, 'models/mfg/farm_hab.py RHO'),
    'grey_iron': (7200.0, 'tables/materials.csv (cast + bar D50 row)'),
    'tool_steel': (7850.0, 'tables/materials.csv (AR400 or D2)'),
}

# AQS-STD-001 shop rule, corrosion allowance (mm)
CA_NONE = 0.0
CA_CS_HYDROCARBON = 1.5

_POLYMERS = ('cpvc', 'pp', 'pvdf', 'hdpe', 'pvc', 'ptfe', 'frp', 'epdm', 'acrylic', 'leca')


def density(material):
    """Density in kg/m3 for a material class label, or None when the class is unknown."""
    key = (material or '').strip().replace(' ', '_').replace('-', '_')
    if key in DENSITY:
        return DENSITY[key][0]
    m = (material or '').lower()
    for k in DENSITY:
        if k.lower() in m:
            return DENSITY[k][0]
    return None


def ca_for(material, service=''):
    """Corrosion allowance in mm per the AQS-STD-001 shop rule.

    Polymer: none. Carbon steel in hydrocarbon service: 1.5 mm. 316L, titanium and
    graphite: 0 mm. A carbon-steel service that is not hydrocarbon is a duty-page
    section 3 decision; this rule returns the 1.5 mm hydrocarbon value and the caller
    names the duty basis.
    """
    m = (material or '').lower()
    if any(p in m for p in _POLYMERS):
        return CA_NONE
    if '316' in m or '304' in m or 'titanium' in m or 'ti_g2' in m or 'graphite' in m:
        return CA_NONE
    if 'cs' in m.split() or 'carbon' in m or 'a36' in m or 's235' in m or m == 'cs':
        return CA_CS_HYDROCARBON
    return None


def unit_rows(repo_root, unit):
    """Rows of tables/materials.csv for one unit name: list of dicts, [] when none.

    Columns: name, part, material, form, qty, unit, density_kg_m3, make_buy, spec, notes.
    """
    import csv
    import os
    path = os.path.join(repo_root, 'tables', 'materials.csv')
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [r for r in csv.DictReader(fh) if r.get('name') == unit]
