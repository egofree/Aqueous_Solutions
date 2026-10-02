# Graph audit

Document: AQS-AUD-GRAPH-001
Date: 2026-10-02
Object: artifacts/plant_flow_graph.json Rev D (99 nodes, 130 edges) and placement_seed.json Rev D.
Not a PE stamp.

## Faults

1. PROD_C29 is not a node. Edge C29_RECYCLE starts there and dangles. The cut tanks exist in oil_line.py and are absent here.
2. IA-OIL-03 sends "frac cut / vapor" to AFTERBURNER. Product cuts and NCG are not the same stream. C29 must not be burned.
3. S67 AFTERBURNER_FLUE → CRYO_CO2. Flue is N2, O2, CO2, NOx. That node then feeds MeOH synth (S73) and is the plant CO2. No separation step is drawn.
4. S46 BACKUP_GEN → GREY_TREAT carries "H2O + NOx". S29 sends grey to VCD. NOx water does not belong on the life/grey train.
5. S81 MEOH_FC → GREY_TREAT. Methanol residual in product water, same grey train.
6. S39 WAFER_FAB → LEACH_CSTR_1 carries spent slurry, solvent, and photoresist. Solvent and resist into chlorate leach is oxidizer plus fuel. Solvent belongs on the oil line.
7. S72 MET_SCRUB → LEACH_CSTR_1 carries organic mist into the same leach.
8. IA-BMED-01 and IA-BMED-02 send BMED acid and BMED base into BMED_UPW_POLISH. Acid and base are not polish feed. S09 then leaves that node as HCl/NaOH to the wet bench. One node, two duties.
9. S38 LITHO_STUB → WET_BENCH is labeled resist/solvent waste. Waste does not flow into the bench.
10. S70 CRYO_AHU condensables → CRYO_H2. Condensate into the hydrogen box contaminates the fuel header.
11. S68 flue/AHU condensate → S13_CLASS_TREAT. Flue liquor is not class-treat feed for a life-side unit.
12. Glass edges are rinse → burnout → mill. Rinse water is then evaporated in the burnout. Mill before burnout, or a dry step between rinse and burnout.
13. HL-HX8-* leaves EW_1. HX-8 is not a node. The cell is not the exchanger.
14. Cross-tie edges are drawn only A→B. The diode rule is hot-to-cold either way. One directed edge cannot say that.
15. Q1 oil battery pipes downhill to Q4 water. A shared fluid would put oil in the life header on a leak. Each step needs its own thermosyphon. Only the Q4 exchanger touches Q4 water.
16. S24 H2 relief and S56 cryo residual still end on BOUNDARY_EXPORT. Those are open vents. S65 and S69 are self-loops standing in for a scrubber residual and a Br2 regen node that were never drawn.
17. EW-3 through EW-8 are not nodes. IA-EW-02 jumps EW-2 to EW-9.

## Layout collisions in the seed

Same level, boxes overlap: ZNBR2 with BACKUP_GEN; MEOH_FERM with GEO_HP_CLOSED_LOOP and GEO_ORC; MEOH_SYNTH with GEO_ORC; FAB_UPW_TANK with SOLAR_PV_CELL; Q4_BUS spine with MET_AHU, MET_SCRUB, MET_HX_Q4, ELECTRODE_COAT. C29_RECYCLE and CONTINUOUS_RECYCLE were given block-sized boxes and sit on top of the Q*_A and Q*_B batteries. Pipes are not 8 m tanks.

## Not faults

ZnBr2 has no edge to CRU. C29 no longer ends at leach. CONTINUOUS_RECYCLE liquor edge ends at LEACH CSTR 1 only. Q1 no longer tees to Q4_BUS. Hydro penstock pair S22/S23 is consistent; the duplicate IA-ESS-HYDRO edges add nothing.
