# Canonical FASTA not included

The requested MT-01 canonical FASTA is not included. The frozen redistribution contract classifies the case as `ACCESSION_AND_REPRODUCIBLE_EXTRACTION_ONLY` and sets `complete_extracted_region_allowed` to `false`. Including a 4079 bp FASTA would override the frozen policy and would no longer be a strict snapshot.

Reproduce it from exact accession `KX758647.1` using source slice `[570:4649]`, then require length 4079 and DNA SHA-256 `1847b411bd0592e0927db433bfc88f8eec3a9f8c30620af97aba5dae465c3104`.

