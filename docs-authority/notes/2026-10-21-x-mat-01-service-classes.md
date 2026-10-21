# X-MAT-01 — Service-class selection guide (AQS-STD-002 Rev L §12)

Date: 2026-10-21. Items: X-MAT-01 (closed). Sibling status noted below.

## What was done

1. **Guide.** `MATERIALS_STD.md` Rev L adds §12 "Service-class selection guide across the
   assay envelope": the bounding chemistry (AQS-ASSAY-001 Rev C phase classes; ASSAY.md
   metal loading Fe 20 / Cu 8 / Ni 3 / Zn 4 / Al 6 / other 9 g/L), the census table for the
   22 classed families with per-family material and source columns ([S1]–[S12], S21/S22,
   PERRY9_MAT — no new sources), the four unclassed ("—") families with their issued
   per-duty materials, and §12.3 dispositions for every §2 ambiguous-list item.
2. **Line-list rules.** `_line_list.py` `cls()` rewritten so every wetted edge lands in a
   named family (AQS-PIP-004 Rev B):
   - Retired the `aqueous process, default thermoplastic` catchall; fallback is the
     `aqueous process liquor (AQS-ASSAY-001 envelope)` P1 family.
   - New rules: melt pours → "—" launder (gas-phase exempt, so MO_CELL anode gas stays a
     gas line); hydrocarbon/fuel/wax cuts → M2 carbon steel (dry, per the issued duties);
     wet methanol → M1 316L (gas-phase exempt, so the H₂-to-MeOH and CO₂-return gas rows
     keep the dry-gas class); silica slurry → P4; S43 geothermal glycol → P5; S36 dopant →
     "—" pending PIP-003 Rev B; MgCl₂/CaCl₂ pot-brine concentrates → "—" unit task 09;
     98 wt% H₂SO₄ make-up → M2 (PERRY9_MAT passivation); fluoro-train dry legs → "—"
     (Hastelloy C-276 / Ni / Inconel 600 per duty sheets). Wet-HF legs (IA-HF-PROD,
     HF_GEN_VDF/TFE, IA-HF-SRC, F_RECOVER_TO_HF_GEN) keep P3 via the `HF`-in-sid rule — the
     actual carries say "aqueous HF": wet-HF family, PVDF [S1].
   - Distribution after reclass (323 piped rows): M1 79, P1 67, P2 46, P3 45, M2 32,
     "—" 20, P5 15, F1 10, P4 9.
3. **Census gate.** New `docs-authority/_service_census.py` (AQS-STD-002 §12 evidence):
   exec-parses the line-list rows, groups all piped wetted rows by (class, service),
   checks each row against its family's class mandate and exits 1 on any retired-catchall
   row or class/family contradiction; prints the doc-ready §12 census table. Green:
   **323 piped wetted rows, 22 families, 0 default catchalls.**
4. **§8 checker alignment.** `_material_temps.py` unit map is now the issued material
   basis (CPVC: LEACH_CSTR_1, FLOAT_SINK, EW_1, ACID_POLISH_SCRUB, NOX_SCRUB; PVDF: HX8,
   WS_NITRIC, WS_PEROX, HNO3, WS_HF_ED). IA-BMED-03/04 inlet temperatures are *derived*
   in the row loop from the booked X-RSZ-04 trim duties and the driver heat capacities
   (cp_hcl20 3.0 / cp_naoh20 3.6 kJ/(kg·K), PERRY9): 0.780 kW on 450.164 kg/d → ΔT 49.9 K
   → 35.1 °C; 1.027 kW on 500.131 kg/d → ΔT 49.3 K → 35.7 °C. Output: **73 edges, 0
   exceed, 33 rows on the registered 40 °C ambient assumption (A-M-269)**. No `--write`
   run — the graph is untouched.
5. **§10 refresh.** The trim table in `MATERIALS_STD.md` §10 still carried the pre-resize
   basis (108.2/118.7 kg/d, 188/247 W) while its own bullet cited the X-RSZ-04 booked
   duties. Refreshed to: 450.164 kg/d / 0.780 kW / 35.1 °C and 500.131 kg/d / 1.027 kW /
   35.7 °C, cp taken from the drivers with PERRY9 naming.
6. **Board.** `_task_plan_gen.py`: X-MAT-01 in DONE_X, EVIDENCE_PASS →
   `docs-authority/MATERIALS_STD.md`, dated closure comment. TASK_PLAN.md regenerated;
   X-MAT-01 line 577 ticks, X-MAT tally 21/18.

## Explicitly left open

- MG_POT / CA_POT / F_RECOVER / POLY_STOCK per-unit wetted-material selection (duty §3:
  "Selection pending, unit task 09") — these are the §12.2 pot-brine consumers; they
  close with X-MAT-06 / unit task 09, not here.
- PIP-003 Rev B class sheets for the "—" families (fluoro train, dopant, pot brines).
- WS_DOPE / WS_SLURRY gasket detail (X-MAT-03).
- Hardware-gated Wave-5 items unchanged (X-MAT-21, X-INV-02B/03/04, X-MFG-41, X-FIR-01,
  A-M-169 compressor first article, A-M-176 RO/EDI bench).

## Verification

- `python3 docs-authority/_service_census.py` → green (323 / 22 / 0).
- `python3 docs-authority/_material_temps.py` → 73 edges, 0 exceed, 33 ambient rows.
- `_nozzle_sched.py` rerun → zero churn in `docs-authority/nozzles/`.
- Full gates (pytest 43, `flow_graph.param.regen --check`, authority contract) run in the
  closure commit; see TASK_PLAN.md EVIDENCE_PASS.
