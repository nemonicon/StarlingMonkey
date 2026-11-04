# Verified bounded m0.10 native Events extension

The optional native `node:events`/`events` module now has real-component evidence
for bounded `addAbortListener` behavior on exact production sources. Twenty-nine
normalized Node22 differential groups pass on both ordinary Release entropy
modes, with namespace/CJS/alias, snapshot, coded error and fatal/discard checks.
The separate callback-return observation confirms a **remaining Node deviation**;
this is not complete EventTarget, Promise, ALS or Node compatibility.

| Frozen engine | SHA-256 prefix | Bytes | Evidence |
| --- | --- | ---: | --- |
| OFF, all seven foundations ON | `1098e7531004a4ca` | 9,754,404 | [native-off-results.json](native-off-results.json) |
| RuntimeOnly, all seven ON | `dc5f834d84e43c34` | 9,761,460 | [native-runtime-results.json](native-runtime-results.json) |
| OFF, existing Release GC stress ON | `5dc29ba071bf85ad` | 9,755,953 | [native-gc-results.json](native-gc-results.json) |
| OFF, Events OFF control | `b2944204fafb110c` | 9,737,453 | [events-off-results.json](events-off-results.json) |

All four use the same 304 exact native inputs and recipe
`354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754`.
Each engine, sidecar, actual cache, compile commands, source, external embedding
and attribution files were frozen before fixtures. Original OFF configuration
evidence is immutable despite later GC reconfiguration of its build directory.
[evidence-receipt.json](evidence-receipt.json) pins reports, scripts, engines,
configuration and source verification. Engine binaries remain external under
`/tmp/starling-node-compat/foundations-v10/native-freeze/`.

## Actual functional evidence

[node-results.json](node-results.json) is the exact Node v22.14.0 oracle for the
shared [public-cases.mjs](public-cases.mjs): sixteen public groups, four nested
once-listener groups and nine receiver groups. The original sixteen-case Node
reference, including ALS context behavior, remains unchanged in the parent
directory. Detailed error messages and target Symbol identity are separated
from the declared class/code differential comparison.

For **each** entropy mode, the new ordinary component gate verifies:

- All 29 groups in three calls to one retained Jco instance and one fresh
  unmodified Wasmtime42 invocation. Structural validation/public hooks,
  synchronous fresh callbacks, already-aborted microtasks, disposal,
  non-assimilation of queued callback returns, synthetic abort, protected
  stopImmediatePropagation order and duplicate tuple behavior are included.
- The four nested once-listener cases match Node. A removed record held by an
  outer dispatch clone remains removed when a nested dispatch re-adds the
  callback; the new record is absent from that outer clone.
- Nine new-source receiver cases reject uninitialized prototypes with uncoded
  TypeError and retain initialized native-derived AbortSignal behavior. These
  negatives are executed **only** after [preflight.mjs](preflight.mjs) proves the
  new source, ordinary Release and derived macro ON across every affected C++ TU
  and the actual external embedding command. No guard-absent old/OFF path ran.
- Exactly sixteen namespace names, named/default and static identities, safe
  inspection, literal CommonJS default lowering and raw native alias caching.
  Raw alias namespace objects are per-specifier; their values/defaults are shared.
- Seven own-coded profile error cases, including call/new stubs, with captured
  constructors and inherited error setters bypassed. The core helper remains m0.8;
  the selected Events helper reports m0.10.
- A listener installed before snapshot fires once after resumption and retains
  correct receiver/currentTarget. Successful main, raw alias and handled controls
  each survive three retained calls plus a fresh Wasmtime invocation.
- Eight application initializers fail componentization, including fresh/queued
  synchronous/async unsupported callbacks, primitive throws, explicit unsupported
  construction and first-error reporting after the second listener executes.
- Five deployed failures are fatal on fresh isolated Jco and Wasmtime instances,
  which are discarded. Separate caught and microtask-handled-later controls
  succeed and remain reusable. No reuse after a fatal export is inferred.

