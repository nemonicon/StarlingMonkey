# Next.js capability checks after checkpoint 77659217

Follow-on work is now ordered by the [Next.js execution roadmap](nextjs-priority-roadmap.md).
The [real HTTP bridge and CommonJS controls](../../tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/README.md)
subsequently pass the full24 HTTP checks and both browser interactions on Node,
including406 JS modules loaded through the new candidate Module core. Native
Module/Buffer kernels have SDK syntax evidence; FS/ALS are unfinished drafts.
These are additional host/source/frontend results. The historical Wasm failures
below remain unchanged, and a full Next component is still outstanding.

The comprehensive Next.js project works on stock Node, but its full server still
does not compile to a component. The tests below were executed after committing
and pushing `77659217c92019d5471570b937d69f6352cbe4e5`. They exercise accepted
**foundations-v13**, not the unadopted 355/357-source experiments.

Pins: Node22.14.0, Next16.4.5, React/ReactDOM19.3.1, ComponentizeJS0.23.0,
Jco1.40.0, Rolldown1.2.16 and stock Wasmtime42.0.1. Engine `d54446dc…` and
metadata `bfaec95e…` retain342 native inputs and nine selected manifests. The
[fixture and reproduction commands](../../tests/node-compat/frameworks/nextjs/README.md)
include the exact engine hashes, dependency locks and tool paths.

| Executed check | Result |
| --- | --- |
| Two fresh production Next builds, generated standalone servers and assets | Both pass |
| HTTP contracts, including a build-derived Server Action POST | 24/24 pass in each run |
| Cache reuse/invalidation, cookies, headers, dynamic SSR, JSON routes, assets and Suspense | Pass on Node; raw bodies/chunks retained |
| Browser hydration/counter and actual form action | Both interactions pass in both runs; first run has one failed network observation described below |
| Main19-case Wasm attempt, in each run | 16 bundling refusals, one execution failure, two successful explicit-refusal probes |
| Supported native-module supplement | Complete Node, three retained Jco and fresh Wasmtime returns agree |
| Optional ten-case package matrix, in two runs against the same fresh app | Native CommonJS identity, supported modules and React elements pass complete differentials; seven guest failures remain |

The first browser worker exits1 despite functional2/2: it records an aborted
`/actions` POST fetch, `net::ERR_ABORTED`. There are no page/console errors or
timeouts. The unchanged fresh replay exits0 for the browser worker, with both
interactions and all network-error checks passing. The first failed record stays
failed. Existing instrumentation cannot distinguish navigation cancellation from
context teardown; the cause is unresolved. The installed Chrome also changed
from156.0.8078.80 in the historical baseline to156.0.8078.81, so this is not an
identical-browser comparison. Do not attribute this observation to guest Wasm.

The full Next standalone/page/route and package entries stop at the current
bundler/loader/native-module boundary. The main shared application probe builds
a component but fails on deferred `node:util.format`; the separately caught
diagnostic retains `ERR_SM_NODE_UNSUPPORTED`. Explicit imports of filesystem,
crypto, async context, HTTP, networking, URL, process and timers remain refused.
The optional bundler gets real ReactDOM edge into a component, whose execution
still traps at clock subscription without selected clocks. These are separate
failures, not successful Next server execution.

The passing supplement checks Buffer view copying, shared ArrayBuffer/slice
relationships, fresh zeroed allocation, UTF8/hex, events, StringDecoder, path,
query strings, util predicates, assertions, web streams and a classic pipeline.
It excludes the deferred `util.format` call explicitly and does not replace the
original failing shared-source case. Buffer and Node support remain bounded.

All components emitted by these application runs have no imports and a scalar
`run() -> string` export. No guest filesystem, HTTP, socket, entropy or custom
host service is supplied. The full Next server never reaches component
construction. This application run uses Jco and unmodified Wasmtime; it does not
instantiate a Next component in wasmCloud. Separate retained selected-clock
ReactDOM evidence uses only standard WASI0.2.10 clocks/poll interfaces and is
checked separately. Neither component sizes nor operational durations establish
a performance result.

The [compact independent review](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217/independent-review.md)
checks both main runs, their retained streams/terminals and six actual component
import sections. The [first run](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217/results.json)
and its [comparison](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217/comparison.json)
retain the three browser/oracle control flags. The
[untouched replay](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217-replay/results.json)
and [comparison](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217-replay/comparison.json)
have no new regressions or changed Wasm blockers and preserve17 known failures.
The main driver still exits1 because the required shared-source differential
fails; comparator exit0 means unchanged observations, not framework support.

The [supplement](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-post-77659217-supplement/results.json)
and [fresh package matrix](../../tests/node-compat/frameworks/package-bundler-execution-v1/results-post-77659217/results.json)
retain complete results. Comparing that matrix to the historical build exits1
on exactly three generated probe-source mismatches: standalone, page and route.
Its seven failure reasons are unchanged. Fresh Next builds produce new input
bytes; the comparator's exact-source checks remain enforced. Independent
read-only correlation confirms that all three current generated roles match the
fresh Next build's recorded artifacts and actual bytes. The
[same-build replay comparison](../../tests/node-compat/frameworks/package-bundler-execution-v1/results-post-77659217-replay/comparison.json)
exits0, with no regressions or changed blockers and all seven failures retained.
Use the current matrix as the exact-source baseline for this app build; a later
fresh build requires another generated-input review.

Future checks must keep the full Next run, supported supplement, optional matrix
and their separate comparators. The existing comparators retain explicit known
failures and reject incomplete observations, mismatched successful returns,
changed source identities and widened capabilities. Current injected checks
pass43 main and40 package cases; the separate retained-clock checker also passes
its18 semantic negatives and publication-integrity checks. Their
[outputs](../../tests/node-compat/frameworks/nextjs/results/2026-11-06-regression-checks/)
are retained, including a finite check of all16 emitted component occurrences,
their actual bytes, retained empty-import/scalar-WIT records and12 whole-string
cases. This count is not a claim of16 distinct binaries. Review changed blockers or artifact pins before adopting a new
baseline; do not delete failing observations to make a check pass.

Next work is to instrument browser request lifecycle/teardown phases while
retaining abort failures, implement demanded `util.format` semantics, and resolve
the real bundler, loader, request-context and selected WASI HTTP requirements.
Native Hash/Hmac now has separately recorded artifact revalidation, frozen
evidence and component returns; snapshot/ownership/cost/adoption gates remain
open. The Next priority roadmap specifies the required IO, crypto and compression
subset for the next application generation. The complete roadmap is in progress.
