# Passing full Next profile with dynamic compression disabled

Updated 2026-11-08. The reviewed Next16.4.5 fixture passes the unchanged full
contract once on both the Wasm component and matched Node22.14.0. This profile
uses explicit filesystem-backed callback state and Next's compress:false option.
The original compression-enabled browser failure remains a failing regression.

| Check | Wasm | Matched Node |
| --- | --- | --- |
| Original owner / deadline | 40483 / 600s | 40694 / 300s |
| Original owner outcome | Exit0, clean | Exit0, clean |
| Fixture HTTP cases | 24/24 | 24/24 |
| Portable cache / supplemental checks | 52 / 80 pass | 52 / 80 pass |
| Callback generation | 1→2 | 1→2 |
| Incremental stream chunks / shell / ready | 3 / 0 / 1 | 3 / 0 / 1 |
| Strict counter / Server Action browser tests | Both pass | Both pass |
| Page / console / failed-request / capture errors | All zero | All zero |
| Redirect action POST | HTTP200, RSC | HTTP200, RSC |
| Decoded POST response | 2,963 bytes | 2,963 bytes |
| Body / finished / sizes completion | All fulfilled | All fulfilled |
| POST Content-Encoding header | Absent | Absent |

The original browser worker01ca is byte identical, including body/finished/sizes
observers, deadlines, close/drain logic, asset assertions and strict zero-error
predicate. The full client changes only names, output policies and the browser
family path. All24 HTTP, generation, incremental-stream, portable-cache,
supplemental and browser conjunctions remain unchanged. The actual stream has
three chunks; the original contract requires shell before ready and complete
markers, not a fixed count of five.

The build changes only19 fixture bytes to add compress:false. The other34 files,
cache tracing exclusion, native engine237c, inner component6b20 and served
observer envelopee4c7 remain unchanged. Actual new HTML supplies five client and
four actions script pins. Binding37db0289 derives2,041 fresh protected inputs,
including all six external client consumers, eight WIT files, six host-tool rows,
actual HTML/scripts and standalone config/server files. Both declared slots run
once, in order; preparation340af5c4 allows no replacement trial.

The Server Action uses the new build's actual action identifier. Its response
has no Content-Encoding header in both observed header lists, and the browser
captures the full decoded body and completion. Playwright reports response body
sizes of3,001 bytes on Wasm and2,976 on Node. These are retained API observations;
they are not raw-wire hashes or a claim that transfer counts equal decoded
entity size. Payload hashes differ. Both UI tests finish with normal browser
closure. Native stdout is completely retained:28,755 bytes/104 chunks, followed
by normal SIGINT shutdown with host exit0.

The component continues to select and emit13 standard WASI0.2.10 interfaces:
cli environment/stdout/stderr; monotonic/wall clocks; random; filesystem
types/preopens; io error/poll/streams; HTTP types/outgoing-handler. Its selected
export remains wasi:http/incoming-handler@0.2.10. No host modification or custom
guest service is introduced. This test does not add sockets or TLS support.

This is one passing application-profile sample. It does not establish reliability,
identify the cause of the compressed abort, preserve arbitrary JavaScript globals,
prove same-Store ALS interleaving or promote the experimental engine to production.
The accepted production checkpoint remains foundations-v13; general Node and
complete Buffer compatibility remain outside this result.

Evidence is in the [Root packet](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/README.md).
The [build/profile report](nextjs-compression-off-profile.md) and
[failed compressed comparison](nextjs-persisted-callback-results.md) retain the
configuration and counterexample. Next run this same full application profile
on stock wasmCloud2.11 with fresh bindings and the same standard interfaces,
then complete the separate lifecycle, resource, reproduction, cost and promotion
gates. Full Next acceptance remains false.

The [independent full-gate review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/independent-full-gate-review.json)
(`d6ab47a6`) recomputes all final conjunctions and checks47 finite files, both
browser publications, all11 body captures per arm, the actual three-chunk stream,
NetLog publication and cleanup. The [binding review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/independent-runtime-binding-review.json)
(`e68db3bd`) reconstructs the2,041-input union and all preserved inverses.

The [primary full-contract review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/actual-runtime-review.json)
(`e19aaa2d`) verifies both full contracts, all14 finished observations per arm,
both canonical35-byte generation2 records with no pending file, complete native
stdout, normal shutdown and preserved inputs. The [raw corpus](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/runtime-records/index.json)
(`55487d02`) retains257 payloads/9,536,752 bytes, rehashed by Root. It retains
browser bodies/screenshots/NetLog, owner records, Source and selected provenance;
app/cache bulk and binaries are explicitly omitted. Whole app/native proofs
remain delegated to their current guarded build evidence.

The subsequent [stock wasmCloud trial](nextjs-compression-off-wasmcloud-results.md)
retains a strict POST7 abort with no Content-Encoding header, while all other
gates pass. This counterexample prevents interpreting these two positive samples
as a cross-host completion guarantee or a compression fix.
