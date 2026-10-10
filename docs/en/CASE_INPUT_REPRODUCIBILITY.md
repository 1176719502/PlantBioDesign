# Case Input Reproducibility Guide

PlantBioDesign V1.0 · Official public documentation · 2026-10-10

## 1. Background and purpose

This case uses rice as the intended expression host and human ALB as the target gene to illustrate authentic provenance documentation, single-gene expression cassette design, and plasmid generation at a fixed insertion boundary. It is a computational design and sequence-consistency check, not evidence of expression in rice, protein activity, yield, or wet-lab performance.

This ALB single-gene example is an independent operational demonstration, not a result from the paper cases MT-01 or MT-02. Those cases concern a 4079 bp source region with two transcription units and a 6609 bp source region with three transcription units, respectively; neither establishes independent reconstruction of a complete plasmid. The 2918 bp expression cassette and 11876 bp plasmid in this guide belong only to the ALB operational case and must not be substituted for the paper's source-region lengths.

The paper's base-by-base agreement is limited to the designated source regions and their sequence exports. Sequence checks for this ALB case must be interpreted within the scope stated for each review round; they do not establish independent reconstruction of complete plasmids, validation of all annotations, formal report delivery, or wet-lab validation.

The frozen submission source-code commit underlying the paper analysis is `8ead74c060c32e653e746030e557398637a2c2fc`. The GitHub distribution snapshot used for the ALB operations in this manual is `176232bdd20eb0ae987b52ad8b84df1f71b35a39`; its `SOFTWARE_SNAPSHOT.md` identifies the submission source above as its origin. These commits identify the paper source and the GitHub distribution separately; this statement does not establish file-by-file equivalence between them. The ALB operation records do not extend the validation scope of the paper cases MT-01/MT-02. Existing operation records call this the R5 ALB case, project `R5-SingleGene-20261008`. Other exploratory runs or fix candidates are not treated as the same case. Raw GenBank records, FASTA, complete derived sequences, and internal logs are not distributed.

## 2. Input materials and sequence provenance

| Input | Versioned source | Extraction rule | Length | Nucleotide SHA-256 (uppercase, whitespace removed) |
| --- | --- | --- | ---: | --- |
| ALB CDS | `NM_000477.7` | Unique `CDS` with `gene=ALB`; GenBank `42..1871`, positive strand; Biopython `[41:1871](+)`; includes stop codon | 1830 | `9ddcd40a33c631ae5de17aa79bf91938d4841968030f8928fa0cbb415b4f541a` |
| CaMV 35S | `AF485783.1` | `4974..5808`, positive strand; Python `[4973:5808]` | 835 | `4f5069bdd68260bb7a243ec7f8b628e13d52f58242c6f7acf53e3cc55a8673e2` |
| NOS terminator | `AF485783.1` | `7727..7979`, positive strand; Python `[7726:7979]` | 253 | `07296665a19dbedd665dc2f350869a1474a72811f54688cbef8835e24372ab3f` |
| Vector backbone | `AF234296.1` | Complete GenBank record; `topology=circular`; no truncation or reverse complementation | 8958 | `83c7d28d071a9ff167dbe78817b2b20a5e285dcc6e1637e7392adb9f7be89de6` |

Official retrieval links: [NM_000477.7](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NM_000477.7&rettype=gb&retmode=text), [AF485783.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF485783.1&rettype=gb&retmode=text), and [AF234296.1](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=AF234296.1&rettype=gb&retmode=text). Save the original response rather than transcribing sequence from screenshots. An accession establishes record identity, not licensing, provenance eligibility, or biological approval.

## 3. Software design workflow

1. Project definition: create a Single Gene project, select rice, and record the actual objectives: stable genetic transformation, no specific tissue or induction requirement, and undetermined localization.
2. Target gene: enter ALB CDS; record `NM_000477.7`, human origin, and positive-strand 42..1871. Check 1830 bp and the complete-CDS checks, then confirm and continue.
3. Expression cassette: use User sequence for CaMV 35S and NOS, add no optional components, confirm promoter → ALB → terminator order and orientation, and generate the 2918 bp expression cassette.
4. Backbone: catalog Select failure is a known limitation. When use is permitted, upload authentic `AF234296.1.gb` and check 8958 bp, circular topology, and fixed forward `27|28` insertion boundary.
5. Complete construct: check inputs and boundary, click Generate full vector, and inspect the 11876 bp circular result and map.
6. Results and export: save the project; download expression cassette FASTA, full plasmid FASTA/GenBank, and JSON backup separately. Reopen and check identity and sequences. Frozen formal reports remain blocked and editing restoration is limited. See User Manual Chapters 4–12 for actual button names and screenshots.

## 4. Computational results

| Object | Length and result | Nucleotide SHA-256 |
| --- | --- | --- |
| Expression cassette | 835 + 1830 + 253 = 2918 bp | `8422558a6f117fb27debb3fc96ad3b954e22de904c0e48fe7eece447413bac7f` |
| Full plasmid | 8958 + 2918 = 11876 bp; circular; historical GenBank has 20 features | `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c` |

Reconstruction uses `backbone[:27] + cassette + backbone[27:]`: forward insertion between original backbone bases 27 and 28. Computational results of 0 blockers and 0 warnings do not establish complete provenance or experimental function.

## 5. Sequence-level reproduction and verification

Download three versioned records using Appendix A and retain the responses and file-byte hashes. Use Appendix B to check identity, coordinates, strand, CDS translation, and four input nucleotide hashes; then compare the expression cassette and fixed-boundary reconstruction. Normalize nucleotides to uppercase with whitespace removed. FASTA headers and GenBank annotations are excluded from nucleotide hashes. Stop on any difference; do not edit original sequences to force agreement.

