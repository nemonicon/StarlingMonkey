# `events.addAbortListener` dependency audit

This is a **source audit, public Node v22.14.0 oracle and ordinary Release initialization diagnostic**, not an installed implementation. Production `builtins/node-compat/events.mjs::addAbortListener` remains an explicit deferred operation. No native build, host service, DEBUG execution or allocation-failure test is added by this audit.

The [Node oracle](node-oracle.mjs), [results](node-results.json) and [upstream source ledger](node-source-ledger.json) pin Node v22.14.0, commit `5d2feb257bcee090e57900eb51720171a6aa92f3`, and the exact executable/source hashes. The [Starling/SpiderMonkey ledger](source-audit.json) records the actual source inspected. The [implementation proposal](native-proposal.md) is uncompiled and requires separate review and component validation.

Run the oracle with the exact Node binary:

```sh
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-add-abort/node-oracle.mjs
```

The runner writes only its two owned JSON reports and uses ordinary public APIs. Isolated child processes observe listener exceptions through public `uncaughtException` handlers; they do not inspect Node private runtime bindings. The official upstream test files are downloaded and hashed, not claimed as executed.

The oracle passes **16 public case groups and two isolated listener-throw cases**. Its ALS case uses actual `node:async_hooks`: fresh and synthetic dispatch run in the dispatching store; an already-aborted queued callback runs in the registering store. Root context is restored afterwards.

## Reference contract

The reference accepts structurally signal-like objects, validates the listener before reading `aborted`, and calls public signal methods dynamically. A fresh registration is a once listener protected from propagation stopping; a synthetic abort event also consumes it. An already-aborted registration queues a zero-argument microtask with undefined receiver, which disposal cannot cancel. Fresh callbacks receive an Event and signal receiver. Repeated disposal is effect-idempotent on a native signal but repeats a fake object's remover side effects. The disposable has a null prototype and one ordinary enumerable symbol method. These are measured details, not assumptions based on the API name. [Pinned Node implementation](https://github.com/nodejs/node/blob/5d2feb257bcee090e57900eb51720171a6aa92f3/lib/internal/events/abort_listener.js), [Node 22 documentation](https://nodejs.org/download/release/v22.14.0/docs/api/events.html#eventsaddabortlistenersignal-listener)

Duplicate registration retains the original listener tuple's flags; an ordinary duplicate is not upgraded to protected/once. Dispatch removes once listeners before invocation, continues to later protected listeners after a propagation stop, and reports synchronous exceptions asynchronously. Promise-like callback results also have a rejection-reporting path in the source; this audit does **not** execute that async-return behavior. [Pinned EventTarget implementation](https://github.com/nodejs/node/blob/5d2feb257bcee090e57900eb51720171a6aa92f3/lib/internal/event_target.js)

Node's measured `Symbol.dispose` is `Symbol.for('nodejs.dispose')`. SpiderMonkey 147's selected headers enable explicit resource management, declare a distinct well-known `dispose` symbol, and its `SymbolClassFinish` installs well-known symbol properties. This supports a source expectation of a target identity difference; **no new target Symbol probe was run here**. A future facade must capture the target's actual global `Symbol.dispose`, preserve it, and explicitly document the registry-identity deviation from Node 22. Defining only a registry-keyed method is insufficient for native `using`/DisposableStack consumers. [Pinned SpiderMonkey Symbol implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/Symbol.cpp)

## Actual guest integration gaps

