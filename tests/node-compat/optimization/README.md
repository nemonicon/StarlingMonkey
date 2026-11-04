# Buffer allocation follow-up

The opt-in profile preserves its Node v22.14.0 API contract. This experiment
compares the original native facade with trusted fresh-output tagging, retaining
strict external-input checks and private WeakSet branding. Both arms include
the same [scalar-export guest patch](../abi-fix/README.md). No host modification,
JavaScript Buffer adapter or extra capability is involved.

Read the [engineering report](../../../docs/node-compat/buffer-optimization-and-abi-fix.md)
for the decision, measured improvements and remaining limitations. The
[factorial probes](README-probes.md) separately isolate backing-buffer getter,
validation, prototype and branding costs on a single historical engine.

## Recorded matched experiment

[improvement-artifacts.json](improvement-artifacts.json) contains both complete
engine source/provenance sidecars, exact component/bundle hashes, WIT and Node
oracle checksums. [improvement-results.json](improvement-results.json) contains
all 40 arm/scenario observations, 120 fresh instances and 840 timed batches,
plus host hashes, raw timings, quartiles, memory observations and comparisons.
Compilation is isolated in separate processes, and arm order alternates by
scenario. That deterministic order is also tied to size: control first for
64 bytes/64 KiB, candidate first for 4 KiB/512 KiB. Seven batches within an
instance are correlated; there are three
fresh instances, not 21 independent trials. There is one snapshot build per arm.

At 64 bytes, copy throughput improves 1.66× and hex decode 1.99×. Each reduces
process peak RSS from about 52.9 to 24.3 MiB and largest linear-memory request
from 51,445,760 to 9,502,720 bytes. At 4 KiB, copying improves 1.54×. Small UTF-8
encode throughput improves but its high-water memory does not. The short-batch
512 KiB decoder observation is 7.7% slower; do not claim uniform improvement.
The separate longer-batch check below observes less than 1% lower 512 KiB
throughput in either arm order; it does not reproduce the short-batch drop.
RSS includes Wasmtime/runtime/allocator retention, and linear-memory requests
are not total heap, allocation counts or leak evidence. This native/native run
must not be multiplied by ratios from the historical JavaScript-adapter run.

## Reproduce the recorded protocol

Use Node v22.14.0, the pinned npm toolchain and the existing stock Wasmtime
42.0.1 [benchmark host](../bench/host/). The build step verifies both engine
hashes, all recorded compiled source hashes, identical guest patches, compiler
versions, matching external embedding sources and exactly two changed repository
files. The application bundle is identical in both arms. Each setup/full-byte
checksum and loop/fingerprint checksum must match Node through Jco before timing.
Both final components must have zero host imports.

The historical metadata lacks separate immutable optimization-option cache
snapshots. The same shared build directory was used sequentially; its cache was
verified after stress as release with `WEVAL=OFF` and `USE_WASM_OPT=ON`.
Future builds now set and record those flags explicitly. This is a provenance
limitation of the recorded experiment, not a claim that flags differed.

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
  /path/to/node-v22.14.0 tests/node-compat/optimization/compare.mjs build

# Wait for other compilation, componentization and benchmark jobs to finish.
/path/to/node-v22.14.0 tests/node-compat/optimization/compare.mjs measure
```

Defaults preserve the immutable ABI-only control at
`/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-control.wasm`
and select `starlingmonkey_embedding.candidate.release.wasm` beside it. Select
other paths with `NODE_COMPAT_CONTROL_ENGINE`, `NODE_COMPAT_CANDIDATE_ENGINE`,
`NODE_COMPAT_BENCH_HOST` and `NODE_COMPAT_IMPROVEMENT_OUTPUT`.
The control engine hash is deliberately pinned to the recorded `6daf…2748`
artifact; a newly built control requires a reviewed new pin and separate results.
Snapshot determinism is not assumed.

The two historical source files are checked against
`NODE_COMPAT_BASELINE_SOURCE/node-compat/`, defaulting to
`/tmp/starling-node-compat/optimization-baseline-source/node-compat/`. This archive
was preserved before optimization. To recreate those source inputs in a **new
external directory**, copy `builtins/node-compat`, apply
[original-facade.patch](original-facade.patch) there with `patch -p3`, and run its
copied `generate-factories.mjs`. This reconstructs the old facade and generated
header for source-hash validation; it does not create the old engine or mutate
the production checkout. Use the build recipe against a separately restored
source checkout when rebuilding a control.

Generated components, precompiled caches, bindings and full execution outputs
stay outside the repository. Checked-in JSON records identify these artifacts;
local paths are provenance, not hosted downloads.

## Targeted decoder stability check

The original 512 KiB decoding batch contains two operations and is shorter than
one millisecond. [stability.mjs](stability.mjs) checks the same precompiled
components with 32 MiB payload batches at 64 and 512 KiB, three fresh instances,
three warmups and seven timed batches, then repeats with the opposite arm order.
It verifies checksums and component/cache/host hashes and writes a separate
`stability-results.json`; it never replaces the original observations.

```sh
/path/to/node-v22.14.0 tests/node-compat/optimization/stability.mjs
```

Longer batches change allocation/GC pressure as well as reducing timer noise.
Repeated component builds, independent sessions and Weval comparisons remain
separate experiments.

[Recorded stability results](stability-results.json) contain 24 fresh instances
and 168 timed batches. Candidate/control throughput ratios are 1.0308/1.0375
at 64 KiB and 0.9957/0.9910 at 512 KiB in the two opposite-order passes. All
checksums pass. No formal significance claim is made.

## Semantic and portability validation

The actual native guest checks and entry-selection options are described in
[README-probes.md](README-probes.md#candidate-semantic-and-portability-checks).
They augment the existing full differential fixture; the host-side reference
kernel tests are supplemental and are not counted as native execution evidence.
The [candidate execution record](candidate-validation-results.json) preserves
release/stress semantic and Wasmtime/wasmCloud HTTP results, with matching
component hashes and the additional intrinsic-check reports.
