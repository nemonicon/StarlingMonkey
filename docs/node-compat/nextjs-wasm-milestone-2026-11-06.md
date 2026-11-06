# Passing Next.js component milestone

The unchanged Next.js **16.4.5 / React 19.3.1** application passes its selected
full application contract in a real StarlingMonkey Wasm component on stock
**Wasmtime 42.0.1**. Two fresh Wasmtime runs and the matched **Node 22.14.0**
control pass. This is an experimental compatibility generation; the accepted
production checkpoint remains [foundations-v13](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md).

The server JavaScript executes inside SpiderMonkey in Wasm. Componentization
snapshots the runtime entry; the deployed component loads the unchanged Next
standalone files from the selected filesystem mount. Browser client JavaScript
executes normally in Chrome. This result does not claim JavaScript AOT, an
application embedded wholly in one component, or a browser Wasm port.

## Verified results

| Contract | Wasmtime first run and repeat | Matched Node control |
| --- | --- | --- |
| HTTP: SSR/layouts/query, headers/cookies, JSON GET/POST/bad input, redirects/404s, filesystem/SHA, assets, cache and real build-derived action | 24/24 each | 24/24 |
| Cache repeat and invalidation | Generation 1 reused, then 2 | Same |
| Suspense streaming | Five chunks, shell 0, ready 2, incremental and complete | Same selected assertions |
| Hydrated client counter | One real click changes 0 → 1 | Pass |
| Hydrated Server Action | Real form submit reaches action result | Pass |
| Browser page/console/failed-request/collector errors | All empty | All empty |
| Original application, copy provenance and shutdown | Original and physical read-only copy preserved; original parent exit 0; all owned groups gone | Original preserved; independent source-mode copy and fresh owned cache; original parent exit 0; all owned groups gone |

The browser harness captures decoded script bodies, response headers, encoded
byte counts and the full event trace. All five pinned client-counter scripts
match the unchanged source bytes. The first native run has nine matching script
fetch captures across the two interactions, plus the actual action RSC body.
Playwright supplies decoded bodies; no compressed wire hash is claimed. The
action's opaque RSC response contains different generated Flight key prefixes
on Node and Wasm. Raw bodies are retained; passing the selected semantic
assertions does not imply byte equality for that response.

The passing [hydration harness](../../tests/node-compat/frameworks/nextjs/browser-hydration-candidate-v1/README.md)
waits for load and the actual React own-data handler before the same click and
form submit. Each test retains its whole **20-second** limit and strict error
gates. It does not call handlers directly, edit application code, increase
timeouts, retry failures or filter cancellations. The matched Node control uses
byte-identical worker code.

The earlier 24/24 HTTP, 1/2 browser result remains failed and retained. Its
counter click preceded all five script responses by about 2.15 seconds. Waiting
for observed hydration resolves that counter failure in both subsequent native
runs. The earlier action fetch abort remains a historical failure; later success
does not retrospectively classify its cause. The original no-Intl, 11/24 route,
eval-provenance and 22/24 failures also remain available.

## Exact generation and capabilities

| Artifact | Identity |
| --- | --- |
| Audited StarlingMonkey base | `54b3329b3ce818fd1f244e871e9c259b63667cda`, plus the recorded composed profile and afterimages; repository HEAD is not compiled identity |
| Guest SpiderMonkey | Firefox fork `9dab3d6f643e926a340c391ea30968e940390dec`, Intl/ICU enabled, guest SavedFrame patch `1a571a89…` |
| Native engine | `4623640b79b97eb91dc8559b3766fdb430a1807fe90b6ace6c85668a97f13067`, 31,324,051 bytes |
| Native metadata | `726d69cf60f99c53a472bde9af1d26a9c8c76aaad9cf8bb90255788ee0bb9bfb` |
| Component | `55f05e3d75b199c6a9e2afa54c7bfe3e2ba6d506324cb896b4d6c4c122f09f70`, 37,214,436 bytes |
| Entry source | [V4](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/index.json), raw entry `c43117a4…`, source index `34c35012…` |
| Constructor | [V4](../../tests/node-compat/frameworks/nextjs/next-entry-fixes-construction-v4/index.json), `add21dc4…` |
| Runtime harness | [V5](../../tests/node-compat/frameworks/nextjs/wasmtime-deployment-candidate-v5/index.json), `dd05c177…`; browser `b7f4ff00…` |
| Packaging | ComponentizeJS 0.23.0, Jco 1.40.0; selected world `next-http`; AOT disabled |
| Application | Next 16.4.5, React/ReactDOM 19.3.1; 2,218 unchanged standalone files, 48,808,299 bytes |
| Browser | Playwright Core 1.64.1, Chrome 156.0.8078.81; executable hash recorded in raw results |

