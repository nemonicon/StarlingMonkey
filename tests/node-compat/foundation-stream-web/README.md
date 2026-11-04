# stream/web source audit and isolated probe

Subsequent evidence: the [m0.9 integration and native gates](production-adoption/README.md)
now install bounded `node:stream/web` behind a default-OFF flag. Actual native
constructor capture, brands, codec/iteration/DataView adapters, aliases/CJS and
snapshot cases pass on a new 302-input Release engine with zero imports. A
separate corrected OFF engine proves native controller guards and denies both
module aliases. The prior-module/strict replay and both-host HTTP gates now pass
in the [accepted v9 checkpoint](../milestones/foundations-v9/README.md). The text and `matrix.json` below
preserve the original source audit and probe, not the current installed status.

The separate [installed matrix supplement](installed-matrix-v9.README.md)
records18 exports,184 Node-own member observations and eight semantic operations.
Node descriptors and private symbol descriptions are inventory evidence, not
assumed native implementations. Unavailable/deferred/unverified members remain
distinct; the original matrix and accepted archive stay unchanged.

**`node:stream/web` is not installed by this work.** This directory contains a
pinned inventory, source analysis and isolated namespace-composition probe,
not a production manifest or compatibility claim. No builtin, CMake flag or
engine source changes are made. Node is exactly **v22.14.0**;
SpiderMonkey is the pinned SpiderMonkey147 source revision
`9dab3d6f643e926a340c391ea30968e940390dec`.

A later, separate [bounded codec/receiver candidate](candidate/README.md) now
implements the two UTF8 codec facades and explicit guards in an isolated
simulation. Its component receipt does not replace the eleven-case audit or
retained-constructor evidence below. Native capture/registration remains
uncompiled, and the module remains uninstalled.

## Exact export inventory and candidate strategy

