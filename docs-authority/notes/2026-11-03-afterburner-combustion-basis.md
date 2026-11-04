# 2026-11-03 AFTERBURNER combustion basis made self-consistent (physics-audit F-1/F-1b)

The AFTERBURNER combustion set booked mutually inconsistent physics: the O2 edge
(IA-AB-O2 0.528 kg/d) counted only a 3 %-organics proxy of the NCG, the flue edge
(IA-AB-FLUE 7.097 kg/d) passed the 5.0 kg/d C1-C4 fuel through unburned, and the heat
ladders (HL-AFTERBURNER-Q1-A/B, 1.383 kW rated each) booked the release for full
combustion of the same fuel (AQS-DUTY-008 basis: 15.0 kg CO2/d / 3.002 kg CO2 per kg
= 5.0 kg/d fuel, 47.46 MJ/kg LHV, 2.744 kW release). Heat assumed everything burns;
mass and O2 assumed nothing does. Fixed at the source (transfer function + drivers),
then regenerated through the tree. A-M-452 records the basis.

## Derived combustion set (one fuel basis)

NCG mix (AQS-DUTY-008, `docs-authority/_hl_edges_study.py` NCG dict, the AQS-DUTY-010
fuel basis): CH4 0.25, C2H4 0.25, C2H6 0.10, C3H6 0.25, C3H8 0.15 by mass.

- Stoich O2 per kg fuel = sum w (x + y/4) 32 / M = CH4 4.000, C2H4 3.429, C2H6 3.733,
  C3H6 3.429, C3H8 3.636, weighted 3.633 kg/kg (driver
  `OIL.afterburner-train.ncg_o2_stoich_kg_kg`).
- CO2 yield = sum w x 44 / M = 3.002 kg/kg (driver `ncg_co2_yield_kg_kg`; the DUTY-010
  note "CO2 15.0 / 3.002" that fixes the 5.0 kg/d NCG rate).
- Excess air 10 % (`combustion_excess_O2` = 1.10, TURNS2012, unchanged).

| Quantity | Before | After | Basis |
| --- | --- | --- | --- |
| IA-AB-O2 | 0.528278 kg/d | 19.982838 kg/d | 1.10 x (5.0 x 3.633 + CO 0.000 + S11 dry 0.0017) |
| IA-AB-FLUE | 7.096878 kg/d | 26.551438 kg/d | NCG 5.0 + S11 0.8 + biogas 0.0986 + cake 0.67 + O2 in (products = mass through) |
| S67 | 117.4276 kg/d | 136.8821 kg/d | + dilution air 110.3307 (unchanged edge) |
| S67B | 14.050492 kg/d | 13.810366 kg/d | Rev N base (sized to the 15.0 kg/d flue-CO2 duty) + SiC CO increment only |
| IA-NOX-CO2 | 21.581514 kg/d | +1.201 kg/d uncaptured NCG CO2 | CO2 formed 15.011 less the KO cut 13.810 |
| Heat ladders | 2 x 1.383 kW rated | unchanged | already the full-combustion basis (2.744 kW release) |

Products check: CO2 15.011 + H2O 8.154 + excess O2 1.817 + Ar 0.200 + S11 water 0.798
+ biogas 0.0986 + cake 0.67 = 26.552 kg/d = fuel in + O2 in. The chamber has margin:
the bounding sizing case (AQS-DUTY-063 Rev B, 242.45 kg/d flue at 850 C) still governs;
the live burner flue (26.55 kg/d) gives residence far above the 2 s requirement, so no
geometry changes (models/mfg/AFTERBURNER stays at ID 200 x 600 mm).

## Double-counts removed (the same audit class)

