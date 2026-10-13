# BioDesign Studio

Current V1.0 component admission evidence and public-summary limits are recorded in [the public evidence notice](docs/qa/public_component_admission_evidence_r1/README.md). Evidence paths resolve from this `software/` directory. The 17 qualified DIRECT_USE identities remain distinct from the two already-declared formal Registry admissions; this repair preserves their existing host/role boundaries.

BioDesign Studio is a local-first documentation workspace for synthetic biology design records, pathway project notes, traceability review, and documentation-only export/import packages.

## Public V1.0 runtime and startup

Use `app.py` as the public runtime entry. Start from the extracted repository root (the parent of this `software/` directory) and follow the complete PowerShell [current-version installation and startup guide](../REPRODUCIBILITY.md#current-public-v10-install-and-run). It creates a separate CPython 3.12 Windows x64 environment, installs this version's `requirements-runtime.lock` with `--require-hashes --only-binary=:all:`, checks dependencies with `python -m pip check`, and runs `python -m streamlit run app.py` from `software/` using the isolated interpreter. The guide selects review port `8632`; it checks the port before launch and isolates project data outside the source tree. Save the project and press `Ctrl+C` in the owning PowerShell window to stop; use the same source and runtime directory to reopen it.

公开运行入口为 `app.py`。从解压仓库根目录（本 `software/` 的上一级）按[当前版 PowerShell 安装与启动指南](../REPRODUCIBILITY.md#current-public-v10-install-and-run)操作：Windows x64 / 64 位 CPython 3.12，独立环境，本版本 `requirements-runtime.lock` 的哈希锁定安装，`python -m pip check`，再用独立解释器从 `software/` 运行 `python -m streamlit run app.py`。指南使用检查后的 `8632` 端口，并将数据隔离在源码之外。保存项目后在所属 PowerShell 窗口按 `Ctrl+C` 停止；重开时使用同一源码和数据目录。

The source and lock must come from the same current-main archive or fixed maintenance baseline `bed1068a9e6e0f74ac80c8a0abd2ae6e97667c19`. `requirements.txt` is a broader development/extended-feature list; it is not a substitute for this public locked route, and its complete feature scope is not accepted here. Current-baseline fresh installation and actual browser report downloads remain **NOT_PROVEN**; these instructions were checked statically, not executed in a new environment.

源码与锁必须来自同一份当前 main 或固定维护基线 `bed1068a9e6e0f74ac80c8a0abd2ae6e97667c19`。`requirements.txt` 是更广的开发/扩展功能依赖清单，不替代公开锁定路线，本轮未验收其完整功能范围。当前基线全新安装及实际浏览器报告下载仍为 **NOT_PROVEN**；本轮仅静态检查命令。

For normal local review, do not start Redis, Docker, FastAPI, or RQ workers unless a separate task explicitly asks for asynchronous infrastructure.

## Retained product context

The inherited product notes describe the **expression-vector-first design-preparation MVP**. BioDesign Studio helps users create and review expression design records, inspect cassette/vector slot context, read source/provenance status, collect manual follow-up notes, and prepare documentation-only handoff review material.

Pathway projects remain useful for grouping, traceability, review notes, documentation snapshots, and package preview context. They are supporting project-workspace surfaces, not the whole product identity.

## Main Workflow

The current expression-vector-first mainline is:

```text
Expression Wizard
-> expression design record
-> cassette/vector slot readback
-> Component Library source/provenance and manual follow-up review
-> Handoff Review expression-vector package preview
-> documentation-only review notes, traceability, and project context
```

Core surfaces include:

- Expression Wizard as the first-stage expression design record path.
- Component Library for slot/source/provenance readback and manual follow-up context.
- Handoff Review for expression-vector package preview and project-level review context.
- Pathway Projects and Pathway Workspace for grouping, notes, linked design records, documentation snapshots, reports, traceability, and package preview context.
- Design Library and Saved Designs for reviewing saved design records.
- Documentation snapshots for preserving local project documentation state.
- Reports and traceability summaries for documentation review.
- Documentation-only export/import packages with import preview and duplicate guard checks.

## Product Boundaries

BioDesign Studio is documentation software. It does not provide:

- Wet-lab automation.
- Experimental validation.
- Biological readiness approval.
- Biological outcome prediction.
- Pathway optimization.
- Automated recommendation of biological actions.
- Protocol generation.
- Autonomous DBTL execution.

Export and import packages are documentation-only. Saved Dashboard snapshots, Design Library entries, Pathway Workspace records, reports, and traceability summaries are local review records; they do not certify biological use.

## Public documentation entry points

- [Repository README](../README.md): current public V1.0 versus historical paper snapshots.
- [Reproducibility guide](../REPRODUCIBILITY.md): separate current and historical installation routes, plus historical sequence reconstruction.
- [Historical Chinese R4 manual](../docs/zh/r4/PlantBioDesign_中文使用手册.md) and [historical English manual](../docs/en/PlantBioDesign_User_Manual.md): ALB operation snapshot `176232bdd20eb0ae987b52ad8b84df1f71b35a39`, with original limitations. Use the current-version guide above for current main.
- [Software source identity](../SOFTWARE_SNAPSHOT.md): frozen source origin, not current-main acceptance.

中文 R4 与英文手册均对应历史 ALB 操作快照，保留原始限制；当前 main 的安装请使用上方当前版指南。

## Historical Material

Historical release notes, frozen MVP records, older roadmap material, and archived planning notes are preserved for traceability. Treat them as historical unless a task explicitly reopens that scope.
