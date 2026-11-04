# Private scheduler diagnostic producer and component gate

This packet is **source only**. It contains a separate diagnostic engine producer,
exact preflight and executable component driver, but the driver has never componentized a guest or invoked one. Root separately
ran a v1 native attempt (compile/link completed, receipt publication failed
because parent target commands were absent from directory-local JSON) and
interrupted a v2 attempt at the disk floor. Neither is runtime acceptance. Root has separately applied the
reviewed production source layer; that does not establish runtime acceptance.
The latest accepted checkpoint remains v11. The v1/v2/v3 proposal and syntax
packets remain unchanged; this candidate does not rewrite their historical labels.

## Producer and complete source partitions

[The new diagnostic recipe](source/tests/node-compat/build-diagnostic-engine.sh)
is derived from the exact production recipe SHA869, not a relaxed old SHA354
receipt. Its [new-file patch](diagnostic-producer.UNAPPLIED.patch) adds a separate
script; [the review diff](diagnostic-producer.REVIEW.diff) compares it to the
production recipe without renaming/deleting that recipe. It requires explicit
`NODE_COMPAT_PRIVATE_TICK_BUILD=1` and `NODE_COMPAT_INTERNAL_TICKS=1`. All existing
Release, Rust lock, OpenSSL, dependency and source-policy guards remain. It uses
a separately named `.diagnostic-ticks-v1` source/build/artifact namespace and
refuses existing artifacts. No engine/SDK/library/source tree is duplicated here. Incremental build disk is
unmeasured: plan one fresh Release namespace with shared pinned caches, at most
four jobs, and an 800 MiB additional-physical-use/remaining-headroom stop budget
under Root monitoring. OpenSSL/Rust objects may still be rebuilt; do not assume
zero disk cost or delete accepted artifacts.

The producer passes the actual existing CMake
`CMAKE_PROJECT_ComponentizeJS_INCLUDE` mechanism, used previously by the
async-context probe, and the explicit diagnostic target option. [diagnostic.cmake](diagnostic.cmake)
uses existing `add_builtin`, linking the same extension API/SpiderMonkey targets.
It does not introduce a host service or a production process/global API.

The receipt keeps these partitions explicit:

| Partition | Count and validation |
| --- | --- |
| Production `sourceManifest` | Exact 306 inputs from the pinned private-tick source policy, checked before/after by the existing producer/helper. |
| `internalTickDiagnosticPolicy.sourceManifest` | Exactly 2 extra files: this packet's `test-extension.cpp` and `diagnostic.cmake`, independently pinned before configure and after compilation. |
| Combined declared native/build source partition | Exactly 308 unique paths. This count does not pretend to include every SDK/dependency/producer/generated artifact. Those retain their separate digests/audits. |
| Generated installation | Actual `INSTALL_BUILTINS` cache path and `builtins.incl` content/digest checked before and after Ninja; exactly one `NS_DEF(diagnostics::internal_ticks)`. |
| Actual diagnostic compilation | Exactly one observed TU command with Release, strict, entropy and private-tick/layout macros. No syntax command or requested value substitutes for this observation. |

The private receipt has `diagnosticOnly:true`, its own recipe digest, exact CMake
values and both source partitions. Default production selector admission must
reject it. The test gate uses raw ComponentizeJS only after [preflight.mjs](preflight.mjs)
checks every one of the 308 frozen files, engine/recipe/policy digests, native and
external embedding compile flags, the new policy names and actual installation.
It never projects private metadata into an old or production receipt. The
source-check protocol currently requires whitespace-free configured build paths;
this is a host test-harness restriction, not a guest API or host-service requirement.

The **new** [diagnostic CPP](test-extension.cpp) retains v3's same-realm rejection
and changes only three JS_FN attributes to `JSPROP_ENUMERATE` relative to v3.
`ScriptLoader::get_builtin_module` uses `GetPropertyKeys(...,JSITER_OWNONLY)`;
SM147 documents that nonenumerables require JSITER_HIDDEN. Without this fix, those
three named exports would be missing. The [diff](diagnostic-enumerable-exports.REVIEW.diff)
preserves that discovery. The new CPP has not been compiled; the previous v3
syntax result covers its API/ownership shape, not this later source file.

The content module has exactly `attemptReentry`, `checkResetGuard`, `default`,
`nextTick`, `scheduleTask`. Its default record shares the named function identities.
The initializer-realm record has `nextTick` and `default`, created using the actual
existing `Engine::init_script_global()` root. No extra persistent root or temporary
stream/host handle is used. There is no alias to public node:process. Production
factories will capture the private callable directly, not import a diagnostic ID.

