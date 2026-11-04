# Independent classic342 RuntimeOnly native proof

The actual **normal-runtime** freeze passes the byte-identical amended reader
from [the normal-OFF proof](../independent-native-verification-v2/README.md):
405 frozen copies, native342/external3, native61/strict4/private5 and separate
embedding1. All 601 consumed paths were rehashed before publication. The reader
exited zero with empty stderr; command, stdout, stderr and status are preserved
beside [normal-runtime-v1/results.json](normal-runtime-v1/results.json).

The engine is
`1a3f4628d4f63445ec0c1a212a38f1eb3ac01fe22ea2d5d2d54f0210f388fd14`,
9,980,809 bytes. Root's separately reviewed `native-input-anchors-v2.json`
was checked against SHA
`9eb230f6e1c42db01fd256c877c28f0eb6dacb9a8c18349631a329754cc7c749`.
The metadata/freeze/launcher digests match those anchors. The selected entropy
policy is runtime-only, classic streams are enabled, and GC stress is false.
RuntimeOnly=1 is checked on all 61 actual native commands and the separate
embedding command; private CLASSIC=1 occurs on exactly five targets and the GC
definition is absent. Native ThinLTO remains required; parent embedding retains
its observed wasm32-wasi/O3/NDEBUG contract without a ThinLTO requirement.

All source/config/command/dependency checks use label-specific frozen copies.
The existing Rust lock evidence, OpenSSL 4,650-source before/after audit
receipts/configuration, linked libcrypto copy, licenses, adapter and tool
closure were reconciled and rehashed. The recorded finite source admission is
read/rehashed, not rerun. The 4,650 original OpenSSL source files are not reread.
No mutable original normal-OFF cache/database was accessed while GC reused it.

**No compiler, Ninja, freezer, componentizer, Wasm guest or target host was
executed.** Native verification does not establish emitted imports, stream
semantics, aliases/CJS behavior, GC safety, cancellation, reset/reuse, ALS,
host operation, size advantage or performance. Consumer pins were not changed.
The prior normal-OFF proof, its initial reader-assumption failure, and the
original preparation seal remain unchanged. This new sibling contains only
the RuntimeOnly proof and a byte-identical reader copy.