The engine's UTF-16 correction uses real SpiderMonkey compilation rather than
the failed `Function` fallback. Its [build review](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-root-results-v1/actual-review/README.md)
records **one fresh frontend**, 1,046 preauthenticated dependencies and 14
unchanged node archive members. The baseline's 80 compile-database rows and
separate embedding are ancestry, not 80 fresh compilations in this delta.

Six bounded guest entry facades supply the global alias, intrinsic Uint8Array
Buffer input recognition, send's ReadStream options, signal-aware response
piping, classic Readable Request BodyInit conversion, and AsyncResource
construction/runInAsyncScope backed by native ALS.snapshot. Their CJS versus
named ESM gaps, deferred operations and stream private-state limits remain
explicit. The entry installs during INIT without loading application files,
capturing request context or consuming deployed entropy. This pass does not
extend the declared Buffer or module export contract.

The validated component emits exactly these **standard WASI 0.2.10** imports:

```text
wasi:cli/environment
wasi:cli/stdout
wasi:cli/stderr
wasi:clocks/monotonic-clock
wasi:clocks/wall-clock
wasi:random/random
wasi:io/error
wasi:io/poll
wasi:io/streams
wasi:filesystem/types
wasi:filesystem/preopens
wasi:http/types
wasi:http/outgoing-handler
```

Its only export is `wasi:http/incoming-handler@0.2.10`. No external Preview 1
or custom import remains. A guest-contained adapter translates engine Preview 1
calls into the selected Preview 2 interfaces. No host modification or socket,
DNS or TLS implementation is introduced; WASI P2 sockets do not supply TLS.

The successful launcher explicitly uses Wasmtime instance reuse **128**, idle
timeout **60s**, an independent `/app` tree with physical modes 0444/0555 and a
fresh writable `/app/.next/cache`, plus the exact loopback origin. Physical
modes and preserved bytes do not establish read-only WASI descriptor rights.
These settings are part of this tested contract.
Pinned wasmCloud 2.11.0's normal P2 HTTP path creates a fresh store/instance per
request. The retained-server/cache contract remains unavailable on that path;
pool settings for its P3 path are not a substitute. See the
[host lifetime analysis](../../tests/node-compat/host-capabilities/wasmcloud-warm-candidate-v1/README.md).

## Repeat and inspect

On this workstation, with the exact private pinned artifacts still present:

```sh
/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9 -I -B \
  tests/node-compat/frameworks/nextjs/run-native-next-regression.py \
  --run-id next-manual-20261106-01
```

Choose a new run ID each time. The wrapper checks baseline request/runner and
selected artifact hashes, creates a fresh request outside the checkout, and
calls the existing owned runner. That runner authenticates full source families,
tools, construction and application before and after serving. It retains the
same Wasmtime flags, independent app/fresh cache, all HTTP/stream/browser checks,
bounded ownership monitor and strict exit behavior. It does not build or
replace anything. `--prepare-only` writes the request and prints the exact
command without launching; execute that printed command to run it afterward.

Results go to `/private/tmp/starling-node-compat/next-wasmtime-deployment-RUNID`;
the sibling `-external-root/observation.json` must report `passed: true`,
`rawExitCode: 0`, `ownedGroupsClean: true` and
`protectedInputsPreserved: true`. Inspect the client HTTP/cache/stream and browser
results too. A recorded expected failure is not a successful regression.

The wrapper has been exercised by actual run
`engine462-hydration-v5-repeat`, which passes the complete contract again.
This is a retained-artifact replay path, not a clean-machine bootstrap. Other
workstations require genuinely reproduced artifacts and reviewed path/pin
manifests; do not bypass checks by altering expected hashes.

Portable, hash-checked raw evidence and read-only DATA checkers are retained in
the [native review](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
and [matched Node review](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-stock-v1-review/README.md).
Those checkers validate evidence; they do not execute a fresh component or
replace the runtime command above.

## Outstanding work

1. Package the exact working generation into a reproducible build/release path;
   application mounting and local artifact inventories currently remain explicit.
2. Run the prepared native pipe cancellation/backpressure/error/lock regression,
   then broaden meaningful context, cancellation, overlapping-request and teardown
   checks. The passing sequential smoke is not exhaustive lifetime evidence.
3. Integrate or retain each audited facade through an explicit production
   decision, preserving error semantics, native roots/ownership and named ESM
   bindings. Run the required production suites before changing the accepted
   checkpoint.
4. Measure component size, startup, memory and throughput against declared
   controls. The sizes above are artifact measurements, not performance gains.
5. Track deeper Next features and other hosts separately. General Node APIs,
   full Buffer/streams/CallSite semantics, TLS, middleware/image transforms,
   arbitrary packages and wasmCloud retained P2 execution are not established.

The dependency order is maintained in the [priority roadmap](nextjs-priority-roadmap.md)
and current completion/in-progress status in [progress.md](../../progress.md).
