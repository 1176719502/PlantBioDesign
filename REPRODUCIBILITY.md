# Reproducibility guide

Current `main` carries V1.0 R1–R3 report maintenance. Its hash lock includes ReportLab 4.2.2; PDF dependency/render failures preserve a successful Markdown download. Saved role-only input sources remain visible with current attribution unconfirmed; component-bound provenance is displayed separately from literature citations. For this maintenance version, apply the commands below to the current main source folder in a separate runtime directory (for example, replace `early-package` with `v1-0-report-maintenance`). Do not mix its lock/environment with a historical fixed snapshot. The fixed ZIP, frozen tags, and historical limitations below are unchanged; this is a report-scoped maintenance check, not whole-software acceptance.

## 1. Start the frozen distribution snapshot

Run these commands in PowerShell from the repository root after extracting the fixed repository snapshot. Use Windows x64 and 64-bit CPython 3.12. Keep the PowerShell window open while the app runs.

Install the locked environment:

```powershell
$ErrorActionPreference = 'Stop'
$reviewSoftware = Join-Path (Get-Location).Path 'software'
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\early-package'
$reviewEnv = Join-Path $reviewRoot 'env'
$reviewPython = Join-Path $reviewEnv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath (Join-Path $reviewSoftware 'app.py'))) {
    throw 'Open PowerShell in the extracted repository root first.'
}
py -3.12 -c "import platform, struct, sys; sys.exit(0 if platform.python_implementation() == 'CPython' and platform.machine().lower() in ('amd64', 'x86_64') and struct.calcsize('P') == 8 else 1)"
if ($LASTEXITCODE -ne 0) { throw '64-bit CPython 3.12 for Windows x64 is required.' }
New-Item -ItemType Directory -Path $reviewRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $reviewEnv)) {
    py -3.12 -m venv $reviewEnv
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed.' }
}
if (-not (Test-Path -LiteralPath $reviewPython)) { throw 'The environment interpreter is missing.' }
& $reviewPython -m pip install --only-binary=:all: --require-hashes -r (Join-Path $reviewSoftware 'requirements-runtime.lock')
if ($LASTEXITCODE -ne 0) { throw 'Locked installation failed. Keep the error log.' }
& $reviewPython -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
```

Start or restart using the same source folder and runtime directory:

```powershell
$ErrorActionPreference = 'Stop'
$reviewSoftware = Join-Path (Get-Location).Path 'software'
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\early-package'
$reviewPython = Join-Path $reviewRoot 'env\Scripts\python.exe'
$reviewRuntime = Join-Path $reviewRoot 'runtime'
$reviewPort = 8632
if (-not (Test-Path -LiteralPath $reviewPython)) { throw 'Install the environment first.' }
if (-not (Test-Path -LiteralPath (Join-Path $reviewSoftware 'app.py'))) { throw 'Return to the extracted repository root.' }
if (Get-NetTCPConnection -LocalPort $reviewPort -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8632 is occupied. Check the existing instance before starting another.'
}
New-Item -ItemType Directory -Path $reviewRuntime -Force | Out-Null
$env:BIODESIGN_DB_PATH = Join-Path $reviewRuntime 'biodesign_unified.db'
$env:BIODESIGN_PLANT_PROJECT_DRAFT_DIR = Join-Path $reviewRuntime 'project_drafts'
$env:BIODESIGN_BACKUP_DIR = Join-Path $reviewRuntime 'backups'
$env:BIODESIGN_PYDNA_CONFIG_DIR = Join-Path $reviewRuntime 'pydna\config'
$env:BIODESIGN_PYDNA_DATA_DIR = Join-Path $reviewRuntime 'pydna\data'
$env:BIODESIGN_PYDNA_LOG_DIR = Join-Path $reviewRuntime 'pydna\logs'
$env:PYTHONDONTWRITEBYTECODE = '1'
Push-Location -LiteralPath $reviewSoftware
try {
    & $reviewPython -m streamlit run app.py --server.address 127.0.0.1 --server.port $reviewPort --server.headless true --server.fileWatcherType none
} finally {
    Pop-Location
}
```

