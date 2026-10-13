# PDF metadata 范围说明

当前图谱 PDF 含项目显示名、construct、revision、长度，但不内嵌独立 sequence SHA-256 metadata。此能力已列入后续版本范围，未指定版本/日期，也不自动归入 V1.1；须另行定义字段、schema、编码、写入位置、冲突优先级和独立消费端验证。

PDF 文件 SHA-256 只校验文件字节。序列身份需关联同次 SVG、对应 canonical 及导出证据；PNG metadata、SVG checksum、外部 manifest 或其他报告正文哈希均不是该 PDF 内嵌字段。原设计绑定、同源转换、FASTA/GenBank 序列与 feature 坐标/方向/顺序合同继续适用，完整圆形质粒与线性表达视图须区分。
