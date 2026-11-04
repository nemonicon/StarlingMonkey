# Portable Node compatibility profile for StarlingMonkey

This directory preserves the initial architecture audit and opt-in implementation templates for a bounded `node:buffer` and an importable, explicitly unavailable `node:child_process`. The initial audit did not add runtime built-ins or establish complete Node or Buffer compatibility. The compatibility reference is **Node.js v22.14.0**. Native code below means code compiled into the Wasm guest, with no additional host service.

Execution of the full roadmap is now active. See the
[gate-by-gate execution ledger](execution-status.md) for implemented, tested and
remaining work, and the repository [continuing tracker](../../progress.md).
Earlier checkpoints retain immutable reports and bounded claims.
The latest accepted [foundations-v10 checkpoint](../../tests/node-compat/milestones/foundations-v10/README.md)
preserves core m0.8 and seven optional foundations, adding bounded Events m0.10
`addAbortListener`. Its four engines share 304 native inputs; 33 reports and 3,445
copied files preserve the source, configuration and executed evidence.
Twenty-nine focused groups pass in both entropy modes, with separate combined-owner
GC and fatal/discard gates. A confirmed callback-return `.then` getter deviation
remains: Node reads `1/1/0` for ordinary/protected/already-aborted callbacks; both
native hosts read `0/0/0`. Target `Symbol.dispose` also lacks Node's registry identity.
These are [explicit false-parity results](../../tests/node-compat/milestones/foundations-v10/results.json),
not complete Node/EventTarget compatibility.

The same HTTP component passes three requests per stock host with six standard
0.2.10 interfaces, including explicit random and a type-only monotonic clock.
Counters are `[1,1,1]`; instance reuse and request isolation are unproved.
Historical audit dispositions below are not current support claims.

The reviewed m0.11 allocation/HTTP-v10 source is now
[applied](../../tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json),
but fresh engine/runtime/GC/two-host gates remain pending. Its frozen proposal's
earlier UNAPPLIED label is historical. Private measurements suggest possible CPU
improvement while retaining RSS/capacity/size counterexamples; they do not
establish performance of this rebased production source. Latest acceptance
remains v10.

Earlier [v7 ordinary controls](../../tests/node-compat/milestones/foundations-v7/README.md)
exposed a strict-initialization gap in callback exception reporting. Private
guest corrections now pass bounded synchronous, post-binding, deployed and
finalizer/getter gates on the new production engine. The original counterexamples
remain preserved. See the [execution ledger](execution-status.md) for exact scope,
remaining event/lifecycle deviations, accepted bounded stream/web and native
compression work.

The subsequent native integration lives in [`builtins/node-compat`](../../builtins/node-compat) with its own [`tests/node-compat`](../../tests/node-compat) and [developer contract](../src/developer/node-compat.md). The inventories and findings in this directory describe the original audited revision; current integration evidence is recorded separately.

The subsequent [wasmCloud validation](../../tests/node-compat/wasmcloud/README-host.md)
executes a standard HTTP variant on the official unmodified 2.11.0 local host.
The [A/B experiment](../../tests/node-compat/bench/README.md) compares supported
Buffer operations with Jco's actual JavaScript adapter using the same release
engine. Those records distinguish observed results from this original audit's
proposed support and validation plans.

The [portability and performance results](portability-and-performance.md)
summarize the executed host checks, all benchmark tradeoffs and the export
binding defect found during measurement.

## Deliverables and evidence

| Deliverable | Artifact | Evidence level |
| --- | --- | --- |
| A. Architecture | [integration findings](integration-findings.md), [toolchain findings](toolchain-findings.md) | Source inspection at the exact revisions below |
| B. API matrix | [readable matrix](compatibility-matrix.md), [per-API records](api-matrix.csv), [exact namespace inventory](node-v22.14.0-exports.json), [policy](policy.json) | Inventory executed with Node v22.14.0; profile dispositions are proposed |
| C. Roadmap | [dependency ordered roadmap](roadmap.md) | Engineering proposal with acceptance gates |
| D. Templates | [template contract](templates/README.md) and files in that directory | JavaScript checks and uncompiled C++ distinguished there |
| E. Validation | [validation plan](validation.md), [real-component fixtures](component-tests/) | Executed results are recorded separately from required future gates |

