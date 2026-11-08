# Uncompressed RSC body after the preceding workload

Updated 2026-11-08. A captured Server Action POST completes once on stock
wasmCloud and matched Node after the non-browser workload. Both original owners
exit0 cleanly. The comprehensive wasmCloud strict-browser failure remains a
required failing regression; full Next acceptance remains false.

| Observation | Stock wasmCloud | Matched Node |
| --- | --- | --- |
| Original owner / deadline | 53303 / 600s | 53776 / 300s |
| Fixture HTTP cases | 24 pass | 24 pass |
| Portable cache / supplemental checks | 52 / 80 pass | 52 / 80 pass |
| Persisted callback generation | 1→2 | 1→2 |
| Stream chunks / shell / ready | 3 / 0 / 1 | 3 / 0 / 1 |
| Following raw POST | HTTP200, RSC | HTTP200, RSC |
| Content-Encoding header | Absent | Absent |
| Captured entity / identity-copy bytes | 2,963 / 2,963 | 2,963 / 2,963 |
| HTTP complete / end / socket cleanup | Pass | Pass |
| Aborted / collection errors | False / none | False / none |

The request uses this compression-off build's
[captured 391-byte body](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-wasmcloud-root-results-v1/identity-request-body.bin)
without reserialization. It preserves the captured headers, including
`Accept-Encoding: gzip, deflate, br, zstd`, with only Host/Origin/Referer
substitutions and removal of the old public correlation header. Absent response
Content-Encoding is an independent assertion, rather than a changed request
preference. No redirect is followed.

Raw body files contain IncomingMessage data after transfer framing. The second
file is an identity copy, despite the inherited `body.decoded.bin` filename;
no content decoding, gzip validation or wire capture occurs. The cloud body
SHA256 is `7380905d27146fe15ed201e43b0ef131cdc306d60cb05807d8df66eeb4b88b55`;
Node's is `96613bc1e14cbf1d7a2940795faba2ae9a23661a9b1cd948b32aff8faed2e0c1`.
Each copy equals its own raw file. Equal lengths across hosts do not imply
equal bytes. The assertions use semantic markers and actual HTTP completion,
with no fixed 2,963-byte success target.

The unchanged prework runs on the same listener before the POST: five portable
cache records, six supplemental records, all24 fixture/SSR-action responses,
generation validation and incremental streaming. All response bodies, stream
chunks and publication records are retained. This preserves the request graph,
not deterministic scheduling or one Component Store/instance identity.

The application, engine237c, inner component6b20 and observer envelopee4c7 are
unchanged. The guest emits13 selected standard WASI0.2.10 interfaces. Stock
wash2.11.0 uses two independent mounts, three guest environment values and
self-origin egress, with configuration inspection before its single dev
process, registration plus TCP readiness and no HTTP warmup. Normal host
shutdown and complete lifetime stdout are checked separately from the HTTP
consumer. The Node reference retains its existing request bridge. No guest
service or host modification is introduced.

The [Root packet](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/README.md)
contains the one-shot controller, source-binding receipt, original-owner
receipts and independent reviews. Binding `84aaacc3` derives2,047 fresh protected
inputs; preparation `57b16d89` issues one cloud600→Node300 pair. The separate
[binding review](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/independent-binding-review.json)
reconstructs the declared input union without running retained helpers. Root's
[terminal DATA check](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/root-terminal-data-check.json)
rehashes both raw/copy files and checks actual prework and completion fields.
The [primary DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/actualreview.json)
(`04f53121`) and [independent runtime gate](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/independent-runtime-gate-review.json)
(`c02e546d`) pass. Both physical35-byte canonical generation2 records have no
pending publication. Complete cloud stdout is2,685 bytes for config inspection
and22,686 bytes for dev, with normal SIGINT0 shutdown and quiescent final stderr.
The [raw index](../../tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/raw-records/index.json)
(`3f20c56c`) retains208 payloads/5,576,656 bytes. Root rehashes every retained
payload; application/cache bulk, native/tool payloads and binaries are explicitly
omitted and remain under their existing guarded build proofs.

This establishes that the selected producer can deliver a complete uncompressed
RSC response to this ordinary Node HTTP consumer after the preceding workload.
The [failed full browser trial](nextjs-compression-off-wasmcloud-results.md)
still records POST7 `ERR_ABORTED`. Browser hydration, assets, client interaction,
React decoding/navigation and their scheduling differ here. No cancellation
initiator or harmless-cancellation interpretation follows.

The next diagnostic is a separate Chrome `fetch`→`arrayBuffer` consumer, with
the same captured body and preceding workload, without React navigation. Its
browser-managed headers must be observed and recorded; forbidden headers cannot
be silently presented as an exact replay. Keep the original strict browser
worker and every full-suite assertion unchanged.
