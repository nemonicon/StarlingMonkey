# Captured Server Action HTTP response

Updated 2026-11-08. A fresh-host ordinary HTTP replay passes once on both the
Wasm component and matched Node. The original comprehensive Wasm browser run
remains failed on strict POST7 response capture. This diagnostic establishes
completion for its own workload; it does not establish the cause of that abort.

| Observation | Wasm | Matched Node |
| --- | --- | --- |
| Original owner / deadline | 29465 / 600s | 29725 / 300s |
| Owner result | Exit0, clean | Exit0, clean |
| Response | HTTP200, gzip RSC | HTTP200, gzip RSC |
| Encoded bytes | 1,488 | 1,491 |
| Decoded bytes | 2,963 | 2,963 |
| End / HTTP complete | Both true | Both true |
| Aborted / collection errors | False / none | False / none |
| Gzip decode / CRC / ISIZE | All pass | All pass |

The request is the actual391-byte multipart POST retained from the failed browser
run. A unique local NetLog send-header record supplies all19 original headers;
the42-character action identifier matches the actual build manifest. The replay
removes the original public correlation header, rewrites Host/Origin/Referer for
the new listener, and preserves every other header and body byte. It negotiates
gzip. It neither follows redirects nor runs React or Chrome. There is no HTTP
warmup. Original wire identity and public-correlation joins are not claimed.

The application, native engine, component, observer envelope, selected13 standard
WASI0.2.10 interfaces and original host adapters stay unchanged. This introduces
no guest service or host modification. Fresh host state, prior workload and the
consumer all differ from the comprehensive browser sample. Encoded and decoded
payload hashes also differ between the two new responses; byte equality is not
the validation contract. Both contain the expected action result and value.

The client retains every observed encoded body byte before validation. Its
result, raw body and publication receipt are synced, closed and read back before
one terminal stdout record. Response EOF, complete retention of observed bytes,
known socket cleanup and semantic success are distinct checks. Normal Node gzip
validation and a separate Root Python DATA decode both pass; the final trailer
matches aggregate CRC/ISIZE. Neither check claims the gzip member count or
captures HTTP transfer framing. The original owner/source/world guards pass
before and after each arm.

Preparation initially failed before publishing a plan: the binder incorrectly
assumed default JSON formatting would reproduce compact inline arrays in its
input. Its failed source and partial preimages are retained. The correction
checks semantic inversion and preserved original bytes separately. Both actual
host slots then execute once, with no replacement trial.

Evidence and reusable checks live in the
[Root result packet](../../tests/node-compat/frameworks/nextjs/next-rsc-response-root-results-v1/README.md),
[client](../../tests/node-compat/frameworks/nextjs/next-rsc-response-client-v1/README.md)
and [runtime](../../tests/node-compat/frameworks/nextjs/next-rsc-response-runtime-v1/README.md).
The [persisted callback result](nextjs-persisted-callback-results.md) retains the
comprehensive failure. Next control the preceding HTTP/cache/supplemental/stream
workload while retaining this raw consumer, then investigate the browser response
lifetime with the original strict assertions. A fresh passing replay does not
justify a native compression, scheduling or cancellation patch.

For future checks, retain this case as a versioned request fixture. A new run
needs fresh output namespaces and before/final input checks; the declared slots
are single-use. A changed Next build needs a new action-manifest/body/header
binding rather than reusing an action identifier silently. Compare status,
completion, retained-byte counts, gzip validity and RSC markers. Preserve raw
failures and compare normalized application semantics separately from response
hashes, generated values or compression sizes. Run the comprehensive strict
browser suite as its own required gate.

The [primary DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-response-root-results-v1/actualreview.json)
(`0e74de45`) and [independent runtime/gzip review](../../tests/node-compat/frameworks/nextjs/next-rsc-response-root-results-v1/independent-runtime-gate-review.json)
(`e22f9f7a`) pass within their stated scopes. The
[retained raw corpus](../../tests/node-compat/frameworks/nextjs/next-rsc-response-root-results-v1/raw-records/index.json)
contains380 payloads/7,575,911 bytes, rehashed by Root. It includes exact returned
bodies, publication/terminal records and selected Source/provenance; large
application copies, SDKs and binaries are omitted explicitly.
