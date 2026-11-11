# Next.js V4 full-workload results

Updated 2026-11-11. One fixed stock wasmCloud 2.11.0 run and its matched bridged
Node run both pass the unchanged comprehensive client, strict browser tests and
CDP resource-completion checks. This is a successful bounded sample on the
filesystem-callback, compression-off application. `fullNextAccepted` remains
false; lifecycle, repeatability and production acceptance are still open.

The [primary review](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v2/actual-runtime-review.json)
(`791317fe…`) records these results:

| Check | Stock wasmCloud | Matched Node |
| --- | --- | --- |
| Original owner / deadline / raw exit | 32470 / 600s / 0 | 33103 / 300s / 0 |
| HTTP requests | 24/24 pass | 24/24 pass |
| Portable-cache cases/checks; supplemental cases/checks | 5/52; 6/80 pass | 5/52; 6/80 pass |
| Persisted callback generation | 1→2 | 1→2 |
| Application stream chunks / shell / ready | 3 / 0 / 1 | 3 / 0 / 1 |
| Stream complete / incremental | True / true | True / true |
| Functional UI / client + action script sets | 2 tests / 5 + 4 pass | 2 tests / 5 + 4 pass |
| Original strict browser / full client | Pass / pass | Pass / pass |
| Page / console / failed-request / capture errors | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Server Action POST status | 200 | 200 |
| Response Content-Encoding / Transfer-Encoding | Absent / chunked | Absent / chunked |
| Playwright body / sizes / finished | Fulfilled / fulfilled / fulfilled | Fulfilled / fulfilled / fulfilled |
| Decoded POST body / reported response-body size | 2,963 / 3,001 bytes | 2,963 / 2,976 bytes |
| CDP command / buffered prefix | Fulfilled / 0 bytes | Fulfilled / 0 bytes |
| CDP binary payload pieces / retained bytes | 2 / 2,963 | 1 / 2,963 |
| CDP terminal / complete resource | loadingFinished / true | loadingFinished / true |
| Full original contract executed / clean owner / inputs preserved | True / true / true | True / true / true |

Chunk counts are observations, not fixed acceptance thresholds. Both physical
callback namespaces contain only the canonical 35-byte generation-2 record and
no pending file. The cloud namespace is in its independent writable cache;
Node's is under `application/.next/cache`. This persisted state does not prove
same-Store or same native-resource identity.

The selected fresh multipart POSTs are each 391 bytes, with different boundaries
and SHA256 values (`bf44b172…` cloud, `2749191d…` Node). Their three semantic
parts, manifest-selected action, public context and Playwright/CDP body evidence
match. The retained resource hashes are `819d8fd0…` and `143660f7…`; equal lengths
do not imply equal bodies. CDP resource bytes and Playwright decoded entity
bytes are distinct from wire framing, and reported encoded sizes are not wire
body hashes. No Flight-parser, React-reader EOF or private request-identity
conclusion follows.

The pinned profile uses Next 16.4.5, React/React DOM 19.3.1, Node 22.14.0,
Playwright 1.64.1 and Chrome **157.0.8103.39**. Application review `9106545f…`
selects the existing `compress:false` filesystem-callback app. Engine `237c4e5a…`
and Next inner component `6b2084d0…` are unchanged. The separately validated
V4 envelope `9da63790…` contains that exact inner and observer `3534089e…`.
The [composition review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-next-v4-composition-review.json)
(`730c2698…`) preserves shared nominal resources, sibling defining instances and
the inner handler's canonical post-return.

The external surface is exactly 13 WASI 0.2.10 imports: `wasi:io/error`,
`wasi:io/poll`, `wasi:io/streams`, `wasi:clocks/monotonic-clock`,
`wasi:clocks/wall-clock`, `wasi:http/types`, `wasi:http/outgoing-handler`,
`wasi:cli/stdout`, `wasi:cli/stderr`, `wasi:cli/environment`, `wasi:random/random`,
`wasi:filesystem/types` and `wasi:filesystem/preopens`. The sole export remains
`wasi:http/incoming-handler@0.2.10`. No engine, Node bridge, host capability or
standard interface was changed for this result.