The old organics term `ab_org = NCG 3 % x 1.066 + 0.3195 + S11 0.1 % x 1.066` folded in
0.3195 kg/d - the sanitation cake/biogas combustion O2, which the X-SAN-01 Rev B deltas
already book on the air chain (S83/S02, A-M-118). It was counted twice: at x1.10 on
IA-AB-O2 and as a supply cut on the deltas. The same constant's share of the S67B
increment (ab_org/2) double-booked the sanitation CO2 against the deltas' IA-ASU-CO2
term, and its share of the IA-NOX-H2O increment double-booked the sanitation water.
All three removed; the deltas are untouched (X-SAN-01 Rev B owner decision stands).

## Species routing on the new basis

- The KO cut S67B keeps its Rev N base ("sized to the neighbor" - the AFTERBURNER
  15.0 kg CO2/d duty, farm-trim allowance +0.554). The increment now counts only
  burner carbon outside that basis (SiC CO, currently a zero edge).
- The NCG combustion CO2 the cut does not capture (15.011 - 13.810 = 1.201 kg/d) now
  books on IA-NOX-CO2 to the cold box, so no flue carbon leaves uncounted; the
  methanol C-sink sees it (S73 closes CRYO_CO2 by difference). Methanol CO2 feed
  moves 47.396 to about 48.357 kg/d (+0.961); the electrolyser follows the H2 demand
  (+0.132 kg/d H2, +1.085 kg/d O2).
- The NCG combustion water (8.15 kg/d vapor) and the uncut CO2 tail ride the scrubber
  gas book by difference (IA-NOX-N2), as the old book carried the inert NCG share.
  The species split of flue water between the KO quench, the NOX scrubber water and
  the ASU feed is a refinement lane (the KO duty section 3 quench text owns that
  balance); mass closes either way.

## O2 ledger headroom (why no owner decision is needed)

Sources: bed S87 0.642 + ASU excess recovery IA-ASU-O2 1.832 (was 0.064) + electrolyser
IA-ELY-O2 75.348 (was 74.263) = 77.821 kg/d. Draws: header 29.738 (was 10.284; IA-AB-O2
+19.455) + direct CRYO_O2 41.800 = 71.538 kg/d. IA-O2-PROD export falls 22.884 to about
6.283 kg/d and stays positive - the surplus outlet survives, the O2 N+1 pair (electrolyser
+ crew-duty bed, A-M-230) still covers the draws. The A-M-272 headroom figure (27.2 kg/d
surplus) is superseded by A-M-452 (about 6.3 kg/d). This is a visible trade against the
PROD_O2 export, recorded here and in the assumption rather than decided silently; the
physics forces it because the heat ladders already booked the full-combustion release.

## Heat-ladder convention (F-25 interaction)

The A/B ladder edge convention (rated = single-ladder x 1.25, normal = both ladders,
2 x 1.383 kW rated / 0.553 kW normal each on HL-AFTERBURNER-Q1-A/B) is unchanged; the
X-THM-01 transit re-solve keeps holding the source rates. No ladder restructuring in
this lane: the combustion set was made consistent inside the existing convention, and
the heat side needed no change because it was already the full-combustion basis that
mass and O2 now match.

## Changed files

- `flow_graph/param/o2_close.py`: combustion block re-derived (drivers-backed stoich
  factors), S67B increment re-scoped, uncaptured NCG CO2 on IA-NOX-CO2, docstring COMB
  bullet.
- `flow_graph/param/drivers.json`: `OIL.afterburner-train.ncg_o2_stoich_kg_kg` 3.633072,
  `ncg_co2_yield_kg_kg` 3.0023 (both A-M-452).
- `flow_graph/param/stub_activation.py`: CAT_OX design feed carries the consistent
  figures (6.57 kg/d waste + 20.0 kg/d plant-O2 bleed at stoichiometric + 10 %) instead
  of the retired 7.097 kg/d pass-through flue.
- `docs-authority/assumptions_manual.json`: A-M-452.
- Regenerated: graph, duties (AFTERBURNER/AFTERBURNER_FLUE/FLUE_KO/NCG_HEADER/CAT_OX
  section 1 basis lines), O2_SOURCE.md, ASSUMPTIONS_REGISTER.md, balance books, views,
  workbook, tracker params (no geometry change), site registers.
