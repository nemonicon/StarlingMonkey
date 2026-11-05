# Codec worker v3: import and pre-output diagnosis

The actual v3 worker rejected with empty streams; its top-level catch discards
the exception. This packet preserves separate read-only diagnosis, not a replay
of that worker or a claim that its original exception was captured.

- Authenticating the complete sealed source families and dynamically importing
  worker-body.mjs succeeds. No exported worker function or loader is called.
- A retrospective DATA check using the actual descriptor fails at the exact
  environment equality. The preceding descriptor, Root and namespace models pass.
- Pinned Node22.14.0, launched with the retained explicit minimal environment,
  exposes an additional macOS __CF_USER_TEXT_ENCODING key with value
  0x1F5:0x0:0x0 (uid501). Both Python's child launch and a benign Node spawn using
  the actual launcher's environment reproduce this. Neither runs the worker.
- A proposed pure environment policy permits only that Darwin key, with its
  exact uid-derived uppercase hex/zero/zero value. All eight explicitly selected
  entries remain exact; other keys and values remain errors. The same DATA
  check then passes all inspected pre-output guards. The original recorded
  launch timestamp is used solely for the retrospective quiet-window model.

The original silent failure is consistent with this demonstrated rejection,
but its exact discarded exception remains unobserved. Complete source audits,
module linking, and duplicated pre-output models do not prove a genuine worker
preflight, component loading, codec execution, calibration, timing or acceptance.
No output job is created and no authority/state/helper is projected or modified.
The sealed v3 packet and failed attempt remain unchanged.

Next: independent failure/diagnostic review, a new source successor with narrowly
bounded environment handling and retained bootstrap diagnostics, source review,
fresh actual prepared-plan proof and fresh run/window authority before retry.
