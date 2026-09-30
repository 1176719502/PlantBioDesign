# MT-01 reviewer material

- Construct: pGrDL_SP deterministic region
- Accession: `KX758647.1`
- Source coordinates: 571–4649, 1-based inclusive
- Expected canonical length: 4079 bp
- Expected canonical DNA SHA-256: `1847b411bd0592e0927db433bfc88f8eec3a9f8c30620af97aba5dae465c3104`

The `contracts/` directory is copied byte-for-byte from the frozen commit. An existing external frozen runtime export was inspected on the build host and its FASTA- and GenBank-derived sequences both matched the authoritative 4079 bp DNA hash. Those bytes were not copied into this package because `contracts/redistribution_contract.json` prohibits bundling the complete extracted region and derived sequence files.

See `CANONICAL_FASTA_NOT_INCLUDED.md` and `GENBANK_NOT_INCLUDED.md`.