The audit started from a clean worktree at **`54b3329b3ce818fd1f244e871e9c259b63667cda`**. Its initial additions were confined to `docs/node-compat`. The subsequent runtime profile remains opt-in; no Node module or global is installed by default.

## Frozen baseline

| Dependency or contract | Pin |
| --- | --- |
| StarlingMonkey source | `54b3329b3ce818fd1f244e871e9c259b63667cda` |
| SpiderMonkey artifact tag | `FIREFOX_147_0_4_RELEASE_STARLING` (`cmake/spidermonkey.cmake:1`) |
| Native build dependencies | WASI SDK `30.0` (`cmake/wasi-sdk.cmake:1`), Rust `1.88.0` / `wasm32-wasip1` (`rust-toolchain.toml`), OpenSSL `3.0.17` with the source hash in `cmake/openssl.cmake:3` |
| Node oracle | `v22.14.0`, official `darwin-arm64` binary; tarball SHA-256 `e9404633bc02a5162c5c573b1e2490f5fb44648345d64a958b17e325729a5e42` checked against release SHASUMS |
| Node API inventory input | [versioned all.json](https://nodejs.org/download/release/v22.14.0/docs/api/all.json), SHA-256 `fdbeac15985adfb8b5298d9e3175263900d0d4dbf49c6c80a96dd5724a080301` |
| ComponentizeJS | npm `0.23.0`, source `4d812f5a7b524cea5bcfd565cac55f3fab876a57` |
| Jco | npm `1.40.0`, source `42cd21e0a31362dbb519f4749f3689bba0fbdb1d` |
| Selected production WASI family | Only explicitly admitted interfaces in `wasi:{cli,clocks,filesystem,http,io,random,sockets}@0.2.10`; not all seven packages for every component |
| Selected milestone test world | `starling:node-compat-test/profile@0.1.0`, application export `run: func() -> string`, **zero host imports required** |
| Existing engine binding world | `local:bindings/bindings`, includes `wasi:cli/command@0.2.10` and `wasi:http/proxy@0.2.10`; audit baseline, not the desired minimal application contract |
| Existing CLI adapter world | `local:bindings/command-extended`, CLI command plus outgoing HTTP at `0.2.10` |
| Direct target | Unmodified Wasmtime `42.0.1` (also this repository's build-tool pin) |
| Secondary target | Unmodified wasmCloud `2.11.0`, source `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff`; embeds Wasmtime `48.0.7` |

A custom local WIT **world** can group standard interfaces and export application functions; it must not import custom host services. The zero-import test world is a concrete minimal contract, not a promise that the current raw engine's broad import set automatically shrinks. ComponentizeJS's splicer and final component inspection must establish that property for the custom engine. A production HTTP variant will select `wasi:http/proxy@0.2.10` with an explicit interface allowlist; optional filesystem and sockets variants have separate allowlists.

The released ComponentizeJS engine used by smoke tests is not the rebuilt engine from this checkout. Replacing it requires the existing `STARLINGMONKEY_SRC` build extension and `engine` option, described in the toolchain audit. No full custom-engine build or wasmCloud deployment is represented as verified here. Node's oracle release is deliberately fixed for API semantics; it is not a recommendation to deploy that old release as a network service.

## Architecture decision

Use existing `add_builtin` and `Engine::define_builtin_module`, with finite export manifests and real ESM bindings. Keep the JavaScript facade responsible for overload selection, branding, typed-array relationships, errors and stream state machines. Put measured expensive byte kernels in native guest code. Reuse the existing native UTF-8 codecs, web streams, zlib and OpenSSL implementations only where semantics match. The first native Buffer kernel is hexadecimal conversion; a template is insufficient evidence of a performance win.

Preserve selected `node:` imports through bundling. Jco's existing adapter plugin otherwise replaces them before the runtime resolver sees them. Bundle CommonJS dependencies to ESM with a narrowly defined static-require mapping, and inject global Buffer from the same canonical module. Do not provide a general CommonJS loader or claim `syncBuiltinESMExports`. Unknown modules/exports fail resolution/linking; admitted stub functions always throw on invocation, including snapshot-time application evaluation.

Reject final imports outside the selected standard WASI allowlist. In particular, Jco's `jco:node/*`, wasmCloud-specific services, Preview1 imports left on the final component, and draft `wasi:tls` imports are outside this profile. Standard P2 sockets provide TCP, UDP and IP lookup; they do not provide TLS. Host-managed HTTPS through `wasi:http` cannot implement arbitrary Node TLS socket behavior. These limits are reflected per API in the matrix.

## Ownership and lifecycle policy

Root JS objects across every allocating/calling JSAPI operation. Use SpiderMonkey-managed ArrayBuffers and views for the baseline. Acquire native byte pointers only within a no-GC region after coercions, roots, lengths and output allocation are complete; release them before further JS execution or allocation. Rooting keeps objects reachable but does not pin movable raw data. No borrowed span crosses a callback, yield or async suspension. Long-lived JS fields require traced `JS::Heap` storage or engine-owned persistent roots with explicit teardown. Do not create static roots with a longer lifetime than the engine.

The baseline copies `Buffer.from(Uint8Array)` and shares `Buffer.from(ArrayBuffer, offset, length)`, `slice` and `subarray`. It retains the real `.buffer`, `.byteOffset`, byte length, index access and inherited Uint8Array behavior. A native codec may allocate its result once and return a view over that allocation. UTF-8 facade paths may still have an avoidable intermediate allocation; measure and remove it only after semantics are validated. A separately allocated Rust/C++ block is not automatically adoptable by `NewArrayBufferWithContents`: allocation family, failure ownership and finalizer must match. `JS_realloc` canonical-ABI storage is likewise not a blanket ownership-transfer mechanism.

Snapshot initialization permits deterministic module state and byte arrays, not deployed host handles or captured build secrets. Launch Wizer with a sanitized environment, source-only temporary preopens and explicitly disabled capabilities. Top-level entropy, environment access, clocks or host I/O require a declared policy; the recommended profile rejects capability-bearing operations during initialization rather than caching their results. Build-time source loading is an embedding concern with temporary resources closed before snapshotting. This is a profile change to implement and test, not a guarantee supplied by `__wasilibc_deinitialize_environ`.

At deployed entry, acquire environment/args from the granted `wasi:cli/environment` capability when enabled, reset time origins, and obtain fresh entropy from `wasi:random/random`. Never reuse a snapshotted random pool, TLS state, resource identifier or build-time environment cache. Deterministic pure modules require none of these imports. Wall time and monotonic time are distinct; Node scheduling uses the latter. Math.random initialization and cryptographic entropy require separate tests.

Initially permit one request lifetime per instance for stateful HTTP applications; pure explicit component exports may be called repeatedly under their documented state model. The current singleton fetch event and `Engine::reset` do not prove request isolation. Request entry must create a fresh context; every resource/task needs a close/cancel owner; entry failure and normal completion must release them. Reject concurrent reentry into a single JS engine until explicitly supported. Component reuse must separately define which application module state persists and which request roots, handles and callbacks are cleared.

Future AsyncLocalStorage must capture context when promise reactions and callbacks are registered, carry it with each queued job/task, restore it for callback execution and restore the prior context on every return/throw. Use rooted context tokens, not a mutable request-global variable. `run`, `enterWith`, `exit`, `disable`, binding and snapshot helpers have different contracts. A custom SpiderMonkey job queue or an equivalent verified embedding hook is needed; wrapping Promise.then and timers alone misses await continuations and native reactions. The actual pinned SpiderMonkey hook choice remains open.

## Regenerate the API records

Run the generator with the exact Node oracle and its versioned API JSON:

```sh
curl -fL https://nodejs.org/download/release/v22.14.0/docs/api/all.json -o /tmp/node-v22.14.0-api.json
/path/to/node-v22.14.0/bin/node docs/node-compat/scripts/inventory.mjs /tmp/node-v22.14.0-api.json
```

The generator refuses other Node releases and different API JSON bytes, enumerates namespaces and global descriptors without executing getters, adds prefix-only `node:test`, `node:test/reporters`, `node:sea`, `node:sqlite`, and supplements reflected exports/static/prototype members with documented overloads, events, properties and globals. Runtime data such as process environment, argv and loader-cache contents is excluded from member enumeration. The generated inventory is platform-specific where Node itself is platform-specific. No Darwin constants are silently adopted as Wasm ABI constants. Documentation paths can represent the same API as a reflected path; these are complementary evidence records, not distinct implemented operations.