The OFF components emit **no imports**. RuntimeOnly emits exactly
`wasi:random/random@0.2.10`; no version rewriting or custom host service is used.
Both use the pinned repository Preview1 adapter and audited ComponentizeJS0.23
v2 splicer. Selected interfaces, emitted WIT and component hashes are recorded
for every emitted fixture. Both target HTTP hosts are validated separately by
the root v10 joint HTTP gate; these focused reports do not claim HTTP deployment.

## GC and optional-OFF evidence

The Release GC engine compiles the existing Buffer `JS::NonIncrementalGC(Shrink)`
hook. Eight valid `Buffer.from(hex).toString('hex')` roundtrips run inside a
protected callback while signal, ordinary/once/protected listeners, disposers,
receiver and event objects are live. Post-GC protected registration/disposal,
nested currentTarget/receiver restoration and all four nested-once Node cases
pass in three retained Jco calls and fresh Wasmtime. This is combined-owner
evidence: the factory closure also owns the key, so it does not isolate
prototype-only Symbol liveness or prove ALS propagation.

A separate initializer retains its first latched thrown object through eight
valid roundtrips and reports `M10_ROOTED_AFTER_8`; the deployed counterpart fails
and is discarded on both hosts. There is no private GC metadata, fault, DEBUG,
raw guest-memory or malformed ABI observation.

The actual Events-OFF engine rejects both specifiers at bundler admission and
raw componentization, then runs a benign export on Jco and Wasmtime with
imports[]. Its actual layout macro is absent. It never imports the receiver
fixture or calls native prototypes. It establishes optional-module absence,
not correctness of guard-absent EventTarget prototype operations.

## Confirmed callback-return gap and other bounds

[callback-return-results.json](callback-return-results.json) records a separate
safe counterexample, explicitly `nodeCompatibilityPassed: false`. Ordinary
EventTarget and fresh protected AbortSignal callbacks return objects whose
`.then` getters only increment counters and return undefined. Node22 reads each
getter once. Fresh Jco and Wasmtime calls on the new ON engine read neither.
The already-aborted queued callback reads neither getter on both implementations.
No throwing/rejecting thenable, async Promise listener or Error poisoning is used
in this observation.

Pinned Node dispatch calls addCatch for callback returns; native inner_invoke
currently ignores its rooted rval. Real unhandled async Promise callbacks fail
under the independently tested strict rejection policy, but **Node-specific
returned-Promise/thenable addCatch/error routing is not implemented**. Future
scheduler/callback-result work must resolve that gap. No native, manifest,
CMake or recipe change was made during this observation or validation cycle.

The target's actual `Symbol.dispose` is unregistered with description
`Symbol.dispose`; Node22 uses registry key/description `nodejs.dispose`.
The disposable uses the actual target well-known symbol. Its identity is
measured and documented rather than globally rewritten or called compatible.

General EventTarget parity, pre-stopped propagation/cancelBubble, registration
getter timing, cross-realm behavior, process/nextTick error handlers, ALS and
AsyncResource, allocation/capture failure, explicit Engine reset and general
AbortSignal/Terminator/request cleanup remain outside these gates. No full
teardown, resource-reclamation, performance, complete Buffer or complete Node
claim follows. Historical private/static-root proposals, v3/v8/v9 evidence and
the stopped fault branch remain separate and unchanged.

Reproduction requires the frozen source/configuration and explicit pins:

```sh
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/foundations-v10/native-freeze/off-foundations.engine.wasm \
NODE_COMPAT_ENGINE_SOURCE_ROOT=/tmp/starling-node-compat/foundations-v10/native-freeze/source \
NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock \
NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js \
NODE_COMPAT_ADD_ABORT_OUTPUT=/tmp/starling-node-compat/foundations-v10/NEW-unique-output \
/path/to/node-v22.14.0 run-component.mjs
```

Use the RuntimeOnly engine for the second mode. The GC runner separately requires
the frozen GC engine and actual kernel stress macro. Output directories refuse
to overwrite an existing start marker. `run-off-control.mjs` is a distinct
module-absence harness; it cannot run prototype negatives.
