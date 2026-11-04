# Blob/File integration and validation packet: source-only

This packet prepares the reviewed native owned-copy v2 fix for a future isolated
normal Release build. **No patch is applied, no engine is linked, and no guest
Blob/File method is executed here.** Existing production exports and all
v1/v2/consumer/Web-iteration evidence remain unchanged. `node:buffer.Blob` and
`File` remain finite import-only bindings whose call/new operations explicitly
fail; they are not advanced to the native globals.

[source-receipt.json](source-receipt.json) checks all **304 current m10 frozen
and live native inputs**, base engine
`1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154`,
actual embedding source/recipe, four before/after files, class/caller/stream
dependencies and retained historical receipts. All four m10 before files are
byte-identical to the reviewed v7 before files. The existing patch
`5c33bf8efa60f80e3f796862c42ab40402c9160923e0fbbe6b802b8c122976b3`
therefore has the same exact four-file ancestry. Relevant existing v7 syntax
headers `builtin.h`, `extension-api.h`, `encode.h`, `buf-reader.h`, and
`native-stream-source.h` also match their m10 versions.

The retained [v2 SDK receipt](../native-blob-candidate/v2/sdk-syntax-results.json)
proves two actual SDK30/SM147 Release **syntax-only** translation units. It
produced no object, engine or runtime result. No compiler was invoked again for
this packet; merely copying that receipt into a new description is not a linked
m10 proof.

## Ownership and class changes already proposed

| File/symbol | Verified source design; runtime gate remains |
| --- | --- |
| `blob.cpp::data_to_owned_array_buffer` | Replaces `new[]`/JS-free adoption with a rooted `JS::NewArrayBuffer`, followed by one explicit native-vector-to-ArrayBuffer copy under `AutoCheckCannotGC`. Rooted self retains the native vector across the allocation; no JS callback/allocation occurs during the copy, and zero length avoids raw pointers. |
| `Blob::append_value/reserve_append` | Roots/materializes backing before borrowing, rejects shared/resizable/detached storage, reserves target capacity before acquiring raw data, reacquires the view pointer/length inside NoGC and uses only `infallibleAppend` during that borrow. Blob/File parts copy immutable native bytes. Strings use an owned UTF8 temporary; arbitrary part conversion remains observable and sequential. |
| `Blob::arrayBuffer/bytes/text` | Roots results and propagates Promise-resolution failures. Public invalid receivers use the existing rejected-Promise helper before private data access. Sync slice/stream/accessor guards still throw. No pointer survives a Promise-resolution thenable/property lookup. |
| `Blob::slice/create` | Checks positive allocation before use; a JS_malloc-compatible UniqueChars buffer transfers once to the matching SystemAllocPolicy vector. The retained v2 proof follows **MallocArena allocation/reallocation/free**, not just compatible-looking destructors. Allocation/result ownership remains single-owner. |
| `Blob::text` | Empty input returns before Rust FFI. Nonempty output capacity is `max(maximum,2)` writable UTF16 units, checked for multiplication overflow; input must be fully consumed with `INPUT_EMPTY` and output within capacity. Output uses JS_string_malloc/StringBufferArena and the documented adopting string API. Rust constructor allocation can still abort; null checking does not make it recoverable. |
| `blob.h::Blob::is_instance` | Native class/registered-subclass plus initialized Data pointer are required. Prototype and partial-constructor objects cannot reach a byte-vector dereference. Type and Endings are initialized before Data is published; getters have their existing explicit prototype checks too. |
| `file.h/file.cpp::File` | Changes to its **own** FinalizableClassPolicy and forwards once to Blob cleanup. JSClassOps are not inherited through the JS prototype chain. File additionally requires initialized name/number slots when used as a File receiver. |
| `Blob::finalize` | Reads only the optional native Data pointer and destroys its byte-only vector, without consulting the mutable subclass registry, allocating, calling JS, or using receiver guards. This accommodates background finalization and undefined Data on prototypes/failure. File reserves the Blob prefix and forwards once; the VM does not also run a parent JSClass finalizer. |

Native Data contains no JS values, so it needs no private GC-edge tracer. Type,
File name, and scalar fields use native reserved slots and the VM's slot
tracing/barriers. A future callback, resource, or JS part retained in native
storage would need an explicit trace policy; the byte-vector design must not be
silently extended to contain untraced JS references.

`include/builtin.h::BuiltinImpl::check_receiver` actually dispatches to
`Impl::is_instance`; this is why the new overrides guard the public method
macros. `FinalizableClassPolicy::class_ops` supplies the concrete class's
finalizer and background-finalize flag. Compile every affected target/header
user together; swapping only one File object file would not establish a
consistent class policy.

## Limits and unresolved semantics

