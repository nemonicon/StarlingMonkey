# Adapter provenance and rewriting prerequisites

Static metadata/source findings only; no build, pruning or runtime admission.
The selected 53,512-byte repository adapter hashes to
`988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0`.
Its last binary-changing commit is234d7c449508f21f4f16e08db0d2609094e10eca
(2024-10-01). Host API0.2.10 selects it through the0.2.0 directory. Producer
metadata identifies Rust1.80.0, without establishing a source revision.

The official [Wasmtime v25.0.0 release](https://github.com/bytecodealliance/wasmtime/releases/tag/v25.0.0)
has an equal-sized reactor adapter, SHA256
`240c28b2561e2d32daef30112bb2aaeb6427976de731401b806d7e32a1a27326`.
It is not byte-identical. Type/function/table/global/export/producer/target-feature
sections match; imports, code, component-type metadata and names differ. There
are133 differing byte positions in the equal-length code payloads; that count
does not establish different runtime semantics. Global P2-version string
replacement does not make the modules equal. Exact source provenance remains
unresolved.

Pinned [v25 source](https://github.com/bytecodealliance/wasmtime/blob/0b195ef5db76c02fb5392ec1418c58bdc5537d41/crates/wasi-preview1-component-adapter/src/lib.rs)
and [diagnostic macros](https://github.com/bytecodealliance/wasmtime/blob/0b195ef5db76c02fb5392ec1418c58bdc5537d41/crates/wasi-preview1-component-adapter/src/macros.rs)
are explanatory, not a claimed derivation. The macros use stderr/stream bindings
before trapping. Existing component graph evidence separately proves retained
bindings, without proving internal branch reachability for this binary.

Both complete adapters import env.memory first, then63 functions. The selected
wirm5.0.0 replacement path and engine-oriented splicer cast import-entry IDs
to function IDs. This adapter violates that precondition. Four inspected source
files match the registry archive, whose SHA matches Cargo.lock. An initial
checker expected an absent .cargo-checksum.json; the corrected check authenticates
the actual .crate archive and compares its members.

The [uncompiled proposal](../clock-io-pruning-candidate-v1/source-derivation.json)
uses the existing binary as an explicit input, with checked import-order
normalization and a narrow pruning entry that avoids engine random/realloc
assumptions. Separate [design notes](../clock-io-pruning-design-review-v1/results.json)
corroborate those hazards without approving the final candidate or execution.

inspect.py reads bounded section/import metadata and hashes payloads; it decodes
no instruction bodies or memory contents and compiles/instantiates nothing.
It is not a general Wasm validator. The public release download stays at its
recorded /private/tmp path. No original adapter or installed package/host changes.
