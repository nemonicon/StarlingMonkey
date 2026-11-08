# Stock wasmCloud compression-off full-contract result

Updated 2026-11-08. The stock wasmCloud2.11.0 trial completes with **the full
contract failed**. All HTTP/cache/streaming and functional UI checks pass; strict
Server Action body completion still aborts. The observed response has no
Content-Encoding header. The Wasmtime/Node passing samples remain separate.

| Check | Stock wasmCloud |
| --- | --- |
| Original owner | 47197 / 600s, exit1, clean |
| Config-show / host exit | Both0; host stopped normally with SIGINT |
| Fixture HTTP cases | 24/24 pass |
| Portable / supplemental checks | 52 / 80 pass |
| Persisted callback generation | 1→2 |
| Incremental stream | 3 chunks, shell0 then ready1 |
| Functional counter / action interaction | Both pass |
| Script asset checks | Pass |
| Overall strict browser | Fail |
| Action POST7 | HTTP200, Content-Encoding absent, chunked |
| Body / sizes capture | Unavailable after ERR_ABORTED |
| Finished observation | requestfailed |

There is one failed request and three associated capture errors, all for POST7
at action-result-assert. The capture drain, context close and page close occur
later. Status200, functional UI success and available byte counts do not prove
body completion. The failed predicate is retained exactly; no replacement trial
or weaker test is substituted.

Configuration inspection passes before one dev launch. It selects the unchanged
served envelopee4c7 and reviewed app9106, two independent app/cache mounts, one
exact loopback self-origin allowlist and three guest environment values. Readiness
requires the pinned post-registration message and TCP; there are no HTTP warmups.
Source bindinga069e157 derives2,049 fresh inputs, using genuine4baf/23313 admission
and current52-field metadata. The inner6b20 constructor/audit remains separate
from the served-envelope composition. Thirteen selected standard WASI0.2.10
interfaces are unchanged. No host modification or custom guest service is added.

Both stock CLI stdout streams finish bounded capture with EOF/sync/close proof:
config-show2,737 bytes; wash-dev30,289 bytes/149 chunks. Host shutdown is normal,
the client exits1 naturally, and the original owner verifies all observed groups
gone. Stderr is hashed after that quiescence. Physical app modes0444/0555 plus
byte bookends establish preservation, not read-only WASI descriptor rights:
stock dev maps volumes with read_only:false. The writable cache is independent.

This failure shows that the compression-off configuration does not eliminate
the observed abort. It does not identify a host, zlib, scheduling, bridge or
browser cancellation cause. The earlier compressed failures, Wasmtime/Node
positive samples and fullNextAccepted:false remain intact.

[Primary DATA review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/actual-runtime-review.json)
(`81a9c56b`) and [independent gate recomputation](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/independent-runtime-gate-review.json)
(`185cecef`) verify the failed outcome and preserved checks. Review success is
separate from runtime acceptance. The [raw corpus](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/runtime-records/index.json)
(`09e9a040`) retains155 payloads/5,368,231 bytes, including client/project/owner
records, browser evidence and physical callback state. App/cache/xdg bulk and
binaries are explicitly omitted; their existing guarded proofs remain in scope.

Next inspect the recorded response-lifetime boundary and run a fresh ordinary
HTTP consumer after the same non-browser workload on stock wasmCloud, with a
matched Node control. Use this build's actual391-byte action body and restored
headers; expect absent Content-Encoding explicitly. A raw pass would narrow the
producer-versus-consumer boundary, not explain Chrome's cancellation or waive
this strict failure. Lifecycle, resource/reuse, reproduction, cost and release
gates remain outstanding.

The [boundary audit](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/response-boundary-data-review.json)
(`b5e4f87a`) and [source-cited next steps](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/next-browser-steps.md)
record a same-loader historyApi update, then canceled:true. No subsequent Document
request or Page.frameNavigated is retained. CDP dataReceived and five same-source
NetLog filtered-byte counts report2,963 bytes; neither supplies a retained body
hash, cancellation initiator or independent HTTP EOF proof. React can resolve
its root chunk before its reader reaches EOF, but deliberate cancellation is
not established. The [fresh request capture](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/identity-request-capture.json)
(`a45dea80`) binds the new402ef action identifier, exact391-byte body, all19
ordered headers and actual manifest. It sends no request or runtime authority.
