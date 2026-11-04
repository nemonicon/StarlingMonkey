# Opt-in Node compatibility profile

The latest accepted core `sm-node-22.14.0-m0.11` profile provides a bounded `node:buffer`
and an importable `node:child_process` stub. It does not provide general Node.js
compatibility or complete Buffer support. The API reference and differential
oracle are Node.js **v22.14.0**.

Latest acceptance is [v11](../../../tests/node-compat/milestones/foundations-v11/results.json),
with core m0.11, Events m0.10 and seven optional foundations. Three current Release
engines share 304 native inputs; 33 reports and 1,746 copied evidence files
preserve the accepted scope. All eight release gates pass, with separate allocator
GC, focused Events and both-host HTTP evidence. Historical m0.10 Events-OFF is a
separate control, not a fourth current engine. The full roadmap remains active;
the repository [continuing tracker](../../../progress.md) records remaining work.

Enable the profile explicitly when building StarlingMonkey or its ComponentizeJS
embedding:

```sh
cmake -S . -B cmake-build-node-profile -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_BUILTIN_NODE_COMPAT=ON
```

The option defaults to OFF. Normal builds do not install these modules or global
Buffer. The profile requires the existing text-codec builtin. Its hexadecimal
kernels are native guest code; the overload/error/view semantics live in a small
JavaScript facade. Neither module adds a host service or calls WASI directly.
The final component import set still depends on the application world and
ComponentizeJS feature selection, and must be inspected after composition.

Seven independent optional foundations are compiled and tested in the
[v11 checkpoint](../../../tests/node-compat/milestones/foundations-v11/README.md).
All default to OFF and require the core option above:

| CMake option | Bounded modules |
| --- | --- |
| `NODE_COMPAT_PATH=ON` | `path`, `path/posix`, `path/win32`; fixed cwd/platform policy and bounded glob matching |
| `NODE_COMPAT_EVENTS=ON` | Synchronous EventEmitter and bounded `addAbortListener`; `once`, `on`, `EventEmitterAsyncResource` and other manifest refusals remain deferred |
| `NODE_COMPAT_STRING_DECODER=ON` | StringDecoder UTF8/hex; other known encodings throw |
| `NODE_COMPAT_ASSERT=ON` | Assert/strict scalar assertions; deep/async/CallTracker operations throw |
| `NODE_COMPAT_QUERYSTRING=ON` | Legacy Querystring with explicit input/output/field caps and deferred overloads |
| `NODE_COMPAT_UTIL=ON` | Bounded Util/types/sys;29 captured-intrinsic predicates, pure helpers and native codec aliases; remaining calls throw |
| `NODE_COMPAT_STREAM_WEB=ON` | Exactly18 stream/web exports over real native classes; bounded UTF8 codecs, iteration and ordinary DataView/BYOB adapters; compression call/new throws. Requires web streams and text-codec builtins |

Each has its own versioned manifest and generated header, with real named/default
bindings and both canonical/bare registration. These modules add no host
capability. The checkpoint validates strict factory execution, selected bundler
imports, aliases, snapshot state and deployed errors; it is not general Node
compatibility. The [compatibility matrix](../../node-compat/compatibility-matrix.md)
and individual manifests define each bounded contract.

Events m0.10 passes 29 focused Node groups in both entropy modes, alias/CJS/
snapshot/error checks and separate fatal/discard controls. Its fresh ordinary
and protected callback returns omit Node's `.then` getter read: Node
`1/1/0` versus native `0/0/0`, ordered ordinary/protected/already-aborted.
The getters return undefined; callable-then/rejection parity is not established.
The target uses its well-known nonregistry `Symbol.dispose`, differing from
Node's `Symbol.for('nodejs.dispose')`. These are
[confirmed limitations](../../../tests/node-compat/milestones/foundations-v11/reports/callbackReturn.json).
The Release GC proof combines signal/listener/closure-held Symbol owners across eight
public hex roundtrips; it does not isolate prototype-only Symbol liveness or add
an OOM/fault result.

Stream/web retains ten corresponding native global constructor identities and
three hidden native class constructors. Its codec constructors are module-only.
Input limits are1Mi UTF16 units per encoder chunk and16MiB per decoder/BYOB
input; fixed attached unshared local unmodified views and min1 only. These caps
do not bound total retained queues or output. Writable-controller signal,
Proxy/layout/cross-realm inputs, several native error codes and controller arity
remain gaps. Both OFF import names fail bundling and actual initialization;
no adapter fallback occurs. See the [m0.9 manifest](../../../builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json)
and [executed native gates](../../../tests/node-compat/foundation-stream-web/production-adoption/README.md).

