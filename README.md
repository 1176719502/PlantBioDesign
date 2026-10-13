# Plant BioDesign: public V1.0 maintenance and historical snapshots


## V1.0 public main release disclosure

PlantBioDesign V1.0 维护版源码已于2026-10-13更新到公开 main，正式提交为 [`6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b`](https://github.com/1176719502/PlantBioDesign/commit/6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b)；该提交包含已经批准的715文件源码版本。本次维护版没有创建 GitHub Release，没有创建 v1.0.1 标签，也没有单独上传供下载的 ZIP Release 资产。仓库已有的论文历史快照 Release 不属于本次维护版发布。

历史上游原始源码候选为 `V1_0_PUBLIC_RELEASE_CANDIDATE_R1_SOURCE.zip`（706 文件），ZIP SHA-256：`49A40ECB2AA4B40F6879B431F26789D488405E1C9B0BDC18E875786FC85D8D67`。旧715文件准备包为 `V1_0_PUBLIC_RELEASE_PREPARATION_SOURCE_CORRECTION_R1.zip`，ZIP SHA-256：`AB3C8A3ACE759E2D55B1A1004DA0038573ABA620A93C9E1997756F4FE7722A6C`；它在706文件候选上仅修改入口 README 并增加9份说明/许可文件，没有改变生产代码、锁或序列。最终获批准的715文件包为 `V1_0_PUBLIC_RELEASE_WHITESPACE_CORRECTED_R1.zip`，ZIP SHA-256：`06F3228293DCCFD21158316DEF4C408237EB1FCC57FB0AD394A3B96EE608AAA2`；相对旧715包仅删除 README 末尾一组 CRLF（2字节），其余714文件同字节。上述 ZIP SHA-256 均不是 Git commit SHA。原 ZIP 及包外校验/资产文件未随本次 main 更新上传；GitHub 自动源码归档不是原批准 ZIP，不能使用该 ZIP SHA-256 校验自动归档。本次文档修正不重建或覆盖这些历史 ZIP。 以下限制继续适用。

- 当前 Publication Map PDF 不内嵌独立 sequence SHA-256 metadata。该能力已列入后续版本范围，须另行定义合同、开发和验证；不自动纳入 V1.1。PDF 文件哈希只对应 PDF 字节，序列身份需关联同次 SVG、canonical 序列及导出证据。原设计身份、FASTA/GenBank 序列与 feature 一致性合同保持，完整质粒和线性视图哈希不可混同。
- 验证限 Windows x64 / CPython 3.12、指定案例、下载和保存/重开/正常停止后冷恢复路径；不代表全部宿主、Multi-TU、Pathway 或全部功能 GO。
- 整合/独立定向测试各75 passed、5 failed；全新安装有效结果65 passed、5 failed。五项历史失败保留，不是全套全绿，首次失败遮挡的后续断言不能计为通过。
- 历史首次 Open 无响应根因及是否候选新增仍未证明，本次未修复该异常。窄视口与语言状态限制仍保留；先保存并确认，再停止或重开，未保存编辑安全不作保证。
- 第三方来源可追溯不等于所有权利清除；项目 MIT 不自动覆盖第三方序列、字体、依赖。当前仅源码分发，不含依赖本体、Edge 或离线运行时。具体许可证/notice 义务未满足则发布阻塞，免责声明不能替代。

完整说明见 [Release Notes](RELEASE_NOTES.md)、[CHANGELOG](CHANGELOG.md)、[PDF范围](PDF_METADATA_SCOPE.md)、[测试范围](TEST_FAILURES_AND_SCOPE.md)、[G05异常](G05_HISTORICAL_OPEN_NOTE.md)、[第三方补充](THIRD_PARTY_NOTICES_SUPPLEMENT.md)。

本副本的安装请使用本包 software/requirements-runtime.lock 和 software/app.py，参见 [安装说明](REPRODUCIBILITY.md#current-public-v10-install-and-run)。下文 current main 及固定正式提交归档已包含本次修复源码；bed1068a 是旧维护基线。后续验收补充不追溯改写下文静态检查及历史结论。



## Current V1.0 source: install and run

原获批准的715文件 ZIP 条目直接位于根层；GitHub 自动源码归档通常带有顶层目录。建议解压到新的专用文件夹；在该文件夹中应同时看到 README.md、REPRODUCIBILITY.md 和 software/。如果解压工具增加了外层目录，继续进入实际含 software/app.py 和 software/requirements-runtime.lock 的那一级。该级就是下列命令所需的解压源码根目录；软件实际入口是 software/app.py。

下列两个代码块全部是 **PowerShell** 命令，均先在同一解压源码根目录执行。依赖安装块从根目录用绝对路径读取本包 software/requirements-runtime.lock；启动块自行 Push-Location 到 software 后运行 Streamlit，再恢复原目录。不要直接照抄旧指南中的 bed1068a 环境目录。本包使用独立 PlantBioDesignReview\v1-0-release-material-correction-r1，首次安装要求该目录不存在；若已经存在，不删除它，选择新的唯一目录并在两个块中一致替换 reviewRoot。后续重开只运行第二块，复用同一包的源码、环境和数据目录；不能混用旧包环境。Windows x64 / 64位 CPython 3.12；依赖只来自本包原有运行锁，未新增依赖。

首次安装：

```powershell
$ErrorActionPreference = 'Stop'
$reviewSoftware = Join-Path (Get-Location).Path 'software'
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\v1-0-release-material-correction-r1'
$reviewEnv = Join-Path $reviewRoot 'env'
$reviewPython = Join-Path $reviewEnv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath (Join-Path $reviewSoftware 'app.py'))) {
    throw 'Open PowerShell in the extracted repository root first.'
}
py -3.12 -c "import platform, struct, sys; sys.exit(0 if platform.python_implementation() == 'CPython' and platform.machine().lower() in ('amd64', 'x86_64') and struct.calcsize('P') == 8 else 1)"
if ($LASTEXITCODE -ne 0) { throw '64-bit CPython 3.12 for Windows x64 is required.' }
if (Test-Path -LiteralPath $reviewRoot) { throw 'First installation requires a new directory. Choose a unique reviewRoot in BOTH blocks.' }
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

启动或后续重开：

```powershell
$ErrorActionPreference = 'Stop'
$reviewSoftware = Join-Path (Get-Location).Path 'software'
$reviewRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PlantBioDesignReview\v1-0-release-material-correction-r1'
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

浏览器打开 [http://127.0.0.1:8632](http://127.0.0.1:8632)。如更换空闲端口，启动变量和浏览器 URL 同步修改。保存并确认结果后，在所属 PowerShell 窗口按 Ctrl+C 停止；未保存编辑不保证保留。

### Browser and conversion engine

既有全新安装验收环境为 Windows 11 10.0.22631 / AMD64 / CPython 3.12.10 x64；界面和真实下载使用 Codex in-app browser。Edge 扩展控制因 auth token unavailable 未使用，不能声称用 Edge 完成界面自动化验收，也不代表全部浏览器/平台已验收。

Microsoft Edge 155 是该验收机已安装的外部 SVG 转换引擎。当前图谱 PDF/PNG 路径要求系统已安装且可被程序发现的 Microsoft Edge（PATH 的 msedge 或标准安装目录）；pip 运行锁不安装 Edge，本源码包不分发 Edge。缺少它时该图谱 PDF/PNG 转换不可用，SVG仍可独立交付。该前提针对图谱转换，不是普通用户必须使用 Edge 访问界面的要求，也不适用于 ReportLab 报告 PDF。没有证据支持将 Edge 写成所有页面或所有软件用户的统一强制依赖。

安装命令沿用已验证路线，仅更换隔离目录并增加首次安装拒绝复用的保护；本次材料修正未重新执行安装或浏览器功能验收。既有验证针对706文件上游候选，715文件包的产品代码/锁/序列与它同字节。

Plant BioDesign is a plant expression-vector design and review workbench. Current `main` is the public V1.0 maintenance line for ordinary users; it also retains historical paper-submission material. It is not the current V1.1 development checkout. Computational results do not establish experimental expression, biological performance, or wet-lab readiness.



## Version identity and package choice



| Identity | Commit |

| --- | --- |

| Current public V1.0 maintenance release checked on 2026-10-13 | `6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b` |

| Previous maintenance baseline checked on 2026-10-12 | `bed1068a9e6e0f74ac80c8a0abd2ae6e97667c19` |

| Original frozen software source | `8ead74c060c32e653e746030e557398637a2c2fc` |

| Historical distribution snapshot reviewed on 2026-10-09 | `176232bdd20eb0ae987b52ad8b84df1f71b35a39` |

| Separately adopted R2.1 submission-package source | `42bfb04c215fcfe76334f4e5a40f9cde60ea2133` |



The source tree is `53f8d4446f719678db363e4e373ddc88123fd80c`, with source tag `paper-01-submission-snapshot-20260930`. Distribution commits and original source commits identify different repository histories. The packaged `software/` source was copied from the frozen software; see [SOFTWARE_SNAPSHOT.md](SOFTWARE_SNAPSHOT.md).



The separate [PlantBioDesign-PAPER01 repository](https://github.com/1176719502/PlantBioDesign-PAPER01) contains a publication bundle with its software under `source_snapshot/`. The two repository layouts and completeness records differ. Use the installation guide matching the repository you downloaded.



## Download and run



Current `main` includes V1.0 report maintenance (R1–R3): the runtime hash lock includes ReportLab 4.2.2, Markdown/PDF downloads handle failures independently, and role-only saved input sources are displayed with current attribution unconfirmed. Component-bound provenance remains visible; source descriptions and accessions are not treated as literature citations. These changes do not establish whole-software V1.0 acceptance. To use the maintenance code, download [current main](https://github.com/1176719502/PlantBioDesign/archive/refs/heads/main.zip) and install its own lock in a separate environment using the guide below. The historical fixed ZIP and frozen tags retain their original bytes and limitations.



### Current public V1.0: ordinary use



Download [current main](https://github.com/1176719502/PlantBioDesign/archive/refs/heads/main.zip), or use the [fixed maintenance source archive](https://github.com/1176719502/PlantBioDesign/archive/6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b.zip) to obtain exactly the source checked by this documentation revision. `main` is a moving branch; the fixed maintenance baseline is not a claim about future main commits. Extract the chosen archive and open PowerShell in the folder containing `software/`. Follow [current-version installation and startup](REPRODUCIBILITY.md#current-public-v10-install-and-run): use `software/app.py` and `software/requirements-runtime.lock` from that same archive, with a separate environment and runtime directory. Do not combine current source with a historical lock or environment.



当前公开 V1.0 维护版供普通用户使用：下载上面的当前 main 或本轮核对的固定正式提交 `6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b`，解压后在包含 `software/` 的目录打开 PowerShell，按[当前版安装与启动说明](REPRODUCIBILITY.md#current-public-v10-install-and-run)使用同一份源码内的 `app.py` 和依赖锁，并使用独立环境和数据目录。不要混用历史快照的锁或环境。



**Historical documentation-only check at `bed1068a` (2026-10-12): fresh installation and actual browser report downloads were NOT_PROVEN at that review time.** Later bounded candidate validation is disclosed above and in Release Notes. This post-release documentation correction performs static checks only; the earlier ALB GO below belongs to its stated commit and case.



**2026-10-12 对 `bed1068a` 的历史文档静态审查：当时全新安装及实际浏览器报告下载为 NOT_PROVEN。** 后续候选限定验证见上文及 Release Notes。本次发布后文档修正仅做静态检查，下述历史 ALB GO 只适用于其指定提交和案例。



### Historical paper reproduction only



Use the [historical fixed snapshot ZIP](https://github.com/1176719502/PlantBioDesign/archive/176232bdd20eb0ae987b52ad8b84df1f71b35a39.zip) only to reproduce the historical distribution and its limitations. Follow [the frozen-snapshot commands](REPRODUCIBILITY.md#1-start-the-frozen-distribution-snapshot) with that snapshot's own lock and separate environment. It is not the latest maintenance version. The archive download and Windows installation have not been replayed in this documentation revision.



论文历史复现请使用固定分发快照 `176232bdd20eb0ae987b52ad8b84df1f71b35a39` 及其自身依赖锁，按[历史快照命令](REPRODUCIBILITY.md#1-start-the-frozen-distribution-snapshot)创建独立环境；它不是最新维护版，其字节、历史测试结论和限制保持不变。本轮未重跑下载或安装。



## Current ALB single-gene acceptance (2026-10-11)



The tested maintenance `main` at `126ebc4303f579e730d41821ec0d6bce6e1dd400` has a documented `ALB_SINGLE_GENE_E2E_GO` result for one fixed ALB/Rice single-gene case. A real browser completed Steps 1–6, producing a 2918 bp expression cassette, an 8958 bp pCAMBIA backbone with the fixed 27|28 insertion, and a 11876 bp complete plasmid. FASTA and GenBank sequences matched; formal save, two complete cold restarts, continued editing, and actual Markdown and four-page PDF downloads were verified. The external acceptance report supplied for this review records these results; this documentation update does not repeat the workflow test.



This result covers the stated ALB single-gene workflow only. It does not establish acceptance for all hosts, Multi-TU, Pathway, the whole software, or wet-lab expression. Historical read-only checking used an explicitly marked result-only test copy; it does not verify a real historical revision chain. Promoter/terminator inputs remain user-provided with attribution pending confirmation; role-only saved inputs do not automatically establish current source attribution or formal Registry admission. The deterministic canonical map artifact was unavailable and is outside the passed deliverables. Third-party rights remain subject to the boundaries below. No internal logs, private project data, unreviewed sequences, or test copies are added to this repository. The historical fixed snapshot's defects and verdicts remain unchanged.



## Known limitations of the historical fixed snapshot



- The historical fixed snapshot's `software/requirements-runtime.lock` does not contain ReportLab. Existing frozen-version operation evidence records both formal report downloads being blocked by its missing dependency. Current main's report maintenance does not change that fixed snapshot.

- The historical fixed snapshot's pCAMBIA catalog contract references `software/case_inputs/rice_hsa/raw/AF234296.1.gb`, which is absent from that snapshot. Another AF234296 record exists elsewhere, but the catalog loader reads the contract's exact path. Do not treat a visible catalog eligibility label as proof that selection succeeds.

- Historical user-manual evidence records incomplete source summaries and limited editing after project reopen. Viewing a saved result and downloading a sequence do not establish complete edit recovery; the current-main ALB acceptance above does not retroactively change that evidence.

- Complete MT-01 and MT-02 derived FASTA/GenBank payloads are omitted under the frozen redistribution contracts. Accession versions, extraction coordinates and hashes remain available for independent region reconstruction. The historical **BLOCKED as a complete reviewer sequence package** verdict applies to that requested payload scope; it is not a new whole-software startup verdict.



V1.1 and unadopted repair candidates are not installed by these instructions; current-main maintenance and the bounded ALB acceptance are described above. The Chinese manual is published separately below; its publication does not change the frozen software or its acceptance status.



## 中文使用手册（历史冻结分发快照）



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



## Current-main component evidence repair (2026-10-11)



The [public evidence notice](software/docs/qa/public_component_admission_evidence_r1/README.md) distinguishes original governance files from new factual summaries and records the necessary source-package files, attribution and limitations. All 17 DIRECT_USE sequence identities are preserved. The repair restores only the two already-declared formal contracts (E8 and HSP18.2 in their existing species scopes); the other 15 qualified identities remain blocked pending formal review. It does not change the frozen paper snapshot or its inventories, PAPER01, V1.1, or other open product audit findings.



## Official public documentation (2026-10-10)



**Historical snapshot manuals, not current-main installation guides.** All manual links below (Markdown and PDF) describe the ALB operation distribution snapshot `176232bdd20eb0ae987b52ad8b84df1f71b35a39`. For current public V1.0 installation, use [the current-version guide](REPRODUCIBILITY.md#current-public-v10-install-and-run). Their ReportLab failures and NO_GO/NOT_PROVEN findings remain historical; do not apply them as new findings about current main. Manual and PDF bytes are retained unchanged.



**以下中英文手册（Markdown 和 PDF）均为历史冻结快照手册，不是当前 main 的安装指南。** 它们的 ALB 操作基线为 `176232bdd20eb0ae987b52ad8b84df1f71b35a39`。当前公开 V1.0 请使用[当前版指南](REPRODUCIBILITY.md#current-public-v10-install-and-run)。手册中的 ReportLab 故障及 NO_GO/NOT_PROVEN 保留为历史判定，不作为当前 main 的新结论；手册及 PDF 原字节不变。



The official documentation preserves the frozen V1.0 limitations, historical NO_GO/NOT_PROVEN findings, and the existing distribution scope. It does not claim software acceptance or wet-lab validation.



### 中文



- [中文 R4 手册](docs/zh/r4/PlantBioDesign_中文使用手册.md) · [PDF](docs/zh/r4/PlantBioDesign_中文使用手册.pdf)

- [中文案例复现说明](docs/zh/r4/CASE_INPUT_REPRODUCIBILITY.md) · [PDF](docs/zh/r4/PlantBioDesign_案例复现说明.pdf)

- [中文软件简介](docs/zh/r4/PlantBioDesign_软件简介.md) · [PDF](docs/zh/r4/PlantBioDesign_软件简介.pdf)



### English



- [English User Manual](docs/en/PlantBioDesign_User_Manual.md) · [PDF](docs/en/PlantBioDesign_User_Manual.pdf)

- [English Case Input Reproducibility Guide](docs/en/CASE_INPUT_REPRODUCIBILITY.md) · [PDF](docs/en/CASE_INPUT_REPRODUCIBILITY.pdf)

- [English Software Overview](docs/en/PlantBioDesign_Software_Overview.md) · [PDF](docs/en/PlantBioDesign_Software_Overview.pdf)
