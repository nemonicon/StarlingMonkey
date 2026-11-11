# Four-call lifecycle collector, v3

This unexecuted successor selects four ordinary GET calls in this order:
`/context`, `/clone-cancel`, `/clone-cancel-followups`, `/context`. It requires a
new V3 Root request and a fresh V3 output directory. The original collector and
its three-call results remain unchanged.

The entire V2 HTTP body reader, Content-Length completeness check, bounded raw
capture, actual component-validation/WIT joins, selected standard WASI0.2.10
allowlist and normal SIGINT0 shutdown requirements are unchanged. The existing
120-second outer owner covers four15-second HTTP deadlines,20-second readiness
and bounded shutdown. No extra warm-up HTTP request is added.

Successful collection says that responses were captured completely. Separate
comparison against the retained Node22.14.0 references must establish semantics.
No same-Store, resource-retirement, full-Next or production claim is made.
