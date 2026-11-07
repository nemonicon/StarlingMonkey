# First real concurrent Next.js request regression

The NativeV8/StockV6 pair is **not accepted**. Both original process owners exit
1 with clean cleanup and preserved inputs. Both supplemental captures pass all
80 checks for the six new cases, but the original full-contract gates fail.
Earlier passing runs and the failed reliability cohort retain their own scopes.

| Check | Native Wasm | Matched Node |
| --- | --- | --- |
| Six context/body/recovery cases | 80 checks pass | 80 checks pass |
| Individual HTTP contracts | 24/24 pass | 24/24 pass |
| Cache generation after revalidation | 1→1, **fail** | 1→2, pass |
| Incremental stream | Five chunks, shell0/ready2 | Five chunks, shell0/ready2 |
| Browser counter/action interactions | 2/2 functional pass | 2/2 functional pass |
| Strict browser gate | **Fail**, action POST `ERR_ABORTED` | **Fail**, action POST `ERR_ABORTED` |
| Whole original contract / pair | **Fail** | **Fail** |

The cases exercise two distinct cookies/headers, a controlled Unicode JSON
upload split inside the UTF-8 encoding of `€`, malformed JSON, then empty-context
and valid-JSON recovery. All six deterministic status/JSON responses match across
arms, with EOF and no request/reader/publication errors. The first four requests
overlap at the client; the upload tail is held until the other three terminate.
This does not identify a guest read boundary, Store, JS heap or native resource.

The native component remains `1c3108d2…`, engine `4623640b…`, metadata `726d69cf…`.
The genuine 2,181-file app and all thirteen selected standard WASI0.2.10 imports
remain unchanged. No new engine, host capability, application rewrite or
production promotion is established by this pair.

## Cache finding and deployment boundary

The fixture's [cache callback](../../tests/node-compat/frameworks/nextjs/app-fixture/app/api/cache/route.js)
increments a module-local `misses` variable. Both arms return successful tag
revalidation responses, but only stock returns generation2 afterward. Both
persist the same FETCH key/tag; native's final cached payload contains1 and
stock's contains2. The records do not identify the instance serving each request
or whether native's final response was a cache hit or a new callback returning1.

In the pinned Next implementation, `FileSystemCache.revalidateTag` modifies
`tagsManifest`, a module-local Map created by `tags-manifest.external.js`.
FETCH `set` persists values and tag names, but does not persist the invalidation
epochs from that Map. A common filesystem therefore does not itself share the
default tag-invalidation state across JS instances. These source findings come
from the actual standalone Next files inspected in both runs; their selected
module snapshots and result descriptors are retained in the evidence below.

The pinned stock host has a corresponding execution boundary. Wasmtime42.0.1
forces P2 concurrent reuse per instance to1. Its shared handler creates another
worker/Store when no worker is available; later requests have no application
affinity key. Reuse-count128 and idle60 preserve idle workers without promising
one JS heap. Allocator capacity limits return errors rather than serializing
requests onto a busy P2 instance. See the pinned
[serve implementation](https://github.com/bytecodealliance/wasmtime/blob/v42.0.1/src/commands/serve.rs#L464-L486),
[worker selection](https://github.com/bytecodealliance/wasmtime/blob/v42.0.1/crates/wasi-http/src/handler.rs#L533-L565),
and [allocator limit](https://github.com/bytecodealliance/wasmtime/blob/v42.0.1/crates/wasmtime/src/runtime/vm/instance/allocator/pooling.rs#L592-L602).

This establishes a source-based risk and a limit on process-global compatibility,
not a proven cause of this specific native failure. The generation gate remains
failed. Next's real `nextConfig.cacheHandler` seam could support a separately
reviewed guest filesystem handler for shared tag/data coherence using existing
standard preopens. It requires correct atomic publication, synchronization and
memory-hit invalidation. It cannot turn an unchanged lexical callback counter
into a global counter across independent heaps. No such handler or same-instance
execution profile has been implemented or validated here.

## Browser failure

Both browsers observe a successful action response/navigation and functional
result markers, then retain an aborted action fetch and unavailable response
body/sizes. Native's recorded cancellation precedes explicit context-close by
about72ms in the same-process event clock. That excludes a later explicit close
as the earlier event; it does not establish an abort cause. CDP received data
events without `loadingFinished`, so those bytes do not prove EOF or a complete
compressed response. Missing bodies remain null; no synthetic body is supplied.

The matched Node failure means the symptom is not unique to the Wasm arm. It
does not prove an instrumentation, browser, bridge, application or runtime cause.
The prepared additional-CDP-session-off diagnostic remains a separate controlled
investigation. Every old strict gate and failed record remains intact.

## Retained evidence and future checks

The [failed-pair results](../../tests/node-compat/frameworks/nextjs/next-app-request-isolation-root-results-v1/first-real-pair-results/README.md)
retain347 unique DATA files (6,250,410 logical bytes), including original owner
records, both nonapp output trees, all physical supplemental publications,
browser/HTTP/stream captures, stock cache artifacts and finite source witnesses.
All archive members independently hash-match the indexed original bytes.
Application/engine/tool binaries and recursive historical closure are excluded.
The archive is DATA, not a replacement live input tree or execution attestation.

The existing V3 reader returns capture-integrity0/80 supplemental checks for
each arm, then pair-mode1 at native original acceptance. Root's independent
readback also verifies all six deterministic responses match while retaining
`strictPairAccepted:false`. No target run is repeated or filtered. Use the same
preserved Source commands with fresh run IDs for a future changed generation;
passing six supplemental cases cannot admit a failed original contract.

Outstanding work is to finish and verify the full native rebuild, investigate
browser reliability, resolve the process/cache deployment contract without
custom host services or host changes, and rerun the complete application gates.
