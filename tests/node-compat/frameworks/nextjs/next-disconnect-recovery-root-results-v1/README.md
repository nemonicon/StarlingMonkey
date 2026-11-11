# Saved Next disconnect/recovery regression

This is a **verified negative lifecycle result**, not a compatibility promotion.
The unchanged Next component completed all 114 client observations on each of
Wasmtime 42.0.1, stock wasmCloud 2.11.0 and the matched Node 22.14.0 bridge.
Both guests emitted 19 request-abort/`mozalloc_abort` diagnostics. The Node
actor exited 1 with 19 transport errors despite its passing client checks.

Run the saved check from any checkout with Python 3.11:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-disconnect-recovery-root-results-v1/check-saved.py
```

Exit 0 means that the saved evidence and its negative outcome were verified.
The output explicitly retains `allClientObservationsPassed: true`,
`allFunctionalRecoveryPassed: false`, `guestAbortDiagnosticsPresent: true` and
`nativeLifecycleAccepted: false`. It does not rerun Next or approve the runtime.

The checker verifies 793 retained payloads (14,877,142 stored bytes), decompresses
them within fixed bounds, and recomputes all three results through the exact
reviewer using a lookup map. All 734 reviewer inputs are retained. Original
absolute paths are keys only: no original application, binary, compiler, host
or temporary build tree is opened. It passes here and from an isolated copy of
795 staged Git files, with byte-identical output. Optimized Python is refused
before packet reads. See `operation-records/` for the closed command records.

`actual-probe-review.json` separates client completion, actor transport failure,
literal diagnostics and lifecycle acceptance. `raw-records/index.json` maps
every retained original tuple to its copied bytes. `source-peer.json`, the
source histories and protocol-control records preserve preparation and the two
collector runs. The initial passing collector run is not relabeled as testing
the subsequent timeout-observation correction.

The [fixed plan](run-plan.md) and sibling client/runtime families document the
actual 3 warm-up +16 recorded cycles, six requests per cycle, 180-second client
budget and 600/600/300-second owners. Existing namespaces and source bindings
are immutable evidence; do not rerun them in place. A new candidate or repetition
must use a separately declared fresh namespace and preserve every outcome.

Next: reproduce the [suspected abort ordering path](source-triage.md) with the
public bridge, then test a narrow guest-entry repair in a real component on both
hosts. Preserve unknown/falsy failures and cleanup errors. Full-browser
repeatability, native resource retirement, concurrent isolation, clean-checkout
reproduction, cost measurements and production promotion remain outstanding.
See the [results](../../../../../docs/node-compat/nextjs-disconnect-recovery-results.md)
and [priority roadmap](../../../../../docs/node-compat/nextjs-priority-roadmap.md).
