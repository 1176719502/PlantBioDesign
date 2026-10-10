# 案例输入复现说明（无项目专有辅助脚本）

论文分析所依据的冻结投稿源码提交为 `8ead74c060c32e653e746030e557398637a2c2fc`。本手册 ALB 操作使用的 GitHub 分发快照为 `176232bdd20eb0ae987b52ad8b84df1f71b35a39`；该快照的 `SOFTWARE_SNAPSHOT.md` 将其来源标为上述投稿源码。两者分别标识论文源码与 GitHub 分发对象，不据此声称两个提交逐文件等价；ALB 操作记录不扩展论文 MT-01/MT-02 的验证范围。

本说明用于该分发快照的 R5 ALB 操作案例。公开载荷不需要、也不包含 `case_input_helper.py`。所有命令使用 Windows PowerShell、Python 3.12 和公开的 Biopython；文内短代码由复现者在本机运行，不提供独立辅助脚本文件。网络取得日期、原始响应和文件哈希必须由复现者自行保存。

本 ALB 单基因操作例是独立操作示例，不是论文 MT-01 或 MT-02 的结果。论文案例分别为 4079 bp 双转录单元和 6609 bp 三转录单元来源区域，均未证明独立完整质粒重建。本说明2918 bp表达盒与11876 bp质粒仅属于ALB操作例，不与论文区域长度交叉替代。

本例没有湿实验验证；序列级重建不等于软件完整质粒导出通过。历史记录支持的保存重开查看和核心序列下载，不等于完整六步编辑恢复或本轮完整复验；完整GenBank qualifiers未证实，冻结分发操作基线的正式报告仍受ReportLab缺失阻断。历史候选修复没有改变冻结版能力。

## 1. 固定输入、坐标和预期值

| 输入 | 版本明确的来源 | 提取规则 | 长度 | 核酸 SHA-256（大写、去空白） |
| --- | --- | --- | ---: | --- |
| ALB CDS | `NM_000477.7` | 唯一 `CDS` 且 `gene=ALB`；GenBank `42..1871`，正链；Biopython `[41:1871](+)`；含终止密码子 | 1830 | `9ddcd40a33c631ae5de17aa79bf91938d4841968030f8928fa0cbb415b4f541a` |
| CaMV 35S | `AF485783.1` | `4974..5808`，正链；Python `[4973:5808]` | 835 | `4f5069bdd68260bb7a243ec7f8b628e13d52f58242c6f7acf53e3cc55a8673e2` |
| NOS terminator | `AF485783.1` | `7727..7979`，正链；Python `[7726:7979]` | 253 | `07296665a19dbedd665dc2f350869a1474a72811f54688cbef8835e24372ab3f` |
| backbone | `AF234296.1` | 完整 GenBank 记录；`topology=circular`；不截取、不反向互补 | 8958 | `83c7d28d071a9ff167dbe78817b2b20a5e285dcc6e1637e7392adb9f7be89de6` |

官方取得地址分别为：[NM_000477.7](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_000477.7&rettype=gb&retmode=text)、[AF485783.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF485783.1&rettype=gb&retmode=text)、[AF234296.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF234296.1&rettype=gb&retmode=text)。保存响应原文，不从网页截图抄序列。accession 只确认记录身份，不替代许可、来源资格或生物学批准。

## 2. 下载、保存和文件哈希

环境要求：Windows x64、PowerShell 7（UTF-8管道）、CPython 3.12、Biopython（`python -m pip install biopython`）。在新目录执行：

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path .\case-inputs | Out-Null
$base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id={0}&rettype=gb&retmode=text'
foreach ($a in @('NM_000477.7','AF485783.1','AF234296.1')) {
  Invoke-WebRequest -Uri ($base -f $a) -OutFile (Join-Path .\case-inputs ($a + '.gb'))
}
Get-FileHash .\case-inputs\*.gb -Algorithm SHA256 | Format-Table Path,Hash
```

文件字节哈希与核酸哈希是两种不同指纹，必须分别记录。NCBI 响应的注释、换行或日期变化会改变文件字节哈希；不得编辑响应去追求历史字节相同。

## 3. 可审查的提取和核酸哈希核验

下面是一次性从标准输入运行的临时代码。它只读取当前目录的三个 GenBank 文件，选择明确 feature，按坐标提取并打印长度和核酸 SHA-256；不访问项目源码、审计数据库或任何内部文件，也不生成完整质粒附件。

```powershell
@'
import hashlib
from pathlib import Path
from Bio import SeqIO
def h(seq):
    s = ''.join(str(seq).upper().split())
    if not s or any(c not in 'ACGT' for c in s): raise SystemExit('非 A/C/G/T，停止')
    return len(s), hashlib.sha256(s.encode()).hexdigest()
