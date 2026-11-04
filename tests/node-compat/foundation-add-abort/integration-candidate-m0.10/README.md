# Unapplied m0.10 Events integration, prototype-owned key revision v2

**No live patch is applied and no m0.10 engine or component is built.** This is
an integrated source candidate for review, rebased onto accepted m0.9. The base
copies match all 302 inputs and recipe `6ccabace…` of the immutable v9 OFF
engine, verified in [base-v9-match.json](base-v9-match.json). The accepted v9
archive, strict-v3 patch, embedding patch, old proposals and runtime reports are
unchanged. [results.json](results.json) pins the complete proposed patch and
preparation evidence.

## Combined behavior proposed

The optional Events manifest becomes `sm-node-22.14.0-m0.10`, retaining exactly
the sixteen pinned Node22 namespace names, `events` alias, callable default
EventEmitter and named/default relationships. `addAbortListener` becomes the
bounded supported operation. `once`, `on`, EventEmitterAsyncResource and the
other declared deferred operations remain explicit throwing functions. No
blank namespace or universal Proxy is introduced.

The finite factory receives exactly one private guest Symbol through the
existing strict evaluator in register.cpp. The independent generator validates
the actual pinned Node22 namespace, schema, finite graph, default identities,
constant types and deferred call/new errors. It strips exactly the declared
helper import and rejects unresolved source syntax; there is no ambient native
helper fallback. The captured local error helper uses own data properties and
null-prototype descriptors. The core m0.8 unsupported helper/version remains
unchanged. Seven other generated headers retain their bytes.

The structural facade preserves public validation and dynamic add/remove
calls, original callback identity, once registration, repeated disposal effects,
already-aborted microtask scheduling and disposal descriptors. It discards
queued callback return values to avoid Promise-reaction thenable assimilation
introduced by Starling's existing queueMicrotask implementation. Fake public
signals remain observable; a native-only signal brand shortcut is not used.

The native listener tuple gains a derived-feature boolean. Dispatch continues
after stopImmediatePropagation, skips ordinary stopped records, and invokes
protected records in their original relative order. Active duplicates keep
their original flags. Function listeners receive the actual current target;
the existing global-event API's hidden target still maps to the engine global.
Object handleEvent and strict-v3 capture/cleanup remain in place.

Removed once records are retired from the target list before re-addition uses
the existing fresh-record path. Existing rooted dispatch clones keep the old
RefPtr marked removed; they cannot revive it when a nested dispatch re-adds
the same callback. The four-case ordinary Node oracle, including protected
synthetic abort and outer stopImmediatePropagation, is preserved in
[checks/node-results.json](checks/node-results.json). No old guest path was
executed. Node's actual linked-list implementation is distinguished from
Starling's cloned vector; general Node event-list traversal parity is not
claimed.

## Key ownership and public receiver guard

Revision v2 creates no new static/PersistentRootedSymbol. After successful
init_class_impl, the existing EventTarget prototype receives a SymbolValue in
a new reserved slot. The getter checks initialized/non-null prototype and
isSymbol before toSymbol. Registration immediately roots the returned Symbol;
option parsing roots it before property lookup can run user code or GC.

[gc-tracing-proof.json](gc-tracing-proof.json) cites the exact SM147 source:
JSObject::traceChildren traces native fixed/dynamic value slots **before** the
class trace hook; SharedPropMap::slotSpan includes all reserved slots. Therefore
the prototype's undefined Listeners slot can make its custom trace hook return
without losing the separately traced Symbol slot. Public SetReservedSlot
provides the write barrier. The key follows existing prototype/module closure
ownership rather than introducing an independent native root. Current Engine
code has no general destructor/context-shutdown protocol; this proposal does
not claim to repair general engine teardown.

The selected public EventTarget add/remove/dispatch entry points reject
uninitialized native class prototypes before listeners() can decode its native
pointer. The guard first checks exact native class/registered-derived
membership, then the inaccessible Listeners slot's isDouble and non-null
toPrivate. Pinned Value.h explicitly stores PrivateValue pointers with that
tag; there is no invented isPrivate API. Only trusted native initialization can
write this slot. AbortSignal is the registered native derived class and its
create path calls EventTarget::init, so initialized signals remain valid.

Nine ordinary Node-only receiver cases show the tested prototypes throw
**uncoded TypeError**, including structural addAbortListener forwarding; the
initial ERR_INVALID_THIS assumption is retained as a failed host-harness
expectation, not a native finding. The staged manifest states the precise
bounded error policy. The old Starling prototype paths were not executed.
Future negative component tests must require the new reviewed source pins and
actual derived macro ON throughout the C++/embedding receipt. Never run these
receiver negatives on Events-OFF engines, where this guard is intentionally
absent.

## Layout, installation and receipt contract

Events remains default OFF. Its ON branch requires existing web event, abort
and queue-microtask targets and adds guest dependency/link edges. Actual earlier
add_builtin declarations establish initializer order; add_dependencies does
not. No new host capability, timer task, clock or poll import is selected.

