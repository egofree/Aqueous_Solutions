# Balance close

Document number: AQS-DUTY-078  
Former number: AQS-DUTY-011 (shared with REV_M_CLOSURE_DUTY.md until 2026-10-24; that page keeps it)
Revision: A
Date: 2026-10-09
Authority: graph Rev M. Not a PE stamp.

The eleven Rev L open balances are closed on the graph. Feeders are sized to the continuous neighbor draw. A standby unit is rated zero on the design day.

| Node | Close |
|---|---|
| H2_DRYER, CRYO_H2 | S64 retired. It was the same pipe as S05. Pool is 5.74 kg/d: fuel cell 4.8, methanol synthesis 0.94. Genset S45 is 0 on the design day. |
| NUTRIENT_DOSE, GREY_TREAT | S12 retargeted to GREY_TREAT. Digest surplus 13.93 kg/d goes to the VCD. Sludge, including the electrolyte bleed, returns to the leach. |
| BMED_UPW_POLISH | Distillate raised to 168.22 kg/d. Fab 60, remineralizer 10, and reject 3.22 are edges. VCD feed basis is 0.187 m³/d. |
| CRU | Chlorate only. S66 in, chlorate liquor back to the leach. |
| BMED_ACID, BMED_BASE | Sized to the digest, 593.5 mol/d, as 20 wt% liquor. A 2 M delivery would need a water plant the condensate cannot feed. Unused acid returns to the leach. |
| Q4_BUS | Life load 3.0 kW is an edge. Surplus 10.09 kW goes to a dry cooler. An ORC is not justified at that duty. |
| SOL_ARK_60K | S20 reversed. Rectifier is the 12 kW continuous rating, not the 50 kW peak. PV daily average 11.59 kW closes the bus. |
| ZNBR2 | Circulation returns. Bleed equals the purge-water accumulation. Make-up comes from the leach. |
| AFTERBURNER | Flue leaves the node. S11 carbon, 0.554 kg/d, is folded into S85 and S89. |

`loops_closed` and every `*_on_site` flag stay false. The chloride inventory at the electrowinning anodes is still the authority Faraday figure, and it is larger than this BMED. BMED is sized to the caustic user, not to that figure.
