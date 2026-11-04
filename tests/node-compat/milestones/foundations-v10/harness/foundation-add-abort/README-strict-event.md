# Strict synchronous event exception candidate

This **private Release candidate** fixes the two swallowed-initializer errors in the [preserved baseline diagnostic](initialization-results.json). The shared production checkout, original v7 engines and original six-case diagnostic are unchanged. `events.addAbortListener` remains deferred; protected listeners, callback receiver corrections and complete Node error reporting are separate work.

The [native patch](strict-event-v1.patch) changes four existing files. It is guarded by `NODE_COMPAT_STRICT_INITIALIZATION`; the macro-disabled reporting path retains its behavior. The [ComponentizeJS patch](componentize-strict-event-boundary-v1.patch) adds a final strict checkpoint after export bindings are generated. These are guest changes: no host modification or custom host interface is needed.

| Ordinary evidence | Result | Scope |
| --- | --- | --- |
| [SDK/SpiderMonkey syntax](strict-event-syntax-results.json) | Four C++ files, strict and macro-disabled branches: eight checks pass. | Actual SDK30/SM147 flags; macro-disabled engine was not built/executed. |
| [Initializer and deployed tests](strict-event-results.json) | 16 initialization cases; three retained successful deployed calls and a fresh Wasmtime call; three separate fatal export cases on both hosts. | Errors include `undefined`, `null`, number, first-event retention, Promise-job dispatch, finalizer-nested dispatch and handled controls. Failed instances are discarded. |
| [Late export-binding tests](late-binding-acceptance-results.json) | Six valid interface-object getter cases pass; three rejected and three accepted. | Jco and fresh Wasmtime for accepted components; a handler attached in a later microtask still works. |
| [Release moving-GC gate](strict-event-gc-results.json) | A latched thrown object survives eight valid native hex round trips; clean component has three retained Jco calls plus fresh Wasmtime; fatal deployed object fails on both. | Uses existing `NODE_COMPAT_GC_STRESS` rooted-boundary Shrink collections. No DEBUG, fault simulation or private GC metadata observation. |
| [Runtime async observation](runtime-async-observation-results.json) | **Two existing policy gaps remain:** async event-listener and queueMicrotask failures return successfully in the guest. | Two retained Jco calls plus fresh Wasmtime per case. Fresh Node22 processes exit fatally; whole-process outcome and individual function-Promise outcome are different scopes. |

Every accepted component in these suites has **zero emitted imports**. Standard Wasmtime42.0.1 and Jco1.40 execute the components; there is no custom service. No wasmCloud, performance, cross-realm execution or full upstream-suite result is inferred from this candidate.

## Capture and checkpoint policy

`EventLoop::init` initializes a `JS::PersistentRootedValue` before builtin installation. A separate presence boolean distinguishes a thrown `undefined` from no error. EventTarget records the first callback exception before clearing it, then continues normal dispatch. Later event exceptions cannot replace the first. No message/code/then getter is read while capturing. The value remains traced through moving GC.

At the existing job, finalizer-drain and final initialization checkpoints, an already-pending direct exception takes precedence. Otherwise the retained value becomes pending with `DoNotCapture`, and the checkpoint fails. The latch is cleared only when consumed or explicitly reset. `eval_toplevel` now honors a failed event-loop result before further TLA/GC/reporting work. `finish_pre_initialization` also covers initializer-only embeddings without a content-script evaluation.

Pinned SpiderMonkey147's `JS_SetPendingException` implementation explicitly allows stored exception values from arbitrary compartments, and `DoNotCapture` stores the value without creating a new stack. This is source justification for the store, **not a cross-realm runtime proof**. A value-only latch preserves the thrown value, not the separate optional `ExceptionStack`. [Pinned implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/jsapi.cpp)

Capture failure leaves the pending failure in place and sets a terminal flag; a nested FinalizationRegistry report-and-clear path must not erase it. That path is source-reviewed and explicitly **not fault-injected**. Ordinary explicit catches inside listeners remain successful. Dispatched errors fail the next embedding checkpoint; wrapping `dispatchEvent` in a JavaScript catch does not handle an otherwise uncaught listener error.

