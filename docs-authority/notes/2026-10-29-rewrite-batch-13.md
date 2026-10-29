# Rewrite batch 13: the pages of the unit sizing sweep

Date: 2026-10-29

The unit sizing sweep, `docs-authority/_unit_sizing_sweep.py`, writes one page AQS-SIZE-<UNIT> for each unit it owns. It owned only units whose unit task 02 was still open in the task plan, and none is open now, so it had stopped writing its pages and they had kept the text of their first issue on 2026-10-20. The sweep now also owns every present unit whose page carries its document number, and it rewrites them all as revision B.

The first issue had four errors, which revision B corrects:

- The vessel diameter and height were printed in metres under a millimetre label.
- The vessel was sized from the sum of the inflow and the outflow, which counts the throughput twice; it now uses the larger of the two.
- Every unit was given a polyethylene material by default, including molten-salt cells at 700 °C. The material now comes from the graph (`params.sec3_material`) or from section 3 of the unit's duty sheet.
- The fit of the vessel in the envelope was stated as true by construction. It is now checked, and the envelope is read from `params.size_mm` or the placement files where `params.envelope` is empty, which had printed an envelope of zero.

The pages also gain a purpose and scope section, a record of revisions, and the design parameters in a table.

On the present graph, one day of flow does not fit within the envelope of these units, which therefore hold less than a day as their duty sheets set: ACID_POLISH_SCRUB, ALK_SCRUBBER, BMED_ACID, BMED_BASE, C29_RECYCLE, CONTINUOUS_RECYCLE, CRYO_CO2, CRYO_O2, EVAP_BASE, FLUE_KO, HDR_N2, MET_AHU, MET_SCRUB, MFG_SHOP, NCG_HEADER, NOX_SCRUB, POLISH_BANK, VCD_TRAIN, ZNBR2_BR2_REGEN. These units have no envelope on the graph or in the placement files: ADS_CHILL, DRY_COOLER, EXT_HALL, F_RECOVER, GREASE_CA, GREASE_LI, GROW_BED, H2O_ELYZ, HABITATION, HYDRO_SET, LI_RECOVER, MAU_HX, P_CA, ROOF_TANK, SI_REDUCE.

The internals register AQS-DSN-INT-001, written by `docs-authority/_internals.py`, scans the sizing pages for evidence of internals. It now reads a page of the sweep without its material section, because that section quotes the duty sheet, which the register scans in its own step; without this, a quote on the page of ZNBR2_BR2_REGEN was taken as evidence for ZNBR2. Because the pages now show all the design parameters of a unit instead of the first six, the register finds evidence for two more units, BMED_UPW_POLISH (membrane area and modules) and MEOH_FC (the stack named in its design). The quotes in the register are now cut at a word boundary, so many of them change slightly.
