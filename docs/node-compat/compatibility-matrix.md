# Node 22 API compatibility matrix

Current accepted checkpoint: [foundations-v13, bounded classic streams](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

The [Next priority roadmap](nextjs-priority-roadmap.md) now records a passing
experimental full-application smoke milestone. The unmodified **Next 16.4.5 /
React 19.3.1** application passes **24/24 HTTP, cache generation 1 → 2, five
incremental Suspense chunks and 2/2 browser interactions** on stock Wasmtime
42.0.1 with reuse 128 and idle timeout 60 seconds. The same hydration-aware
browser worker, whole 20-second limits and strict zero-error gates also pass on
the matched stock Node 22.14.0 control. See the
[current milestone report](nextjs-wasm-milestone-2026-11-06.md). Portable
[native](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
and [matched Node](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-stock-v1-review/README.md)
reviews preserve the raw evidence and DATA checks.

This result uses component `55f05e3d…`, native engine `4623640b…`, raw entry V4
and six bounded guest facades. Its thirteen emitted standard imports are all
WASI 0.2.10, with the incoming-handler export. Server JavaScript runs in embedded
SpiderMonkey/Wasm; client JavaScript runs in the browser. No JavaScript AOT,
client-Wasm, complete Node/Buffer compatibility or production promotion follows.
The accepted foundations-v13 checkpoint and its machine-readable API statuses
remain unchanged.

| Experimental API/language gate | Strategy and capability | Current status and deviation | Validation |
| --- | --- | --- | --- |
| Node `global` alias | Pure guest entry facade; no additional host capability | Bounded exact self-alias descriptor; other Node globals retain separate contracts | Pinned Node descriptor/private-realm tests and successful full Next smoke |
| CommonJS JS/JSON, aliases and demanded Buffer operations | Native loader/P2 reads and native byte kernels; bounded Buffer view facade | Native UTF-16 Module compilation fixes the Unicode source discrepancy without a Function fallback. Broader Buffer/loader semantics remain partial | 48 dependency records and full 24/24 HTTP plus 2/2 browser smoke; exact decoded static assets match source |
| ALS await, ticks, timers, bind/snapshot | Native Promise/task context propagation | Selected cross-owner, disable/capture and ordinary-call unref continuity work. Actual overlapping HTTP, broader ref/unref semantics, GC and teardown depth remain open | Five logical-branch controls pass459 native assertions; [three-call unref control](../../tests/node-compat/async-context/unref-reuse-root-results-v1/actual-review/README.md) passes51 call checks plus9 distinct callback checks. Public Node projections do not prove native owner/enable bits or physical Store identity |
| AsyncResource | Small CJS-default guest facade over native ALS.snapshot | Only constructor(string/no options) and runInAsyncScope selected; IDs, hooks, emitDestroy, bind and named ESM rebinding remain deferred | 16 host cases plus the app's actual asset/action path in the passing component |
| WASI request-body EOF and classic body conversion | Typed ComponentError.payload handling plus bounded classic Readable conversion | Unknown errors remain failures; body/resource ownership has explicit limits | GET/GET/POST dependency controls, JSON POST and real Server Actions pass |
| Request signal and peer-disconnect cleanup | Standard WASI I/O error observation plus guest adapter; no independent disconnect capability | Isolated V3 adapter passes abort/handled-close checks. Full candidate1c3108d2 integrates it and passes24HTTP plus cold8, but its strict browser gate fails on an actionPOST abort/body capture. Fully passing55f05 retains its original policy. Idle disconnect, trailers and native counts/teardown remain open | [Isolated V3](../../tests/node-compat/frameworks/nextjs/peer-disconnect-root-results-v3/actual-review/README.md) raw0 is separate from the [full V5 failure](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/full-next-io-v5-first-review/README.md). No physical Store identity or complete Node compatibility follows |
| Unicode property regex and ignore-case | Native SpiderMonkey with coherent patched Intl/ICU/ICU4X; no new host interface | Selected Unicode expressions supported; no full RegExp conformance claim | Strict 12-case differential passes all 36 records, including Kelvin folding and invalid-property controls |
| Error.captureStackTrace and selected CallSite methods | Native SavedFrames, bounded guest facade and explicit guest-SM provenance API | Lazy hooks and exact send/depd extraction work. Three anonymous function-name type differences remain; eval-origin/receivers/native/async flags defer | Strict stack suite remains failed at 9/12; native UTF-16 app loading preserves genuine provenance and the full app smoke passes |
| ReadableStream.pipeTo with AbortSignal | Audited guest facade over real native readers/writers and protected abort listeners | Measured Next paths and twelve selected ordinary controls work. Private disturbed/queued-close state and signal pipeThrough limits remain; the C++ signal path is not replaced | 31 host cases plus [36 exact actual guest/Node records](../../tests/node-compat/frameworks/nextjs/native-pipe-root-results-v1/README.md), actual JSON/actions and five-chunk Suspense; no app signal removal or teardown-count claim |
| fs.createReadStream send options | Bounded option facade over native WASI FS/streams | Send's irrelevant options normalized while real FS checks remain; general FS parity is not claimed | Public asset, nine decoded script responses against five source files, full HTTP/browser and cache smoke pass |

The passing generation retains the coherent patched Intl build's 80 native
compile rows and separate embedding as ancestry, then freshly compiles one
UTF-16 Module unit and relinks. The
[actual incremental build review](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-root-results-v1/actual-review/README.md)
keeps the new metadata kind, immutable baseline, archive/core checks and input
protections distinct; no eighty-fresh-frontend claim is made. The
[Intl build plan](nextjs-intl-build-plan.md) and
[earlier runtime baseline](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/actual-review/README.md)
retain the language/stack gates and original failures.

The prior 11/24, 0/23 and 22/24 runs remain failures. The pre-hydration V4 browser
clicked before its client scripts arrived; the new version-bounded readiness
observer checks own data properties without invoking handlers, then performs
the same real clicks. It preserves the 20-second limit and zero-error gates.
Nine decoded script captures match the unchanged app files; the tenth captured
body is the actual POST RSC response, not a tenth script. Encoded byte counts
are recorded separately and do not establish compressed-wire hashes.

Current work is reproducible retained-artifact runs, deeper native stream/context
and cleanup regressions, exact production-selection review, and measurements.
Re-snapshot/reset safety, broad API compatibility and portable clean-machine
bootstrap remain open. Pinned wasmCloud 2.11.0 P2 HTTP makes a fresh store/instance
per request, so its retained-server/cache contract is not accepted; its P3 pool
settings do not change that P2 lifetime. A separate [eight-request cold contract](../../tests/node-compat/frameworks/nextjs/wasmcloud-cold-candidate-v2/README.md)
now passes on that stock host with the same55f05 component and all13 imports:
health×3, SSR, JSON POST, filesystem/SHA, asset and strict streaming; both CLI
commands and parent exit0 with input/ownership checks intact. No retained cache
or browser assertions ran there. The earlier premature-readiness eight host404s
remain failed observations. No host changes or interface widening
are used to manufacture reuse. The successful Wasmtime smoke remains scoped to
its explicit reuse configuration. App mode 0444/0555 and a separate writable
cache do not prove read-only rights on the actual WASI preopen descriptor.

The [optional package-bundler follow-on](../../tests/node-compat/frameworks/package-bundler-execution-v1/README.md)
runs native CommonJS interop, supported modules and real React creation with
complete Node/Jco/Wasmtime agreement. Its pure-profile ReactDOM clock trap
remains the original baseline. A separate selected-clock component passes its
artifact/type graph review, a first Wasmtime render and a seven-return
Jco/Wasmtime differential at raw0, with independent actual-result review passed.
Guarded secret355 component/runtime and three fresh stock-host validations pass
independent review. These experimental results do not implement Node crypto or
promote new API statuses; foundations-v13 remains accepted.

The earlier [Next.js application experiment](../../tests/node-compat/frameworks/nextjs/README.md)
recorded two real Node production builds,24 HTTP and two browser checks per run,
and19 isolated Wasm attempts. Those full Next/React entries failed at the CommonJS
bundler boundary; eight unavailable Node module imports refuse explicitly. The
shared application function builds a zero-import component but fails on deferred
`util.format`; a caught-error diagnostic identifies that refusal. A separate
supported Buffer/foundations/web/classic-stream fixture returns complete
Node-equal values on Jco and fresh Wasmtime. These findings add repeatable
regression checks and demand priorities, not complete Next.js compatibility or
new API support.

Latest experimental evidence and remaining gates are recorded in
[progress.md](../../progress.md). The reviewed codec cost workload does not
establish universal speed or lower guest memory. Native combined355 build/freeze
passes, validation-only export/bootstrap and retained read-only API checks now
precede five accepted component constructions and one identified, unaccepted INIT
timer refusal. The pure component imports nothing; clock/resource components
select only three standard WASI0.2.10 clock/poll interfaces. A separate pure
control returns seven whole Node-equal Jco/Wasmtime strings at raw0, with
independent runtime DATA review passed. The separate ordinary resource suite also
passes independent review:35 public strings/49 cases/98 callback observations/322
per-instance timer IDs on retained/fresh Jco and stock Wasmtime. This is web timer
behavior, without Node Timeout-object parity, native cleanup proof or a public
`node:timers` implementation. Clock-snapshot and surviving-job seven-return
suites also pass independent review, without an epoch/native offset/cleanup claim.
Fatal observation remains unaccepted because the source-specific diagnostic is
missing; native lifecycle and operational adoption remain open.
The default-OFF Hash/Hmac candidate has compiled and linked, with independent
review of its complete83-field metadata and retained failed wrapper protection.
Its two zero-import components now pass fourteen retained/fresh Jco and stock
Wasmtime returns,280 accepted Node-record comparisons and112 separate native
policy checks. The first reporting-counter bug is preserved; corrected runs
have truthful counters. Direct native aliases share functions/default objects
and retain separate namespace objects, a Node deviation. Its1,893-file freeze
and frozen-only verifier finish0, with independent frozen-artifact review passed.
Lifecycle/cost and release gates remain open. The candidate
is unadopted, and accepted production's `node:crypto` API status remains deferred.
The60-observation host Node oracle stays separate. The experimental clock and guarded-key results remain
separate from public API compatibility; exact evidence is in the
[execution status](execution-status.md).

The separate private clock diagnostic357/82 generation now links at
recipe0/wrapper0 after independent Source/stage review. Its actual-build review
passes; new component/runtime checks remain unissued. Private diagnostics add no
public Node API support and admit no new profile.

The machine-readable [API matrix](api-matrix.csv) is the per-API record: each row has module, API, type, inventory origin, status, implementation strategy, required capability, deviation and validation plan. [Node export inventory](node-v22.14.0-exports.json) contains the exact 72 module namespaces obtained from Node v22.14.0 on macOS arm64. [Policy](policy.json) defines dispositions and overrides; [generator](scripts/inventory.mjs) checks the oracle version and documentation hash. Documented overload/event/property records supplement reflection and can duplicate reflected API records.

The [inventory correction record](inventory-correction-results.json) verifies
6,795 evidence rows with all 4,132 reflection/CommonJS rows unchanged. JSON parser
labels `Type`/`return` are resolved to declared property names, and non-module
chapters (`errors`, `esm`, `permissions`, `n-api`) are recorded as exclusions
rather than invented builtin IDs. Run `scripts/inventory-test.mjs` against the
same pinned API JSON to check these regressions. Current implementation work is
tracked separately in the [execution ledger](execution-status.md).

Statuses describe the **proposed profile contract**, not checkout-wide implemented Node support:

| Status | Meaning |
| --- | --- |
| supported | A precisely listed semantic-template operation/constant; actual execution coverage is identified separately. Native integration still requires compilation. |
| partial | Only specified overloads/semantics; all deviations are part of the contract. |
| import-only | Module/default/constructor name can be imported and inspected, but its unavailable operations throw. This is not operational support. |
| deferred | Not part of this milestone. Unregistered module IDs fail imports; no implicit empty module or fallback host adapter. |
| unavailable | Cannot operate with the selected profile/capabilities or is deliberately excluded. Only explicitly installed manifests are importable. |

Every CSV row also says that production checkout integration is not implemented by this deliverable. Existing native **web** APIs are distinguished from Node-facing module parity. An unavailable module is not automatically an import-only stub: only the chosen `child_process` manifest and the finite Buffer namespace are supplied in this milestone.

## Current implemented overlay

The CSV and the following initial-contract tables preserve the original audit.
Current bounded implementation evidence is separate:

The latest accepted overlay is [foundations-v13](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md), adding the bounded corrected classic-stream layer to its reviewed v12 parent. The original audit tables below retain their initial contract. Getter/Symbol parity, combined GC owners and reset/reuse remain limits.

The original classic342 artifacts retain their bounded suites, replay/followon and same-byte HTTP evidence:40+20+15+1 component occurrences, without a global binary-uniqueness claim. Fourteen host-model trace differences and six actual minimal Node differences remain preserved counterexamples; old passes do not validate a changed source generation.

The [corrected source generation](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
retains four reviewed production freezes, 474 files each, and its reviewed
26-file runtime family with 6,414 consumed inputs and 22 tool links. The three
[corrected classic suites](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-classic-runtime-root-results-v1.json)
finish at Root-observed exit 0, publishing 90/91/90 files and 15 component
occurrences. OFF/GC import nothing; RuntimeOnly imports only
`wasi:random/random@0.2.10`. The [independent all-four result review](../../tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md),
index `8c3da4a2…41e8cc`, passes 19 ordinary groups, 48 deferred call/new cases,
17 overload refusals, three limits and 65 initializer failures per enabled suite,
plus retained/fresh state and failure controls. Disabled OFF passes eight
ESM/static-CJS denials without a component. The separately reviewed Node11 gate
adds one zero-import component occurrence. Main and successful clean-control
Wasmtime stdout bytes were not retained: the review checks parsed observations
and stdout hashes, not an independent decode of those missing streams. Fatal
raw streams are checked; generic traps do not identify error origin. GC covers
combined owners only. Original source/native packets and counterexamples stay
unchanged.

Diagnostic producer-v3 has successful [ON](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-on-native-root-results.json)
and [OFF](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-off-native-root-results.json)
build/freeze/read-only checks, each at exit 0 with 109 build steps and 525 frozen
files. Independent native reviews [ON `c05afb8d…`](../../tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-on-native-review-v1/README.md)
and [OFF `ca2debb8…`](../../tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-off-native-review-v1/README.md)
pass. Root's separate [ON-only pins](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-on-pins.json)
(`2e9811a5…`) and [authority](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-on-root-review-receipt.json)
(`9681578e…`) do not constitute a measurement pair.
The [correctness companion138a](../../tests/node-compat/foundation-classic-streams/measurement-correctness-candidate-v1/README.md),
mandatory [reporting amendment0558](../../tests/node-compat/foundation-classic-streams/measurement-correctness-reporting-amendment-v1/README.md)
and [source review c695](../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-source-review-v1/README.md)
remain bound to the [ce2f activator](../../tests/node-compat/foundation-classic-streams/measurement-correctness-activation-candidate-v1/README.md)
(19 files/6,908 inputs, 27 Root source checks and [peer ee4d5](../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-activation-source-review-v1/README.md)).
[Source activation and artifact preflight](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/correctness-source-activation-and-preflight-root-results.json)
pass, creating family `4728c365…f33f49` (21 files/7,489 inputs), whose
[generated-family review634077e4](../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-family-review-v1/README.md) passes.

The [first full 20-workload/14-boundary attempt](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-timeout-attempt1-root-results.json)
(`e8165564…`, session90660) exits 1 after a 55-second Wasmtime child timeout.
It publishes no final result, completion or semantic counterexample. The
original timed-out case is unknown; unretained Jco observations cannot count as
passes. The [independent failure review c5a0a80f](../../tests/node-compat/foundation-classic-streams/independent-workload-timeout-failure-review-v1/README.md)
passes within that evidence scope. Separate fresh case0 Jco and Wasmtime
controls match the full Node oracle. A [separate fresh case5 control](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-public-case5-root-results.json)
(`793a2f0d…`, session16818) returns child exit 0 after 177.338 operational seconds
under a 600-second cap; its complete trace, setup and checksum equal Node case5.
This proves neither the original timeout's case/cause nor deadline adequacy for
all cases or a performance result. The original failure remains unchanged.

The [persistence amendment60a8687e](../../tests/node-compat/foundation-classic-streams/measurement-correctness-persistence-amendment-v1/README.md)
and [peer6fb6](../../tests/node-compat/foundation-classic-streams/independent-correctness-persistence-source-review-v1/README.md)
lead through the reviewed v2 activator to [source418ff8fe](../../tests/node-compat/foundation-classic-streams/measurement-correctness-activated-v2/README.md)
(22 files/7,542 inputs; [family peer c30b596a](../../tests/node-compat/foundation-classic-streams/independent-correctness-v2-family-review-v1/README.md)).
The [fresh full v2 run](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-workload-v2-root-results.json)
finishes at Root-observed raw exit0 (session66794, receipt `6218afd5…`).
[Independent result review0f59a0da](../../tests/node-compat/foundation-classic-streams/independent-workload-v2-results-review-v1/README.md)
passes: all105 returned records match the complete original20 Node workload
rows and14 boundary observations, across three retained Jco rotations, fresh
Jco and21 fresh Wasmtime calls. All21 raw Wasmtime streams independently
double-decode exactly;632 completion files and final source/native/tool seals
are checked. Component29c7d954… is12,977,999 bytes with zero imports and two
public scalar exports. No old result is resumed or reused. The ON-only
diagnostic authority stays separate from production and measurement-pair
authority. scheduledCallbacks is the original workload counter; native queue/
work/empty counters are unavailable. This finite pass claims no performance,
GC/root isolation, reset/ALS, request reuse or full Node/Streams compatibility.

The separate [measurement-execution source4b6fdfa5](../../tests/node-compat/foundation-classic-streams/measurement-execution-candidate-v1/README.md)
has 43 files/7,004 inputs. [Independent review96bc44a3](../../tests/node-compat/foundation-classic-streams/independent-measurement-execution-source-review-v1/README.md)
requires mandatory M1 deadline/capture fixes and permits no activation. A
[new amendment](../../tests/node-compat/foundation-classic-streams/measurement-execution-deadline-amendment-v1/README.md) is sealed at index `b0975b54…` (25 files/7,112 inputs), with 36 source/reversal,
18 pure deadline and11 syntax checks. Its [independent source review9e602ec9](../../tests/node-compat/foundation-classic-streams/independent-measurement-execution-deadline-source-review-v1/README.md)
passes. A separate Root review now authenticates both actual diagnostic variants.
The [new source family and both preflights](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-source-and-preflights-root-results.json)
pass at Root-observed exit0 (69131/24691): index1b801439… has35 files/7,709 inputs.
[Independent family review4e986ca1](../../tests/node-compat/foundation-classic-streams/independent-common-byte-v2-family-review-v1/README.md) passes.
The [four-arm attempt25227](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json) finishes at raw exit1 in the
host stock graph checker before stock componentization. The inventory has no
`provider` field; its three original guest paths are explicit sourceBeforeAfter
rows. Native-on, canonical-on and canonical-off completed their full arms.
[Independent reviewbf9fa2a6](../../tests/node-compat/foundation-classic-streams/independent-common-byte-v2-three-arm-failure-review-v1/README.md) verifies231 durable observations against
all14 Node oracles, identity/probes, raw calls and final source closure. A new
[stock-only correction and composition source](../../tests/node-compat/foundation-classic-streams/measurement-stock-composition-candidate-v1/README.md) passes
[independent reviewddbbe2a7](../../tests/node-compat/foundation-classic-streams/independent-stock-graph-composition-source-review-v1/README.md). Root source checks pass; a separate
[three-arm authorityafdbc0bc](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-common-byte-three-arms-for-stock-only-v1.json) permits fresh stock execution.
[Stock run91122](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-stock-only-root-results-v1.json) and [composition12839](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composition-root-results-v1.json) finish
at exit0. [Independent actual reviewab100c83](../../tests/node-compat/foundation-classic-streams/independent-common-byte-stock-and-composition-results-review-v1/README.md) verifies all308
observations against14 Node cases, exact raw calls, component/graph data and
each arm origin. Both required actual-proof documents are indexed. Original
source1b801, arm records and parent exit1 stay unchanged; this is new composed
evidence, not a pass for the original failed run. Timing was still disabled at that preparation checkpoint. Future
authority templates stay NULL; no external timing phase or timing result exists.

The [corrected replay producer8851](../../tests/node-compat/foundation-classic-streams/trace-replay-activation-candidate-v1/README.md)
passes [source review c373](../../tests/node-compat/foundation-classic-streams/independent-trace-replay-activation-source-review-v1/README.md)
and its source activation creates [family a08aec2d](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-source-activation-root-results.json)
with 83 files and 2,293/2,292 root/capability inputs; [generated-family review8529](../../tests/node-compat/foundation-classic-streams/independent-trace-replay-family-review-v1/README.md) passes.
Root's [preflight environment failure](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflight-attempt1-root-env-failure.json)
is preserved: native OFF/RuntimeOnly/GC pass, then Release OFF lacks the required
explicit `NODE_COMPAT_WASMTIME`. The [corrected-environment retry and combined preflights](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflights-root-results.json)
pass without source/native changes or a guest in those preflight attempts.
The [fresh eight-stage replay](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-release-replay-root-results.json)
then passes at Root-observed exit 0, covering six optional foundations and 40
component occurrences, including one fresh historical control. All import
nothing. Five allocator-GC/focused/getter follow-ons also pass, with
[20 component import audits](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-followon-imports-root-results.json):
only the eight RuntimeOnly components import standard random@0.2.10.
Independent [replay6a67](../../tests/node-compat/foundation-classic-streams/independent-corrected-replay-results-review-v1/README.md)
and [follow-on d116](../../tests/node-compat/foundation-classic-streams/independent-corrected-followon-results-review-v1/README.md)
result reviews pass, including source/native/tool/completion seals and control
origins. These are occurrences, not globally unique binaries. Replay retains
eight fatal raw streams and one independently decoded alias return; 30 other
Wasmtime records have parsed-only or digest-only evidence. Follow-on allocator
GC has a parsed observation without raw stdout or digest; getter Node/Jco values
are parsed-only, while its Wasmtime return independently decodes. Getter/Symbol
parity remains false, GC covers combined owners and failed instances are discarded.

The [corrected HTTP source and whole-entry bundle](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-source-and-bundle-root-results.json)
pass with17 expected imports and no bundled JS built-in adapters. The
[first packaging attempt](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-packaging-attempt1-root-env-failure.json)
retains prepared inputs; build stderr asserts missing `NODE_COMPAT_WASM_TOOLS`
before output creation. Its outer terminal status was lost to context and is
not inferred. The [fresh same-input buildv2 and packaging audit](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-package-root-results.json) finish at Root-observed raw0
(session71459, explicit tool): component24d76605… is64,058,731 bytes, with the
17-import application bundle and exact six standard WASI0.2.10 interfaces;
monotonic-clock duration is type-only, with no callable clock. Production
admission completion exists; the collector verifies25 artifact references and
the7,496-input closure, including a fresh static WIT audit. The
[fresh combined host result](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-combined-root-results.json)
finishes at Root-observed raw0 for Wasmtime, wash and audit (session60088).
Both hosts return three successful responses and stop at exit0 on identical
component24d76605 bytes. [Independent result review2f5df929](../../tests/node-compat/foundation-classic-streams/independent-corrected-http-results-review-v1/README.md)
passes all six bodies and source/native/tool/configuration evidence. Counters
are1/1/1 on each host; no instance reuse or request isolation is inferred.
Measurement is complete; targeted memory/startup, artifact/archive and acceptance remain incomplete; bounded
v12 stays accepted and the roadmap is unfinished.
The completed [measurement](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json) finishes raw0:42 calibration/126 timed workers plus final source audit,1,037 output files. [Integrity review3843d019](../../tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and the [numerical analysis](classic-stream-measurement-v1/README.md) are separate evidence. The [Root strategy decision](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the shared guest-JS stream state machine and native byte primitives; registered imports avoid a duplicate bundle and save7.85% measured component bytes, with no consistent same-engine warm-speed or memory advantage. The optional unused installation stays OFF. Stock-provider differences include a different provider/scheduler; FNV/validation stays timed and controls are not subtracted. Public RSS includes proof/V8 overhead, and raw timing-call compact returns were not retained. The smaller-worker [process RSS supplement](../../tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v1/README.md) passed source review, but the [actual attempt](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v1-preworker-failure-root-results.json) exits1 before any worker: setup is signed32, while the probe expected strings. The corrected [v2 source](../../tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v2/README.md) passes independent review; the [actual v2 run](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-root-results.json) finishes raw0 with18 fresh workers,126 retained typed returns,599 files and final source audit. [Independent result/numerical review](../../tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md) passes all18 workers/126 typed returns; same-engine pre-final maximum RSS ratios cross1 and no controls are subtracted. It excludes full proof reports from workers and retains public raw returns. No private heap or production-engine performance claim follows.

Historical failures/counterexamples remain unchanged. The61-case [zlib corpus
and harness a7eca234](../../tests/node-compat/foundation-zlib/component-validation-candidate-v1/README.md) and
[control-evidence amendment fd3ec6ef](../../tests/node-compat/foundation-zlib/component-validation-control-evidence-amendment-v1/README.md)
retain the [240fdc77 source hold](../../tests/node-compat/foundation-zlib/independent-component-validation-source-review-v1/README.md).
The new [bootstrap/coverage amendment a376c32b](../../tests/node-compat/foundation-zlib/component-validation-bootstrap-coverage-amendment-v1/README.md)
(15 files/8,640 inputs) addresses the call-counter, native error-field-type and
repeated-namespace identity gaps and rebinds producer v3. Its [independent source
review654f077f](../../tests/node-compat/foundation-zlib/independent-component-validation-coverage-source-review-v1/README.md)
passes. The [v4 publisher rebindcd458](../../tests/node-compat/foundation-zlib/component-validation-v4-rebind-amendment-v1/README.md)
(8 files/8,770 inputs, nine publisher edits) passes [independent review74109e3f](../../tests/node-compat/foundation-zlib/independent-component-validation-v4-rebind-source-review-v1/README.md).
The a376 payload stays exact:61 Node cases,28 full-byte fixtures,40 bindings and
107 typed constants. Separate [Root validation-only pinsb61e1f38](../../tests/node-compat/foundation-zlib/reviewed-native-v4-validation-bootstrap-pins-v1.json)
and [review7274a874](../../tests/node-compat/foundation-zlib/native-v4-validation-bootstrap-root-review-v1.json) bind the three actual native variants; the
normal production selector stays closed. The first activation wrapper omitted
required arguments and stopped before publication. The corrected-argument
[attempt49004](../../tests/node-compat/foundation-zlib/validation-source-activation-attempt2-context-failure-root-results.json) then stops at a historical preparation-path
collection error; no source family or guest is published. A [context-only
amendmentf6f0e191](../../tests/node-compat/foundation-zlib/component-validation-preparation-context-amendment-v1/README.md) is sealed, but [review541b2779](../../tests/node-compat/foundation-zlib/independent-component-validation-preparation-context-source-review-v1/README.md) holds it on ZVCTX-M2:
the publisher treats an indexed-only peer as a preparation family and reads a
manifest that does not exist. The [Root origin correction](../../tests/node-compat/foundation-zlib/validation-source-activation-attempt2-root-origin-correction.json)
retains the original diagnosis and records this earlier observed failure; the
later relocated-bootstrap-path issue is independently confirmed. A new publisher
correction now distinguishes those family roles explicitly. The [indexed-peer successorbd66](../../tests/node-compat/foundation-zlib/component-validation-indexed-peer-amendment-v1/README.md) and [postseal inventory evidence5aa0](../../tests/node-compat/foundation-zlib/component-validation-indexed-peer-regression-evidence-v1/index.json) pass [independent source review6cbe](../../tests/node-compat/foundation-zlib/independent-component-validation-indexed-peer-source-review-v1/README.md): all8,904 inventory rows agree, required preparation manifests remain mandatory, and the indexed-only peer requires all five indexed files. Root [source activation-v3](../../tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) finishes raw0 and publishes family8868d212 (19 files/10,964 consumed inputs). Its [generated-family review999df5f8](../../tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) holds on ZV6-M1: four component-harness loaders are physically absent from the native stage and omitted from the consumed manifest. The [tooling successor daa7d28a](../../tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) now passes [source review567c3214](../../tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) and Root22 physical/source checks plus six syntax commands. [Activation-v4](../../tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0, publishing v7/d67971d0 (21 files/11,036 inputs). Its native configured root and fully sealed component-tool root are distinct. [Generated-family review178ab2d0](../../tests/node-compat/foundation-zlib/independent-component-validation-v7-family-review-v1/README.md) passes. The [first normal codec attempt](../../tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) then finishes raw1 during componentization: its snapshot uses unsupported Buffer.from(Array). No component, final result or deployed codec observation is published; the failure source recheck passes. The same input kind also occurs in constructor-refusal arguments and the ordinary-GC fixture. The [three-expression Uint8Array amendment b0ced580](../../tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) passes12 Root host-only regression checks using explicit test doubles and [independent source reviewc277823a](../../tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md). [Fresh source activation-v5](../../tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0 and publishes corrected v8/8af9a213 (21 files/11,107 inputs). [Generated-family review1e966afe](../../tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md) passes. [Normal validation-v2](../../tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile codec observations over61 cases and1,544 completion artifacts. [GC validation-v1](../../tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) finishes raw0 with three codec cases, combined-owner ordinary-GC and fresh Wasmtime checks,49 completion artifacts. Both components import nothing. [Independent normal reviewa36758db](../../tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC review461dec9c](../../tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) pass. The [combined Root result review](../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 Node/profile error-case differences (16 outcome/code, six additional errno-only), including11 originally unlabelled rows. The [per-case difference ledger](../../tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/node-profile-difference-ledger.json) binds exact oracle/raw citations; no61-case Node parity is claimed. Source-coupled public VERNUM evidence does not rewrite metadata backend proof; operational admission remains closed. Separately, [actual disabled validation](../../tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0 with eight pre-componentization denials, five Buffer/stub observations and imports[]; [independent result review5b199668](../../tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) passes. This does not prove codec support or a unique cause for its generic direct-import rejection. The guest, driver, Node fixtures and native evidence remain unchanged.

The [independent timing-input review372256](../../tests/node-compat/foundation-classic-streams/independent-composed-timing-inputs-review-v1/README.md) passes all non-authority data checks for the unapproved timing candidate and four Root prerequisite reviews. The three issuance gates remain closed: candidate state, timingAllowed:false and NOT_ISSUED quiet window. No timing has run.

The [conditional integration56a6](../../tests/node-compat/foundation-zlib/integration-candidate-v1/README.md)
and [SDK syntax evidence e757/peer4ef](../../tests/node-compat/foundation-zlib/independent-sdk-syntax-review-v1/README.md)
remain bounded source/syntax evidence:350 proposed native paths, two syntax
commands and1,048 dependency files (2 CPP+1,046 headers), with static `MOZ_Z_*`
mapping. Old [3ff/dafaff Z350-M1](../../tests/node-compat/foundation-zlib/independent-native-integration-source-review-v1/README.md)
and [c65/89bc Z350-M2](../../tests/node-compat/foundation-zlib/independent-native-integration-v2-source-review-v1/README.md)
holds remain unchanged. The [two-identifier correction c92e](../../tests/node-compat/foundation-zlib/descriptor-shadow-amendment-v1/README.md)
and [producer v3 index3929e24d](../../tests/node-compat/foundation-zlib/native-integration-candidate-v3/README.md)
(81 files/2,146 inputs) pass [source reviewf471ec27](../../tests/node-compat/foundation-zlib/independent-native-integration-v3-source-review-v1/README.md).
[Root's eight source checks and isolated staging](../../tests/node-compat/foundation-zlib/native-integration-v3-root-stage-results.json)
pass (76544/964346f9), followed by [actual stage reviewc75f3484](../../tests/node-compat/foundation-zlib/independent-native-integration-v3-stage-review-v1/README.md):
869 exact copied rows =350 native+522 tooling−3 overlaps, plus the exact proposal
and isolated Git54b base. Original preparation context is retained.

The first ordinary Release normal-OFF attempt (Root62113) finishes at raw exit1.
It reaches the final108/108 copy entry and then postbuild evidence collection.
The actual CMake chain has one compiler `-o` and another for `wasm-opt`;
`codec.link_commands` counts both across the compound line and asserts. The
[Root failure receipt accf4b05](../../tests/node-compat/foundation-zlib/native-integration-v3-build-attempt1-failure-root-results.json)
retains11 references, recipe/launcher exit1 and completed cleanup. No standalone
CMake exit receipt was captured. The [independent failure reviewc319](../../tests/node-compat/foundation-zlib/independent-native-zlib-v3-build-failure-review-v1/README.md)
and [Root label clarification](../../tests/node-compat/foundation-zlib/native-integration-v3-build-failure-labels-root-clarification.json)
retain that distinction. Raw v3 engine62d8e6d8… remains unchanged and UNADMITTED
at9,995,287 bytes, with no metadata sidecar, freeze or backend/runtime proof.

The [v4 source d384af81](../../tests/node-compat/foundation-zlib/native-integration-candidate-v4/README.md)
(85 files/2,261 preparation inputs) passes [source review31d5408e](../../tests/node-compat/foundation-zlib/independent-native-integration-v4-source-review-v1/README.md).
[Root checks and staging](../../tests/node-compat/foundation-zlib/native-integration-v4-root-stage-results.json)
record nine source-check commands at0 (34385/42f14b), then plan/apply, staged
verification, factory and Git checks at0 (89971). The [independent actual-stage
review5d857788](../../tests/node-compat/foundation-zlib/independent-native-integration-v4-stage-review-v1/README.md)
passes:979 exact copies=350 native+632 tooling−3 overlaps,85 proposal files plus
index, ordinary Git54b clone and original-context preparation references.

The one-job ordinary Release normal-OFF retry finishes at exit0 (Root69972) from
`/tmp/starling-node-compat/zlib-source-v4`, with fresh `zlib-v4-build` and
`production-zlib-v4` namespaces and2GiB start/800MiB stop guards, without
DEBUG/OOM. The separate [four-file cache preseed47668](../../tests/node-compat/foundation-zlib/native-integration-v4-cache-preseed-root-results.json)
contains only three archive downloads and cbindgen; no engine, configuration,
source or old proof was copied. [Build, freeze and verification](../../tests/node-compat/foundation-zlib/native-integration-v4-normal-off-root-results.json)
finish at Root-observed exit0 (69972/30705/85956). Engine fb165689… is9,995,295
bytes; all1,024 frozen copies and1,022 original references rehash. The actual
350-source build records62 native units, four strict, six private and one separate
embedding command. [Independent ordinary native reviewba0451db](../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-normal-off-review-v1/README.md) passes.
The [GC variant](../../tests/node-compat/foundation-zlib/native-integration-v4-gc-off-root-results.json) also finishes build/freeze/verification at exit0
(44299/71826/23840). All ordinary frozen
copies remain unchanged after the expected shared build-cache reconfiguration.
[Independent GC review90e9e6e3](../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-gc-off-review-v1/README.md) passes. The [disabled variant](../../tests/node-compat/foundation-zlib/native-integration-v4-disabled-off-root-results.json)
also finishes build/freeze/verification at exit0 (66192/28710/63712), and
[independent reviewac8d15ac](../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-disabled-off-review-v1/README.md) confirms its61 native/five private
commands and kernel omission. All three frozen sets remain intact. Runtime backend proof
remains false/null/null; checked-in future pins stay NULL, while the external
Root authority permits validation only. The later [bounded runtime results](../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) now include normal codec, combined-owner GC and disabled-control components with independent reviews. Operational admission, explicit Node differences, matched codec costs and new-engine selected-host/release gates remain open. Historical host/ECHO vectors and syntax remain separate evidence; metadata backend-proof fields stay false. Complete `node:zlib` support is not claimed.

The [installed stream/web supplement](../../tests/node-compat/foundation-stream-web/installed-matrix-v9.README.md)
adds per-export/member records for the current m0.9 bridge:18 exports,184 Node-own
member observations and eight semantic operations. It distinguishes unavailable
properties, deferred calls and unverified target presence/behavior; private
nonregistry symbol descriptions remain reflection observations. The original
audit inventory and accepted v9 freeze are unchanged.

| APIs | Current status/strategy | Capability | Executed evidence and limits |
| --- | --- | --- | --- |
| `node:buffer` selected `Buffer` overloads, view/accessor methods and numeric constants | Partial; compiled guest C++ hex kernel plus audited JS semantics and existing native web UTF8 codecs | None | [Accepted v11 core](../../tests/node-compat/milestones/foundations-v11/reports/release-core.json) covers 381 string/250 byte vectors and aliases/default/global with m0.11; the [allocator GC gate](../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json) is separately bounded. Four genuine native kernel OOM scopes remain tied to [allocation-r2](../../tests/node-compat/milestones/allocation-r2/README.md), not inferred for new engines. Shared/cross-realm and complete Buffer support are excluded |
| `Buffer.allocUnsafe(size)` and hardened core refusal errors | Partial; accepted core m0.11 JS facade over captured native Uint8Array, with release and moving-GC gates | None | [Installed v11 evidence](../../tests/node-compat/milestones/foundations-v11/reports/release-allocator.json) and [GC supplement](../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json). Primitive finite raw size 0..16MiB; fractions truncate, fresh zeroed exact backing/no pool after unchanged validation. Ten differential/five policy groups, 240 refusal checks per call, eleven initialization failures and actual old-profile controls. All91 prototype refusals and five other static refusals remain. No new exports, C++ allocation kernel, genuine OOM or accepted production performance result. Historical [v8 measurements](../../tests/node-compat/foundation-alloc-unsafe/matched/measurement-v1/README.md) retain the slowdown versus Jco; the private direct-U8 pair retains RSS/capacity/size counterexamples |
| `node:child_process`: all nine named callables plus default | Import-only finite real ESM bindings | None | Same manifest/checkpoint. Every call/new throws identifiable `ERR_SM_NODE_UNSUPPORTED`, including initialization; namespace inspection stays safe |
| `node:path`, `/posix`, `/win32`: all 18 exports per namespace, 13 callable lexical/glob operations | Partial; registered guest module with JS lexical algorithms and bounded patched matcher, not a C++ path kernel | None | [Manifest](../../builtins/node-compat/export-manifest.path.node-v22.14.0.json), [v11 replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-path.json). 15,696 lexical/4,046 glob vectors and six first-deployed aliases pass Jco/Wasmtime. Fixed cwd/POSIX/case policy and explicit budgets remain deviations |
| `node:events`: bounded EventEmitter, static helpers and `addAbortListener`; exactly 16 exports | Partial; guest JS state machine with protected native AbortSignal integration | None | [V11 m0.10 replay](../../tests/node-compat/milestones/foundations-v11/reports/focusedOff.json) and [RuntimeOnly](../../tests/node-compat/milestones/foundations-v11/reports/focusedRuntime.json): 29 focused groups, aliases/CJS/snapshot, 8 rejected initializers and 5 fatal/discard cases per mode. The 19-component focused set includes combined-owner GC, not prototype-only Symbol liveness. [Historical m0.10 Events-OFF denials](../../tests/node-compat/milestones/foundations-v11/reports/historical-m10-events-off.json) remain separate. Callback-return getter parity is false (Node `1/1/0`, native `0/0/0`); Symbol.dispose registry differs. `once`, `on`, `EventEmitterAsyncResource` and captureRejections=true remain deferred |
| `node:string_decoder`: `StringDecoder` and default, UTF8/hex only | Partial; optional guest JS carry-state semantics over existing native Buffer codecs | None | [Manifest](../../builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-string-decoder.json): 2,982sequences/8,886writes and40generic decoder cases, three retained Jco calls and fresh Wasmtime, strict receiver/aliases/CJS/snapshot/three initialization failures. Other known encodings throw; shared/resizable/detached input restrictions and two native ordering deviations are explicit |
| `node:assert`, `node:assert/strict`: exactly22exports each | Partial; optional audited JS scalar assertions, typed errors and shared root/strict function graph | None | [Manifest](../../builtins/node-compat/export-manifest.assert.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-assert.json): 55groups/784primitive comparisons+22profile cases per call, aliases/CJS/snapshot/nine initialization failures on Jco+Wasmtime. Deep/async/CallTracker operations throw; diagnostics/cross-realm behavior remain bounded |
| `node:querystring`: exactly8exports | Partial; optional pinned JS parser/scanner with native URI intrinsics and Buffer UTF8 fallback | None | [Manifest](../../builtins/node-compat/export-manifest.querystring.node-v22.14.0.json), [v11 installed replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-querystring.json): 32groups/210delimiter/1,536malformed-byte vectors+11profile cases, aliases/CJS/private Buffer/snapshot/eight initialization failures on Jco+Wasmtime. Legacy malformed-Unicode behavior, caps and deferred nonstring overloads are explicit |
| `node:util`, `node:util/types`, `node:sys` | Bounded installed module, replayed in v11 | None | [V11 util replay](../../tests/node-compat/milestones/foundations-v11/reports/optional-util.json): 47 util/sys named exports and42type predicates plus defaults, with 29 captured-intrinsic predicates, bounded pure helpers and native codec aliases. 2,436 shared checks+108 deferred call/new checks per call, six deployed aliases and fresh Wasmtime. Forty-one root functions and13predicates remain deferred; warnings and other stated deviations remain |
| `node:stream/web`, bare `stream/web`, exactly18 exports | Partial; accepted m0.9 facade over real native classes and codecs, replayed in v11 | None | [Accepted v11 replay](../../tests/node-compat/milestones/foundations-v11/reports/release-stream-web.json): 41 constructor/250 codec/67 iteration/26 DataView cases, aliases/CJS/cache/snapshot and 7 initializer failures. Prior [v9 OFF guards](../../tests/node-compat/milestones/foundations-v9/README.md) remain separately frozen. UTF8/fixed-unshared/min1, proxy/layout/code/arity/signal gaps persist; compression call/new defers; classic-stream acceptance remains separate |
| `node:stream`/`stream`, `node:stream/promises`/`stream/promises`: root24/promises3 | Partial; corrected bounded suites and full20+14 v2 reviews pass | No intrinsic module capability; RuntimeOnly retains selected random | [Adoption ledger](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md): classic8c3d (15+Node11), replay6a67 (40), follow-on d116 (20) and v2 peer0f59 pass. Root66794/6218 verifies105 complete Node-exact returned records,632 completion files and21 raw Wasmtime decodes; old90660 unknown-case failure unchanged. HTTP packaging71459 and fresh both-host/audit60088 finish raw0 on64,058,731B component24d76605; independent2f5df929 passes six bodies, exact six0.2.10/type-only clock and bothstop0.The separate61-case corpus belongs to zlib validation. Actual diagnostic pair and source preflights pass; timing-input data reviewed, no timing yet; cost/archive/acceptance and broad API/lifecycle claims stay open. Missing raw evidence in earlier scopes, combined-GC and unavailable native queue counters stay explicit; getter/Symbol parity remains false. Accepted v12 and historical counterexamples unchanged. |
| `node:zlib`/`zlib`:39 named plus default | Experimental partial; six native sync APIs validated, operational selection closed | None | [Combined reviewed results](../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json): normal283, GC3 and disabled5 observations, actual Node bytes, namespace40/constants107/counters/refusals/snapshot/ownership and zero imports. Input1MiB/output16MiB/byte-only/strict one member/no dictionary/only integer maxOutputLength. Twenty-two observed error-case differences and public VERNUM4880 versus Node4865 are explicit.31 other callables defer; async/streaming/Brotli, cost, release/host gates remain open. |
| Existing global WebCrypto entropy/owned inputs | Bounded guest implementation policy; no `node:crypto` exports added | OFF: none; runtime: exact `wasi:random/random@0.2.10` | [Entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md): snapshot denials, repeated/fresh calls and 233 original upstream subtests on both stock hosts. Selected pure hashing works without entropy; Node key/Hash/Hmac APIs remain deferred. The experimental355 [secret/bounds source audit](../../tests/node-compat/foundation-crypto/ownership-secret-bounds-audit-v1/README.md) identifies unfixed allocation-check and BIGNUM/EC-buffer cleanup gaps; bounded HMAC results do not cover those paths |
| All other Node namespaces/APIs in the inventory | Deferred or unavailable according to the original per-API plan | Only separately selected standard interfaces | No current runtime support inferred from an inventory row, web global, isolated prototype or successful import of another module |

Native registration and computational native code are distinct. Path and Events
use real native registration but keep small API algorithms in guest JavaScript.
StringDecoder, Assert and Querystring have compiled OFF component evidence and
[joint Runtime HTTP replay on both stock hosts](../../tests/node-compat/milestones/foundations-v11/reports/httpAudit.json). Async-context investigations
still provide no installed `node:async_hooks` module.
The [execution ledger](execution-status.md) is the current acceptance index.

### Experimental six-sync zlib validation

This is the compiled m0.13 validation subset, with operational admission still closed. All six APIs use the selected native SpiderMonkey MOZ_Z codec archive plus a small guest facade and require no host capability. Inputs are fixed, attached, unshared byte buffers/views, at most1MiB; strings and dictionary/coercion domains are unavailable. Outputs are fresh Buffers sharing their fresh JS-owned backing, at most16MiB. This output bound is not a peak-memory bound. Only a plain data option record with integer `maxOutputLength` in1..16MiB is admitted.

| API | Bounded operation | Status / validation |
| --- | --- | --- |
| `deflateSync` | zlib-wrapped encode | Partial; full decoded-byte comparison and limits/error/recovery checks |
| `inflateSync` | zlib-wrapped decode | Partial; full output bytes, strict one-member/trailing/dictionary refusals |
| `gzipSync` | gzip encode | Partial; full decoded-byte comparison; compressed byte identity is not required |
| `gunzipSync` | gzip decode | Partial; full output bytes; concatenated members and trailing bytes refuse |
| `deflateRawSync` | raw deflate encode | Partial; full decoded-byte comparison and supported byte-view ownership |
| `inflateRawSync` | raw deflate decode | Partial; full output bytes and strict complete-input/error/recovery checks |

The [independent difference ledger](../../tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/node-profile-difference-ledger.json) records22 differing error cases out of31:16 outcome/code differences and six additional errno-only differences. Eleven rows had no original deviation label; that original data is preserved. For example, requested-output-limit errors have matching RangeError/ERR_BUFFER_TOO_LARGE but a profile-owned numeric errno1 absent in the Node oracle; fractional maxOutputLength refuses with ERR_OUT_OF_RANGE rather than Node's observed ERR_BUFFER_TOO_LARGE. Profile size caps, strict member/trailing handling, dictionary/string/options restrictions and the source-coupled public ZLIB_VERNUM4880 versus Node4865 remain deviations. No exact error-message or complete Node parity claim follows. The complete per-case raw/oracle citations govern the detailed differences.

The remaining31 callable exports are finite identifiable call/new refusals, including at initialization. Default/named identities, aliases, safe namespace inspection and107 typed constants are validated. No private backend export was added; metadata backend proof remains false/null/null. See the [combined result receipt](../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) for the exact variants and evidence boundaries.

## Initial module and export contract

| Module / API | Disposition and implementation | Capability | Deviations and validation |
| --- | --- | --- | --- |
| `buffer`, `node:buffer`: `Buffer` | Partial Uint8Array facade + proposed native hex kernel | None | Only overloads below; differential and component tests; C++ uncompiled |
| `Buffer.alloc(size, fill?)` | Partial; integer size and numeric fill | None | 0 through 16 MiB; zero-init; no string fill/pool/unsafe allocation; Node byte vectors and boundary failures |
| `Buffer.from(string, encoding?)` | Partial; existing native TextEncoder UTF-8, native hex template | None | `utf8`, `utf-8`, `hex` (case-insensitive); missing/empty string encoding means UTF-8. 1,048,576 source UTF-16 units; hex stops before invalid pair and drops odd nibble; Node vectors |
| `Buffer.from(Uint8Array)` | Partial; copy visible bytes | None | Copies nonzero-offset views; no alias with input; no other typed arrays/array-likes/DataView; identity/copy tests |
| `Buffer.from(ArrayBuffer, offset?, length?)` | Partial; share backing buffer | None | Nonnegative integer arguments; 16 MiB view cap; shared/resizable backing excluded; offset/length and mutation tests |
| `Buffer.isBuffer`, `Buffer.isEncoding`, `Buffer.byteLength` | Private brand, explicit encoding set, bounded byte count | None | byteLength accepts selected strings/U8/AB; cross-realm and detached cases require decision; other Node encodings not claimed |
| `buf.toString(encoding?, start?, end?)` | Partial; UTF-8 decoder preserving BOM or hex kernel | None | Integer ranges with clipping; malformed UTF-8 uses replacement; unknown encodings and unsupported overloads fail; full coercion parity not claimed |
| `buf.slice`, `buf.subarray`, `.buffer`, `.byteOffset`, `.byteLength`, `.length`, `.parent`, `.offset`, numeric indices | Real typed array/view behavior | None | slice/subarray share storage; copied construction does not. Preserve inherited U8 behavior except explicitly overridden Node overload methods. Species/map/filter tested; mutation/prototype edge cases deferred |
| `INSPECT_MAX_BYTES`, `kMaxLength`, `kStringMaxLength`, `constants` | Explicit numeric constants, finite frozen constants object | None | 50; 16 MiB; 32 MiB; not Darwin/Node maximums. No coercible function placeholders |
| `Blob`, `File`, `SlowBuffer`, `atob`, `btoa`, `isAscii`, `isUtf8`, `resolveObjectURL`, `transcode` | Explicit imported callable names, invocation unavailable | None | Existing web implementations are candidates for future reuse; currently throw. This avoids implying Node semantics solely from web globals |
| Buffer constructor and all other Node Buffer-specific own functions | Unavailable explicit throwing functions | None | Includes unsafe allocation, compare/concat/copy/search/write, all numeric readers/writers, other codecs, JSON/inspect and fill overloads. See finite manifest and tests |
| `child_process`, `node:child_process` | Import-only ESM module with default | None; no P2 spawn/IPC service | Exact names: `ChildProcess`, `_forkChild`, `exec`, `execFile`, `execFileSync`, `execSync`, `fork`, `spawn`, `spawnSync`, `default`. All nine callables throw `ERR_SM_NODE_UNSUPPORTED` on call/new, including during snapshot |

All fourteen named Buffer exports plus default match the oracle's namespace; operational support is deliberately narrower. Default members have the same function/object identities as named exports. Defaults are frozen; Node's mutable CJS default and `syncBuiltinESMExports` are not supported. `then` is absent, namespace enumeration is safe, and no universal Proxy or property-read trap is used. Unknown named imports fail linking. The private factory/reference codec exports are not public Node exports.

## Pure modules and foundational streams

The following strategy inventory preserves the initial audit. Its original deferred status is historical; current bounded contracts and accepted checkpoints are tracked in the [execution ledger](execution-status.md) and [progress file](../../progress.md). Guest-only implementations require no host services. Small JS semantic facades are preferred to native rewrites when computation does not dominate.

Current consumer experiment: the explicit six-binding `node:stream/consumers` / `stream/consumers` module has partial `text` and `json` implementations. `arrayBuffer`, `blob` and `buffer` are explicit call/new refusals; `default` initially shares the named function identities and is mutable. The actual355-source normal component run passes190 observations, six namespace checks and11 initialization rejections with imports[]; independent normal-result review also passes. GC4 and independent review pass behind that reviewed-normal gate, with strong coowners and no isolated-root guarantee. The consumer-OFF control separately passes eight bundler denials and five Buffer/stub observations with independent result review. This experiment is outside accepted foundations-v13. Positive web inputs use the selected `node:stream/web` iteration wrapper; raw global ReadableStream is not automatically adapted. See the [actual normal result](../../tests/node-compat/foundation-stream-consumers/normal-component-validation-v1-root-results.json) and [control result](../../tests/node-compat/foundation-stream-consumers/disabled-component-validation-v1-root-results.json).

| Modules / relevant exports | Strategy and capability | Required deviation / validation |
| --- | --- | --- |
| `assert`, `assert/strict` | Audited JS assertions; no capability | Deep equality, errors, cyclic objects, typed arrays and strict/default alias identities; pinned Node tests |
| `events` | JS EventEmitter, `once`, `on`, EventEmitterAsyncResource after context design | Web EventTarget is not EventEmitter. Listener ordering, reentrancy, abort, rejection capture and async iteration |
| `stream` | Node JS state machines plus native byte kernels | `Stream`, `Readable`, `Writable`, `Duplex`, `Transform`, `PassThrough`, `pipeline`, `finished`, `compose`, `duplexPair`, `addAbortSignal`, `promises`, predicates, high-water controls and oracle internal helper exports are individually inventoried. Backpressure, object mode, lifecycle, half-close and error order |
| `stream/promises` | Promise facade over classic stream lifecycle; no capability | `finished`, `pipeline`, `default`; rejection and cancellation cleanup |
| `stream/consumers` | Small facade over selected readable adapters; no capability | Six explicit bindings. Experimental text/JSON only; byte/blob outputs refuse. Node streams and the selected web iteration wrapper need separate tests; no blanket raw-web input claim |
| `stream/web` | Reuse existing native web implementations after export-by-export parity gate | Readable/Writable/Transform streams, all public readers/writers/controllers/BYOB classes, queuing strategies, TextEncoder/DecoderStream, Compression/DecompressionStream; presence/constructor identity and WPT/Node differential. No `stream/iter` in Node 22 inventory |
| `string_decoder` | Incremental native codec + JS retained state | `StringDecoder`; split-sequence and flush behavior differs from simply calling TextDecoder |
| `path`, `path/posix`, `path/win32` | JS path algorithms, declared default POSIX and virtual cwd `/` | Relative resolve uses profile cwd, not the host cwd. Optional deployment cwd requires explicit `cli/environment`. Exact edge-case vectors for both variants |
| `url` | Existing native WHATWG URL/URLSearchParams + separate legacy facade | `parse`, `format`, `resolve`, legacy Url, file URL and domain conversions require Node-specific tests; URL support alone is insufficient |
| `querystring`, `punycode` | Small guest algorithms; native codec only if useful | Querystring is not URLSearchParams; deprecated punycode still requires exact Unicode vectors |
| `util`, `util/types`, `sys` | Mixed JS utilities/native introspection; sys aliases util | Explicit predicates, format/inspect, promisify/callbackify and symbols; no V8 internal assumptions. Node tests for cycles and exotic objects |
| `diagnostics_channel` | Small JS channel facade after async context | `channel`, subscription APIs, tracing channels and `Channel` require context/error lifetime tests |

`buffer` and classic streams are joint foundations: swapping only application imports leaves adapters' internal Feross/unenv Buffer dependencies intact. Resolve those dependencies and global Buffer injection to the same canonical module, or reject the mixed bundle.

## Host capability modules

The interface package version is **0.2.10** for every production capability selected below. These are candidate capabilities, not permissions granted to all applications. Interface use requires a matching selected world and host grant. Namespace/individual member records remain authoritative in the CSV.

| Module / API group | Disposition and implementation | Standard capability and limits | Validation |
| --- | --- | --- | --- |
| `fs`, `fs/promises` descriptor/read/write/stat subset | Deferred native descriptor adapter + JS callbacks/promises | `filesystem/types`, `filesystem/preopens`, `io/streams`, `io/poll`; preopen rights only. No global host root or guaranteed cwd | Rights denial, `..`/symlink confinement, short reads/writes, file offsets, async close and cancellation |
| FS watch/chown/chmod family | Unavailable with selected P2 subset | No watcher/ownership/permission-mode interface selected; do not fake success | Per-operation identifiable throws; named constants remain typed |
| `dns`, `dns/promises`: restricted lookup | Deferred native IP lookup | `sockets/ip-name-lookup`, `sockets/network`, `sockets/instance-network`; host policy and address results | IPv4/IPv6, allow/deny, cancellation and family ordering |
| DNS record queries, Resolver/server configuration | Unavailable in this profile | No portable MX/TXT/SRV/CNAME/SOA/TTL resolver/server API from P2 IP lookup | Reject operations; no custom Jco DNS capability |
| `net` TCP | Deferred native socket resource + classic streams | `sockets/tcp`, `tcp-create-socket`, network/instance-network, IO streams/poll; no Unix-domain socket/fd injection | Partial writes, half-close, connect/listen policy, teardown and backpressure |
| `dgram` UDP | Deferred native resource adapter | `sockets/udp`, `udp-create-socket`, network/instance-network, `io/poll`; do not assume multicast/socket-option portability | Datagram boundaries, address family, limits and permission failures |
| `http` limited requests/responses | Deferred WASI HTTP bridge | `http/types`, `http/outgoing-handler`, optional exported `http/incoming-handler`, IO streams/poll | Streaming, trailers, cancellation and mapping errors. Node Server.listen/raw sockets/Agent internals/upgrades are not furnished by this interface |
| `https` limited HTTPS requests | Deferred HTTP bridge; Node TLS surface unavailable | Same HTTP capabilities; TLS transport/cert trust governed by host | Reject unsupported Node client-certificate, ALPN, custom trust and socket controls instead of ignoring them |
| `tls`, Node HTTP/2 sessions via `http2` | Unavailable initially | **P2 sockets do not provide TLS**. HTTP may use HTTP/2 internally without exposing Node sessions/settings/push | Throwing manifests only if explicitly admitted; future guest TLS needs trust/time/cert validation design |
| `crypto` deterministic primitives | Deferred native guest OpenSSL/web primitive reuse + Node facade | No added import for selected deterministic paths only after RNG audit; `random/random` belongs to an explicitly selected entropy variant | Known answers, Node algorithm/KeyObject/Hash/Hmac parity, key ownership and RNG reseeding |
| `zlib` | Deferred guest zlib; assess Brotli separately | None; no `jco:node/zlib` host service | Sync/callback/stream modes, formats/options/error vectors, final size and throughput |
| `timers`, `timers/promises` | Deferred Node scheduling facade over native event loop | Intrinsic timers need `clocks/monotonic-clock`, `io/poll`; the current engine/Preview1 adapter also retains realtime through `clocks/wall-clock` | `Timeout`/Immediate/ref/unref, scheduler.wait/yield, nextTick/microtask/immediate ordering, snapshot refusal and teardown; no Node timers module is admitted yet |
| `process` bounded env/args/stdio/exit subset | Deferred explicit JS facade with native capability calls | Selected CLI environment/exit/stdin/stdout/stderr; optional clocks for hrtime | Read deployment env after resume, never build env. No OS process, pid fiction, signals, uid/gid mutation or addon loading |
| `console` | Deferred Node formatting over existing native console sink | CLI stdout/stderr and IO streams | Native web console does not imply Console class/inspect parity |
| `perf_hooks` | Deferred Node facade over monotonic clock | Monotonic clock, optional wall clock for explicit origin policy | No fabricated V8/libuv/process metrics; observer entries and resume origin |
| `readline`, `readline/promises` | Deferred line editing after streams | CLI stdio, IO poll/streams, optional terminal interfaces | Nonterminal mode, Unicode, abort and absent TTY |
| `tty` | Unavailable full Node fd/termios APIs | Standard CLI terminal handles could permit narrow future detection only | Reject unsupported terminal setters; no host fd assumptions |
| `os` | Deferred profile constants/pure conversions; host introspection unavailable | No general P2 system CPU/memory/hostname/network interface service | Explicit values/throws, no invented host facts |

The [experimental clock profile](clock-capability-decision.md) explicitly selects
monotonic-clock, wall-clock and poll at 0.2.10. Its actual component passes a
callable/resource graph audit, and [one fresh stock-Wasmtime render](../../tests/node-compat/foundation-scheduler/clock-v13-wasmtime-first-render-v1-comparison.json)
matches the complete retained Node oracle. A subsequent seven-return Jco/
Wasmtime differential finishes raw0 with all whole strings equal to Node;
independent result review passes. It remains unadmitted: the seven
resource cases and broader lifecycle tests are still required. The historical two-interface failure and zero-capability
ReactDOM trap remain unchanged; neither unwanted IO imports nor an identifiable
pure-profile JavaScript refusal are claimed fixed. Node timer objects, request
context, host-handle lifetimes and async scheduling remain separate work.

## Runtime and engine modules

| Modules | Disposition / required design | Capability and validation |
| --- | --- | --- |
| `async_hooks` | Deferred AsyncLocalStorage/AsyncResource/native propagation; broad hook parity separately reviewed | Guest job and task metadata, no host service; interleaved await/rejection/I/O/timer tests and request teardown |
| `module` | Deferred inventory/introspection facade only after bundler contract | No runtime Node loader, dynamic require, createRequire, mutable builtin synchronization or package loader assumed |
| `constants` | Deferred finite guest constants by selected ABI | Node oracle's Darwin constants are an inventory, not valid guest OS constants; compare types and declared values |
| `test`, `test/reporters` | Deferred guest runner; prefix-only specifiers | `after`, `before`, describe/it/test/suite, mocks, assertions, snapshots; reporter APIs. CLI isolation/process behavior excluded until separately designed |
| `sqlite` | Deferred optional guest SQLite | Memory-only DB needs no host capability; file DB needs FS. Native extension loading not selected; size/SQL/lifetime tests |
| `worker_threads`, `cluster`, `child_process` operations | Unavailable process/IPC/worker model | No selected standard P2 process-spawn/worker host service; child_process alone receives import-only template |
| `v8`, `inspector`, `inspector/promises`, `trace_events` | Unavailable V8/Inspector/native tracing APIs | SpiderMonkey/debugger support does not implement these APIs; no new host services |
| `vm` | Unavailable initially | Do not substitute eval; realms/context/module/timeouts need independent SpiderMonkey design and security review |
| `wasi`, `sea`, `repl`, `domain` | Unavailable Node WASI launcher, SEA assets, REPL and legacy domains | Already running in a component does not supply Node's WASI launcher; no fake environment |
| `_http_*`, `_stream_*`, `_tls_*` builtin IDs | Unavailable private modules | Inventory includes them because the oracle lists them; public profile intentionally excludes them |

## Globals and aliases

Existing native ECMAScript globals come from SpiderMonkey; their presence is not a claim about Node-only globals. Existing native web globals (URL, encoding, Blob/File, Event/EventTarget/CustomEvent, AbortController/Signal, console, performance, timers, streams, structuredClone, queueMicrotask, fetch/Request/Response/Headers/FormData and web crypto) are candidates for Node global reuse, with per-descriptor/constructor/behavior tests. Some Node web exports, controllers and stream wrappers are not yet installed globally; inspect each before aliasing it.

The profile's only proposed added global in this milestone is bounded `Buffer`, equal to `node:buffer`.Buffer. `process`, `global`, `setImmediate`/`clearImmediate` are deferred with explicit future behavior; `global` could alias globalThis after descriptor policy is selected. Ambient `require`, `module`, `exports`, `__dirname`, `__filename` are not supplied at runtime. Build-time static CJS lowering can introduce explicit lexical bindings under its own tested contract. Worker/message-port and V8/performance extras are not inferred from web API support.

All ordinary builtin aliases in the inventory have bare and `node:` spellings; the selected bundler canonicalizes admitted aliases before adapter resolution. `test`, `test/reporters`, `sea`, `sqlite` remain **prefix-only**. `sys` is a future util alias; `path/posix`/`path/win32`, `assert/strict`, the stream subpaths, `dns/promises`, `fs/promises`, `readline/promises`, `timers/promises`, `inspector/promises`, `util/types` have their own exact manifests. Not all aliases are automatically registered. Runtime CommonJS and mutable builtin export synchronization remain outside the contract.

Reference semantics: [Node 22 Buffer](https://nodejs.org/download/release/v22.14.0/docs/api/buffer.html), [child_process](https://nodejs.org/download/release/v22.14.0/docs/api/child_process.html), [ESM built-ins](https://nodejs.org/download/release/v22.14.0/docs/api/esm.html#built-in-modules); capability limits are also sourced to the checked-in WIT and pinned toolchain files in the architecture audit.
