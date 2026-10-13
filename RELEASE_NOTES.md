# PlantBioDesign V1.0 maintenance — Release Notes

状态：拟公开稿，尚未发布。拟议版本：v1.0.1（仅建议，未创建标签）。经功能验收的上游原始源码候选为 706 文件，SHA-256：`49A40ECB2AA4B40F6879B431F26789D488405E1C9B0BDC18E875786FC85D8D67`，文件名 `V1_0_PUBLIC_RELEASE_CANDIDATE_R1_SOURCE.zip`。准备正式发布的对象为 `V1_0_PUBLIC_RELEASE_PREPARATION_SOURCE_CORRECTION_R1.zip`（715 文件），在上游候选基础上仅修改发布入口 README 并增加9份说明/许可文件；没有改变生产代码、锁或序列。最终 ZIP 的实际 SHA-256 只登记在与下载包一起提供的包外 `SHA256SUMS_SOURCE_CORRECTION_R1.txt` 和 `RELEASE_ASSET_MANIFEST_R1.json`，上游哈希不能用作715文件包哈希。包内不记录自身 ZIP 哈希，避免自引用。当前没有发布提交、标签或下载 URL。 本稿随准备源码发布时须完整保留“已知限制”和“分发边界”；发布提交 SHA、日期及下载链接由未来发布前检查填写。

## 本次变化

- 修复图谱 SVG/PDF/PNG 导出的格式失败隔离、损坏 PDF 拒绝、安全错误诊断及 Windows 临时资源清理；PDF/PNG 保持由已验证 SVG 同源转换。
- 补充图谱导出定向回归测试；公开安装文档区分当前维护版与历史论文快照，使用同版本源码和哈希锁定依赖。
- 本次不修改序列、元件准入、报告生成或项目持久化逻辑，不涉及 PAPER01、Formal 或 V1.1。

- P1-02（已独立通过的文档修复）：移除不存在的 test_imports.py、START.bat、Stop_BioDesign_Formal.bat、Start_BioDesign_MVP.bat 启动/检查操作引用，改为真实 software/app.py 入口、同包 software/requirements-runtime.lock 的锁定安装、pip check，以及从 software 目录用独立环境解释器运行 Streamlit；没有新增脚本或产品功能。

## 安装与浏览器前提

本包解压根层即包含 software/；进入实际含 software/app.py 的源码根目录，依赖安装在该根目录执行，Streamlit 由启动块进入 software 执行。使用同包锁和新的独立环境/数据目录，首次安装不复用 bed1068a。完整 PowerShell 两块命令见包内 README 的 This preparation package: install and run 一节。

界面验收实际使用 Codex in-app browser；Windows 11 x64 / CPython 3.12.10。Microsoft Edge 155 为已安装的外部图谱 SVG→PDF/PNG 转换引擎，当前该转换功能需要可发现的 Edge，pip 锁不安装它，缺少时 PDF/PNG 不可用而 SVG 可独立交付。它不是所有用户访问界面的强制浏览器，ReportLab 报告 PDF 也不依赖这条转换路径。其他浏览器/宿主没有因此全面验收。

## 验证范围

既有独立验证覆盖 Windows x64 / CPython 3.12 的指定候选全新安装、真实浏览器 SVG/PDF/PNG 图谱和 Markdown/PDF 报告下载，以及指定草稿和完成项目的保存、重新打开与正常停止后冷恢复。原中文导航顺序后首次 Open 已在新会话中成功复测。以上不是全部项目、平台或浏览器交互的验收。

整合与独立候选的定向回归各为 **75 passed、5 failed**；全新安装报告另有 **65 passed、5 failed** 的有效测试运行。五项历史报告名称/来源文本断言失败继续保留；与同环境基线相比，失败集合和消息一致，未发现本次新增失败。没有宣称完整测试套件全部通过。

源码内 README/安装说明中的“静态检查、NOT_PROVEN”记录属于此前文档审查时点，本说明补充同一候选的后续限定验证，不改写历史快照的缺陷和验收结论。固定 `bed1068a` 链接仍只对应旧维护基线，不能把它当成本修复候选的下载链接；请使用本次发布明确列明并校验 SHA-256 的源码工件及其自身锁文件。

## 已知限制

**PDF 序列 metadata。** 本次图谱 PDF 包含项目显示名、construct、revision 和长度信息，但不提供独立内嵌的 sequence SHA-256 metadata。核对序列身份需关联同次 SVG、对应 canonical 序列及导出证据；PDF 文件 SHA-256 仅证明 PDF 字节完整性。PDF 单文件序列 metadata 将作为后续功能单独定义合同、开发和验证，未指定交付版本或日期。该范围决定不降低图谱与当前设计的绑定、FASTA/GenBank 与相应 canonical 的序列一致性及 GenBank feature 一致性要求。完整质粒与线性表达构建视图的哈希不可混同。

**项目交互。** 历史会话出现过首次 Open 后无可见变化；最新诊断没有复现持续 Open 阻断，已验证所测草稿和完成项目保存、重开及冷恢复一致。首次无响应的精确根因以及是否为本候选新增仍未证实，**本次未修复该历史异常**。窄视口侧栏展开时仍观察到一次“新建项目”点击无变化，折叠侧栏后成功；语言单选标记与页面语言也可能短暂失配。可尝试折叠侧栏、增大视口并明确选择语言，但这不是已证明能消除所有 Open 异常的修复。请先保存并确认保存结果，再停止/重开；刷新、换会话或重启不能保证保留尚未保存的编辑。未验证写入瞬间断电、任意历史 session、移动端或全部项目类型。

**第三方序列。** 本次未新增或扩大既有序列分发范围。保留 accession、原提交者/文献、提取坐标与链/拼接、哈希和来源说明。INSDC/NCBI 数据库政策与来源核验不等于专利、版权、材料转让或商业实施的全部许可；专利有效性、法域、FTO 和完整权属链仍需个案确认。项目 MIT 不自动覆盖第三方序列、字体或软件。测试所用用户提供元件及私有项目备份不随源码发布。

**依赖 notices。** 当前运行锁含52项，包内历史 THIRD_PARTY_NOTICES 和 license_inventory 只列49项，漏列 pypdf 6.10.0、ReportLab 4.2.2、chardet 7.6.0；不能称旧表已完整。精确安装版本的许可分别为 BSD-3-Clause、BSD 三条款式文本、0BSD。配套 notice 补充稿记录这三项，不替代完整运行时许可审计。

## 分发边界

本次只发布已审查源码与配套说明，依赖由用户按同包锁安装；不包含依赖 wheels、site-packages、Edge 或 onedir/离线可执行运行时。随包 Noto Sans SC 的 OFL、版权和 provenance 必须保留。任何包含依赖本体的未来包都须另行核对直接、传递和嵌套组件许可及 notices，本次结论不覆盖它们。计算结果不构成实验验证或生物学可用性承诺。


当前验证不代表全部宿主、Multi-TU、Pathway 或全部功能 GO。五项失败及逐项原因见 [测试范围](TEST_FAILURES_AND_SCOPE.md)。更多范围见 [PDF说明](PDF_METADATA_SCOPE.md)、[G05异常](G05_HISTORICAL_OPEN_NOTE.md)、[第三方补充](THIRD_PARTY_NOTICES_SUPPLEMENT.md)。
