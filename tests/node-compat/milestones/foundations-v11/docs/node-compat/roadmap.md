# Dependency ordered implementation roadmap

Each phase has a measurable gate. The initial deliverable supplies templates and source evidence; these phases describe the work required to turn them into a shipped profile.

The user has authorized execution of the full roadmap. The active
[execution ledger](execution-status.md) tracks every gate, current evidence and
remaining work; completing the initial milestone does not complete this plan.

The opt-in Buffer/stub slice has an [accepted immutable checkpoint](../../tests/node-compat/milestones/allocation-r2/README.md): corrected guest ABI packaging, strict initialization, zero-import pure components, two target HTTP hosts, and four genuine allocator failure scopes with recovery. General DEBUG indirect bindings remain unavailable. The historical performance figures require refresh after the clock-stub correction.

Accepted [entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md),
[foundations-v3](../../tests/node-compat/milestones/foundations-v3/README.md),
[foundations-v4](../../tests/node-compat/milestones/foundations-v4/results.json) and
[foundations-v5](../../tests/node-compat/milestones/foundations-v5/README.md)
checkpoints now cover bounded entropy, Path/loader, Events and ordinary UTF-8
encoder integration. Their exact artifacts pass the documented zero-import or
explicit0.2.10 HTTP worlds on stock hosts. Corrected-clock and matched native
allocation experiments have replaced the old timing claims; a frozen v5 [Weval comparison](../../tests/node-compat/weval-experiment/v5/RESULTS.md)
now reports both throughput gains and copying/memory counterexamples. See the execution ledger for its current state.

The [v8 checkpoint](../../tests/node-compat/milestones/foundations-v8/README.md)
accepts bounded Util, zeroed allocUnsafe and the guest correction for the
previously swallowed callback failures, with all prior module and both-host
gates. New [matched allocator measurements](../../tests/node-compat/foundation-alloc-unsafe/matched/measurement-v1/README.md)
show the initial allocation facade is slower than the portable Jco adapter;
an isolated direct-allocation proposal must earn its own evidence. Stream/web
codecs, iteration and DataView adapters now pass actual native integration,
ON/OFF, prior-module, strict-callback and both-host gates in the
[v9 checkpoint](../../tests/node-compat/milestones/foundations-v9/README.md).
The latest accepted [v10 checkpoint](../../tests/node-compat/milestones/foundations-v10/README.md)
adds bounded native-backed `addAbortListener`,29 focused groups in both entropy
modes, combined-owner GC, optional-OFF and both-host HTTP evidence. Fresh
callback-return `.then` getter reads still differ (Node `1/1/0`, native `0/0/0`), as
does `Symbol.dispose` registry identity; neither is a parity pass. HTTP retains
six standard 0.2.10 interfaces, a type-only clock and counters1, without a reuse claim.

The reviewed m0.11 source is now
[applied](../../tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json),
with fresh production engine/runtime/strict/GC/HTTP gates pending. Private CPU
measurements retain RSS and size counterexamples and do not validate this
rebased source. Scheduler/Blob packets remain source-only; isolated async-context
probes are not production ALS. These findings do not complete the roadmap.

## Phase 0 Freeze and reproduce the engine

1. Freeze the revisions in the audit and record npm lockfile, engine/Wizer/SpiderMonkey/SDK artifact hashes and compiler flags. Build ComponentizeJS with `STARLINGMONKEY_SRC` pointing at this exact checkout, `HOST_API=wasi-0.2.10` and production debugger disabled. Preserve existing `add_as_subproject`, `add_builtin`, aggregate Rust and `engine` override mechanisms.
2. Run the existing StarlingMonkey E2E tests and ComponentizeJS pure/global/snapshot/error fixtures against that engine. Identify source/API incompatibilities before implementing more built-ins.
3. Build the zero-import profile test world. Print and inspect the final component's import/export types. Any unexpected interface is a failing gate, not an invitation to install another host provider.

Gate: reproducible custom engine, final component validates, explicit zero-import fixture instantiates on Wasmtime 42.0.1. Resolve wasmCloud 2.11.0 deployment entry/world requirements before claiming secondary-host portability. A capability-free custom export may need a test harness on wasmCloud; use its existing component workload facility or the separately declared standard HTTP export variant, never a new host service.

## Phase 1 Manifests and deterministic failure

Depends on Phase 0. Promote Node 22 export inventories into schema-validated module manifests. Generate plain finite registration objects and ESM exports; pin the facade interoperability contract and alias canonicalization. Implement `node:child_process` first: every exported callable is a named throwing function, construction throws, namespace/default inspection is safe, and no host capability is imported.

