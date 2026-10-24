# Documentation style guide

Document number: AQS-DOC-002  
Former number: AQS-DOC-001 (the separate house-style page DOCUMENTATION_STYLE.md, merged into this guide on 2026-10-24)  
Revision: B  
Date: 2026-10-24

| Rev | Description | Date |
|---|---|---|
| A | Practical notes on warnings, signs and revisions | 2026-09-26 |
| B | Single style guide for the repository, distilled from KSC-DF-107 Rev F and the IET guide; replaces DOCUMENTATION_STYLE.md | 2026-10-24 |

## 1. Purpose and scope

This guide sets how documents in this repository are written. It applies to every published Markdown page, to the text that generators write into documents, to code comments and docstrings that a reader of the design will see, and to commit messages and pull request descriptions.

It is distilled from the two sources in section 2. It is not a copy of either, and it does not claim issuance by NASA or the IET. Where this guide departs from a source, it says so and gives the reason.

## 2. Sources

1. NASA Kennedy Space Center, KSC-DF-107 Revision F, *Technical Documentation Style Guide* (2017-07-08). <https://standards.nasa.gov/sites/default/files/standards/KSC/F/0/ksc-df-107_rev_f_07082017.pdf>
2. The Institution of Engineering and Technology, *A Guide to Technical Report Writing*, as published by the IEEE Industry Applications Society. <https://ias.ieee.org/wp-content/uploads/2023/06/2020-01-16_IET_Technical_Report_Writing_Guidelines.pdf>

Read the sources at those links. Do not commit copies of them to this repository.

## 3. Write for the reader

The reader is the most important person (IET law 1). Assume the reader is an engineer who knows the subject but not this project, and who needs to understand the page in one pass (KSC-DF-107 3.1).

- Before writing, decide who the page is for, what they need to know and what they should do with it (IET section 1).
- Keep the page as short as the reader's need allows (IET law 2).
- Put the answer first. A page opens with its purpose and, where it reaches a result, a summary of that result (IET law 7).
- Organise the page for the person using it, not in the order the work was done (IET law 3).
- Check the page for technical errors, typing errors and inconsistency before committing it (IET law 8).

## 4. Words

- Use short, common words. Write "use", not "utilize"; "help", not "facilitate"; "start", not "commence" (KSC-DF-107 3.1).
- Call one thing by one name throughout a page, and use the names in the plant graph, on the drawings and on the equipment labels (KSC-DF-107 3.2).
- Avoid long strings of nouns. Rewrite "heat store standing loss limit value" as "the limit set by the store's standing loss" (KSC-DF-107 3.8.1).
- Do not write working jargon from the tools, chats or task lists used to produce the design. A reader outside the project cannot know what "landed", "wave 3", "the box" or "the hub" meant. Say what was done and where the result is. The terms that the check rejects are listed in `docs-authority/style_terms.json` (section 16).
- Do not record who asked for a change or how the work was organised. State the decision, its reason and its source. Decisions owned by the project are recorded in `docs-authority/OPEN_QUESTIONS.md`.
- Write in English with consistent spelling within a page.

## 5. Sentences, voice and mood

- One idea per sentence. Prefer short declarative sentences.
- Prefer the active voice when the actor matters: "The generator writes the register." Use the passive voice when the actor is unknown or unimportant (KSC-DF-107 3.3).
- Write instructions in the imperative: "Run the checks before you push."
- Use parallel grammar in lists: every item in a list is a sentence, or every item is a phrase of the same kind (KSC-DF-107 3.11).
- Avoid ambiguous pronouns. If "it" could mean two things, repeat the noun (KSC-DF-107 3.7).

## 6. Shall, should, will and must

These words follow KSC-DF-107 3.4.

Table 6.1. Requirement words

| Word | Use | Example |
|---|---|---|
| shall | A requirement that can be verified | The vent header shall be sized for the bounding relief case. |
| should | A recommendation; a deviation needs a stated reason | The store should be insulated to the thickness in Table 4.1. |
| will | A statement that an event is certain or highly likely | The pipeline will regenerate the page on the next run. |
| must | A dependent relationship, not a requirement | For the check to pass, the file must be committed. |

Do not use "shall" for history or description. Do not state an obligation from a code or standard unless the edition and clause have been checked and are cited.

## 7. Abbreviations

- Spell out a term at its first use in a page and give the abbreviation in parentheses after it: "continuous stirred-tank reactor (CSTR)". Use the abbreviation after that (KSC-DF-107 3.5.2).
- Abbreviate only a term that recurs or is long. Do not give one abbreviation two meanings (KSC-DF-107 3.5.2).
- Avoid introducing an abbreviation in a heading or a table title (KSC-DF-107 3.5.2).
- SI unit symbols next to a value, chemical formulas and the identifiers in section 8 need no expansion.
- Every abbreviation used in a published page is defined in `docs-authority/GLOSSARY.md`. Add a missing one in the same change.
- Form plurals by adding a lowercase s, without an apostrophe: "PLCs" (KSC-DF-107 3.5.4).

## 8. Identifiers

