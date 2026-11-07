# Next.js execution

The unmodified **Next.js 16.4.5 / React 19.3.1** standalone application now
passes the selected **experimental native Wasm smoke contract**: 24/24 HTTP,
cache generation 1 → 2, five incremental Suspense chunks, and 2/2 browser
interactions with zero recorded page, console, request or observer errors.
The same hydration-aware browser worker, whole 20-second limits and strict
error gates also pass against stock Node 22.14.0 in the first fresh pair. The
later fixed cohort passes native3/3 and stock2/3, leaving the all-six strict
gate failed; the stock action abort remains unresolved. The
[current milestone report](../../../../docs/node-compat/nextjs-wasm-milestone-2026-11-06.md)
and [priority roadmap](../../../../docs/node-compat/nextjs-priority-roadmap.md)
record the exact scope and remaining work. The current
[fresh-app paired review](next-app-runtime-root-results-v1/first-pair-review/README.md)
and [cohort review](next-browser-reliability-root-results-v1/cohort-review/README.md)
retain those new results separately. Earlier portable
[native first/repeat](next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
and [matched Node](next-intl-runtime-root-results-v1/hydration-stock-v1-review/README.md)
reviews retain the actual evidence and DATA checkers.

The current fresh-app route uses component `1c3108d2…` (37,214,251 bytes), engine `4623640b…`
(31,324,051 bytes), the V5 integration of the raw entry and its six bounded
guest facades plus observed-I/O abort policy. The earlier55f05 generation and
[entry V4](next-component-entry-fixes-v4/guest-entry.mjs) remain retained.
Native UTF-16 Module compilation preserves
real source and stack provenance; no Function fallback or app source rewrite is
installed. Server JavaScript runs inside SpiderMonkey/Wasm while the browser
runs ordinary Next client JavaScript. This is not JavaScript AOT compilation
or a client-side Wasm application.

Stock Wasmtime 42.0.1 is configured with reuse **128**, idle timeout **60s**,
a physically read-only app tree mounted at `/app`, a fresh writable nested
cache and explicit loopback origin.
The component emits exactly thirteen selected standard WASI **0.2.10** imports
and the incoming-handler export. No custom host service, host modification,
interface widening or raw socket/TLS implementation is used. wasmCloud's pinned
P2 HTTP path creates a fresh instance per request and is not accepted for this
retained-server/cache contract. The fresh-app [eight-request cold control](wasmcloud-cold-candidate-v4/README.md)
now passes on stock wasmCloud2.11.0/embedded Wasmtime48.0.7 using the current
component: health×3, SSR, JSON POST, filesystem/SHA, assets and strict incremental
streaming. Its runtime/CLI parents exit0 with inputs preserved. The [portable
DATA review](wasmcloud-cold-root-results-v4/actual-review/README.md) retains175
records and passes readback. The earlier
TCP-only readiness attempt's eight host404s remain retained failures. No browser
or retained cache assertion ran on wasmCloud. The physical 0444/0555 modes do not establish
read-only capability rights on the WASI preopen descriptor. Production remains accepted **foundations-v13**;
the experimental pass does not promote broad Node or Buffer support.

The [hydration worker](browser-hydration-candidate-v1/README.md) observes the
pinned React own-data handler binding without invoking it, then performs the
same real counter click and browser action. Nine decoded script responses
match five unchanged app files; a tenth captured body is the actual POST RSC
response. The previous early-click timeout and aborted action request remain
failed observations, with no retroactive causal or pass relabeling.

Use the [fresh-app runner](run-fresh-next-regression.py) for the current
experimental generation and its exact reviewed private artifacts:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/run-fresh-next-regression.py --run-id FRESH
```

A fresh lowercase run ID of at most48 characters is mandatory. The command
requires at least1GiB free at launch and preserves each result. `--prepare-only`
writes a request without starting the runtime or browser. It reuses the pinned
app and component; it does not build them from a clean checkout. The older
[retained-artifact runner](run-native-next-regression.py) still selects55f05 and
its original application generation. Do not mix their inventories.
Portable clean-machine bootstrap and broader lifecycle/production regression
work are separate; the historical commands
below deliberately reproduce the older foundations-v13 bundler corpus.

The next [request-isolation regression](next-app-request-isolation-root-results-v1/README.md)
adds six overlapping context/body/recovery checks while preserving that full
contract. Its Source/local-client tests and preparation pass, but its real
launch stopped before any actor below1GiB free; all six application cases are
still unexecuted. Use `run-next-request-regression.py --run-id next-check-001` once there
is sufficient headroom. It reuses the same app/component and retains partial
bytes and errors; it makes no same-instance concurrency claim.
The prepared `run-next-request-control.py` command uses the same helper against
pinned Node while retaining the original strict control gates. Neither new
six-case arm has run against real Next yet.

## Historical foundations-v13 bundler corpus

The original experiment tested the full application against the accepted
foundations-v13 finite profile. Its full Next entries were refused by that
profile's bundler; the working stock Node controls and every Wasm failure remain
regression observations. The newer successful raw-entry/native-loader route
above does not replace or rewrite this corpus.

The [2026-11-06 post-push application report](../../../../docs/node-compat/nextjs-results-2026-11-06.md)
records two fresh builds after `77659217`,24/24 HTTP checks per run and the same17
Wasm failures. Both browser interactions work; one first-run aborted action POST
fails the network-error check, while the untouched replay passes it. That failed
record remains retained. The fresh supported supplement passes full Node/Jco/
Wasmtime comparison; the optional package matrix keeps three positives and seven
guest failures. Exact generated-input changes are reviewed separately from
changed failure reasons. The reproduction commands below remain checks for that historical corpus;
they do not replay the newer native server component.

The retained-evidence checks were rerun on2026-11-06: the full Next baseline/replay
comparison and43 injected checks, optional package comparison and40 injected
checks, and the separate seven-return clock check with18 semantic negatives all
pass. These are evidence rechecks; the known17 main-Next and seven optional-matrix
failures remain. Current native experiments and outstanding work are tracked in
[progress.md](../../../../progress.md).

The follow-on [optional package-bundler experiment](../package-bundler-execution-v1/README.md)
advances beyond the original CommonJS refusals below. A fresh ten-case run after
checkpoint `d8034839` passes complete Node/Jco/Wasmtime comparisons for native
CommonJS interop, the supported native modules and real React elements. ReactDOM
edge builds but traps on both hosts; Next libraries and generated server/page/route
entries remain refused. The [post-push results](../package-bundler-execution-v1/results-post-push-v2/results.json)
retain the corrected Node Next subpath controls and every guest failure. The table
below describes the original finite-profile baseline; the optional experiment has
its own runner and regression baseline. It does not replace that baseline.

A separate opt-in standard-clock probe now renders the exact retained ReactDOM
edge workload on stock Wasmtime and returns the complete Node-equal HTML. Its
component imports only `wasi:clocks/monotonic-clock`,
`wasi:clocks/wall-clock` and `wasi:io/poll` at **0.2.10**.
[The retained comparison](../../foundation-scheduler/clock-v13-wasmtime-first-render-v1-comparison.json)
and [independent result review](../../foundation-scheduler/independent-clock-v13-first-wasmtime-render-results-review-v1/results.json)
cover the first fresh render. A later [seven-return differential](../../foundation-scheduler/clock-v13-runtime-v2-root-results.json)
finishes raw0: three retained Jco calls, one fresh Jco call and three fresh
Wasmtime calls all match the complete retained Node result. [Independent review](../../foundation-scheduler/independent-clock-v13-runtime-v2-results-review-v2/results.json)
passes all seven full returns and raw cleanup. The zero-import failure above remains the
original regression baseline. Clock lifecycle gates remain separate; this historical clock experiment did
not exercise the full Next server.

Use the separate read-only [clock record checker](../package-bundler-execution-v1/check-clock-render.mjs)
for this exact experimental source/component generation:

```sh
node tests/node-compat/frameworks/package-bundler-execution-v1/check-clock-render.mjs \
  /private/tmp/starling-node-compat/clock-v13-runtime-v2 \
  tests/node-compat/foundation-scheduler/clock-v13-runtime-v2-root-results.json \
  --self-test
```

The directory argument may point at a genuine fresh run or a complete relocated
copy. The checker validates all published file hashes, seven complete strings,
five child terminals, recorded native frame and selected-interface fields.
Changed source/component pins require review. It does not rerun a component,
reaudit the emitted type graph, or replace the independent parent/provenance
review. Its 18 semantic negative cases and separate changed-byte/unindexed-file
checks pass; the original Next comparators below retain their own baselines.

The fixture pins Next.js **16.4.5**, React/ReactDOM **19.3.1**, Node **22.14.0**,
ComponentizeJS **0.23.0**, Jco **1.40.0**, Rolldown **1.2.16**, and Wasmtime
**42.0.1**. Browser controls use Playwright Core **1.64.1** and the installed
Chrome executable, whose version and SHA are recorded. Both npm dependency trees
have lockfiles. The native engine for this historical corpus is accepted **foundations-v13**, normal OFF,
SHA `d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92`.
Its metadata SHA is `bfaec95ee0058edf587ebbf1cb020d7871759e896aa0d809e1af788a300531d6`;
all 342 native source hashes and nine selected manifests are checked.
This is an application experiment, not acceptance of a new native profile.
Unaccepted 350/355 codec, consumer and crypto ownership generations are not
substituted into this application experiment; their separate proofs stay separate.

| Actual test | Result |
| --- | --- |
| `next build --webpack`, genuine standalone server and copied public/static assets | Pass on Node, in two fresh runs |
| 23 HTTP contract requests plus a real, build-derived server-action POST | 24/24 pass per run |
| Browser hydration/counter click and real form server action | 2/2 pass per run; no recorded browser errors |
| Cookies, headers, redirects, not-found, JSON GET/POST/bad input | Pass in the Node baseline |
| Same-server cache repeat and invalidation | Generation 1 is reused, then becomes 2 |
| Suspense delivery | First run retains five raw chunks; shell in chunk 0, ready in chunk 2 |
| React element, ReactDOM edge/string renderer, Next request/response/headers, generated standalone/page/route | Eight bundling refusals: unsupported general CommonJS/`require` contract |
| `fs/promises`, `crypto`, `async_hooks`, `http`, `net`, `url`, `process`, `timers` imports | Eight explicit native-profile admission refusals |
| Original shared application compatibility function | Builds a zero-import component, then traps on both Jco and Wasmtime |
| Separate caught-error diagnostic | Identifies `ERR_SM_NODE_UNSUPPORTED`: `node:util.format` is deferred |
| Supported native-module supplemental differential | Pass: complete Node, three retained Jco and fresh Wasmtime returns match |
| `child_process.exec` and three unsupported Buffer overloads/methods | Expected identifiable refusals; three retained Jco calls equal fresh Wasmtime returns |

The [supplemental results](results/2026-11-05-v13-supplement/results.json)
verify Buffer copying/shared ArrayBuffer and slice relationships, zero allocation,
UTF-8/hex, path, EventEmitter on/once/off, split UTF-8 StringDecoder, scalar asserts,
query strings, util type predicates, native web streams and a classic-stream
pipeline. Complete strings and structured values match Node on both component
execution paths. This supported subset omits the deferred `util.format` call
explicitly; the original failing application test remains unchanged.

The original shared function completes its earlier operations before calling
`util.format`, but its trap does not provide a complete successful return.
The caught diagnostic establishes the error in that wrapper; the generic trap
alone does not identify its cause. Neither the wrapper nor a bounded positive
probe substitutes for running the actual Next framework.

The [fixture contract](fixture-contract.json) covers static and nested layouts,
dynamic/query SSR, metadata, client rendering, Suspense, server actions, request
context, cache invalidation, public assets, JSON routes, bounded Node operations,
and a real filesystem/SHA-256 route. Node's success on that last route does not
implement guest filesystem or `node:crypto` bindings. The [source audit](audit.md)
separates observed failures from likely later requirements such as process
semantics, request async context, file loading and a real WASI HTTP adapter.

The [main results](results/2026-11-05-v13/results.json) and
[fresh replay](results/2026-11-05-v13-replay/results.json) retain all 19 Wasm
observations: 16 bundling refusals, one execution failure and two passing refusal
probes. The test driver deliberately exits **1** because the full shared
Node/Wasm differential cannot pass. Known failures are not converted into API
support. The separate observation comparator distinguishes unchanged failures,
regressions, improvements and a changed blocking reason.
The [retained-evidence validation](results/2026-11-05-v13/evidence-validation.json)
passes 1,673 checks across 505 files, including response bodies, screenshots,
raw stream reassembly, terminals, component hashes, full returns and native inputs.

All three components emitted by each main run have exactly `run() -> string`
and **no imports**, including the component that traps. They are 12,946,112,
12,914,375 and 12,912,302 bytes in the first run. These sizes include the engine;
they are not incremental library costs or performance measurements. No custom
host service, host modification, adapter Buffer replacement or widened import
policy is used. None of the full Next entries in this historical bundler corpus reached
component construction, so that corpus contains no deployed Next HTTP/Wasm
result. This does not describe the newer native milestone above. wasmCloud
was not exercised for this historical application run.

Use an exact Node 22.14.0 executable and the existing reviewed packager/toolchain.
Keep generated dependencies and binaries outside the checkout. Default paths
refer to this workstation; override the environment and engine/source arguments
with genuine copies of the same pinned artifacts when reproducing elsewhere.
The source-root argument is checked against the actual engine source manifest.

```sh
export NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/toolchain
export NODE_COMPAT_COMPONENTIZE_MODULE=/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js
export NODE_COMPAT_WASMTIME=/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime

node tests/node-compat/frameworks/nextjs/run.mjs --browser \
  --engine /tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm \
  --source-root /tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source \
  --output /private/tmp/nextjs-fresh-run \
  --record /private/tmp/nextjs-fresh-evidence

# Historical v13 baseline: the driver exits 1 with complete observations and known breaks.
# Evaluate the retained evidence even when that expected exit occurs.
node tests/node-compat/frameworks/nextjs/check-results.mjs \
  tests/node-compat/frameworks/nextjs/results/2026-11-05-v13/results.json \
  /private/tmp/nextjs-fresh-evidence/results.json
```

The [actual fresh-run comparison](results/2026-11-05-v13-replay/comparison.json)
exits `0` with no regressions or changed blockers and 17 known failures retained.
The comparator also passes [43 injected checks](results/comparator-self-tests.json),
including missing evidence, interrupted workers, successful-return mismatches,
changed errors and reordered parallel diagnostic blocks.

Comparator exit `0` means no new observation regression, including explicitly
listed known failures; it does **not** mean Next.js works in Wasm. Exit `1` means
regression/incomplete evidence, and exit `2` requires review of a changed blocker.
It compares whole successful typed returns, requires complete worker terminals,
checks the Node/browser controls, and refuses a newly successful compatibility
case without its Node/Wasm differential. Engine upgrades require explicit new
artifact pins and admission; do not simply relax the existing checks.

The supplementary differential can be repeated against the application tree
produced by a full run, without rebuilding Next:

```sh
node tests/node-compat/frameworks/nextjs/run-diagnostics.mjs \
  --application /private/tmp/nextjs-fresh-run/application \
  --output /private/tmp/nextjs-fresh-supplement \
  --record /private/tmp/nextjs-fresh-supplement-evidence
```

It must exit `0` with the full Node/Jco/Wasmtime differential passing and the
separately caught original error identified. It uses the same environment
settings above. The default browser executable is macOS Chrome; its path/version
are not part of a claim about cross-platform browser automation. Guest components
remain capability-free.

The first [harness preparation failure](results/2026-11-05-v13-attempt1/harness-failure.json)
is preserved: a reporting lockfile changed Next's inferred tracing root and the
recorder's parent was absent. A later replay comparator correction handles the
same two parallel Rolldown diagnostics appearing in opposite order, retaining
the raw messages and every diagnostic block. These are harness/reader issues,
not additional runtime capabilities.

Repository evidence includes complete HTTP bodies, browser screenshots/errors,
process logs/terminals, emitted WIT, typed returns, source snapshots and artifact
descriptors. Large components, transpiled cores and `node_modules` remain at the
recorded external paths. An evidence commit does not make those binaries part
of Git. The experiment does not measure performance, prove request reuse or
establish complete Buffer, Streams, Node or Next.js compatibility.

The following historical demand priorities led to the native route above.
Current work is ordered by the [priority roadmap](../../../../docs/node-compat/nextjs-priority-roadmap.md);
these original requirements remain recorded for the older corpus:

1. Integrate and extend the separately tested optional production CommonJS
   bundler while preserving native builtin admission and explicit denials. Its
   real React/Next runs now expose clocks, async context, process and loader
   barriers; repeat those unchanged entries after each relevant runtime change.
2. Implement and differentially validate demanded small semantics such as
   `util.format`, retaining the current deferred-operation failure tests.
3. Design genuine request-context/AsyncLocalStorage propagation and a selected
   standard WASI HTTP integration. Node socket listeners and filesystem loaders
   require their own capability contracts; WASI sockets do not imply TLS.
4. Keep this fixture, positive native differential and known-failure comparison
   in future release checks. Review changed blockers before updating a baseline.