Add the profile bundler resolver before Jco adapter replacement, coherent global injection, and explicit CJS-to-ESM lowering for static builtin require. Test both aliases, namespace/default identities, unknown export link failure, ambiguous npm names, dynamic require rejection and accidental thenables. Confirm a top-level unsupported call fails componentization. Make strict initialization rejection handling an explicit decision, since not every unhandled rejection currently aborts snapshot creation.

Gate: exact namespace parity for the chosen stub, call/new failures in initialization and deployment, no `jco:*` or draft imports, one implementation of Buffer in the bundle graph.

## Phase 2 Bounded Buffer

Depends on Phase 1. Implement the documented bounded facade and native hex kernel through optional `add_builtin`, with explicit limits, no legacy constructor and no pool. Compile and review the C++ template against the pinned JSAPI. Resolve detached/resizable/shared backing-store handling and string-size checks before enabling it. Keep unsupported exports/methods explicit and identifiable; do not claim full Node Buffer API.

Add Node differential vectors, component tests, forced-GC and OOM/boundary tests, buffer-view identity and overlap checks. Test facade use through a minimal CommonJS dependency and global Buffer injection. Compare against Jco 1.40's existing adapter in equivalent capability-free components. Add UTF-8 native fast paths or native copy/search/numeric kernels only when measurements justify them.

Gate: supported overloads pass differential/component tests; declared deviations have explicit negative tests; compiled native implementation passes GC and allocator review; no added WASI imports; size/startup/memory/throughput results recorded. If the kernel does not improve the chosen workload, retain the simpler implementation.

## Phase 3 Pure foundations and scheduling

Depends on Phase 2 for Buffer-dependent APIs. Implement EventEmitter, string_decoder, assert, path, querystring and bounded util semantics. Retain JS for small semantic state machines. Bridge the native web stream exports only after checking identities, BYOB behavior and per-export availability. Implement classic Readable/Writable/Duplex/Transform/PassThrough plus stream/promises and stream/consumers; web streams alone do not satisfy this dependency.

Before exposing Node timers, process.nextTick or AsyncLocalStorage, define queue ordering, promise draining, cancellation, ref/unref and lifecycle. Integrate context tokens at the actual SpiderMonkey promise-job and native-task boundaries. Establish request teardown and sequential reuse; do not add an ALS facade that loses context on await.

Gate: stream backpressure/error/cancellation tests and interleaved context tests pass in a real component, no leaked interest count or request resources, and the scheduler's documented deviations are stable.

## Phase 4 Native compression and cryptography

Depends on byte ownership from Phase 2; streaming APIs depend on Phase 3. Evaluate native zlib reuse for gzip/deflate/deflateRaw; add Brotli only after a size/throughput decision. Reuse OpenSSL-backed web primitives for matching algorithms; implement Node key/Hash/Hmac semantics separately. Audit RNG use inside OpenSSL rather than treating deterministic crypto as permission for ambient entropy. No custom compression/crypto host services.

Gate: known-answer and malformed-input vectors, Node differential, streaming boundary tests, key lifetime/zeroization policy, final component size and operation benchmarks. Algorithm lists and OpenSSL flags remain versioned. Restrict entropy imports to variants that need random operations/key generation.

## Phase 5 Optional standard capabilities

Depends on Phase 3 lifecycle/scheduler. Design independent filesystem, HTTP, TCP/UDP/name-lookup, CLI and entropy variants with explicit standard `0.2.10` allowlists. Start with a small subset per module and publish deviations per export. No blanket `fs`, `net`, `dns`, `http` or `process` support label. Preserve preopen confinement and network grants. Reject unsupported socket/TLS/HTTP options rather than silently ignoring them.

TLS remains unavailable unless a guest TLS stack, certificate trust source, validation/time policy and socket integration are selected and measured. WASI HTTP HTTPS does not justify claiming `node:tls` or full `node:https`. Process creation, IPC, Node workers, V8/Inspector APIs and POSIX signals remain unavailable with the selected interfaces.

Gate: identical components validate and instantiate on both unmodified target hosts under documented grants, capability-denied tests fail predictably, and unused variants do not enlarge the pure profile's import set. Publish actual emitted imports for every profile variant.

## Phase 6 Expand only from measured demand

Depends on the relevant earlier phases. Add further encodings, numeric Buffer operations, search/copy kernels, module APIs and optional guest libraries in response to application traces. Require a manifest change, Node release differential, component fixture and size/performance comparison for each extension. Retargeting Node or WASI is a compatibility release, not an unreviewed inventory refresh.
