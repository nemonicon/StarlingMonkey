This directory preserves an isolated EventEmitter prototype and the tests for
its optional native built-in registration. **The optional v4 native module gate and joint HTTP host gate now pass.** No complete
`node:events`, async scheduling or classic-stream compatibility is claimed.

The optional feature is `NODE_COMPAT_EVENTS=ON`, default OFF, requiring
`ENABLE_BUILTIN_NODE_COMPAT=ON`. It adds no host capability. The authoritative
[production manifest](../../../builtins/node-compat/export-manifest.events.node-v22.14.0.json)
uses profile `sm-node-22.14.0-m0.3`; the local manifest preserves the earlier
isolated proposal. Core and Path manifests/header bytes remain unchanged.

Source audit and demand:

- Pinned Node.js v22.14.0 exposes 16 ESM exports. Its embedded `events` source
  SHA256 is `ce56cf6f167106eab5a97486b494e73e2939e291769128dc3d0dd5d179c4bbe7`.
  [Node v22.14.0 lib/events.js](https://github.com/nodejs/node/blob/v22.14.0/lib/events.js)
  supplies `EventEmitter`, `init`, `_addListener`, `onceWrapper`,
  `removeListener`, `removeAllListeners`, `_listeners`, `listenerCount`, and
  `emit`. MIT attribution is preserved in `LICENSE.events` in both directories.
- Pinned Jco 1.40.0 `dist/node-builtins/events.js:createEventsBuiltin` wraps
  unenv2.0.0-rc.24 and applies jco-std `completeEvents`. The unenv core imports
  `node:async_hooks` and includes async helpers. Its adapter allocates a new
  emitter on an unbound no-new call, while Node 22 throws; unenv also uses
  `Symbol.for('events.errorMonitor')`, while Node 22's symbol is unregistered.
  These are reasons to audit semantics against the selected release.
- Existing events 3.3.0 implementation/tests were inspected for emit mutation,
  once/remove ordering, symbols, legacy subclasses, listener inspection and
  max listeners. Its promise helper does not prove Node 22 scheduler behavior.
- Demand is concrete in locked readable-stream 4.7.0: `readable.js`,
  `writable.js`, and `legacy.js` import EventEmitter and use constructor calls,
  on/emit/remove/prepend operations; `lib/ours/util.js` checks addAbortListener.
  The latter remains a dependency gate for abort-aware streams.
- [Pinned inventory](inventory.node-v22.14.0.json) records all 16 exports,
  callable names/arities, default/prototype members, four package versions and
  hashes of 15 inspected repository/dependency sources. It concerns the original
  isolated prototype; production-source evidence is separate below.

| Export(s) | Bounded status | Contract |
| --- | --- | --- |
| `default`, `EventEmitter` | partial | Same callable constructor and `default.EventEmitter`; legacy `.call(receiver)` and ordinary subclasses. Unbound no-new call fails. |
| `init` | partial | Ordinary receiver initialization; production constructor honors a replaced public `.init`, while named ESM binding retains its initial function. |
| `listenerCount`, `getEventListeners`, `getMaxListeners`, `setMaxListeners` | partial | Synchronous EventEmitter-compatible targets; listener arrays are copies. EventTarget targets fail explicitly. |
| `errorMonitor` | supported constant | Unique symbol; observes error first and does not consume an otherwise unhandled error. |
| `captureRejectionSymbol` | supported constant | `Symbol.for('nodejs.rejection')`. |
| `captureRejections`, `usingDomains` | supported constants | Boolean false. Enabling rejection capture throws a coded deferred error. |
| `defaultMaxListeners` | partial | Named ESM snapshot 10; constructor has mutable, nonconfigurable accessor, default 10. No builtin-export synchronization. |
| `once`, `on` | deferred module helpers | Throw on call/new. Instance `.once` and `.on` are distinct supported synchronous operations. |
| `addAbortListener` | deferred | Throwing callable; ordinary addEventListener cannot provide protected abort semantics. |
| `EventEmitterAsyncResource` | deferred | Throwing constructor/call until actual async resource/context integration. |

The 15 prototype methods are `setMaxListeners`, `getMaxListeners`, `emit`,
`addListener`, `on`, `prependListener`, `once`, `prependOnceListener`,
`removeListener`, `off`, `removeAllListeners`, `listeners`, `rawListeners`,
`listenerCount`, and `eventNames`. The on/addListener and off/removeListener
aliases share identity. Listeners run synchronously with emitter `this`,
registration order, active-array snapshots and original argument identities.
New/remove notifications, latest-duplicate removal, LIFO remove-all, once
wrappers, symbol names, reentrancy and inspection are tested. Exceptions
propagate immediately; Error values are thrown by identity, other error-event
values receive `ERR_UNHANDLED_ERROR` and original `.context`.

Only string/symbol event names are admitted. Limits are 65,536 listeners per
event, 4,096 names per emitter and **64 nested emit entries**. Exhaustion raises
RangeError `ERR_SM_NODE_LIMIT` and preserves existing registration state. These
are explicit deviations from Node's unbounded behavior. The original proposal
of 256 was rejected: a valid diagnostic component reached SpiderMonkey's own
recursion guard at 173 simple nested emits. The exact rejected source and
observations are preserved in [depth-proposal-results.json](depth-proposal-results.json).
The 64 policy passes Jco and Wasmtime, including unwind recovery; arbitrary
preexisting application stack can still reach the engine guard earlier.

The numeric max-listener threshold remains advisory. Its warned marker is
retained, but process warning delivery is deferred; it does not create a
console/stdio import. Event-name coercion, received-value error-message details,
private Node symbol layout, arbitrary `_events` mutation and cross-realm
receivers are outside the contract. Default's two CJS-only EventTarget symbols
preserve types/descriptions, but do not configure native EventTarget storage.
The namespace/default have no accidental own `then` or universal Proxy.

Implementation and ownership:

[`events.mjs`](../../../builtins/node-compat/events.mjs) is a small guest JS
semantic state machine, appropriate for listener ordering and mutation. It
captures language primordials before application execution. State uses ordinary
JS dictionaries/arrays/functions and a private WeakMap for depth; GC traces
listeners normally and the WeakMap does not retain emitters. No native byte
span, allocator transfer or host handle is introduced. Listener snapshots and
inspection copies preserve observable mutation semantics.

`generate-factories.mjs` emits an independent `events-factories.generated.h`.
`register.cpp:install_events` evaluates it once in the existing content realm,
then uses the existing `Engine::define_builtin_module` for `node:events` and
`events`, sharing export values/constructor state. Namespace records may remain
per-specifier; canonical repeated imports must cache normally. The existing
profile bundler lowers selected literal CommonJS require to the default callable
constructor. No runtime CommonJS loader or public JS registration backdoor is
added. CMake includes the source literal only when the optional flag is enabled.

Verified evidence and next gate:

- [node-results.json](node-results.json): refreshed 23 Node-versus-isolated
  prototype cases, 13 deferred call/construct cases and three resource bounds.
- [component-results.json](component-results.json): those 23 cases, safe namespace
  Promise inspection, limits/deferred operations, four initialization failures,
  two retained Jco calls and fresh Wasmtime 42; zero imports. This bundles the
  local prototype and does not establish native module registration.
- [native-node-results.json](native-node-results.json): production-source facade
  and generated factory each match27 Node cases, adding public init mutation,
  protected default-threshold descriptor, internal threshold behavior under
  public override, and the invoked retained-primordial operations. It also
  executes 13 deferred cases/three resource bounds. This is Node-only evidence.
- [native-component-results.json](native-component-results.json): native
  `node:events` imports remain external, 27 differential cases, static CJS, raw
  alias/cache/shared-value identities, mutable/snapshot state, 13 deferred
  operations/three limits, seven initialization failures, two retained Jco calls
  and fresh Wasmtime 42; zero imports. Exact OFF v4 engine SHA
  `347025c9641820c50206a9b6dee3f5e0a60b4d40c326e5c3ca66853c44fa5087`,
  all 271 frozen inputs verified. Actual v3 Events-OFF selection rejects the
  import before packaging. Raw alias namespace records differ, while canonical
  repeated namespace identity and every alias export value match.
- [native-syntax-results.json](native-syntax-results.json): actual pinned Release
  headers/wasm32-wasi `-Werror` syntax checks for all four Path/Events define
  combinations; core/Path header hashes unchanged. Not a linked engine.
- [cmake-policy-results.json](cmake-policy-results.json): four actual CMake guard
  configurations, with unrelated targets mocked; default OFF, selected ON and
  ON-without-core rejection. Not native compilation.

`run-native-component.mjs` ran against the v4 engine. It leaves native imports
external, verifies selected manifests/source receipts, compares 27 cases, tests
static CJS lowering, raw alias/cache/shared-value identities, mutable state,
13 deferred operations/three limits and seven initialization failures, then
invokes retained Jco and fresh Wasmtime 42. An optional actual OFF-engine input
checks bundler admission denial. Its executed results are linked above.

Lifecycle and future work:

Pure emitters/listeners may be snapshotted. Reused component instances retain
application listeners until removal; this is not request isolation. The native
runner explicitly tests a pure emitter invoked during snapshot and deployment.
Async expansion still needs Promise/nextTick ordering, rejection ownership,
bounded async-iterator queues/cancellation, AsyncLocalStorage propagation and
resource destruction.

Native reuse was checked against
[`EventTarget::dispatch_event`](../../../builtins/web/event/event-target.cpp#L363)
and `inner_invoke`: they require/pass one Event and report/clear listener
exceptions, which differs from EventEmitter spreading/exception propagation.
[`AbortSignal::add_algorithm`](../../../builtins/web/abort/abort-signal.h#L77)
is an existing protected guest hook, but exposes no matching removal API.
A future disposable abort bridge requires traced callback ownership and removal;
this implementation invents no embedding API or host service.

The [joint standard HTTP gate](../foundations/joint-results.json) then passed
three requests each on Wasmtime 42 and official wash 2.11 with Runtime v4 engine
`c89d9b4f0b5d8decac81e76dec030167e716bf2071c073d58e58a95a2f510de7`.
It combines all Buffer/stub/entropy checks with full bounded Path and native
Events 27 checks and first-deployed computed imports of all six bare aliases.
Only the existing six standard 0.2.10 HTTP/IO/type/secure-random interfaces are
selected. Counters `[1,1,1]` on both hosts do not establish instance reuse.
