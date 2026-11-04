# Classic Stream source audit and next dependency gates

**No classic Stream module is installed by this work.** This directory contains
pinned source/reflection evidence and small Node-host reference experiments.
It does not claim compatibility from native Web globals, a package import or a
successful bundle. Production builtins, CMake and accepted v6 records are unchanged.
The separate [Stream Web audit](../foundation-stream-web/) owns native Web parity.

Subsequent dependency progress is recorded separately from this original audit.
The [accepted v8 installed allocator](../foundation-alloc-unsafe/installed/README.md)
now supplies bounded fresh zeroed `Buffer.allocUnsafe` and executes the actual
`BufferList.concat/_getBuffer` excerpts; this removes the original allocation
blocker for its documented inputs. It does not supply a tick queue or classic
stream API. The [m0.9 native stream/web integration](../foundation-stream-web/integration-candidate/README.md)
is applied and awaiting fresh engine gates, including actual async iteration and
DataView adapters. Native abort-listener and reentrant-listener corrections are
[staged m0.10 proposals](../foundation-add-abort/m0.10-proposal/README.md), still
unapplied. The original source hashes, demand records and Node-only results below
remain unchanged.

## Exact pinned inventory

[inventory.node-v22.14.0.json](./inventory.node-v22.14.0.json) derives actual ESM
exports, function names/arities, class own methods/accessors/symbols, default
relationships and source hashes from Node **v22.14.0**:

| Module / proposed bare alias | Exact ESM exports |
| --- | --- |
| `node:stream` / `stream` | 24: `Duplex, PassThrough, Readable, Stream, Transform, Writable, _isArrayBufferView, _isUint8Array, _uint8ArrayToBuffer, addAbortSignal, compose, default, destroy, duplexPair, finished, getDefaultHighWaterMark, isDestroyed, isDisturbed, isErrored, isReadable, isWritable, pipeline, promises, setDefaultHighWaterMark` |
| `node:stream/promises` / `stream/promises` | `default, finished, pipeline` |
| `node:stream/consumers` / `stream/consumers` | `arrayBuffer, blob, buffer, default, json, text` |

`stream.default === stream.Stream`, `Stream.Stream === Stream`, and
`stream.promises === promises.default`. Default methods initially share their named
bindings. The `util.promisify.custom` getters of callback `pipeline` and `finished`
return the matching promise functions. Root default is a callable Stream function,
not an object of constructors. Node22 has neither `stream/iter` nor consumer `bytes`.
The recorded Darwin byte HWM is64KiB/object HWM16; pinned Node uses16KiB on Windows.
A portable profile must choose/document its default, not invent a host platform.

[api-matrix.json](./api-matrix.json) includes **166 derived API rows**, including
constructor statics/prototypes and symbols. Every row is currently **deferred**:
there is no installed import-only Stream stub or supported Node Stream namespace.
Native Web primitives are separate partial capabilities, not evidence that these
Node rows work. The matrix records proposed strategy, capability and validation.

