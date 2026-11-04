# Private strict callback candidate v2 — not promoted

V2 adds a selected-profile fatal check for unhandled Promise rejections after deployed jobs/finalizers drain and before the export result is returned or marshalled. It also retains an internal failed-invocation flag when a native callback reports false without a pending exception. The original [v1 proof](README-strict-event.md), v7 and their reports are unchanged. No shared production file or host runtime is modified.

The [combined native patch](strict-event-v2.patch) still changes only four v7 files; compared with v1, three files change. The [combined embedding patch](componentize-strict-event-boundary-v2.patch) contains v1's final export-binding checkpoint plus the new deployed boundary. `NODE_COMPAT_STRICT_INITIALIZATION` guards both; macro-disabled code retains the old policy. [Eight actual SDK30/SM147 syntax checks](strict-event-v2-syntax-results.json) cover all four C++ files with the macro both enabled and disabled.

| Evidence | Actual result |
| --- | --- |
| [Repeated synchronous/initialization suite](strict-event-v2-results.json) | 16 initializer cases pass; three fatal deployed values reject on Jco and fresh Wasmtime; handled deployed events survive three retained calls plus a fresh invocation. |
| [Runtime boundary suite](runtime-v2-results.json) | Five fatal cases reject on both hosts. Two are byte-identical to v1's accepted async counterexamples. Four caught/late-handled controls survive three retained Jco calls and fresh Wasmtime each. |
| [Export-binding suite](late-binding-v2-acceptance-results.json) | All six cases pass, including a rejection handled by a later microtask. |
| [Node callback oracle](node-callback-oracle-results.json) | Three public Node22 cases pass; isolated `uncaughtException` handlers observe dispatch/finalizer reporting, with documented `--expose-gc` only to schedule the reference finalizer. |
| [Remaining guest counterexamples](callback-counterexamples-v2-results.json) | **Three differences remain**, including direct FinalizationRegistry unsupported operations being swallowed during componentization. These block promotion as complete strict initialization. |

All accepted components have zero emitted imports and execute through ordinary WIT string exports in Jco1.40 and stock Wasmtime42.0.1. The runtime error marker `ERR_SM_NODE_EXECUTION_REJECTION` is defined in the guest source. Import-free fatal calls expose a terminal trap, not a JavaScript error-property channel to the host; the reporting message is available only when an appropriate standard diagnostic interface is selected. This is a bounded fatal/discard profile policy, not `process.on`, `unhandledRejection`, nextTick ordering or complete Node process semantics. A failed instance is never reused.

The new invocation-failure state has no JS edge; the existing first-value root remains. Direct pending exceptions retain precedence, a later callback cannot overwrite the first captured event value, and explicit reset clears the flags. Invocation/capture failure execution, explicit reset, cross-realm behavior and broader teardown are source-reviewed only. No v2 GC engine was run; v1's moving-GC result remains explicitly scoped to v1. No DEBUG/fault or private memory observation is used.

## Counterexamples requiring the next reviewed patch

The guest direct FinalizationRegistry callback increments `seen` then calls unsupported `child_process.spawn()`. The existing finalizer reporter dumps and clears it, so componentization still succeeds and both hosts report `seen:1`. The corresponding Node reference uses an ordinary sentinel Error and observes public uncaught-exception reporting; error-code equivalence is not claimed.

Object-listener getter timing is independently different: Node reads `handleEvent` during registration, while Starling accepts the object without reading it. For an armed getter that throws only during dispatch, Node's async wrapper continues to the second listener and reports the error separately. Starling currently throws to the dispatch caller and skips the second listener. An outer caller catch therefore suppresses that error in the guest. The registration timing difference is separately deferred; fixing dispatch exception capture must not be presented as complete Node EventTarget parity.

The removed-once-listener re-add branch also dereferences its iterator after erasing it. This is a source finding only: **the known-invalid old path was not executed**. The separately reviewed v3 proposal will copy the owning RefPtr before erasing and will test ordinary re-add only on a new corrected engine.

## Reproducible isolated build

Use [build-strict-event-v2.sh](build-strict-event-v2.sh). Its [private recipe transformation](build-recipe-strict-event-v2.patch) preserves frozen v7's 293 input paths, exact dependencies, locked Cargo, all OpenSSL source audits and actual configuration receipts. It adds only the pinned combined embedding patch. All work remains under `/tmp/starling-node-compat/strict-event-v2`; ordinary Release uses four jobs and the pinned prebuilt SM147, with no SpiderMonkey source build.

The engine SHA-256 is `5d40eaed51959e8b98b8119c30012b6501c248c04ce762ca4fe0745c1b7745e3`. The native patch is `b46e1dc9a054f872c45872504a28b399be0c19b3c631997efd4623c109f0611b`; the embedding patch is `84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2`, producing exact embedding source `9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977` over the previously pinned entry-patched source.

The immutable engine/source/configuration copy is `release-freeze/` within that directory. Test outputs are `release-tests/`, `runtime-tests/`, `late-tests/` and `callback-observations/`, with adjacent logs. Run the corresponding v2 scripts using the explicit engine/source root, pinned toolchain/v2 componentizer and Wasmtime environment variables documented for v1, selecting fresh output directories. The failure-observation runner intentionally asserts v2's differences and must remain unchanged after a future fix.
