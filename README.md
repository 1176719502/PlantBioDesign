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

Current `main` includes V1.0 report maintenance (R1–R3): the runtime hash lock includes ReportLab 4.2.2, Markdown/PDF downloads handle failures independently, and role-only saved input sources are displayed with current attribution unconfirmed. Component-bound provenance remains visible; source descriptions and accessions are not treated as literature citations. These changes do not establish whole-software V1.0 acceptance. To use the maintenance code, download [current main](https://github.com/1176719502/PlantBioDesign/archive/refs/heads/main.zip) and install its own lock in a separate environment using the guide below. The historical fixed ZIP and frozen tags retain their original bytes and limitations.

Use the [fixed snapshot ZIP](https://github.com/1176719502/PlantBioDesign/archive/176232bdd20eb0ae987b52ad8b84df1f71b35a39.zip), extract it, and open PowerShell in the folder containing `software/`. Follow [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the locked installation and isolated runtime commands. The archive download and Windows installation have not been replayed in this documentation revision.

## Current ALB single-gene acceptance (2026-10-11)

The tested maintenance `main` at `126ebc4303f579e730d41821ec0d6bce6e1dd400` has a documented `ALB_SINGLE_GENE_E2E_GO` result for one fixed ALB/Rice single-gene case. A real browser completed Steps 1–6, producing a 2918 bp expression cassette, an 8958 bp pCAMBIA backbone with the fixed 27|28 insertion, and a 11876 bp complete plasmid. FASTA and GenBank sequences matched; formal save, two complete cold restarts, continued editing, and actual Markdown and four-page PDF downloads were verified. The external acceptance report supplied for this review records these results; this documentation update does not repeat the workflow test.

This result covers the stated ALB single-gene workflow only. It does not establish acceptance for all hosts, Multi-TU, Pathway, the whole software, or wet-lab expression. Historical read-only checking used an explicitly marked result-only test copy; it does not verify a real historical revision chain. Promoter/terminator inputs remain user-provided with attribution pending confirmation; role-only saved inputs do not automatically establish current source attribution or formal Registry admission. The deterministic canonical map artifact was unavailable and is outside the passed deliverables. Third-party rights remain subject to the boundaries below. No internal logs, private project data, unreviewed sequences, or test copies are added to this repository. The historical fixed snapshot's defects and verdicts remain unchanged.

## Known limitations of the historical fixed snapshot

- The historical fixed snapshot's `software/requirements-runtime.lock` does not contain ReportLab. Existing frozen-version operation evidence records both formal report downloads being blocked by its missing dependency. Current main's report maintenance does not change that fixed snapshot.
- The historical fixed snapshot's pCAMBIA catalog contract references `software/case_inputs/rice_hsa/raw/AF234296.1.gb`, which is absent from that snapshot. Another AF234296 record exists elsewhere, but the catalog loader reads the contract's exact path. Do not treat a visible catalog eligibility label as proof that selection succeeds.
- Historical user-manual evidence records incomplete source summaries and limited editing after project reopen. Viewing a saved result and downloading a sequence do not establish complete edit recovery; the current-main ALB acceptance above does not retroactively change that evidence.
- Complete MT-01 and MT-02 derived FASTA/GenBank payloads are omitted under the frozen redistribution contracts. Accession versions, extraction coordinates and hashes remain available for independent region reconstruction. The historical **BLOCKED as a complete reviewer sequence package** verdict applies to that requested payload scope; it is not a new whole-software startup verdict.

V1.1 and unadopted repair candidates are not installed by these instructions; current-main maintenance and the bounded ALB acceptance are described above. The Chinese manual is published separately below; its publication does not change the frozen software or its acceptance status.

## 中文使用手册

- [PlantBioDesign V1.0 中文使用手册（14 章，15 张真实截图）](docs/zh/PlantBioDesign_中文使用手册.md)
- [案例输入复现说明](docs/zh/CASE_INPUT_REPRODUCIBILITY.md)
- [手册许可与发布范围](docs/zh/LICENSE_MANUAL.md)
- [本次文档与图片 SHA-256 清单](docs/zh/MANIFEST_SHA256.txt)

手册对应固定提交 `176232bdd20eb0ae987b52ad8b84df1f71b35a39`，保留已验证、未验证和未采纳候选的区别。本次只公开文档及截图，不修改软件代码，不追加完整序列或内部审查日志。现有完整序列的来源和分发权利仍属独立后续检查事项，本次手册发布不表示整个仓库已无风险。文档及截图不包含在上述历史固定 ZIP 或历史完整性清单中。

## Repository contents

- [software/](software/): V1.0 runtime files and dependency lists, with report maintenance on current main.
- [cases/](cases/): MT-01/MT-02 reconstruction contracts and non-inclusion notices.
- [component_library/](component_library/): frozen 171-record component metadata.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md): installation, region reconstruction and sequence comparison.
- [SOFTWARE_SNAPSHOT.md](SOFTWARE_SNAPSHOT.md): software-source identity.
- [MANIFEST_SHA256.txt](MANIFEST_SHA256.txt) and [PACKAGE_FILE_LIST.txt](PACKAGE_FILE_LIST.txt): byte-level integrity inventories.
- [SUBMISSION_PACKAGE_REVIEW.md](SUBMISSION_PACKAGE_REVIEW.md): historical package review; its original verdicts are retained.

## License and documentation scope

Software licensing is recorded in [software/LICENSE](software/LICENSE), with dependency notices in [software/THIRD_PARTY_NOTICES.md](software/THIRD_PARTY_NOTICES.md). No license text is changed here. This documentation revision records the bounded current-main ALB browser acceptance above; it adds no software code, wet-lab result, or historical revision-chain claim.

## Public-content provenance and license boundaries (2026-10-09)

### Frozen package and current documentation

The paper-frozen software and the V1.1 development checkout are separate versions. This repository does not distribute the current V1.1 development work or imply that its fixes have been adopted. The fixed ZIP above identifies commit `176232bdd20eb0ae987b52ad8b84df1f71b35a39`; the public-content audit used the later documentation HEAD `f79be74ca7318ecd81f094007181de73dbd0fc67`. Current `main` documentation supplements the historical package, but does not enter an older commit's fixed ZIP or change its source commit, tag, or bytes.

`MANIFEST_SHA256.txt and PACKAGE_FILE_LIST.txt` describe the historical package, not a regenerated inventory of current `main`. The current root README has later documentation bytes. Added provenance notes are outside the historical inventories; in PAPER01, `source_snapshot/tools/MUSCLE_PROVENANCE.md` is a later documentation addition, not a file copied from the frozen software source. Verify historical package hashes against the fixed package, and read these later notices separately. The historical inventories and source-tree proofs are retained without rewriting their hashes.

### MIT scope and third-party software

The [MIT license](software/LICENSE) applies only to original software material that the project has the right to license. It does not automatically apply to database-derived sequences or records, fonts, third-party programs, or other third-party materials. Retain their own source, copyright, and license notices; this supplement does not assert that every project contribution's ownership chain has been independently proven.

The [third-party inventory](software/THIRD_PARTY_NOTICES.md) records a historical Windows base-runtime lock and wheel review, rather than the actual bundled contents of this source repository or a complete future runtime package. Biopython 1.87 and Streamlit 1.55.0 are declared dependencies; their program bodies, wheels, and Python site-packages are not bundled in the audited repositories or PAPER01 release ZIP. Imports and requirements entries do not establish redistribution of those programs.

- [Biopython 1.87 license](https://raw.githubusercontent.com/biopython/biopython/biopython-187/LICENSE.rst): Biopython License Agreement; some individual files offer BSD-3-Clause as an alternative. Do not describe the entire package as BSD-only. Actual redistribution requires retention of applicable copyrights and supporting license/copyright statements; contributor names cannot be used for promotion without permission.
- [Streamlit 1.55.0 license](https://raw.githubusercontent.com/streamlit/streamlit/1.55.0/LICENSE): Apache-2.0. Actual redistribution requires its license, applicable notices, and modification notices where relevant. The audited tag's root NOTICE URL returned 404; this is not evidence that every nested component lacks notice requirements.
- Noto Sans SC retains its own [OFL 1.1 text](software/assets/fonts/noto_sans_sc/OFL.txt) and [provenance](software/assets/fonts/noto_sans_sc/PROVENANCE.md), rather than project MIT.

Any future bundle containing dependency program bodies must be checked against its actual direct, transitive, and nested component inventory. The historical notice inventory is not a completed license clearance for such a bundle.

### Sequence sources, counting scope and reuse

The 2026-10-09 audit counted 61 sequence-file paths and 122 candidate rows in this repository. Across the two repositories, 130 sequence-file paths deduplicated to **49 sequence contents**; the two copies of the candidate inventory deduplicated to **122 candidate source identities and 122 candidate sequences**. The 49 figure concerns the file-sequence set, not the combined file-and-candidate set (170 sequence contents). Deduplication used sequence-string hashes; reverse complements, coordinate fragments, and related variants were not forced into one biological identity.

The audit verified 82 real accession records online (81 INSDC/ENA and one NCBI RefSeq), checked all 122 candidates against their declared hashes and source regions, and checked all 34 Registry entries, referencing 20 unique source files. Preserve the versioned accession, original submitter/reference attribution, extraction coordinates, strand or joined-region transformations, and hashes in the [source manifest](software/data/plant_component_registry_v1/source_manifest.csv), [Registry](software/data/plant_component_registry_v1/registry.batch1.json), and [candidate inventory](software/data/plant_component_registry_v1/intake_20260827/candidate_inventory.csv). Other source records include [pBI121 provenance](software/data/real_assets/pbi121/provenance/source_manifest.json) and [betalain CDS provenance](software/data/real_cases/betalain_three_enzyme/provenance/source_manifest.json). A Direct Submission or patent reference is a source record, not a reason to invent a paper or DOI. Synthetic test inputs are outside the real-accession claim.

[INSDC policy](https://www.insdc.org/policy/) provides unrestricted database access and redistribution and calls for citation of original submissions. The [NCBI molecular-database policy](https://www.ncbi.nlm.nih.gov/home/about/policies/) states that NCBI imposes no use or distribution restrictions, while warning that third-party patent, copyright, and other rights may remain. These policies support the audited sequence-data redistribution; they do not relicense the records under project MIT or clear every third-party right. Reading source data, publicly redistributing data, commercial exploitation, biological material transfer, and implementing a patented invention are distinct matters.

| Verified accession | Patent provenance present in the database record |
| --- | --- |
| [AF354045.1](https://www.ebi.ac.uk/ena/browser/view/AF354045.1) | PCT/US98/19217 |
| [AF354046.1](https://www.ebi.ac.uk/ena/browser/view/AF354046.1) | PCT/US98/19217 |
| [AF354047.1](https://www.ebi.ac.uk/ena/browser/view/AF354047.1) | PCT/US98/19217 |
| [MP385296.1](https://www.ebi.ac.uk/ena/browser/view/MP385296.1) | WO2019211296-A1, sequence 60 |

These references are confirmed source facts, not a finding that redistribution is prohibited or that a patent is enforceable. Patent claims, jurisdiction, grant status, and current legal status have not been assessed. Public sequence access does not establish freedom to operate or an unrestricted commercial implementation license. The audit does not constitute clearance of every embedded dataset or the full project history.

## Official public documentation (2026-10-10)

The official documentation preserves the frozen V1.0 limitations, historical NO_GO/NOT_PROVEN findings, and the existing distribution scope. It does not claim software acceptance or wet-lab validation.

### 中文

- [中文 R4 手册](docs/zh/r4/PlantBioDesign_中文使用手册.md) · [PDF](docs/zh/r4/PlantBioDesign_中文使用手册.pdf)
- [中文案例复现说明](docs/zh/r4/CASE_INPUT_REPRODUCIBILITY.md) · [PDF](docs/zh/r4/PlantBioDesign_案例复现说明.pdf)
- [中文软件简介](docs/zh/r4/PlantBioDesign_软件简介.md) · [PDF](docs/zh/r4/PlantBioDesign_软件简介.pdf)

### English

- [English User Manual](docs/en/PlantBioDesign_User_Manual.md) · [PDF](docs/en/PlantBioDesign_User_Manual.pdf)
- [English Case Input Reproducibility Guide](docs/en/CASE_INPUT_REPRODUCIBILITY.md) · [PDF](docs/en/CASE_INPUT_REPRODUCIBILITY.pdf)
- [English Software Overview](docs/en/PlantBioDesign_Software_Overview.md) · [PDF](docs/en/PlantBioDesign_Software_Overview.pdf)
