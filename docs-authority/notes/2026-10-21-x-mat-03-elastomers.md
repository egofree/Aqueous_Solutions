# X-MAT-03 — Elastomer and gasket compatibility per service (AQS-STD-002 Rev N §14, AQS-PIP-003 Rev B)

Date: 2026-10-21. Item: X-MAT-03 (closed; depends X-MAT-01, done). Triage: desk P2.

## What was done

1. **Registered source.** Parker Hannifin O-Ring Division, *Parker O-Ring Handbook*, ORD 5700
   (2022 ed.) — the same source class as the existing manufacturer guides ([S1]–[S4]). Registered
   as **[S23]** in MATERIALS_STD. PDF cross-checked (ord5700 full text): EPDM heat window
   (150 °C; 204 °C max in water/steam; hot water/steam to 149 °C, special compounds to 260 °C;
   Na/K alkalis; many organic/inorganic acids; many polar solvents — alcohols, ketones, esters;
   NOT mineral oil/fuels), FKM (to 204 °C; ozone/oxygen/mineral oil/fuels/aromatics; special
   compounds with improved acids resistance; static low-temp −26 °C), FFKM (320 °C; polar
   solvents, acids, water/steam verified), and the explosive-decompression passage (smaller
   cross-sections resist high-pressure gases better).
2. **§14.1 per-class decision table** over all nine AQS-PIP-003 Rev A classes: FKM on the
   acid/hydrocarbon/vent families within the class T ceilings; EPDM on P4/P5 (alkali/water);
   spiral-wound 316/graphite + PTFE-for-O₂ on M1; SW 304/graphite on M2 (no elastomer by design
   at 250 °C oil); PTFE soft goods on G1; FKM on F1.
3. **§14.2 family exceptions and held checks**: solvent families (wet MeOH, organic liquid
   ethanol+acetone) → EPDM primary ([S23]: alcohols/ketones in its polar-solvent range), FFKM
   alternate, the exact FKM grade stays a maker-table check per line; Q3 100 °C water → EPDM
   special compound (maker confirmation at procurement); wet-acid H₂ header → FKM, bonded
   hardware, no RGD exposure at the relief-bounded pressure; dry H₂ → FKM O-rings, RGD-grade
   check held for compressed-H₂ duty with X-MAT-09; 98 wt% H₂SO₄ leg → PTFE envelope over FKM;
   fluoro train → issued duty-sheet rows govern (unfilled PTFE preferred in HF; PIP-003 Rev B
   pending); pot brines → defer with unit task 09; launder pours → no flanged joints;
   Q1/Q2 pump seals → mechanical-seal maker package (elastomer ceiling 204 °C < 250 °C oil);
   WS_DOPE/WS_SLURRY → EPDM at vessel flanges; potable UPW → potable-certified EPDM.
4. **Machine gate.** New `docs-authority/_gasket_census.py`: every PIP-003 class must have a
   §14.1 row, every §12.1 family class must be covered by §14.1/14.2, and every §14 row must
   cite a registered source ([Snn]/PERRY9_MAT/ULLMANN_FLUOROPOLY/AQS-REV-H2-001) or a named
   deferral; exits nonzero otherwise. Green: 9 classes covered, 9 per-class + 12 family rows,
   8 family classes covered.
5. **Pointer hygiene.** The "gasket detail stays X-MAT-03" holds in §12.3/§13 resolve to §14;
   AQS-PIP-003 → Rev B (its §3 "Held: elastomer selection per service is X-MAT-03" now points
   at MATERIALS_STD Rev N §14; the class-sheet rows stay Rev A defaults).
6. **Board.** X-MAT-03 in DONE_X, EVIDENCE_PASS → MATERIALS_STD.md, dated comment; TASK_PLAN
   line 579 ticked.

## Explicitly open (named, not blockers)

- FKM-grade verification for methanol/acetone duties; compound confirmation at 100 °C water and
  for the potable joints; RGD compound grading when compressed-H₂ P/T (X-MAT-09) is sized;
  Q1/Q2 pump mechanical-seal maker data. All are procurement-time maker-table checks named in §14.2.

## Verification

- `_gasket_census.py` green; pytest 43; `regen --check` 920 files 0 stale (no graph writes this lane);
  `_service_census.py` and `_ambiguous_units.py --done` unchanged-green.
