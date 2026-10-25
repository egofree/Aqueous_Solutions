# CAST_LINE CAD acceptance note (FOUNDRY-CAST_LINE-10)

Date: 2026-10-25. Task: FOUNDRY-CAST_LINE-10 (AQS-PLAN-006 M3), following the AL_POT pattern (2026-10-21 note).

What: the permanent-mould cast line at `models/mfg/CAST_LINE/` is built headless by
`cast_line.py` from `params.json` alone and passes the A-core acceptance: exact
1500 x 800 x 1500 envelope, all six task-04 schedule connections verified in-model
against the parsed CSV (nozzle bore, rating, height and the registered face mapping
`schedule_face`), one valid manifold solid, STEP assembly and sheet-model exports,
an 8-sheet stamped drawing set under `drawings/` registered as
AQS-MFG-CAST_LINE-<SHEET>, a 15-row BOM regenerated from the model, and a 4-row
fastener record. The duty section 7 line names the manufacturing model via the
regenerated duty sheet.

Machine shape: two mould stations at y 250 and 550 (backing platens, water jackets,
fine-graphite inserts with 110 x 70 x 60 cavities), an under-deck refractory melt
path feeding both cavities from below (bottom fill is the registered layout choice),
a hand-tilted 12 kg-class lined ladle, a 700 mm runout roller table on solid rollers,
a static shear/stop block at the line end, guards, and a mould-change gantry. The
line is manual (0 kW node duty); the mould-jacket cooling water is a utility loop
with no graph edge and no rate claim - it is sized at the task 12 first articles.

Geometry findings fixed on the way in: an end rail 40 mm over the envelope, a
disconnected rear-guard group, an unsupported shear pedestal, glide-rail posts with
edge-only contact to the frame, and roller bodies ending coplanar with the bearer-rail
faces (coincident-face tessellation artifacts). After the fixes the metric-registry
STL and the mm-scale export are both watertight with 0 degenerate edges after vertex
merge and one island (trimesh). Nothing connected was left as a text claim.

Board effect: FOUNDRY-CAST_LINE-10 ticked with `build_log.md` as evidence;
-11 continues partial (per-part dimension chains and the tolerance stack);
-12/-13 stay ticked. Papers and program claims unchanged: no residence time,
no cooling rate, no wear allowance and no load calculation is claimed; the holds
are named in WORK_ORDER.md and build_log.md.
