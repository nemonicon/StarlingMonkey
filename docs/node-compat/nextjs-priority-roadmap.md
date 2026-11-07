# Next.js execution priority

Updated 2026-11-07. The complete existing **Next 16.4.5 / React 19.3.1 App Router
application now passes the selected experimental Wasmtime smoke contract**:
24/24 HTTP checks, cache generation 1 → 2, five incremental Suspense chunks,
and both browser interactions, with zero recorded browser or observer errors.
A stock Node 22.14.0 control passes the same browser worker, readiness checks,
20-second test limits and error gates. See the
[current milestone](nextjs-wasm-milestone-2026-11-06.md). The portable
[native first/repeat review](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
and [matched Node review](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-stock-v1-review/README.md)
retain the actual observations and read-only checkers.

The accepted production checkpoint remains
[foundations-v13](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md).
The new result is an experimental profile, not production promotion or complete
Node/Buffer compatibility. Server JavaScript executes in SpiderMonkey inside
Wasm; the browser executes ordinary Next client JavaScript. This is neither
JavaScript AOT compilation nor a client-side Wasm port.

## Exact passing generation

The passing component is `55f05e3d…` (37,214,436 bytes), engine `4623640b…`
(31,324,051 bytes), and incremental metadata `726d69cf…`. The engine retains the
coherent patched Intl/SavedFrame V7 build and its 80 native compile rows plus
separate embedding as ancestry. One fresh UTF-16 Module translation unit and a
new archive/relink replace the failed non-ASCII `Function` workaround; this is
not a claim of 80 fresh frontend compilations. The
[build review](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-root-results-v1/actual-review/README.md)
records that distinction and the input protections.

The raw [guest entry](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs)
loads the unmodified standalone application from `/app`. Its six bounded guest
facades provide the Node global alias, cross-prototype Buffer input handling,
send's ReadStream options, AbortSignal-aware pipeTo, classic request-body
conversion, and AsyncResource construction/runInAsyncScope over native ALS
capture. Their limits remain part of the experimental contract. The entry
contains no `Function` compilation fallback or diagnostic app wrapper.

The final component imports exactly thirteen selected standard WASI interfaces,
all at **0.2.10**, and exports `wasi:http/incoming-handler@0.2.10`. The successful
host is stock **Wasmtime 42.0.1**, explicitly configured with instance reuse 128
and idle timeout 60 seconds, a physically read-only app tree and fresh writable nested
cache, and a declared loopback origin. No custom host service, host modification,
raw socket/TLS/DNS implementation or interface-version widening is involved.
The generic accepted foundations-v13 engine remains `d54446dc…`, sidecar
`bfaec95e…`, with 342 native policy inputs; repository HEAD is not its identity.

Other tool pins remain ComponentizeJS 0.23.0, Jco 1.40.0 and Rolldown 1.2.16.
The matched browser is Chrome 156.0.8078.81 with Playwright Core 1.64.1.
The second host target is wasmCloud 2.11.0, pinned source
`bc5acfb8e15f7d6d199ca940354d82e590c2d5ff`, embedding Wasmtime 48.0.7;
retain the [existing host setup](../../tests/node-compat/wasmcloud/README-host.md).

## Success contract and retained failures

Keep the original [fixture contract](../../tests/node-compat/frameworks/nextjs/fixture-contract.json):
23 base requests plus the build-derived Server Action POST, SSR/layouts,
headers/cookies, JSON/bad input, filesystem/SHA, public assets, cache reuse and
invalidation, hydration/counter click, browser action, and incremental Suspense.
The passing run retains all 24 HTTP responses, cache generations 1 and 2, shell
in chunk 0 and ready content in chunk 2 of five chunks, and nine decoded script
captures matching five unchanged source files plus one actual POST RSC body. Both real browser clicks
pass; no handler is invoked by the readiness observer.

The [hydration harness](../../tests/node-compat/frameworks/nextjs/browser-hydration-candidate-v1/README.md)
waits for load and the pinned React own-data handler binding before interaction.
It keeps the same count/action assertions, whole 20-second limits and strict
zero page/console/request/observer-error gates. The earlier V4 counter click
preceded script responses by about 2.15 seconds. Its timeout and action abort
remain failures; the later pass does not rewrite them or establish a unique
cause for every earlier abort. Browser decoded-body hashes and encoded byte
counts are retained; compressed wire hashes are not inferred from Playwright.

Earlier no-Intl failures, the 11/24 route baseline, the eval-provenance 0/23
prototype, and the native UTF-16 22/24 run remain in the
[runtime records](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1).
The original foundations-v13 bundler corpus and its expected failures remain
separate regression baselines. A React-only render or successful import never
substitutes for this application contract.

## Priorities after the first pass

| Priority | Work | Completion gate |
| --- | --- | --- |
| 1 | Make the passing generation reproducible | The [retained-artifact runner](../../tests/node-compat/frameworks/nextjs/run-native-next-regression.py) passes a fresh repeat. The [clean-machine dependency audit](nextjs-reproducibility-plan.md) locates committed sources and real build mechanisms; portable composition, external artifact/tool materialization, fresh inventories and an isolated app-build command remain open. Historical failures remain unchanged. |
| 2 | Regress response and compression semantics | The [twelve-case native-stream probe](../../tests/node-compat/frameworks/nextjs/native-pipe-root-results-v1/README.md) now matches all36 actual Node records in a real component, raw0/clean. It covers cancellation, abort, falsy errors, backpressure, final chunks and locks without expected-gap allowances. This validates the audited guest facade over native streams, not a new C++ pipeTo path or native resource-count/teardown proof. Broader cancellation/compression boundaries remain open. |
| 3 | Close context and disconnect boundaries | Five logical-branch controls pass459 native assertions and ordinary-call unref matches51+9 checks. The [isolated I/O-abort successor](../../tests/node-compat/frameworks/nextjs/peer-disconnect-root-results-v3/README.md) now passes eight real responses on two fresh hosts, both signal/error paths and same-factory JS inspections, raw0/clean. The original raw1 remains inconclusive. **Integrate this audited adapter change into the full Next entry and rerun24+2 next.** Native counts/teardown and broader AsyncResource remain open. |
| 4 | Run unchanged Next on the second host | **Eight cold requests now pass** on stock wasmCloud2.11.0/embedded Wasmtime48.0.7 with the same55f05 component: health×3, SSR, JSON POST, filesystem/SHA, asset and strict streaming. Config/dev/outer0 and input/ownership bookends pass. V2 waits for the pinned post-registration CLI marker; the earlier eight host404s/SIGINT130 remain failed evidence. This closes the finite cold contract, while retained cache/browser acceptance remains separate. |
| 5 | Make the successful profile buildable and measurable | Provide a clean-machine build path and execute the [paired measurement plan](nextjs-measurement-plan.md) for size, startup, public server RSS and route timing. That plan is unexecuted; functional success establishes no performance advantage or memory bound. |
| 6 | Prepare production promotion | Review exact selected manifests, defaults, build inputs, INIT barriers, facade limits and host rights; run required release and compatibility suites before profile/API promotion. Keep foundations-v13 accepted until this decision is explicit. |

## Per-surface depth

The full app pass demonstrates the paths it actually exercised. It does not
replace each surface's broader differential, lifetime and failure suite.

| Surface | Current experimental evidence | Remaining boundary |
| --- | --- | --- |
| CommonJS, VM and primitive util.format | Genuine Module/createRequire, JSON/cache/chunk loading and VM client-reference-manifest evaluation run in the successful app. Native UTF-16 compilation preserves real stack provenance. | Arbitrary packages, full Contextify/security sandbox, broad formatting and all Node loader semantics are unproved. |
| Buffer | Bounded native bytes/codecs plus an intrinsic-view entry facade satisfy the measured routes, POST and asset paths. | Complete Node Buffer overloads/prototypes/coercions, pooling and cross-realm parity are not claimed. |
| Filesystem | Actual physically read-only app/assets, static chunks, request FS/SHA route and writable nested cache work. ReadStream send options use a bounded facade. | General mount rights, recursive/path options, native resource cancellation/close and adversarial reuse need their own suites. |
| HTTP and WASI adapter | Real custom-server prepare/getRequestHandler, typed request-body EOF, native response streaming, actions and resource translation pass the selected full app contract. | General Node listen/TCP/TLS/HTTP2 behavior and exhaustive cancellation/ownership semantics are outside the pass. |
| AsyncLocalStorage and AsyncResource | Real native store/Promise queue/task/tick/fresh/neutral boundaries; dependency controls and actual Next request/action/static paths run. The bounded AsyncResource facade calls native ALS.snapshot. | Full hooks/IDs/lifecycle, cross-request concurrency, broader AsyncResource and named ESM binding parity remain open. |
| Startup, timers and performance | Required process/env/cwd, URL/OS, timers/immediates and performance paths are present in the linked profile and measured app. | Broad Node API coverage, phase/ref-unref edge cases, snapshot resumption and reset safety remain separate. |
| Native web and classic streams | The app's request conversion, response piping, gzip/static delivery and five-chunk Suspense path pass. | pipeTo facade disturbed-state/queued-close/private-state limits and signal pipeThrough remain explicit; native regression work is priority 2. |
| Crypto/compression | RuntimeOnly RNG, native SHA256, existing Hash/Hmac and streaming Gzip/Deflate are selected in the generation; demanded app paths execute. | This is not proof of all crypto operations, keys, compression formats or persistent-state cleanup. |
| Unicode and Error stacks | Patched Intl/ICU generation passes 36 strict Unicode records. Real native SavedFrames unblock send/depd. | Three anonymous function-name type differences keep the separate strict stack run failed; eval-origin/receiver/native/async methods remain deferred. |

The [startup/API inventory](../../tests/node-compat/frameworks/nextjs/startup-api-demand-v1/README.md)
retains 56 citations from 406 loaded JS files and nine pinned export inventories.
Static or conditional calls are demand evidence, not proof that every branch ran.
The [original bridge control](../../tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/README.md)
and [C deployment probe](../../tests/node-compat/host-capabilities/probe-v1/README.md)
remain distinct controls rather than substitutes for the successful Next guest.

## Lifecycle and host limits

Application loading is deployed-only. INIT installs snapshot-safe facades without
reading app files, deployed environment, entropy or request resources. The lazy
guest boundary prepares the logical server once under a neutral native resource,
then enters a fresh request owner before constructing the Web Request/body.
The successful sequential smoke run does not prove concurrent first-request
behavior, complete resource teardown or deployed re-snapshot/reset safety.

Keep the real custom-server prepare/getRequestHandler route. The host owns HTTP
transport; an HTTPS scheme is routing metadata, not a raw TLS implementation.
The app and browser source trees stay unchanged. App files/directories are
physically mode 0444/0555; the CLI mounts `APP::/app` and the separate cache.
These Unix-mode checks do not prove that the WASI preopen descriptor itself
has read-only capability rights. Optional APIs cannot be inferred from names
that happen to import or appear in the inventory.

The passing host configuration requires declared instance reuse. On pinned
wasmCloud 2.11.0 the normal **P2 HTTP** path creates a new store/instance per
request; pool size, max concurrency and reclaim settings govern a different P3
path and do not provide retained P2 state. The complete retained-server/cache
contract is therefore not accepted on that wasmCloud path. Report cold-request
results separately; do not widen the world or modify the host to force reuse.
See the [pinned lifetime analysis](../../tests/node-compat/host-capabilities/wasmcloud-warm-candidate-v1/README.md).

The experimental full-application smoke milestone has passed on the selected
Wasmtime configuration and its matched Node control. Reproducibility, deeper
per-surface/lifecycle regressions, production promotion and performance work
remain open.
