# Independent classic342 GC-OFF native proof

The actual **gc-off** freeze passes the byte-identical amended reader from
[normal-OFF](../independent-native-verification-v2/README.md) and
[RuntimeOnly](../independent-native-verification-v3/README.md): 405 frozen
copies, native342/external3, native61/strict4/private5 and separate embedding1.
All 604 consumed paths were rehashed before publication, including the three
separately anchored prior normal-OFF files. The reader exited zero with empty
stderr; command, stdout, stderr and status accompany
[gc-off-v1/results.json](gc-off-v1/results.json).

The engine is
`f9f48f4f8351654a2f2859eeda944ed144ba5c334f914b7f09bec14b0a5e4236`,
9,975,084 bytes. Root's external `native-input-anchors-v3.json` was checked
against SHA `a6bab7d0ff451bbc1891a439694f16721178dfdbd0edd999ec0771960e2abf07`.
Engine/metadata/freeze/launcher digests match those anchors. CLASSIC=1 and
GC_STRESS=1 occur on exactly the five existing private C++ targets; both are
absent from the separate embedding command. Entropy policy is OFF and the
RuntimeOnly definition is absent from all 61 native commands and embedding.
Native ThinLTO stays required; the parent embedding retains its actual
wasm32-wasi/O3/NDEBUG contract without a ThinLTO requirement.

The launcher's `normalOffFrozenBeforeGCReconfigure` path, receipt digest and
engine digest match independent normal-OFF anchors. That frozen receipt,
engine and original sidecar were rehashed. No mutable original normal-OFF
cache/database was read after the shared project was reconfigured for GC.
All current configuration/command checks likewise use label-specific frozen
copies. Existing locked Rust evidence, OpenSSL source-audit receipts and
configuration, linked libcrypto, licenses, adapter, tools and recorded finite
source admission were reconciled. The source admission and original 4,650
OpenSSL source-file audit are not re-executed.

**This proves selection and preservation of a GC-enabled native artifact, not
execution of a collection or GC safety.** No compiler, Ninja, freezer,
componentizer, Wasm guest or target host ran in this verification. No stream
semantics, imports/exports, GC root isolation, reset/reuse, ALS, host behavior,
size advantage or performance is established. Consumer pins remain unchanged.
All earlier proof packets and their indexed files remain unchanged; this new
sibling contains only the GC-OFF proof and the same reader bytes.
