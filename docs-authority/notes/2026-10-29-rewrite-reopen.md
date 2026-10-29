# Pages re-opened for the documentation rewrite; glossary corrections

Date: 2026-10-29. Documents: AQS-DOC-003 Rev B, AQS-DOC-002 Rev C, AQS-GLO-001 Rev C.

## Change

- The pages taken off the style-check pending list on 2026-10-25 because they passed the automated check, and the pages closed earlier as "verified compliant" without edits, were reviewed against AQS-DOC-002 section 10. Each page that lacks the identity lines, the record of revisions or the purpose and scope section, or that uses arrows or working phrasing in place of sentences, is back on the pending list. AQS-DOC-003 section 4 gives the defects for each page.
- `flow_graph/test_rewrite_todo.py` fails when AQS-DOC-003 sections 3 and 4 and the pending list in `docs-authority/style_terms.json` disagree, or when a page in the done table is still pending.
- Glossary entries added in bulk on 2026-10-25 were checked against the pages that use each term. Wrong expansions were corrected; for example PA is polyamide, not phosphoric acid; PG is propylene glycol; IED is the EU Industrial Emissions Directive; FFC is the Fray-Farthing-Chen process; LR is long radius; CRC is CRC Press. Entries for terms that no page uses were removed, as were duplicate entries. Words in capitals that are not abbreviations (sign face words and parts of chemical formulas) moved to the `not_abbreviations` list.
