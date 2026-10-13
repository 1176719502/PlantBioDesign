# V1.0 maintenance changelog

PlantBioDesign V1.0 维护版源码已于2026-10-13更新到公开 main，正式提交为 [`6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b`](https://github.com/1176719502/PlantBioDesign/commit/6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b)；该提交包含已经批准的715文件源码版本。本次维护版没有创建 GitHub Release，没有创建 v1.0.1 标签，也没有单独上传供下载的 ZIP Release 资产。仓库已有的论文历史快照 Release 不属于本次维护版发布。

原706文件候选、旧715文件准备包及最终715文件包均保留，身份与 ZIP 校验和见 [Release Notes](RELEASE_NOTES.md)。

## Changed

- 修复图谱导出失败隔离、损坏 PDF 校验、安全诊断及 Windows 临时资源清理，增加定向回归。
- 更新当前 V1.0 与历史冻结版的安装入口、依赖锁和文档范围说明。
- 新增运行依赖 pypdf 6.10.0；ReportLab 4.2.2 和 chardet 7.6.0 为既有依赖。

- P1-02（已独立通过的文档修复）：移除不存在的 test_imports.py、START.bat、Stop_BioDesign_Formal.bat、Start_BioDesign_MVP.bat 启动/检查操作引用，改为真实 software/app.py 入口、同包 software/requirements-runtime.lock 的锁定安装、pip check，以及从 software 目录用独立环境解释器运行 Streamlit；没有新增脚本或产品功能。

## Validation and known limitations

- 指定 Windows x64 / CPython 3.12 候选完成安装、真实浏览器下载和受控保存/重开/冷恢复验证；定向整合与独立运行各75 passed、5 failed，不是全套全绿。
- 图谱 PDF 没有独立内嵌 sequence SHA-256 metadata；该能力列为后续独立功能。现有图谱/FASTA/GenBank/设计序列一致性要求保持。
- 历史首次 Open 无响应未证明根因、未确认是否候选新增，也未修复；已验证路径通过不代表所有交互无缺陷。
- 不新增序列分发；第三方权利未全清。旧依赖 notices 49项未覆盖当前52项；源码发布不包含依赖本体。
- 完整范围、用户操作说明及第三方边界须与本次 Release Notes 一并公开，不能删去限制单独引用通过结论。

源码可从 [公开 main](https://github.com/1176719502/PlantBioDesign/tree/main) 或上述正式提交获取。GitHub 自动源码归档与原批准 ZIP 的压缩字节不同；原 ZIP 校验和不适用于自动归档。
