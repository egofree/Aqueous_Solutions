# Rewrite batch 39: the Ti, Mo and Cr cells take the float-sink grit first (Q-037)

Date: 2026-10-29

## Change

The owner delegated questions Q-034 to Q-037 to a decision on the merits (t62u). This batch closes Q-037, which asked whether the leach grit should replace the Ti, Mo and Cr ore concentrates.

- Under the recovery-first rule (A-M-423) the plant's own grit comes ahead of ore. Under the redundancy principle the concentrate stays installed as a second, different source. Both sources are therefore built, with the grit first.
- `flow_graph/param/foundry_poly.py` now feeds TI_CELL, MO_CELL and CR_CELL from the dense grit of FLOAT_SINK on FLOAT_SINK_GRIT_TO_TI, FLOAT_SINK_GRIT_TO_MO and FLOAT_SINK_GRIT_TO_CR, as far as the grit assay supports. The gangue and the oxide the chlorination does not take up return to the leach on TI_CELL_SLAG_RETURN, MO_CELL_SLAG_RETURN and CR_CELL_SLAG_RETURN. The concentrate edges carry only the shortfall, and the float-sink liquor return falls by the grit drawn.
- No assay of the grit exists yet (AQS-ASSAY-TI-MO), so its content is not invented. The dense fraction and the TiO2, MoO3 and Cr2O3 contents are driver inputs (grit_dense_frac and grit_TiO2_wt, grit_MoO3_wt and grit_Cr2O3_wt), and they are 0 until the assay lands. Until then the grit feeds stand by at 0 and the concentrate carries the full need. Setting the assay values moves the feed to the grit with no code change. The driver grit_route_mode selects GRIT_FIRST, the default, or ORE_ONLY.
- A trial with assumed assay values (dense fraction 0.05, TiO2 0.3) moved 0.25 kg/d of TiO2 from the concentrate to the grit, and the balance and the recovery-first check stayed clean. Those values are not used in the design.
- The basis is recorded in A-M-427. Q-037 is closed in AQS-OQ-001 revision F.

## Values

At the design point the assay drivers are 0, so the rates do not change.

| Quantity | Before | After |
|---|---|---|
| IA-TIO2-MU, IA-MOO3-MU and IA-CR2O3-MU | full need | full need, less the grit oxide (0 until the assay) |
| FLOAT_SINK_GRIT_TO_TI, _MO and _CR | TI only, at 0 | all three, standby at 0 |
| MO_CELL_SLAG_RETURN and CR_CELL_SLAG_RETURN | none | standby at 0 |

## Left open

The grit is shared in the order Ti, Mo, Cr. When the assay lands, it should also give the Fe and gangue terms of the chlorination, which take chlorine and carbon.