This selected policy is fatal for an uncaught synchronous event failure in a deployed export. Discard that component instance. Successful retained calls are tested; reuse after a failed export is not permitted by this policy. `Engine::reset` clears retained state by assigning undefined while keeping the persistent root registered, but no current public guest/WIT entry invokes reset: its behavior is source-reviewed only. Task cancellation, finalizer drainage, request ownership and general teardown remain separate.

## The post-binding boundary is necessary

The [late-binding baseline](late-binding-baseline-results.json) uses an ordinary `api.run` object getter for a valid exported WIT interface. It dispatches a listener calling unsupported `spawn()` after Starling's `finish_pre_initialization`; v7 still componentizes successfully. The candidate therefore adds a versioned checkpoint at the end of ComponentizeJS0.23's `componentize_initialize`, after `bindExports` and binding lookup. It drains jobs, checks synchronous failures, then checks the actual unhandled-Promise set. A rejection handled by a later microtask is accepted before that final set check.

The first late-binding acceptance harness used both root `run` and `api.run`. Jco passed, but Wasmtime42's CLI rejected the ambiguous basename. That original script/log/component is preserved under `/tmp/starling-node-compat/strict-event-v1/late-binding-tests/`. The corrected test gives the root observer the unique name `inspect-result`; it changes no native code or host behavior.

## Reproduction and source provenance

Run [build-strict-event.sh](build-strict-event.sh) with Node22.14.0. It reconstructs exactly frozen v7's 293 input paths over the audited base checkout, changes only the four native files, and applies the extra embedding patch over exact source `78f4bef1…`. It reuses immutable downloaded archives/SDK/static SpiderMonkey with four build jobs. No SpiderMonkey build is performed.

The original frozen recipe remains preserved. [Its private transformation](build-recipe-strict-event-v1.patch) only admits and applies the fourth exact embedding patch. Locked aggregate Cargo, all OpenSSL source checks, archive pins, actual CMake options and before/after source inventories remain enforced. Engine receipts record the actual strict macro in EventTarget's compile command. The Release CMake cache and compile commands were copied and matched their recorded digests **before** reconfiguring the same private project for the GC artifact.

| Artifact | SHA-256 | Bytes |
| --- | --- | --- |
| Private Release | `c32c5e5769af39153e9219ab84b2dd3f68e16719441792e9e74e48f2d7c31a57` | 9,728,845 |
| Private Release + GC stress | `976c3ff7216926a270c60f0de212d200ef4a9ff98f53e5c3fb7d229aa2087630` | 9,730,394 |
| Native patch | `f6918e7f32a7e74c44dd0f7b951aaab5dd18910ce1b873a0e16d6527a126a7fc` | — |
| Extra embedding patch | `6a5519d540a533b94a96949ce391f3c6a28c92590fb13d0b9ff7805bf4ec25c1` | — |

The immutable ordinary Release engine/source/configuration copies are under `/tmp/starling-node-compat/strict-event-v1/release-freeze/`. The GC engine path is in `gc-artifact.txt` in the parent directory; build/test logs and retained component artifacts are alongside it. Both engines have identical native source manifests and the same private `libcrypto.a` hash. This is correctness evidence, not a performance comparison.

```sh
bash tests/node-compat/foundation-add-abort/build-strict-event.sh
NODE_COMPAT_GC_STRESS=1 bash tests/node-compat/foundation-add-abort/build-strict-event.sh
```

For runners, select the emitted `NODE_COMPAT_ENGINE`, its matching `NODE_COMPAT_ENGINE_SOURCE_ROOT`, the exact npm toolchain and v2 `NODE_COMPAT_COMPONENTIZE_MODULE`, Wasmtime42.0.1, and a fresh `NODE_COMPAT_STRICT_EVENT_OUTPUT`. Run `run-strict-event.mjs` on the ordinary artifact, `late-binding-acceptance.mjs` and `runtime-async-observation.mjs` separately, then `run-strict-event-gc.mjs` on the GC artifact. The historical diagnostic intentionally expects old v7 failures and must not be rewritten into a new acceptance test.

Remaining limits include deployed async rejection policy, `handleEvent` getter failure behavior, the pre-existing ignored `AbortSignal::run_abort_steps` result, uncatchable invocation failure without a pending value, capture-failure execution, explicit reset, broader finalizer/owner cleanup, and cross-realm behavior. No stopped DEBUG/fault branch is resumed or relied upon.
