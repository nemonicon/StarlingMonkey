# Captured RSC request with an ordinary HTTP consumer

This diagnostic selects one actual391-byte multipart Server Action request from
the failed Wasm browser run. The uniquely matching local NetLog send-header event
supplies all19 original headers. The exact body, boundary and action-manifest
binding are retained in `request-capture.json`, `request-body.bin` and
`header-evidence.json`.

For each fresh listener, only Host/Origin/Referer are rewritten to its actual
canonical loopback origin. The old public correlation header is removed. Every
other captured header, including gzip negotiation and Content-Length, is kept.
This is a new semantic HTTP request, not the original browser socket or wire
identity. There is no React/Chrome client, redirect following or HTTP warmup.

The application, engine, component and observer envelope are unchanged. The
world remains the selected13 standard WASI0.2.10 interfaces; no host modification
or new service is used. The original strict browser failure remains failed.
Fresh-host/workload differences prevent attributing any result solely to the
consumer.

The Node HTTP client retains raw encoded bytes before validation and records
end/aborted/error/close plus response.complete. Normal host gzip decoding and
trailer checks are bounded separately. HTTP completion, complete retention of
observed bytes, durable result publication and semantic pass are separate facts.
Collection overflow, missing publication or uncertain cleanup stops the pair;
a fully recorded HTTP abort or semantic failure can remain failed and continue.

Root owns Source binding and the original600-second Wasm then300-second Node
owners. Both slots are prepared before the first action, with no retry or
replacement. Existing native/source/world guards run before/final. No result
accepts full Next.js, waives a prior failure or proves private Store identity.

See [progress](../../../../../progress.md) and
[the persisted-state report](../../../../../docs/node-compat/nextjs-persisted-callback-results.md).

Preparation initially failed before plan publication: the binder incorrectly
required default JSON serialization to reproduce a plan containing compact
inline arrays. `binding-preparation-format-failure.json` retains the observed
failure and exact partial preimages. The corrected binder verifies the semantic
inverse and separately preserves/read-checks original bytes; it makes no JSON
serializer byte-inverse claim. The controller literal replacement still has an
exact byte inverse. Fresh binding history is `source-history/binding-v2`.

Actual fixed pair: Wasm29465/600 and Node29725/300 both exit0 cleanly. Both
complete HTTP200 gzip RSC and2,963 decoded bytes, with1,488/1,491 encoded bytes.
[Primary review](actualreview.json), [independent gate](independent-runtime-gate-review.json)
and [raw index](raw-records/index.json) retain the evidence. The original browser
failure remains failed. See the [result report](../../../../../docs/node-compat/nextjs-rsc-http-response-results.md).
