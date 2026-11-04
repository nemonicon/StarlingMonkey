# Validation and outstanding decisions

This page preserves the **original audit's validation plan and evidence scope**.
Its uncompiled/pending descriptions below refer to that initial deliverable,
not the current worktree. Subsequent bounded native integration, GC, bundler,
import and both-host gates are recorded in the
[execution ledger](execution-status.md), the accepted
[v11 checkpoint](../../tests/node-compat/milestones/foundations-v11/README.md)
and [progress.md](../../progress.md). The newer scheduler has an ordinary
diagnostic component pass; GC and production acceptance remain pending.
Request reset/reuse and complete Node/Buffer compatibility remain unproved.

## Evidence boundaries

The exact Node oracle produced the namespace/API inventories and executed the bounded facade differential tests. The explicit child-process stub executes inside a real ComponentizeJS component on Wasmtime 42.0.1; [component test results](component-tests/results.json) record final imports, WIT, component hash, size, call/new checks, snapshot marker and repeated calls. Component tests use the released engine; they do not establish native registry integration in the audited checkout. Additional facade checks use a named reference JS hex kernel when stated, not the uncompiled C++ kernel.

The C++ templates, custom-engine build, target native module resolver/bundler path, GC stress, deployment environment/entropy/clock policies, request reuse and wasmCloud deployment remain required acceptance gates. Test failures or unexecuted gates cannot be converted into a support label. The current generated matrix is a proposed API disposition with explicit checkout-integration qualification.

## Executable checks supplied

```sh
/path/to/node-v22.14.0 docs/node-compat/templates/template-test.mjs
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 docs/node-compat/component-tests/run.mjs
```

Install dependencies using the checked-in [toolchain lockfile](component-tests/toolchain/package-lock.json) outside the checkout, as described in [component test reproduction](component-tests/README.md). Set `NODE_COMPAT_ENGINE` only to a ComponentizeJS **embedding** engine built from the audited source, not a stock raw StarlingMonkey binary. Repeating the smoke suite is not a substitute for the native-import fixtures below.

## Required differential and component coverage

| Area | Oracle and real-component fixtures | Acceptance |
| --- | --- | --- |
| Module exports | Compare explicit manifests with Node 22 namespaces/default own members; reflect descriptors without invoking getters; invalid named import must fail linking | Every selected name accounted for, constants numeric, no extra then/export leakage |
| Resolution and caching | Native `node:buffer` and bare `buffer`; child-process aliases; static CJS require lowering; global Buffer; repeat imports and dynamic ESM import | Same exported constructor/default identity; namespace identity follows documented canonicalization; no duplicate adapter Buffer |
| Stub failure | Invoke and construct each admitted callable in deployed functions, initializer application top level and top-level await; directly invoke exposed prototype methods | Error code/module/operation stable; all operations fail; top-level calls fail componentization |
| Inspection | Object.keys, descriptors, typeof, JSON.stringify(default), Promise.resolve(namespace/default), missing property and Symbol inspection | Safe reads; no accidental thenable; no universal Proxy |
| Buffer allocation | Sizes 0, 1, bounds, over cap, negative, NaN/Infinity, fractional, wrong type, OOM injection | Same supported bytes/error category/code; declared deviations explicitly rejected |
| Encodings | UTF-8 ASCII/multibyte/astral/lone surrogate/BOM, every malformed UTF-8 boundary; hex case/odd length/first invalid pair/NUL/non-ASCII | Node byte/string result for supported domain; unknown vs excluded encodings distinguishable |
| ArrayBuffer/view semantics | U8 with nonzero offset, AB shared view, copy from Buffer/U8, slice/subarray negative/clipped ranges, empty/end views, map/filter/species | Identity, offset, length, mutation propagation and no unintended copies |
| Unsupported Buffer operations | Every explicit stub, wrong supported overload, other encodings, other input kinds and legacy constructor | Stable profile error; no unnoticed fallback to U8 overload with different semantics |
| Native data safety | Forced minor/major GC before/after each kernel, allocation-failure paths, detached/shared/resizable inputs, zero-length spans, input species/prototype tampering | No use-after-free, no borrowed pointer over allocating call, no invalid allocator transfer; documented behavior for edge cases |
| Snapshot | Deterministic bytes/state created before Wizer survive; entropy/env/time/live-handle attempts rejected or follow explicit policy; unsupported top-level calls always fail | No build-secret capture; fresh runtime entropy/time/env; no resource IDs cross snapshot |
| Reuse and scheduling | Repeated explicit exports; two request contexts, cancellation, timeout/error paths; nextTick/microtask/timer ordering once implemented | Pure state persistence explicit; request cleanup/isolation proven separately; interest count/resources return to baseline |
| Hosts | Validate/instantiate the exact component on Wasmtime 42.0.1 and wasmCloud 2.11.0 with explicit grants and denied-grant cases | No host changes/providers/custom interfaces needed; failures attributable to absent/denied declared capabilities |

Use existing `test_e2e`/`tests/test.sh` fixtures for rebuilt StarlingMonkey HTTP tests and existing ComponentizeJS API helpers for exported-function tests. Add standard `wasmtime serve` HTTP entry variants when HTTP is selected. Keep the zero-import exported-function fixture for guest-only Buffer/stub work; a broad proxy world must not hide accidental filesystem or socket dependencies.

## Final component import audit

