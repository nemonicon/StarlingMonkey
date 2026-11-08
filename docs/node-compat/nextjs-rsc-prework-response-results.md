# Raw Server Action response after the preceding workload

Updated 2026-11-08. The non-browser workload followed by a captured raw RSC POST
passes once on both Wasm and matched Node. Both original owners exit0 cleanly.
The original comprehensive strict browser failure remains failed.

| Observation | Wasm | Matched Node |
| --- | --- | --- |
| Original owner / deadline | 34292 / 600s | 34423 / 300s |
| Fixture HTTP cases | 24 pass | 24 pass |
| Portable cache / supplemental checks | 52 / 80 pass | 52 / 80 pass |
| Persisted callback generation | 1→2 | 1→2 |
| Stream chunks / shell / ready | 5 / 0 / 2 | 5 / 0 / 2 |
| Following raw POST | HTTP200, gzip RSC | HTTP200, gzip RSC |
| Encoded → decoded bytes | 1,486 → 2,963 | 1,492 → 2,963 |
| End / HTTP complete / gzip CRC and ISIZE | Pass | Pass |
| Aborted / collection errors | False / none | False / none |

The helper copies the exact4,382-byte request span preceding the browser block
in the original full client. Portable cache, supplemental concurrent/recovery
requests, fixture requests, SSR FormData action, generation assertion and
incremental stream retain their request ordering and original predicates. This
is a fixed dependency graph, not a deterministic network schedule. The helper
publishes its result with sync/close/readback before the raw POST starts.

The raw operation preserves the earlier
[captured request and consumer](nextjs-rsc-http-response-results.md):391 body
bytes, captured headers with only Host/Origin/Referer substitutions and the old
public nonce removed, no redirect following, and bounded encoded/decompressed
collection. Both bodies pass normal Node gzip validation and a separate Root
Python DATA decode with matching aggregate CRC/ISIZE. There is no gzip member
count or wire-frame claim. Response bytes differ; semantic markers and completion
are the contract.

The same listener remains running across prework and the raw request. That does
not establish one Component Store, instance reuse or JavaScript global lifetime.
The app, engine, component, observer envelope, host adapters and selected13
standard WASI0.2.10 interfaces are unchanged. This adds no guest service or host
modification. Browser hydration, assets, client-counter interaction and React
navigation are absent. Their absence and scheduling differences prevent treating
the consumer as the sole changed variable relative to the failed full run.

Collection and semantic outcomes are separate. All24 response body descriptors,
five portable EOF/byte records, six supplemental EOF/error/publication records
and actual stream chunks must be retained. Validator counts are recorded; a
fully captured semantic failure may produce fewer checks and remains failed.
Successful prework requires the original predicates and normal52/80 checks.
The raw result, publication receipt, post-receipt stdout witness, owned socket
cleanup and original host-group cleanup remain independently checked. There
are no replacement trials.

Evidence is in the [Root packet](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-root-results-v1/README.md),
[client source](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-client-v1/README.md)
and [runtime source](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-runtime-v1/README.md).
The [original full result](nextjs-persisted-callback-results.md) remains a required
failing regression. Full Next acceptance remains false.

The next bounded diagnostic is a separately versioned application with only
`compress: false` added to its existing Next configuration. Run the unchanged
full client and strict browser on Wasm and matched Node, with freshly derived
build inventory and browser assets. This standard Next option removes dynamic
HTTP compression without changing the native zlib implementation. A passing
sample would narrow the reproduction profile; it would not identify a zlib,
bridge, backpressure, cancellation or timing cause, or establish reliability.
Keep every compression-enabled failure and strict assertion intact.

The [independent runtime/gzip review](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-root-results-v1/independent-runtime-gate-review.json)
(`79d0bfa0`) verifies130 finite files, including all50 prework raw files per arm,
stream marker indices, both publication chains and owner cleanup. The separate
[binding review](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-root-results-v1/independent-binding-review.json)
(`fa90206c`) reconstructs the2,028-input union and checks preserved plan/controller
inverses without executing helpers.

The [primary DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-root-results-v1/actualreview.json)
(`026c026a`) also verifies both physical35-byte canonical generation2 records,
unique regular files with no pending publication, separate from portable cache
data. The [raw corpus](../../tests/node-compat/frameworks/nextjs/next-rsc-prework-root-results-v1/raw-records/index.json)
(`61ce2c24`) retains202 payloads/6,368,082 bytes, rehashed by Root. App/cache bulk
and binaries are explicitly omitted; existing guarded build/native proofs remain
the authority for those payloads.
