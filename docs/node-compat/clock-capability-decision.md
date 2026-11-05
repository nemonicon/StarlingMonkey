# Runtime clock capability decision

This is an engineering decision for the next clock-profile source proposal.
It does not change an accepted profile, activate a capability, or admit the
captured timer component. The accepted checkpoint remains foundations-v13.

Current experimental evidence advances the earlier proposal below: actual core
pruning/validation succeeds, and the separate complete WIT-package decode passes
[independent DATA review](../../tests/node-compat/foundation-scheduler/independent-clock-io-metadata-package-results-review-v1/README.md).
The original Jco decoder phase remains failed. The first package-loader source
is held on a repeated-call protection gap; the genuine v2 successor passes
[independent source review](../../tests/node-compat/foundation-scheduler/independent-clock-package-loader-v2-source-review-v1/README.md).
The fresh [ReactDOM construction](../../tests/node-compat/foundation-scheduler/clock-v13-component-v1-root-results.json)
now exits0: its 15,693,386-byte component imports exactly these three0.2.10
interfaces and exports run()->string. The full accepted v13 engine and retained
ReactDOM bundle remain unchanged. [Independent artifact/type-graph review](../../tests/node-compat/foundation-scheduler/independent-clock-v13-component-results-review-v1/README.md)
passes callable/resource bindings and all four core identities. The
[first fresh stock-Wasmtime run](../../tests/node-compat/foundation-scheduler/clock-v13-wasmtime-first-render-v1-comparison.json)
now returns complete Node-equal ReactDOM markup at raw0. A subsequent
[seven-return differential](../../tests/node-compat/foundation-scheduler/clock-v13-runtime-v2-root-results.json)
finishes raw0: three retained/one fresh Jco and three fresh Wasmtime calls all
equal the complete retained Node result. [Independent actual-result review](../../tests/node-compat/foundation-scheduler/independent-clock-v13-runtime-v2-results-review-v2/results.json)
passes all seven strings and raw cleanup. All seven resource cases and broader clock/snapshot/lifetime/target-host gates
remain open.
The accepted pure profile and original failure baseline stay unchanged.
Historical statements below describe their original preparation checkpoints.

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

The [provenance check](../../tests/node-compat/foundation-scheduler/clock-adapter-provenance-v1/README.md)
finds that the equal-sized Wasmtime v25.0.0 release adapter differs in imports,
code and metadata. Exact source revision remains unproved. A third option is
an explicit build-time transformation of the pinned repository binary, with
new artifact identities and a checked failure contract.

The [uncompiled IO-pruning proposal](../../tests/node-compat/foundation-scheduler/clock-io-pruning-candidate-v1/source-derivation.json)
splits poll from stream/error stubbing and adds a narrow adapter-pruning CLI.
The original memory-first adapter violates the selected wirm replacement
helpers' import-entry/function-index assumption. A checked import-order
normalizer and exact normalized-input hash guard precede the proposed operation;
engine-specific random/realloc stubs are excluded. At that proposal checkpoint, in-memory hash preparation
and pure tests had run, without normalized-adapter publication, Rust pruner,
new package or guest execution. Later tool/core/type evidence is linked above;
final application import graphs and runtime gates remain open.

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
