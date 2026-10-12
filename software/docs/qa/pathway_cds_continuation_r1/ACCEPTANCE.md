# V1.0 Pathway CDS continuation R1 — bounded acceptance

Task: `V1_0_PATHWAY_STEP2_CONTINUATION_R1` · 2026-10-12.
Baseline: `6c39a8a5666e0cfee1a65cea62a507602e25d76d`.

## Reproduced defect

The original audit A02 was independently reproduced on the unmodified baseline:
both CDS Apply operations wrote their sequences to the selected stable TUs, and
Next reached Step 3. However, Step 3 selected the library route and displayed
unconfigured CDS instead of the saved user sequences. Mapping stores
`user_provided` and other manual CDS source types; the editor only recognized
`paste`/`upload`. A second inconsistency was reproduced: with only TU1 applied
and TU2 empty, Next was enabled, but clicking it stayed in Step 2 because the
navigation predicate required all TU CDS.

## Minimal change

- Recognize manual Pathway CDS sources when restoring Step 3 inputs, and keep
  the existing source type/accession for unchanged DNA during confirmation.
- Use the same mapping/TU completion and review predicate for the Step 2 Next
  button and navigation. Mapping completion requires actual Apply for every
  step; existing missing/invalid/shared/dangling/hash-mismatch blockers remain.
- Restore Step 2 TU selectors from stable mapping records on project mount.
- Revalidate matching original CDS text on rerender so invalid input findings
  cannot disappear through sequence normalization.

The strict CDS analyzer, Apply implementation, generic planning signature,
component admission and published rights/evidence rules were not changed.

## Browser and sequence evidence

Windows, isolated CPython 3.12 environment using the runtime lock, isolated DB,
draft/backup/PyDNA directories, localhost port 8799. The primary reviewer and a
separate browser reviewer each used real browser actions. The latter created a
new project independently; it did not reuse the primary project's saved state.

| Input | Exact CDS feature | bp | SHA-256 of DNA |
|---|---|---:|---|
| CYP76AD1 / HQ656023.1 | 259..1752 (+) | 1494 | 79c7ffaaa7ad20dbfc1903619d14208160be9b0af48851a85b89a19eeb43a27c |
| DODA1 / HQ656027.1 | 60..887 (+) | 828 | cbdd9b4070de50ff2a863c361a1e6791adde5707b55abe8227dcb47b607654f7 |

Independent biological review re-extracted GenBank CDS features, checked
translation qualifiers and compared the official NCBI records. Step records,
saved TU records and actual Step 3 input values matched these sequences and
hashes. Save, browser refresh followed by Project Center Open, and server cold
restart followed by Open preserved stable mapping IDs, CDS hashes and sources.
Switching between Pathway, ALB and generic Multi-TU projects showed no CDS
cross-contamination in the tested cases.

Missing CDS, valid-but-unapplied CDS, partial Apply, illegal N/multiple FASTA,
and duplicate TU mapping stayed blocked in real browsers. Service tests also
covered dangling TU, applied-hash mismatch and an additional empty TU.

The primary browser additionally configured user-recorded AF485783.1 promoter
4974..5808 and NOS terminator 7727..7979 with explicit absence of a separate
5′ region, confirmed both TUs and reached Step 4. The generated expression DNA
was 4498 bp, SHA-256
`ec601d2f8c6da326db9d3b1a6762b1811ea114c85294c177b08f5a3eaf11294f`;
generated original inputs retained both CDS/TU/source relationships.

## Regression and independent decision

- Five new targeted tests pass, including repeated invalid-input normalization.
- ALB saved Step 6 result remains 11876 bp, SHA-256
  `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c`;
  browser backup matches its pre-existing sequence/export hashes and cassette.
- Generic Multi-TU restored Step 4, restored both Step 3 CDS, regenerated and
  saved Step 4: 4783 bp, SHA-256
  `3a2303b096c827ff03bbc0dd6d163436e8166380b6c9d29be552d9d5bb98215e`.
  DNA, stable TU order, CDS and sources match its prior saved result.
- With a real ALB report fixture, baseline tests yield 16 passed / 5 failed;
  candidate tests yield 21 passed / the same 5 failed. These five pre-existing
  report-text expectations are recorded test debt, not an all-green suite.
- Separate flow/state, biology/CDS-TU and browser reviewers each gave scoped GO
  for this continuation fix. One candidate repair was used; no second feature
  or unrelated P1 was attempted.

## Boundaries

This is a two-CDS manual handoff example, not a complete three-enzyme betalain
pathway or experimental expression claim. Step 4 was reached; no backbone was
selected and Step 5/6 Pathway completion was not tested. Step 4 remains blocked
until its real backbone/operation requirements are met.

The optional review count of six is expected: each step lacks substrate/product,
EC number and enzyme source organism. These are nonblocking review records,
and the page currently shows their count. Default TU2 display text refers to a
plant selection marker; DODA1 is only the CDS mapped to that stable TU in this
test and is not asserted to be a selection marker.

Changing only a source description after Apply does not automatically update
the TU source in the baseline or this candidate. Re-Apply is required. This
existing metadata-edit boundary was not expanded into a separate repair.
Refresh starts a new session; saved projects are recovered through Project
Center Open. Source provenance stays user-recorded and is not upgraded to
official/direct-use status.

Formal frozen releases, PAPER01, V1.1, historical tags, map export and other
component admission work are outside this change.
