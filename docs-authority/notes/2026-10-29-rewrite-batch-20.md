# Rewrite batch 20

Date: 2026-10-29

This batch brings four pages to the documentation style guide (AQS-DOC-002) and fixes one script.

- `docs-authority/MVS_PITCH_PASS.md` (AQS-PLACE-SEED-001) is now revision B. It gains identity lines, a record of revisions and a purpose section stating that it is a superseded placement record; the current origins are in `flow_graph/placement_seed.json` and AQS-SITE-013. Arrows are written as sentences.
- `docs-authority/MVS_STUDY_CLOSE.md` (AQS-STUDY-CLOSE-001) is now revision B, treated the same way. The current loads are on the graph nodes through the stub activation; the lithography stub has been replaced by the three lithography units.
- `docs-authority/MATERIALS_SEC3.md` (AQS-STD-006) is now revision B. It gains a purpose section, loses its working phrasing, and its headings no longer carry a unit count. No selection changed.
- `docs-authority/STL_MANIFEST.md` (AQS-STL-001) is now revision B. The typed list of expected meshes is replaced by the mapping in `models/freecad/import_mfg.py`.
- `models/freecad/import_mfg.py` read its meshes from `models/detail/stl/`, which nothing writes, so it skipped every mesh. It now reads `models/export/detail/`, where `build_stls.sh` publishes, with `models/openscad/detail/stl/` as a fallback.
