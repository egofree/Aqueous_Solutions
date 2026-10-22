# VAC_IND fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service vacuum induction skull melt (ISM), N+1 diverse of IND_MELT; design_case_kg 2; connected_kW 15; backup_of IND_MELT; outage_d 2; duty_

Internals: duty sheet: "ll melt); outage_basis IND_MELT relining/repair outage 2 d (crucible life 20-50 heats, AQS-SIZE-FOUNDRY sec. C" [docs-authority/duties/VAC_IND.md]
Material: Water-cooled copper induction crucible (no wetted-refractory interface) + 304L vacuum chamber; ceramic-fibre insulation on the shell. Basis: vacuum induction skull/ISM melt of Ti sponge, N+1 diverse of IND_MELT, 2 kg batch class (graph design, A-M-282): the water-cooled copper face keeps the Ti melt out of contact with any refractory (CRC_TI melting point 1668 C; INDUCT_SOCX power class). (continues on the duty sheet)

Nozzles: 5 process connections per docs-authority/nozzles/VAC_IND.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
