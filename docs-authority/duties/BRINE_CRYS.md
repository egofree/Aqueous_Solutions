# BRINE_CRYS

Standard: AQS-STD-001 Rev A. Graph Rev AD. Study. Not a PE stamp.

1. Basis. Mass in 2 kg/d. Mass out 2 kg/d. Electrical duty 0.0700 kW. In: IA-BRINE-SRC 2 kg/d (leach-liquor side-stream to the crystallizer). Out: IA-BRINE-CACL2 0.1161 kg/d (crystallized CaCl2 to the calcium pot (recovered, was the dock import)); IA-BRINE-MGCL2 0.03978 kg/d (crystallized MgCl2 to the magnesium pot (recovered, was the dock import)); IA-BRINE-ML 1.844 kg/d (mother liquor (residual chlorides) returned to the leach).

2. Size.
- Graph design (AQS-PAR-001 sizing): cacl2_kg_d 0.1161; mgcl2_kg_d 0.03978; feed_kg_d 2; ml_kg_d 1.844; kw 0.07.
- Node note: Brine crystallizer (A-M-496).

3. Material. CPVC crystallizer body, hood and agitator on the leach side-stream; PVDF (P3) pump and jacket legs on any leg above the CPVC class; FKM gaskets; steel frame and jacket casing outside the wetted and vapour zone. Basis: CaCl2/MgCl2 crystallization out of the hot chloride leach liquor on a 2 kg/d side-stream, the mother liquor returned to the leach (graph design; A-M-503): the leach is an M2 system and its liquor carries the oxidizing chlorate (AQS-STD-002 section 7), so no bare metal is wetted (M3); the vessel is the hot-leach family CPVC (section 12.1 P2, M5 limit 93 C, the same liquor class that sets the 85 C CPVC wall of LEACH_CSTR_1) and PVDF (P3) carries any leg above the CPVC class. Selection per AQS-STD-002 with the duty section 2 environment (X-QA-11). Alternative: borosilicate glass 3.3 body (the HX-5 coil class) if the flash zone runs above the CPVC 93 C limit at the crystallizer - a higher-rated thermoplastic, glass or a lined part, never bare metal (M5). the crystal slurry leaves as solids to the pot feeders and the mother-liquor line returns to LEACH_CSTR_1 on the issued P2 hot-leach family; no corrosion allowance on the polymer wetted path (AQS-STD-001 shop rule); the commissioning brine assay and salt weigh-in/weigh-out carry the verification (A-M-503). (X-QA-11)

4. Nozzles. Schedule at `nozzles/BRINE_CRYS.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
