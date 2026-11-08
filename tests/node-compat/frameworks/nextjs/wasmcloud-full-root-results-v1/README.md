# Full Next contract on stock wasmCloud

This Root wrapper selects sealed actor `f22d805c` and the unchanged D990/f805
component/application. It reuses the original full-native and whole-world guards
in their original module contexts, deriving the actual 31/39/18 roles and all
825 source/target pairs. No host service, native build or new component is added.

The unbound wrapper `92a57220` and preparer `8d37bea1` passed Root/B/R Source
review. The sole actor-SHA binding produces wrapper `95f360f1`; reversing that
literal restores the unbound bytes exactly. Their `UNBOUND` docstrings describe
that historical Source cutoff. The preparer is unchanged. The external
[grammar receipt](source-grammar-checks.json) records three successful Node
syntax checks, with no application evaluation or target operation.

Preparation accepts `--self-origin http://127.0.0.1:<nondefault-port>` and does
not select or bind a port. The caller supplies one literal origin; the actor
leases that exact port through config inspection, releases it before one dev
launch, and fails on collision without fallback. Manifest/effective egress is
exactly one normalized URL with a trailing slash; the guest environment uses
the corresponding origin without a slash.

The one declared run ID is `wasmcloud-full-476b-first`. Preparation and runtime
outputs must be absent before use. The existing 600-second owner covers the
three commands and their descendants. The original full client/browser sources
and every cache/HTTP/stream/browser assertion are unchanged. Client failure
remains failure. Physical app modes do not prove read-only WASI descriptor rights;
the host's readiness log-size check is not a lifetime stdout bound.

Current actual origin, runtime authority and result are unissued. Source/grammar
success does not accept execution, request affinity, reliability or full Next
compatibility. Actual progress is recorded in [progress.md](../../../../../progress.md).
