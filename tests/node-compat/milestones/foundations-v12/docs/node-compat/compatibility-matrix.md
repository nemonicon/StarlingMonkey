# Node 22 API compatibility matrix

The machine-readable [API matrix](api-matrix.csv) is the per-API record: each row has module, API, type, inventory origin, status, implementation strategy, required capability, deviation and validation plan. [Node export inventory](node-v22.14.0-exports.json) contains the exact 72 module namespaces obtained from Node v22.14.0 on macOS arm64. [Policy](policy.json) defines dispositions and overrides; [generator](scripts/inventory.mjs) checks the oracle version and documentation hash. Documented overload/event/property records supplement reflection and can duplicate reflected API records.

The [inventory correction record](inventory-correction-results.json) verifies
6,795 evidence rows with all 4,132 reflection/CommonJS rows unchanged. JSON parser
labels `Type`/`return` are resolved to declared property names, and non-module
chapters (`errors`, `esm`, `permissions`, `n-api`) are recorded as exclusions
rather than invented builtin IDs. Run `scripts/inventory-test.mjs` against the
same pinned API JSON to check these regressions. Current implementation work is
tracked separately in the [execution ledger](execution-status.md).

Statuses describe the **proposed profile contract**, not checkout-wide implemented Node support:

| Status | Meaning |
| --- | --- |
| supported | A precisely listed semantic-template operation/constant; actual execution coverage is identified separately. Native integration still requires compilation. |
| partial | Only specified overloads/semantics; all deviations are part of the contract. |
| import-only | Module/default/constructor name can be imported and inspected, but its unavailable operations throw. This is not operational support. |
| deferred | Not part of this milestone. Unregistered module IDs fail imports; no implicit empty module or fallback host adapter. |
| unavailable | Cannot operate with the selected profile/capabilities or is deliberately excluded. Only explicitly installed manifests are importable. |

Every CSV row also says that production checkout integration is not implemented by this deliverable. Existing native **web** APIs are distinguished from Node-facing module parity. An unavailable module is not automatically an import-only stub: only the chosen `child_process` manifest and the finite Buffer namespace are supplied in this milestone.

## Current implemented overlay

The CSV and the following initial-contract tables preserve the original audit.
Current bounded implementation evidence is separate:

The latest accepted overlay is [v11](../../tests/node-compat/milestones/foundations-v11/results.json): core m0.11, seven optional foundations, 304 native inputs, three current Release engines, 33 reports and 1,746 copied evidence files. Direct zeroed Uint8Array allocation adds no exports or C++ allocation kernel. Historical m0.10 Events-OFF is a separate control. Callback getter/Symbol parity and prototype-only GC ownership remain explicit limits. The [continuing tracker](../../progress.md) keeps remaining roadmap gates active.

The [installed stream/web supplement](../../tests/node-compat/foundation-stream-web/installed-matrix-v9.README.md)
adds per-export/member records for the current m0.9 bridge:18 exports,184 Node-own
member observations and eight semantic operations. It distinguishes unavailable
properties, deferred calls and unverified target presence/behavior; private
nonregistry symbol descriptions remain reflection observations. The original
audit inventory and accepted v9 freeze are unchanged.

