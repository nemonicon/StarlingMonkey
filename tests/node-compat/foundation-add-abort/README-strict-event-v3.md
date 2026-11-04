# Strict callback v3: private Release validation

The [v3 native patch](strict-event-v3.patch) closes the direct-finalizer and dispatch-getter counterexamples preserved in [v2](README-strict-event-v2.md). It retains the same first-value root and the [v2 embedding boundary patch](componentize-strict-event-boundary-v2.patch). Root subsequently adopted the four exact native source files; the results here remain tied to the **private 293-input build with the earlier core profile**, not a fresh production/core-m0.8 build. The original v7/v1/v2 evidence remains unchanged.

| Verified v3 evidence | Result |
| --- | --- |
| [Actual SDK30/SM147 syntax](strict-event-v3-syntax-results.json) | Four C++ files × strict/macro-disabled: eight checks pass. The latter is syntax evidence, not an executed macro-disabled engine. |
| [Repeated initializer/synchronous export tests](strict-event-v3-results.json) | 16 initialization cases; three terminal exported values on Jco and Wasmtime; successful retained-instance controls. |
| [Runtime rejection boundary](runtime-v3-results.json) | Five fatal cases, including byte-identical v1 async counterexamples; four caught/late-handled controls, each with three retained Jco calls and fresh Wasmtime. |
| [Late binding](late-binding-v3-acceptance-results.json) | Six valid exported-interface getter cases: three reject and three accept, including a rejection handled in a later microtask. |
| [Finalizer/getter/cleanup tests](callback-v3-results.json) | Eight initializer failures reject; five controls each pass three retained Jco calls and fresh Wasmtime. |
| [v3-specific Release moving GC](strict-event-v3-gc-results.json) | Eight native hex round trips preserve a latched thrown object; clean three-call reuse and fresh Wasmtime pass; fatal deployed object fails on both hosts. |

All accepted final components have **zero imports**. These are actual Jco1.40 and stock Wasmtime42.0.1 executions. The native profile still does not implement `events.addAbortListener` or claim Node EventTarget/process compatibility. Uncaught failures use a selected-profile **fatal/discard** policy after the current jobs/finalizers drain; a failed component is never reused. Standard diagnostic output is optional: import-free fatal calls expose a trap rather than a host JavaScript error-property channel.

## What v3 changes

Under `NODE_COMPAT_STRICT_INITIALIZATION`, a directly thrown FinalizationRegistry cleanup exception enters the same traced first-value latch before any reporting/clearing. Invocation failure without a pending exception sets the existing terminal flag. Explicit catches inside cleanup callbacks still succeed. No scheduler, collection-order or request-teardown equivalence is claimed.

A throwing object listener's `handleEvent` getter now follows the same callback capture/clear path as invocation errors. Dispatch continues, so a catch around `dispatchEvent` cannot swallow the error, and later listeners run. A primitive `undefined` remains distinguishable from no captured error. Tests preserve a first thrown object's ordinary observable behavior when a later finalizer error occurs.

Strict-only `mozilla::MakeScopeExit` guards clear passive state and compact removed once-listener entries on every exit from the invocation loop. The target is held by `JS::RootedObject`; the guard runs before that root is destroyed. Propagation stopping leaves through cleanup. Re-adding a removed listener copies its owning RefPtr before erasing the invalidated iterator. Both new-listener and re-add appends now check their fallible result and report allocation failure. These failure branches are source-reviewed, **not fault-injected**.

The old iterator path was never executed by the new re-add tests. Only the reviewed corrected v3 engine runs ordinary re-add, nested re-add and stop/re-add controls. Getter tests also verify later-listener execution, once behavior, passive reset and restored public `currentTarget` state. This proves the stated observable paths, not prompt reclamation of every event/abort resource.

## Moving-GC evidence belongs to v3

The v3 ordinary Release configuration was copied and matched its recorded CMake/compile-command hashes before reconfiguring the same private project with existing `NODE_COMPAT_GC_STRESS=ON`. Native sources and embedding bytes at source level remain identical; the actual Buffer compile command must contain the GC flag. The ordinary artifact is preserved separately.

The initializer throws a fresh ordinary object with no application variable binding, then performs eight supported Buffer hex round trips at existing rooted-boundary Shrink collections. Its ordinary `toString` subsequently reports `ROOTED_EVENT_AFTER_8` when initialization fails. The clean control performs its eight operations **inside** listener dispatch, exercising the temporary target root and cleanup guards across collection. A separately built deployed fatal fixture is discarded after failure. No DEBUG, OOM simulation, private GC metadata, raw memory or malformed ABI carrier is involved.

## Exact sources and reproduction

Use [build-strict-event-v3.sh](build-strict-event-v3.sh), then the four ordinary v3 runners and [the separate GC runner](run-strict-event-gc-v3.mjs). The [private recipe transformation](build-recipe-strict-event-v3.patch) retains frozen v7's dependency pins, aggregate Cargo lock enforcement, complete OpenSSL source audit, actual CMake flags and before/after source checks. It adds the same fourth guest embedding patch as v2. There is no new host service, WASI import, SpiderMonkey source build or host modification.

| Item | SHA-256 |
| --- | --- |
| Private ordinary engine, 9,729,505 bytes | `8594fe89fb7048cca5feed57fe073d4040a5f0636fabddb6721df463202c905a` |
| Private Release + GC stress engine | `62c309fbb6e778198ec32b2458edc0f3dedd22cb91c021f8adb44f4e24174146` |
| Native patch | `9b2e54c9527a5c078221ad49f67f7354c9fb1df00eb99f0720b3d7874402603a` |
| Embedding patch (unchanged v2) | `84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2` |
| Compiled embedding source | `9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977` |

Raw artifacts/logs are under `/tmp/starling-node-compat/strict-event-v3/`; immutable copies are `release-freeze/` and `gc-freeze/`. Both include exact source/configuration receipts. These private components use the pinned v2 componentizer, Node22.14.0, repo Preview1 adapter and an explicitly capability-free WIT world. Choose the corresponding engine/source root and a fresh output folder using the environment variables documented for v1. `NODE_COMPAT_GC_STRESS=1` selects the separate GC artifact; it never overwrites the ordinary engine.

## Boundaries still open

Registration-time getter reads remain an explicit measured difference: Node reads `handleEvent` when registering an object listener; Starling does not. Function-listener receiver differences, other object-listener semantics, protected abort listeners, full Node process handlers/nextTick/async-hooks semantics, cross-realm execution and general request/resource teardown remain outside this change. Capture/invocation/append failure execution and explicit `Engine::reset` remain untested. A value-only latch does not retain the separate optional exception stack.

The [production recipe review](production-recipe-review-v3.json) verifies source/recipe adoption guards only. Fresh combined production engines and their module/entropy/HTTP/host gates are required independently; these private proofs and v1's earlier GC results are not transferred to them automatically.
