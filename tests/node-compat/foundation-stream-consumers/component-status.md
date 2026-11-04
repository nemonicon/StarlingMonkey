# Isolated v7 consumer component results

The separate `metadata-v2/` candidate now passes an actual component gate over native TextDecoder. No `node:stream/consumers` module is registered or production-admitted, no production version is assigned, and no native source was edited. The earlier [source-only README](README.md), its prototype/oracles/source audit and [source index](index.json) are preserved as the earlier stage; this document records the additional component evidence.

[metadata-v2/component-results.json](metadata-v2/component-results.json) contains the full immutable v7 OFF engine receipt: SHA `ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09`, all 293 frozen source inputs, normal Release/no GC stress, and exact reviewed decoder SHA `4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c`. It uses Node22, locked Jco1.40/ComponentizeJS0.23 with the audited clock-v2 packager, the pinned adapter and stock Wasmtime42.0.1. The main component is `b0a39f73080e8018815b5ee84c1dd70126ed984d6d5c428b051a2a4c202291fc` (12,132,776 bytes, a test fixture artifact, not a performance measurement).

The main bundle imports only actual `node:buffer` for legitimate snapshot storage/brand/alias checks. The text/JSON implementation is explicitly the isolated JS facade over the actual native TextDecoder. It contains no native consumer namespace, Node/Jco/unenv stream adapter or JavaScript UTF8 kernel. Final WIT exports only `run() -> string` and imports nothing. The reflection-only auxiliary component also imports nothing.

## Executed checks and one explicit vector exclusion

* All 18 selected Node text/JSON groups pass in two calls of one retained Jco instance (`calls [1,2]`) and a fresh Wasmtime invocation (`call 1`). One invalid-input subgroup runs five of the frozen Node helper's six vectors: its `new Blob(['a'])` vector remains Node-only, because this gate prohibits native Blob invocation. [guest-oracle.mjs](guest-oracle.mjs) checks the original hash and makes only the listed removal/unused-code trimming; the full selection is retained in each report.
* All 12 policy groups pass for finite exports, coded deferred call/new behavior, default mutation, captures, 1MiB byte/string/output limits, 4096-chunk limit, iterator closing and error precedence. Profile resource errors are not OOM tests.
* Snapshot text, shared ordinary AB/view offsets and a genuine native Buffer survive resumption. The Buffer byte advances `[18,19]` in the retained instance and is `18` in a fresh host. Decoder final-flush state is not reused by a later call; invalid JSON does not contaminate a later valid parse. These are pure iterator cases, not request cancellation or host-resource ownership tests.
* Eleven application initialization cases fail predictably: call/new for all three deferred functions, awaited/unawaited/microtask invalid text input, malformed JSON and the input cap. Errors are exercised during componentization, not suppressed in a runtime wrapper.
* The actual engine reports `ReadableStream.prototype[Symbol.asyncIterator]`, `values` and `ReadableStream.from` as absent. No native Web reader/Blob stream or classic Stream input was constructed. Plain iterable success does not establish those unsupported input paths or Node nextTick/ALS scheduling semantics.

No native Blob constructor/prototype/method, hazardous getter, detached/shared/resizable lifetime, GC/OOM fault or other hazard probe ran. No HTTP/two-host deployment is part of this isolated scalar gate.

## Reflection finding and bounded factory fix

The first strict reflection check failed because SpiderMonkey's async function properties were materialized in application-read order: `name` then `length`, whereas Node returns own keys `length` then `name`. The [v1 diagnostic](reflection-v1/component-results.json) retains the full subsequent component/report with observed order and the other checks. [mismatch.json](reflection-v1/mismatch.json) preserves the strict error and explains that the initial failed artifact had already been replaced by that diagnostic before archiving. The diagnostic is explicitly not an exact Node reflection pass.

The separate [metadata-v2 factory](metadata-v2/create-module.mjs) captures `Object.getOwnPropertyDescriptor`, then resolves each supported function's `length` followed by `name` before exposing it. It defines no new function property and changes no algorithm, value or attribute. The original prototype is untouched. Metadata-v2 reinstates the exact Node own-key ordering assertion; it does not accept either order silently.

[reflection-results.json](metadata-v2/reflection-results.json) independently checks the same v2 factory in Node, retained Jco and fresh Wasmtime. It observes keys **before** requesting descriptors, so the probe cannot repair the order itself. Both functions have `length: 1` and their expected name, with writable/enumerable false and configurable true, exactly matching Node. The auxiliary run does not repeat the initialization suite.

## Remaining gates

Review the bounded optional contract and choose a production version/manifest before native registration. Real native namespace/aliases/static-CJS admission, optional-OFF rejection, request-associated lifecycle/cancellation and joint host deployment remain pending. Rolldown's `[object Module]` namespace wrapper is recorded as a bundler result, not evidence of a native Module Namespace Object.

The Blob-dependent `blob`, `arrayBuffer` and `buffer` functions remain explicit refusals. Their allocator/error/backing/identity/reader gates from the source audit remain open. Classic streams, Web reader adapters, Node task ordering and ALS remain deferred. No memory/throughput/size benefit is claimed.

`component-index.json` pins the new sources/reports and verifies the unchanged source/Node stage. The preserved v1 and v2 external artifacts are in separate output directories under `/tmp/starling-node-compat/stream-consumers-prototype-v7*`.