For every built component, save raw `wasm-tools component wit component.wasm` output (or pinned Jco's component-WIT tool output), run component validation, and record exact import names and versions after Preview1 adaptation and optimization. Include type-only resource dependencies in the audit. Do not report source world declarations or core Wasm imports as measured final-component imports.

The pure test world allowlist is empty. Future selected variants use exact standard interfaces at `0.2.10`, with IO/clock/resource dependencies spelled out. Reject all unexpected imports, including `jco:*`, `wasmcloud:*`, nonstandard host adapters, draft `wasi:tls`, final Preview1 imports and unselected standard interfaces. A package-wide wildcard is insufficient. Also audit exports: required application/standard exports only, with no unintended debugging or test entrypoints in production.

Current **measured** imports are in `component-tests/results.json` and are empty for the stub smoke component. Imports from a native-template engine have not been measured. Existing default `local:bindings/bindings` WIT is broad; it is not the pure-profile emitted import list. Merely setting `DISABLED_BY_DEFAULT` or adding no JS filesystem imports does not establish dead import removal.

## Performance and component-size experiment

Compare (A) Jco 1.40's current audited JavaScript Buffer adapter, (B) the same bounded facade with the reference JS kernel and (C) the compiled native guest kernel. Match Node semantics, input caps, application payload, custom engine, build flags, optimization, world, imports and host grants. Audit adapter internal stream/Buffer dependencies so the comparison does not contain both implementations. Never compare custom host compression/crypto against guest-native code as if they were equivalent portable implementations.

Record raw/optimized component bytes, compressed distribution bytes, code/data sections, compile-cache size and incremental difference against an otherwise identical empty application. Record Node oracle and Jco adapter versions, compiler/SDK flags, LTO and wasm-opt/weval settings, host version/architecture and CPU. Measure final components; linked archive size alone is not relevant.

Measure fresh process/instance latency, module snapshot creation, first call after resume, warm calls, GC pauses, host RSS and peak linear-memory pages/JS heap when instrumentable. Keep cold and warm distributions separate. Use enough independent instances and repetitions for median/p95 and confidence intervals; report sample sizes and variance. Host-side timing permits a zero-import guest benchmark. A dedicated development export using Wasm memory-size can observe pages without adding a custom host service; keep instrumentation out of production exports.

Exercise 0/1/16/128-byte, 1 KiB, 64 KiB, 1 MiB and maximum admitted inputs where applicable: U8 copy, AB view creation, UTF-8 encode/decode, hex encode/decode, and mixed stream chunks. Hex/UTF-8 source-string limits constrain decode input sizes; do not bypass caps for an attractive benchmark. Use observable checksums and varying input so optimization cannot remove work. Separate throughput, allocation count/bytes, copied bytes and peak temporary memory. Include malformed inputs and error throughput. Later add compression level/ratio/format and crypto algorithm/key-size measurements.

Decide an acceptable component-size and memory budget before promoting more native libraries. Set no invented speedup or size threshold in this audit; initial measurements determine whether native hex is worthwhile and whether direct string allocation/adoption can safely remove its temporary string copy.

## Outstanding technical decisions

1. **Custom-engine compatibility:** compile the ComponentizeJS extension against this revision and confirm native registration order, CMake paths, JSAPI declarations and splicer behavior. Released-engine checks cannot settle this.
2. **Buffer edge contract:** finalize cross-realm branding, detached backing-store behavior, resizable/shared exclusions, user-controlled species/prototypes, full coercion/empty-string behavior and error message stability. Keep existing limits versioned; `MAX_LENGTH` is a profile limit, not the engine maximum.
3. **Native allocation design:** keep the conservative no-GC borrow plus copy pattern initially; consider adopting codec/string storage only with allocator/OOM/finalizer proof. Decide whether UTF-8 byteLength needs a no-allocation native length kernel.
4. **Facade initialization:** generated bundled classic factory executes in the content realm before application evaluation. Compile and test it in the real installer; do not evaluate the facade in the initializer realm and accidentally bind builtins to different intrinsics. Verify web codec installation precedes the optional profile.
5. **Bundler/CJS contract:** implement manifest-first externalization and static require conversion; decide package-name ambiguity and failure handling for dynamic requires. Do not advertise a nonexistent Jco nativeBuiltins option.
6. **Strict snapshot policy:** remove inherited build environment, reject capability-bearing initialization, decide fatal behavior for detached unhandled rejections, and validate live-handle accounting. Raw Wizer environment clearing does not erase JS-captured secrets.
7. **Scheduler/ALS hooks:** inspect the exact SpiderMonkey job queue extension API before implementing context capture; define nextTick/Immediate/ref semantics and prevent context leakage across async jobs/requests.
8. **Reuse and hosts:** initially restrict stateful request lifetimes; prove teardown before reuse. Run the selected world on unmodified wasmCloud 2.11.0, including standard HTTP entry routing/grants if needed. No success claim until deployment is observed.
9. **Optional capabilities and TLS:** pin exact interface allowlists per variant and measure import pruning. Choose guest TLS plus trust policy only if required; never infer TLS from P2 sockets or use a draft/custom host service to fill the gap.
10. **Release policy:** decide per-API acceptance thresholds, licensing for reused Jco/unenv/readable-stream code, Node target upgrade cadence, differential CI coverage and budget limits before expanding the profile.
