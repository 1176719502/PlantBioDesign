# PlantBioDesign V1.0 ALB 案例复现说明

中文 R4 正式公开文档 · 2026-10-10

## 1. 案例背景与目的

以水稻为计划表达宿主、人 ALB 为目标基因，说明如何记录真实来源、设计单基因表达盒并按固定边界生成质粒。本例是计算设计与序列一致性核验，不证明水稻表达、蛋白活性、产量或湿实验效果。

本 ALB 单基因操作例是独立操作示例，不是论文 MT-01 或 MT-02 的结果。论文案例分别为 4079 bp 双转录单元和 6609 bp 三转录单元来源区域，均未证明独立完整质粒重建。本说明的 2918 bp 表达盒与 11876 bp 质粒数值仅属于 ALB 操作案例，不能与论文区域长度交叉替代。

论文的逐位一致仅限指定来源区域及其序列导出；本 ALB 案例的序列核验按各轮已列明的范围解释，不覆盖完整质粒独立重建能力、全部注释、正式报告或湿实验验证。

论文分析所依据的冻结投稿源码提交为 `8ead74c060c32e653e746030e557398637a2c2fc`。本手册 ALB 操作使用的 GitHub 分发快照为 `176232bdd20eb0ae987b52ad8b84df1f71b35a39`；该快照的 `SOFTWARE_SNAPSHOT.md` 将其来源标为上述投稿源码。两者分别标识论文源码与 GitHub 分发对象，不据此声称两个提交逐文件等价；ALB 操作记录不扩展论文 MT-01/MT-02 的验证范围。既有操作记录称为 R5 ALB 案例，项目名为 `R5-SingleGene-20261008`；不将其他探索或修复候选混作同一案例。原始 GenBank、FASTA、完整衍生序列和内部日志不随包分发。

## 2. 输入材料及序列来源

| 输入 | 版本明确的来源 | 提取规则 | 长度 | 核酸 SHA-256（大写、去空白） |
| --- | --- | --- | ---: | --- |
| ALB CDS | `NM_000477.7` | 唯一 `CDS` 且 `gene=ALB`；GenBank `42..1871`，正链；Biopython `[41:1871](+)`；含终止密码子 | 1830 | `9ddcd40a33c631ae5de17aa79bf91938d4841968030f8928fa0cbb415b4f541a` |
| CaMV 35S | `AF485783.1` | `4974..5808`，正链；Python `[4973:5808]` | 835 | `4f5069bdd68260bb7a243ec7f8b628e13d52f58242c6f7acf53e3cc55a8673e2` |
| NOS terminator | `AF485783.1` | `7727..7979`，正链；Python `[7726:7979]` | 253 | `07296665a19dbedd665dc2f350869a1474a72811f54688cbef8835e24372ab3f` |
| backbone | `AF234296.1` | 完整 GenBank 记录；`topology=circular`；不截取、不反向互补 | 8958 | `83c7d28d071a9ff167dbe78817b2b20a5e285dcc6e1637e7392adb9f7be89de6` |

官方取得地址分别为：[NM_000477.7](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_000477.7&rettype=gb&retmode=text)、[AF485783.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF485783.1&rettype=gb&retmode=text)、[AF234296.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF234296.1&rettype=gb&retmode=text)。保存响应原文，不从网页截图抄序列。accession 只确认记录身份，不替代许可、来源资格或生物学批准。

## 3. 软件设计步骤

1. 项目定义：新建 Single Gene 项目，选择水稻，记录稳定遗传转化、无特定组织或诱导要求、定位未确定等真实设计目标。
2. 目标基因：输入 ALB CDS，记录 `NM_000477.7`、人来源及正链42..1871，核对1830 bp和完整CDS检查，确认后继续。
3. 表达盒：以 User sequence 输入 CaMV 35S 和 NOS；不添加可选元件，确认启动子→ALB→终止子的顺序和方向，生成2918 bp表达盒。
4. 骨架：目录Select失败属于已知限制；有使用权限时上传真实 `AF234296.1.gb`，核对8958 bp、circular及固定正向 `27|28` 插入边界。
5. 完整构建：核对输入和边界，点击 Generate full vector，检查11876 bp环状结果及图谱。
6. 结果与导出：保存项目，分别下载表达盒FASTA、完整质粒FASTA/GenBank及JSON备份；重开后核对身份与序列。冻结版正式报告仍阻断，重开编辑有限制。具体按钮及截图见中文手册第4–12章。

