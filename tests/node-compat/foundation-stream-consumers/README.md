# Independent Stream consumers source audit

No `node:stream/consumers` module is installed by this work. This directory contains a Node v22.14.0 source/oracle audit and a bounded host-only prototype with real finite ESM exports. It does not install classic streams, a Web reader adapter or a Node scheduler. Production/CMake/registration files and accepted v6/v7 evidence are unchanged.

## Exact Node contract and observations

[node-results.json](node-results.json) derives five async functions, each arity 1, plus `default`: `arrayBuffer`, `blob`, `buffer`, `json`, `text`. The bare alias is `stream/consumers`. Default is an ordinary mutable object whose initial property order is `arrayBuffer, blob, buffer, text, json`; each initially equals its named binding. Async functions are nonconstructible. There is no Node22 `bytes` consumer export.

Pinned [Node source](https://github.com/nodejs/node/blob/v22.14.0/lib/stream/consumers.js) has two distinct algorithms: `blob` collects part references until iteration ends, then constructs Blob; `arrayBuffer` reads that Blob, and `buffer` wraps the returned ArrayBuffer. `text` eagerly decodes byte chunks, appends string chunks directly and flushes once after iteration. `json` parses the completed text. The [pinned tests](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-consumers.js) cover classic/Web inputs, object-mode parts and incomplete UTF8; they have not run against a guest consumer here.

The 30 ordinary Node groups comprise 18 text/JSON groups and 12 Blob/ownership groups. Some useful results are:

| Input/action | Node22 observation |
| --- | --- |
| Yield one U8 twice, changing A→B→C before completion | `arrayBuffer` yields `[67,67]`; `text` yields `AB`. |
| Change the retained part when final `next()` returns done | Blob collection observes the final mutation. |
| Byte `E2`, string `X`, bytes `82 AC` | `text` is `X€`; Blob text is `�X��`. Strings do not flush decoder state. |
| Separate strings containing high/low surrogate halves | `text` concatenates to `😀`; Blob repairs each part and yields `��`. |
| String before a byte BOM | It does not consume the byte decoder's initial BOM state. Literal string BOM remains literal. |
| Body decoding error, with rejecting iterator `return()` | Original TypeError/`ERR_INVALID_ARG_TYPE` wins; return is called once. |
| `next()` rejects | Original error propagates; no additional return call is made. |
| Invalid Blob part conversion | It fails after source completion; text validation instead fails during iteration. |
| Sync iterator yields a Promise / async iterator returns Promise as its value | Sync iteration unwraps it; async iteration passes the Promise value to the decoder and rejects its type. |

ArrayBuffer/DataView/typed-view cases use ordinary fixed storage and visible offsets. Node Blob snapshots its source parts at construction; repeated `arrayBuffer()`/`bytes()` results are independent. Its `stream()` is a byte stream and supports BYOB. These are **Node reference observations**, not new StarlingMonkey results. No native getter/detach/shared-lifetime, GC fault or OOM probe ran.

## Native ownership review and reuse decision

[source-audit.json](source-audit.json) hashes 34 source/header/test files and cites 19 native symbols. Seventeen relevant production inputs are checked against the actual v7 OFF engine's 293-input receipt and frozen source bytes. Its source identity is evidence only; the engine was not invoked for this task. Stored WPT expectation files are recorded as expectations, not fresh test passes.

| Existing source/symbol | Source finding and decision |
| --- | --- |
| `builtins/web/blob.h::Blob::ByteBuffer`, `Blob::append_value/finalize` | A private `js::Vector<uint8_t,0,SystemAllocPolicy>` owns bytes. Valid parts are copied synchronously; no raw part span is retained across a Promise/iterator await. Blob input handles root their owning objects. This ownership model is suitable in principle. |
| `runtime/builtin.cpp::value_to_buffer`, `Blob::append_value` | The span is appended through native vector allocation without an intervening JS callback, but the shared flag is ignored. Add explicit backing policy and error reporting before broad reuse; do not claim shared-memory safety or probe it here. |
| `Blob::data_to_owned_array_buffer`, `arrayBuffer`, `bytes` | Native source storage stays stable with rooted self, but output uses `mozilla::MakeUnique<uint8_t[]>` (`std::make_unique`/`new[]`) and transfers it to `NewArrayBufferWithContents`, whose public contract requires JS_free-compatible memory. Compatibility/fallibility is not established at this call site. A coordinated change should use explicit fallible JS allocation/FreePolicy or a GC-owned buffer with reacquired NoGC data. No observed corruption/OOM is claimed. |
| `Blob::text` | Own native input is stable during decode. Pinned Vector's zero-capacity storage supplies a nonnull sentinel, so this audit does **not** diagnose a null empty Rust slice. Decoder allocation, arithmetic/result checks and Promise failure paths still need review. The direct consumer prototype uses the separately audited TextDecoder instead. |
| `Blob::append_value`, `arrayBuffer/bytes/text` | SystemAllocPolicy does no JS error reporting. Some failures return false after Promise creation; ResolvePromise results are unchecked. Coherent pending-exception/rejection behavior and genuine allocation failures remain gates. |
| `Blob::slice/init/init_options` | Positive slice allocation failure can reach creation with null data; constructor options are processed after parts, so endings selection occurs after string appends. Failed-constructor/finalizer state and limits need separate review. Default-option consumer construction would avoid option differences but would not solve the other gates. |
| `Blob::stream`, `BufReader::create`, `StreamTask::trace`, `NativeStreamSource::create` | Reserved owner/user/stream slots and the task's traced Heap reader retain the owner. Tasks allocate 8192-byte buffers, copy owned bytes and enqueue U8 views. Creation is a default stream, not Node's byte stream. |
| `BufReader::pull/cancel`, `StreamTask::run` | Pull queues an unchecked task allocation; cancel is a no-op and does not remove queued work. Cancellation, post-cancel enqueue/error routing, task lifetime and BYOB differences must be solved before Blob-stream reuse claims. No race/fault probe was run. |
| `builtins/web/text-codec/text-decoder.cpp::TextDecoder::decode` | Current source roots input, checks kind before options, rereads lengths after options, rejects shared views, allocates output before reacquiring input under NoGC, synchronously consumes Rust decoder state and copies the JS string. This justifies a small captured text/JSON facade proposal with private frozen options; guest validation remains pending. |

Node's global Blob is the same constructor as `node:buffer.Blob` ([pinned Blob source](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/blob.js)). The current profile's `Buffer.Blob` is an explicit deferred function distinct from the native global Blob. The prototype avoids returning a Blob and makes no identity parity claim. That public identity decision remains separate from fixing native storage.

## Minimal isolated proposal

[create-module.mjs](create-module.mjs) and [prototype.mjs](prototype.mjs) propose `text` and `json` for finite sync/async iterables. They capture the existing native decoder, decode method, JSON parser, brand getters and error constructors before application code. No Blob, Buffer, early part copy, custom host service or JavaScript UTF8 codec is introduced. The for-await state machine keeps ordinary JS values traced and invokes decode synchronously before the next await; pending UTF8 bytes belong to the decoder. No native pointer is retained by the facade.

`blob`, `arrayBuffer` and `buffer` are real named functions that synchronously throw identifiable `ERR_SM_NODE_UNSUPPORTED` on invocation **and construction**, including at initialization. They are deliberately ordinary constructible functions to provide that refusal contract; this differs from Node's async shape. Default inspection is safe, has no then property or Proxy, and initially shares all named function identities. Default-property mutation does not rewrite named bindings or the lexical text function used by JSON.

[export-contract.node-v22.14.0.json](export-contract.node-v22.14.0.json) is finite and explicitly versioned as an **isolated contract**, with no production profile version reserved. It is not a schema-valid selected production manifest and cannot admit a native module. A coordinator must assign the optional module's version and validate/register its real bindings after gates. The Jco Node24 `bytes` export is excluded. Jco's early-copy `collectParts` is not reused; unenv's stub module is not a Node oracle.

| Proposed cap | Value / behavior |
| --- | --- |
| Aggregate byte input | 1,048,576 visible bytes, checked before decode. |
| Aggregate string input | 1,048,576 UTF16 code units. |
| Output | 1,048,576 UTF16 code units, including final decoder flush. |
| Iteration | 4,096 yielded chunks, including empty chunks; detecting the excess consumes a 4,097th next result. |
| Failure | RangeError with `ERR_SM_NODE_LIMIT`; a body cap failure closes the iterator through standard for-await semantics, and its original error wins over return rejection. Final-flush cap failure occurs after completion. |

Fixed unshared ArrayBuffer/ArrayBufferView chunks and strings are the declared byte/text subset; undefined remains an empty decoder input as in Node. Shared/resizable/detached backing is outside the prototype. A pending next Promise cannot be time-bounded by these counters; external cancellation/deadline ownership remains with the source and a future lifecycle policy. JSON uses no reviver and parses only bounded completed text; the output string cap is not an exact cap on parser heap, object count, nesting or genuine OOM.

[prototype-node-results.json](prototype-node-results.json) passes all 18 ordinary text/JSON groups against the pinned oracle and 12 profile groups for finite exports, call/new refusals, default mutation, captures, caps, close/error precedence and safe inspection. These tests use **Node22's** TextDecoder. No StarlingMonkey component, snapshot, target host or production support result is inferred.

## Dependency-ordered next gates

1. Review this bounded contract independently of classic streams. Preserve the Blob-dependent three refusals until native allocator/error/backing/lifetime fixes and the Blob identity decision are coordinated. No native Blob patch/template was compiled here.
2. On a separately authorized frozen engine, run an isolated source component using actual native TextDecoder and these finite ESM bindings: repeat 18 ordinary groups/cap/error checks; verify exact zero host imports, Node-kind errors, two retained-instance calls and fresh Wasmtime execution. Do not include hazardous legacy Blob lifetime probes.
3. Test valid finite initialization and strict call/new/deferred and async rejection failures during componentization. No pending external iterator, live reader/host handle or request-associated state should be captured into a deployed snapshot. Add cancellation/resource-owner tests before consuming request-associated iterables; no ALS or Node nextTick ordering follows from generic Promise use.
4. If text/JSON passes, assign a versioned optional manifest/factory through the existing registry/generator mechanism. Static CJS lowering returns the same default object; no dynamic require or mutation synchronization is promised. Optional OFF must reject admission, without npm/Jco adapter fallback. Pure imports remain empty.
5. For future Blob outputs, retain actual JS part references through completion, validate final bounds/backing and copy at constructor time. Reject deferred coercion overloads explicitly rather than converting/copying early. Test exact output ownership, offsets, mutations, rejection precedence, Blob identity and reader cancellation before enabling those names. Owned Blob output can feed existing `Buffer.from(ArrayBuffer)` without an extra Buffer copy only after that storage gate.
6. Validate the selected pure module in the existing joint standard HTTP fixture on both unmodified hosts without widening WASI imports. Measure final size/startup/memory/throughput before any cost claim. Classic Stream lifecycle, abort helpers, tick scheduling/ALS and other Buffer/encoding demands remain separate deferred work.

Reproduce the source/Node-only audit with the pinned Node executable using `run-node.mjs`, `run-prototype-node.mjs` and `audit-sources.mjs`. No component/native build script is run by these commands.
