This source-only regression harness isolates two newly observed public stream
trace gaps. It makes no installed-guest failure claim before actual execution.
It does not change live classic342 sources, factories, manifests, native pins,
private scheduler or any earlier packet. Existing Node22.14.0 source/guest model
checks are labelled separately from the unexecuted component runner.

The input is always exactly64 deterministic Buffer bytes. Six Writable cases
place that input below/at/above HWM65/64/63 and complete _write synchronously or
through the standard queueMicrotask global. All byte/checksum/callback/terminal
invariants match. Node sync returns true/true/true; the actual factory evaluated
on Node dependencies returns true/false/false. Deferred controls match exactly
at true/false/false. The model uses real Node Buffer/events/StringDecoder and
process.nextTick; it proves neither the native guest dependencies nor its
private queue. The guest never imports or exposes process/nextTick.

Two smaller pipeline cases use PassThrough(source)→PassThrough→Writable with
64bytes, sync or microtask sink completion and exact terminal-event traces.
Here the **source PassThrough** emits end before finish on Node and finish before
end in the host model; middle-pass ordering matches in this smaller topology.
This is explicitly distinguished from the larger benchmark's middle-pass gap.
Every trace cell is a string/number/boolean and each trace is bounded below128
records; undefined is not silently converted to null. No private stream state,
fault, GC/OOM, cancellation or reset is inspected. Toolchain's full benchmark
oracles and Buffer agent's semantic fix proposals remain separate.

The future entry run-component.UNEXECUTED.mjs first authenticates its fixed
source seal and actual runtime-v3 index7e952, then calls the existing exact
classicPreflight({variant:'normal-off'}). Only actual b827/873c frozen engine
authority is admitted. Its captured recheck retains the actual342/6000-input,
tool-root/two-tree/22-link and native freeze checks. The new guard adds its own
source/template seal without projecting metadata or adding an engine flag.

The future driver reuses loadToolchain/loadComponentizer/bundleProfile, actual
module selection, the repository adapter988 and trackedWriter/publishCompletion.
Only guest/cases are bundled; node:buffer and node:stream stay external actual
registered bindings. The application-owned WIT exports only run()->string.
All standard optional capabilities are disabled and selectedInterfaces=[];
there is no custom host service or new WIT host import. Final imports and WIT
are checked after real packaging when separately authorized.

After review, the future runner will make three retained Jco calls, one fresh
Jco instance and one fresh pinned Wasmtime42 call, preserve all raw observations,
and require deterministic bytes/traces across guest instances. Node differences
are reported through nodeCompatibilityPassed and full per-case data, not forced
to appear or relaxed away. The model-to-guest comparison is also explicit. A
completed observation is not a compatibility pass. Snapshot Buffer identity is
not a new ownership/GC test; only fixed input length/checksum/call state is used.

No componentizer, bundle, guest, target host, native build or timing ran during
this preparation. Root must review this packet before executing the future
entry with an explicit fresh NODE_COMPAT_STREAM_TRACE_OUTPUT and the existing
selected Node/toolchain/Wasmtime environment. Outer raw exit0 and completion
hashes remain mandatory. Actual guest reproduction is required before a live
semantic change or product-failure conclusion. Full Node streams, scheduler,
reset/ALS, memory and performance claims remain outside this regression.
