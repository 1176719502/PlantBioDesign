# Reproducibility guide

## 1. Start the frozen software

Use CPython 3.12 on Windows x64. Install `software/requirements-runtime.lock` with `--require-hashes`, set writable database/pydna paths outside the package, and launch `software/app.py` on isolated port 8632 as shown in `README.md`.

The build-host smoke check uses the same entry point and port. A successful HTTP response confirms startup only; it does not establish complete browser workflow acceptance or biological validation.

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