| APIs | Current status/strategy | Capability | Executed evidence and limits |
| --- | --- | --- | --- |
| `node:buffer` selected `Buffer` overloads, view/accessor methods and numeric constants | Partial; compiled guest C++ hex kernel plus audited JS semantics and existing native web UTF8 codecs | None | [Accepted v11 core](../../tests/node-compat/milestones/foundations-v11/reports/release-core.json) covers 381 string/250 byte vectors and aliases/default/global with m0.11; the [allocator GC gate](../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json) is separately bounded. Four genuine native kernel OOM scopes remain tied to [allocation-r2](../../tests/node-compat/milestones/allocation-r2/README.md), not inferred for new engines. Shared/cross-realm and complete Buffer support are excluded |
| `Buffer.allocUnsafe(size)` and hardened core refusal errors | Partial; accepted core m0.11 JS facade over captured native Uint8Array, with release and moving-GC gates | None | [Installed v11 evidence](../../tests/node-compat/milestones/foundations-v11/reports/release-allocator.json) and [GC supplement](../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json). Primitive finite raw size 0..16MiB; fractions truncate, fresh zeroed exact backing/no pool after unchanged validation. Ten differential/five policy groups, 240 refusal checks per call, eleven initialization failures and actual old-profile controls. All91 prototype refusals and five other static refusals remain. No new exports, C++ allocation kernel, genuine OOM or accepted production performance result. Historical [v8 measurements](../../tests/node-compat/foundation-alloc-unsafe/matched/measurement-v1/README.md) retain the slowdown versus Jco; the private direct-U8 pair retains RSS/capacity/size counterexamples |
| `node:child_process`: all nine named callables plus default | Import-only finite real ESM bindings | None | Same manifest/checkpoint. Every call/new throws identifiable `ERR_SM_NODE_UNSUPPORTED`, including initialization; namespace inspection stays safe |
| `node:path`, `/posix`, `/win32`: all 18 exports per namespace, 13 callable lexical/glob operations | Partial; registered guest module with JS lexical algorithms and bounded patched matcher, not a C++ path kernel | None | [Manifest](../../builtins/node-compat/export-manifest.path.node-v22.14.0.json), [v11 replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-path.json). 15,696 lexical/4,046 glob vectors and six first-deployed aliases pass Jco/Wasmtime. Fixed cwd/POSIX/case policy and explicit budgets remain deviations |
| `node:events`: bounded EventEmitter, static helpers and `addAbortListener`; exactly 16 exports | Partial; guest JS state machine with protected native AbortSignal integration | None | [V11 m0.10 replay](../../tests/node-compat/milestones/foundations-v11/reports/focusedOff.json) and [RuntimeOnly](../../tests/node-compat/milestones/foundations-v11/reports/focusedRuntime.json): 29 focused groups, aliases/CJS/snapshot, 8 rejected initializers and 5 fatal/discard cases per mode. The 19-component focused set includes combined-owner GC, not prototype-only Symbol liveness. [Historical m0.10 Events-OFF denials](../../tests/node-compat/milestones/foundations-v11/reports/historical-m10-events-off.json) remain separate. Callback-return getter parity is false (Node `1/1/0`, native `0/0/0`); Symbol.dispose registry differs. `once`, `on`, `EventEmitterAsyncResource` and captureRejections=true remain deferred |
| `node:string_decoder`: `StringDecoder` and default, UTF8/hex only | Partial; optional guest JS carry-state semantics over existing native Buffer codecs | None | [Manifest](../../builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-string-decoder.json): 2,982sequences/8,886writes and40generic decoder cases, three retained Jco calls and fresh Wasmtime, strict receiver/aliases/CJS/snapshot/three initialization failures. Other known encodings throw; shared/resizable/detached input restrictions and two native ordering deviations are explicit |
| `node:assert`, `node:assert/strict`: exactly22exports each | Partial; optional audited JS scalar assertions, typed errors and shared root/strict function graph | None | [Manifest](../../builtins/node-compat/export-manifest.assert.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-assert.json): 55groups/784primitive comparisons+22profile cases per call, aliases/CJS/snapshot/nine initialization failures on Jco+Wasmtime. Deep/async/CallTracker operations throw; diagnostics/cross-realm behavior remain bounded |
| `node:querystring`: exactly8exports | Partial; optional pinned JS parser/scanner with native URI intrinsics and Buffer UTF8 fallback | None | [Manifest](../../builtins/node-compat/export-manifest.querystring.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-querystring.json): 32groups/210delimiter/1,536malformed-byte vectors+11profile cases, aliases/CJS/private Buffer/snapshot/eight initialization failures on Jco+Wasmtime. Legacy malformed-Unicode behavior, caps and deferred nonstring overloads are explicit |
| `node:util`, `node:util/types`, `node:sys` | Bounded installed module, replayed in v11 | None | [V11 util replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-util.json): 47 util/sys named exports and42type predicates plus defaults, with 29 captured-intrinsic predicates, bounded pure helpers and native codec aliases. 2,436 shared checks+108 deferred call/new checks per call, six deployed aliases and fresh Wasmtime. Forty-one root functions and13predicates remain deferred; warnings and other stated deviations remain |
| `node:stream/web`, bare `stream/web`, exactly18 exports | Partial; accepted m0.9 facade over real native classes and codecs, replayed in v11 | None | [Accepted v11 replay](../../tests/node-compat/milestones/foundations-v11/reports/release-stream-web.json): 41 constructor/250 codec/67 iteration/26 DataView cases, aliases/CJS/cache/snapshot and 7 initializer failures. Prior [v9 OFF guards](../../tests/node-compat/milestones/foundations-v9/README.md) remain separately frozen. UTF8/fixed-unshared/min1, proxy/layout/code/arity/signal gaps persist; compression call/new defers, classic Stream is uninstalled |
| Existing global WebCrypto entropy/owned inputs | Bounded guest implementation policy; no `node:crypto` exports added | OFF: none; runtime: exact `wasi:random/random@0.2.10` | [Entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md): snapshot denials, repeated/fresh calls and 233 original upstream subtests on both stock hosts. Pure hashing works without entropy; Node key/Hash/Hmac APIs remain deferred |
| All other Node namespaces/APIs in the inventory | Deferred or unavailable according to the original per-API plan | Only separately selected standard interfaces | No current runtime support inferred from an inventory row, web global, isolated prototype or successful import of another module |

