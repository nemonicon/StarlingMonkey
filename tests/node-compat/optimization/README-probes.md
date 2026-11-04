# Allocation and facade investigation

The original A/B result showed a small-copy slowdown and a large 64-byte
hex-decode linear-memory high-water mark. These diagnostic probes isolate
construction stages on the **immutable original engine**
`da69618da72315c3b3f20d105708fd625a3b7c0691f49329201036c3c2fd5796`.
They do not install alternative public Buffer semantics.

All 40 cases use one capability-free component, the same already-materialized
source bytes, checksum/fingerprint and stock Wasmtime 42.0.1 measurement host.
Each case uses three fresh instances, three warmup batches and seven timed
batches per instance. Cases vary output `.buffer` access, prototype assignment,
WeakSet insertion and validation. Native Buffer operations anchor those controls.
Additional valid-input controls use SpiderMonkey's actual native
`Uint8Array.fromHex`, retaining one kernel while changing its output policy.

The original engine's complete recorded source manifest matched the checkout
before it was frozen. Its `typedName` validation was already present: the
regression was not a stale-engine discrepancy. Frozen profile-source hashes,
component/bundle hashes and the resolved SpiderMonkey source commit are in
[investigation-artifacts.json](investigation-artifacts.json). Raw samples are in
[investigation-results.json](investigation-results.json); external working files
are under `/tmp/starling-node-compat/optimization`.

## Observations

For 64-byte outputs, each batch contains 10,000 operations. Memory columns are
MiB, not decimal MB.

| Control | Median batch ms | Largest linear-memory request MiB | Peak process RSS MiB |
| --- | ---: | ---: | ---: |
| Plain Uint8Array copy | 23.28 | 9.06 | 24.06 |
| Copy, then read output `.buffer` | 27.91 | 43.06 | 43.66 |
| Copy, then WeakSet insertion | 25.87 | 9.06 | 24.20 |
| Copy, output `.buffer`, WeakSet | 31.87 | 49.06 | 52.61 |
| Copy, prototype and WeakSet; no `.buffer` | 28.68 | 9.06 | 24.23 |
| Model: input checked, output checked and tagged | 120.62 | 49.06 | 52.58 |
| Model: same input checks, fresh output tagged directly | 70.26 | 9.06 | 24.20 |
| Actual original native `Buffer.from` copy | 129.68 | 49.06 | 52.56 |
| Actual original native hex decode | 98.69 | 49.06 | 52.61 |
| Native Uint8Array hex intrinsic, unchanged output | 27.04 | 9.06 | 24.06 |
| Same intrinsic, checked output and tag | 81.34 | 49.06 | 52.61 |
| Same intrinsic, fresh output tagged directly | 35.36 | 9.06 | 24.30 |

Output backing-store materialization controls reproduce the large small-array
high-water mark. WeakSet insertion alone does not reproduce it; combining
WeakSet insertion with materialization increases the observed peak further.
The validation wrapper also adds substantial fixed work: retaining identical
input checks, prototype assignment and WeakSet insertion while omitting the
redundant fresh-output checks changes the modeled median from 120.62 to 70.26 ms.

At 4 KiB, 256 operations form a batch. Plain copy and copy-plus-`.buffer` both
request at most 17.56 MiB of linear memory, with medians 0.79 and 0.81 ms. The
full checked/tagged model takes 3.12 ms versus 2.11 ms with the same input checks
and direct fresh-output tagging. This separates fixed validation cost from the
size-specific materialization penalty.

The pinned SpiderMonkey source explains the allocation mechanism:
[`BufferGetterImpl`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/TypedArrayObject.cpp#L1794)
calls `ensureHasBuffer`; that function creates backing storage and copies inline
bytes, while already-malloced storage can be transferred without a byte copy.
[`WeakSet.add`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/WeakSetObject.cpp#L28)
uses the engine's weak-collection insertion machinery. These source facts and
the factorial controls support keeping the private WeakSet brand while avoiding
unnecessary backing-store inspection on guaranteed fresh outputs.

The high-water differences are **not** allocation counts, a memory-leak finding,
or a partition of all GC/allocator costs. No allocation profiler was enabled.
RSS includes host/runtime code and allocator retention; later instances in a
measurement process inherit its cumulative RSS maximum. Within-instance timings
are correlated. The wrapper model does not reproduce every production overload
branch, and different native hex implementations alone cannot attribute their
timing difference to the facade.

## Brand controls and semantic boundaries

The own-symbol-property control is reflectable and its token can be copied onto
another object. It is excluded as a production brand. Class-private stamping
adds no reflectable key and rejects the tested spoof, but its 64-byte batch is
38.42 ms versus 25.87 ms for WeakSet insertion. It is only a control: realm,
species, repeated-stamping and lifecycle parity are not established.

Every pseudo-tagged control remains rejected by the production `Buffer.isBuffer`.
No production brand was weakened. Native hex-intrinsic controls accept only
valid even-length hex; their strict malformed-input behavior differs from Node.
They are not substitutes for the profile's truncating hex contract.

The implementation decision is consequently narrow: retain external input and
species validation, retain the private WeakSet, capture trusted native producer
and branding intrinsics, and skip revalidation only for outputs guaranteed fresh
by those captured producers. Actual before/after engines use the same separately
fixed scalar ABI; their comparison is recorded by `compare.mjs`, not inferred
from these controls. Probe APIs transport only signed 32-bit checksum results,
so the unrelated high-unsigned-result binding defect is not exercised here.

## Reproduce the controls

Preserve the original engine and its adjacent build metadata; current optimized
source must not be mistaken for the frozen baseline. Copy them to
`/tmp/starling-node-compat/optimization/baseline.engine.wasm` and
`baseline.engine.wasm.build.json`, or set `NODE_COMPAT_BASELINE_ENGINE`.

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
  /path/to/node-v22.14.0 tests/node-compat/optimization/build-probes.mjs

NODE_COMPAT_BENCH_HOST=/path/to/stock-wasmtime-42.0.1-benchmark-host \
  /path/to/node-v22.14.0 tests/node-compat/optimization/run-probes.mjs
```

`NODE_COMPAT_PROBE_OPERATIONS` and `NODE_COMPAT_PROBE_SIZES` select a disclosed
subset. Run measurements while other CPU-heavy work is idle. Inputs, outputs
and full untimed setup checksums match the pinned Node oracle. The original
engine hash is enforced; current-source production optimization is deliberately
outside this diagnostic component.

## Candidate semantic and portability checks

`candidate-component.mjs` combines the full existing native fixture with
`intrinsics-checks.mjs`. Those guest-safe checks use the actual registered module,
never the semantic factory/reference kernel. They test boundary sizes,
on-demand ArrayBuffer identity, species, prototype/proxy/wrong-typed-array
spoofs, public property shadows, excluded backing stores and post-install
replacement of web producers, fill, private-brand methods and prototype changes.
All replaced public methods must remain uncalled, and all replacements are
restored before returning.

Set `NODE_COMPAT_SEMANTIC_ENTRY` to the absolute path of
`optimization/candidate-component.mjs` when using the normal native runner.
`candidate-http.mjs` carries the same checks through the existing standard HTTP
transport; select it with `NODE_COMPAT_HTTP_ENTRY`. Use new external output
directories and preserve earlier baseline reports. Candidate verification does
not establish cross-realm behavior where the deployed engine provides no realm
creation API.
