# Peer collector V3: require fresh signal on normal output reuse

Dormant Source only. Heldfe1 V2 and the unused prepared Root runtime grant remain
unchanged; no V2 actor ran. The independent reviewer found that V2 accepted a
normal output path with an unexpectedly pre-aborted Request but no observed I/O
abort. Its final coverage remained inconclusive, yet it wrongly permitted
inspection4. This is a material reuse-gate hold, not an actual guest failure.

The only classifier change requires freshSignal for an output-close normal path,
or the existing strict known-handled-closed path with its full signal/abort,
cancel/lock/disposal/order/identity proof. Unexpected pre-aborted normal output
without that proof stops/discards. Fresh normal output with all eight writes
accepted may still inspect, but its I/O cancellation coverage stays inconclusive.
No marker, failed cleanup, arbitrary error or missing signal becomes a PASS.

`test-reuse-gate.mjs` calls the actual exported old/new parser and analyze on the
same synthetic log DATA: old accepts, new refuses. It also preserves the fresh
eight-write/inconclusive case. The unchanged46-case test retains the strict
handled-close positive and prior negatives. No WASI objects, AbortController,
timers, socket, actor or guest is instantiated by these DATA tests.

Actor, TCP helper, native model, owner and existing test bytes are unchanged V2
copies. Only plan state/output prefix/failure description and this own index
change their Source identity. Same240 owner, two fresh cohorts,13 standard WASI
interfaces/8025, V3Source78c/ctor656/late643-compatible component role, raw-before-
gate capture, no app/mounts, original ownership/final protection. Actual target
and authority fields remain NULL. No deployment, engine, native compiler, host runtime, guest or network
action ran. Root must issue a fresh reviewed authority after independent review.