## Concrete real-component driver

[run-components.UNEXECUTED.mjs](run-components.UNEXECUTED.mjs) is gated by explicit
`NODE_COMPAT_PRIVATE_TICK_DIAGNOSTIC_RUN=1`, the future diagnostic engine and its
frozen v2 source root. It authenticates label-specific frozen cache/database,
raw parent Ninja commands before/after, the three external embedding inputs and
all freezer copies; the old mutable original paths are never read. It uses existing `loadToolchain`, `loadComponentizer`, Jco
`transpile`/`componentWit`, the pinned repository Preview1 adapter, all five
features disabled and `selectedInterfaces:[]`. It requires Wasmtime42.0.1. It
creates only a fresh output directory, records every source/initializer/component
hash and emitted WIT/interface audit, and never overwrites accepted output. The 16 local runner/fixture/preflight/pins/
worker/decoder inputs, old Node phase oracle, and seven consumed host-policy/freezer inputs
are pinned in input-freeze.json, checked before packaging/invocation and checked
again afterward. Engine/metadata and all 308 declared source files are rechecked
at the end as well; the final manifest is not merely captured after execution.

The basic world exports only `run: func()->string` and must emit **zero imports**.
The late-binding world has `inspect-result` and an `api.run` interface. The gate
runs three retained Jco calls and fresh Wasmtime calls; Release and Release-GC
must be invoked with different actual engines/output directories. It does not call or import the production bundle selector, even indirectly: the
CLI string decoder is copied into a local host-only module. The private preflight
therefore does not grant diagnostic IDs through production admission. The corrected producer/pins live in diagnostic-producer-v2, preserving this
packet's first failed producer attempt. This packet's original producer source remains
historical; future builds use diagnostic-producer-v2. Native61 commands come from the actual
directory-local database; external embedding1 and diagnostic1 come from captured
parent-target Ninja stdout, never a fabricated database projection. All blocking
invocations have 55-second timeouts (the version query has ten seconds).

The ordinary corpus includes:

- Exact five-name namespace, default/named identity, safe missing then inspection
  and cached dynamic namespace. This catches the enumerable-export bug.
- Initial ESM/snapshot, synchronous deployed-entry, real IMMEDIATE AsyncTask, and
  Promise-job ordering against the preserved exact Node22 phase oracle. The
  deployed case schedules before its first await. Bundled CJS initializers follow
  ESM; no native CommonJS/process implementation is supplied.
- Shared object/Symbol arguments and strict undefined receiver, separately from
  GC ownership. The GC case enqueues an inline callback, inline object and an
  unregistered Symbol with no application closure/global strong co-owner, then
  performs eight valid Buffer hex operations while that entry remains pending.
  Actual Release-GC kernel flags must be observed. VM temporary retention is not
  instrumented, so this does not claim an exhaustive sole-root/liveness theorem.
- Two FIFO/identity batches of 3000 and 2000 separated by **native task** promises,
  crossing the 4096-slot ring. Awaiting Promise.resolve alone is not used as a
  tick flush inside the full job checkpoint.
- The 4096 callback, 1024 argument and 65536 retained-value caps, caught-error
  noncommit and continuation. The checkpoint's 65536-work failure is a separate
  fatal component; no independent infinite Promise-chain bound is claimed.
- A benign return object's then getter is ignored, compared to a fresh exact
  Node22 oracle. No callable-then/prototype poisoning probe is used. Rejecting
  async callback returns fail through the existing strict default policy.
- Reentry and active-reset **precondition** errors only. There is no Engine.reset
  call, cancellation experiment or claim of safe post-fatal reuse.

Five initialization/final-bind failures and three deployed/work-limit failures
use independent instances; each runtime-fatal Jco call and Wasmtime call runs
in its own fresh child process and exits, with every failed instance discarded. Three successful paired components catch the same queued throw, attach the
returned rejection handler during the checkpoint, and execute exactly 65536
self-enqueued callbacks. Generic negative traps establish boundary failure and
discard only, not a specific original cause; marker text is recorded if present
and never invented as a guaranteed ABI channel. Runtime trap messages are recorded; original thrown-JS reference identity across the canonical
ABI is not claimed. This is ordinary Release work, with no DEBUG, fault, OOM,
raw-memory or old hazardous native receiver probes.

## Initializer and configured-classic protocols

