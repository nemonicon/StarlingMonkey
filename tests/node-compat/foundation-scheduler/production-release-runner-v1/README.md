# Fresh OFF release replay: source preparation

This is a new **source-only runner packet**, not a release or runtime pass.
Actual production pins remain null in the unchanged common
`production-regression-candidate-v3`. Every public entry rejects before reading
an engine, loading a toolchain/packager, following old controls or creating its
output. No native build, componentization, Wasmtime or guest ran here. Accepted
compatibility remains foundations-v11.

The packet supplies the remaining six-foundation replay and an all-fresh serial
eight-gate OFF batch. `run-release.mjs` runs, in order: core, allocator, stream/web,
six foundations, strict sync, strict runtime, strict late binding, strict
callbacks. It consumes the exact common-v3 and Buffer-owned followon-OFF entries;
the callback report name is singular `private-ticks-callback-results.json`.
All jobs use the same future fixed normal Release/OFF engine and fresh outputs.
There is no resume, copied success, accepted-v11 pass reuse or native build step.

## Preserved module semantics and writes

`run-optional.mjs` serially invokes `run-{path,events,string-decoder,assert,
querystring,util}.mjs`. Nine isolated copies—six runners, the shared scalar
harness and two Path oracles—are recorded in `runner-transformations.json`.
Every import/path/report/guard edit reverses exactly to the original bytes.
Fixtures and source oracles stay at their real original paths. Events' inner
strict-version guard names the actual private-ticks policy; no old metadata is
projected into the new policy.

The cloned scalar harness writes its report mirror into the fresh output.
Standalone Path, Events and StringDecoder mirrors are redirected likewise.
Path executes its copied `semantic.mjs` and `glob.mjs` with an explicit fresh
`node-oracles/` directory, reads those generated vectors/results, and records
actual vector paths. All five oracle writes are redirected, including
`glob-differences.json`. Original Node checks, budgets, ordinary-pattern policy,
VM shims, source pins and skipped virtual-cwd probe remain unchanged. The actual
guest bundle still imports installed native modules, with all no-facade checks.

Existing OFF controls are preserved: Assert and Querystring select the actual
v5 OFF engine, Util the actual v6 OFF engine. The old six-module orchestration
cleared Events-OFF; that default remains. The existing Events optional branch
is retained for an explicitly selected, exact historical v10 Events-OFF control.
Path and StringDecoder acquire no invented OFF flags. These controls prove only
their historical admission behavior, never a new scheduler engine pass.

The full original module bodies retain Node comparisons, aliases/cache/static
CJS, snapshots and repeated/fresh execution, deferred call/new/initializer
failures, namespace inspection, limits and real OFF admission. Additional report
checks preserve Path's three calls/two rejected initializers, Events' two calls/
seven rejected initializers, StringDecoder's three calls/three rejected
initializers, Assert's 784 comparisons/nine rejected initializers, Querystring's
210 separator and1,536 byte vectors/eight rejected initializers, and Util's eight
rejected initializers. Exact remaining assertions stay in the unchanged bodies.

## Fixed admission and evidence

`verifyReleaseOff()` first calls actual common fixed-production admission. It
then authenticates the common-v3 and followon-OFF indexes and captures the local
manifest's primitive digest. Final checks call the common pins-first recheck,
then compare the exact local manifest bytes to the captured digest before
parsing or following rows. No mutable returned report object supplies the
expected digest. Each module needs exit0, its full semantic report and
`release-module-admission-complete.json`; optional and eight-job scopes also
need `release-admission-complete.json`. A partial report alone is insufficient.

The 1,405-file seal covers both existing runner closures, finite original
fixtures/oracles, generated siblings and helpers, Path's primary upstream inputs,
old output guards and actual historical control engines/sidecars/sources. The
306 future native and three external embedding inputs remain a separate fixed
artifact partition. The18 unresolved relative references are pinned Node
upstream `../common`/`../common/fixtures` data handled by the preserved VM shims.
Archived/host-test sources remain hashed witnesses rather than runtime imports.
Npm provenance remains the existing checked toolchain/componentizer contract;
this is not a byte archive of all dependencies or future generated outputs.

## Executed host checks and remaining gates

`test-results.json` records **53 host-only checks**; `source-checks.json` records
**24 syntax/source checks**. Eight fresh negative entry children reject the null
pins before engine/toolchain/output access. Pure checks cover serial execution,
failure stop, no resume, report validation, exact old controls, reversible
transforms and local digest rejection before parsing/following changed rows.

The two copied Path Node oracles execute in a fresh owned output. They pass
**15,696 lexical vectors**, **220 invalid cases**, **934 upstream assertions in
16 files**, and **4,046 glob comparisons with zero differences**. All five fresh
output files equal their original bytes; all eleven old report/oracle outputs
remain unchanged. Raw stdout/stderr and output digests are retained in the host
report. Initial50-check evidence predates three added local-seal controls and is
preserved separately; neither stage ran a guest.

Actual future pin/freeze compatibility, positive fixed-artifact admission and
all eight guest results remain unexecuted. GC, focused protected29/getter gates,
RuntimeOnly, HTTP/both-host checks and milestone acceptance are separate. Buffer
GC does not prove tick queue ownership; no ALS, reset/reuse, performance or full
Node/module support follows. Host children are serial; this packet adds no
process-tree cancellation or in-flight disk-allocation guarantee. The host
prelaunch check stops new guest jobs below800MiB but does not lower the separate
2GiB native-build guard or prove enough space for an entire batch.

Future entry variables are `NODE_COMPAT_PRODUCTION_RELEASE_OUTPUT` for all eight,
`NODE_COMPAT_OPTIONAL_OUTPUT` for the six replay, or the original module output
variables for individual entries. All require nonexistent fresh directories.
Host-only reproduction uses the pinned Node22 binary and a fresh
`NODE_COMPAT_RELEASE_HOST_TEST_OUTPUT`; source checks use a fresh
`NODE_COMPAT_RELEASE_SOURCE_CHECK_OUTPUT`. Actual execution must wait for real
reviewed production pins and capacity. The packet index is the source-review
boundary; it is not an engine receipt or runtime acceptance record.