Native registration and computational native code are distinct. Path and Events
use real native registration but keep small API algorithms in guest JavaScript.
StringDecoder, Assert and Querystring have compiled OFF component evidence and
[joint Runtime HTTP replay on both stock hosts](../../tests/node-compat/milestones/foundations-v11/reports/httpAudit.json). Async-context investigations
still provide no installed `node:async_hooks` module.
The [execution ledger](execution-status.md) is the current acceptance index.

## Initial module and export contract

| Module / API | Disposition and implementation | Capability | Deviations and validation |
| --- | --- | --- | --- |
| `buffer`, `node:buffer`: `Buffer` | Partial Uint8Array facade + proposed native hex kernel | None | Only overloads below; differential and component tests; C++ uncompiled |
| `Buffer.alloc(size, fill?)` | Partial; integer size and numeric fill | None | 0 through 16 MiB; zero-init; no string fill/pool/unsafe allocation; Node byte vectors and boundary failures |
| `Buffer.from(string, encoding?)` | Partial; existing native TextEncoder UTF-8, native hex template | None | `utf8`, `utf-8`, `hex` (case-insensitive); missing/empty string encoding means UTF-8. 1,048,576 source UTF-16 units; hex stops before invalid pair and drops odd nibble; Node vectors |
| `Buffer.from(Uint8Array)` | Partial; copy visible bytes | None | Copies nonzero-offset views; no alias with input; no other typed arrays/array-likes/DataView; identity/copy tests |
| `Buffer.from(ArrayBuffer, offset?, length?)` | Partial; share backing buffer | None | Nonnegative integer arguments; 16 MiB view cap; shared/resizable backing excluded; offset/length and mutation tests |
| `Buffer.isBuffer`, `Buffer.isEncoding`, `Buffer.byteLength` | Private brand, explicit encoding set, bounded byte count | None | byteLength accepts selected strings/U8/AB; cross-realm and detached cases require decision; other Node encodings not claimed |
| `buf.toString(encoding?, start?, end?)` | Partial; UTF-8 decoder preserving BOM or hex kernel | None | Integer ranges with clipping; malformed UTF-8 uses replacement; unknown encodings and unsupported overloads fail; full coercion parity not claimed |
| `buf.slice`, `buf.subarray`, `.buffer`, `.byteOffset`, `.byteLength`, `.length`, `.parent`, `.offset`, numeric indices | Real typed array/view behavior | None | slice/subarray share storage; copied construction does not. Preserve inherited U8 behavior except explicitly overridden Node overload methods. Species/map/filter tested; mutation/prototype edge cases deferred |
| `INSPECT_MAX_BYTES`, `kMaxLength`, `kStringMaxLength`, `constants` | Explicit numeric constants, finite frozen constants object | None | 50; 16 MiB; 32 MiB; not Darwin/Node maximums. No coercible function placeholders |
| `Blob`, `File`, `SlowBuffer`, `atob`, `btoa`, `isAscii`, `isUtf8`, `resolveObjectURL`, `transcode` | Explicit imported callable names, invocation unavailable | None | Existing web implementations are candidates for future reuse; currently throw. This avoids implying Node semantics solely from web globals |
| Buffer constructor and all other Node Buffer-specific own functions | Unavailable explicit throwing functions | None | Includes unsafe allocation, compare/concat/copy/search/write, all numeric readers/writers, other codecs, JSON/inspect and fill overloads. See finite manifest and tests |
| `child_process`, `node:child_process` | Import-only ESM module with default | None; no P2 spawn/IPC service | Exact names: `ChildProcess`, `_forkChild`, `exec`, `execFile`, `execFileSync`, `execSync`, `fork`, `spawn`, `spawnSync`, `default`. All nine callables throw `ERR_SM_NODE_UNSUPPORTED` on call/new, including during snapshot |

