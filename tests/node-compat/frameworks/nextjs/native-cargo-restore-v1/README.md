This is an inert plan and an explicit source-only restorer for the final 84-package
Cargo generation. It never runs Cargo, a compiler, network acquisition, a native
engine or a guest. Python 3.11+ is required; this does not change build Python 3.9.

From any checkout location, the default is read-only:

```sh
python3.12 -I -B tests/node-compat/frameworks/nextjs/native-cargo-restore-v1/restore.py --plan
```

The catalog authenticates the existing repo-relative Cargo text bundle, its exact
final `dc098f33` lock, 76 original checksum JSON files, the 2,354-file vendor ledger,
the 1,127-file four-tree FFI manifest and the 21-file base-crate manifest. It does
not use the earlier untrusted seed or historical Cargo metadata as a new proof.

Only a later authorized source stage should use `--donors CONFIG --output FRESH`.
`donors.example.json` is a null/unselected tree template. Its three roles must be
canonical already-owned paths. `baseRoot` contains the four `crates/rust-*`
prefixes, and `ffiRoot` contains all four Firefox-relative prefixes, including
`third_party/rust/unicode-bidi`. Neither role has a default private path.

The vendor role has exactly one of these shapes:

```json
{"kind":"tree","root":"/canonical/existing-vendor"}
```

```json
{"kind":"archives","root":"/canonical/already-owned-crate-archive-pool"}
```

Tree mode requires exact 76-package membership, checksums, directory membership
and ledger modes. Archive mode uses 75 fully identified registry name/version/
source tuples and their lock SHA256 values. It bounds gzip expansion before TAR
header parsing, rejects unsafe names, aliases, duplicates, links and specials,
then writes only exact checksum-listed file bytes. Safe surplus members are
recorded and discarded; dotfiles are not excluded indiscriminately. Original
checksum JSON bytes come from the authenticated text bundle. The exact 22-file
Mozilla FFI bidi subtree supplies Git-bidi, including its normalized Cargo.toml
and package:null checksum. A same-version registry crate cannot substitute.

The public static-crate URLs are fixed checksum-required acquisition recipes,
with availability explicitly unqueried. They are never fetched by this program.
The prospective Git archive has no acquired archive checksum and is not an
accepted input. No Cargo serializer, new resolution or checksum repair is used.

The fresh output contains `vendor`, `sources/base`, `sources/firefox`, `project`
and `offline-cargo`. All 3,502 source files total 47,153,823 bytes. Vendor files
retain the ledger's 2,351 modes0644 and three modes0755; its 420 child directories
are0755. Fresh base/FFI and generated files are0600, other private directories0700.
The base21 files are native-policy-source in this actual portable825 generation,
not build-support. Any later builder must join them to its complete selected
native/support map, retaining the existing435/387 roles.

Only the eight known project path values and the offline vendor directory value
change. Parsed non-path semantics, six root dependencies, empty workspace,
single Rust staticlib, the four explicit ICU CAPI features, and the Git revision
remain unchanged. The final lock bytes are copied exactly. Absolute new paths
are rendered at the fresh location; no historical absolute path is retargeted
inside old evidence.

This source stage has its own 512MiB start floor, 384MiB checks before/after each
payload copy, and 64MiB accepted logical output cap including its receipt. These
are boundary samples, not a continuous disk guard or measured memory/peak bound.
The final metadata receipt is written after payload/source bookends and counts
toward that cap; it does not include itself or root timestamps in its payload
physical inventory. Original FFI-fetch, browser and full-build floors remain
unchanged. No automatic cleanup or retry occurs. Partial output is retained on
failure, and the original process exit must accompany any receipt; a receipt
alone does not establish successful publication/fsync.

Donor files, modes, identities and selected directory membership are authenticated
before copying and again in finally. Fresh exclusive files have independent
physical records. The output's exact payload membership and modes are audited
before receipt publication. Unknown errors keep the stage failed. A failure
before output creation leaves no new source root; later failures retain their
partial root and failure receipt when publication is possible.

Even a successful source restore has `actualCargoMetadata`, `actualNativeBuild`,
`actualEngine` and `actualRuntime` set to null. New genuine offline/locked Cargo
metadata and full graph/features/edge comparison require separate reviewed Root
authority. Existing portable-builder V2 still pins old Intl roots; this restorer
does not silently replace that admission or claim a new compiled generation.

The exported read-only `admit_restore(receipt_ref)` accepts an explicit descriptor
`{path,sha256,bytes}`. It authenticates the producer family, exact succeeded
source-only receipt, all current payloads/directories/modes/physical identities,
root identity, rendered paths/lock and original donor/metadata bookends. It returns
fresh `intlLockfile`, `offlineCargoConfig`, `baseRoot`, `firefoxRoot`, `vendorRoot`
and physical records. Its `dataConsistent:true` result explicitly leaves actual
Cargo metadata null and `sourceProcessExecutionAttested:false`. A separate Root
must bind actual stage/process evidence; this reader cannot invent that proof.
The full real positive admission is pending an authorized actual source restore.

The tiny DATA tests exercise actual parser/renderer/admission functions with
owned fixture files and in-memory TAR bytes. They do not restore the real source
trees, invoke Cargo or simulate a successful Cargo result:

```sh
python3.12 -I -B tests/node-compat/frameworks/nextjs/native-cargo-restore-v1/test-restore.py
```