The derived NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER macro propagates through
extension_api INTERFACE, never as a register-only flag. In addition to the
listener struct, the new prototype slot changes EventTarget::Slots::Count from
one to two and thereby shifts AbortSignal::ParentSlots/Reason and subsequent
slot indices. **Every affected C++ TU must agree.** The recipe verifies the
macro in every actual repository builtins/runtime C++ command and the real
external embedding command, and records the exact guest prerequisite options.
OFF excludes the symbol, new slot, receiver correction, protected iteration,
record retirement and new dependencies; accepted macro-OFF code remains.

The recipe uses a distinct `entropy-entry-v1-strict-callback-v3-protected-abort-v2`
namespace. Its policy ID is `sm-uncaught-event-v3-protected-abort-v2`, with
`sm-protected-abort-listener-v2` source extension. The original strict-v3 patch
hash and all four original source hashes remain verbatim in basePolicy. The
new actual source map separately requires the new EventTarget bytes and all
three unchanged runtime hashes. Ten exact protected-source hashes, the durable
combined native patch, actual macros and prerequisite options are guarded.
The old v3 attestation must never describe the new EventTarget bytes. The
durable native attestation patch uses zero-context unified hunks so its blank
context lines do not become outer-patch whitespace errors. Standalone use
requires git apply --unidiff-zero and the exact reviewed baseline hashes; the
recipe hashes it but does not apply it. The complete integration patch below
uses normal context and needs no whitespace exception.

Admission requires this new policy/source/layout receipt for the m0.10 manifest.
Legacy m0.3 manifests remain bound to their frozen source roots. The existing
legacy stream-OFF allowlist is not expanded or weakened; the synthetic test now
uses hash-matched immutable legacy manifest fixtures instead of current m0.10
bytes. Old m0.3 prototype callers retain their test support option; future
native Events runners explicitly select the m0.10 eleven deferred checks.
Their component runners remain unexecuted here.

## Preparation evidence and limits

| Check | Verified scope |
| --- | --- |
| Ten SDK30/SM147 checks | Actual staged native syntax; selected/OFF branches, registration with m0.9 stream-web code, AbortSignal/global targets and ON/OFF constexpr slot indices. No link or guest. |
| Nine CMake cases | Actual add_builtin configure/generate, dummy non-guest dependencies, default/OFF and missing prerequisites, all generated C++ plus dummy embedding layout flags and install declaration order. No compilation. Script mode separately proves only code-free listing. |
| 328 admission/bundler checks | Synthetic selections, source/patch/layout refusals and finite aliases. No engine evidence. |
| Eight header checks + six negatives | Exact Node22/schema/graph/helper binding; wrong input rejects before overwriting a header. Seven unrelated headers are byte-identical. |
| 27 existing Node differentials | Existing cheap EventEmitter semantics; no native protected-event proof. |
| Four facade groups | Fake public hooks, validation order, queued return-value discard and captured constructor/error fields. No simulated native key. |
| Four nested-once + nine receiver Node cases | Exact ordinary Node22 public behavior only. No Starling old path. |
| Shell/four Python parsers | Recipe syntax; recipe not executed. |

Static-root v1 and pre-receiver-guard reserved-slot drafts are retained under
history. Initial admission fixture failures, the initial SDK overlay-path
correction and the wrong Node prototype-code expectation remain distinguishable
from final preparation checks. They establish no guest failures.

Before support is promoted, root must review/apply the exact patch and build in
fresh namespaces after preserving v9. Require actual all-TU/embedding layout
receipts and linked class identities, then execute new source-pinned ordinary
Release components on Jco and fresh stock Wasmtime42 with imports[]. Cover
namespace/aliases/CJS defaults, optional OFF refusal, snapshot initialization,
already-aborted and disposal behavior, synthetic protected order/duplicates,
all four nested-once cases, corrected prototype rejection, valid native-derived
signals and callback receiver/currentTarget. Exercise callback throws and
queued unsupported calls at top level, detached jobs and deployed drained
boundaries; caught/handled-later controls must survive retained calls. Failed
instances are discarded. Replay existing strict-v3/old-foundation/codec gates
under the new policy ID, then test genuine existing Release moving-GC boundaries
with the key/receiver/once records alive. Target-host HTTP/import audits remain
separate acceptance gates. No DEBUG/OOM/fault/private-memory work is proposed.

General EventTarget parity, pre-stopped propagation/cancelBubble synthetic
events, registration getter timing, detailed receiver errors, process handlers,
AsyncResource/ALS, general AbortSignal container/Terminator cleanup and request
teardown remain bounded or deferred. Future ALS must use dispatch context for
fresh native callbacks and registration context for queued already-aborted work;
unconditional callback binding is incorrect. Request-associated owners must
dispose subscriptions explicitly. Target Symbol.dispose identity requires a
real component check; it is not globally rewritten to Node's registry symbol.
No performance or complete Node/Buffer/stream compatibility claim is made.
