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

The declared run is now consumed. [Preparation](runtime-preparation.json) binds
origin `http://127.0.0.1:61785` and [authority](full-contract-runtime-authority.json)
`906c12e3`; the original owner completes raw1/clean/protected. Config-show/dev/client
exit0/0/1. The [DATA review](actual-runtime-review.json) verifies HTTP24/cache52/
supplemental80/stream/function passes and preserves generation1→1/strict browser
failures. Request affinity, reliability and full Next acceptance remain false.
The [portable corpus](retained-raw-data-v1/README.md) is complete; current and
Git-mode offline checks pass. Run `python3 -I -B retained-raw-data-v1/check.py`
from this directory to verify the copied evidence without original paths or
target execution. Actual progress is recorded in
[progress.md](../../../../../progress.md).
