# First-principles audit — 2026-10-17 (post 8d1e918)

Three-lane audit: planning-doc principles (40 testable rules), graph structure,
engineering coherence. Full lane outputs in session logs; findings merged below.

## Verdict: organization SOUND-WITH-CAVEATS; execution under-wired, not mis-conceived

19-sector organization is coherent flowsheet practice; one connected component
(157/167 units); zero closure failures caused by a wrong process concept. All 43
failing units trace to the scope pivot's mechanics: ~17 structural (missing/
placeholder/degenerate edges), ~24 numeric (null or inconsistent rates), 2 orphaned.

## Blocking owner decisions (param pass cannot close without them)

- D-AIR: air-separation source. CRYO_ASU and H2O_ELYZ both retired; CRYO_O2/N2
  have zero feed while O2 demand is ~131 kg/d vs 0.6 kg/d single source (GROW_BED
  S87) — breaks the O2 N+1 rule. Options: restore ASU/ELYZ from BH, re-basis the
  cold boxes with a dock air feed, or a named import.
- D-FARM: GROW_BED. Recommendation: keep + re-base to crew duty (food and
  photosynthetic O2 are named N+1 life-support systems); retire TERRACE_IRRIG
  outright (all-zero false-pass; drop S40 from balance.py STOICH).
- D-GEO_ORC: HL-Q4-REJ 10.16 kW (largest ladder flow) terminates on the
  placeholder GEO_ORC. Resolve the sink (real ORC, GEO_HP lift, or Q4 dump with
  basis) — heat-ladder test cannot close otherwise.
- D-PV: three mutually inconsistent numbers on one feeder: PV_ARRAY params
  70 kWp, IA-PV-01 edge 242.07 kW, inverter 60 kW; D75 rule (2.0 x balancing
  nameplate, ~3394 kWp per POWER_SIZING Rev F) entirely absent from the graph.
- Doc contradictions to rule (lower priority): BACKUP_GEN 2.5 kW graph vs 40 kW
  docs; inverter count 1 vs 47 vs 48 vs 56; crew 4 vs 2 (LIFE_SUPPORT note);
  IA-NAOH-MU steady NaOH import vs DOCK_BOUNDARY import ban.

## Structural corrections, ranked by leverage (extends R10)

1. Flip 8 BH placeholder edges to present (S25, S28, S29, S52, IA-OIL-01/02,
   IA-BMED-03/04) — rates already in-graph, ~7-8 of 43 failures, one commit.
2. D-AIR resolution + re-home NOX_SCRUB outlets (IA-NOX-N2/CO2 -> CRYO_N2/CO2),
   give HDR_O2 an outlet (PROD_O2/export) — ~4 units + unblocks o2_close.
3. Repair the polish loop: replace the degenerate IA-POL-02 self-loop with the
   real POLISH_BANK->CONTINUOUS_RECYCLE edge, rate MO_CELL_RAFFINATE/POLISH_TO_LI
   — 3 units but 10.4 t/d = 61% of total residual; removes NORTH_DOCK +3772
   knock-on and the -3743 negative-rate artifact.
4. D-FARM resolution (GROW_BED re-base + TERRACE retirement).
5. Utility hygiene: delete dup S05/S64; re-layer S76 to mass; activate
   IA-ESS-ZNBR2-CHG/DIS; add elec edges for IND_MELT/VAC_IND/RF_HEAT (foundry is
   the heaviest load block with zero electrical edges); rate IND/VAC_HEAT_TO_HX;
   retire dead HL-HX8-Q3-A/B; wire CRYO_DED_COOL; add BOUNDARY_EXPORT to SINK.

## Organization defects (schema-level, beyond closure)

- Placement: *_POT/*_CELL cluster (6 units) in MFG but 100% of edges go to
  FOUNDRY/DIGESTER; Q4_BUS (plant thermal bus) parked in HAB; MEOH_COND in ELEC;
  S13_CLASS_TREAT dead+unclassed in DIGESTER (grey-water language); AFTERBURNER_FLUE
  unclassed junction with no DIGESTER neighbour.
- Dead nodes (8): FORGE, RES_HEAT, RF_HEAT (FOUNDRY primary heat unconnected),
  LITHO_COAT/ALIGN/DEV (real tools dead while LITHO_STUB carries flows),
  LOAD_AGG, S13_CLASS_TREAT.
- Sector definitions: mvs.sectors + design_tool sector_definitions.py missing
  DIGESTER/FOUNDRY/HEAT/POLYMERS; 6 stale rows (WET, TRR, ELEC_PV, ZNBR2,
  BACKUP_GEN, FUEL_CELL); ESS_PEER_SECTOR_IDS stale.
- Denormalized from/to_sector_id wrong on ~55% of carrying edges (188/288 or
  316/576 depending on basis) — legacy names + GAS->CRYO placeholder stamps.
- Composition on only 35% of mass edges (120/340) — element closure impossible
  for 65%; phase vocabulary split (E/electric, heat/thermal); 5 Q4 feeds phase E
  but carry heat.
- Class taxonomy: 67 classes/167 nodes, 35 singletons, 4 unclassed; duplicative
  pairs mill/forming, cell/ew_cell, melt/furnace, caster/former, digest/vessel;
  'intra' used as a class; SOLAR_PV_CELL (FAB headline product) a study_stub.
- Missing links: no ELEC feeds to FOUNDRY/POLYMERS; no HEAT to FAB/MEOH; 4 of 6
  MFG cells have zero inbound (no chloride feeds); export outlets missing for
  FOUNDRY/MFG/FAB/POLYMERS/MEOH vs the every-surplus-has-an-outlet rule; S99
  water-surplus edge absent.
- Electrical triangle unauditable: storage unplugged (ZNBR2 ties placeholder),
  foundry loads unwired, PV/inverter mismatch above; S20 direction reversed.
- Heat: RECTIFIER 10 kW x2 at Q3 suspect (electronics cooling cannot heat an
  85 C store; belongs at Q4 or GEO_HP lift); foundry furnace heat unintegrated.

## Principle failures vs the 40-rule checklist (computable today)

P2 closure: 43/97 fail (was 0 at BH). P19 O2 N+1: broken (single 0.6 kg/d
source). P33 dock ban: IA-NAOH-MU violates. P35/P36: five sectors lack export
outlets; water surplus >=50 L/d absent. P15/P16 D75: not represented. P38 board:
TASK_PLAN stranded at BH/212 (R6 pending owner ruling on sector rows).