All fourteen named Buffer exports plus default match the oracle's namespace; operational support is deliberately narrower. Default members have the same function/object identities as named exports. Defaults are frozen; Node's mutable CJS default and `syncBuiltinESMExports` are not supported. `then` is absent, namespace enumeration is safe, and no universal Proxy or property-read trap is used. Unknown named imports fail linking. The private factory/reference codec exports are not public Node exports.

## Pure modules and foundational streams

All rows in this section are **deferred** as Node modules in this milestone. Guest-only implementations require no host services. Small JS semantic facades are preferred to native rewrites when computation does not dominate.

| Modules / relevant exports | Strategy and capability | Required deviation / validation |
| --- | --- | --- |
| `assert`, `assert/strict` | Audited JS assertions; no capability | Deep equality, errors, cyclic objects, typed arrays and strict/default alias identities; pinned Node tests |
| `events` | JS EventEmitter, `once`, `on`, EventEmitterAsyncResource after context design | Web EventTarget is not EventEmitter. Listener ordering, reentrancy, abort, rejection capture and async iteration |
| `stream` | Node JS state machines plus native byte kernels | `Stream`, `Readable`, `Writable`, `Duplex`, `Transform`, `PassThrough`, `pipeline`, `finished`, `compose`, `duplexPair`, `addAbortSignal`, `promises`, predicates, high-water controls and oracle internal helper exports are individually inventoried. Backpressure, object mode, lifecycle, half-close and error order |
| `stream/promises` | Promise facade over classic stream lifecycle; no capability | `finished`, `pipeline`, `default`; rejection and cancellation cleanup |
| `stream/consumers` | Small facade over readable adapters and Buffer; no capability | `arrayBuffer`, `blob`, `buffer`, `json`, `text`, default; both web and Node stream inputs |
| `stream/web` | Reuse existing native web implementations after export-by-export parity gate | Readable/Writable/Transform streams, all public readers/writers/controllers/BYOB classes, queuing strategies, TextEncoder/DecoderStream, Compression/DecompressionStream; presence/constructor identity and WPT/Node differential. No `stream/iter` in Node 22 inventory |
| `string_decoder` | Incremental native codec + JS retained state | `StringDecoder`; split-sequence and flush behavior differs from simply calling TextDecoder |
| `path`, `path/posix`, `path/win32` | JS path algorithms, declared default POSIX and virtual cwd `/` | Relative resolve uses profile cwd, not the host cwd. Optional deployment cwd requires explicit `cli/environment`. Exact edge-case vectors for both variants |
| `url` | Existing native WHATWG URL/URLSearchParams + separate legacy facade | `parse`, `format`, `resolve`, legacy Url, file URL and domain conversions require Node-specific tests; URL support alone is insufficient |
| `querystring`, `punycode` | Small guest algorithms; native codec only if useful | Querystring is not URLSearchParams; deprecated punycode still requires exact Unicode vectors |
| `util`, `util/types`, `sys` | Mixed JS utilities/native introspection; sys aliases util | Explicit predicates, format/inspect, promisify/callbackify and symbols; no V8 internal assumptions. Node tests for cycles and exotic objects |
| `diagnostics_channel` | Small JS channel facade after async context | `channel`, subscription APIs, tracing channels and `Channel` require context/error lifetime tests |

`buffer` and classic streams are joint foundations: swapping only application imports leaves adapters' internal Feross/unenv Buffer dependencies intact. Resolve those dependencies and global Buffer injection to the same canonical module, or reject the mixed bundle.

## Host capability modules

