# Actual combined Intl Cargo baseline

`data.tar.gz` losslessly retains 174 UTF-8 payloads: both plans, source-input hash
ledgers, untrusted seeds and old locks; the final actual lock; the six direct
dependency manifests and two patch manifests; all four phase folders; complete
Cargo stdout/stderr; Root authorities/configs/audits; and all 76 vendor checksum
manifests. Historical caller/helper code is retained as DATA, never imported by
the reader. Registry/vendor Rust source payloads and tool binaries are not copied.

The original outcome remains visible:

| Actual command | Cargo exit | Wrapper exit | Original result |
| --- | ---: | ---: | --- |
| V1 online metadata | 101 | 1 | Failed; Smallvec lock conflict |
| V2 online metadata | 0 | 0 | Passed |
| V2 locked vendor | 0 | 0 | Passed |
| V2 offline locked metadata | 0 | 0 | Passed |

All four phases record completed owned cleanup and 2,296 unchanged selected
original/copied source files. V1 lacks the newer worker/status descriptor fields;
its preserved direct files and exit values are checked without retrofitting that
schema. Its original 660-second operational budget included an extra 60 seconds;
V2's 600/600/300 seconds include worker startup, with cleanup additional. V1's
known exceptional-collector final-check gap is not erased: the actual Cargo101
returned normally and did retain successful final source protection.

The actual final lock is
`dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61`,
20,626 bytes. Its 84 packages preserve all 49 old name/version/source identities
and checksums, adding 35. The ten explicit shared-family reconciliations select
the old versions rather than silently choosing newer compatible releases. Both
untrusted seed locks remain distinguishable from this actual Cargo-resolved lock.

The online/offline logical dependency graphs and feature sets match after
normalizing only root-dependent path package IDs. The root requests one static
Rust aggregate with exactly four existing and two Intl direct dependencies.
`icu_capi` disables default features and selects exactly `any_provider`,
`compiled_data`, `segmenter` and `calendar`. This is manifest/metadata evidence,
not proof that a new archive or single Rust standard library has linked.

All 76 external packages' 2,278 source files (35,510,599 bytes), plus their 76
checksum manifests, match the already-retained 2,354-row hash ledger. Curation
rehashed those actual files and the selected original/copied source inputs before
and after reading. Each retained checksum manifest joins that ledger and the
actual lock. Mozilla/Git Unicode-bidi's parsed manifests and Rust source hashes
also match. No vendor source bodies are duplicated here.

`references.json` binds the adjacent old-feature-control index, authority/ledger
and DATA reconciliation, plus the unchanged 26/99 Source-test records, test code
and exact FFI-source manifest. Their existing payloads are not recopied. The
feature control reports three widened old feature sets: Serde gains
`derive/serde_derive`, Smallvec gains `union`, and Syn gains `full`.
`serde_derive@1.0.218` is newly selected in metadata despite already being in the
old lock. All failed collector results and original raw data remain unchanged.

Run from this directory, retaining output outside the indexed family:

```sh
python3.12 -B check.py
```

The checker needs the adjacent referenced files in the same repository layout;
it uses relative paths rather than the original machine's absolute paths for
retained DATA. It does not execute Cargo, the historical helper/caller, a compiler
or a guest. Actual metadata processes included Rustc queries; no claim that no
compiler executable appeared is made. Protection covers selected files and
recorded bookends, not an OS sandbox or whole-filesystem immutability.

The successful DATA reconciliation does not turn the first failed command into a
pass. It does not accept an Intl compile, engine relink, guest runtime, profile or
full Next.js execution. The reviewer authored the resolver sources, operated the
separate old-four metadata control, and did not operate these original four
Root-controlled Cargo phases.
