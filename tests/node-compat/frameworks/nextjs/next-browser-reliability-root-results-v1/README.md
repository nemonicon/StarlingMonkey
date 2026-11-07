# Fresh-app browser cohort preparation

The [first fresh Node/Wasmtime pair](../next-app-runtime-root-results-v1/first-pair-review/README.md)
passes24HTTP/cache/stream/2strict-browser checks on each arm. Its portable DATA
reader passes Root readback. All three additional pairs are now complete:
native3/3 and matched Node2/3 pass, so the all-six strict gate fails. All144HTTP
checks and12 browser functions pass. p3-stock retains its actionPOST ERR_ABORTED,
missing body and three observer errors. Source/world/ownership/helper checks
pass on all six; no retry or failure filter is applied. The [portable cohort
reader](cohort-review/README.md) validates580 logical records and preserves
strictCohortGatePassed:false. The first V5 abort and matched Node reproduction remain
unresolved.

StockV4 supplies mandatory safe run-ID namespaces with the same V3 browser
worker and unchanged workload body,300s owner and strict error gates. Its73
inert checks and independent Source review pass. The new control command uses
that reviewed owner's actual pure selector:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/run-fresh-next-control.py --run-id FRESH
```

It requires retained private tools and the fresh application. Each runtime
launch requires at least1GiB free, writes an exclusive0600 request under a
canonical user-owned0700 directory, and delegates exactly one original owned
runner. `--prepare-only` intentionally skips the launch-space floor and writes
only a small request; it launches no Node, Chrome, server or app copy. Its real
preparation exits0, duplicate preparation refuses without overwriting, and an
inert mocked-zero-space check refuses before runtime/request creation. AST and
independent CLI/base reviews pass; reviewer B authored the stock owner and
reviewed Root's separate integration. No cohort or retry runs implicitly.

`prepared-members.json` fixes the six future members in order:
p1-stock,p1-native,p2-native,p2-stock,p3-stock,p3-native. Their exact authority
requests were generated with the two preparation-only CLIs before execution.
Reviewed `cohort.json` c185f2f8/15342 binds their immutable descriptors,23 shared
inputs, prerequisite DATA review83988ce9 and single-member launchere93fe0ec.
Root explicitly selected one member per command; every subsequent admission
verified earlier original monitors, results, source/world checks and the prior
launcher's own error-free completion. `final-audit.json` explicitly audits all
six including the last, with state COHORT_COMPLETE_STRICT_GATE_FAILED_V1 and
raw codes0,0,0,0,1,0. A clean retained raw1 remains a failure. Existing
source-mode stock cache writes and native
read-only-copy/separate-cache policies remain distinct.

See the [finite reliability protocol](../../../../../docs/node-compat/nextjs-browser-reliability-plan.md)
for failure retention, stop conditions, raw CDP/Playwright evidence limits and
the scope of any eventual positive observations.

This exact cohort and its launcher log namespaces are single-use. General
fresh native/control checks use the two `run-fresh-next-*.py` CLIs with new run
IDs. Do not delete prior outputs to rerun this cohort. The separate
[unmodified Node standalone comparison](../direct-standalone-control-root-results-v1/actual-review/README.md)
now passes once without the Module-provider/HTTP bridge and with the same
strict browser worker. This does not establish the failed member's cause.