The interface package version is **0.2.10** for every production capability selected below. These are candidate capabilities, not permissions granted to all applications. Interface use requires a matching selected world and host grant. Namespace/individual member records remain authoritative in the CSV.

| Module / API group | Disposition and implementation | Standard capability and limits | Validation |
| --- | --- | --- | --- |
| `fs`, `fs/promises` descriptor/read/write/stat subset | Deferred native descriptor adapter + JS callbacks/promises | `filesystem/types`, `filesystem/preopens`, `io/streams`, `io/poll`; preopen rights only. No global host root or guaranteed cwd | Rights denial, `..`/symlink confinement, short reads/writes, file offsets, async close and cancellation |
| FS watch/chown/chmod family | Unavailable with selected P2 subset | No watcher/ownership/permission-mode interface selected; do not fake success | Per-operation identifiable throws; named constants remain typed |
| `dns`, `dns/promises`: restricted lookup | Deferred native IP lookup | `sockets/ip-name-lookup`, `sockets/network`, `sockets/instance-network`; host policy and address results | IPv4/IPv6, allow/deny, cancellation and family ordering |
| DNS record queries, Resolver/server configuration | Unavailable in this profile | No portable MX/TXT/SRV/CNAME/SOA/TTL resolver/server API from P2 IP lookup | Reject operations; no custom Jco DNS capability |
| `net` TCP | Deferred native socket resource + classic streams | `sockets/tcp`, `tcp-create-socket`, network/instance-network, IO streams/poll; no Unix-domain socket/fd injection | Partial writes, half-close, connect/listen policy, teardown and backpressure |
| `dgram` UDP | Deferred native resource adapter | `sockets/udp`, `udp-create-socket`, network/instance-network, `io/poll`; do not assume multicast/socket-option portability | Datagram boundaries, address family, limits and permission failures |
| `http` limited requests/responses | Deferred WASI HTTP bridge | `http/types`, `http/outgoing-handler`, optional exported `http/incoming-handler`, IO streams/poll | Streaming, trailers, cancellation and mapping errors. Node Server.listen/raw sockets/Agent internals/upgrades are not furnished by this interface |
| `https` limited HTTPS requests | Deferred HTTP bridge; Node TLS surface unavailable | Same HTTP capabilities; TLS transport/cert trust governed by host | Reject unsupported Node client-certificate, ALPN, custom trust and socket controls instead of ignoring them |
| `tls`, Node HTTP/2 sessions via `http2` | Unavailable initially | **P2 sockets do not provide TLS**. HTTP may use HTTP/2 internally without exposing Node sessions/settings/push | Throwing manifests only if explicitly admitted; future guest TLS needs trust/time/cert validation design |
| `crypto` deterministic primitives | Deferred native guest OpenSSL/web primitive reuse + Node facade | No host import for pure hashing/ciphers; `random/random` only when entropy is needed | Known answers, Node algorithm/KeyObject/Hash/Hmac parity, key ownership and RNG reseeding |
| `zlib` | Deferred guest zlib; assess Brotli separately | None; no `jco:node/zlib` host service | Sync/callback/stream modes, formats/options/error vectors, final size and throughput |
| `timers`, `timers/promises` | Deferred Node scheduling facade over native event loop | `clocks/monotonic-clock`, `io/poll` | `Timeout`/Immediate/ref/unref, scheduler.wait/yield, nextTick/microtask/immediate ordering and teardown |
| `process` bounded env/args/stdio/exit subset | Deferred explicit JS facade with native capability calls | Selected CLI environment/exit/stdin/stdout/stderr; optional clocks for hrtime | Read deployment env after resume, never build env. No OS process, pid fiction, signals, uid/gid mutation or addon loading |
| `console` | Deferred Node formatting over existing native console sink | CLI stdout/stderr and IO streams | Native web console does not imply Console class/inspect parity |
| `perf_hooks` | Deferred Node facade over monotonic clock | Monotonic clock, optional wall clock for explicit origin policy | No fabricated V8/libuv/process metrics; observer entries and resume origin |
| `readline`, `readline/promises` | Deferred line editing after streams | CLI stdio, IO poll/streams, optional terminal interfaces | Nonterminal mode, Unicode, abort and absent TTY |
| `tty` | Unavailable full Node fd/termios APIs | Standard CLI terminal handles could permit narrow future detection only | Reject unsupported terminal setters; no host fd assumptions |
| `os` | Deferred profile constants/pure conversions; host introspection unavailable | No general P2 system CPU/memory/hostname/network interface service | Explicit values/throws, no invented host facts |