## 4. 计算结果

| 对象 | 长度及结果 | 核酸 SHA-256 |
| --- | --- | --- |
| 表达盒 | 835 + 1830 + 253 = 2918 bp | `8422558a6f117fb27debb3fc96ad3b954e22de904c0e48fe7eece447413bac7f` |
| 完整质粒 | 8958 + 2918 = 11876 bp；circular；历史GenBank为20个features | `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c` |

边界重建规则为 `backbone[:27] + cassette + backbone[27:]`，即原骨架第27与28个碱基之间正向插入。计算0阻断、0警告不等于来源完整或实验功能通过。

## 5. 序列级复现与核验

按附录 A 下载三个带版本记录，保留响应和文件字节哈希；按附录 B 核对身份、坐标、方向、CDS翻译及四段核酸哈希，再比较表达盒和固定边界重建值。核酸标准化为大写、去空白，FASTA标题及GenBank注释不参与核酸哈希。任何差异都应停止，不改动原序列以求通过。

### 5.1 实际导出文件的独立复核

从软件取得文件后，在其目录打开PowerShell，用下列短命令读取单条FASTA、打印核酸长度和哈希。将实际文件名代入，分别对表达盒FASTA、完整质粒FASTA执行，比较本说明的对应预期值；重新打开项目前后各做一次。

```powershell
@'
import hashlib
from Bio import SeqIO

r = SeqIO.read("expression-cassette.fasta", "fasta")
s = str(r.seq).upper()
assert set(s) <= set("ACGT")
print(len(s), hashlib.sha256(s.encode()).hexdigest())
'@ | python -
```

完整质粒GenBank另用下面命令读取。历史预期11876 bp、同一完整核酸哈希、circular、20个features。

```powershell
@'
import hashlib
from Bio import SeqIO

r = SeqIO.read("full-plasmid.gb", "genbank")
s = str(r.seq).upper()
assert set(s) <= set("ACGT")
print(
    len(s),
    hashlib.sha256(s.encode()).hexdigest(),
    r.annotations.get("topology"),
    len(r.features),
)
'@ | python -
```

仅序列哈希、环状标记及feature数量相符仍不能证明全部注释正确；完整注释和qualifiers需另作逐项比较，本公开文档不宣称已复验通过。
## 6. 已验证范围及局限

按主手册第 6–9 节输入：启动子 → ALB CDS → NOS 终止子；确认正向排列后生成表达盒。骨架使用第 4 步 `Upload GenBank file`，确认 `AF234296.1`、8958 bp、circular 和固定 `27|28` 正向插入边界。目录 `Select` 失败不能用改名或改坐标绕过。

既有复现记录的实际验证范围：三个来源记录、四段输入、2918 bp 表达盒和按固定边界得到的 11876 bp **序列级重建**均已核对。以下事项仍为 **NOT_PROVEN**：冻结软件在本机重新执行后的导出文件是否逐字符相同；完整质粒 GenBank 的 20 个 features、qualifiers 和注释指纹；保存、重开和下载流程的完整复验；报告生成。因而不能把本节的序列级重建写成“软件完整质粒导出通过”。

原候选为文档整合；本轮截图整改 R2 在同一冻结提交的独立副本中进行了有限重开与下载复核。2026-10-09 独立下载和序列重建通过属于原复现说明的既有记录；原整合轮未重新运行软件导出、保存重开或完整GenBank注释复验。历史R5操作与本轮未复验事项按各自时间、版本和范围区分，不将 NOT_PROVEN 改成通过。

许可与分发说明见 [LICENSE_MANUAL.md](LICENSE_MANUAL.md)。不分发历史 `case_input_helper.py`，也不借数据库可获取推定全部第三方权利已确认。

### 6.1 截图整改 R2 的有限实际复核

