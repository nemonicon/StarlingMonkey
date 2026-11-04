# Independent classic342 normal-OFF native proof

The new actual normal-OFF freeze passes this independent reader: **405 frozen
copies, native342/external3, native61/strict4/private5 and separate embedding1**.
All 601 consumed paths were hashed and checked again before publication.
The exact engine is `b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4`,
9,973,535 bytes. The result is
[normal-off-v1/results.json](normal-off-v1/results.json), with raw process status,
command/stdout/stderr beside it. The reader checks Root's external SHA-pinned
actual-anchor file; this directory's default `actual-pins.json` stays null.
It does not install or activate consumer pins.

This is native artifact evidence. **No compiler, Ninja, freezer, componentizer,
Wasm guest or target host was executed by this verification.** Recorded finite
source admission is read/rehashed rather than rerun. The existing complete
OpenSSL before/after source audit is reconciled with frozen receipts and the
actual linked archive; its original 4,650 source files are not reread here.
No component imports, exports, stream semantics, GC safety, reset/reuse, ALS,
target-host behavior, size advantage or performance is established.

The [first attempt](history/attempt1/failure.json) preserved the original sealed
reader and exact captured traceback. It failed a **reader assumption**, after
the native61 checks: the parent embedding command has O3/NDEBUG and
`--target=wasm32-wasi`, but no `-flto=thin`. The earlier combined assertion
mistakenly imposed native-target ThinLTO on that separate parent target.
The target flag is present; its absence was not the cause. No native failure
or source/configuration/artifact change occurred.

[reader-amendment.diff](reader-amendment.diff) changes exactly three expressions:
an optional `require_thin_lto=True` parameter, a separate target/conditional
ThinLTO check, and `False` only at the embedding call. Native61 still requires
ThinLTO; the embedding still requires wasm32-wasi/O3/NDEBUG, the same source
operand and all strict/entropy/private-macro checks. Four additional pure
host test groups check that narrow correction and exact source delta. The
[original preparation seal](../independent-native-verification-v1/index.json)
and all eight original indexed files remain unchanged.

Only frozen label-specific normal-OFF cache/database files are read, so later
shared-project GC reconfiguration does not affect this proof. No mutable
original normal-OFF cache/database path was dereferenced. Other label proofs
are still pending separate actual anchors and explicit execution.
