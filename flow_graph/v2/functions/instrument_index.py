"""The instrument-index census (family migration; reference writer
docs-authority/_instr_index.py -- ledger section J row `doc_instr_index`, the
306-line generator with the embedded authored-loop table). AQS-CTL-001
(X-CTL-01, A-M-193): every instrument of AQS-INV-004 (the OTHER_INVENTORY rows
of category `instrument`, gas detectors excluded -- they are listed in
AQS-SAF-006 and wired to the fire panel and SIS) gets an ISA5_1_2022 tag
<UNIT>-<letters>-<nn>, a calibrated range from the graph, a signal
(IEC61131_2) and a loop on its sector PLC. SIF elements carry the 90+ numbers
(AQS-CTL-003). Ranges: flow = 2 x normal of the named stream (turndown),
liquid at the edge density or 1000 kg/m3; pressure = next standard range >=
1.25 x unit design pressure (gauge), else the inventory 0-10 bar; temperature
= band of the unit (cryogenic, hot or ambient); level = 0-100 % of the liquid
height of A-M-182, high-level switch at 90 %. An inventory range below the
computed need is flagged (the `flags` book, the doc's deviation table; a need
above 16 bar g also steps the element to the thin-film strain gauge, the same
element rule as flow_graph/inventory/other.py).

The per-unit extension (2026-10-20): the AUTH table below carries the loops
authored for units with no AQS-INV-004 instrument rows (FOUNDRY/POLYMERS
trains, gas headers, relief stacks, stores, EVAP_ACID_VS and the standalone
heat machines). The authored loops are design decisions -- declared data with
a per-row basis, exactly like the materials3 selection table. Every measured
variable, range and citation comes from a node design param, an edge rate or a
cited inventory artifact -- nothing invented; the citation is the basis column
of the CSV. The six numeric rows (pot-cell currents and bath temperatures, the
HF kiln spar feed, the groundwater and UPW supply meters, the methanol product
meter) declare their rule instead of a frozen string; the resolver computes
the range from the same graph value the v1 generator read. SIF-numbered
elements continue the AQS-CTL-003 convention.

The merge: an AQS-INV-004 row of the same tag letters wins once the inventory
lane catches up (per letters, no duplicate tags; asserted), and an authored
SIF element is skipped where the inventory already carries the -90 element of
those letters. The tag allocation, the duplicate-tag gate and the AUTH
coverage gate (every unit the rows do not cover must be a graph-class
`boundary` -- trade and bookkeeping boundaries, not process units) port as the
v1 asserts, raised loud.

Grid doctrine where numeric: the ranges are spec strings -- ported verbatim
from the reference writer's own float chains (the census family doctrine);
counts are native integers.

Payload bridge (the ledger's read set: OTHER_INVENTORY.csv + graph): the v1
stage read the committed inventory CSV beside the graph; here the rows travel
as inputs['other_inventory'] (dict rows, the committed CSV face), and an
absent payload means no inventory lane -- the AUTH rows alone then cover only
their own units and the coverage gate fails loud (the v1 assert against a
missing inventory). The census reads no drivers: the stage ran with
depends_on (none) in the manifest, so the book computes identically over the
committed seed with no solve at all (the no-drivers bridge contract, proven in
flow_graph/v2/test_instrument_index.py).

Like the other censuses of the inventory family, this one stamps NO graph
field: the rows are boundary data the renderer lane lays out into
INSTRUMENT_INDEX.csv and the AQS-CTL-001 page (the doc_instr_index product;
the index feeds duty_basis/pid/haz_area/hazop/commissioning downstream). The
registered solve set does not import this module. Pure: no I/O here.
"""
import collections
import re

from flow_graph.v2.functions import inventory as _INV   # the census family's graph views


def flo(s):
    """A constant as the float of its exact decimal (the no-float-literal rule)."""
    return float(s)


AI = '4-20 mA HART (AI)'
DI = '24 V DC discrete (DI)'
K600 = '0 to 600 C (Pt100 to 600 C, IEC 60751)'
AMB = '-20 to 150 C'
HOT_KEYS = ('PYRO', 'FURNACE', 'MELT', 'AFTERBURN', 'HTC', 'SIC', 'DRYER', 'EVAP', 'DIGEST')
LET = {'temperature element (SIF, independent)': 'TE', 'flow transmitter': 'FT', 'pressure transmitter': 'PT',
       'temperature element': 'TE', 'level transmitter': 'LT', 'high-level switch': 'LSH'}
# Standard temperature-element bands: (top C, range, element). Pt100 to 600 C
# per IEC 60751; type K thermocouple to 1100 C and type S to 1600 C per
# IEC 60584-1 (continuous-use limits of the base-metal and platinum
# thermocouples).
TE_BANDS = ((150, '-20 to 150 C', 'IEC 60751, 316L thermowell'),
            (600, '0 to 600 C (Pt100 to 600 C, IEC 60751)', 'IEC 60751, 316L thermowell'),
            (1100, '0 to 1100 C', 'type K thermocouple, IEC 60584, Inconel sheath'),
            (1600, '0 to 1600 C', 'type S thermocouple, IEC 60584, ceramic sheath'))
PR = (1, flo('2.5'), 6, 10, 16, 25, 40, 60, 100, 160, 250, 400)     # bar standard ranges
NICE = (1, 2, flo('2.5'), 5)


def _nice(x):
    """The v1 nice(): the next 1/2/2.5/5 x 10^n value >= x (the 1-2-5 ladder)."""
    k = 10 ** int(f'{x:e}'.split('e')[1])
    return next(m * k for m in NICE + (10,) if m * k >= x)


