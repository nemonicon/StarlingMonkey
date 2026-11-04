# Production GC-OFF engine: independent artifact verification

This packet verifies the actual Release-GC production engine `502320aa…`,
9,760,842 bytes, metadata `5810e9d0…`, immutable receipt `8629f1cd…`. It proves
artifact/source provenance, not guest compatibility or GC-root isolation.

All335 GC frozen copies,306 source/build inputs, external3, native61/strict4/
queue1 and separate after-build Ninja embedding1 are verified from frozen views.
Actual Buffer.cpp and exactly four other expected native commands carry the GC
macro. Entropy policy is1 on all62 native/embedding commands; runtime entropy
and OOM macros are absent. No before-build Ninja witness is invented.

The GC launch's prerequisite binds prior normal-OFF receipt `86b5d78c…` and
engine `6e5bc2ca…` before its shared project was reconfigured. The independent
reader rehashes all335 normal-OFF frozen copies and verifies that frozen cache
still selects GC=OFF. It never reads the original normal/GC project cache or
native database. Both prior independent normal and RuntimeOnly packets remain
unchanged. The zero-status16-step incremental build and freezer evidence are
bound as recorded provenance, not rerun.

Pinned host Node runs only the exact original finite metadata/source helper
against the frozen GC sidecar/source; eight manifests and corem0.11 must match.
Locked Rust, four OpenSSL evidence files, attribution7, adapter and code copies
are rehashed. OpenSSL4650-file completeness is preserved audit evidence rather
than a fresh re-audit; the referenced original libcrypto archive is not read.

No native build, compiler, linker, Ninja, componentizer, adapter, Wasmtime or
Wasm guest executes here. Actual reviewed pins remain null. Full guest,
GC-ownership, release/focused/HTTP gates and explicit activation remain pending.
No reset/ALS/request cleanup/public process, first-classic, memory or performance
claim follows. [results.json](results.json), [selector-command.json](selector-command.json)
and [verify.py](verify.py) record the exact evidence and limits.