2026-10-09，在冻结提交的独立运行副本中打开历史 R5 ALB 数据库副本，并实际下载表达盒FASTA、完整质粒FASTA、完整质粒GenBank及项目JSON。UTF-8解析确认表达盒2918 bp，完整质粒11876 bp；核酸哈希与第4节相符；GenBank为circular、20个features。图谱原生PNG下载得到3000×2000完整标签图。下载文件和完整序列只保留在私有工作范围，不随本公开文档分发。

这次复核不证明本轮重新生成、实际上传、新保存、完整GenBank qualifiers一致性、JSON灾后恢复或报告下载通过。前文NOT_PROVEN记录属于原整合轮；只有上述明确列出的下载及序列身份取得新增证据，其余未升级。第2步恢复空字段和历史只读回退已实际观察并保留。

## 7. 复现命令和详细数据附录

命令适用Windows PowerShell 7（UTF-8管道）、CPython 3.12及Biopython。请在独立复现环境中运行，不向冻结软件环境临时补装。Markdown代码块为复制执行源；PDF中代码保留相同字符与缩进，整块复制时仍应核对换行。

### 附录 A：下载、保存和文件哈希

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

### 附录 B：提取与核酸哈希核验

下面是一次性从标准输入运行的临时代码。它只读取当前目录的三个 GenBank 文件，选择明确 feature，按坐标提取并打印长度和核酸 SHA-256；不访问项目源码、审计数据库或任何内部文件，也不生成完整质粒附件。

```powershell
@'
import hashlib
from pathlib import Path
from Bio import SeqIO


def h(seq):
    s = "".join(str(seq).upper().split())
    if not s or any(c not in "ACGT" for c in s):
        raise SystemExit("非 A/C/G/T，停止")
    return len(s), hashlib.sha256(s.encode()).hexdigest()


root = Path("case-inputs")
alb = SeqIO.read(root / "NM_000477.7.gb", "genbank")
reg = SeqIO.read(root / "AF485783.1.gb", "genbank")
bb = SeqIO.read(root / "AF234296.1.gb", "genbank")
if (alb.id, reg.id, bb.id) != ("NM_000477.7", "AF485783.1", "AF234296.1"):
    raise SystemExit("版本不符")
fs = [
    f
    for f in alb.features
    if f.type == "CDS" and f.qualifiers.get("gene") == ["ALB"]
]
if len(fs) != 1:
    raise SystemExit("ALB CDS 不是唯一 feature")
if str(fs[0].location) != "[41:1871](+)":
    raise SystemExit("CDS 坐标/方向不符")
seqs = {
    "ALB": fs[0].extract(alb.seq),
    "35S": reg.seq[4973:5808],
    "NOS": reg.seq[7726:7979],
    "backbone": bb.seq,
}
for k, s in seqs.items():
    print(k, *h(s))
if str(seqs["ALB"].translate(to_stop=True)) != fs[0].qualifiers["translation"][0]:
    raise SystemExit("翻译不符")
if bb.annotations.get("topology") != "circular":
    raise SystemExit("骨架不是 circular")
cas = seqs["35S"] + seqs["ALB"] + seqs["NOS"]
full = seqs["backbone"][:27] + cas + seqs["backbone"][27:]
print("cassette", *h(cas))
print("full_sequence_reconstruction", *h(full))
for k in ("ALB", "35S", "NOS"):
    path = root / (k + ".fasta")
    if path.exists():
        raise SystemExit("FASTA 已存在，不覆盖")
    path.write_text(">" + k + "\n" + str(seqs[k]).upper() + "\n", encoding="ascii")
'@ | python -
```

预期输出应为：表达盒 `2918` bp、核酸哈希 `8422558a6f117fb27debb3fc96ad3b954e22de904c0e48fe7eece447413bac7f`；按 `backbone[:27] + cassette + backbone[27:]` 的固定正向边界重建序列为 `11876` bp、核酸哈希 `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c`。这些值已于 2026-10-09 通过独立 NCBI 下载和上述标准库代码实际核对。

逐行将实际长度及哈希与第2节及上述两个组装值比较，任何不同均停止，不修改序列以求通过。生成的 `ALB.fasta`、`35S.fasta` 和 `NOS.fasta` 分别粘贴到主手册第6–7节的用户序列字段；标题和换行不参与核酸哈希。骨架仍上传原始 GenBank。