[api-matrix.json](api-matrix.json) contains27 finite rows, exact pinned Node
constructor/prototype inventory, per-API strategy/capability/status/deviations,
and evidence selection. Candidate behaviors remain **unverified** until linked
and tested; a constructor captured in source does not prove all its observable
members. Nonregistry Node symbols are reflection-only observations, not portable
public keys. Registered inspect hooks have explicit unverified target presence.

- The v2 native byte bound is `PTRDIFF_MAX` (2,147,483,647 on wasm32), with real
  allocator/component limits potentially much lower. It is not a tested2GiB
  allocation guarantee or a consumer input cap. Nonempty UTF16 capacity must be
  at least2 units. SM147's public `JS::MaxStringLength` is1,073,741,822 code units;
  v2 checks size_t arithmetic, but lacks an explicit pre-allocation string cap.
- Current native vectors grow through SystemAllocPolicy. V2 improves error
  reporting, but C++ `std::string` paths and Rust allocation are not proven
  recoverable. Native reserve/copy/read outputs can coexist and create memory
  peaks; no size or speed benefit is measured here.
- GC external-memory pressure is unresolved. A small number of JS Blob objects
  can own large native capacities without corresponding JS-heap growth. The
  installed public `JS::AddAssociatedMemory`/`RemoveAssociatedMemory` and
  `MemoryUse::Embedding1..5` are real candidate mechanisms, **not used by v2**.
  Before adding them, account actual capacity deltas, transfer/adoption, failed
  construction and exactly-once release; verify the background-finalizer
  contract in the pinned implementation. Allocator-family proof alone is not
  GC accounting.
- Constructor options are processed **after** all parts. Endings selection
  therefore cannot affect strings already appended. The source still uses
  HasProperty before Get; it does not match Node's option getter/conversion
  order. Numeric/boolean MIME values become empty and Symbol type does not get
  Node's normal conversion failure. Printable-ASCII string MIME is the bounded
  future ordinary subset.
- The Node oracle records exact order
  `get-type,get-endings,endings-toString,iterator,part-toString,type-toString`.
  Node22's native-line-ending regex normalizes CRLF/LF on this POSIX host and
  preserves a lone CR; do not substitute an assumed Web-spec algorithm for this
  compatibility pin. A guest `native` platform policy must be explicit.
- File uses `ToInt64` whereas Node22 uses unary-number conversion, maps NaN to0,
  and preserves fractions/infinities/negative zero. Candidate name conversion
  lacks Node's well-formed surrogate repair; Node reads lastModified before
  converting name, while the candidate converts name first. The future guest
  subset uses plain names and explicit finite integer lastModified.
- `File` without lastModified calls `JS_Now()/1000`. That is a real clock fact,
  not permission to snapshot a constant or invent process time. The pure future
  fixture always supplies17 or another explicit integer. Default construction
  requires a reviewed snapshot/deployed policy and explicitly selected
  `wasi:clocks/wall-clock@0.2.10`, including verification of its P1 bridge/final
  emitted imports. A disabled-clock packaging stub is not a live clock.
- V2 resolves native read Promises before returning. Node22's nonempty native
  read path queues another read microtask before resolution; the new Node-only
  oracle observes `promise,microtask,result` for arrayBuffer/bytes/text. Exact
  settlement ordering is a separate compatibility gate. The three ordinary
  slice coercion observations are **not** evidence of a mismatch; full
  conversions/error precedence remain untested and string MIME is the subset.

## Stream, cancellation and related callers

V2 does not touch Blob.stream/BufReader. Genuine stream execution is excluded
from the future fixture, even on the four-file candidate. Existing source shows:

- `Blob::stream` uses `BufReader::create` and
  `NativeStreamSource::create`, which builds a default stream with HWM0 rather
  than Node's byte/BYOB stream.
- Reserved User/Stream/Owner values retain the Blob and source graph.
  `StreamTask` additionally owns a traced Heap reader reached by the rooted
  EventLoop task queue, so queued work can keep Blob bytes alive.
- `BufReader::pull` queues an unchecked `js_new<StreamTask>` allocation. Its
  cancel algorithm does not remove queued work. `StreamTask::cancel` only
  invalidates its handle; safe post-cancel enqueue/error routing and timely
  owner release have not been established.
- Each task allocates8192 output bytes, borrows their span and invokes the
  registered native read function. Blob's particular read callback only copies
  immutable native bytes, but the generic callback/borrow/GC contract and task
  cancellation need an independent source fix/review. No safety inference is
  drawn from a successful Node reader example.

