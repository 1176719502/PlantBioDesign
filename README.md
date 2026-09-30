# Plant BioDesign PAPER-01 reviewer/reproducibility package

Plant BioDesign (BioDesign Studio) is a plant expression-vector design and review workbench. This directory is a paper-submission snapshot prepared for reviewer and author reproducibility review. It is not a public software release and it does not claim experimental validation, expression success, biological performance, or wet-lab readiness.

## Frozen identity

- Commit: `8ead74c060c32e653e746030e557398637a2c2fc`
- Git tree: `53f8d4446f719678db363e4e373ddc88123fd80c`
- Submission tag: `paper-01-submission-snapshot-20260930`
- Package generation date: 2026-09-30
- Source branch used for verification: `paper/paper-01-submission-package-r1-20260930`

The `software/` directory contains only tracked runtime files copied from the exact frozen commit. No post-freeze commit was merged or copied. The Formal worktree and Formal port 8528 were not used or modified.

## Important package status

This build is **BLOCKED** as a complete reviewer sequence package. The frozen MT-01 and MT-02 redistribution contracts permit accession/version, coordinates, hashes, extraction rules, and feature metadata, but explicitly prohibit bundling the complete extracted region and derived FASTA/GenBank bytes. Therefore the requested canonical FASTA files and GenBank outputs are not included. The package preserves the frozen contracts and documents exact reproduction steps instead of overriding that policy.

## Windows + Python launch

Requirements recorded by the frozen snapshot target Windows x64 and CPython 3.12. Create the environment outside this package so the package remains immutable:

```powershell
py -3.12 -m venv C:\ubd_repro_envs\paper01-r1
C:\ubd_repro_envs\paper01-r1\Scripts\python.exe -m pip install --require-hashes -r .\software\requirements-runtime.lock

$env:BIODESIGN_DB_PATH = "C:\ubd_repro_runtime\paper01-r1\biodesign_unified.db"
$env:BIODESIGN_BACKUP_DIR = "C:\ubd_repro_runtime\paper01-r1\backups"
$env:BIODESIGN_PYDNA_CONFIG_DIR = "C:\ubd_repro_runtime\paper01-r1\pydna\config"
$env:BIODESIGN_PYDNA_DATA_DIR = "C:\ubd_repro_runtime\paper01-r1\pydna\data"
$env:BIODESIGN_PYDNA_LOG_DIR = "C:\ubd_repro_runtime\paper01-r1\pydna\logs"

C:\ubd_repro_envs\paper01-r1\Scripts\python.exe -m streamlit run .\software\app.py --server.address 127.0.0.1 --server.port 8632 --server.headless true --server.fileWatcherType none
```

Open `http://127.0.0.1:8632`. Do not substitute port 8528 for this reviewer check.

## Contents

- `software/`: frozen tracked runtime snapshot and dependency locks.
- `cases/MT-01/` and `cases/MT-02/`: frozen deterministic-region contracts, metadata, checksums, and non-inclusion notices.
- `component_library/`: the five frozen component-library R2 JSON files preserving 171 / 17 / 24 / 95 / 35 classifications and existing admission states.
- `SOFTWARE_SNAPSHOT.md`: exact software provenance.
- `REPRODUCIBILITY.md`: launch, case reconstruction, and sequence/hash comparison procedure.
- `MANIFEST_SHA256.txt` and `PACKAGE_FILE_LIST.txt`: package integrity inventories.
- `SUBMISSION_PACKAGE_REVIEW.md`: commands, results, file inventory, limitations, and final verdict.

