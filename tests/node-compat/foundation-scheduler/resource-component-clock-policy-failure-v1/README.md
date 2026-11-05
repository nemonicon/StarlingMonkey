# Resource component clock policy refusal

The actual pure-control construction exits0 with a12,926,280-byte component,
imports[] and `run: func() -> string`. The timer/resource construction exits1
with clean cleanup after retaining the complete12,940,860-byte component and
emitted WIT before the final interface audit. No generated module or ordinary
guest export is invoked in either action.

The selected timer interfaces are only monotonic-clock and io/poll@0.2.10.
The emitted timer root additionally imports wall-clock, cli/stderr, io/streams
and io/error, all at0.2.10. The strict admission therefore fails and remains
unchanged. No missing output is reconstructed or partial candidate relabelled.
The raw failure transport deliberately does not inspect opaque error properties;
it proves a captured candidate at the componentize/final-audit stage, not the
unique underlying exception. Callable versus type-only/core/adapter imports
still require graph review.

The pinned ComponentizeJS clock feature retains both clock families and its
`has_io` condition skips the combined IO stub whenever clocks are enabled.
The native clock override also retains Preview1 clock calls, introducing the
adapter path. These source observations motivate selective guest pruning review;
they do not independently prove every emitted dependency's reachability. The
remaining timer fixture construction and all timer runtime gates are deferred
until that closure is corrected and separately reviewed.
