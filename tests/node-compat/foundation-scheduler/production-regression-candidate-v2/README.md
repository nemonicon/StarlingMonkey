# Production scheduler regression runners: implemented preparation

This is a **source-only, unapplied runner packet**. It implements the finite
preflight and three runner siblings proposed in [v1](../regression-candidate-v1/README.md).
Both actual production pin sets in [pins.json](pins.json) remain `null`.
Every entry therefore fails before loading a toolchain, packager or existing
runner. A new reviewed revision must supply real frozen production306 normal
and Release-GC artifacts. The actual a49 diagnostic engine has extra diagnostic
policy/inputs and is rejected unchanged; it cannot supply production pins.
Latest accepted remains foundations-v11.

[test-results.json](test-results.json) records **34 host-only checks passed**.
[source-checks.json](source-checks.json) records 12 syntax checks, all29 ancestry
inputs unchanged, all306 current native-policy inputs matching, and665 sealed
local runtime inputs. No native compiler, componentizer, Wasmtime invocation,
component or guest ran. The successful real-artifact branch of the new
preflight remains **unexecuted**. Earlier host-test source/result are preserved
under [history](history/host-checks-v1/); their34-case result predates the fresh
external report-path option.

## Admission and artifact boundaries

[admission.mjs](admission.mjs) separates two pure checks from artifact work:

* `validateProductionMetadata` is an early shape/rejection filter. Its two
  synthetic positive cases are built from scratch without engine paths/hashes;
  results explicitly set `artifactProof:false` and `runtimeProof:false`.
  This is not standalone acceptance of the complete layered source policy.
* `selectActualPin` rejects the checked-in unconfigured document and absent,
  malformed or zero-digest pins. There is no environment override for pins.

[preflight.mjs](preflight.mjs) calls the pin gate first, before dynamic imports
or external engine/toolchain reads. With future reviewed pins it will verify
exact engine/sidecar bytes, all frozen copies and306 native plus3 external
embedding inputs; recipe869, policy98e80, helper78521 and embedding9dcb ancestry;
the frozen CMake cache/database and requested/observed flags;61 native compile
commands including the queue, four strict commands, and the separate actual
embedding command; and the real freeze/Rust/OpenSSL evidence. This bounded
harness requires unquoted captured command paths and all seven options ON,
ticks ON, entropy OFF, strict ordinary Release, locked Rust, no DEBUG/OOM.
The GC variant additionally requires the actual Buffer compiler GC macro.

The existing authoritative `selectedManifestsForEngine` performs full finite
layered policy admission and source rehashing. It is reused after fixed-file
checks, together with the existing native stream guard/decoder/factory
`nativePreflight` and corem0.11/direct-U8 expectations. Those helpers are sealed
inputs, not modified here. The existing native safety preflight accepts
ordinary Release-GC. Production recipe869 does not provide diagnostic-v2 raw
parent-target Ninja witnesses: no JSON row or witness is fabricated. Its real
embedding command remains the separate existing producer observation.

Future pin records must identify exact `native-freeze` paths, engine/sidecar,
cache/database/freeze-receipt hashes, recipe/core source pins, and a unique
frozen copy inventory. The preflight expects the existing production freeze
schema1 (`immutable-release-engine-frozen`) with306 native/3 embedding/61 native
commands/1 embedding command, plus frozen Cargo and4650-source OpenSSL audit
evidence. Its compatibility with a future real production freeze must be
reviewed then; no new freezer is supplied or claimed tested here.

## Preserved regression scope

| Entry | Existing semantic source retained |
| --- | --- |
| [run-core.mjs](run-core.mjs) | Dynamically loads unchanged `tests/node-compat/run.mjs` only after admission. Canonical semantic entry required;631 string/byte vectors, backing/brand/intrinsic/refusal checks, native aliases/caching and four initialization failures remain. |
| [run-allocator.mjs](run-allocator.mjs) | Generated sibling preserves installed fixtures,10 differential groups, five profile groups, six numeric-hook cases,240 refusal checks and11 current initialization failures. Keeps real v7 m0.1 call/new initializer denials and the real v10 m0.8 delegated Number-hook counterexample. |
| [run-allocator-gc.mjs](run-allocator-gc.mjs) | Generated sibling preserves the inline guest source byte-for-byte: eight native hex roundtrips, brands, backing/offset/view relations, snapshot state, three retained calls and a fresh Wasmtime call. No private tick queue ownership/ALS/reset proof follows from Buffer GC checks. |

[prepare.py](prepare.py) records every changed admission/path/report field in
[runner-transformations.json](runner-transformations.json). Reversing these
edits exactly restores both original v11 runner byte sequences. No original
runner, fixture or historical pin was edited; generated bodies use those actual
fixtures. The old strict boundary84a remains separate from the new scheduler
layer. Report mirrors go only into the new fresh output, never old v11 paths.

Every future run requires a nonexistent explicit output directory. After the
existing runner returns, the wrapper rehashes the frozen artifact copies and
the entire local input seal, then writes `production-admission-complete.json`
exclusively. Acceptance requires successful process exit, the existing semantic
report **and** that completion seal; a partial semantic report alone is not a
new pass. Existing Node22/toolchain/clock-v2 componentizer/Wasmtime42 checks and
zero selected interfaces/import audits remain in the unchanged harnesses.

## Input closure and reproducible host checks

[input-freeze.json](input-freeze.json) is a665-file pre/post byte seal, not a
claim to archive the whole npm tree. It covers the finite local import/require
graph, computed export manifests, all core fixtures, explicitly selected oracle
data, and the exact external `buffer_list.js` demand source. That external file
is data: the existing pinned `bufferListDemandModule` extracts four exact
methods and checks the oracle's generated-module hash; the npm module is not
loaded as the future guest implementation. Package provenance remains the
existing `loadToolchain`/`loadComponentizer` checked-artifact contract.

The seal also includes the **actual immutable** v7/v10 control engines,
sidecars and their597 frozen native sources as data. Their old behavior remains
control evidence, not new scheduler evidence. The future production306/native
and3/external partitions are checked separately from this local runtime list.
No binary was copied into this repository packet. Verify [index.json](index.json)
before consuming the packet; its input list is independently reviewed evidence,
not a mutable metadata substitute.

Run the host tests with the pinned Node executable and a new external JSON
path (the parent directory must already exist):

```sh
NODE_COMPAT_REGRESSION_HOST_TEST_OUTPUT=/tmp/scheduler-production-host-check-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/production-regression-candidate-v2/test-host.mjs
```

This executes only host assertions and three negative child Node entries;
impossible engine/source/host paths prove null pins stop before those are used.
It does not run a guest or packager. The output is exclusive and never
overwrites the sealed report. `check-source.py` similarly requires a fresh
`NODE_COMPAT_REGRESSION_SOURCE_CHECK_OUTPUT`; it uses Node `--check`, Python AST
parsing and read-only hashes. Regenerators are preparation tools, not commands
to change a sealed revision.

Strict suites, focused Events/getter counterexamples, installed stream/web's
wrapper, RuntimeOnly variants, HTTP/host replays and actual production normal/GC
builds remain separate gates in the [full regression plan](../regression-plan-v1/README.md).
Node1/1/0 versus native0/0/0 callback-return getter and Symbol.dispose registry
gaps remain; GC co-ownership qualifications and Reset OPEN remain. This packet
adds no public process, ALS, request reuse, classic streams or performance claim.