## Supported Buffer subset

| API | Contract |
| --- | --- |
| `Buffer.alloc(size, fill?)` | Integer size from 0 to 16 MiB; numeric fill only, zero by default. No pool. |
| `Buffer.allocUnsafe(size)` | Primitive finite raw number from0 through16MiB; accepted fractions truncate. After unchanged validation, m0.11 directly returns privately branded captured native Uint8Array storage: fresh exact zeroed backing at offset0, no pool. This intentionally differs from Node's uninitialized/slab storage; allocUnsafeSlow remains deferred. |
| `Buffer.from(string, encoding?)` | UTF-8 (`utf8`, `utf-8`) or hexadecimal (`hex`), case-insensitive. At most 1,048,576 UTF-16 source units. Hex truncates at the first invalid pair and drops an odd final nibble. |
| `Buffer.from(Uint8Array)` | Copies the visible bytes to independent storage. |
| `Buffer.from(ArrayBuffer, offset?, length?)` | Shares fixed-length backing storage; nonnegative integer offset/length only; view length at most 16 MiB. |
| `Buffer.isBuffer`, `Buffer.isEncoding` | Private instance brand and explicit profile encoding allowlist. |
| `Buffer.byteLength` | Selected string encodings, fixed attached ArrayBuffer or Uint8Array. Shared, resizable and detached storage is rejected. |
| `buf.toString(encoding?, start?, end?)` | UTF-8 or hex; integer range arguments with clipping. UTF-8 preserves a leading BOM and replaces malformed input. |
| `buf.slice`, `buf.subarray` | Shared backing storage and Buffer identity, with Uint8Array range normalization. |
| `.buffer`, `.byteOffset`, `.byteLength`, `.length`, indices, `.parent`, `.offset` | Real Uint8Array backing relationships and legacy view aliases. |

Core m0.11 adds no exports, encodings, C++ allocation kernel, raw byte borrow or
allocator transfer. The same JS-owned zeroing and 16 MiB cap apply; acceptance
establishes bounded correctness, not a current performance or memory advantage.

Instances have genuine typed-array internal slots. Both constructor and prototype
inherit from Uint8Array; species operations such as map/filter create independent
Buffer instances. Inherited Uint8Array operations remain available except methods
that Node overloads and this profile explicitly rejects.

Array-like/valueOf/JSON input, non-Uint8 typed arrays, DataView, SharedArrayBuffer,
resizable backing storage for construction, the legacy Buffer constructor,
additional encodings, numeric readers/writers, copying/searching/writing/fill
methods, concat, uninitialized allocation, allocUnsafeSlow and full inspection/serialization are outside
the subset. Invalid supported arguments use selected Node error codes; excluded
overloads throw `ERR_SM_NODE_UNSUPPORTED`. Full coercion, error-order and message
parity are not promised.

The finite manifest accounts for every Node 22 `node:buffer` export. Blob, File,
SlowBuffer, atob, btoa, isAscii, isUtf8, resolveObjectURL and transcode are explicit
throwing callable bindings in this milestone. Constants remain numeric:
`INSPECT_MAX_BYTES` is 50, `kMaxLength`/`constants.MAX_LENGTH` are 16 MiB and
`kStringMaxLength`/`constants.MAX_STRING_LENGTH` are 32 MiB. These are profile caps,
not Node's platform maxima; memory pressure may still cause allocation failure.

## Module and bundler contract

Native installation uses the existing `add_builtin` and
`api::Engine::define_builtin_module`. Both `node:` and bare aliases are registered
with the same exported values. Global Buffer is the same constructor as the
module export. Namespace objects remain cached by specifier; aliases need not
have equal namespace-object identity unless the bundler canonicalizes them.

In the core Buffer/stub modules, every named export equals the corresponding
default-object member; their defaults and constants are frozen. Optional
foundations have their own declared default graphs: Path/Querystring/StringDecoder
defaults are mutable objects, Events/Assert defaults are mutable functions, and
named bindings retain the initially registered references. There is no runtime CommonJS loader or
`syncBuiltinESMExports` mutation protocol. Unknown names fail ESM linking;
unadmitted modules have no implicit empty stub.

