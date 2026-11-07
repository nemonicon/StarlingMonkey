# Next.js execution priority

Updated 2026-11-07. The current critical path is the remaining request-state
and Server Action response-completion gaps. Bounded Fetch cleanup compiles and
passes its public tests; the fresh full Next.js run still fails both gates.
Engine476b1c1d/metadata22f1d456, componentd990ecc1 and runtime result2fb8d5fd
pass all five persistent-cache requests/52 checks,24 HTTP cases,80 supplemental
checks, five stream chunks and both functional browser interactions. Legacy
generation stays1→1 and strict POST7 capture retains three ERR_ABORTED errors.
The first prefix-mismatched harness attempt remains a separate pre-HTTP failure.
The following earlier2251/4e results remain as a separate baseline.
The optional persistent cache profile works on that corrected native loader.
Engine2251/metadataafb pass full-build
DATA review; component08ce passes construction review and all16 declared
CJS/fileURL cases in one real Wasmtime GET (runtime review030fad8b). The new
real-Next component4e and31-file standalone build are verified. Its first Wasm
application trial passes all five nonce checks,24HTTP,80 supplemental and
streaming checks, but still fails legacy cache1→1 and strict Server Action
response capture. The first matched Node control's VM loader gap is corrected
in a separate verified version: its new control passes every declared gate in
one sample. The failed Wasm full trial remains unaccepted. See
[current cache results](nextjs-portable-cache-2026-11-07.md).

Next actions, in dependency order:

1. **Completed:** compose and compile the reviewed six-file native Fetch cleanup source.
   Task retirement remains separate from terminal body cleanup; lazy metadata
   remains usable and native append is explicitly excluded. The source passes
   98 pure ownership-model checks. Two actual frontend checks pass; the third
   fails three ignored nodiscard results. The separate18-byte correction passes
   all three fresh frontend checks with independent DATA review. The full
   native build now exits0 with coordinated DATA review. A fresh interop
   component passes all16 deployed cases (review55a255e7); a separate public
   Fetch component passes INIT review4b3b0f43 with the complete actual import
   audit. Its eight public groups now pass the real Node/Wasm comparison,
   raw0/clean/protected, with coordinated DATA review705270ee. A fresh real-Next
   componentd990ecc1 also constructs/validates successfully; its completed full
   application regression retains the two failures above.
   See the [bounded cleanup plan](nextjs-fetch-resource-cleanup-2026-11-07.md).
2. **Completed public scope:** eight Fetch lifecycle groups/eleven requests per
   Node and guest arm pass. The corrected full application suite then executes
   and preserves the two failures above; coordinated DATA reviewc3a8b95b
   verifies that failed trial. Durable raw records belong to these separate runs.
3. **Next implementation priority:** inspect the pinned Next/React Server Action
   consumer and guest outgoing-stream/compression/finish boundaries. Use the
   retained POST7 trace to choose a concrete completion invariant and targeted
   test before changing native code. Keep the strict browser assertions.
   The [client audit](nextjs-server-action-next-steps.md) and
   [response-path audit](nextjs-response-completion-next-steps.md) now identify
   those boundaries; a normal-input gzip/backpressure probe is the next proposed
   test. Declared React19.3.1 and the captured Next-vendored browser canary are
   recorded separately.
