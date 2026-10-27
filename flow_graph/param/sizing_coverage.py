"""Unit task 02 evidence registry (AQS-PLAN-007): maps every sized unit to the sizing document
that carries its calculation. Writes docs-authority/inventory/SIZING_COVERAGE.json, read by
docs-authority/_task_plan_gen.py on every TASK_PLAN regeneration (STORAGE_HOLDUP.json pattern).

Rule (2026-10-20 evidence-audit discipline): a unit is listed only where the cited document
names the unit and carries its sizing basis; the build asserts both - every unit id must appear
in the cited document text, and every listed unit must be a present, non-boundary graph node.
The legacy DONE_U entries (LEACH_CSTR_1, EW_1..9) and the storage set stay in their own
mechanisms; this registry carries them too so the task plan has one evidence line per unit.
Run: python3 -m flow_graph.param.sizing_coverage   (no --write: the JSON is the write)"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
OUT = os.path.join(ROOT, 'docs-authority/inventory/SIZING_COVERAGE.json')
EW = [f'EW_{i}' for i in range(1, 10)]

FAMILIES = [
    # (doc path relative to repo root, doc number, family line, unit list or None = read a JSON)
    ('docs-authority/sizing/EW_CELLS.md', 'AQS-DUTY-051', 'EW cells, Faraday basis (docs-authority/_ew_sizing.py)', EW),
    ('docs-authority/sizing/LEACH_CSTR_1.md', 'AQS-DUTY-050', 'Leach CSTR (docs-authority/_leach_sizing.py)', ['LEACH_CSTR_1']),
    ('docs-authority/sizing/STORAGE_HOLDUP.md', 'AQS-DUTY-064', 'Storage and holdup (docs-authority/_storage_sizing.py)',
     [r['unit'] for r in json.load(open(os.path.join(ROOT, 'docs-authority/inventory/STORAGE_HOLDUP.json')))]),
    ('docs-authority/sizing/FOUNDRY_LINE.md', 'AQS-DUTY-072', 'FOUNDRY line (docs-authority/_foundry_sizing.py; transfer functions flow_graph/param/foundry_poly.py)',
     ['AL_POT', 'CA_POT', 'CR_CELL', 'MG_POT', 'MO_CELL', 'TI_CELL', 'IND_MELT', 'RES_HEAT', 'COMB_HEAT', 'VAC_IND',
      'CAST_LINE', 'CONT_CAST', 'INV_CAST', 'VAC_CAST', 'ROLL', 'EXTRUDE', 'DRAW', 'FORGE', 'SINTER', 'FLUX_PREP', 'WAX_PATTERN',
      'SHELL_BUILD', 'SHELL_BURNOUT', 'SHELL_BREAK', 'STOCK_OUT']),
    ('docs-authority/sizing/POLYMERS_LINE.md', 'AQS-DUTY-073', 'POLYMERS line (docs-authority/_polymers_sizing.py; transfer functions foundry_poly/fluoro_train)',
     ['FILM_CAST', 'HF_GEN', 'PELLET', 'POLY_COND', 'POLY_F', 'POLY_FIBER', 'POLY_OLEFIN', 'POLY_STOCK', 'POWDER_RESIN', 'TFE_SYN', 'VDF_SYN']),
    ('docs-authority/sizing/REACTOR_DESIGN.md', 'AQS-DUTY-062', 'In-house reactors (flow_graph/param/reactor_design.py)',
     ['GLASS_DIGEST', 'OIL_PYRO', 'MEOH_SYNTH', 'MEOH_FERM']),
    ('docs-authority/sizing/EVAP_DESIGN.md', 'AQS-DUTY-060', 'MVR evaporators (flow_graph/param/evap_design.py)', ['EVAP_ACID', 'EVAP_BASE']),
    ('docs-authority/sizing/COLD_BOX.md', 'AQS-DUTY-069', 'Micro cold box (flow_graph/param/cold_box.py)', ['CRYO_ASU']),
    ('docs-authority/sizing/GAS_RECEIVERS.md', 'AQS-DUTY-065', 'Gas receiver banks (flow_graph/param/receivers.py)', ['CRYO_H2', 'CRYO_O2', 'CRYO_CO2']),
    ('docs-authority/sizing/H2_PURIFIER_BEDS.md', 'AQS-DUTY-066', 'H2 purifier / dryer beds (flow_graph/param/h2_purifier.py)', ['H2_DRYER']),
    ('docs-authority/sizing/HOUSE_SCRUBBERS.md', 'AQS-DUTY-079', 'House scrubbers (flow_graph/param/house_scrubbers.py)',
     ['ALK_SCRUBBER', 'ACID_POLISH_SCRUB', 'NOX_SCRUB', 'MET_SCRUB']),
    ('docs-authority/sizing/BMED_STACK.md', 'AQS-DUTY-068', 'BMED stacks (flow_graph/param/bmed_stack.py)', ['BMED_ACID', 'BMED_BASE']),
    ('docs-authority/sizing/SANITATION.md', 'AQS-DUTY-063', 'Sanitation train (flow_graph/param/sanitation.py)', ['BLACK_DIGEST']),
    ('docs-authority/sizing/UPW_POLISH.md', 'AQS-DUTY-070', 'UPW polish RO/EDI (flow_graph/param/upw_polish.py)', ['BMED_UPW_POLISH']),
    ('docs-authority/sizing/VENT_SCRUBBER.md', 'AQS-DUTY-061', 'Evaporator vent scrubber (flow_graph/param/vent_scrubber.py)', ['EVAP_ACID_VS']),
    ('docs-authority/sizing/PV_CELL_LINE.md', 'AQS-DUTY-071', 'PV cell line (flow_graph/param/pv_cell_line.py)', ['SOLAR_PV_CELL']),
    ('docs-authority/sizing/HEAT_BATTERY.md', 'AQS-DUTY-074', 'Heat batteries (flow_graph/param/heat_battery.py)',
     [f'Q{t}_{s}' for t in (1, 2, 3, 4) for s in ('A', 'B')]),
    ('docs-authority/sizing/HEADERS.md', 'AQS-DUTY-075', 'Headers and the Q4 bus (flow_graph/param/headers.py)',
     ['HDR_H2', 'HDR_O2', 'HDR_CO2', 'HDR_N2', 'HDR_UPW', 'Q4_BUS', 'NCG_HEADER', 'AFTERBURNER_FLUE']),
    ('docs-authority/sizing/GEO_LOOP.md', 'AQS-DUTY-076', 'GEO loop (flow_graph/param/geo_loop.py)', ['GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP']),
    ('docs-authority/sizing/MEOH_TRAIN.md', 'AQS-DUTY-077', 'Methanol train residuals (flow_graph/param/meoh_train.py)', ['MEOH_COND', 'MEOH_FC']),
    ('docs-authority/FARM_DESIGN.md', 'AQS-FARM-001', 'Aquaponics + smallstock + larvae composting (docs-authority/_farm_hab.py; A-M-415..418)',
     ['AQUA_TANK', 'BIOFILTER', 'GROWBED_A', 'GROWBED_B', 'DUCKWEED', 'FEED_PREP', 'AQUA_UV', 'CHICKEN_COOP', 'DUCK_PEN', 'QUAIL_CAGE', 'RABBIT_HUTCH', 'BSFL_BIN', 'BEE_HIVE', 'VERMI_BIN']),
    ('docs-authority/HAB_DESIGN.md', 'AQS-HAB-002', 'Hab interior zoning (docs-authority/_farm_hab.py; A-M-419)',
     ['GALLEY', 'WASHROOM', 'MEDICAL', 'REC_DAYROOM', 'SLEEP_QUARTERS', 'COMMON_AREA']),
    ('docs-authority/MFG_TOOLS.md', 'AQS-MFG-010', 'Metal-shop tools (docs-authority/_mfg_tools.py, X-MFG-37)',
     ['MET_MELT', 'GAS_ATOMIZER', 'COLD_MILL', 'WIRE_DRAW']),
    ('docs-authority/WATER_TOWER.md', 'AQS-BLD-014', 'Water tower reservoirs and hydro set (docs-authority/_water_tower.py)',
     ['ROOF_TANK', 'CATCH_TANK', 'HYDRO_SET']),
    ('docs-authority/POWER_SIZING.md', 'AQS-ELEC-007', 'Plant power sizing (docs-authority/_power_sizing.py)',
     ['PV_ARRAY', 'ZNBR2', 'SOL_ARK_60K', 'BACKUP_GEN', 'FUEL_CELL']),
    ('docs-authority/POLYMER_HX_SIZING.md', 'AQS-DUTY-049', 'Polymer heat exchangers (docs-authority/_polymer_hx_study.py, X-MAT-11/12)', ['HX8']),
    # Residuals NOT listed (docs size the equipment under a legacy name): RECTIFIER, LITHO_ALIGN
    # and the rest of the task-02 tail retire through the per-unit sweep-doc pass below
    # (2026-10-20 note stands only until AQS-SIZE-<UNIT>.md exists; the tail is now covered there).
]


def build():
    g = json.load(open(GP))
    present = {n['unit_id'] for n in g['nodes'] if n.get('presence') == 'present' and n.get('class') != 'boundary'}
    cov, problems = {}, []
    for doc, num, fam, units in FAMILIES:
        p = os.path.join(ROOT, doc)
        if not os.path.exists(p):
            problems.append(f'{doc}: missing'); continue
        text = open(p).read()
        for u in units:
            if u not in present:
                problems.append(f'{u}: not a present non-boundary unit (cited by {doc})'); continue
            if u not in text:
                problems.append(f'{u}: not named in {doc}'); continue
            if u in cov:
                problems.append(f'{u}: claimed by both {cov[u]["doc"]} and {doc}'); continue
            cov[u] = dict(doc=doc, docnum=num, family=fam)
    # Per-unit tail pass (2026-10-21): the unit sizing sweep owns docs-authority/sizing/<UNIT>.md for
    # every unit still open on -02; where that doc exists and names the unit it is the sizing
    # calculation's evidence line. Same assertions apply: doc names the unit, unit is present
    # and non-boundary, no double claim.
    swept = 0
    for u in sorted(present - set(cov)):
        doc = f'docs-authority/sizing/{u}.md'
        p = os.path.join(ROOT, doc)
        if not os.path.exists(p):
            problems.append(f'{u}: no family doc and no per-unit sweep doc'); continue
        if u not in open(p).read():
            problems.append(f'{u}: per-unit doc {doc} does not name the unit'); continue
        cov[u] = dict(doc=doc, docnum=f'AQS-SIZE-{u}',
                      family='Unit sizing sweep - graph params + vessel calc (docs-authority/_unit_sizing_sweep.py)')
        swept += 1
    return cov, problems, swept


def main():
    cov, problems, swept = build()
    if problems:
        print('SIZING COVERAGE REFUSES TO BUILD:'); [print(' -', p) for p in problems]
        sys.exit(1)
    json.dump(cov, open(OUT, 'w'), indent=1, sort_keys=True)
    print(f'{len(cov)} units with a unit task 02 sizing document ({len(cov)-swept} family docs, {swept} per-unit sweep docs) -> {OUT}')


if __name__ == '__main__':
    main()
