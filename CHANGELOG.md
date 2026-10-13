# V1.0 maintenance changelog — 拟新增条目

未发布；版本标签和发布日期尚未确定。本文件是准备源码包内的拟公开稿；原706文件候选未改。

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

提交 SHA、工件链接及校验和须在发布前用实际结果填写；当前不生成或虚构发布提交。
