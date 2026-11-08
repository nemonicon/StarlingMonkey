# Completion comparison after the Promise diagnostic

Status: recorded engineering proposal. Current B/D construction and trial status
is tracked in [progress.md](../../progress.md). A and C have separate historical results.
The current cd60 sample passes strict browser completion while the earlier c6ae
sample fails it. Both retain legacy generation1→1. That difference does not
identify a cause: cd60 changes await scheduling, holder allocation and logging.

Use a small predeclared comparison before changing native code or promoting an
entry. Keep the current engine, standalone app, selected standard13 world,
default browser worker, cache/HTTP/stream contracts and bounded stdout capture.
Build only the two missing entry variants through the existing constructor.

| Arm | Response-site logger | Explicit neutral-handler await | Artifact |
| --- | --- | --- | --- |
| A | Off | Off | Existing D990/V5 baseline |
| B | Off | On | New V5 descendant; only `return handler.handle(...)` becomes `return await handler.handle(...)` |
| C | On | Off | Existing c6ae response-only diagnostic |
| D | On | On | New c6ae descendant with the same single return-await change |

Keep the response logger identical between C and D. Do not add the child-Promise
holder or fulfillment logger to D: that would introduce another difference.
The existing cd60 artifact remains a separate diagnostic, not arm D. Both new
entries must preserve the original readiness/disposal boundary and exact
fulfillment value/rejection reason. The old async return already adopts the
Promise; this is an explicit scheduling comparison, not a missing-await fix.

Proposed fixed exploratory schedule: A,B,C,D then D,C,B,A, with one prepared
Node control at the start of each block. Declare all ten output namespaces before
the first action. Use a fresh owned server, app copy, cache and browser contexts
per trial. Run each once. Do not add repetitions, drop a result or stop after a
favorable outcome. An infrastructure failure remains recorded and makes that
comparison incomplete; there is no automatic replacement trial.

Each trial retains every original gate and its raw outcome. In particular,
generation1→1 must still fail the original overall contract. Summarize strict
browser completion separately, including POST body, finished and sizes, errors,
failed requests, NetLog and complete bounded stdout. Preserve instance/token
ambiguity and independent clock domains; do not infer private identities.

Two samples per arm are exploratory evidence, not a reliability estimate or
production acceptance. The comparison can guide a focused source investigation;
it cannot by itself prove a scheduling defect or justify a native fix. If no
discriminating pattern appears, preserve that result and avoid another broad
retry campaign. Request-state portability remains the separate
[module-state contract](nextjs-request-state-contract.md).