Before enabling a returned Blob's stream surface, fix cancellation/resource
ownership, checked task allocation, closed/error/EOF behavior, tracing during
active dispatch and byte/BYOB semantics using actual supported APIs. Existing
v9 iteration/DataView proof does not turn this default native source into a byte
stream. A bounded returned-Blob contract must explicitly handle unsupported
methods, rather than advertising a return object whose unchecked legacy methods
silently act as supported Node APIs.

Other actual callers also need regression coverage: structured-clone read
adopts JS_malloc bytes through `Blob::create`; fetch body parsing creates Blob
from owned body bytes or invokes Blob.stream; FormData and multipart parsing
call `File::create`. Blob-derived FormData conversion can omit lastModified and
therefore reaches the clock path, while an existing File preserves its value.
The current structured-clone read function also has a source-visible read-failure
cleanup issue outside these four files; no malformed clone/fault probe is run.
No blanket structured-clone/fetch/FormData correctness claim follows from v2.

## Consumers stay separately deferred

The existing [consumer metadata-v2 component evidence](../metadata-v2/component-results.json)
and text/JSON facade are reused unchanged. Their limits remain1MiB byte input,
1MiB string input/output code units, and4096 chunks. The accepted v9 installed
Web iteration receipt is pinned separately, rather than repeating its tests.
Neither result proves Blob output or classic-stream scheduling.

Future `blob`, `arrayBuffer`, and `buffer` must retain actual yielded JS values
through iteration completion, then perform **sequential** constructor conversion
and copying. Copying a reused U8 when yielded incorrectly yieldsA/B where Node
observes finalC/C. Converting all object parts before the final constructor can
also change ordering: a later object's ToString can mutate an earlier byte part
that Node would already have copied during constructor processing. Do not hide
this difference in a pre-validation/size-counting pass.

Small finite chunk/byte/string/output limits must be designed around that
observable order before these consumers are implemented. Arbitrary object
coercion cannot be safely budgeted by eagerly calling ToString. A reviewed
bounded input domain or a sequential capped native builder may be needed; this
packet neither invents that API nor claims it is implemented. Existing
`Buffer.from(ArrayBuffer)` can share the **fresh returned** ArrayBuffer after the
storage gate, avoiding an extra Buffer copy without sharing original Blob
storage. Blob/File namespace/default/global identities and the returned Blob's
full supported surface remain distinct admission decisions. No export is
promoted here.

## Completed evidence and future runner

[node-results.json](node-results.json) contains11 ordinary groups,23 invalid
receiver observations and11 Node-only remaining-semantics groups, against exact
Node v22.14.0. It pins extracted shipped `internal/blob`/`internal/file` source
and MIT notice. The ordinary groups cover empty and one-byte text, surrogate
repair, malformed/BOM UTF8, visible offsets/raw typed bytes, source snapshots,
independent outputs, nested Blob/File, bounded integer slices, ASCII MIME,
explicit File fields and64 small objects. This is only Node evidence.

[run-future-component.UNEXECUTED.mjs](run-future-component.UNEXECUTED.mjs) is
prepared for a **new** normal Release source freeze. It first verifies the exact
four reviewed after hashes (hard-pinned in the runner), all300 other m10 source
hashes, actual engine digest, unchanged embedding, and unadvanced core manifest.
Only then can the existing native-scalar harness load the selected componentizer
and package the fixture. It uses the real native globals and existing native
Buffer; no JS Blob substitute is bundled.

The planned gate compares11 ordinary groups and23 receiver phase/type results,
retaining raw native error-code observations because exact Node error fields are
not claimed. It prepares snapshot Blob/File reads with explicit timestamps,
three calls to a retained Jco instance, fresh Wasmtime42, exact zero imports,
four continued public Blob/File call/new refusals, and three initialization
failure cases. **None has run.** Node-only genuine stream/clock/coercion/timing
cases are excluded by source selection and a bundle guard. No detach/shared/RAB,
old native prototype entry, fault/OOM/DEBUG/raw-memory work, or poisoned
Error.code/native fatal-decode combination is included.

Before authorization/build, root must review the four-file delta and explicitly
choose which remaining Web semantics/accounting/stream gates block integration.
Use existing builtin_web_blob/builtin_web_file CMake targets, a new private
source/build directory and immutable full304-input/recipe/licensing receipts;
do not overwrite m10 or copy only a partially compiled class. Run ordinary
tests only after source preflight and keep public Node bindings deferred through
that validation. Source fixes, a linked build, actual component execution and
public API admission are four different milestones.

```sh
# Safe host/source work completed in this packet:
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-stream-consumers/blob-integration-candidate/run-node.mjs
python3 tests/node-compat/foundation-stream-consumers/blob-integration-candidate/make-matrix.py
python3 tests/node-compat/foundation-stream-consumers/blob-integration-candidate/prepare-packet.py
# Future runner is deliberately not invoked on a corrected guest in this phase.
```
