This is a new source/Node-host workload packet. It does not build, componentize,
run a Wasm guest or target host, or measure time. All future engine/component
pins remain null. Existing342 sources, generated header, stock Jco scheduler,
old oracles and sealed predecessors are unchanged.

`workload.mjs` implements the protocol's seven ordinary scenarios and three raw
controls through one finite provider record. The four byte pipelines use128×64B
or8×512KiB fixed, attached, unshared offset8 windows. View reuse and
`Buffer.from(existing Buffer)` copying construction stay separate; Buffer.copy,
concat, Web bridges and deferred operations are not called. Fragmented UTF8
uses64 windows over complete valid ASCII/2/3/4-byte input. Object writes use HWM2
and the selected scheduler; cancellation has16 possible objects, aborts after
four writes and handles the rejection. Streams/pipelines run sequentially.

Every output byte is checked online against its deterministic position, decoded
text against its exact prefix and object values against their exact order.
Traces retain per-chunk checksums/counts, bounded text, write returns, callback
receiver/arity/typed encoding, EOF, events, Promise boundaries and cleanup—not
per-byte number arrays or repeated large payloads. Each iteration permits at
most4096 trace records and128 write callbacks. The actual private checkpoint
budget remains65536; counting workload callbacks on Node is not proof of the
guest's total internal tick budget. Snapshot setup creates input buffers only,
with no streams or queued work. Actual fresh/retained snapshot and max-batch
guest correctness remain required.

Pinned real Node22.14.0 captures20 checksum/trace cases at1/16 iterations.
The canonical installed factory, exercised on Node with real Node dependencies
and process.nextTick, matches all exact outputs and checksums but has14 trace
counterexamples: the seven ordinary scenarios at both bounds. The first byte
case returns true from Node's synchronous HWM-boundary write and false from the
canonical factory; end/finish ordering also differs. Object-mode callback
encoding is Node undefined versus canonical utf8. These remain exact results,
not parity passes. The three controls match. Separate unapplied source-fix and
actual342 guest-reproduction work does not alter this packet's original model.

Two first host attempts exhausted Node's normal heap while assert.deepEqual
formatted a large repeated trace mismatch. Their source/failure facts remain in
history; original stderr is in tool history. No heap limit override/dump, fault,
DEBUG, native or guest experiment was used. Bounded exact serialized comparison
and retained raw data complete without that formatting. Typed undefined is
explicit in the final trace carrier; the earlier successful carrier is retained.

Actual-entry host bundles verify three distinct graphs: native binding imports,
the same canonical factory over native dependencies/private callable, and locked
stock Jco1.40 adapters over Jco-std0.10/readable-stream4.7/unenv dependencies.
The canonical source mechanically reconstructs the exact installed generated
header. The stock graph has no external imports and contains the actual
readable-stream process/→stock scheduler resolutions. The explicit workload
scheduler import uses that same canonical physical module identity; an initial
/tmp versus /private/tmp duplication was refused and preserved. No
streamSchedulerModule option, source replacement or scheduler override is used.
Stock's own Buffer/global and callable-emitter adaptation remains stock behavior,
not an intervention by this harness. Stock Node-host observations also retain14
ordinary trace counterexamples, so that arm is not timing-ready.

The primary future pair must use identical new diagnostic CLASSIC-ON engine
bytes and native Buffer/Events/StringDecoder/private queue. Whole-profile cost
uses distinct reviewed ON/OFF engines and includes bundle/snapshot differences.
Stock is a separate provider/dependency/scheduler comparison. These meanings
must not be merged into a C++ state-machine or performance claim. Raw controls
are reported without subtraction: input-only uses128×64B, copying-only8×512KiB,
and construction-only a clean empty three-stream pipeline. They are applied
identically across arms, not asserted to isolate every scenario's overhead.

`component-plan.json` lists future gates; timing is refused by null artifacts
and the retained trace gaps. Correctness and timing WIT carriers are ordinary
Release s32/string exports, with no guest clocks or custom host imports. The
complete source/notice/resolver evidence is separate from actual component
size/RSS/startup/throughput. No full Node streams, reset/ALS, request reuse,
isolated GC-owner or total-heap bound follows. Accepted checkpoint remains v12.