root=Path('case-inputs')
alb=SeqIO.read(root/'NM_000477.7.gb','genbank')
reg=SeqIO.read(root/'AF485783.1.gb','genbank')
bb=SeqIO.read(root/'AF234296.1.gb','genbank')
if (alb.id,reg.id,bb.id)!=('NM_000477.7','AF485783.1','AF234296.1'): raise SystemExit('版本不符')
fs=[f for f in alb.features if f.type=='CDS' and f.qualifiers.get('gene')==['ALB']]
if len(fs)!=1: raise SystemExit('ALB CDS 不是唯一 feature')
if str(fs[0].location)!='[41:1871](+)': raise SystemExit('CDS 坐标/方向不符')
seqs={'ALB':fs[0].extract(alb.seq),'35S':reg.seq[4973:5808],'NOS':reg.seq[7726:7979],'backbone':bb.seq}
for k,s in seqs.items(): print(k,*h(s))
if str(seqs['ALB'].translate(to_stop=True))!=fs[0].qualifiers['translation'][0]: raise SystemExit('翻译不符')
if bb.annotations.get('topology')!='circular': raise SystemExit('骨架不是 circular')
cas=seqs['35S']+seqs['ALB']+seqs['NOS']
full=seqs['backbone'][:27]+cas+seqs['backbone'][27:]
print('cassette',*h(cas))
print('full_sequence_reconstruction',*h(full))
for k in ('ALB','35S','NOS'):
    path=root/(k+'.fasta')
    if path.exists(): raise SystemExit('FASTA 已存在，不覆盖')
    path.write_text('>'+k+'\n'+str(seqs[k]).upper()+'\n',encoding='ascii')
'@ | python -
```

预期输出应为：表达盒 `2918` bp、核酸哈希 `8422558a6f117fb27debb3fc96ad3b954e22de904c0e48fe7eece447413bac7f`；按 `backbone[:27] + cassette + backbone[27:]` 的固定正向边界重建序列为 `11876` bp、核酸哈希 `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c`。这些值已于 2026-10-09 通过独立 NCBI 下载和上述标准库代码实际核对。

逐行将实际长度及哈希与第1节及上述两个组装值比较，任何不同均停止，不修改序列以求通过。生成的 `ALB.fasta`、`35S.fasta` 和 `NOS.fasta` 分别粘贴到主手册第6–7节的用户序列字段；标题和换行不参与核酸哈希。骨架仍上传原始 GenBank。

## 4. 软件内输入和边界

按主手册第 6–9 节输入：启动子 → ALB CDS → NOS 终止子；确认正向排列后生成表达盒。骨架使用第 4 步 `Upload GenBank file`，确认 `AF234296.1`、8958 bp、circular 和固定 `27|28` 正向插入边界。目录 `Select` 失败不能用改名或改坐标绕过。

本轮实际验证范围：三个来源记录、四段输入、2918 bp 表达盒和按固定边界得到的 11876 bp **序列级重建**均已核对。以下事项仍为 **NOT_PROVEN**：冻结软件在本机重新执行后的导出文件是否逐字符相同；完整质粒 GenBank 的 20 个 features、qualifiers 和注释指纹；保存、重开和下载流程的完整复验；报告生成。因而不能把本节的序列级重建写成“软件完整质粒导出通过”。

## 5. 许可和证据边界

本发布包不包含历史辅助脚本 `case_input_helper.py`、原始 GenBank/FASTA、完整衍生序列或内部审查证据。项目负责人已授权本说明及配套手册和截图公开，署名为 PlantBioDesign；具体使用范围见 [手册许可与发布范围](LICENSE_MANUAL.md)。本说明中的数据库链接、记录版本、坐标与哈希用于引用和独立核验，不授予第三方序列或专利实施权。软件运行验收边界不因文档公开而改变。

## 6. 实际导出文件的独立复核

从软件取得文件后，在其目录打开PowerShell，用下列短命令读取单条FASTA、打印核酸长度和哈希。将实际文件名代入，分别对表达盒FASTA、完整质粒FASTA执行，比较本说明的对应预期值；重新打开项目前后各做一次。

```powershell
python -c "import hashlib; from Bio import SeqIO; r=SeqIO.read('expression-cassette.fasta','fasta'); s=str(r.seq).upper(); assert set(s)<=set('ACGT'); print(len(s),hashlib.sha256(s.encode()).hexdigest())"
```

完整质粒GenBank另用下面命令读取。历史预期11876 bp、同一完整核酸哈希、circular、20个features。

```powershell
python -c "import hashlib; from Bio import SeqIO; r=SeqIO.read('full-plasmid.gb','genbank'); s=str(r.seq).upper(); assert set(s)<=set('ACGT'); print(len(s),hashlib.sha256(s.encode()).hexdigest(),r.annotations.get('topology'),len(r.features))"
```

仅序列哈希、环状标记及feature数量相符仍不能证明全部注释正确；完整注释和qualifiers需另作逐项比较，本轮不宣称通过。