Open [http://127.0.0.1:8632](http://127.0.0.1:8632). Save your project before pressing `Ctrl+C` to stop your instance. Reuse the same runtime directory to reopen its saved projects. Change the port variable and browser URL together when using another free port. These commands have been reviewed for paths and control flow; this documentation revision has not replayed them on Windows.

The hash-locked installation reproduces the declared dependencies, including their known limitations: ReportLab is absent, and both formal report downloads were blocked in the existing frozen-version operation records. `pip check` does not detect undeclared application imports. A successful HTTP response establishes startup only.

The existing package review and prior case evidence are historical records; this documentation revision does not rerun their tests.

## 2. Locate MT-01 and MT-02 material

- MT-01 frozen contracts: `cases/MT-01/contracts/`
- MT-02 frozen contracts: `cases/MT-02/contracts/`

For each case, inspect `source_contract.json`, `extraction_contract.json`, `expected_hashes.json`, `feature_contract.json`, and `redistribution_contract.json`.

The package does not contain source-record bytes, canonical FASTA bytes, or derived GenBank bytes because the frozen redistribution contracts prohibit bundling them. Reproduction therefore requires retrieving the exact versioned public accession and applying the frozen extraction interval.

## 3. Reconstruct and verify canonical DNA

### MT-01

- Accession: `KX758647.1`
- External coordinates: 571–4649, 1-based inclusive
- Python slice: `source_sequence[570:4649]`
- Expected length: 4079 bp
- Expected uppercase DNA SHA-256: `1847b411bd0592e0927db433bfc88f8eec3a9f8c30620af97aba5dae465c3104`

### MT-02

- Accession: `KM507054.1`
- External coordinates: 111–6719, 1-based inclusive
- Python slice: `source_sequence[110:6719]`
- Expected length: 6609 bp
- Expected uppercase DNA SHA-256: `ec86af6644082317a79dd938d6e70a0011b5d0f784f21da61fac55df4f43f8d2`

Use the exact accession version. Do not substitute an unversioned accession or another provider record unless its parsed sequence identity is first shown to be byte-equivalent to the frozen source hash.

Example sequence-only comparison after independently obtaining a source GenBank record:

```python
from hashlib import sha256
from Bio import SeqIO

record = SeqIO.read("SOURCE.gb", "genbank")
source = str(record.seq).upper()
canonical = source[570:4649]  # MT-01; use [110:6719] for MT-02
print(len(canonical))
print(sha256(canonical.encode("ascii")).hexdigest())
```

## 4. Compare canonical, FASTA, and GenBank-derived sequence

For any independently reproduced export set:

1. Parse the canonical sequence as uppercase DNA.
2. Parse the FASTA record and normalize to uppercase DNA without headers or whitespace.
3. Parse the GenBank record with Biopython and normalize `record.seq` to uppercase DNA.
4. Require identical lengths and identical DNA strings.
5. Compute SHA-256 over the uppercase ASCII DNA string and compare with the authoritative case hash above.

The whole-file SHA-256 of FASTA or GenBank is format-dependent and is not the canonical DNA SHA-256. The frozen runtime evidence records prior export byte hashes, but those export files are not distributable from this package under the frozen contracts.

## 5. Verify package integrity

From the package root:

```powershell
Get-FileHash -Algorithm SHA256 .\README.md
Get-Content .\MANIFEST_SHA256.txt
Get-Content .\PACKAGE_FILE_LIST.txt
```

`MANIFEST_SHA256.txt` covers critical documentation, sequence-contract, and component-library data files. `PACKAGE_FILE_LIST.txt` covers every package file except itself and lists relative path, byte size, and SHA-256.