There is no invented custom-initializer option. The driver temporarily wraps the
actual returned `splicer.spliceBindings`, calls the original once with unchanged
arguments/features, and captures its `jsBindings`. Normal cases return that exact
result. Only the INIT case appends the pinned IIFE from
[initializer.fixture.js](initializer.fixture.js); the method is restored in
`finally`, and original/amended glue and hashes are saved. This is an explicit
**test-only packaging variant**, never a deployed host service or standard claim.

The IIFE uses existing `defineBuiltinModule`, imports the actual native INIT-realm
callable and schedules its INIT-realm callback. [The content fixture](initializer-main.fixture.mjs)
records the value at content-module BODY entry. It must already be 1, proving
initializer checkpoint completion before content evaluation. Because capture
itself is a Promise job, this is **not** before-jobs priority proof.

The additional [classic bootstrap](classic-bootstrap.fixture.js) uses only real
`opts.runtimeArgs:'--legacy-script placeholder.js --eval smSeed()'` and a real
`sourceName`. `smSeed()` is a single token; no quoting/tokenizer behavior is
invented. ComponentizeJS appends the real source path after those arguments;
ConfigParser therefore retains both the restored content path and inline source.
Engine runs the file then inline source, both with module_mode=false. The first
file uses a drained import job to capture the content-realm callable into ordinary
**global lexical LET bindings**, not global-object properties. The subsequent
inline evaluation synchronously schedules the scenario and returns the actual
`{run}` completion object used by bindExports.

[The ordinary Node22 oracle](classic-node-results.json) executed the equivalent
two-stage script using vm.runInThisContext and actual process.nextTick; stage two
runs in a real Node task after capture. It confirms the trace and that the three
lexical names are absent from global-object properties. The guest driver remains
unexecuted. This protocol tests **subsequent configured ClassicEvaluation**;
first-ever startup classic priority and a full Node CommonJS loader remain
unverified. [source-protocol.json](source-protocol.json) pins the actual APIs and
source files supporting both protocols.

## Remaining gates and reproduction

Root review/adoption of this diagnostic producer and the finite production
admission branch comes first. Then build normal and Release-GC diagnostic
engines serially with at most four jobs, freeze native306 + extra2, actual
CMake/cache/compiler/installation/producer receipts, and preserve v11 binaries.
The corrected v2 producer is the separate frozen diagnostic-producer-v2 packet;
its recipe/pins and the two unchanged native/CMake extras are immutable. The
producer is a new script at the proposed repository-relative location,
not a command to execute the partial source tree in this packet.

After approved builds, the real driver command uses pinned Node22, toolchain,
clock-v2 componentizer module, Wasmtime42.0.1, explicit new engine/source-root,
`NODE_COMPAT_TICK_OUTPUT` and the run opt-in above. Normal/GC output paths must
be fresh and distinct. It writes results only externally; this source packet
will not silently acquire a passed runtime status.

**Reset is OPEN.** Existing cancellation/Promise/finalizer/request teardown and
post-fatal reuse have not been repaired. No ALS or public process capability is
introduced. Root must replay existing core/allocator/prior-module/stream/strict/
protected/GC and selected-host regressions before any new accepted milestone.
The safe then-getter counterexample, Symbol registry gap and other v11 bounds
are not erased. No optimization or performance result transfers to this work.

The reviewed first build command (only AFTER Root applies this new producer) is:

```sh
NODE_COMPAT_PRIVATE_TICK_BUILD=1 NODE_COMPAT_INTERNAL_TICKS=1 \
NODE_COMPAT_JOBS=4 NODE_COMPAT_GC_STRESS=0 NODE_COMPAT_ARTIFACT_TAG=''  \
NODE_COMPAT_PATH=1 NODE_COMPAT_EVENTS=1 NODE_COMPAT_STRING_DECODER=1 \
NODE_COMPAT_ASSERT=1 NODE_COMPAT_QUERYSTRING=1 NODE_COMPAT_UTIL=1 NODE_COMPAT_STREAM_WEB=1 \
NODE_COMPAT_ENTROPY_MODE=OFF NODE_COMPAT_NODE=/path/to/pinned/node22 \
  tests/node-compat/build-diagnostic-engine.sh
```

A later GC build uses the same empty additional tag and its naturally distinct
.gc-stress artifact name and actual GC=1 receipt, after
normal functional acceptance and disk review; its .gc-stress name is already
distinct. Additional tags exceed NAME_MAX for the all-seven-ON configuration.
No successful scheduler build/publication or guest acceptance is claimed here.