## Runtime and engine modules

| Modules | Disposition / required design | Capability and validation |
| --- | --- | --- |
| `async_hooks` | Deferred AsyncLocalStorage/AsyncResource/native propagation; broad hook parity separately reviewed | Guest job and task metadata, no host service; interleaved await/rejection/I/O/timer tests and request teardown |
| `module` | Deferred inventory/introspection facade only after bundler contract | No runtime Node loader, dynamic require, createRequire, mutable builtin synchronization or package loader assumed |
| `constants` | Deferred finite guest constants by selected ABI | Node oracle's Darwin constants are an inventory, not valid guest OS constants; compare types and declared values |
| `test`, `test/reporters` | Deferred guest runner; prefix-only specifiers | `after`, `before`, describe/it/test/suite, mocks, assertions, snapshots; reporter APIs. CLI isolation/process behavior excluded until separately designed |
| `sqlite` | Deferred optional guest SQLite | Memory-only DB needs no host capability; file DB needs FS. Native extension loading not selected; size/SQL/lifetime tests |
| `worker_threads`, `cluster`, `child_process` operations | Unavailable process/IPC/worker model | No selected standard P2 process-spawn/worker host service; child_process alone receives import-only template |
| `v8`, `inspector`, `inspector/promises`, `trace_events` | Unavailable V8/Inspector/native tracing APIs | SpiderMonkey/debugger support does not implement these APIs; no new host services |
| `vm` | Unavailable initially | Do not substitute eval; realms/context/module/timeouts need independent SpiderMonkey design and security review |
| `wasi`, `sea`, `repl`, `domain` | Unavailable Node WASI launcher, SEA assets, REPL and legacy domains | Already running in a component does not supply Node's WASI launcher; no fake environment |
| `_http_*`, `_stream_*`, `_tls_*` builtin IDs | Unavailable private modules | Inventory includes them because the oracle lists them; public profile intentionally excludes them |

## Globals and aliases

Existing native ECMAScript globals come from SpiderMonkey; their presence is not a claim about Node-only globals. Existing native web globals (URL, encoding, Blob/File, Event/EventTarget/CustomEvent, AbortController/Signal, console, performance, timers, streams, structuredClone, queueMicrotask, fetch/Request/Response/Headers/FormData and web crypto) are candidates for Node global reuse, with per-descriptor/constructor/behavior tests. Some Node web exports, controllers and stream wrappers are not yet installed globally; inspect each before aliasing it.

The profile's only proposed added global in this milestone is bounded `Buffer`, equal to `node:buffer`.Buffer. `process`, `global`, `setImmediate`/`clearImmediate` are deferred with explicit future behavior; `global` could alias globalThis after descriptor policy is selected. Ambient `require`, `module`, `exports`, `__dirname`, `__filename` are not supplied at runtime. Build-time static CJS lowering can introduce explicit lexical bindings under its own tested contract. Worker/message-port and V8/performance extras are not inferred from web API support.

All ordinary builtin aliases in the inventory have bare and `node:` spellings; the selected bundler canonicalizes admitted aliases before adapter resolution. `test`, `test/reporters`, `sea`, `sqlite` remain **prefix-only**. `sys` is a future util alias; `path/posix`/`path/win32`, `assert/strict`, the stream subpaths, `dns/promises`, `fs/promises`, `readline/promises`, `timers/promises`, `inspector/promises`, `util/types` have their own exact manifests. Not all aliases are automatically registered. Runtime CommonJS and mutable builtin export synchronization remain outside the contract.

Reference semantics: [Node 22 Buffer](https://nodejs.org/download/release/v22.14.0/docs/api/buffer.html), [child_process](https://nodejs.org/download/release/v22.14.0/docs/api/child_process.html), [ESM built-ins](https://nodejs.org/download/release/v22.14.0/docs/api/esm.html#built-in-modules); capability limits are also sourced to the checked-in WIT and pinned toolchain files in the architecture audit.
