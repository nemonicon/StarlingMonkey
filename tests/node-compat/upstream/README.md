This is a selected upstream regression gate for the opt-in native profile. It
reuses actual StarlingMonkey and ComponentizeJS test sources and assertions.
It does not claim an untouched CTest/Vitest run or complete upstream coverage.

The [current R2 acceptance records](allocation-r2-results.json) use engine
`99fdaa97c2fbdea67cb7e5463d3dd2ca10c6981615acb4483d442079f6aab65c`
and `componentize-js-0.23.0+sm-import-i32.v1+sm-clock-errno.v1`, with the
191-file source archive at
`/tmp/starling-node-compat/allocation-r2-native-freeze/source`.
Strict initialization is 9/9, adapted E2E is 19/19, upstream builtin fixtures
are 15/15, and ownership callbacks are 2/2. All 191 source hashes match. The
observed capability union is exactly the 18 selected standard interfaces at
0.2.10; the three handled-initialization components and ownership component
have zero imports. The integration crypto failure is retained as separate
historical evidence, and is not counted as a current rerun.

For this selected rerun, set the frozen engine/source root above, select
`NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js`,
choose a new `NODE_COMPAT_UPSTREAM_OUTPUT`, and run `run-selected.mjs` with
`NODE_COMPAT_INIT_EXPECT=strict NODE_COMPAT_UPSTREAM_SKIP_INTEGRATION=1`.
The collector explicitly records the omitted integration gate and its prior
evidence hash. This option does not convert an unexecuted route into a pass.

The newer [Phase 1 records](phase1-results.json) verify release engine
`680fb48a93921e5bfd077d12338d114913eecc5c6e6b12eb8f66e3e9cd8a554b`
with 191 matching source files and the separately audited
`componentize-js-0.23.0+sm-import-i32.v1` packaging module. All nine strict
initialization vectors, all 19 adapted Starling E2E cases, all 15 upstream
builtin fixtures and both ownership callbacks pass. This includes the
debugger-OFF initializer fix. The crypto integration trap remains: nine of ten
routes pass, totaling 81 subtests. No failure was converted into a skip.

The first run used the immutable optimized release engine
`3f5bf602ad2d1507db5c1bcd5b938984aba9ca65af4c5a840b5bf8fcd09d370f`.
Its 188 repository source hashes were checked and copied before subsequent
native changes. Raw output is under `/tmp/starling-node-compat/upstream-gate`.
The original ComponentizeJS fixture files match the pinned source archive
`8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10`
at revision `4d812f5a7b524cea5bcfd565cac55f3fab876a57`.
The checked-in [baseline records](baseline-results.json) retain the initial
failures; the [crypto diagnostic log](crypto-diagnostic.log) names the failing
upstream subtest and trap. Records are evidence of those exact binaries.

| Selected coverage on that engine | Observed result |
| --- | --- |
| All 15 `test/builtins/*.js` fixtures | 15 pass with the explicit adaptations below |
| Both `test/export-buffers.js` callbacks | Pass: 5,000 64-KiB echo calls; retained lists, empty allocations, aligned realloc/free |
| All 19 registered Starling E2E sources | 18 pass with embedding adaptations; `init-script` exposes disabled-debugger `print` bug |
| Ten registered Starling integration routes | Nine pass, totaling 81 subtests; `crypto` traps at Preview1 `random_get` |
| Nine initializer rejection/handling cases | Baseline behavior confirmed; four cases demonstrate the unhandled-rejection gap |

`export-buffers.js` calls a runtime retained-list accessor `snapshot()`. The
Starling `finalization-registry-snapshot` fixture separately verifies real
pre-snapshot GC cleanup; TLA error and deferred-runtime TLA fixtures also run.
The existing ownership test allows bounded GC high-water growth, and is not
an assertion that the guest never allocates or never retains memory.

Use exact Node v22.14.0 and the existing pinned npm toolchain. Freeze a newly
built engine before other agents change its source:

```sh
export NODE_COMPAT_ENGINE=/absolute/path/to/custom-engine.wasm
export NODE_COMPAT_UPSTREAM_FREEZE=/tmp/starling-node-compat/upstream-gate/new-freeze
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/upstream/freeze-engine.mjs
```

Then select the frozen engine/source and a new output directory. Do not mix
engines in one result directory; collectors reject engine/component hash drift.

```sh
export NODE_COMPAT_ENGINE=/tmp/starling-node-compat/upstream-gate/new-freeze/engine.wasm
export NODE_COMPAT_ENGINE_SOURCE_ROOT=/tmp/starling-node-compat/upstream-gate/new-freeze/source
export NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock
export NODE_COMPAT_COMPONENTIZE_SOURCE=/tmp/starling-node-compat/native-build/componentize
export NODE_COMPAT_COMPONENTIZE_ARCHIVE=/tmp/starling-node-compat/improved-build/componentize-source.tar.gz
export NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-build/package/src/componentize.js
export NODE_COMPAT_WASMTIME=/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime
export NODE_COMPAT_UPSTREAM_OUTPUT=/tmp/starling-node-compat/upstream-gate/new-run
NODE=/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node
"$NODE" tests/node-compat/upstream/run.mjs
"$NODE" tests/node-compat/upstream/buffer-ownership.mjs
"$NODE" tests/node-compat/upstream/starling.mjs
"$NODE" tests/node-compat/upstream/integration.mjs
NODE_COMPAT_INIT_EXPECT=strict "$NODE" tests/node-compat/upstream/initialization.mjs
NODE_COMPAT_INIT_EXPECT=strict "$NODE" tests/node-compat/upstream/collect.mjs
```