Cloud retained two independent mounts, three guest environment entries,
self-origin-only egress, configuration inspection before one dev process,
post-registration plus TCP readiness and zero HTTP warmups. Its stdout captures
completed and the host stopped normally with SIGINT/exit 0. Both original owners
and browsers closed cleanly; before/final input guards passed. The
[binding DATA peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v2/binding-data-peer-v2.json)
checks the fresh 2,199-reference union and the added constructor dependencies.

The first V4 attempt is preserved separately: original owner **30991** exited 1
cleanly before output creation or host launch because the historically pinned
constructor adapter was missing. Root restored the exact 49,672-byte artifact,
requiring its original `d30ade5b…` hash, then checked all 54 constructor artifact
references. The [restoration/preflight record](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v1/construction-artifact-preflight.json)
(`7213123a…`) and V1 failure remain intact. V2 uses fresh `-second` run IDs and
`v2` output prefixes. The earlier Source/binding review is qualified: it proved
the declared union but missed this transitive actor dependency. V2 checks that
complete constructor/audit-terminal/log set before issuing an owner.

V4's outer public-tuple analyzer admits one observed `POST /actions` witness:
51 ordinary rows contain one target, 47 proved present-other rows and three
distinct known rows, with no malformed or blocking observed row. The
[analyzer command](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v2/public-tuple-command.json)
(`ff50bc8e…`) nevertheless exits **1**: outcome coverage is explicitly
`observed-only`, so `prospectivePublicTupleJoinAdmitted` is false. Complete
stdout cannot universally exclude a silent getter/trap/producer failure. The
named witness does not prove a global or physical end-to-end join.

Historical Chrome **156** strict failures remain failed, including the canceled
cloud resource prefix in the [previous full sample](nextjs-resource-stream-results.md).
This pair changes both observer metadata policy and browser version. It supplies
no engine-fix, cancellation-cause or reliability proof, and does not repair the
old module-global callback contract. The new observer evidence never enters or
waives the original strict predicate.

The next priorities, in order, are:

1. **Request isolation and lifecycle/reuse:** verify sequential and overlapping
   requests, normal and aborted bodies, child-resource retirement, late callbacks
   and safe reuse. Check cross-request state explicitly; public tuples and the
   filesystem counter do not establish resource identity or retirement.
2. **Repeatability:** predeclare multiple fresh cloud/Node slots with the same
   pinned app, tools, workload and strict gates. Retain every failed slot and
   capture; do not replace failures or infer a failure rate from this one pair.
3. **Clean-machine reproduction:** rebuild from pinned inputs, verify tool and
   adapter availability before owners, preserve absent source caches and
   independent writable runtime caches, and replay the retained-data checks.
4. **Cost:** after correctness is repeatable, measure startup, steady requests,
   memory and teardown separately from compilation, app copying and browser/CDP
   observation overhead. The 600/300-second caps are not performance results.
5. **Promotion:** decide production/default-profile adoption only after those
   gates and the remaining compatibility requirements pass. Keep current
   `fullNextAccepted:false` and all prior failures in that decision record.

The reusable saved-record check passes against the frozen 270-file,
7,987,845-byte packet (index `d588c81e…`):

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v2/review-runtime.py --retained
```

It recomputes the original review exactly, reads only repository copies and
launches no targets. Optimized Python is explicitly refused before file reads.
The checker also passes from an isolated 273-file copy of actual staged Git
blobs, with identical output. At that cut all 505 staged files matched the
worktree byte for byte.
The [independent runtime review](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-v4-root-results-v2/independent-runtime-gate-review.json)
(`8595fd75…`) also verifies the full assertions, physical callback files and
actual CDP payload reconstruction. The public-tuple peer (`a82bfea9…`) retains
the observed-only limit. C drafted this note from closed data; Root executed the
runtime and retained-data checks. Clean-machine runtime reproduction is still
open.