[Node's pinned module](https://github.com/nodejs/node/blob/v22.14.0/lib/stream/web.js)
exports seventeen constructors; ESM adds `default`, for exactly **18 names**.
The ordinary default object initially maps each name to the same function.
Every named constructor is also the corresponding Node global. None of
`TextEncoder`, `TextDecoder`, Node classic Readable/Writable or zlib helpers is
an export of this module. The future aliases are `node:stream/web` and
`stream/web`; neither is registered in the selected v6 profile.

All candidate implementations are guest code and require **no host interface**
for the pure operations considered here. Importing the future module must not
implicitly select HTTP, filesystem, clocks, entropy or a custom host service.
The [machine-readable matrix](matrix.json) retains exact Node static/prototype
inventories, deviations and validation gates.

| Exact export | Verified source / ordinary observation | Candidate strategy and outstanding gate |
| --- | --- | --- |
| `ReadableStream` | Real SM global; basic reads, lock/release, cancel, pipeTo, tee pass selected cases | Reuse identity; add audited `from`, `values`, async iterator. No complete parity claim. |
| `ReadableStreamDefaultReader` | Real SM global; read/closed/release/cancel observed | Reuse; additional brand/error/pending-read tests. |
| `ReadableStreamBYOBReader` | Real SM global; basic BYOB detaches destination and returns bytes | Reuse; **reject unsupported `min>1` explicitly**, then implement/test minimum-fill before supporting it. |
| `ReadableStreamBYOBRequest` | Real SM global; `respond` observed | Reuse; `respondWithNewView`, close/error and ownership boundaries need tests. |
| `ReadableByteStreamController` | Real SM global; request/close observed | Reuse; enqueue/auto-allocation/cancel/error and remaining transfer cases need tests. |
| `ReadableStreamDefaultController` | Real SM global; enqueue/close observed | Reuse; desiredSize, error and reentrancy gates remain. |
| `TransformStream` | Native Starling global; basic transform/close observed | Reuse; cancellation/error/backpressure and strategy gates remain. |
| `TransformStreamDefaultController` | Global intentionally deleted; actual instance retains native constructor | Capture the real retained prototype constructor; never fabricate a controller class. |
| `WritableStream` | Real SM global; writes/close/abort and lock state observed | Reuse; direct `stream.close`, pipeline abort and error propagation need more tests. |
| `WritableStreamDefaultWriter` | Hidden global; actual instance retains native constructor and passes identity tests | Capture the real cached/native constructor. |
| `WritableStreamDefaultController` | Hidden global; native instance/constructor retained; **`signal` absent** | Reuse real class; native AbortSignal/controller work required. Do not fabricate signal semantics from sink.abort. |
| `ByteLengthQueuingStrategy` | Real SM global; HWM/size observed | Reuse; descriptor, conversion, shared size-function and reentrancy tests remain. |
| `CountQueuingStrategy` | Real SM global; HWM/size observed | Reuse; same remaining strategy gates. |
| `TextEncoderStream` | No native/global definition found | Small audited facade over native TransformStream/TextEncoder; preserve a trailing high surrogate across chunks. Not implemented here. |
| `TextDecoderStream` | No native/global definition found | Small facade over fixed native TextDecoder with captured internal `stream:true`; validate BOM/fatal/flush/ownership policy. Not implemented here. |
| `CompressionStream` | Existing native zlib class, gzip/deflate/deflate-raw | Deferred reuse pending source hardening and bounded tests below; no compression transform was invoked. |
| `DecompressionStream` | Existing native zlib class, same formats | Deferred reuse pending ownership, cleanup, error and output-budget gates. |
| `default` | Ordinary mutable object; initial named/default equality | Explicit seventeen-member record, named bindings snapshotted; no syncBuiltinESMExports/runtime require promise. |

This is a candidate matrix. The entire module's **production status is deferred**.
Native availability, a matching constructor name or a passing ordinary case is
not evidence that every method or overload conforms.

## Actual native installation and missing APIs

`runtime/engine.cpp::create_content_global` enables SM streams and invokes
`JS::InitRealmStandardClasses`; `create_initializer_global` also enables them.
The SM `js/ProtoKey.h` stream keys include readable/default/BYOB classes,
writable classes and both queuing strategies. Use the **content realm** when
capturing constructors, preserving brands shared with Request/Response bodies.

`builtins/web/streams/streams.cpp::install` registers native source/sink helpers,
TransformStream/controller, Compression/DecompressionStream and BufReader.
`TransformStream::init_class` invokes
`ReadableStream_additions::initialize_additions`, which replaces `pipeTo` and
`pipeThrough` with the existing optimized native-sink path. Ordinary custom JS
sources/sinks use the original SM behavior; the probe does not validate HTTP
body-handle handoff.

The exact SM `ReadableStream.cpp` explicitly marks async iteration unimplemented;
the class tables provide no `values` or static `from`. The real v6 observations
confirm all three are absent. SM `ReadableStreamBYOBReader_read` consumes no
second argument, explaining its ignored Node22 minimum-fill option.
`WritableStreamDefaultController` has no `signal` property in its source table
or observed prototype.

Three missing globals are **real existing classes**, not absent implementations:
the SM writable writer/controller use `ClassSpec::DontDefineConstructor`;
Starling `TransformStreamDefaultController` extends `BuiltinNoConstructor`,
whose `init_class` explicitly deletes its global name. The ordinary component
proves each retained prototype has a function constructor, that
`constructor.prototype === prototype`, and that the instance passes
`instanceof constructor`.

A **separate** ordinary constructor gate now goes further:
[`constructors-component-results.json`](constructors-component-results.json)
constructs `new retainedWriterConstructor(fresh WritableStream())`, writes,
closes, awaits completion and releases the lock. Its trace/identity/locking
fields match Node. Plain calls, invalid arguments and already-locked streams
reject with TypeError. The two retained controller constructors reject both
call and construction with TypeError, as Node does. Node's error codes on
invalid/locked writer construction and illegal controller construction are
absent here; TransformStreamDefaultController arity is 1 rather than Node's 0.
The separate component `1a788072…da380` is 11,956,887 bytes, emits zero imports,
and passes two Jco calls and a fresh Wasmtime instance. These results are not
merged into or counted as the eleven-case 9/2 comparison.

For integration, the real public `JS_GetClassObject(cx, JSProtoKey,
JS::MutableHandleObject)` exists in the pinned `jsapi.h:204`; its implementation
calls `GlobalObject::getOrCreateConstructor`. The two writable classes have
real ProtoKeys. This audit has **not executed a new C++ call** to that API.
The alternative retained-prototype constructor identity is actually observed.
For the custom Transform controller, the existing public
`BuiltinImpl::proto_obj` root permits reading its real `constructor` property
without constructing temporary streams or snapshotting writer promises.
No invented embedding or host API is needed.

## Eleven ordinary cases in a real component

[`node-results.json`](node-results.json) is the exact Node oracle.
[`component-results.json`](component-results.json) records the frozen v6 OFF
Release engine `33b9cb24…cd59516`, all 285 verified source hashes, patched pinned
packager, final WIT/import audit, two Jco-hosted Wasm calls and a fresh stock
Wasmtime42.0.1 instance. The accepted component is
`a04beca6…095686`, **12,004,431 bytes**, with **zero host imports**. A queued,
closed snapshot-created readable resumes with its queued value on first call.

Nine of eleven selected cases match Node **exactly for the recorded fields**:
basic readable, cancel, writable abort, writable backpressure, transform,
pipeTo, tee, basic BYOB, and queuing strategies. Writable backpressure observes
desiredSize = 0 and a pending ready promise during the held write, then desiredSize = 1
and readiness after explicit release. Basic BYOB transfers the original
eight-byte destination to detached state and returns `[7,8]`.

Two differences are explicit, not filtered out:

- Writable-controller `signal` is an AbortSignal object in Node and undefined
  here; all other fields of that ordinary write/close trace match.
- For `read(Uint8Array(4), {min:2})`, Node returns `[1,2]` on its first read;
  SM returns `[1]`, then `[2]` on the second read. The underlying source supplies
  one byte per pull in both executions.

The five missing globals are exactly TextEncoderStream, TextDecoderStream,
TransformStreamDefaultController, WritableStreamDefaultController and
WritableStreamDefaultWriter. The isolated
[`prototype.mjs`](prototype.mjs) has real finite ESM declarations and an ordinary
default object; missing constructor exports are explicit throwing functions,
never blank objects or a Proxy. Those temporary stubs are **probe policy only**:
the real hidden native constructors should be reused in a production proposal.
No module-resolution/cache/CommonJS/native-registration parity is claimed by
this bundled namespace probe.

No native compression transform, shared/resizable/detached lifetime probe,
forced GC, raw-memory operation, fault injection, timer or host I/O is used.
The ordinary BYOB transfer is the API's own standard ownership transfer.
The original first accepted component/report remain in the external
`stream-web-probe` directory; `stream-web-probe-v2` adds explicit retained
constructor identity fields without changing the native engine.

## Compression source gates (not runtime fault demonstrations)

The existing C++ kernels should not be advertised as compatible solely because
their constructors exist:

- Both constructors pass an unchecked `JS_NewObjectForConstructor` result into
  `create`, which immediately dereferences it. Ordinary fallible allocation
  propagation needs a null check; no exhaustion probe was executed.
- `deflate_chunk` / `inflate_chunk` put the `value_to_buffer` pointer in
  `z_stream::next_in` across loops containing `JS_NewUint8Array` and
  `TransformStreamDefaultController::Enqueue`. Remaining-byte and callback/GC
  lifetime safety needs a proof or scoped reacquisition/owned input. This is
  a **source review gap**, not a demonstrated stale-pointer fault.
- Both classes use default class policy with **no finalizer**. The `z_stream`
  structure allocated with JS_malloc has no matching JS_free in these files;
  normal flush calls the zlib End routine and frees only the output buffer.
  Abort/cancel/error paths do not provide the needed owned-state cleanup.
- `inflate_chunk`'s unexpected-status branch is empty. Truncated, malformed,
  trailing and concatenated data require explicit predictable validation.
- A fixed 16 KiB scratch buffer does not bound total enqueued decompressed output.
  Expansion/input/output budgets and backpressure behavior need a deliberate
  profile policy and tests before hostile or large input is admitted.

Before reuse: root source objects before observable conversion, initialize
owned slots before fallible work, use matched exactly-once teardown for both
state allocations and zlib internals on success/error/cancel/GC, scope native
input borrowing across every allocating boundary, and validate status/end
conditions. No production hardening is applied here and no allocator recovery
claim follows from these source findings.

## Existing adapters and tests

Jco1.40's `createStreamBuiltin` registers stream, promises, consumers and iter,
but has **no stream/web adapter entry**. Its jco-std `stream/web.ts` file is a
classic/Web bridging helper, not the seventeen-export Node submodule. These
must not be mistaken for a complete portable stream/web implementation.
The inspected unenv2.0.0-rc.24 standalone shim selects globals or unimplemented
functions; it also assigns its CompressionStream binding from
`globalThis.DecompressionStream`. That shim is not a correct baseline identity
mapping to copy.

The existing checked-in WPT expectations include readable byte-stream,
transform, queue, cancellation and writable suites. Async-iterator expectations
are FAIL, consistent with source. Expectations are historical test metadata,
**not a newly executed WPT pass**. Existing E2E forwarding/tee cases and their
earlier execution evidence exercise HTTP body streams, not the complete Node
module namespace or every Web Stream method.

## Dependency-ordered bounded proposal

1. Capture existing native classes in the content realm, retrieving the three
   hidden constructors through verified existing roots/JSAPI. Validate real
   instance/constructor/global reuse; do not create temporary live handles or
   promises during factory installation.
2. Add an opt-in captured BYOB `read` wrapper before user code. Preserve the
   **native constructor/prototype identity**, capture the original read method,
   validate options using a pinned oracle, and reject supported-but-unavailable
   minimum-fill overloads with `ERR_SM_NODE_UNSUPPORTED` rather than ignoring
   them. Any global-prototype mutation is an explicit optional-profile policy
   requiring review, not an edit made by this probe.
3. Implement audited pure `from`/async iteration with correct lock, cancel,
   pending-operation serialization and preventCancel semantics. Add the two
   small codec-stream facades with native bulk work. Test split surrogate/UTF8
   sequences, BOM, fatal errors, coercion and cancellation.
4. Treat writable-controller `signal` as a real missing native feature. It must
   be tied to controller/abort state, not fabricated from sink.abort callbacks.
   Keep that deviation explicit until implemented and tested.
5. Harden native compression ownership/status/resource limits and validate
   bounded gzip/deflate/raw differentials, cleanup and backpressure before
   exporting it as supported.
6. Only then select a finite versioned production manifest/default-OFF flag and
   existing native factory/registration. Test import aliases, ESM/default/CJS,
   initialization failures, repeated component reuse, selected HTTP body
   integration, and final standard-WASI imports on both target hosts.

Future validation must add AbortSignal pipe cancellation, locked/error states,
pending read release, auto-allocated BYOB buffers, respondWithNewView, invalid
minimum arguments, constructor/prototype descriptors, transfer support boundaries
and the selected pinned WPT cases. Node worker/MessagePort transfer behavior is
not inferred from this guest's globals or from WASI sockets.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/inventory.mjs
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/path/to/v2/package/src/componentize.js \
NODE_COMPAT_ENGINE=/path/to/frozen-v6-off.wasm \
NODE_COMPAT_ENGINE_SOURCE_ROOT=/path/to/frozen-v6-source \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/run-component.mjs
```
