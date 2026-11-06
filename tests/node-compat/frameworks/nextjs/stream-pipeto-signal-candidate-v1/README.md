Guest-only signal-aware ReadableStream.prototype.pipeTo Source, prepared for the
measured Next JSON response failure. This has31/31 genuine pinned Node22.14 host
differential cases, not a SpiderMonkey/guest/native result. Root reviewed the
closed algorithm and corrected lock/final-chunk seams without an additional
blocking finding. No independent R Source peer was performed.

entry-install.fragment.mjs is the exact generated inline Source join. It imports
only existing native node:events.addAbortListener and node:stream/web, uses the
actual global ReadableStream/WritableStream constructors, and installs the method
before app loading. Reader/writer constructors come from the real stream/web
namespace, avoiding assumptions about global constructor exposure. Installation
only captures intrinsic functions/getters and defines a prototype method. It
creates no reader, writer, Promise, timer, IO, entropy or resource at INIT. There
is no new native module, CMake option, manifest export, host adapter, or WIT import.
Current engine/metadata are unchanged. Root owns the new profile/entry generation,
actual constructor audit and ordinary guest experiment; future native integration
must be a distinct derived Source generation, never old metadata relabeling.

Signal undefined preserves the original native pipeTo, with a canonical option
snapshot so getters are read once. Signal-present calls use genuine native default
reader/writer operations, ready/closed promises and AbortSignal brand/reason
getters. The protected existing addAbortListener is mandatory; no ordinary-listener
fallback can silently lose cancellation to stopImmediatePropagation. Source and
destination errors propagate in both directions, with preventClose/preventAbort/
preventCancel honored and action failures/falsy reasons preserved. Shutdown waits
for already queued writes when the destination remains writable, then executes
real cancel/abort/close actions and always attempts both lock releases plus listener
disposal. The public closed/read ordering is handled explicitly so the last
already-read chunk is forwarded before a source-close shutdown. There is one
outstanding read; queued writes follow the real writer.ready backpressure. No JS
chunk accumulation replaces native stream state.

Three precise limits prevent a full spec/Node parity claim:

- Public reader/writer APIs cannot set the private disturbed bit without reading.
  A pre-aborted signal with preventCancel=true leaves that bit false here; pinned
  Node sets it true. Host data retains both values rather than normalizing them.
- Public APIs cannot synchronously distinguish an already-close-queued destination
  from ordinary backpressure. Fully closed destinations and runtime error/abort
  cleanup are tested; the private close-queued race is not declared complete.
- The existing C++ pipeThrough stores its native pipeTo function. Replacing the
  public prototype method fixes the measured direct pipeTo(signal) call; it does
  not repair signal-bearing pipeThrough. Cross-realm/proxy/fake signals and exact
  Node error-code/message text are not an additional supported profile promise.

The exact9dab ReadableStream/PipeToState sources require configured AbortSignal
hooks and explicitly refuse required abort operations. The native default reader
release does reject pending reads, so cancel prevention can release a lock without
secretly cancelling the source. The relevant primary sources are:

- https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/streams/PipeToState.cpp
- https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/streams/ReadableStreamDefaultReader.cpp
- https://github.com/nodejs/node/blob/v22.14.0/lib/internal/webstreams/readablestream.js
- Current builtins/web/streams/transform-stream.cpp and builtins/web/event/event-target.cpp
  retain the actual native optimization/cached function and protected listener policy.

The first29-case host run was clean0. A later preseal audit found stale lock values
captured before option getters. history/attempt1 preserves the exact old Source,
test and authority/receipt. Two new cases release preexisting source/destination
locks inside option getters: the actual old function rejects, while pinned Node
and corrected Source succeed. The corrected31-case run is clean0 with26 listener
installs/disposals, no stderr and unchanged Source before/final. Each host run used
the authenticated original0af monitor,60-second bound and exact Node22 binary;
no compiler, engine, guest, provider, native allocator/reset or GC/OOM test ran.

Run check-host-evidence.py for read-only portable raw evidence verification. The
host test itself is reusable but starts a new ordinary host workload if invoked.
generate-fragment.mjs --check only reads/compares Source bytes, never imports or
evaluates the guest implementation. Both assembly check and fragment grammar
passed. Original Next baseline failures and app/world bytes remain separate held
records; this Source does not turn11/24 into an unobserved runtime success.
