Mandatory SOURCE-ONLY successor for immutable measurement-execution4b6.
The old proposal is not eligible for activation without this amendment and its
independent review. No activation, artifact verifier/preflight, command collector,
bundle, component, guest, target host, native/compiler or timing action ran here.
Future pair and timing authority remain NULL in4b6 and are copied unchanged.
`measurement-execution-activated-v2` and its staging sibling remain absent.

R's sealed source review96bc identifies M1: the old correctness collector used
55-second synchronous Wasmtime calls and checked exit0 before preserving a
structured status; current-arm observations were memory-only until arm success.
The old timing worker used an unvalidated fixed300-second whole-process cap.
Those are host collection/deadline defects, not evidence of a stream algorithm
failure. The original full20/14 run90660 did not publish a durable full Jco pass
or final completion. Failure peer c5a0 preserves its unknown failed case.

Root receipt793a records a SEPARATE fresh public case5, original HWM workload,
16 iterations, exact full Node trace/checksum match under a600-second cap and
177.338 seconds of operational wall time. It does not identify the original
failed case, prove full20/14, establish all-case deadline adequacy or provide a
one-iteration pilot/performance sample. The witness is copied byte-exact.

Only three host afterimages change: prepare-correctness.mjs, collect-worker.mjs
and measure.mjs. Full before/after hashes, unified patches and exact reversals
are in host-derivations.json. Every workload, provider, oracle, guest export,
WIT world, scheduler, graph guard, identity contract, min/max case and sampling
count remains unchanged. The two new host-only modules are deadline-policy.mjs
and audit-inputs.mjs, plus a separately derived owned-host helper. The latter is
the sealed60a helper with exactly one allowed-ceiling change600000→7200000ms;
its17 existing benign owned-child tests are authenticated, not rerun. This new
ceiling itself has source/data checks only. No induced timeout, cleanup or
external-cancellation experiment was performed here.

Future correctness collection writes a fsynced progress/start record with arm,
case, scenario, iteration count and call ID before expensive Jco exports. Every
returned raw string and full decoded value is exclusively persisted before
semantic validation. These partial files never claim a completed pass. Failed
validation still retains the original full counterexample. Completed arm data
is saved separately; no earlier report is overwritten or reused.

Each future Wasmtime invocation is an async, exclusively owned POSIX session.
The600-second cap is an explicit operational policy, not a general adequacy claim.
Launch arguments/start/deadline, streamed stdout/stderr and fsynced structured
terminal status/signal/spawn-error/timeout/cleanup evidence are written before
the caller checks exit0 or decodes its response. Decoded full observations are
persisted before validation. The helper uses only its own fresh PGID, handles
ESRCH races, TERM then KILL with5-second grace, a bounded close/reap allowance,
30-second heartbeat, and temporary TERM/INT handlers. It neither searches nor
signals unrelated processes. Source ancestry is explicit; there is no new
embedding API, native capability, guest clock or custom host service.

Public one-iteration pilots remain capped at600 seconds. For each arm/family,
the whole timed-worker estimate uses its recorded pilot and the shared chosen
N, unchanged1..16:

    work = pilotBatchMs * N * (3 warmups + 7 samples)
    first = pilotBatchMs * N
    startup = 120000 + 2 * max(0, pilotWholeProcessMs - pilotBatchMs)
    requestedDeadlineMs = ceil(2 * work + first + startup)

The separate first batch and observed startup/evidence work are accounted for.
The fixed hard maximum is7200000ms. Both pilot records, chosen N and each budget
are saved before admission. If either estimate exceeds that maximum, the whole
arm/family stops before timed workers. There is no clamping to the cap, N change,
sample clipping, early-good-sample selection, skipped case or later median from
a partial run. The unchanged42 calibration plus126 timed workers, AB/BA/AB,
three fresh timed processes/arm/family/comparison, three warmups and seven
correlated samples remain mandatory. Even an admitted estimate may be inadequate;
a real timeout remains a failed collection and requires separate review.

Original failures are persisted before post-operation auditing. A separate
owned source-only child has a180-second cap for exact source/authority/artifact
rehash; it invokes no guest entry. Original and audit failures remain separate,
and the original is thrown if both fail. No completed PASS can be published from
timeout, nonzero status, incomplete capture, surviving owned group or failed
source audit. Storage failure may prevent a receipt; raw stderr fallback reports
that limitation and no crash-durability guarantee is claimed. Existing in-process
Jco calls are not made interruptible by a JavaScript timer: persisted start
records identify the active call, and the external owner can stop that process.
No child is active during those direct Jco calls. Correctness now also carries
the2GiB initial/800MiB stop storage guards, previously timing-only in4b6.

`activate.py` is a concrete UNEXECUTED successor, not a generic runner framework.
It requires the caller-reviewed index of this mandatory amendment, hashes all
of4b6 before genuine verifier imports, and preserves4b6's exact authority parser,
actual344/external3/frozen/tool source delegation, two tool roots/22 links,
private primitive captures and exclusive pre/post source seals. It copies all26
old payloads, replaces exactly the three host bodies, adds the three host helper
modules, and records both parent4b6 and mandatory amendment indices. The fresh
output is measurement-execution-activated-v2; old4b6/v1 sources are never edited.
The five source-publisher edits reverse exactly to4b6's producer.

Future command, only after independent review and separate actual pair authority:

    python3 activate.py OWN_AMENDMENT_INDEX PAIR_JSON PAIR_SHA ROOT_PAIR_REVIEW REVIEW_SHA

All prerequisites from4b6 remain: real four-arm14-case common-domain correctness,
fresh full20/14, replay/followon, fresh same-byte HTTP on both standard hosts,
actual graph/artifact review and a separate explicit Root timing phase/window.
No current native proof, ON-only authority, failed old run or this amendment
supplies those passes. Capacity/grow remain unavailable, RSS is process-level,
consume/FNV work remains in measured batches, raw controls stay unsubtracted,
and no native C++ state-machine/heap ownership/reset/ALS/whole Streams or
performance claim is made.
