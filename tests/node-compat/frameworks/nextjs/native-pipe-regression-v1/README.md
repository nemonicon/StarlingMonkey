Twelve-case source-only native signal-pipe regression for the selected Next profile.

The guest uses the exact sealed C signal-aware pipeTo implementation (d9d3d391),
actual native global ReadableStream/WritableStream, real node:stream/web default
reader/writer constructors and protected node:events.addAbortListener. It adds no
host service, new native API, alternate stream model or application mount. The
original eight-file next-http WIT world remains referenced, with its same thirteen
standard0.2.10 allowed interfaces and incoming-handler export; actual emitted imports
must be validated by the constructor. World selection does not claim all imports
are emitted or exercised.

The twelve cases retain the donor semantics: final chunks, preventClose, source
error/abort, rejected writes/source cancellation, pre-aborted actions, false/null
action failure precedence, stopImmediatePropagation resistance, in-flight write
shutdown, ready backpressure and both preexisting-lock refusals. Eleven scenario
statements are byte-identical donor copies; source-error specializes its existing
loop to preventAbort=false. The task barrier uses real setTimeout(0) on both targets
instead of Node-only setImmediate; entered/gate promises preserve required ordering.
No stream/AbortController/timer/Promise is created during module initialization.
Installation only captures intrinsics and installs the existing selected method.

node-oracle.mjs is dormant and uses unmodified pinned Node22.14 pipeTo over the same
case module. It emits identity plus three complete raw JSON strings. Guest responses
record case completion, identity comparisons, ordered cancel/abort/write events and
post-operation stream locks. Individual unexpected errors are typed/captured without
asserting success or omitting later cases. A hang must fail the separately owned
runtime deadline. Future comparison must capture all three whole HTTP responses
first, require counters1/2/3 and twelve complete records each, then compare every
case record to the pinned actual Node oracle. A mismatch remains a failed strict
comparison, including native scheduling/cleanup differences; no expected-gap pass.

This subset does not test every one of the donor31 host cases or repair native
cached pipeThrough. The three donor public-API limitations remain: disturbed state
for pre-aborted preventCancel, close-queued private state, and cached pipeThrough.
This is not full stream-spec, GC, teardown, full Next or production acceptance.

The sibling native-pipe-regression-construction-v1 reuses the exact existing
constructor/capture/run executables. Root must separately bind the actual reviewed
incremental engine, raw native metadata, Source/build evidence and runId. All actual
Root/component/oracle/runtime slots remain null. No constructor, oracle, engine,
stream workload or guest execution was performed to publish this Source.