A bundler must preserve the selected native imports before an adapter plugin can
replace them. The finite resolver in `tests/node-compat/profile-bundler.mjs`
canonicalizes modules selected by the actual engine receipt, externalizes their `node:` imports,
rejects other builtins/custom adapters, and lowers a deliberately narrow literal
CommonJS require contract for local `.cjs` files imported by explicit path. It is
not a general npm CommonJS package loader. Applications using Jco's default Node
adapter bundling
do not automatically use this native profile. Global injection must use the
canonical native Buffer and must not bring in another Buffer implementation.

`node:child_process` has nine callable exports plus default: ChildProcess,
_forkChild, exec, execFile, execFileSync, execSync, fork, spawn and spawnSync.
Calls and construction always throw an Error with `code`, `module`, `operation`
and `profile` fields. This applies during snapshot initialization and deployed
execution. Importing and inspecting the namespace/default object is safe; neither
is an accidental thenable. No process-spawn or custom host capability is imported.

## Native ownership and generated sources

The byte kernels allocate JS-managed typed arrays or owned staging memory. All
JS objects/strings are rooted across allocation. Typed-data pointers are borrowed
only inside no-GC regions, after allocation and validation, and never retained
across a callback or suspension. Hex encoding copies owned staging bytes into a
JS string. The production UTF8 encoder now writes directly into an exactly sized
GC-owned Uint8Array; TextDecoder owns its UTF16 staging allocation and releases
the borrowed input before result-string creation. These remain distinct paths,
without a blanket zero-copy claim. No Rust/C++ allocation is implicitly
transferred to an incompatible allocator.

Fresh, bounded outputs from captured native producers receive prototype and
private WeakSet branding without reading their backing-buffer getter. This
avoids materializing SpiderMonkey's small inline arrays unnecessarily. External
inputs and observable species/view outputs keep full validation. The
[allocation follow-up](../../node-compat/buffer-optimization-and-abi-fix.md)
records the mechanism, matched experiment and limits.

The facade and stub sources and their versioned manifest live under
`builtins/node-compat`. The checked-in generated factory header keeps normal CMake
builds independent of Node/npm. The accompanying deterministic generator checks
that the header agrees with those sources and validates the manifest against its
[versioned restricted schema](../../node-compat/manifest-validation.md).
Factories execute as strict script in the content realm
after native text codecs are installed, before application module evaluation.

`NODE_COMPAT_GC_STRESS` is a development-only build setting for forced collection
at rooted kernel boundaries. It is not a Node API or host capability. It must not
be enabled for performance measurements.

## Integration validation

`tests/node-compat` builds the pinned ComponentizeJS embedding against this source
and tests surviving native imports, aliases, CommonJS conversion, global identity,
the Buffer subset and predictable stub failures. The runner requires an explicit
custom engine, an exact Node v22.14.0 oracle and Wasmtime 42.0.1. It validates final
imports against the empty allowlist for the pure test world.

Earlier normal and compacting-GC-stress native engines passed the full component
suite on Wasmtime 42.0.1: 381 string vectors and 250 byte-array vectors against
Node v22.14.0, shared/copying views, native static/dynamic imports and aliases,
snapshot state, CommonJS/global identities, 91 unavailable Buffer methods and all
nine child-process callable exports. Direct/constructed/awaited top-level stub
calls and unknown named imports failed componentization. Both final test
components had zero host imports. SharedArrayBuffer was not exposed by the engine,
so native shared-input construction tests were skipped explicitly.

The accepted [v11 release batch](../../../tests/node-compat/milestones/foundations-v11/reports/releaseEight.json)
contains eight passing gates: five successful same-engine results were reverified,
and three strict suites ran fresh after a preserved storage failure. The first
allocator attempt's missing `pathToFileURL` import was a harness failure, also
preserved before its successful fresh retry. Neither failure changes native
source or establishes failure reuse.

The new [allocator GC gate](../../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json)
covers three retained Jco calls and fresh Wasmtime, with eight valid native hex
roundtrips per call; it is narrower than rerunning the full byte corpus under GC.
The [19 focused Events components](../../../tests/node-compat/milestones/foundations-v11/reports/focusedReceipt.json)
retain the callback getter/Symbol counterexamples and combined-owner limitation.
No new genuine OOM/fault result, ALS or request teardown is established.

