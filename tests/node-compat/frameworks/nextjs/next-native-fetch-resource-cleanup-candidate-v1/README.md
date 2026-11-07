This uncompiled Source candidate repairs a bounded native Fetch ownership path.
It is based on six exact files from the genuinely compiled825 generation2251/
afb and leaves the40ee loader, Next, zlib, HTTP bridge, V5 entry, event loop,
current WORK, engine/component artifacts and failed runtime records unchanged.
No compiler, CMake, Cargo, componentizer, HTTP, guest, GC, DEBUG or reset action
is authorized or recorded by this family. Every future actual slot is NULL.

The observed Source gaps are concrete: read-task completion discards only its
integer identifier; incoming-body.close and native body-source cancel are TODOs;
body.subscribe does not retain the pollable needed by unsubscribe; normal fetch
future retirement drops no host resource. These gaps do not establish the cause
of browser request7 ERR_ABORTED or fresh JS-global observations. Existing valid
stream/gzip evidence and all failed acceptance gates remain unchanged.

`before/` contains the six exact compiled afterimages, with original descriptors
and accepted full-build provenance in afterimages.json. `after/` is the proposed
patch only. resource-cleanup.patch reproduces the entire difference; no existing
Source family or compiled tree was edited. These six replacements intend to
preserve435 native/387 support/3 embedding members. A future genuine825 selection,
new generators/build/constructor and complete normal app regression are separate.
No old engine metadata, constructor import-count131 or prepared authority may be
retargeted as proof of this Source. The same13 interfaces are intended; a future
component must independently audit its actual function imports and world.

The proposed lifecycle is described by ownership-plan.json. One BodyFutureTask
owns one read subscription, not the body's lifetime. Ordinary chunks retire
only that subscription. EOF retires subscription then input stream, consumes
body.finish, and drops the uninspected trailers future. This records EOF
retirement, not successful typed HTTP/trailer delivery. Direct cancellation
promotes the weak pending task, uses the real engine cancel_async_task (which
root-copies/erases before calling cancel), then drops the body after its children.
An already running task receives a cancellation request and disposes at a safe
post-borrow boundary. No first tee branch is closed by this path. Native append marks a sticky exclusion
before acquiring its independent subscriptions: new read cancellation preserves
that path's original no-op, and read terminal disposal refuses to drop its
resources. A currently pending ordinary read continues via the read path rather
than acquiring an overlapping append subscription. This explicitly defers
append lifecycle instead of merely describing it as deferred.

ResponseFutureTask uniquely owns its future wrapper, allocated with the
existing C++ new family. It retires its child subscription before the future,
including get-error, ready response transfer and task preheader abort. Not-ready
requeues without disposal. Nonstreaming ownership moves directly into the task;
normal streamed-upload EOF clears Request.PendingResponseHandle before transfer.
Source moves use std::unique_ptr; no generic WASIHandle destructor or borrow-drop
is changed. Generated drop_borrow calls really drop resources, so they are never
used as a second ownership release.

The existing include/link architecture matters: host_api.cpp quotes its local
wasi-0.2.0/bindings/bindings.h, while the linked generated binding TU uses the
wasi-0.2.10 header. The six new owned drop/body.finish declarations are identical
in both exact retained header witnesses. This narrow signature comparison is
not a general cross-version ABI proof, nor a claim that host_api.cpp directly
includes the0.2.10 header. No binding/WIT generation or capability is changed.

JS body owners, streams and incoming-response objects remain rooted/traced by
the genuine queue and rooted execution locals. Existing bytes move into the
ArrayBuffer only after allocation succeeds; terminal host cleanup allocates no
JS values or replacements for pending exceptions. Weak registration follows
the existing SupportsWeakPtr allocation policy. This is not a new recoverable
OOM or void queue-commit allocation guarantee. Response/Headers metadata and
body wrapper allocations remain cached as before; this candidate claims neither
universal native allocation cleanup nor empty host-resource tables.

Explicitly deferred: postheader/unreified Response abort and late reification/
exact reason behavior; both-branch clone cancellation; native fast-forward
BodyAppendTask; outgoing-upload abort/error before normal future transfer;
owned io-error diagnostic allocations; generic metadata/finalizer ownership,
including unpublished-response allocation failures; reset/GC/resource-count
proof. ReadableStreamError is not treated as if it invoked underlying cancel.
All covered and deferred public operations/states are listed in the plan.

Run `python3 -I -B check.py` for read-only afterimage, deterministic patch and
retained API-witness joins. `--current` additionally reads only the six exact
before sources and selected public API/header witnesses, never a binary or full
tool tree. `test-ownership-model.py` runs normative pure state/order models:
nonterminal chunks, repeated retirement, late old-task retirement, queued versus
running cancellation, primary identity and unique future transfer. The models
use no WASI object/API and do not execute or prove the proposed C++ implementation.
No C++ grammar/typecheck or native execution is claimed. normal-tests-plan.json
is a future Root-owned public-observable plan using existing app routes only;
it requires fresh actual build/component review and is not a resource counter.

R authored these proposed afterimages and prior native substrate. B independently
mapped the actual public WASI/WeakPtr APIs and ordering constraints; B did not
author these afterimages. Independent stopped Source review remains required
before seal. Actual behavior and any relation to the current failures remain
unproved. Historical child-mode annotations in closed runtime reports are also
not evidence for this patch: c101 requests no explicit child file/directory mode;
Root's separate erratum governs those annotations, with actual modes unchanged.