Primary sources are pinned [stream.js](https://github.com/nodejs/node/blob/v22.14.0/lib/stream.js),
[promises](https://github.com/nodejs/node/blob/v22.14.0/lib/stream/promises.js),
[consumers](https://github.com/nodejs/node/blob/v22.14.0/lib/stream/consumers.js),
[task queues](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/process/task_queues.js),
and inspected [consumer](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-consumers.js)/
[pipeline](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-pipeline.js)
tests. The full upstream suites have not run against StarlingMonkey Streams.

## Actual adapters and dependency demand

[source-audit.json](./source-audit.json) hashes **74 files**, records **225 literal
dependency edges** and **53 demand sites**, and separates the portable core's
reachable graph from unused package main/browser wrappers. Locked readable-stream
4.7.0 is a Node18.19-derived JS core. Use its explicit `lib/stream.js` entry when
evaluating reuse; its package main can branch on `READABLE_STREAM` and require
`stream` again, and its browser default is Readable rather than Node's Stream.

The locked Jco1.40.0 `createStreamBuiltin` routes core dependencies to shared
Buffer/EventEmitter/StringDecoder and a private scheduler, and Jco-std0.10 adds
Node24.20-derived lifecycle/Web adapters. It also advertises nonpinned
`stream/iter` and `consumers.bytes`. Its `callableEmitter` uses a constructor Proxy
for an unenv ES class; our native EventEmitter is already callable. Do not adopt
that adaptation or its prototype mutations without identity/initialization tests.
Unenv rc24's standalone Stream default is an object and many operations are
explicit stubs; its promise/consumer modules are also stubs. Neither is a Node22
oracle. Published readable-stream packages omit their upstream conformance tests.

| Required dependency | Exact demand | Boundary at the original source audit |
| --- | --- | --- |
| Buffer allocation | `internal/streams/buffer_list.js::concat/_getBuffer` call `Buffer.allocUnsafe` | Current bounded Buffer deliberately throws; byte-mode aggregation is blocked |
| Buffer views/codecs | `lib/stream.js::_uint8ArrayToBuffer`, `readable.js`, `writable.js` use `from`, `isEncoding`, UTF8 conversion | Shared AB/offset relationships must be preserved; fixed unshared backing and UTF8/hex restrictions remain |
| Abort listener | `ours/util.js` selects `require('events').addAbortListener || fallback`; pipeline/eos/add-abort-signal call it | Current truthy deferred export wins; fallback never runs and those paths throw |
| Scheduler | `readable/writable/destroy/end-of-stream/pipeline/from/duplexify` use `process.nextTick` | No production Node tick queue; queueMicrotask shim has measured differences |
| StringDecoder | `ReadableState(options.encoding)` and `Readable.setEncoding` require `string_decoder/` | Optional native decoder supports UTF8/hex only; other encodings remain deferred |
| Cancellation and private utilities | AbortController/Signal, Symbol.dispose, own `ours/util`, `ours/errors`, primordials | Reuse native abort only after callback/disposal/propagation semantics; no broad public util/assert demand follows |

Trailing-slash `process/` and `string_decoder/` are npm requests, not admitted
native aliases. Jco has explicit importer-scoped rewrites for these. A native
factory/bundler must make shared dependencies explicit and reject duplicate npm
Buffer/emitter/decoder implementations. Truthy unsupported operations must not be
silently replaced, ignored or forced through a fallback.

## Verified scheduling and ownership differences

[reference-results.json](./reference-results.json) executes only small valid Node
host cases against the exact standalone Jco scheduler/consumer source:

| Boundary: promise enqueued before nextTick | Node22 trace | Jco microtask-batch trace |
| --- | --- | --- |
| Native task callback | tick, nested-tick, promise-first, microtask | promise-first, tick, nested-tick, microtask |
| Inside a Promise job | promise-first, microtask, tick, nested-tick | promise-first, tick, nested-tick, microtask |

This does **not** mean Node interposes ticks between Promise reactions. Its
`processTicksAndRejections` drains the tick queue and a complete microtask
checkpoint in a boundary-sensitive loop. Initial ESM evaluation, static CommonJS
lowering into ESM and deployed host callback entry must have separate explicit
oracles/contracts. A queueMicrotask shim cannot move a tick ahead of existing
promise jobs or flatten those two boundaries into one correct order.

One reused mutable Uint8Array yielded twice then changed to67 gives Node consumer
`arrayBuffer` bytes `[67,67]`; Jco gives `[65,66]`. Pinned Node collects Blob-part
references until Blob construction, whereas Jco `collectParts/toArrayBuffer`
copies each part early. Avoiding copies here is observable behavior, not only an
optimization. Any consumer implementation must retain GC-traced JS values and
copy at the specified time, with final backing validation; never retain a raw
borrowed span across await. The safe reference case performs no detachment, GC
fault injection or unsafe native probe.

[node-reference-results.json](./node-reference-results.json) additionally records
11 bounded ordinary Node API groups in reusable `valid-api-checks.mjs`: object
pipeline/flush, backpressure/drain, cork/writev, destroy/error/close, shared U8
offsets, Node22 DataView writes, consumer decoding/mutable parts/JSON, and abort
cleanup. They are future differential vectors, **not** candidate or component
passes. Byte inputs share backing at offset1 in the reference; pipeline abort
retains the original reason as cause while destroying both ends.

## Existing guest integration sites and lifecycle

* `runtime/engine.cpp::init_js` uses `js::UseInternalJobQueues`.
* `runtime/event_loop.cpp::EventLoop::run_event_loop` drains `js::RunJobs`, runs
  FinalizationRegistry cleanups, checks interest, then selects/runs the oldest
  ready `api::AsyncTask`. It has no Node tick/check/libuv phases.
* `builtins/web/queue-microtask.cpp::queueMicrotask` uses
  `JS::CallOriginalPromiseResolve` and `JS::AddPromiseReactions`. Exception routing
  needs actual tests; the public API does not create a normal chained Promise.
* `TimerTask` roots/traces callback/arguments, owns monotonic-clock subscriptions
  and runs through the task queue. `REQUEST_HANDLER_ONLY` prohibits public timer
  creation during preinit. `AsyncTask::select` can create a zero-duration clock
  pollable when mixing immediate and pollable tasks; immediate tasks are not a
  substitute for a pure priority tick queue.
* The exact ComponentizeJS `embedding/embedding.cpp` compiled in v6 is hashed and
  verified against its receipt. `call()` increments interest, invokes JS, adds
  promise completion reactions and drains until settled. Its deployed entropy
  barrier is permanent policy state, **not** a request owner or context token.

The [existing async-context audit/probes](../async-context/README.md) already
identify actual SM147 `JS::JobQueue` host-defined-data hooks, the queue preference,
registration/Promise-creation timing, mutable resource cells and fresh owner
requirements. Reuse that evidence; do not wrap `.then` or invent an embedding API.
Node's nextTick source captures the current context frame/resource at enqueue,
then restores it around callback execution. Future guest tick entries need traced
callback/arguments/context, correct callback receiver/error policy and RAII
restoration. Request cancellation must dispose registered work under its captured
resource before dropping owner roots. No production ALS support follows yet.

## Dependency-ordered proposal

1. **Accept dependency contracts first.** Review/version a bounded zeroed no-pool
   `allocUnsafe` policy or keep affected byte APIs deferred; test its size/errors,
   brand/backing and aggregation demands. Implement/test Node abort-listener
   semantics (including already-aborted timing, disposal and resistance to event
   propagation interference), or keep dependent operations deferred. Preserve the
   selected decoder's explicit encoding limits. No silent shim bypass.
2. **Native guest scheduler/resource gate.** Implement a private traced tick queue
   using actual guest hooks, with Node boundary-sensitive full-checkpoint ordering,
   reentry/starvation limits, callback failures, cancellation, init/resumption and
   owner cleanup. Pure scheduling must import nothing. Integrate ALS resource
   capture from the accepted probe design; public ALS and Node timers remain
   separately gated. No host modification/service is needed.
3. **Independent small consumers route.** After Blob/decoder ownership and iterable
   validation, six finite exports can serve bounded plain async/sync iterables
   without classic streams or nextTick. Reuse owned native Blob/UTF8/Buffer where
   exact, preserve mutable-part timing and cancellation/error precedence. SM147
   ReadableStream lacks async iteration, so Web inputs need an explicitly audited
   reader adapter/brand boundary, not an assumption from the global class. The
   separate Web audit owns that engine assessment. Do not expose Node24 `bytes`.
4. **Bounded classic core.** Adapt a pinned, licensed JS state machine and only
   required Node22 changes; prefer native storage/byte work. Start with explicit
   object/UTF8 byte modes, constructors, read/write/backpressure, finish/error/close,
   cork/writev, destroy and iteration. Declare all deferred methods/overloads using
   finite real bindings and identifiable call/new errors. Do not advertise all
   readable-stream methods merely because they bundled.
5. **Lifecycle and promise facade.** Add pipeline/finished/compose and exact
   default/promisify aliases once cancellation, multiple errors, callback ordering,
   cleanup and return identities pass. Web-state predicates/finished observation
   cannot be implemented by acquiring a reader and changing the lock as a side effect.
6. **Bridges and hosts.** Add only verified toWeb/fromWeb pairs, preserving locks,
   transfer/copy behavior, desired-size/backpressure and error/cancel ownership.
   Run actual components, snapshot/reuse, strict init failures, optional-OFF
   admission and both unmodified hosts. Filesystem/HTTP/socket streams remain
   separately selected resource adapters; pure streams do not require their imports.
7. **Measure before expanding.** Compare stripped applications on the same frozen
   engine/packager/host for size, cold/startup, memory and throughput. Large remaining
   byte-copy loops may justify native guest code after GC/ownership review.

Only explicit standard interfaces may be added for real resources: timer variants
need selected `wasi:clocks/monotonic-clock@0.2.10` and `wasi:io/poll@0.2.10`, with
the final type/import closure audited; HTTP/filesystem/socket variants need their
own narrow catalogue/world. This audit selects none, infers no TLS from sockets
and requires no Wasmtime/wasmCloud changes. No native stream source is implemented
here. Reproduction scripts are `inventory.mjs`, `audit-sources.mjs`,
`reference-oracles.mjs`, `api-matrix.mjs` and optional Node-only `run-node.mjs`,
using the pinned Node22/toolchain.
