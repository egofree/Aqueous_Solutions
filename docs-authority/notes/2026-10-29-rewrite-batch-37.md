# Rewrite batch 37: the acid cake kiln runs in campaigns (Q-034)

Date: 2026-10-29

## Change

The owner delegated questions Q-034 to Q-037 to a decision on the merits (t62u). This batch closes Q-034, which asked about the sulfuric acid route and the duty of the cake kiln.

- The route stays GYPSUM_LOOP. It recovers the acid sulfur from the HF kiln cake, and SULFUR_ORE recovers none, which fails the recovery-first rule (A-M-423).
- At the present acid demand the shell loss of the kiln is nearly all of its load. `flow_graph/param/sulfuric.py` now models the kiln duty, selected by the new driver acid_kiln_mode. On CAMPAIGN, the default, the cake is stored and fired in one run every acid_kiln_campaign_d days, and a day store holds the acid for HF_GEN. Each run pays the heat-up of the Inconel tube and its ceramic-fibre insulation. On CONTINUOUS the kiln is held at temperature every day, as before.
- ACID_PLANT carries the duty in params.kiln_duty, with the average and peak loads and the store sizes. Its continuous_kw is the daily average.
- AQS-DUTY-073 is at revision E. Section 4.1 describes the duty, and Table 4.2 gives both duties.
- The basis is recorded in A-M-425. Q-034 is closed in AQS-OQ-001 revision D.

## Values

| Quantity | Before | After |
|---|---|---|
| ACID_PLANT average load | 0.9660 kW | 0.2061 kW |
| ACID_PLANT peak load during a run | 0.9660 kW | 1.0850 kW |
| Heat-up per campaign | none | 8.60 kWh |
| Cake store | none | 4.21 kg |
| Acid day store | none | 1.54 L |

## Left open

The kiln lining must be checked for the thermal cycles at the first article. CONTINUOUS duty is the fallback.
