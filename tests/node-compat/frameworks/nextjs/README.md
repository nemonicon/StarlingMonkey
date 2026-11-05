This experiment tests a real Next.js application against the accepted StarlingMonkey
profile. **The full Next.js server does not currently compile through this profile's
bundler.** The stock Node application works; its failures in the Wasm pipeline are
retained as regression observations.

The fixture pins Next.js **16.4.5**, React/ReactDOM **19.3.1**, Node **22.14.0**,
ComponentizeJS **0.23.0**, Jco **1.40.0**, Rolldown **1.2.16**, and Wasmtime
**42.0.1**. Browser controls use Playwright Core **1.64.1** and the installed
Chrome executable, whose version and SHA are recorded. Both npm dependency trees
have lockfiles. The native engine is accepted **foundations-v13**, normal OFF,
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
policy is used. None of the full Next entries reaches component construction,
so there is no deployed Next HTTP/Wasm result. wasmCloud was not exercised for
this new application.

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

# Current baseline: the driver exits 1 with complete observations and known breaks.
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

The next implementation priorities from this experiment are:

1. Add audited production CommonJS package bundling while preserving native
   builtin admission and explicit denials. Re-run the unchanged real Next/React
   entries to reveal the next barrier; this alone will not supply Node services.
2. Implement and differentially validate demanded small semantics such as
   `util.format`, retaining the current deferred-operation failure tests.
3. Design genuine request-context/AsyncLocalStorage propagation and a selected
   standard WASI HTTP integration. Node socket listeners and filesystem loaders
   require their own capability contracts; WASI sockets do not imply TLS.
4. Keep this fixture, positive native differential and known-failure comparison
   in future release checks. Review changed blockers before updating a baseline.
