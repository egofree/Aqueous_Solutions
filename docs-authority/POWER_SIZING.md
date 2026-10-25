# Storage and generation sizing

Document number: AQS-ELEC-007
Revision: F
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-05. From AQS-ELEC-002 Rev C bus demand. Script `docs-authority/_power_sizing.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-060 to A-M-062). Graph sources are not changed (the EW power rate change awaits the owner).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Two cases; PV, storage, inverters, backup. | 2026-10-15 |
| F | X-PAR-08: hall HVAC comparison, gains and slab; air-source kept (owner, D77); 186 x 174 m. | 2026-10-15 |
| E | X-PAR-09 (D75): PV at 2.0 x requirement, cloudy-day storage charge rate, inverters for export. | 2026-10-15 |
| C | X-PAR acid-loop decision: BMED 26.93 kW, EVAP_ACID and EVAP_BASE, RECT-EW at 2.12 V / CE 0.85. Values written by `flow_graph/param/write_graph.py power`. | 2026-10-15 |

## 1. Basis

Flat 24 h profile (continuous process; study). PV yield 5.41 kWh/kWp/d before losses (NREL PVWatts, AQS-SITE-002), system derate 0.80. Night 14 h served from storage at 0.70 round-trip efficiency (ZnBr₂ flow battery class, study). Inverters in 60 kW SOL_ARK units. Backup covers critical loads for 2 days without sun. Rev E (D75): PV at 2.0 x the balancing nameplate; design cloudy day = mean yield / 2.0 (NREL PVWatts v8 output scales with plane-of-array irradiance; daily distribution to verify on the NSRDB TMY, A-M-109); storage charge rate = PV peak on that day less direct load; inverters at the PVWatts default DC/AC 1.2.

## 2. Results

| Item | Bounding EW | Reference EW | Graph now |
| --- | --- | --- | --- |
| Bus demand incl. EXT_HALL, kW | 244.8 | 211.7 | PV average to plant 233.3 |
| Energy, kWh/d | 5875 | 5080 | — |
| PV balancing nameplate, kWp | 1697 | 1467 | 1697 |
| PV nameplate at 2.0 x, kWp (roof only) | 3394 | 2934 | 3394 |
| PV array area on the roof, m² | 29,783 | — | 29,783 |
| Storage energy, kWh | 3427 | 2963 | 3428 |
| Storage charge / discharge, kW | 1113 / 245 | 962 / 212 | 1113 / 245 |
| Inverters | 48 x 60 = 2880 kW | 41 x 60 = 2460 kW | 2880 kW |
| Export at noon, storage full, kW | 2635 | 2248 | 2635 |
| Export energy, clear day, kWh/d | 7344 | 6349 | 7344 |

Backup. Critical loads 15.66 kW graph-derived (HABITATION 3, CRYO_H2 4, CRYO_ASU 1.66 at duty (A-M-238), GROW_BED 5, controls 2; study list). Generator 40 kW — single governed source `drivers.json backup_gen_rated_kW` (this document / AQS-RED-001 rule: 125 % of the issued 32 kW critical list, rounded to 5 kW steps; NFPA 110 standby, 8.4.2 monthly exercise only), read by `_power_sizing.py` and `o2_close.py`, stamped on the graph by `write_graph power()` (D3 unification 2026-10-18; was doc 2.5 / graph 40 / o2_close 40 / ceil formula 20). Two days' critical energy 751.7 kWh; on H₂ at about 33 kWh/kg LHV and 40 % engine efficiency that is about 57 kg H₂ held in CRYO_H2 (study). Graph: BACKUP_GEN rated 40 kW (standby continuous 0.008 kW exercise average), FUEL_CELL 4.0 kW.

## 3. Findings

Rev F (X-PAR-08, 2026-10-15). Hall loads by degree-day split with internal gains, slab edge loss and an air- versus ground-source comparison (ASHRAE 90.1-2025 Table 6.8.1-2): air 91.34 kW / 32,364 m², ground 90.46 kW / 32,292 m². Ground-source first adopted by rule, then reverted by the owner (D77): 27 km of bores for a 0.2 % gain is inside input uncertainty and adds major build complexity. Air-source converged: 186 x 174 m (31 x 29 bays, 32,364 m², 16 arrays, roof capacity 3395 kWp); PV 3394 kWp; storage 3428 kWh, charge 1113 kW; 48 x 60 kW inverters; export up to 2635 kW. Lighting (28.0 kW) and fans (12.0 kW) dominate the hall load. Utility interconnection study is an owner input (A-M-113).

Rev E (X-PAR-09, owner principle D75 2026-10-15: commodity surplus, PV at 200 %). roof_close carries 2.0 x the balancing PV: converged 234 x 138 m (39 x 23 bays, 32,292 m², extension 31,860 m², 15 arrays, roof capacity 3390 kWp); EXT_HALL 90.0 kW (lighting 28.04, ventilation 40.43, envelope 21.54); bus 243.4 kW. A day at half the mean yield still fills the 3409 kWh store; below that the backup case applies. Clear-day surplus is exported through the AQS-ELEC-002 Rev D interconnection; with no utility service the inverters curtail. The footprint grew 2.5 x; X-PAR-08 (ground-source, internal gains) is the next lever on the hall load.

Rev D (X-PAR-07, owner decisions 2026-10-15: roof-only PV, grow the building, extension conditioned). `flow_graph/param/solver.py` roof_close iterates the footprint on the 6 m bay grid until the roof, after IFC 2027 1205.3 / NFPA 1 11.12 pathways (1829 mm perimeter, 1219 mm between arrays of at most 45.72 m), carries the PV that closes the balance including the extension's own loads: lighting 8.8 W/m² lit 10 % of hours (IECC 2021 C405, C405.2.1), outdoor air 0.30 L/(s m²) (ASHRAE 62.1-2025) conditioned at COP 3.2 (ASHRAE 90.1-2025 Table 6.8.1-2) with ISO 16798-3 SFP 3 fans, roof U 0.199 and wall U 0.534 W/(m² K) over the full new perimeter at 6 m eave (IECC 2021 Table C402.1.4, climate zone 3), mean |dT| 7.9 K from the NOAA 1991-2020 DFW degree days. Converged: 156 x 84 m (26 x 14 bays, 13,104 m², extension 12,672 m²); EXT_HALL 37.26 kW (lighting 11.15, ventilation 16.08, envelope 10.02); bus 192.7 kW; PV 1336 kWp roof-only (roof capacity 1341 kWp, 8 arrays); ZNBR2 2698 kWh / 193 kW; SOL_ARK_60K 4 x 60 kW (was 3). Roof framing LRFD 1.72 kPa (ASCE 7-22). Ground field removed. The earlier 33,500 m² estimate assumed lighting at 100 % of hours; with occupant-sensor control (10 %) the conditioned hall converges at 13,104 m². GEO_GHEX coupling not applied (bore field sized for Q4; a ground-source unit at COP 3.6 would cut the envelope and air loads by about 11 %). A-M-103 to A-M-105.

Rev C (X-PAR acid-loop decision, AQS-PAR-001, 2026-10-15). BMED_ACID at the published SEC 26.93 kW (was 16.13), EVAP_ACID 2.41 kW and EVAP_BASE 2.51 kW added (2.40 kW after the NaOH balance, X-PAR-06), RECT_EW 38.66 kW AC (was 38.02). Bus load +16.36 kW, carried on IA-PV-01. Graph: PV_ARRAY 1078 kWp (was 984), about 5390 m²; ZNBR2 2176 kWh / 156 kW (was 1987 / 142); SOL_ARK_60K 3 × 60 kW unchanged. Rev B text below keeps its own figures.

Rev B (X-RSZ-02, 2026-10-15). The bounding case is booked on the graph: PV_ARRAY 984 kWp nameplate (1968 × 0.5 kW, about 4918 m² ground field off the plate), ZNBR2 1987 kWh / 142 kW, SOL_ARK_60K 3 × 60 kW. RECT_EW (38.02 kW AC) and BMED_ACID (16.13 kW) have graph feeds; PV average raised by 54.15 kW to carry them. Items 1 and 2 below are superseded: the plate restriction is revised by the off-plate PV field (site area to confirm, X-BAS-03).


1. The graph's energy system (70 kWp PV, 120 kWh ZnBr₂, one 60 kW inverter) covers about a tenth of the calculated demand. Most of the demand is still study shares (AQS-ELEC-003); CRYO_ASU 18 kW, MFG_SHOP 12 kW and RECT-EW dominate.
2. PV at 758–984 kWp needs 3792–4918 m², far beyond the plate. Owner choices: a utility service, a smaller plant rate, or load reduction. None is taken here.
3. Pumped hydro (HYDRO_SET, about 7 kWh recoverable) does not change the result.
4. The backup generator and the H₂ store must grow with the critical list, or the critical list must shrink.

## Code basis (X-STD-01)

| Check | Governing clause |
| --- | --- |
| Roof PV access | NFPA 1-2027 11.12; IFC 2027 1205.3 |
| Energy storage | NFPA 855-2026 |
| Ventilation fans | EN 16798-3:2017 |
| PV modelling | NREL PVWatts v8; IEC 61724-1:2021 performance monitoring |
