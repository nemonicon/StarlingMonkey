# Full Next observed-I/O entry V5: strict failure retained

The V5 constructor passed, but the first deployed full Next run remains
**raw1 / failed overall**. All24 HTTP contracts, cache generation1→2, five
incremental stream chunks (shell0, ready2), hydrated counter and browser Server
Action functional assertions pass. Strict browser acceptance fails on the
recorded action request and collector errors. No event is filtered or relabeled,
and no target was rerun by this review.

| Retained stage | Actual result |
| --- | --- |
| Construction/API capture/validate/WIT | Three inner raw0 and outer0, clean |
| HTTP/action/cache/stream client |24/24; cache1→2; stream5 chunks, complete/incremental |
| Browser function |2/2, no timeout; real hydrated click and form submit |
| Browser strict errors |0 page errors,0 console errors,1 failed request,2 collector errors |
| Runtime/client | Original parent1 and client1; failed/unaccepted states preserved |
| Wasmtime shutdown | Planned SIGINT→0, no forced cleanup; owned groups gone |
| Original inputs/world/app copy | Preserved; full-world guard before=after |

The136-event browser trace gives this bounded ordering:

1. Action response200/headers, then main-frame navigation (sequence122).
2. POST `/actions` `net::ERR_ABORTED` during `action-result-assert` (124).
3. `response.body` CDP `No data found … navigated away from` (125).
4. Functional completion and screenshot; explicit context close starts (131).
5. `response.finished` rejects `Target page, context or browser has been closed`
   during close (133).

The abort and unavailable body precede explicit context closure. That ordering
does not identify a cause or establish that any error is benign. All13 finished
observations, full trace, failed-request records and error messages remain in
the original JSON. Ten body-capture records exist: **nine decoded scripts**
match five pinned application files; the tenth POST capture has no decoded RSC
body and retains its body error. No complete RSC body, encoded-wire hash or
cross-host RSC equality is invented. Both actual PNG screenshots are retained.
Server stdout is165 bytes of five ordinary `Running next.config` timing lines;
stderr is the complete40-byte listener line. No diagnostic error was added to
the guest entry by this experiment.

The exact chain is Source `73b583be…`, raw entry `1e49ddc6…`, constructor
`cc411d38…`, constructor result `3831a5aa…`, component
`1c3108d2fdce72a1bfa8cc64a0e6e0645acd71223b26b6dc11d037d4a95efe83`
(37,214,251 bytes), runtime result `8fa934ee…`, runtime Root `8c83d2fc…` and
outer terminal `5ee31c4c…`. The complete API own-property graph/import tuples,
three raw constructor records, raw WIT and byte descriptors are retained. The
component emits exactly13 selected standard WASI0.2.10 interfaces and only the
resource-based incoming-handler export. Root's constructor and runtime receipts
both bind the complete802595 world family:28 payloads/eight WIT files/exact
directories/no aliases, with before=after and native inputs preserved.

The engine remains `4623640b…`; genuine `726d69cf…` metadata records one fresh
UTF16 Module frontend,79 reused baseline rows,80-row ancestry and the retained
separate embedding. All issued fixed fields and roles agree. This is a guest
entry policy experiment, not another native build. The previous successful
component55f05 and matched Node results remain separate unchanged evidence.
The isolated peer diagnostic's pass is also not a full-Next browser pass.

`data.tar.gz` contains195 exact finite records (3,325,194 expanded bytes,
656,760 bytes compressed): full constructor/runtime raw logs and monitors,
Root authorities/callers, actual metadata, four Source/world families, relevant
facade sources, the request contract/app inventory, all response bodies,
base64 stream chunks, browser trace/body records and both PNGs. It excludes
application trees, components, engines, SDKs, caches, archives and recursive
build ancestry. Current original/copy app readbacks matched all2218 files /
48,808,299 bytes before/final; copies have distinct single-link inodes,
physical0444 files and0555 directories. These modes do not prove read-only
WASI preopen rights. Runtime uses stock Wasmtime42.0.1, reuse128/idle60,
explicit loopback origin and a fresh writable nested cache.

Run the inert portable DATA reader from any complete copy:

```sh
python3 -B -I check.py
```

It verifies retained hashes/membership, issued roles, complete API/WIT graph,
original process records, independent HTTP/action/cache/chunk semantics,
browser bodies/PNG hashes, timeline categories and the still-failed strict
outcome. It runs no project JS, browser, server, oracle, compiler or guest.
Current readbacks are finite observations, not all-time filesystem attestation.

Reviewer C authored earlier ALS, constructor tooling and the signal-aware pipe
facade; this separate actual-data reader is not independent authorship of those
Sources. No clean-machine build, native disposal count, physical Store identity,
snapshot/reset safety, performance, adoption or full Next acceptance follows
from a successful evidence reader.