# ---- X-CTL-01 per-unit extension: the authored loops -------------------------
# Why these units had no loops: flow_graph/inventory/other.py emits instrument
# rows only where the unit has a nozzle csv, has liquid inflow (class not
# farm/product/building/hab), or is hcl_synthesis/pem_electrolyser, and skips
# the boundary/header/relief classes outright; the FOUNDRY/POLYMERS machines
# are solid-fed with no nozzle csv at the last AQS-INV-004 regen, and
# EVAP_ACID_VS's only instrument-category row is a gas detector (listed in
# AQS-SAF-006, skipped by this index).
#
# Declared data. One row per authored loop:
#   unit, letters, type, spec, range, signal, basis, sif
# A range or basis that the v1 generator computed from the graph declares its
# rule instead of a frozen string; the resolver computes the same string from
# the model (the declared-rule kinds are the six numeric rows):
#   ('i_a',)                        cell-current range, 2 x design I_A
#   ('feed_kg_h', sid)              solids-feed range, 2 x normal of the edge, kg/h
#   ('feed_l_h', sid)               liquid-feed range, 2 x normal of the edge at its density
#   ('feed_l_h_rho', sid, rho)      the same at a declared density, kg/m3
#   ('cell_current_basis',)         basis: design I_A of the unit
#   ('bath_t_basis',)               basis: design bath_T_C of the unit
#   ('edge_kg_d_note', prefix, sid) basis: prefix, the edge rate and its L/h
#   ('edge_lh_note', head, sid)     basis: a fixed head plus the edge L/h
#   ('edge_lh_rho_note', head, sid, rho)  the same at a declared density
AUTH = (
    # FOUNDRY: pot cells (cell current, bath temperature, hood chlorine), Kroll train, melt/cast/FORM chain, benches, store
    ('AL_POT', 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', ('i_a',), AI, ('cell_current_basis',), False),
    ('AL_POT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI, ('bath_t_basis',), False),
    ('CA_POT', 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', ('i_a',), AI, ('cell_current_basis',), False),
    ('CA_POT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI, ('bath_t_basis',), False),
    ('CR_CELL', 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', ('i_a',), AI, ('cell_current_basis',), False),
    ('CR_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI, ('bath_t_basis',), False),
    ('MG_POT', 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', ('i_a',), AI, ('cell_current_basis',), False),
    ('MG_POT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI, ('bath_t_basis',), False),
    ('MO_CELL', 'IT', 'current transmitter', 'DC shunt + isolated amplifier, IEC 61010-1', ('i_a',), AI, ('cell_current_basis',), False),
    ('MO_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI, ('bath_t_basis',), False),
    ('AL_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', AI,
     'anode-gas Cl2 offtake: IA-CL2-SHIP 39.42 kg/d; AL_POT_CL2 recycle standby', False),
    ('CA_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', AI,
     'anode-gas Cl2 offtake: IA-CA-CL2-SHIP 0.10 kg/d', False),
    ('CA_POT', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of bath height', AI,
     'molten CaCl2 bath: IA-CACL2-MU 0.15 kg/d brine feed', False),
    ('CR_CELL', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', AI,
     'carbochlorination loop Cl2 (design chemistry); IA-CR-VENT CO 0.20 kg/d', False),
    ('MG_POT', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', AI,
     'anode-gas Cl2 to the Kroll chlorinator: IA-CL2-MG-TI 1.48 kg/d', False),
    ('MG_POT', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of bath height', AI,
     'molten MgCl2 bath: IA-MGCL2-MU 0.04 kg/d brine make-up', False),
    ('MO_CELL', 'AE', 'chlorine analyzer', 'electrochemical Cl2 cell', '0-100 vol % Cl2', AI,
     'anode gas (Cl2 or O2) to CRU: MO_CELL_ANODE_GAS_TO_CRU', False),
    ('TI_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', AI,
     'Kroll reduction retort: design retort_T_C 900 C', False),
    ('TI_CELL', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1000 C', AI,
     'chlorinator: design chlorinator_T_C 800 C', False),
    ('TI_CELL', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'Ar-cover Kroll retort; no design pressure on the graph', False),
    ('TI_CELL', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'TiCl4 receiver between chlorinator and retort (design chemistry, AQS-BAL-KROLL)', False),
    ('IND_MELT', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'Cu/Fe/Zn/Al remelt (design service); 4 heats/d of the 10 kg crucible', False),
    ('IND_MELT', 'TE', 'temperature element (SIF, independent)', 'type B thermocouple, own thermowell', '0 to 1600 C', AI,
     'independent high-temperature trip (AQS-CTL-003); design service Cu/Fe/Zn/Al', True),
    ('RF_HEAT', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'equal-duty backup of the IND_MELT crucible class (design backup_of)', False),
    ('RES_HEAT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', AI,
     'design T_C 900 C (reheat, N+1 of SHELL_BURNOUT/SINTER)', False),
    ('RES_HEAT', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1100 C', AI,
     'independent high-temperature trip (AQS-CTL-003); design T_C 900 C', True),
    ('COMB_HEAT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', AI,
     'combustion reheating furnace (class furnace); offgas COMB_OFFGAS to MET_SCRUB', False),
    ('CAST_LINE', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'mould pour: IND_MELT_TO_CAST 3.0 kg/d molten metal', False),
    ('CAST_LINE', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of ladle height', AI,
     'pour ladle: IND_MELT_TO_CAST 3.0 kg/d molten metal', False),
    ('VAC_IND', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'vacuum induction skull melt (design service, 2 kg ISM case)', False),
    ('VAC_IND', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0 to 1000 mbar a', AI,
     'melt-chamber vacuum; no design pressure on the graph', False),
    ('VAC_CAST', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'vacuum tilt-pour of VAC_IND_TO_VAC_CAST melt (design case 3 kg)', False),
    ('VAC_CAST', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0 to 1000 mbar a', AI,
     'cast-chamber vacuum; no design pressure on the graph', False),
    ('ROLL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'hot rolling of CAST_TO_ROLL + CONT_TO_ROLL billet (13 kg/d); no design T on the graph', False),
    ('EXTRUDE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'billet/container preheat for extrusion (N+1 of ROLL); no design T on the graph', False),
    ('DRAW', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'cold wire/rod draw bench (N+1 of ROLL); band by service', False),
    ('FORGE', 'ZT', 'position transmitter', 'LVDT ram position transducer', '0-200 mm', AI,
     'ram stroke: design ram_mm 200', False),
    ('FORGE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'open-die press stock temperature (N+1 of ROLL); no design T on the graph', False),
    ('SINTER', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1400 C', AI,
     'design T_C 1300 C powder sinter', False),
    ('SINTER', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1400 C', AI,
     'independent high-temperature trip (AQS-CTL-003); design T_C 1300 C', True),
    ('FLUX_PREP', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'salt flux bench (class prep); IA-KROLL-FLUX 0.04 kg/d salt', False),
    ('FLUX_PREP', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of hopper height', AI,
     'flux hopper: design hopper_L 20 L', False),
    ('STOCK_OUT', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'formed-metal staging rack (CONT_TO_STOCK 21.7 kg/d); condensation watch', False),
    ('CONT_CAST', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'strand feed: IND_TO_CONT 31.7 kg/d melt; water-cooled copper mould (design)', False),
    ('CONT_CAST', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of tundish height', AI,
     'tundish: IND_TO_CONT 31.7 kg/d molten metal', False),
    ('WAX_PATTERN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'wax pot: WAX_RECLAIM_TO_PATTERN 1.8 kg/d reclaim + make-up 0.2 kg/d', False),
    ('WAX_PATTERN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of pot height', AI,
     'wax pot: design pot_L 10 L', False),
    ('SHELL_BUILD', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'slurry tank of the 6-dip booth (design dips 6)', False),
    ('SHELL_BUILD', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of slurry tank height', AI,
     'slurry tank: design slurry_L 40 L', False),
    ('SHELL_BURNOUT', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 1100 C', AI,
     'design T_C 900 C flash-dewax + shell fire', False),
    ('SHELL_BURNOUT', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 1100 C', AI,
     'independent high-temperature trip (AQS-CTL-003); design T_C 900 C', True),
    ('INV_CAST', 'TE', 'temperature element', 'type B thermocouple, IEC 60584, alumina sheath', '0 to 1600 C', AI,
     'investment pour: IND_TO_INV 2.0 kg/d melt', False),
    ('INV_CAST', 'LT', 'level transmitter', 'laser level meter, non-contact', '0-100 % of crucible height', AI,
     'pour crucible: IND_TO_INV 2.0 kg/d molten metal', False),
    ('SHELL_BREAK', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'knock-out station (class separator); INV_TO_BREAK 10 kg/d', False),
    ('METAL_STORE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'metal product store (IA-STOCK-STORE 36.7 kg/d); condensation watch', False),
    # POLYMERS: HF kiln (offgas T, HF analyzer, feed rate), VDF/TFE trains, kettle, formers, stock
    ('HF_GEN', 'FT', 'flow transmitter', 'gravimetric loss-in-weight feeder (solids feed)', ('feed_kg_h', 'IA-CAF2-MU'), AI,
     'acid-spar feed: IA-CAF2-MU 0.33 kg/d (design spar_kg_d)', False),
    ('HF_GEN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'kiln/offgas: design T_C 250 C rotary kiln', False),
    ('HF_GEN', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, AI,
     'independent high-temperature trip (AQS-CTL-003); design T_C 250 C', True),
    ('HF_GEN', 'AE', 'HF analyzer', 'electrochemical HF cell', '0-10 ppm HF', AI,
     'kiln offgas HF watch: design hf_kg_d 1.67 kg/d', False),
    ('HF_GEN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vat height', AI,
     'feed blend vat: F_RECOVER_TO_HF_GEN 1.52 kg/d + IA-H2SO4-MU 0.40 kg/d', False),
    ('VDF_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', K600, AI,
     'chlorination reactor: design chlorination_C 350 C', False),
    ('VDF_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 800 C', AI,
     '142b cracking furnace: design cracking_C 650 C', False),
    ('VDF_SYN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed tank height', AI,
     'aqueous HF feed tank: HF_GEN_TO_VDF 0.09 kg/d', False),
    ('TFE_SYN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 900 C', AI,
     'R-22 pyrolysis: design pyrolysis_C 750 C (immediate quench per design)', False),
    ('TFE_SYN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed tank height', AI,
     'aqueous HF feed tank: HF_GEN_TO_TFE 0.08 kg/d', False),
    ('POLY_F', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'emulsion kettle: design T_C 60 C', False),
    ('POLY_F', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.23 m kettle', AI,
     'kettle: design H_mm 225', False),
    ('POLY_COND', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'standby condensation kettle: design jacket_C 160 C', False),
    ('POLY_COND', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.30 m kettle', AI,
     'kettle: design H_mm 300', False),
    ('POLY_OLEFIN', 'TE', 'temperature element', 'type K thermocouple, IEC 60584, Inconel sheath', '0 to 400 C', AI,
     'oligomerization reactor: design T_C 250 C', False),
    ('POLY_OLEFIN', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell', '0 to 400 C', AI,
     'independent high-temperature trip (AQS-CTL-003); design T_C 250 C', True),
    ('POLY_OLEFIN', 'PT', 'pressure transmitter', '316L thin-film strain gauge, IEC 61298', '0-100 bar g', AI,
     'design P_MPa 5.0 (1.25 x = 62.5 bar)', False),
    ('POLY_OLEFIN', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of 0.23 m vessel', AI,
     'reactor: design H_mm 225', False),
    ('PELLET', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', AI,
     'underwater die-face pelletizer process water (design machine); no design T on the graph', False),
    ('POWDER_RESIN', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'PTFE pin-mill line, ambient milling (design product note)', False),
    ('POWDER_RESIN', 'ST', 'speed transmitter', 'incremental encoder on the mill drive', '0-100 % of drive speed', AI,
     'mill drive: design duty_kW 0.0152 kW', False),
    ('FILM_CAST', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 300 C', AI,
     'extruder melt: design melt_C 220 C', False),
    ('FILM_CAST', 'ST', 'speed transmitter', 'incremental encoder on the chill-roll/haul-off drive', '0-100 % of drive speed', AI,
     'chill-roll drive: design chill_roll_D_mm 150', False),
    ('FILM_CAST', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of feed vessel height', AI,
     'PVDF feed: POLYF_TO_FILM 0.14 kg/d resin', False),
    ('POLY_STOCK', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'polymer stock bins (PELLET_TO_STOCK 0.29 kg/d)', False),
    ('POLY_STOCK', 'LT', 'level transmitter', 'ultrasonic bin level', '0-100 % of bin height', AI,
     'pellet tote bins (design bin)', False),
    # HEAT: chiller, MAU, dry cooler, Q4 hot-water bus
    ('ADS_CHILL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', AI,
     'drive water in: IA-Q4-ADS 5.0 kW Q4 65 C', False),
    ('ADS_CHILL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 40 C', AI,
     'chilled water out: IA-ADS-CHW 2.25 kW at 12 C', False),
    ('MAU_HX', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', AI,
     'Q4 coil: IA-Q4-MAU 12 kW Q4 water 65/45 C (winter design)', False),
    ('DRY_COOLER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', AI,
     'recooling: IA-ADS-REJ 7.25 kW + HL-Q4-REJ Q4 surplus', False),
    ('Q4_BUS', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', '0 to 100 C', AI,
     'Q4 hot-water bus supply (IA-Q4-ADS/IA-Q4-MAU 65 C design)', False),
    ('Q4_BUS', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'hot-water bus; no design pressure on the graph', False),
    # WTR: groundwater intake skid (make-up source; X-LOC-07, AQS-PLAN-011 section 6.2)
    ('GW_INTAKE', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456',
     ('feed_l_h', 'IA-GW-MAKEUP'), AI, ('edge_kg_d_note', 'make-up to ROOF_TANK', 'IA-GW-MAKEUP'), False),
    ('GW_INTAKE', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'RO membrane feed; no design pressure on the graph', False),
    ('GW_INTAKE', 'CT', 'conductivity transmitter', 'inductive conductivity, IEC 60746-1', '0-2000 uS/cm', AI,
     'RO product quality watch; well water moderately mineralised with high silica, fluoride and arsenic (USGS_DV_GW)', False),
    # DIGESTER: acid vent scrubber (pH/ORP + level + recirc flow), recovery separators
    ('EVAP_ACID_VS', 'AE', 'pH analyzer', 'glass electrode pH, IEC 60746-2', '0-14 pH', AI,
     'scrub liquor: NaOH 2 M bleed IA-VS-NAOH 0.5 g/d', False),
    ('EVAP_ACID_VS', 'AE', 'ORP analyzer', 'ORP electrode, IEC 60746-2', '-1000 to +1000 mV', AI,
     'acid-gas breakthrough watch: IA-VS-OFF 0.029 kg/d scrubbed vent', False),
    ('EVAP_ACID_VS', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'scrub liquor: IA-VS-SPENT 0.6 g/d spent bleed', False),
    ('EVAP_ACID_VS', 'LSH', 'high-level switch', 'vibrating fork, IEC 60947-5, 316L', 'trip at 90 % of vessel height', DI,
     'scrubber sump high level trips the feed', False),
    ('EVAP_ACID_VS', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456', '0-700 L/h', AI,
     'sump recirculation 0.35 m3/h (AQS-INV-001 motor inventory)', False),
    ('EVAP_ACID_VS', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, AI,
     'independent high-temperature trip (AQS-CTL-003); acid vent scrubber', True),
    ('F_RECOVER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'fluoride concentrate receiver (class separator)', False),
    ('F_RECOVER', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'concentrate: F_RECOVER_TO_HF_GEN 1.52 kg/d', False),
    ('LI_RECOVER', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'standby Li polish liquor: POLISH_TO_LI (rate pending assay)', False),
    ('P_CA', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'standby Ca precipitator: PCA_TO_GREASE (rate pending assay)', False),
    # GAS/HAB/WTR/OIL headers: pressure on every gas header, UPW header also metered
    ('HDR_H2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'H2 pool header: IA-HDR-H2-02 1.98 kg/d max feed; no design pressure on the graph', False),
    ('HDR_O2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'O2 pool header: S83 33.2 kg/d product + returns; no design pressure on the graph', False),
    ('HDR_CO2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'CO2 header: S89 0.88 + S90 4.02 kg/d; no design pressure on the graph', False),
    ('HDR_N2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'plant air/N2 header: IA-AIR-RX-OUT 192.0 kg/d; no design pressure on the graph', False),
    ('HDR_UPW', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'UPW header; no design pressure on the graph', False),
    ('HDR_UPW', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456',
     ('feed_l_h', 'S01'), AI, ('edge_lh_note', 'UPW supply: S01 67.30 kg/d', 'S01'), False),
    ('NCG_HEADER', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'NCG header: IA-OIL-03 5.0 kg/d to the afterburner; no design pressure on the graph', False),
    # OIL: standby grease kettles; CRYO: air receiver, product stores, relief stacks; GLASS/ELEC/FARM remainder
    ('GREASE_CA', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'Ca grease kettle (class kettle); WAX_TO_GREASE_CA wax cut (rate pending assay)', False),
    ('GREASE_CA', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of kettle height', AI,
     'kettle holdup (class kettle)', False),
    ('GREASE_LI', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'Li grease kettle (class kettle); WAX_TO_GREASE_LI wax cut (rate pending assay)', False),
    ('GREASE_LI', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of kettle height', AI,
     'kettle holdup (class kettle)', False),
    ('AIR_RECEIVER', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'plant-air receiver bank: IA-AIR-RX-OUT 192.0 kg/d; no design pressure on the graph', False),
    ('AIR_RECEIVER', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'receiver bank; band by service', False),
    ('PROD_O2', 'PT', 'pressure transmitter', 'ceramic diaphragm, IEC 61298', '0-10 bar g', AI,
     'O2 product cylinder bank: IA-O2-PROD 22.9 kg/d; no design pressure on the graph', False),
    ('PROD_O2', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'cylinder bank; band by service', False),
    ('PROD_MEOH', 'FT', 'flow transmitter', 'electromagnetic, PFA liner, Hastelloy C electrodes, ISO 20456',
     ('feed_l_h_rho', 'IA-MEOH-PROD', '792'), AI,
     ('edge_lh_rho_note', 'methanol product: IA-MEOH-PROD 28.15 kg/d', 'IA-MEOH-PROD', '792'), False),
    ('PROD_MEOH', 'LT', 'level transmitter', 'radar 80 GHz, IEC 62828, PTFE lens', '0-100 % of vessel height', AI,
     'methanol product store (liquid, A-M-182)', False),
    ('PROD_MEOH', 'LSH', 'high-level switch', 'vibrating fork, IEC 60947-5, 316L', 'trip at 90 % of vessel height', DI,
     'store high level trips the feed', False),
    ('PROD_MEOH', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'product store; band by service', False),
    ('RELIEF_CRYO', 'PSH', 'pressure switch, high (rupture indication)', 'diaphragm pressure switch, IEC 60947-5-1',
     'trips on header pressure rise (disc burst / PSV lift)', DI, 'vent stack: S56 + S86 cryo contingency vents', False),
    ('RELIEF_H2', 'PSH', 'pressure switch, high (rupture indication)', 'diaphragm pressure switch, IEC 60947-5-1',
     'trips on header pressure rise (disc burst / PSV lift)', DI, 'vent stack: S24 H2 relief contingency', False),
    ('SI_REDUCE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'Si reduction furnace (class furnace, standby; CHAR_TO_SI rate pending); band by service', False),
    ('EXT_HALL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'hall air: SF-EXT_HALL 68.28 kW electrical feed (ventilation watch)', False),
    ('FOOD_STORE', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'food store temperature watch (class store)', False),
    ('FOOD_STORE', 'LT', 'level transmitter', 'ultrasonic bin level', '0-100 % of bin height', AI,
     'food stock level: S14 4.2 kg/d', False),
    ('AFTERBURNER_FLUE', 'TE', 'temperature element (SIF, independent)', 'Pt100 class A, own thermowell', K600, AI,
     'independent high-temperature trip (AQS-CTL-003); flue gas service (AQS-INV-004 carries no SIF element for it yet)', True),
    ('SW_INTAKE', 'FT', 'flow transmitter', 'magnetic, seawater service', '0-200 m3/h', AI,
     'intake delivery watch against the desalination and rejection demand (X-LOC-11 placeholder; A-M-409)', False),
    ('DESAL_RO', 'AN', 'conductivity analyser', 'permeate loop, contacting cell', '0-1000 uS/cm', AI,
     'permeate quality watch against the UPW feed spec (X-LOC-11 placeholder; A-M-410)', False),
    ('BRIN_RECOVER', 'AE', 'composition analyser', 'brine loop, sampling line', '0-150 g/L', AI,
     'brine concentration watch on the recovery path (X-LOC-11 placeholder; A-M-411)', False),
    ('ICE_EXTRACT', 'FT', 'flow transmitter', 'magnetic, brine service', '0-2 m3/h', AI,
     'melt-water delivery watch against the make-up demand (X-LOC-09 placeholder; A-M-406)', False),
    ('PERC_REMOVE', 'AE', 'perchlorate analyser', 'ion-selective, bed outlet', '0-100 mg/L', AI,
     'bed breakthrough watch on the ClO4 reduction (X-LOC-09 placeholder; A-M-407)', False),
    ('ATM_INT', 'PT', 'pressure transmitter', 'gauge, compressor discharge, 316L diaphragm', '0-400 kPa', AI,
     'compressor discharge pressure watch against the process pressure (X-LOC-09 placeholder; A-M-408)', False),
    ('LIO_BAT', 'PT', 'pressure transmitter', 'gauge, pack enclosure', '0-700 kPa', AI,
     'pack enclosure pressure watch on the sealed storage (X-LOC-10 placeholder; A-M-402)', False),
    ('WET_OX', 'TE', 'temperature element', 'sheathed type K, reactor service', '0-500 C', AI,
     'reactor temperature watch on the wet-oxidation window (X-LOC-10 placeholder; A-M-403)', False),
    ('HYDRO_GROW', 'AE', 'carbon-dioxide analyser', 'NDIR, chamber air loop', '0-5000 ppmv', AI,
     'chamber CO2 watch against the habitat management set-point (X-LOC-10 placeholder; A-M-404)', False),
    ('MEM_DIST', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'feed-permeate temperature difference watch on the membrane loop (X-LOC-10 placeholder; A-M-405)', False),
    ('BSFL_BIN', 'TE', 'temperature element', 'substrate probe', '0 to 50 C', AI,
     'substrate temperature watch on the larvae bin (overheat above 40 C kills larvae) (X-FARM build-out; A-M-418)', False),
    ('COMMON_AREA', 'TE', 'temperature element', 'wall sensor, circulation area', AMB, AI,
     'common-area temperature watch (X-HAB build-out; A-M-419)', False),
    ('MEDICAL', 'TE', 'temperature element', 'wall sensor, medical room', AMB, AI,
     'medical room temperature watch (X-HAB build-out; A-M-419)', False),
    ('REC_DAYROOM', 'TE', 'temperature element', 'wall sensor, day space', AMB, AI,
     'day-space temperature watch (X-HAB build-out; A-M-419)', False),
    ('SLEEP_QUARTERS', 'TE', 'temperature element', 'wall sensor, quarters', AMB, AI,
     'quarters temperature watch (X-HAB build-out; A-M-419)', False),
    ('AQUA_TANK', 'PT', 'pressure transmitter', 'gauge, tank head', '0-50 kPa', AI,
     'fish-tank head and loop pump watch (X-FARM build-out; A-M-415)', False),
    ('FEED_PREP', 'PSH', 'pressure switch high', 'mash line, press pump discharge', '0-250 kPa', AI,
     'press-line overpressure interlock on the mash loop (X-FARM-10; A-M-426)', False),
    ('AQUA_UV', 'FIT', 'flow instrumentation transmitter', 'loop inline, reactor tube', '0-100 kg/d', AI,
     'loop flow permissive: the UV dose is valid only above the minimum flow (X-FARM-12; A-M-428)', False),
    ('AQUA_UV', 'UVT', 'UV intensity sensor', 'reactor wall, 254 nm window', '0-5 mW/cm2', AI,
     'dose watchdog: lamp depletion or sleeve fouling decays the signal (X-FARM-12; A-M-428)', False),
    ('MET_SYN', 'TIR', 'temperature instrumentation recorder', 'reactor column, thermocouple well', '0-200 C', AI,
     'the Strecker step is temperature-sensitive: the hydrolysis runs at 100-150 C (X-UI-002; A-M-416)', False),
    ('MET_SYN', 'FIT', 'flow instrumentation transmitter', 'reagent feed lines', '0-50 g/h', AI,
     'the precursor metering: CH3SH, acrolein and NH3 are each fed at the gram/h class (A-M-416)', False),
    ('REE_RECOVER', 'TIR', 'temperature instrumentation recorder', 'leach reactor jacket + demag oven + calcine muffle wells',
     '0-1000 C', AI,
     'campaign temperature control: leach 55 C, demag > 320 C (Nd2Fe14B Curie), calcine 900 C (A-M-433)', False),
    ('REE_RECOVER', 'SIT', 'pH instrumentation transmitter', 'leach reactor, PTFE-body pH probe', '0-14 pH', AI,
     'pH fronts the two precipitations: Fe(OH)3 sweep at pH 3-3.5, RE oxalate at pH 1-2 (A-M-433)', False),
    ('POLY_FIBER', 'TIR', 'temperature instrumentation recorder', 'melt vessel, thermocouple well', '0-300 C', AI,
     'melt temperature is the spin-quality variable: PP spins at the 200-260 C class (X-POLY-01; A-M-429)', False),
    ('POLY_FIBER', 'FIT', 'flow instrumentation transmitter', 'spin pump discharge', '0-2 kg/h', AI,
     'denier control: fibre mass per unit length follows the pump volumetric consistency (X-POLY-01; A-M-429)', False),
    ('BIOFILTER', 'PT', 'pressure transmitter', 'gauge, loop side', '0-50 kPa', AI,
     'biofilter loop pressure watch (X-FARM build-out; A-M-415)', False),
    ('GROWBED_A', 'LT', 'level transmitter', 'ultrasonic, bed sump', '0-300 mm', AI,
     'flood-and-drain cycle watch on the aerobic root zone (X-FARM build-out; A-M-229)', False),
    ('GROWBED_B', 'LT', 'level transmitter', 'ultrasonic, bed sump', '0-300 mm', AI,
     'mineralisation-zone level watch (X-FARM build-out; A-M-229)', False),
    ('DUCKWEED', 'TE', 'temperature element', 'Pt100 class A, raceway water', AMB, AI,
     'raceway water temperature watch on the duckweed yield (X-FARM build-out; A-M-420)', False),
    ('CHICKEN_COOP', 'TE', 'temperature element', 'Pt100 class A, coop air', '-20 to 60 C', AI,
     'coop air temperature watch on the layer flock (X-FARM build-out; A-M-417)', False),
    ('DUCK_PEN', 'TE', 'temperature element', 'Pt100 class A, pen air', '-20 to 60 C', AI,
     'duck pen temperature watch (X-FARM build-out; A-M-421)', False),
    ('QUAIL_CAGE', 'TE', 'temperature element', 'Pt100 class A, cage bank', '0 to 50 C', AI,
     'cage bank temperature watch on the coturnix lay rate (X-FARM build-out; A-M-422)', False),
    ('RABBIT_HUTCH', 'TE', 'temperature element', 'Pt100 class A, hutch air', '-10 to 50 C', AI,
     'hutch temperature watch (heat stress above 30 C) (X-FARM build-out; A-M-423)', False),
    ('BEE_HIVE', 'TE', 'temperature element', 'brood-frame probe', '0 to 60 C', AI,
     'brood temperature watch at the 34-36 C cluster set-point (X-FARM build-out; A-M-424)', False),
    ('VERMI_BIN', 'TE', 'temperature element', 'soil probe, bin substrate', '0 to 40 C', AI,
     'vermi-bin substrate temperature watch (X-FARM build-out; A-M-425)', False),
    ('GALLEY', 'PT', 'pressure transmitter', 'gauge, wash water', '0-400 kPa', AI,
     'galley wash-water pressure watch (X-HAB build-out; A-M-419)', False),
    ('WASHROOM', 'PT', 'pressure transmitter', 'gauge, fixture feed', '0-400 kPa', AI,
     'washroom fixture feed pressure watch (X-HAB build-out; A-M-419)', False),
    ('RAD_PANEL', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', AMB, AI,
     'radiator loop outlet temperature watch; rejection performance against the A-M-396/A-M-397 design (X-LOC-09 placeholder)', False),
    ('TANK_BLD', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, pad service', '0-400 kPa', AI,
     'bladder pad pressure gives the water level in the closed tank (X-LOC-09 placeholder; A-M-400)', False),
    ('REC_HDR', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, header service', '0-400 kPa', AI,
     'recovery header pressure watch; the header takes every relief and offgas discharge (X-LOC-09 placeholder; A-M-398)', False),
    ('CAT_OX', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'catalyst bed temperature watch against the A-M-399 450 C light-off window (X-LOC-09 placeholder)', False),
    ('E_HEAT', 'TE', 'temperature element', 'Pt100 class A, IEC 60751, 316L thermowell', K600, AI,
     'resistance element temperature watch on the N+1 melt trim duty (X-LOC-09 placeholder)', False),
    ('LB_INTAKE', 'FT', 'flow transmitter', 'magnetic, HDPE wetted, brine service', '0-60 m3/h', AI,
     'feed throughput watch against the design 1,000 m3/d (X-LOC-05 Lake Boehmer; A-M-434)', False),
    ('LB_DEGAS', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, blower discharge', '0-30 kPa', AI,
     'air-stripper blower discharge pressure watch at the packing air-to-water ratio (X-LOC-05 Lake Boehmer; A-M-450)', False),
    ('LB_DEGAS_SCRUB', 'AT', 'hydrogen sulfide analyzer', 'fixed H2S monitor at the scrubbed vent, electrochemical',
     '0-50 ppm', AI,
     'scrubbed-vent H2S watch against the 10 ppm OSHA ceiling; lethal-site alarm (X-LOC-05 Lake Boehmer; A-M-436)', False),
    ('LB_SOFTEN', 'AT', 'pH analyzer', 'gel electrode, 316L holder, softened outlet', '6-12 pH', AI,
     'lime/soda dosing control on the softened-brine pH (X-LOC-05 Lake Boehmer; A-M-447)', False),
    ('LB_ED1', 'PT', 'pressure transmitter', 'gauge, 316L diaphragm, stack feed header', '0-600 kPa', AI,
     'primary ED stack feed pressure watch (X-LOC-05 Lake Boehmer; A-M-438)', False),
    ('LB_ED2', 'AT', 'conductivity analyzer', 'graphite electrode, product line', '0-30 mS/cm', AI,
     'product TDS watch against the segment 2311 target (X-LOC-05 Lake Boehmer; A-M-448)', False),
    ('LB_PROD_TANK', 'LT', 'level transmitter', 'radar, atmospheric tank', '0-4 m', AI,
     'product buffer level watch (X-LOC-05 Lake Boehmer; A-M-225 basis)', False),
    ('LB_BRINE_RETURN', 'FT', 'flow transmitter', 'magnetic, HDPE wetted, concentrate service', '0-40 m3/h', AI,
     'concentrate return flow watch; with the product flow it closes the site salt balance (X-LOC-05 Lake Boehmer; A-M-437)', False),
    # X-QA-11 on-site routes and the mars surface-power units (F-20261113-01): the four new units' loops
    ('BRINE_CRYS', 'FIC', 'flow transmitter', 'coriolis mass flow, brine service, wetted 316L', '0 to 4 kg/d', AI,
     'crystallizer side-stream draw: design feed_kg_d 2.0 kg/d (X-QA-11; A-M-503)', False),
    ('BRINE_CRYS', 'LIC', 'level transmitter', 'hydrostatic level, 316L diaphragm, mother-liquor service', '0 to 100 %', AI,
     'crystal-thickener level; the mother liquor returns to the leach at design ml_kg_d 1.844 kg/d (X-QA-11; A-M-503)', False),
    ('BRINE_CRYS', 'TIC', 'temperature transmitter', 'Pt100 class A, jacketed vessel', '0 to 100 C', AI,
     'jacket heater control: design kw 0.07 kW at the flash-crystallization temperature (X-QA-11; A-M-503)', False),
    ('NUT_AN', 'FIC', 'flow transmitter', 'thermal mass flow, NH3 service', '0 to 0.5 kg/d', AI,
     'Ostwald ammonia feed: design nh3_kg_d 0.231 kg/d (X-QA-11; A-M-497)', False),
    ('NUT_AN', 'FIC', 'flow transmitter', 'thermal mass flow, oxidation gas off the ASU waste stream', '0 to 0.9 kg/d', AI,
     'oxidation gas feed: design o2_kg_d 0.433 kg/d against the ammonia at the 0.97 selectivity basis (X-QA-11; A-M-497)', False),
    ('NUT_AN', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell, catalyst bed',
     '0 to 1100 C', AI,
     'independent high-temperature trip on the oxidation bed (AQS-CTL-003); the Ostwald bed runs hot by design', True),
    ('NUT_AN', 'FIC', 'flow transmitter', 'magnetic flow, ammonium-nitrate solution service', '0 to 8 kg/d', AI,
     'product dose to NUTRIENT_DOSE: design dose_kg_d 4.087 kg/d at 4.5 % N (X-QA-11; A-M-497)', False),
    ('FSP_40K', 'IT', 'current transmitter', 'DC shunt + isolated amplifier on the Stirling alternator output, IEC 61010-1',
     '0 to 40 kW', AI,
     'unit electric output: unit_kW_e 40 (NASA_FSP); the locale count solves in site_units (F-20261113-01)', False),
    ('FSP_40K', 'TE', 'temperature element', 'type N thermocouple, sheathed, primary loop', '0 to 700 C', AI,
     'primary-loop hot-leg watch at the NASA FSP class operating point', False),
    ('FSP_40K', 'TE', 'temperature element (SIF, independent)', 'type K thermocouple, own thermowell, primary loop',
     '0 to 900 C', AI, 'independent high-temperature trip, fission unit scram (AQS-CTL-003)', True),
    ('MMRTG', 'IT', 'current transmitter', 'DC shunt + transducer, GPHS thermoelectric stack', '0 to 130 W', AI,
     'thermoelectric output watch: unit_W_e 110 (NASA_RTG); a static uncontrolled source - no control loop by design (F-20261113-01)', False),
    ('MMRTG', 'TE', 'temperature element', 'Pt100 class A, fin root', '0 to 300 C', AI,
     'heat-rejection fin temperature watch; the decay-heat output declines over mission life (NASA_RTG)', False),
    ('LB_CHEM_STORE', 'LT', 'level transmitter', 'radar, day tank', '0-2 m', AI,
     'chemical day-tank level watch against the resupply interval (X-LOC-05 Lake Boehmer; A-M-225 basis)', False),
)


def _design(N, u):
    """The v1 _d(): the node's design param dict."""
    return (N[u].get('params') or {}).get('design') or {}


def _lph(E, sid, rho=None):
    """The v1 _lph(): L/h of an edge, for the 2 x normal FT range rule."""
    e = E.get(sid) or {}
    q = (e.get('rate') or {}).get('value') or 0
    return q / (rho or (e.get('params') or {}).get('density_kg_m3') or flo('1000.0')) * 1000 / 24


def _resolve(slot, u, N, E):
    """A declared range or basis: the string verbatim, or its rule computed
    from the same graph value the reference writer read."""
    if isinstance(slot, str):
        return slot
    kind = slot[0]
    if kind == 'i_a':
        return f"0-{_nice(2 * _design(N, u)['I_A']):g} A"
    if kind == 'cell_current_basis':
        return f"cell current: design I_A {_design(N, u)['I_A']} A"
    if kind == 'bath_t_basis':
        return f"bath temperature: design bath_T_C {_design(N, u)['bath_T_C']:.0f} C"
    if kind == 'feed_kg_h':
        e = (E.get(slot[1]) or {}).get('rate') or {}
        return f"0-{_nice(2 * ((e.get('value') or 0) / 24)):g} kg/h"
    if kind == 'feed_l_h':
        return f"0-{_nice(2 * _lph(E, slot[1])):g} L/h"
    if kind == 'feed_l_h_rho':
        return f"0-{_nice(2 * _lph(E, slot[1], flo(slot[2]))):g} L/h"
    if kind == 'edge_kg_d_note':
        e = (E.get(slot[2]) or {}).get('rate') or {}
        return f"{slot[1]}: {slot[2]} {(e.get('value') or 0):.2f} kg/d ({_lph(E, slot[2]):.2f} L/h)"
    if kind == 'edge_lh_note':
        return f"{slot[1]} ({_lph(E, slot[2]):.2f} L/h)"
    if kind == 'edge_lh_rho_note':
        return f"{slot[1]} ({_lph(E, slot[2], flo(slot[3])):.2f} L/h at {slot[3]} kg/m3)"
    raise ValueError(f'undeclared AUTH slot rule {kind!r}')


def instrument_book(m, inputs):
    """The AQS-CTL-001 census book: the instrument index rows (tag, unit,
    sector, type, spec, range, signal, loop, plc, basis) in the v1 write order
    (AQS-INV-004 rows first, then the AUTH extension in table order), the
    range-need flags (the doc's deviation table), and the count of authored
    rows appended. Reads the OTHER_INVENTORY rows from
    inputs['other_inventory'] (absent payload = the v1 missing-inventory
    branch: only the AUTH units cover, and the coverage gate fails loud) and
    the graph from the model. No drivers are read. Raises loud on an authored
    unit off the graph, a duplicate tag, or a process unit without a loop (the
    v1 asserts, the AUTH-coverage gate)."""
    N = _INV._node_view(m)
    E = {e['stream_id']: e for e in _INV._edges(m)}
    rows = []
    cnt = collections.Counter()
    flags = []
    for r in (inputs.get('other_inventory') or []):
        if r['category'] != 'instrument':
            continue
        if r['item'].startswith('gas detector'):       # AQS-SAF-006, fire panel and SIS wiring
            continue
        u = r['unit']
        n = N.get(u) or {}
        p = n.get('params') or {}
        L = LET[r['item']]
        cnt[(u, L, 'SIF' in r['item'])] += 1
        tag = f"{u}-{L}-{(89 if 'SIF' in r['item'] else 0) + cnt[(u, L, 'SIF' in r['item'])]:02d}"   # SIF elements 90+ (AQS-CTL-003)
        sig = DI if L == 'LSH' else AI
        if L == 'FT':
            sid = r['basis'].split(':')[0].strip()
            e = E.get(sid) or {}
            q = (e.get('rate') or {}).get('value') or 0
            rho = ((e.get('params') or {}).get('density_kg_m3')) or flo('1000.0')
            lh = q / rho * 1000 / 24
            rng = f'0-{_nice(2 * lh):g} L/h' if lh > 0 else '0-10 L/h (standby line)'
            note = f'{sid} normal {lh:.2f} L/h'
        elif L == 'PT':
            d = p.get('design') or {}
            dk = p.get('design_kPa') or d.get('design_kPa') or (d['P_MPa'] * flo('1000.0') if d.get('P_MPa') else None)   # either place on the graph
            need = flo('1.25') * dk / 100 if dk else 0
            inv = float(re.search(r'0-([0-9.]+)', r['size']).group(1))
            top = next((x for x in PR if x >= need), PR[-1]) if need > inv else inv
            rng = f'0-{top:g} bar g'
            note = f'design {dk} kPa g' if dk else 'no design pressure on the graph'
            if need > inv:
                flags.append((tag, r['size'], rng, f'design {dk / 100:.0f} bar g'))
                if top > 16:
                    r = dict(r, spec='316L thin-film strain gauge, IEC 61298')   # same element rule as flow_graph/inventory/other.py
        elif L == 'TE':
            T = (p.get('design') or {}).get('T_C')
            cry = u.startswith('CRYO') or 'cold' in (n.get('class') or '')
            hot = any(k in u for k in HOT_KEYS)
            rng = '-200 to 50 C' if cry else (K600 if hot else AMB)
            note = f'design T {T} C' if T is not None else 'band by service'
            if T is not None and not cry:   # span must contain the design temperature with margin: smallest standard band with top >= 1.1 x T
                band = next((b for b in TE_BANDS if b[0] >= flo('1.1') * T), TE_BANDS[-1])
                if band[0] > (150 if not hot else 600):
                    rng, r = band[1], dict(r, spec=band[2].replace('316L thermowell', 'own thermowell') if 'SIF' in r['item'] else band[2])
        else:
            mm = re.search(r'\(([0-9.]+) m full', (p.get('relief_basis') or {}).get('design_case') or '')
            h = float(mm.group(1)) if mm else None
            rng = f'0-100 % of {h:.2f} m' if h else '0-100 % of vessel height'
            note = 'alarm at 90 %' if L == 'LSH' else 'A-M-182 liquid height'
            if L == 'LSH':
                rng = f'trip at 90 % ({flo("0.9") * h:.2f} m)' if h else 'trip at 90 % of vessel height'
        rows.append(dict(tag=tag, unit=u, sector=r['sector'], type=r['item'], spec=r['spec'], range=rng, signal=sig,
                         loop=tag.replace('-', '', 1), plc=f"PLC-{r['sector']}", basis=note))
    # the merge: an AQS-INV-004 row of the same letters wins; an authored SIF
    # element is skipped where the inventory already carries the -90 element
    have = {(r['unit'], r['tag'].split('-')[-2]) for r in rows}
    nauth = 0
    for u, L, typ, spec, rng, sig, basis, sif in AUTH:
        rng = _resolve(rng, u, N, E)
        basis = _resolve(basis, u, N, E)
        if u not in N:
            raise ValueError(f'authored unit {u} not on the graph')
        if (u, L) in have and not sif:
            continue            # an AQS-INV-004 row of the same letters wins once the inventory lane catches up
        if sif and any(r['unit'] == u and r['tag'].endswith(f'-{L}-90') for r in rows):
            continue
        num = (90 if sif else 0) + sum(1 for r in rows if r['unit'] == u and r['tag'].split('-')[-2] == L
                                       and (int(r['tag'].split('-')[-1]) >= 90) == sif) + (0 if sif else 1)
        tag = f"{u}-{L}-{num:02d}"
        rows.append(dict(tag=tag, unit=u, sector=N[u]['sector_id'], type=typ, spec=spec, range=rng, signal=sig,
                         loop=tag.replace('-', '', 1), plc=f"PLC-{N[u]['sector_id']}", basis=basis))
        nauth += 1
    tags = [r['tag'] for r in rows]
    if len(tags) != len(set(tags)):
        raise ValueError('duplicate instrument tags')
    covered = {r['unit'] for r in rows}
    no_loop = [uid for uid in N if uid not in covered]
    boundary = sorted(uid for uid in N if N[uid].get('class') == 'boundary')   # trade and bookkeeping boundaries, not process units
    if not set(no_loop) <= set(boundary):
        raise ValueError(f'process units without a loop (extend AUTH): {sorted(set(no_loop) - set(boundary))}')
    return {'rows': rows, 'flags': flags, 'auth_rows': nauth, 'boundary_units': boundary}
