# Guest-completion capture: next runtime gate

The identity-negotiated native browser trial still fails strict response capture,
while the matched prepared Node control passes (review8151dc47). The next
diagnostic uses the [bounded guest entry](../../tests/node-compat/frameworks/nextjs/next-guest-response-completion-diagnostic-entry-v1/README.md),
without changing native code or the application. Its fresh componentc6ae13b9
constructs/validates successfully, with coordinated INIT DATA review `ee7511ac`.
Deployed observations remain unexecuted.

The entry observes GET/POST/actions and GET/action-result. Adapter records
distinguish existing reader EOF, output-child disposal return, body-finish
return, post-finally state and the normal-return site. Classic finish/close
events form a separate lane. Read bytes are not successful-write or peer bytes;
finish return is not cleanup, Promise settlement or transport completion.
Counters can collide across instances, so equal tokens/paths never establish
an identity or outer-to-inner causal join. Missing or ambiguous logs stay
unobserved. Logging itself can change scheduling.

## Source finding and proposed parent capture

The existing [e697 deployment](../../tests/node-compat/frameworks/nextjs/next-browser-netlog-native-candidate-v1/deploy.mjs)
`launch` function passes stdout directly to a file descriptor. The size check
in its readiness loop is not a lifetime bound. The original
[ownership monitor](../../tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py)
also inherits output descriptors; it does not supply a bounded stdout pump.

[durable-host.mjs::runOwnedCommand/pump](../../tests/node-compat/foundation-crypto/ownership-component-candidate-v1/durable-host.mjs)
provides the existing Node pipe/write/sync/close API pattern. Its limit check
runs after writing and continues pumping, so that implementation is not a
strict-cap sink. Its separate session/group policy must not replace the
full-Next actor's existing ownership mechanism.

The proposed minimal change is a parent-only stdout pipe with an8-MiB raw-file
limit. Check the next whole chunk against the remaining limit before each
serialized write. Preserve accepted bytes without decoding/filtering/slicing.
On overflow or write/sync/close failure, fail the run, enter the existing owned
shutdown, and retain explicit incomplete-prefix metadata. A hard cap cannot
also retain an unlimited complete stream: omitted bytes must remain unknown.
Never truncate the file or call that prefix complete.

Await pipe EOF, pending writes, sync and close before final hashing/publication
or marker interpretation; child exit alone does not drain Node pipes. Operational
readiness may inspect already-retained complete lines, with partial trailing
lines excluded so a split port cannot match. Select stock Wasmtime42's standard
`--no-logging-prefix`, already exercised by the gzip control. A pipe and logging
both perturb scheduling. No custom host capability or interface is introduced.

## Construction and runtime dependencies

Using the accepted INIT review, derive component/audit/return graph/caller/input
roles from the new actual constructor. Reuse `deploy.artifactRefs` and the genuine
full-native/world guards; freshly derive31/39/actual Source roles and all825
source/target pairs. Preserve failed D990 records as additional baseline evidence,
without retargeting their old artifact arrays to the new component.

Keep the original deployment prefix,600-second owner, default f19d NetLog browser,
standard13 WASI0.2.10 imports and every52/80/24/legacy/stream/strict-browser gate.
The identity header is not part of this next intervention. Capture failure and
application failure remain separate recorded outcomes; neither grants a waiver.
The parent capture helper passes nine finite Node22 file/stream tests, with
independent DATA review `b68296a6`. These cover the hard cap, whole-chunk refusal,
pending EOF, partial writes and sync/close/abort failures. They execute no Wasm,
Wasmtime or network; interrupted-client orchestration remains Source-reviewed
only. The complete controller/binder then passes whole Source review. Its first
actual run captures13,296 stdout bytes completely, while the original application
gates remain failed (review `d0085b5c`). The
[trace results](../../tests/node-compat/frameworks/nextjs/next-guest-completion-runtime-root-results-v1/README.md)
retain54 qualified marker records and a portable raw corpus. The
[export/Promise Source audit](nextjs-export-promise-completion-audit.md) maps the
remaining settlement/event-loop/host-task boundaries without finding a defect.
