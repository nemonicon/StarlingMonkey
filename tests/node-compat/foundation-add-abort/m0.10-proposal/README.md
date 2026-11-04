# Unapplied m0.10 `events.addAbortListener` proposal

This directory reserves an optional Events extension. Nothing here is installed
or selected by a production engine. The seven actual SDK30/SpiderMonkey147
checks in [syntax-results.json](syntax-results.json) are syntax-only: no link,
componentization, native callback execution or final-import measurement occurred.
The existing production Events manifest still declares this API unsupported.

The baseline is the immutable v8 OFF engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9`
and its 293 frozen inputs. The existing strict-v3 callback policy is retained;
the proposal neither changes error checkpoints nor adds asynchronous host tasks.

## Proposed contract and source

[add-abort.mjs](add-abort.mjs) is a small private factory receiving one unique
guest Symbol. [events-facade.mjs](events-facade.mjs) composes it into the existing
finite Events graph. The proposed manifest retains the exact sixteen Node
v22.14.0 ESM names, `events` alias, callable default/EventEmitter identity,
default static relationships and explicit unsupported functions. It changes
only the bounded policy/version and adds this supported operation.

The pinned primary sources are Node v22.14.0
[abort_listener.js](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/events/abort_listener.js),
[event_target.js](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/event_target.js)
and validators. The existing [Node oracle](../node-results.json) and
[source ledger](../node-source-ledger.json) remain unchanged. They establish
Node behavior; they do not establish execution of this new proposal.

The facade preserves these observable operations:

- Structural signal validation precedes listener validation and the `aborted`
  getter. Proxy `has`/`get` errors propagate. Callable signals are rejected.
- A fresh signal receives the original function through its dynamic public
  `addEventListener`, with `once: true` and the private Symbol option. Public
  method overrides, callback identity and duplicate tuples remain observable.
- Disposal is a null-prototype ordinary object containing one symbol-keyed
  method. Each fresh-signal disposal repeats the dynamic public remove call.
  It does not become a thenable or use a Proxy.
- Already-aborted callbacks are queued, called without arguments, and cannot
  be cancelled by disposal. The wrapper discards their return values. This is
  necessary because Starling's existing queueMicrotask uses a Promise reaction,
  whereas Node's microtask does not assimilate a callback's returned thenable.
- Error constructors and property-definition operations are captured during
  trusted factory installation. Error metadata uses own data properties and
  null-prototype descriptors; inherited setters cannot replace the error code.

`generate-proposal.mjs` writes only this directory's generated header. It uses
the existing schema validator, exact Node22 namespace inventory and the strict
script packaging contract already used by native registration. Header/ESM
syntax checks do not invoke the factory or simulate a native event target.

## Native changes proposed for review

Apply [native-protected-option.patch](native-protected-option.patch) first, then
the independent [native-target-receiver.patch](native-target-receiver.patch).
Both are based on frozen v8 sources; the latter is reviewed separately because
it also corrects function-listener receivers for selected native EventTargets.
Neither patch has been applied to live source.

The protected-option patch uses a new **internal guest**
`EventTarget::node_abort_resist_key` function implemented by this proposal. This
is not an existing embedding API or host service. Actual pinned JS APIs are
`JS::NewSymbol`, `JS::PersistentRootedSymbol`, `JS::RootedSymbol`,
`JS::PropertyKey::Symbol`, `JS_GetPropertyById` and `JS::SymbolValue`.
`EventTarget::init_class` creates the unregistered Symbol before the Node
factory installs. Registration roots the result and passes it through the
existing one-argument strict factory evaluator. Initialization failure
propagates normally. No stream, timer, I/O handle or temporary Promise is made
to obtain the Symbol.

`EventListener` gains a native boolean only when the derived feature macro is
selected. Its existing callback/signal JS::Heap values remain traced through
the target's GCVector and cloned rooted dispatch vector. The Symbol is held
by a persistent GC root. No new raw JS pointer survives a GC boundary.

Dispatch skips stopped ordinary records while continuing later protected
records **in original registration order**. Protected callbacks are not moved
to a separate pre-dispatch list. Active duplicate registrations retain the
original flags; remove/re-add records receive their newly requested flags.
Existing strict-v3 once cleanup, rooted target, passive cleanup and first-error
latch remain in effect. A protected callback that throws does not prevent
remaining listeners from dispatching; the existing drained boundary rejects or
aborts/discards according to the selected strict profile policy.

The receiver patch gives callable listeners the actual current target. It
preserves the existing global-event API's hidden-target convention by mapping
only that known target to the engine global. Object `handleEvent` receivers
retain existing behavior. Both changes are guarded by the new feature macro;
macro-OFF public-call behavior is preserved. This is source/syntax evidence,
not a runtime receiver or cross-realm proof.

Using `AbortAlgorithm` alone is unsuitable. Existing
`AbortSignal::run_abort_steps` executes algorithms before ordinary event
dispatch, and the algorithm list exposes no removal operation. It would alter
relative order, synthetic dispatch, duplicate/removal and callback arguments.
The proposed public subscription instead uses existing listener ownership.
Manual removal drops the target's reference; an active dispatch clone can keep
it alive until that dispatch finishes. A retained disposer intentionally keeps
the signal and callback reachable, matching repeated public disposal effects.

## Integration work required before a build

[cmake-prerequisites.patch](cmake-prerequisites.patch) is an **unconfigured**
proposal. Events remains default OFF. Its ON branch verifies existing web
event, abort and queue-microtask targets, and adds explicit guest dependency and
link edges. Earlier add_builtin declarations determine installation order;
add_dependencies alone does not. The new derived macro propagates through
`extension_api INTERFACE` because every TU using `EventListener` must agree on
its layout. It must not be supplied inconsistently as a register-only flag.
No new WASI interface or host capability is requested.

The main Events generator would need to consume the new composed canonical
factory and manifest through its existing independent generator mechanism.
The temporary helper here is not a replacement production build entry point.
Existing module registration, alias/cache and bundler literal-CommonJS lowering
are reused; runtime require and syncBuiltinESMExports remain excluded.

The current build recipe pins all four strict-v3 native files, including
EventTarget SHA `431267539ab361832094fd212af3b3605241ea0f2ad196b132c6df78e33896d5`.
This proposed EventTarget change must obtain a new reviewed source attestation,
policy-source revision, private build namespace and actual macro receipts.
The old guard must continue failing until that review is complete. Do not
overwrite private v3, production v8, core m0.8 or m0.9 proof records. If m0.9 is
applied first, compose against its new frozen register/CMake hashes and retain
the reviewed literal/guard source identities.

## Remaining gates and explicit limits

Before support is declared, build a separate ordinary Release engine and check
the exact sixteen namespace/default identities, ESM/CJS aliases, schema,
capability admission and imports[]. Reuse the unchanged Node oracle cases for
public validation ordering, fake signal hooks, repeated disposal, synthetic
abort, ordinary/protected duplicates, synchronous abort order and receiver.
Add already-aborted microtask ordering, returned thenable non-assimilation,
disposal descriptors and actual target Symbol.dispose identity. Exercise
callback primitive/object throws, unsupported operations from top-level
listeners and queued callbacks, later handlers and retained-instance success.
Use actual Jco and fresh Wasmtime42; retain ordinary moving-GC tests separately.
No DEBUG, allocator fault or private-memory execution is part of this proposal.

The following remain bounded or deferred:

- Detailed invalid-value messages and broader Node EventTarget parity,
  including pre-stopped stopPropagation/cancelBubble synthetic events and
  registration-time handleEvent getter timing.
- Target Symbol.dispose is captured for native disposal integration. Its
  identity with Node22's registry symbol is not assumed or globally rewritten.
- No process error handlers, nextTick or AsyncResource parity is added. Fresh
  native callbacks belong to dispatch context; already-aborted jobs belong to
  queued registration context. Future ALS must propagate these through real
  engine hooks rather than unconditionally binding callbacks at registration.
- Request cleanup must explicitly dispose subscriptions whose owners expire;
  disposal is not automatic merely because a component is reused. Scope
  expiration and ALS store semantics are separate policies.
- Existing AbortSignal container finalization and `{signal}` Terminator
  unlinking need an independent lifetime review. This facade does not create
  an AbortAlgorithm and does not claim to fix those broader ownership gaps.
- Allocation/capture/wrap failure paths remain source-reviewed only. No fault
  simulation is proposed, and syntax checks establish no allocator-success or
  cross-realm claim.