### 5.1 Independent checks of actual exported files

After downloading files from the software, open PowerShell in their directory. The short command below reads one FASTA record and prints nucleotide length and hash. Substitute the actual filename and run separately for expression cassette FASTA and full plasmid FASTA, comparing against their expected values. Repeat before and after reopening the project.

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

Read full plasmid GenBank separately with the following command. Historical expectations are 11876 bp, the same full nucleotide hash, circular topology, and 20 features.

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

Agreement of sequence hash, topology, and feature count alone does not establish the correctness of every annotation. Complete annotations and qualifiers require separate item-by-item comparison; this public edition does not claim that revalidation passed.

## 6. Verified scope and limitations

Enter promoter → ALB CDS → NOS terminator as in User Manual Chapters 6–9; confirm forward arrangement before generating the expression cassette. Use `Upload GenBank file` in Step 4 for the backbone and confirm `AF234296.1`, 8958 bp, circular topology, and fixed forward `27|28` boundary. Do not bypass catalog `Select` failure by renaming files or changing coordinates.

The existing reproduction record checked three source records, four inputs, the 2918 bp expression cassette, and the 11876 bp **sequence-level reconstruction** at the fixed boundary. The following remained **NOT_PROVEN** in the original integration round: character-for-character agreement of exports after rerunning the frozen software locally; all 20 full plasmid GenBank features, qualifiers, and annotation fingerprints; complete revalidation of saving, reopening, and downloads; and report generation. Sequence-level reconstruction must therefore not be described as “full plasmid software export passed.”

The original candidate integrated documentation. Screenshot remediation R2 performed limited reopening and download checks in an isolated copy of the same frozen commit. Independent download and sequence reconstruction on 2026-10-09 are existing records in the original guide. The original integration round did not rerun software export, save and reopen, or complete GenBank annotation validation. Historical R5 operations and untested items must remain separated by date, version, and scope; NOT_PROVEN is not upgraded to passed.

See [LICENSE_MANUAL.md](LICENSE_MANUAL.md) for licensing and distribution. Historical `case_input_helper.py` is not distributed. Public database access does not imply confirmation of all third-party rights.

### 6.1 Limited actual checks in screenshot remediation R2

On 2026-10-09, an isolated running copy of the frozen commit opened a copy of the historical R5 ALB database and downloaded expression cassette FASTA, full plasmid FASTA, full plasmid GenBank, and project JSON. UTF-8 parsing confirmed 2918 bp for the cassette and 11876 bp for the full plasmid; nucleotide hashes matched Section 4. GenBank was circular with 20 features. Native map PNG download produced a complete-label 3000×2000 image. Download files and complete sequences remained in the private work area and are not distributed in this public edition.

This check does not establish new generation, actual upload, new saving, complete GenBank qualifier agreement, JSON disaster recovery, or report download in that round. The preceding NOT_PROVEN record belongs to the original integration round; only the explicitly listed downloads and sequence identity obtained additional evidence. Other items were not upgraded. Empty Step 2 fields and historical read-only fallback were observed and retained.

## 7. Reproduction commands and detailed-data appendices

Commands apply to Windows PowerShell 7 (UTF-8 pipeline), CPython 3.12, and Biopython. Use a separate reproduction environment; do not temporarily add packages to the frozen software environment. Markdown code blocks are the execution source. PDF code preserves the same characters and indentation, but check line breaks when copying whole blocks.

Executable blocks are unchanged from R4, including Chinese diagnostics. No new sequence retrieval, software run, or biological experiment was performed for this English translation.

### Appendix A. Downloading, saving, and file hashes

Requirements: Windows x64, PowerShell 7 (UTF-8 pipeline), CPython 3.12, and Biopython (`python -m pip install biopython`). Run in a new directory:

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path .\case-inputs | Out-Null
$base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id={0}&rettype=gb&retmode=text'
foreach ($a in @('NM_000477.7','AF485783.1','AF234296.1')) {
  Invoke-WebRequest -Uri ($base -f $a) -OutFile (Join-Path .\case-inputs ($a + '.gb'))
}
Get-FileHash .\case-inputs\*.gb -Algorithm SHA256 | Format-Table Path,Hash
```

File-byte hashes and nucleotide hashes are different fingerprints and must be recorded separately. Changes in NCBI response annotations, line endings, or dates can change file-byte hashes. Do not edit responses to match historical bytes.

R4 supplies commands for recording file-byte hashes but does not publish numeric historical GenBank file-byte hashes in the three source documents. None is invented or substituted in this edition.

### Appendix B. Extraction and nucleotide-hash verification

The following temporary code runs once from standard input. It reads three versioned GenBank files from the `case-inputs` directory, selects an explicit feature, extracts by coordinates, and prints lengths and nucleotide SHA-256. It does not access project source, audit databases, or internal files and does not generate a full plasmid attachment.

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

Expected results: expression cassette `2918` bp, nucleotide hash `8422558a6f117fb27debb3fc96ad3b954e22de904c0e48fe7eece447413bac7f`; fixed forward-boundary reconstruction using `backbone[:27] + cassette + backbone[27:]`, `11876` bp, nucleotide hash `26399b187adc487ac7cdc2f56bf260a35175f8970f29de6349cd99ceecc1667c`. The source guide records actual independent NCBI retrieval and verification with the Biopython-based code above on 2026-10-09.

Compare every actual length and hash against Section 2 and both assembled values above. Stop on any mismatch; do not alter sequences to pass. Paste generated `ALB.fasta`, `35S.fasta`, and `NOS.fasta` into the user sequence fields in User Manual Chapters 6–7. Headers and line breaks are excluded from nucleotide hashes. Upload the original GenBank record for the vector backbone.

