# Production v8 OFF strict callback validation

The combined production v8 OFF engine passes the four separately versioned strict callback suites on Jco1.40 and stock Wasmtime42.0.1. This is **new execution evidence** for core `sm-node-22.14.0-m0.8` and the adopted strict-callback v3 code. It does not reuse a private-v3 result as a production claim. All private v1/v2/v3 code, reports and receipts remain unchanged.

| Production result | Actual checks |
| --- | --- |
| [Initialization/synchronous exports](production-v8-sync-results.json) | 16 initializer cases (13 reject, three handled controls succeed); three terminal exported values fail on both hosts; successful retained dispatch control. |
| [Runtime async boundary](production-v8-runtime-results.json) | Five fatal cases on both hosts; four caught/late-handler controls each pass three retained Jco calls and fresh Wasmtime. Two fatal source strings are unchanged from the original v1 counterexamples. |
| [Post-binding getters](production-v8-late-results.json) | Six valid exported-interface getter cases; three reject, three accept. A rejection handled by a later microtask remains accepted. |
| [Finalizer/getter/cleanup](production-v8-callback-results.json) | Eight initializer errors reject; five controls each pass three retained Jco calls and fresh Wasmtime. Includes primitive finalizer errors, first-value retention, getter continuation/passive/once cleanup and corrected-engine re-add. |

There are 24 valid emitted components, 24 expected componentization rejections, 50 Jco export calls and 24 fresh Wasmtime invocations. Eight fatal exported-component instances per host are discarded. Every emitted component has **zero imports**; no custom service or host modification is involved. These are ordinary Release tests, not DEBUG, OOM/fault, private memory or malformed-carrier experiments.

## Exact admission and source provenance

The [read-only preflight](production-v8-preflight.mjs) pins engine SHA-256 `e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9` (9,724,864 bytes) and receipt SHA-256 `857dde83661919ac0c494b17be1cfd7bb2d5b4724067b6cffb433b7c252d9dad`. It verifies all 293 frozen inputs, the actual core-m0.8 manifest, four native source hashes, native patch `9b2e54c9…`, embedding patch `84a91c1f…`, compiled embedding source `9a7c30ba…`, recipe `af5b0e8c…`, actual strict macros in three native TUs plus the embedding, and immutable CMake/compile-command copies. It requires ordinary OFF/Release, all six selected foundations, debugger/WPT/GC/OOM OFF, and locked Rust metadata. It does not require private recipe/base-receipt fields absent from the production receipt.

The [source receipt](production-v8-source-receipt.json) and `production-v8-source-freeze/` captured all four new runners, preflight and helper hashes **before any component execution**. Each actual result carries a fresh preflight record and the runner digest. [The final evidence receipt](production-v8-evidence-receipt.json) rechecks these against the frozen copies and records all final component hashes.

The engine/source/configuration are under `/tmp/starling-node-compat/foundations-v8/native-freeze/`. Run the four `run-production-v8-*.mjs` scripts with explicit OFF `NODE_COMPAT_ENGINE`, matching `NODE_COMPAT_ENGINE_SOURCE_ROOT`, pinned npm toolchain, v2 componentizer, Wasmtime42 and fresh `NODE_COMPAT_STRICT_EVENT_OUTPUT` directories. The executed output folders are `strict-sync/`, `strict-runtime/`, `strict-late/` and `strict-callbacks/` within `foundations-v8`, with adjacent logs. New report filenames preserve the private evidence.

## Compatibility limits

The selected guest policy makes uncaught callback errors or unhandled rejections fatal at the drained export boundary; discard failed instances. It is not full Node process handlers, nextTick or async-hooks behavior. Import-free fatal calls expose a trap rather than a JavaScript error-property channel to the host. User catches and handlers attached during the current microtask turn are tested and remain effective.

Registration getter timing remains explicitly different from Node22 and is asserted as a deviation. Function-listener receiver parity, other EventTarget semantics, protected `addAbortListener`, explicit reset, cross-realm execution and general request/resource teardown are outside this result. Allocation/capture/invocation failure branches remain source-reviewed only. The separate private-v3 moving-GC proof is not transferred to this production artifact; no production-v8 GC, Runtime-only capability variant, HTTP/wasmCloud or performance result is claimed by these four OFF suites.
