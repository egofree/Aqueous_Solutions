# Rewrite batch 42d: wafer-fab photoresist made on site, and an honest fab balance

Date: 2026-10-30

## Change

The owner decision of 2026-10-30 asks for the fab polymer consumables to be defined from first principles and made from plant streams, recovery first, with the resist chemistry chosen on the merits. Task X-RTE-POLY_TO_FAB is done.

- The fab's chemical polymer consumable is the photoresist. Wafer carriers, wet-bench parts and seals are formed in the shop from POLY_TO_MFG and FLUORO_TO_MFG, so they are spares and not a direct fab draw.
- The new module `flow_graph/param/fab_resist.py` sizes the resist from the coats per day: the wafer starts of `fab_silicon.py` times fab_mask_layers, times the dispense volume and the solids fraction. The fab also draws acetone for the edge-bead rinse and the strip on IA-FAB-SOLV.
- The resist is the positive diazonaphthoquinone-novolac class. It images at the 365 nm aligner and develops in the aqueous TMAH/KOH bench that LITHO_DEV already is, and every precursor has a plant source.
- The new unit RESIST_SYN makes it in small batches:
  - Benzene extracted from the C5-C10 cut becomes phenol by the Raschig-Hooker oxychlorination. Plant methanol is oxidised in air to formaldehyde, and the two condense to the novolac.
  - Naphthalene extracted from the C11-C18 cut becomes 1-naphthol. Nitrosation with nitrous acid from ammonia oxidation, reduction with header hydrogen, sulfonation with ACID_PLANT acid and diazotisation give the DNQ sulfonic acid.
  - Phosgene from the chlorinator CO and the pot chlorine turns the acid into its chloride, which is esterified onto the novolac. The phosgenation HCl returns to CRU, which turns it back into chlorine.
  - The casting solvent is diacetone alcohol made from SOLV_PLANT acetone. The water of reaction and the ammonium chloride go to the leach as a brine, and the extraction raffinate goes back to OIL_FRAC.
- The stoichiometric ledger is checked for element closure in the code. ACID_PLANT makes the extra acid from sulfur ore, and the sulfur record names the resist sulfur as unrecovered, with its basis.
- The spent resist and acetone go from the develop bench to the SOLV_PLANT still on IA-LITHO-OUT instead of to OIL_FRAC. The still returns the acetone, and its bottoms carry the resin to the oil cut.
- The negative cyclised-polyisoprene and bis-azide class is not built. It needs an organic developer, and its isoprene and aromatic azide have no route on the plant. Those precursors are open tasks X-RTE-RESIST-ISOPRENE and X-RTE-RESIST-AZIDE.

## Finding: the fab balance was closed by the nitrogen purge

Before this batch the S03 nitrogen purge, 1.50 kg/d, entered WAFER_FAB and never left it. It balanced two flows that had no source: the 0.99 kg/d resist and solvent issue on IA-LITHO-IN, and the 0.51 kg/d IA-FAB-LOSS dust line to BAGHOUSE. The dust line duplicated the kerf that `fab_silicon.py` already sends to the leach on IA-FAB-KERF.

- The purge now vents to atmosphere on IA-FAB-N2-VENT at the S03 rate.
- IA-FAB-LOSS is retired, and BAGHOUSE closes on its live inputs.
- The spent rinse water IA-FAB-SPENT closes the fab by difference.

## Values

| Quantity | Before | After |
|---|---|---|
| POLY_TO_FAB, resist solution | 0 | 0.1200 kg/d |
| IA-FAB-SOLV, rinse and strip acetone | none | 0.2195 kg/d |
| IA-LITHO-IN, resist and solvent issue | 0.9875 kg/d, unsourced | 0.3395 kg/d |
| IA-FAB-N2-VENT, nitrogen purge vented | none | 1.4998 kg/d |
| IA-FAB-LOSS, fab dust | 0.51 kg/d | retired |
| C5-C10 and C11-C18 cut drawn for extraction | none | 1.0052 and 0.3664 kg/d |
| RESIST_SYN load | none | 0.0037 kW |

The basis is recorded in A-M-432. AQS-PAR-001 is at revision H, with section 7.4 and Table 7.6, and the glossary AQS-GLO-001 is at revision D with the entry DNQ.
