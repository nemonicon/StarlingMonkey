# Runtime clock capability decision

This is an engineering decision for the next clock-profile source proposal.
It does not change an accepted profile, activate a capability, or admit the
captured timer component. The accepted checkpoint remains foundations-v13.

The intended runtime-clock profile will explicitly select:

- `wasi:clocks/wall-clock@0.2.10` for live realtime reads used by `Date`.
- `wasi:clocks/monotonic-clock@0.2.10` for monotonic reads and timer subscriptions.
- `wasi:io/poll@0.2.10` for those subscriptions and their resource lifetimes.

This profile must preserve ordinary realtime JavaScript behavior rather than
silently freezing `Date.now()` to fit a monotonic-only interface selection.
Applications selecting the existing pure profile must retain imports[]. Node
`perf_hooks`, process uptime and full Node scheduling compatibility are separate
API work; this decision does not add those exports.

The [retained failure](../../tests/node-compat/foundation-scheduler/resource-component-clock-policy-failure-v1/README.md)
and [independent graph review](../../tests/node-compat/foundation-scheduler/independent-resource-component-results-and-clock-failure-review-v1/README.md)
establish the current boundary. Pure construction emits no interfaces. The
timer candidate emits six standard0.2.10 interfaces: both clocks, poll,
streams, error and stderr. Its historical strict two-interface policy remains
unchanged and the candidate remains rejected. The actual graph resolves engine
Preview1 `clock_time_get` through the generated shim/fixup into the adapter;
that adapter has callable wall-clock and stderr/stream dependencies. The
io/error resource also participates in a canonical resource-drop binding.
These are static graph facts, not timer or Date runtime results.

Two separate corrections are required. First, the pinned splicer's combined
IO handling must distinguish poll support from stream/error transport. Setting
`has_io` to false would also remove required timer poll operations. A source
successor must preserve Stdio, HTTP/fetch-event and explicitly selected
filesystem/socket worlds when they actually need those IO operations.

Second, the Preview1 clock path must stop pulling in unrelated adapter IO.
Evaluate a guest clock-only adapter or a native guest P2 clock bridge against
the real adapter ABI and allocation/lifetime rules. The existing53512-byte
repository adapter has an exact binary pin; its original source/build revision
has not been established by the new graph review. A replacement cannot claim
to be a source derivation of that binary without further provenance evidence.
No installed package, Wasmtime or wasmCloud binary may be modified, and no
custom external host interface may replace the standard clocks.

The native bridge alternative also needs snapshot analysis before coding.
[`clock_gettime` and `wizen`](../../runtime/js.cpp#L38) currently call Preview1
clock functions, and `wizen` captures a monotonic offset. Snapshot initialization
must continue to work with the actual Wizer import policy. Build-machine and
deployed-host monotonic epochs cannot be assumed comparable. Reads during
initialization, application values intentionally captured in the snapshot,
first deployed execution and later reuse need separate fixtures. Neither a
new bridge nor a packaging pass may silently change the existing pure profile's
bounded clock behavior.

Admission requires a new immutable source/tool cut and new construction phase.
Retain the original seven resource cases, all nine manifests and native Buffer
resolution. Capture complete component bytes and WIT before checking the exact
new selection. Independently inspect the root/core/type/adapter graph; require
no Preview1 host import and no unselected IO, stderr or other interfaces.
The native engine identity must be the actually reviewed selector generation
when that fix is included, with no old metadata or engine substitution.

Runtime validation must then cover live realtime reads, monotonic ordering,
snapshot/resumption, timer ordering/cancellation/self-clear, handled/fatal
callback failures, all-invalid and surviving task queues, interest settlement,
fresh and retained instances, and stock-host instantiation. A generic fatal trap
does not prove its originating error or safe failed-instance reuse. Request
epochs, fallible enqueue, cached pollables, teardown/reuse and ALS remain
separate unresolved lifecycle requirements.