Unit ids (LEACH_CSTR_1), stream ids (S64), sector ids (FOUNDRY), document numbers (AQS-SEC-001), task ids (X-PAR-02) and assumption ids (A-M-329) are names, not abbreviations. Write them exactly as the plant graph and the registers write them, in code format where a page lists many. Name a sector by its id and, at first use in a page, say what it does: "FOUNDRY (metal production)".

Cite a document by its number and give its path where the reader needs to find it. Do not cite a former number, a retired id or a removed path; the citation check rejects them.

## 9. Numbers and units

- Use SI units. Where a code is written in customary units, give the customary value in brackets after the SI value.
- Put a space between a value and its unit symbol: 12 mm, 70 °C, 150 kg/d. In a range, repeat the unit: 70 °C to 85 °C (KSC-DF-107 3.16.2).
- Give a value with the precision its basis supports, and name the basis: a solved value, a cited source or a registered assumption.
- For a count of things, write the numbers one to nine in words in running text (KSC-DF-107 3.16.1).
- Write dates as YYYY-MM-DD. This departs from the "Month day, year" form of KSC-DF-107 3.16.8 because ISO 8601 dates sort correctly and are unambiguous to readers in every country.
- Do not state how many files, units, documents, tests or commits the repository holds, or the current value of a driver, in hand-written text. Those facts go stale on the next change. Point to the register, the generator or the command that reports them. A generated page may state its own counts because it is regenerated with the data.

## 10. Structure of a page

Every page under `docs-authority/` starts with:

1. A title that says what the page covers.
2. The identity lines: `Document number:`, `Revision:` (a letter) and `Date:`. A generated page also says which generator writes it and that it must not be edited by hand.
3. A record of revisions table (Rev, Description, Date) with one row per issued revision. Do not record drafts (KSC-DF-107 5.3).
4. Section 1, purpose and scope: why the page exists, what it controls and what it does not.

Use decimal section numbers (1, 1.1, 1.1.1) and no more than four levels (IET section 2.4). Put supporting detail that only some readers need in an appendix (IET section 2.2).

## 11. Tables and figures

- Introduce each table and figure in the text before it appears, and place it as close to that text as possible (KSC-DF-107 3.17 and 3.18; IET law 6).
- Number tables and figures by section (Table 3.1, Figure 4.2) and give each a short title. The table title goes above the table; the figure title goes below the figure (KSC-DF-107 3.17 j and 3.18 g).
- Use a table only for data with more than one column; otherwise use a list (KSC-DF-107 3.18). Keep one fact per cell. A cell that holds a whole list belongs in its own table.
- Label every axis and column with its quantity and unit.
- Do not rely on colour alone to carry meaning.

## 12. References

- Every reference is correct in all details (IET law 4). Register each published source once in `flow_graph/param/refs.py` and cite it by key. Give the edition year and the clause, table or page.
- Name a standard by its body, number and edition, for example ASME B31.3-2022. Quote no copyrighted standard text beyond a short clause reference.
- Number the references at the end of a page in the order they are first cited.
- Link to external documents. Do not commit copies of them.

## 13. Warnings, cautions and notes

These follow KSC-DF-107 3.20.

- A WARNING gives information that, if ignored, may injure or kill someone.
- A CAUTION gives information that, if ignored, may damage or destroy equipment.
- A NOTE gives information that needs emphasis to prevent a misreading.

Place the callout immediately after the paragraph it belongs to, with the title in bold capitals on its own line and a short complete statement after it. If several apply, give the warning first, then the caution, then the note.

## 14. Signs

The face text of every plate is in `docs-authority/SIGN_SCHEDULE.md`. A safety sign has four lines: signal word, unit name, hazard and instruction. Sign geometry follows ANSI Z535, not this guide.

## 15. Generated documents

Generators write prose too. The text templates in a generator follow this guide in the same way as a hand-written page, and a change to a template is reviewed as a change to every page it writes.

## 16. Automated check

`python3 -m flow_graph.check_doc_style` checks two rules on every published page, and `flow_graph/test_doc_style.py` runs it with the other tests:

1. Every abbreviation written in capitals is defined in `docs-authority/GLOSSARY.md` (section 7). Identifiers from the plant graph, unit folders, tokens containing a digit, code and revision letters are not counted.
2. No page uses a term from the banned list in `docs-authority/style_terms.json` (section 4). Each entry gives the reason and what to write instead.

The check is deliberately light: it cannot judge clarity, and passing it does not make a page follow this guide. Pages not yet brought to the guide are listed as pending in the same data file. They are reported but do not fail the check. When a pending page becomes clean, remove it with `python3 -m flow_graph.check_doc_style --shrink`. Do not add pages to the list; fix the page or the glossary instead.

## 17. Related documents

| Document | Role |
|---|---|
| `CONTRIBUTING.md` | How to contribute, including the checks to run |
| `docs-authority/GLOSSARY.md` | Definitions of terms and abbreviations |
| `docs-authority/DOC_REGISTER.md` (AQS-REG-001) | Document numbers |
| `docs-authority/COMPLIANCE_MATRIX.md` (AQS-COMPL-001) | Codes and standards applied to the design |
