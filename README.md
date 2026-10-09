# Plant BioDesign: early PAPER-01 distribution snapshot

Plant BioDesign is a plant expression-vector design and review workbench. This public repository contains an early paper-submission distribution snapshot. It is not the current V1.1 development checkout. Computational results do not establish experimental expression, biological performance, or wet-lab readiness.

## Version identity and package choice

| Identity | Commit |
| --- | --- |
| Original frozen software source | `8ead74c060c32e653e746030e557398637a2c2fc` |
| This repository snapshot reviewed on 2026-10-09 | `176232bdd20eb0ae987b52ad8b84df1f71b35a39` |
| Separately adopted R2.1 submission-package source | `42bfb04c215fcfe76334f4e5a40f9cde60ea2133` |

The source tree is `53f8d4446f719678db363e4e373ddc88123fd80c`, with source tag `paper-01-submission-snapshot-20260930`. Distribution commits and original source commits identify different repository histories. The packaged `software/` source was copied from the frozen software; see [SOFTWARE_SNAPSHOT.md](SOFTWARE_SNAPSHOT.md).

The separate [PlantBioDesign-PAPER01 repository](https://github.com/1176719502/PlantBioDesign-PAPER01) contains a publication bundle with its software under `source_snapshot/`. The two repository layouts and completeness records differ. Use the installation guide matching the repository you downloaded.

## Download and run

Use the [fixed snapshot ZIP](https://github.com/1176719502/PlantBioDesign/archive/176232bdd20eb0ae987b52ad8b84df1f71b35a39.zip), extract it, and open PowerShell in the folder containing `software/`. Follow [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the locked installation and isolated runtime commands. The archive download and Windows installation have not been replayed in this documentation revision.

## Known limitations of this snapshot

- The locked `software/requirements-runtime.lock` does not contain ReportLab. Existing frozen-version operation evidence records both formal report downloads being blocked by its missing dependency; this documentation change does not fix that behavior.
- The pCAMBIA catalog contract references `software/case_inputs/rice_hsa/raw/AF234296.1.gb`, which is absent from this repository snapshot. Another AF234296 record exists elsewhere, but the catalog loader reads the contract's exact path. Do not treat a visible catalog eligibility label as proof that selection succeeds.
- Existing user-manual evidence records incomplete source summaries and limited editing after project reopen. Viewing a saved result and downloading a sequence do not establish complete edit recovery.
- Complete MT-01 and MT-02 derived FASTA/GenBank payloads are omitted under the frozen redistribution contracts. Accession versions, extraction coordinates and hashes remain available for independent region reconstruction. The historical **BLOCKED as a complete reviewer sequence package** verdict applies to that requested payload scope; it is not a new whole-software startup verdict.

V1.1 and unadopted report/editing repair candidates are not installed by these instructions. The Chinese manual remains a separately reviewed candidate and is not bundled here by this documentation patch.

## Repository contents

- [software/](software/): frozen runtime files and dependency lists.
- [cases/](cases/): MT-01/MT-02 reconstruction contracts and non-inclusion notices.
- [component_library/](component_library/): frozen 171-record component metadata.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md): installation, region reconstruction and sequence comparison.
- [SOFTWARE_SNAPSHOT.md](SOFTWARE_SNAPSHOT.md): software-source identity.
- [MANIFEST_SHA256.txt](MANIFEST_SHA256.txt) and [PACKAGE_FILE_LIST.txt](PACKAGE_FILE_LIST.txt): byte-level integrity inventories.
- [SUBMISSION_PACKAGE_REVIEW.md](SUBMISSION_PACKAGE_REVIEW.md): historical package review; its original verdicts are retained.

## License and documentation scope

Software licensing is recorded in [software/LICENSE](software/LICENSE), with dependency notices in [software/THIRD_PARTY_NOTICES.md](software/THIRD_PARTY_NOTICES.md). No license text is changed here. This documentation revision clarifies the public repository layout and known limitations; it adds no new installation, browser acceptance, sequence-validation or biological results.
