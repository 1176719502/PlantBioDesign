# PlantBioDesign Software Overview

PlantBioDesign V1.0 · Official public documentation · 2026-10-10

## Research context and development purpose

Plant expression construct design involves a host, coding sequence, regulatory components, vector backbone, and output files. When these materials are scattered, their provenance, versions, and design records are difficult to reconcile. PlantBioDesign brings them into one computational design and human-review workflow for researchers in plant biology, biology, and synthetic biology.

## Main functions and six-step workflow

The single-gene workflow follows project definition → target gene → plant expression cassette → vector backbone → complete construct → results and export. It provides input checks, expression cassette assembly, insertion into a backbone according to fixed rules, plasmid maps, save and reopen, and entry points for FASTA/GenBank sequence exports and JSON backups.

## Component provenance and traceability

Design records should retain accession and version, source species, extraction coordinates, strand, original files, and nucleotide SHA-256. Component Library eligibility and user sequence routes must be distinguished: accepted input does not establish completed provenance review. The current provenance summary has gaps, so original source records must be retained separately.

## Actual computational case

The human ALB single-gene case with rice as the intended host uses `NM_000477.7` CDS (1830 bp), CaMV 35S (835 bp) and NOS (253 bp) from `AF485783.1`, forming a 2918 bp expression cassette. Forward insertion at the fixed 27|28 boundary of the 8958 bp circular `AF234296.1` backbone produces an 11876 bp plasmid. Existing records support input identity and sequence-level reconstruction checks; they do not establish expression in rice, yield, or biological function. See the accompanying guide for detailed provenance, hashes, and commands.

This ALB single-gene example is an independent operational demonstration, not a result from the paper cases MT-01 or MT-02. Those cases concern a 4079 bp source region with two transcription units and a 6609 bp source region with three transcription units, respectively; neither establishes independent reconstruction of a complete plasmid.

## Current scope and future priorities

The frozen submission source-code commit underlying the paper analysis is `8ead74c060c32e653e746030e557398637a2c2fc`. The GitHub distribution snapshot used for the ALB operations in this manual is `176232bdd20eb0ae987b52ad8b84df1f71b35a39`; its `SOFTWARE_SNAPSHOT.md` identifies the submission source above as its origin. These commits identify the paper source and the GitHub distribution separately; this statement does not establish file-by-file equivalence between them. The ALB operation records do not extend the validation scope of the paper cases MT-01/MT-02. Operation evidence is limited to the single-gene case above. Historical records support generation, viewing after save and reopen, and sequence downloads. Missing dependencies block formal report downloads; backbone catalog selection fails; provenance summaries and editing restoration after reopening remain limited. Other visible modules have not undergone complete acceptance in this manual.

Future work should prioritize report delivery, provenance summaries, backbone resources, and restoration for editing, supported by independent evidence. Report and editing fix candidates have not been formally adopted. V1.1 development remains separate from the frozen version. This documentation promises neither unverified functions nor a release date.

[Project repository](https://github.com/1176719502/PlantBioDesign) · [User Manual](PlantBioDesign_User_Manual.md) · [Case Input Reproducibility Guide](CASE_INPUT_REPRODUCIBILITY.md)

