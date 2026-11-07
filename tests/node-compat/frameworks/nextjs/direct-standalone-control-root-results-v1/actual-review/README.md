# Direct standalone control — one actual PASS

The separately authorized first control passed all **24 HTTP contracts**, cache generation **1→2**, five incremental stream chunks (shell at 0, ready at 2), and **both strict browser tests**. Browser errors, failed requests, page errors and console errors are empty. The Browser V3 worker and all five fresh-app asset pins match; nine JavaScript captures, the action response body, two PNGs and all 83 CDP events are retained losslessly.

The server invocation was bare pinned Node 22.14.0 plus the independent owned copy of the generated `server.js`. Both that entry and Next's `start-server.js` retain their original hashes. Recorded argv and the Source-controlled environment exclude Module providers, the HTTP bridge, preloads, NODE_OPTIONS/NODE_PATH, manual signal handling and an IPC channel. These launch facts are Source-coupled process evidence; the observed server changes its process title to Next. No guest, SpiderMonkey engine or component was invoked.

The original0af controller had a 600 s cap and returned **0**, with both observed process groups gone and no timeout, forced cleanup, errors or monitor signals. After the client completed, the controller deliberately sent the server SIGINT; Next returned its expected code **130**, with no exit signal, error or forced cleanup. That server result is distinct from the controller's clean zero. Admission recorded **1,286,488,064 bytes**, above 1 GiB, without a continuous disk-floor or peak claim.

Readiness required the exact leased loopback Local URL and one TCP connection, without an extra HTTP request or port fallback. The Local log does not prove application handlers were initialized. The pinned Next request path waits for its handlers promise; the actual contracts then exercised it.

The source inventory is the genuine fresh build: **2,181 files / 48,714,867 bytes / 425 descendant directories**, plus its separately pinned root. The initial owned copy was checked for exact membership, source modes and independent root/file inodes. Current DATA checks match all original source identities and all recorded final copy hashes/modes/identities. The runtime copy contains **2,218 files / 455 directories including root**, with 37 additional owned fetch/route-cache files; it is writable and is not a wholly immutable tree. The final inventory is retained as hashes and identities, without copying those cache or application payloads. Physical modes are not a WASI descriptor-rights claim.

The compressed evidence includes the complete authority/CLI streams, original monitor records, full controller/client/browser results, response and stream bodies, screenshots, traces, active Source families, fresh app inventories/build records, and a bounded reference to the earlier cohort. It excludes application and tool trees, engine/binary/archive files and raw generated encryption keys. The actual key value was checked absent without printing it. A final finite hash check binds all captured originals. The portable reader imports no retained code, requires no private originals, and launches no tools or workloads:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/direct-standalone-control-root-results-v1/actual-review/check.py
```

This is **one new, separate positive sample**, not a replacement or retry of p3-stock. The fixed six-member cohort remains strict **5/6**, with p3-stock `ERR_ABORTED` and the earlier V5 failure unresolved. No abort cause, general reliability, guest parity, native counts, teardown/Store identity, GC/reset/fault, performance or promotion follows.

C authored the direct Source, B independently reviewed Source/grant and the completed monitor lane, and Root executed the control. R authored native substrate and curated earlier cohort evidence but did not author this direct controller. This review performed only DATA reads, hashing and evidence retention; it executed no actor or retry.
