# Reproducibility guide

Current public V1.0 maintenance and historical paper reproduction are separate routes. Use matching source and dependency lock from the chosen archive; never reuse the other version's environment. The fixed historical ZIP, frozen tags, original hashes and historical limitations are unchanged.

当前公开 V1.0 维护版与论文历史复现是两条独立路线。源码与依赖锁必须来自同一个版本的解压目录；不得复用另一个版本的环境。历史固定 ZIP、冻结标签、原哈希和历史限制不变。

## Current-main ALB acceptance boundary (2026-10-11)

The tested maintenance commit `126ebc4303f579e730d41821ec0d6bce6e1dd400` received `ALB_SINGLE_GENE_E2E_GO` for one fixed ALB/Rice single-gene case. Verified scope: real-browser Steps 1–6; 2918 bp expression cassette; 8958 bp pCAMBIA backbone; fixed 27|28 insertion; 11876 bp complete plasmid; FASTA/GenBank sequence agreement; formal save, two complete cold restarts and continued editing; actual Markdown and four-page PDF downloads. This documentation update records the supplied external acceptance report and does not repeat the workflow test.

Historical read-only checking used an explicitly marked result-only test copy, not a verified real historical revision chain. No all-host, Multi-TU, Pathway, whole-software or wet-lab acceptance is claimed. User-provided promoter/terminator attribution remains pending confirmation; role-only inputs do not automatically establish current source attribution or formal Registry admission. The deterministic canonical map artifact was unavailable and is outside the passed deliverables. Third-party rights remain subject to the [README boundaries](README.md#public-content-provenance-and-license-boundaries-2026-10-09). Internal logs, private project data, unreviewed sequences and test copies are not included. Frozen-version defects and verdicts below remain historical facts.

## Current public V1.0: install and run

Run these commands in PowerShell from the repository root after extracting the current-main archive or the fixed maintenance baseline archive `bed1068a9e6e0f74ac80c8a0abd2ae6e97667c19` linked in [README](README.md#download-and-run). Use Windows x64 and 64-bit CPython 3.12. Keep the PowerShell window open while the app runs. If selecting a later source commit, use a new environment/runtime directory instead of the baseline directory below.

使用 Windows x64、64 位 CPython 3.12。在当前版解压根目录（包含 `software/`）运行以下 PowerShell 安装块，再运行启动块。两块均使用同一源码目录和 `PlantBioDesignReview\v1-0-maintenance-bed1068a`；不要把历史手册的安装块用于当前版。若以后改用其他源码提交，应使用新的环境和数据目录。

Install the locked environment:

```powershell
$ErrorActionPreference = 'Stop'
$reviewSoftware = Join-Path (Get-Location).Path 'software'
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\v1-0-maintenance-bed1068a'
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
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\v1-0-maintenance-bed1068a'
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

The current baseline lock declares ReportLab 4.2.2. Current code handles Markdown/PDF failures independently; this static fact does not prove successful installation or download. **Fresh installation and actual browser report downloads at this baseline remain NOT_PROVEN.** `pip check` does not detect undeclared application imports; a successful HTTP response establishes startup only. The earlier ALB GO above is bounded to its stated commit and case.

当前基线依赖锁含 ReportLab 4.2.2，代码分别处理 Markdown/PDF 失败；静态事实不等于实装或下载成功。**当前基线全新安装及实际浏览器报告下载仍为 NOT_PROVEN。** 先前 ALB GO 仅适用于上文指定提交和案例。

`software/requirements.txt` is a broader development/extended-feature dependency list, not the public locked installation route. Its full feature scope has not been accepted by this revision. Do not replace the runtime lock with it as part of these instructions.

`software/requirements.txt` 是范围更广的开发/扩展功能依赖清单，不是此处的公开锁定安装路线；本轮未验收其完整功能范围，不要用它替换运行锁。

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

