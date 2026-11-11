# Fixed disconnect and recovery probe — Source only

`run-client.mjs ORIGIN FRESH_CLIENT_OUTPUT UNUSED_BROWSER_TOOLS RUN_ID` uses the pinned Node22.14.0 HTTP client. The reserved tools argument is never opened. The three exact Wasmtime/cloud/stock output policies are in `plan.json`; Root supplies the admitted server and owns every execution. No app, engine, host, browser or service is changed by this packet.

Three warmup cycles and sixteen measured cycles each make six sequential requests, for exactly114 planned calls:

1. Complete `/stream`, checking SHELL before READY and recording whether they arrived in different client body events.
2. `/stream`, invoking local request destruction after the first actual nonempty IncomingMessage Buffer.
3. Malformed `{bad` POST `/api/json`, expecting400 and `NEXT_JSON_BAD_INPUT`.
4. `/api/context` with the cycle's frozen distinct `alpha-NNN` cookie and `probe-value-NNN` header.
5. The same context route with no cookie/probe headers, expecting both values null.
6. `/api/fs-crypto`, checking the unchanged fixture's exact marker, text and SHA256.

The controlled context inputs differ from the original fixture's literal `alpha`/`probe-value` case. All19 values and phases are frozen in the plan. Serial set→empty checks observable recovery; it does not establish concurrent ALS isolation. `agent:false` creates an owned socket for each call, with no cookie jar or connection/instance/Store reuse claim. The fixture's existing30ms Suspense delay is not a new sleep or performance threshold.

Normal success requires IncomingMessage `complete`, consumer `end`/`readableEnded`, request finish, no transport errors, and the exact observed Content-Length byte count when present. `node:http` supplies entity bytes after transfer framing; there is no content decoder. Content-Encoding presence is a semantic failure. A locally requested socket close after consumer EOF is not described as peer TCP FIN; the separate `socketEndObserved` flag records an actual socket end if received. These boundaries follow the pinned [message.complete](https://nodejs.org/download/release/v22.14.0/docs/api/http.html#messagecomplete) and [request.destroy](https://nodejs.org/download/release/v22.14.0/docs/api/http.html#requestdestroyerror) documentation.

The intentional call records complete/readableEnded/end both at the local first-Buffer intent and at final close. It never passes as a normal completed body. If the response was already parsed at intent, the local boundary is still recorded and peer truncation remains inconclusive. No particular reset/abort event is required. Actual errors before intent or unrelated error codes fail its semantics; recognized post-intent reset errors remain visible. No guest cancellation, resource retirement, socket-to-guest identity or harmlessness is inferred.

Each call has a20s absolute request bound,2s cleanup bound,4MiB body bound,65536 chunk ceiling and256KiB chunk metadata ceiling. A fixed180s total client budget can leave an explicit unattempted suffix. Known fully retained and cleanly closed HTTP/protocol/semantic failures continue the fixed schedule. Unknown closure/publication, capture overflow/unretained data or total-budget expiry stops it. There are no retries, adaptive counts or backoff sleeps.

Each body and call JSON is written exclusively, fsynced, closed and read back before its descriptor enters the final result. `bodyPublication.complete` means all body bytes observed by this client were saved, not that HTTP completed. The durable final `result.json` precedes `publication.json`; one stdout JSON summary follows both. Top `probeExecuted`, `collectionComplete`, `cleanupComplete` and `passed` are distinct. `controlOnly:true`, `fullOriginalContractExecuted:false` and `fullNextAccepted:false` remain fixed even on a successful sample. The old full-suite failures and all existing Sources are untouched.

`test-real-http.mjs FRESH_OUTPUT` is a separate six-case real loopback protocol control for Root to execute before deployment. It exercises complete Content-Length, complete chunked framing, underlength Content-Length, overflow, a never-body deadline and first-body local close. It runs no guest and makes no guest resource claim. The production module is inert on import; the tests call that exact module with real Node sockets and reduced test-only deadlines/one reduced body cap. No tests or target executions were performed by the Source author.
