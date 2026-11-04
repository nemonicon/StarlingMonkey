Mandatory source-only reporting amendment for immutable correctness138a4.
The workload, fourteen boundary cases, Node oracles, scheduler/provider,
preflight and every success record remain unchanged. Only the host driver and
one host helper change. New activation must bind this index and afterimage.

Complete JSON records are compared without Node assert/inspect expansion. A
mismatch writes the full actual/oracle and optional raw Wasmtime carrier before
a compact RecordedMismatch is constructed. Outer catch paths recognize that
recorded error and do not attempt a second exclusive write. Fresh-Jco whole
rotation comparison uses the same gate. Counter/metadata wrapper keys are also
compared exactly; unexpected extra wrapper fields now fail this finite contract.
No trace fields are normalized, sampled, discarded or waived.

Owned host tests exercise equality, a last-row mismatch in2000 records, complete
saved data/raw carrier, no custom assert inspection and writer failure. No Node
workload, guest, native/SDK, packager, artifact verifier, host or timing runs.
Earlier successful source bundle138a4 remains valid because this is host-only.
