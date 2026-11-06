# Independent HTTP bridge host review

The four retained attempts support the documented **Node-host** results. This review does not accept a Next Wasm component or guest HTTP implementation. The reviewer authored the proposed native ALS fresh-request seam, but did not author this HTTP bridge or operate these four attempts.

| Retained attempt | Actual process | HTTP | Browser | Other actual observations |
| --- | --- | --- | --- | --- |
| `next-http-bridge-v1` | raw1, owned groups clean | 0/22 observed | Not reached | Original request-header/implicit-header failures and final timeout retained. |
| `next-http-bridge-v2` | raw0, owned groups clean | 24/24 | Not run | Cache generation1→2; five chunks, shell0 and ready2. |
| `next-http-bridge-v3-browser` | raw0, owned groups clean | 24/24 | 2/2, error-free | Actual hydrated click and form POST; same cache/stream observations. |
| `next-http-bridge-module-v1` | raw0, owned groups clean | 24/24 | 2/2, error-free | Candidate Module core compiled406 distinct files and cached412 modules; candidate Module identity true. |

`review.json` records exact source, summary, result and terminal descriptors. The independent read-only reader verified all155 copied files/474,769 bytes, closed capsule membership, fixed four-attempt coverage, exact HTTP ID sets, whole stdout summaries, raw exit/cleanup fields, browser record equality, stream bytes/markers, source snapshot joins and Module observations. The existing evidence checker separately validated contract response bodies, hashes, headers, derived action, cache and browser semantics. `command-receipts.json` preserves actual commands and tool observation IDs: bridge unit21 and mock WASI ownership unit13 passed; both retained-data checks passed before and after Root hardened the checker. No application, browser, compiler or guest was started by this review.

The original checker trusted the summary to select coverage and expected raw exits. Root corrected that unsealed source during this review. The final checker now fixes the known three-run or one-module plan, HTTP/browser counts, pinned versions and raw1/0 outcomes. The two final checks passed against unchanged evidence. Its new negative-test source covers empty/missing plans, a disabled browser gate and relabeling the failed first attempt; Root ran those cases, while this review inspected their source. This review independently fixes the four expected attempts and verifies exact capsule membership as additional boundaries.

One runner limitation remains: its top-level `passed` expression requires complete stream content but does not require `incrementalDeliveryObserved`. A future collapsed delivery could therefore pass that expression. The retained checker additionally requires ready to appear after shell, and this review independently observed shell0/ready2 in all three actual successful runs. Thus this is a future runner acceptance limitation, not a failure of these retained streaming observations. A separate read-only reviewer confirmed the prepare/fresh-root/TLS source joins and identified this limitation; that lane ran no commands or workloads and wrote no files.

The Module provider uses real host `readFileSync`, `statSync`, `realpathSync`, `vm.compileFunction` and Node builtins/globals. Its results establish a host loading control, not guest IO, native compilation or builtin admission. The recorded `applicationModified:false` is consistent with fresh recursive source copying and the harness flow; only `server.js` receives a direct copy-hash check in that flow. The capsules omit the large application/dependency trees, so this is not independent byte attestation of every file in the53MiB copy. The known candidate Module generator inventory-dependency gap remains documented.

`profile.wit`, `wasi-adapter.mjs` and `guest-smoke.mjs` remain uncompiled proposals. The13 ownership tests use fake resources; they do not establish real WIT lowering, own-resource transfer, stream disposal/backpressure or native resource lifetime. The proposed world names HTTP types/handler, streams, errors, poll and clocks at0.2.10; no emitted component/import graph exists here. The virtual transport's `encrypted` property reflects the incoming URL scheme. It does not implement TLS sockets.

The current bridge has **no native `runFreshRequest` wiring**. Actual host controls use Node's own ALS and call `app.prepare()` before admitting HTTP. A future guest must prepare the application once under a neutral server resource, keeping global readiness promises/cache infrastructure outside the first request. It then needs the real native fresh-request boundary before request-body stream construction, with that resource preserved across the handler's await continuations. A private factory binding or actual export-entry boundary must supply it; an identity fallback or added public `async_hooks` name is not evidence. The proposed native ALS candidate is uncompiled WIP and its queue, lifecycle and propagation requirements remain open.

No guest runtime, TLS, native ALS propagation, stock-host HTTP resource compatibility, snapshot/resumption, full Next compatibility or deployment/adoption claim follows from this host control. All existing Wasm failures remain separate.

To repeat the independent DATA inspection without executing the application:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/http-bridge-independent-review-v1/review.py
```
