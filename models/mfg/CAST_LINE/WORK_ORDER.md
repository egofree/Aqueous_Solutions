# Work order CAST_LINE

Authority: AQS-DUTY-072 (X-MFG-30 pattern). In-house fabrication; no bought line machine.

1. Fabricate and level the bench weldment per bom.csv item 1 (feet anchored with the M12 anchors, fasteners.csv item 2); set the envelope 1500 x 800 x 1500 mm with the +X discharge head and the -Y guard plane as registered in params.json.
2. Fit the under-deck melt path (refractory trough, distribution header, two graphite bottom-fill risers, drain well) and set the mould seats with their fine-graphite inserts per bom.csv items 3-6; insert cavity 110 x 70 x 60 (about 3.7 kg Cu class pour).
3. Fit the deck, runout roller table (5 solid rollers on press-fitted pillow blocks) and scrap chute per bom.csv items 2 and 9; end rail flush at x 1500 (+X face pick, N3/N4).
4. Mount the pour station: tilt post, arm and saddle on the deck, the 12 kg-class lined ladle under its trunnion lugs (bolted, fasteners.csv item 1); hand tilt, no actuator.
5. Mount the static shear/stop block and the rear hot-zone guard with its fixed knife cover; fit the mesh at fabrication (AQS-BLD-012 class).
6. Mount the mould-change gantry and hang the safe working load 250 kg manual chain hoist (purchase item named with the rating, A-MACH).
7. Terminate the scheduled connections per docs-authority/nozzles/CAST_LINE.csv: N1 DN15 Class 150 melt inlet (-X, z 160), N2 solids chute (-Y), N3/N4 discharge lane guides (+X), N5 DN15 drain (bottom, z 50), N6 DN15 vent tap (top, z 800); gasket faces per AQS-PIP-003 class practice (AQS-STD-002 section 14).
8. Test: dry run, then trial feed pass; record dimensions on the traveller.
9. Inspect against models/mfg/CAST_LINE/export/cast_line.step.

## Holds (named, per AQS-PLAN-006 A-core 11)

- Unit task 12 (first articles + real BOM at order): mould-jacket cooling-water utility loop sizing and commissioning (a utility loop with no graph edge; no rate is claimed in the model), mould insert change-out traveller, shear campaign, ladle relining campaign.
- X-MAT-21 / A-M-318 pot-cell verification: mould-cycle wear allowances and refractory campaign data stay study proportions until that campaign reports.
- Mould-change gantry: safe working load 250 kg chain hoist is a fit choice against the modeled seat mass; no load calculation is claimed.
