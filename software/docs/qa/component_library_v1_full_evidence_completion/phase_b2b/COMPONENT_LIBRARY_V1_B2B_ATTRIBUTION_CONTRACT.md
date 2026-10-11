# Component Library V1 B2B - Attribution Contract

## Purpose

This contract defines the minimum provenance that a future UBD product-
admission change must retain if it bundles an exact canonical component from
the four B2B targets. It does not itself admit a component, change production
data, or grant legal clearance.

## Required Attribution Fields

Every bundled component record must retain:

1. UBD component ID and display name.
2. Database name: `NCBI GenBank / INSDC`.
3. Exact `accession.version` and stable NCBI record locator.
4. Original record submitter or record authors and submission year.
5. Linked publication citation, DOI, PMID, or PMCID when applicable.
6. Exact one-based inclusive feature coordinates, strand, and feature type.
7. Source-record SHA-256 and extracted-feature SHA-256 from Phase B2A.
8. Retrieval date and the version of this B2B governance decision.
9. The bounded rights notice below.

No future presentation or export may replace the accession/version with a
family-level label, drop the feature boundary, or imply that a related paper
is the exact sequence authority when it is only research context.

## Required Notice

Use this bounded notice with bundled metadata:

> Sequence provenance: NCBI GenBank / INSDC, accession and version shown
> above. INSDC database policy supports access and redistribution of database
> records. NCBI does not receive submitter rights and cannot grant unrestricted
> third-party permission. This attribution is not a legal clearance,
> freedom-to-operate conclusion, biological performance conclusion, or formal
> product-admission record.

## Target Citations

| Component | Required record attribution | Additional source attribution |
| --- | --- | --- |
| `PCLV1-PRO-UBQ10` | `HQ693235.1`; Hashimoto and Kudla; direct submission, 2010; feature `1..636 (+)` | Cite the GenBank record. A future admission record must also link the completed human review of the `WO2012028646` family. |
| `PCLV1-PRO-E8-2164` | `KJ561284.1`; Hong, Duc, Son, Ngoc, and Ha; direct submission, 2014; feature `1..2164 (+)` | Cite Deikman and Fischer only as E8 research context, not exact accession authority. |
| `PCLV1-TER-HSP18-2-250` | `PP558908.1`; Sagawa et al.; direct submission, 2024; feature `852..1101 (+)` | Cite Sagawa et al. 2024 for the Level0_HSPt source context and Nagaya et al. 2010 only as HSP18.2 research context. |
| `PCLV1-CDS-BAR` | `X17220.1`; Bibb direct submission, 1989; feature `31..582 (+)` | Cite White et al. 1990. A future admission record must also link completed human review of relevant exact-accession patent references. |

## Derivatives And Exports

If a future authorized implementation includes a bundled sequence in a saved
design record, FASTA, GenBank, or review package, the same accession/version
and feature attribution must remain available in machine-readable metadata or
an adjacent provenance manifest. This B2B contract does not authorize such an
implementation and does not alter current export semantics.

## Review And Change Control

- The attribution contract is bound to the exact Phase B2A source and feature
  hashes recorded in `COMPONENT_LIBRARY_V1_B2B_RIGHTS_GOVERNANCE.json`.
- A source-version, coordinate, strand, or digest change requires a new
  technical and rights review.
- `HQ693235.1` and `X17220.1` cannot proceed to product admission on this
  contract alone; their human legal-review items remain open.
- Attribution must not be represented as a biological recommendation,
  experimental validation, or replacement for company/expert review.