The same v11 HTTP component, SHA-256
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`,
passes three requests on stock Wasmtime 42.0.1 and official wash 2.11.0; both stop
with exit 0. Its [six exact standard 0.2.10 imports](../../../tests/node-compat/milestones/foundations-v11/reports/httpAudit.json)
are `wasi:http/types`, `wasi:io/{error,poll,streams}`, `wasi:random/random` and
type-only `wasi:clocks/monotonic-clock` for `duration`. No clock function, outgoing
HTTP, socket, DNS, TLS, filesystem, CLI/environment or custom service is inferred.
Counters `[1,1,1]` on both hosts prove neither same-instance reuse nor request
isolation. The [immutable checkpoint](../../../tests/node-compat/milestones/foundations-v11/README.md)
records all three current engines and their exact sources and configuration.

The following v10 and earlier results retain their historical artifact scope.

The historical v10 release batch replays the core and prior foundations, with
four source-pinned engines sharing 304 native inputs and 33 primary reports.
Exact hashes, configs and executed scope are in the
[immutable checkpoint](../../../tests/node-compat/milestones/foundations-v10/results.json).
Its separate combined-owner GC gate is narrower than rerunning the entire byte
corpus under a new GC engine.

That v10 HTTP component, SHA-256
`0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610`,
passes three requests on stock Wasmtime 42.0.1 and official wash 2.11.0; both stop
with exit 0. Its [six exact standard 0.2.10 imports](../../../tests/node-compat/milestones/foundations-v10/reports/http-audit.json)
are `wasi:http/types`, `wasi:io/{error,poll,streams}`, `wasi:random/random` and
type-only `wasi:clocks/monotonic-clock` for `duration`. Random is explicitly
selected; no clock function, outgoing HTTP, socket, DNS, TLS, filesystem,
environment or custom service is inferred. Counters are `[1,1,1]` on both hosts;
this proves neither same-instance reuse nor request isolation. The corrected
Wasmtime-v2 result and failed first harness attempt are preserved separately.

The HTTP packaging script uses a hash-guarded composition of the pinned stock
splicer's real APIs to keep manual HTTP bindings while removing outgoing HTTP.
It restores its process-local function replacement afterward. The native engine,
installed npm files and host binaries remain unchanged. Its final core has no
Preview1 imports and is wrapped without an adapter. These packaging details and
the exact emitted type graph are part of the reproduction record.

The [A/B measurement results](../../../tests/node-compat/bench/README.md)
compare supported operations with Jco's actual Buffer adapter using the same
release engine and capability-free world. Conversion throughput improved in the
measured non-Weval mode; copying throughput was about 4–15% lower, and peak memory
was higher in some small-buffer cases. The
[result summary](../../node-compat/portability-and-performance.md) separates those
tradeoffs from component size and startup observations. A separate
[ABI diagnostic](../../../tests/node-compat/bench/abi-results.json) reproduced
incorrect high-`u32` result transport without Buffer code. The current build
recipe applies a versioned guest-source patch for scalar export results; its
[direct regression](../../../tests/node-compat/abi-fix/README.md) passes 339 Jco
checks and direct Wasmtime controls. This is a local ComponentizeJS guest patch,
not a fix in released 0.23.0. A separately reproduced high-`u32` imported-callback
argument defect required a separate imported-I32 splicer patch; the current
explicit v2 packager includes that correction and the disabled-clock errno fix.
Both fixes have separate pinned source/provenance gates. Benchmark checksums retain signed
`s32` to preserve their original matched protocol.

The original architecture audit and frozen semantic templates are in
`docs/node-compat`; their released-engine/reference-kernel results must not be
confused with tests of the current native implementation. Complete Node
semantics, exhaustive OOM injection, shared input construction, concurrent
request isolation and production cluster deployment remain separate gates.

Current [corrected-clock](../../../tests/node-compat/bench-clock-v2/RESULTS.md)
and [Weval](../../../tests/node-compat/weval-experiment/v5/RESULTS.md) measurements
retain their own exact engines and workload limits. Native byte codecs improve
the measured throughput, while small copying constructors and several memory
cases remain counterexamples. The copying scenario calls `Buffer.from(existing
Buffer)`; it does not validate the still-deferred `Buffer.prototype.copy` API.