`NODE_COMPAT_INIT_EXPECT=legacy` instead records the original engine's four
known holes: detached Promise callback/async unsupported calls, an explicit
unhandled rejection, and a rejection queued by GC finalization. Direct calls
and awaited TLA reject already. A handler attached in a later initialization
microtask, including finalizer-queued work, must still pass. The profile-only
strict implementation checks the tracked rejection set after jobs and
pre-snapshot cleanup, not in the rejection tracker itself. Its first new-build
execution must be recorded separately from the baseline.
Reproducing the original packaging control requires unsetting
`NODE_COMPAT_COMPONENTIZE_MODULE` and explicitly setting
`NODE_COMPAT_LEGACY_COMPONENTIZER=1`. New acceptance runs use the audited
`sm-import-i32.v1` guest packaging module and record its exact provenance.

Harness differences are explicit:

- The real custom engine and repository Preview1 adapter are passed to the
  published ComponentizeJS API. The released engine is rejected. Every emitted
  interface must appear in the exact `regressionImports` allowlist in
  [common.mjs](common.mjs), all at 0.2.10. These broad upstream regression
  capabilities are separate from zero-import Buffer applications.
- Upstream's `pure` fixture disables only stdio/random/clocks; it leaves the
  default HTTP features enabled. Its name does not imply zero host imports.
  The export-buffer ownership fixture and handled-initialization fixtures
  disable all five features and explicitly check zero emitted imports.
- Tests run sequentially without upstream retries, with external output and
  loopback listeners. Original `tests/test.sh` serves prebuilt E2E components
  and performs its actual body/header/status/console comparisons. Its only
  shell change binds loopback; its process group is killed on timeout.
- The selected native profile adds exactly `Buffer` to the upstream globals
  fixture. The original failed golden is retained; after removing that one
  allowed entry the actual upstream assertion runs unchanged.
- Node22/Jco reports ``RuntimeError: wasm trap: wasm `unreachable` instruction executed``
  where upstream expects `RuntimeError: unreachable`. The disabled
  timer test retains raw stderr and verifies the exact trap and
  `subscribe-instant` frame before normalizing that diagnostic for the callback.
- ComponentizeJS's existing console override omits Starling's `Log:` prefix and
  routes error diagnostics to stderr. E2E copies retain original goldens and
  explicitly map these formats/streams, preserving exact assertion messages.
  Original first-run failures remain under `initial-mismatches`.
- ComponentizeJS parses exports before Wizer, so its source parser rejects the
  `syntax-err` fixture before SpiderMonkey's exact diagnostic can be checked.
  This is recorded as an unreached original diagnostic assertion.
- The upstream `init.js` is composed with the generated initializer in the
  existing initializer realm because ComponentizeJS occupies the single `-i`
  slot. Debugger-OFF builds currently advertise a `print` stub that returns
  false without a pending exception. The source fix makes that optional
  diagnostic absent when `ENABLE_JS_DEBUGGER` is OFF; debugger-ON behavior is
  preserved by the compile guard, but no debugger-ON runtime was tested here.
- The export-buffer fixture uses its actual hooks and callbacks, with a Node
  strict-assert adapter for its small Vitest assertion subset. Guest exports
  and allocation checks are unchanged. `assert.isBelow` is implemented as a
  strict bound, not a non-failing mock.

The crypto failure remains an open gate. A one-line trace in an external copy
of the actual server identifies the first failing original subtest as
`subtle.importKey.rsa-jwk-public.second-parameter-missing-key_ops-field`
(`tests/integration/crypto/crypto.js:426`). A valid public RSA JWK import calls
the native path that traps at `random_get`; the previous 15 subtests complete.
Reproduce that diagnostic without overwriting the full route records:

```sh
NODE_COMPAT_UPSTREAM_OUTPUT=/tmp/starling-node-compat/upstream-gate/crypto-diagnostic \
NODE_COMPAT_UPSTREAM_TRACE_CRYPTO=1 NODE_COMPAT_UPSTREAM_ROUTES=crypto \
"$NODE" tests/node-compat/upstream/integration.mjs
```

ComponentizeJS `stub_wasi.rs:210` unconditionally replaces Preview1
`random_get` with `unreachable`, even with its random feature enabled. Existing
`deps/patches/rand.patch` sends WASI `RAND_priv_bytes_ex` and `RAND_bytes_ex`
through libc `arc4random_buf`. The trap and patch are verified; the intermediate
libc call chain is an inference from those sources, not a symbolized stack.
A future guest bridge can use existing `host_api::Random::get_bytes`, which
the 0.2.10 host API wires to `wasi:random/random@0.2.10`. It must propagate
failure, enforce lifecycle/entropy selection and avoid retaining seed state in
the snapshot. Disabled entropy currently becomes deterministic upstream PRNG
behavior, as its original disabled-random goldens demonstrate; this is not
secure-entropy conformance.

The complete upstream WPT suite, debugger-enabled builds, concurrent Vitest
or AOT mode, every arbitrary-interface bindings fixture and all Node tests
remain outside this selected gate. WPT support is OFF in this profile. Several
bindings fixtures require synthetic custom test-host interfaces; they cannot
be treated as admitted deployed capabilities. No host modification or custom
service was introduced for these tests.