4. **Parallel compatibility priority:** distinguish module-local generation
   from durable cache invalidation, then inspect guest export quiescence and
   scheduling. Persistent nonce success never waives the original counter
   failure. Per-instance reuse128 does not guarantee global request affinity;
   Wasmtime's [serve options](https://raw.githubusercontent.com/bytecodealliance/wasmtime/v42.0.1/src/commands/serve.rs)
   and [worker dispatch](https://raw.githubusercontent.com/bytecodealliance/wasmtime/v42.0.1/crates/wasi-http/src/handler.rs)
   describe reuse and availability, not an observed Store identity in this run.
   Preserve per-instance/process limitations explicitly.
5. Check wasmCloud, lifecycle/resource limits and measured costs after the
   relevant application gates. Preserve the read-only route delegate, bounded
   two-primary-tag mutation contract, all failures and unchanged legacy app code.

The implementation/build checkpoint is committed and pushed through
`172f5690`; [progress.md](../../progress.md) tracks current work and closed evidence.

The retained first fresh **Next 16.4.5 / React 19.3.1 App Router application
passes the selected experimental Wasmtime smoke contract**:
24/24 HTTP checks, cache generation 1 → 2, five incremental Suspense chunks,
and both browser interactions, with zero recorded browser or observer errors.
A stock Node 22.14.0 control passes the same browser worker, readiness checks,
20-second test limits and error gates in the first fresh pair. The later fixed
cohort passes native3/3 and stock2/3, leaving its combined all-six gate failed.
The [fresh paired review](../../tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/first-pair-review/README.md)
and [cohort review](../../tests/node-compat/frameworks/nextjs/next-browser-reliability-root-results-v1/cohort-review/README.md)
retain these separate outcomes. Next.js execution takes priority over expanding
unneeded Node APIs. The first concurrent request/body/recovery pair now passes all 80 supplemental
checks per arm but fails strict acceptance: native cache generation1→1, stock
1→2, and browser action-response aborts in both. See the [actual results](nextjs-request-regression-2026-11-07.md).

The accepted production checkpoint remains
[foundations-v13](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md).
The new result is an experimental profile, not production promotion or complete
Node/Buffer compatibility. Server JavaScript executes in SpiderMonkey inside
Wasm; the browser executes ordinary Next client JavaScript. This is neither
JavaScript AOT compilation nor a client-side Wasm port.

## Retained passing generation

The retained first fresh-app component is `1c3108d2…` (37,214,251 bytes), engine `4623640b…`
(31,324,051 bytes), and incremental metadata `726d69cf…`. The engine retains the
coherent patched Intl/SavedFrame V7 build and its 80 native compile rows plus
separate embedding as ancestry. One fresh UTF-16 Module translation unit and a
new archive/relink replace the failed non-ASCII `Function` workaround; this is
not a claim of 80 fresh frontend compilations. The
[build review](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-root-results-v1/actual-review/README.md)
records that distinction and the input protections. Earlier `55f05e3d…`
first/repeat successes remain in the [original milestone](nextjs-wasm-milestone-2026-11-06.md).

The raw [guest entry](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v5/guest-entry.mjs)
loads the unmodified standalone application from `/app`. Its six bounded guest
facades provide the Node global alias, cross-prototype Buffer input handling,
send's ReadStream options, AbortSignal-aware pipeTo, classic request-body
conversion, and AsyncResource construction/runInAsyncScope over native ALS
capture. Their limits remain part of the experimental contract. The entry
contains no `Function` compilation fallback or diagnostic app wrapper.
The current integrated V5 component also includes the reviewed observed-I/O
abort policy; it is the artifact selected by the fresh regression command.

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

## Immediate Next.js critical path

The **fresh isolated app build now passes on matched Node and real Wasm**. Its
four owned host-build phases pass;
the [actual DATA review](../../tests/node-compat/frameworks/nextjs/next-app-build-root-results-v1/actual-review/README.md)
retains the genuine2,181-file inventory and new build/action IDs. The new
nativeV7, matched-NodeV3 and browserV3 Sources now pass independent review for
the root-excluding schema, empty owned-copy cache mountpoint and two changed
script pins. The [reusable fresh-app command](../../tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/README.md)
ran the first actual native trial successfully and preserves fresh results.
Both arms pass the unchanged24HTTP/cache1→2/five-chunk stream/2strict-browser
contract, raw0/clean with protected inputs. Native result650e7a91/8546 and stock
1e02e583/323608 use component1c3108d2/engine4623640b and the genuine fresh app.
The [portable paired DATA review](../../tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/first-pair-review/README.md)
retains304 payloads and passes Root readback; the prior abort remains unresolved.

Earlier sub1GiB capacity holds ended when launch admission measured1,638,600,704
free bytes for stock and1,578,336,256 for native. Keep the same start guards on
future actions; this is not measured peak demand. No SDK, old proof or shared
binary was deleted to manufacture headroom.

## Execution order

Run new application checks with the existing component before changing the
engine. Keep source-build preparation moving while the volume lacks launch
headroom. Do not wait for a stock-only diagnostic to finish before testing a
new native application behavior; preserve its strict failure and unresolved
cause. Every changed engine must rerun the complete app contract.

The capacity hold ended after the user freed the volume: native admission
observed23,397,662,720 free bytes. The first real request pair is complete and
failed strictly as described above. The first full-build admission then found
two missing empty SDK directories; their exact pinned-archive restoration is
recorded without inventory or Source changes. The fresh full build now passes
independent DATA review: engine02a6601d/31,324,563 bytes, full metadata9e960c41/
4,877,968 bytes,80 native TUs plus separate embedding, all825 copies and protected
inputs intact. ConstructorV6 now passes INIT/validation/WIT DATA review for
component4afeeb76/37,218,693 bytes, with the same13 standard0.2.10 imports.
Its first V9 application run is terminal and independently checked:80 supplemental
checks,24HTTP, five chunks and two functional browser interactions pass, while
cache1→1 and strict action-response capture fail. Keep the1GiB runtime/3GiB
build admission policies on future actions.

The separately declared affinity component811459ea now completes its first
deployed run. All80 supplemental/24HTTP/stream checks pass; cache1→1 still
fails. Its strict browser gate passes in this sample. Four admission records
show different JS-global state epochs for cache-first, repeat, invalidation
and after-revalidation, each with ordinal7. This does not identify private
Stores or prove the callback/tag-map cause. Added logging may perturb timing;
the browser positive does not accept prior failures. The
[diagnostic plan/results](nextjs-cache-affinity-diagnostic-plan.md) and
[optional shared-cache proposal](nextjs-portable-cache-proposal.md) keep the
original failed process-counter contract separate from any future scenario.

The [exact-action transport EOF control](nextjs-action-transport-2026-11-07.md)
now passes both predeclared native/Node arms0/clean/protected, with valid complete
chunked/gzip messages and2963 opaque decoded bytes each. This is a separate
draining client without navigation, not a cause proof or old-browser waiver.
Its182-member packet is sealed and passes independent/current-original readback.
The checked loader-referrer boundary now compiles in a separately accepted full
buildca84/e674 (825 inputs,80 native TUs plus embedding); fresh INIT component49013f31
passes complete typed-return/standard13-import/world/package DATA review.
Its first full unchanged deployed regression finishes1/clean/protected:24HTTP/
80supplemental/stream and both strict browser tests pass, but cache1→1 still
fails. Independent DATA review is pending; no browser reliability/fix claim
follows. Both records now have sealed replayable DATA packets. The separate
two-case deployed guard probe also passes0/clean/protected: builtin import works
and natural CJS file-URL import rejects with the selected TypeError/code/operation/
specifier. Independent DATA review passes. A genuine pinned Node reference
imports that target successfully; safe refusal remains a compatibility gap.
The bounded interop prototype's825 sources are now freshly materialized and
admitted, with824 other payloads/21 Rust files unchanged. It remains uncompiled.
The next implementation order is: run its unchanged generator checks and full
native build; construct/test the sixteen-case interop component; then build an explicitly configured portable cache scenario
through Next's actual CacheHandler extension. Do not patch global state or
change host scheduling to simulate one Node process.

| Priority | Work | Completion gate |
| --- | --- | --- |
| 1 | Run the freshly built unchanged Next app in Wasm | **First actual pair passes** on nativeV7/stockV3/browserV3:24HTTP/cache1→2/five chunks/2strict-browser checks, raw0/clean/protected inputs. Genuine2,181-file inventory/new build+action IDs run on1c3108d2 without rebuilding the engine. The304-payload portable paired DATA review passes Root readback. Old2,218-file evidence and failures remain unchanged. |
| 2 | Resolve the actual request-regression failures | The [first real V8/V6 pair](nextjs-request-regression-2026-11-07.md) completes both arms. Each passes 80 supplemental checks, physical six-case outcomes, 24 individual HTTP checks, five stream chunks and two functional browser interactions. Native cache stays 1→1 (failed), stock advances 1→2; both strict browser gates retain action POST ERR_ABORTED/null body. The closed reader accepts capture integrity and rejects whole-pair admission. Preserve these failures; investigate cache/process-instance scope and browser cancellation without waivers or cause claims. |
| 3 | Build and regress the genuinely rebuilt engine | The [SDK-restored full build](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-sdk-restored-root-v1/README.md) completes raw0/clean and passes independent DATA review: all825 inputs,80 native TUs plus separate embedding, fresh Rust/link inputs and ten preserved trees. ConstructorV6 also passes INIT/validation/WIT DATA review for4afe/02a/9e960. Its [first V9 application trial](../../tests/node-compat/frameworks/nextjs/next-full-build-runtime-root-results-v1/) preserves the same strict cache/browser failures despite80 supplemental/24HTTP/stream/function passes. Diagnose those failures; no runtime acceptance or clean-machine reproduction follows from a passing build. |
| 4 | Close response, context and resource boundaries demanded by Next | The [native-stream probe](../../tests/node-compat/frameworks/nextjs/native-pipe-root-results-v1/README.md) matches36 Node records; context interleaving and isolated I/O-abort controls pass their bounded contracts. Broader cancellation/compression, AsyncResource, native handle counts, trailers and teardown remain open. Guest facade results do not prove native private-state/resource counts. Fix observed application failures before adding unrelated APIs. |
| 5 | Investigate browser reliability without erasing the failure | The [fixed cohort](../../tests/node-compat/frameworks/nextjs/next-browser-reliability-root-results-v1/cohort-review/README.md) retains **5/6 strict passes and an unmet all-six gate**. The direct standalone control passes. The three predeclared [extra-CDP-session-off Node controls](../../tests/node-compat/frameworks/nextjs/extra-cdp-off-root-results-v1/completed-final-audit.json) all pass strictly, but one separately declared [native off-session control](../../tests/node-compat/frameworks/nextjs/next-native-extra-cdp-off-root-results-v1/README.md) still fails cache1→1/action capture despite80supp/24HTTP/stream/two functional-browser passes. The instrumentation change is not sufficient for this native sample; investigate completion without unique cause, retry acceptance or reliability claims. |
| 6 | Preserve the second-host boundary | **Fresh cold8 passes** on stock wasmCloud2.11.0/embedded Wasmtime48.0.7, including strict streaming and protected inputs. The [coldV4 review](../../tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v4/actual-review/README.md) passes Root readback. Retained-cache/browser acceptance remains separate: this host's selected P2 path does not retain an instance between requests. Do not change the host or widen the world to force that behavior. |
| 7 | Measure and consider production promotion | The [paired measurement plan](nextjs-measurement-plan.md) is unexecuted; no performance advantage or memory bound follows. Review exact manifests, defaults, build inputs, INIT barriers, facade limits and host rights, then run release/compatibility suites before promotion. Keep foundations-v13 accepted until that decision is explicit. |

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
| Native web and classic streams | The app's request conversion, response piping, gzip/static delivery and five-chunk Suspense path pass. | pipeTo facade disturbed-state/queued-close/private-state limits and signal pipeThrough remain explicit; broader native stream regression remains open. |
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
