# Five context-interleaving controls

Source candidate only for future native construction/runtime. No component,
engine, guest, network or compiler action was run while authoring it. The actual
pinned Node22 host oracle and selected sealed AsyncResource facade host control
passed; those results are not native context/ownership proof.

The shared workload retains all five controls from the lifecycle plan:

1. Two real fresh logical branches enter before either resumes, retaining two
   ALS stores through nextTick, Promise, immediate and timer callbacks plus their
   continuations, with caller restoration and branch-local partial-order checks.
2. Neutral-created pending promises get both .then and direct await registration
   under A/B and resolve from the opposite branch. Promise.all, settled await
   and ordinary thenable assimilation retain the registering context and values.
3. Two logical readiness callers share exactly
   `readiness ??= Promise.resolve().then(prepare)`, with real neutral entry, one
   suspended preparation, no early result and later reuse. This is a logical
   shared-readiness test, not concurrent WASI resource ownership or real Next
   app.prepare coverage.
4. B disables a shared ALS while A's registered reaction is pending, observes
   disabled captures, then re-enables it. Snapshot, bind and AsyncResource use
   A's old captured values and restore B. A second ALS remains unaffected;
   exit's default Node22 disabled behavior remains explicit.
5. B normally aborts A's real timers/promises timeout. The original AbortError,
   ABORT_ERR, reason identity, captured/caller context and one settlement are
   checked. A separate ordinary finish precedes a later abort and stays settled
   exactly once. No invalid-handle/fault/reset/GC/OOM workload is involved.

`cases.mjs` exports collectContextInterleaving, contextPublicProjection and the
fixed five IDs. It imports no assert module or platform service. Checks are
strict booleans/object identity and ordinary Error. Full observed event order is
retained. The comparison projection sorts only assertion IDs/event inventory and
the explicit required partial-order edges; it does not invent a total ordering
between independent branches or normalize a failing observation into success.

The guest uses actual private runFreshRequest/runNeutralServer references and
the real public native ALS/timer APIs. It installs the exact sealed e5f26
AsyncResource facade on mutable CJS/default async_hooks during pure INIT, without
capturing context. Constructors run ordinarily in the controls. Frozen ESM
named AsyncResource remains old/deferred; it is not used. The old static/instance
bind/destroy/ID/hook limitations remain. No JS context stack or Promise patch is
implemented. Native owner identity is not exported and is not fabricated.

`guest-entry.mjs` is a deterministic raw single-file assembly, with only
incomingHandler exported. It combines the exact sealed facade, complete real V3
WASI adapter, first V2 readiness helper and shared workload.
bootstrap executes only in deployed prepareContextServer, before the real
Request handler. No app/filesystem bootstrap or application import is performed.
The existing indexed next-http WIT world (802595) and all eight WIT inputs are
referenced by exact descriptors; all 13 standard WASI0.2.10 selections and the
sole incoming-handler export remain unchanged. No host service or world was
added. Raw output is marker NEXT_NATIVE_CONTEXT_INTERLEAVING_V1, call ordinal,
request method and the complete collection. Future HTTP calls are 1/2/3 under
one positively observed instance; different instance ordinals must be reported,
not silently reset or inferred from host pooling.

The test-only Node reference uses actual Node ALS and AsyncResource. For the
public empty-store projection, each control owns a new managed set of ALS
instances, explicitly enables each through run(nonundefinedSeed), then restores
public empty state. Nested genuine ALS.run(undefined) calls provide the reference
empty-store boundary. These are not guest native boundaries, native owner
objects or native enable-bit equivalence. No projected boundary runs while the
disable control has its state disabled: its A/B entries and all neutral gates
are created first, then disable/re-enable use real unwrapped Node methods. Prior
disabled controls are not accumulated in later projection sets.

The actual oracle ran three collections with original Node AsyncResource and
three with the sealed facade over real Node ALS. Calls 1/2/3 passed in each arm,
with 41/44/31/22/15 assertions (153 per collection; 918 across six). It retained
the entire six results before comparing their public projections. Four grammar
checks and the oracle ran under original0af, each120seconds, all raw0/clean with
source/tool/WIT bookends. No first host failure occurred in this family.

At most two logical branches are active. Actual observed host peak is three
planned waits, including a five-second collection watchdog; the source rejects
above eight planned waits and uses no intervals. The 60-second abort target is
normally canceled immediately after the registration barrier. Watchdog time is
a test bound, not a timing oracle. Normal referenced work is settled/cleared;
these JS workload records do not prove native queue/pollable counts or root
release. A failed collection is retained as passed=false and must not be accepted
or treated as a safe reusable component.

Source assembly is `python3 -B -I build-entry.py --check` (no entry import).
Portable retained Source/host DATA checking is `python3 -B -I check.py`; optional
--current rehashes the selected current source/tool/WIT references. Both emit
only stdout when checking. run-host-checks.py is a one-shot authoring driver and
must not be rerun on this held family. Its entire original monitor directories,
stdout/stderr/started/terminal records are losslessly retained in host-raw.tar.gz;
node-oracle.stdout.jsonl is the exact whole stream for easy future comparison.

Future engine, metadata, Root action, component and guest runtime slots are NULL.
Root must independently review and issue construction/runtime authority. No
same-instance HTTP overlap, unref-across-calls, peer disconnect, post-Store-death
cleanup, snapshot/reset, fault, security, cost, full Node or full Next admission
is claimed by this candidate. Those later controls are deliberately separate.