| Source and symbol | Verified source finding | Consequence |
| --- | --- | --- |
| `builtins/web/abort/abort-signal.h::AbortAlgorithm`, `AbortSignal::add_algorithm` | Unique-owned, traced algorithm list; no removal method. Algorithms run before creating the abort Event. | It cannot supply the public listener's Event, ordering, synthetic dispatch or disposal contract. |
| `abort-signal.cpp::run_abort_steps`, `abort` | An algorithm false result exits before list clearing/event dispatch; the caller currently ignores the returned bool. | A new callback must not silently reuse this error path. Existing failure propagation also needs a focused source fix and regression. |
| `event-target.h::EventListener` | Target-owned `RefPtr` listener records trace callback and signal; normal removal marks removed and erases the target list. | Reuse this ownership/dispatch mechanism instead of a second untraced callback registry. |
| `event-target.cpp::inner_invoke` | No protected flag; function receiver is the engine global; a propagation stop exits the loop. | Ordinary `addEventListener` does not implement the Node contract. |
| Same dispatcher | Once records are marked before invocation, but propagation-stop early return skips its final compaction. Exceptions are printed and cleared; callback results are ignored. | Removal cleanup, error-reporting and rejected-callback policy require explicit gates. |
| `event-target.cpp::Terminator` | A signal's algorithm retains target/callback/options; manual listener removal does not unregister that algorithm. `AbortSignal::finalize` delegates only to EventTarget finalization. | Audit and fix algorithm unlinking/native-list destruction before claiming prompt callback reclamation. No GC/retention measurement is inferred from source alone. |
| `builtins/web/queue-microtask.cpp::queueMicrotask` | Implemented through `CallOriginalPromiseResolve` plus `AddPromiseReactions`. | Ordering is useful, but an ignored rejected reaction is not Node's uncaught-exception behavior. |

## Admission and validation boundary

Keep the method deferred until protected dispatch/removal, callback receiver, microtask exception policy, symbol key and lifecycle tests pass. This is computationally cheap API semantics; it does not justify a new byte-processing kernel. The needed native work is guest event ownership and dispatch, with **no WASI capability added**.

The [ordinary initialization diagnostic](initialization-diagnostic.mjs) and [results](initialization-results.json) reproduce **two current strict-initialization gaps** on the immutable v7 Release engine `ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09`, with all 293 source inputs verified. A synchronous ordinary EventTarget listener and an AbortSignal listener each call unsupported `child_process.spawn()` during application top-level evaluation; the existing dispatcher clears the exception, so componentization succeeds. Both resulting components have zero imports, and Jco plus fresh Wasmtime 42 return `calls:1` and `completedAfterDispatch:true`. Direct invocation, an async event listener, and queueMicrotask reject as expected; an explicitly caught listener error succeeds. This is a preserved failure report, **not a compatibility acceptance result**.

Raw fixtures/components/log are under `/tmp/starling-node-compat/foundations-v7/add-abort-initialization/` and its adjacent `.log`. The checked-in result captures component hashes, packaging/host/source provenance and original rejection messages. Reproduce with the current audited componentizer and the immutable v7 engine/source root using `NODE_COMPAT_ADD_ABORT_OUTPUT` to select a new output directory; the runner intentionally asserts the old observed behavior, so a future fix needs a separately versioned acceptance runner rather than rewriting this evidence.

```sh
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm \
NODE_COMPAT_ENGINE_SOURCE_ROOT=/tmp/starling-node-compat/foundations-v7/native-freeze/source \
NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock \
NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js \
NODE_COMPAT_WASMTIME=/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime \
NODE_COMPAT_ADD_ABORT_OUTPUT=/tmp/starling-node-compat/add-abort-initialization-reproduction \
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-add-abort/initialization-diagnostic.mjs
```

The future component suite must carry valid public API calls through both Jco and stock Wasmtime, retain/reuse one component, verify a fresh instance, inspect final zero imports, and test snapshot-created signals/disposables and already-aborted microtask completion. Listener throws/rejections need an explicit guest reporting contract; no custom host error service is proposed. Reference Node process/`nextTick` behavior cannot be claimed by printing to stderr or converting it into an unhandled rejection.

Actual request cancellation and ALS integration remain separate from this public listener API. Fresh EventTarget invocation is synchronous within the dispatching resource; the already-aborted branch is a queued job. A request owner may remove its own outstanding registration on teardown, but must not silently change an application-owned disposable or invalidate all ALS stores. See the [resource-context investigation](../async-context/resource-model.md).
