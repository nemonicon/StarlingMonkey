# Dependency ordered implementation roadmap

**Current execution priority:** follow the [Next.js priority roadmap](nextjs-priority-roadmap.md)
after the first complete application pass in a real component. Two fresh
Wasmtime runs and a matched Node control now pass24/24 HTTP, cache invalidation,
incremental Suspense and both hydrated browser interactions. The next gates
are native stream semantics, request context/lifetime, reproducible packaging
and explicit production promotion. See the [milestone](nextjs-wasm-milestone-2026-11-06.md)
and [context/lifecycle plan](nextjs-context-lifecycle-plan.md). Generic
diagnostics and unrelated compatibility expansion move behind Next dependencies;
the chronological evidence below remains historical context.

Current accepted checkpoint: [foundations-v13, bounded classic streams](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

Measured application demand includes the [Next16.4.5 regression project](../../tests/node-compat/frameworks/nextjs/README.md).
The experimental native loader/entry route now passes its selected full app
contract on stock Wasmtime42.0.1 with declared instance reuse. It has thirteen
standard WASI0.2.10 imports; complete Node/Buffer support and production
promotion remain open. The original foundations-v13 bundler profile refuses
Next/React general CommonJS packaging and eight unselected Node modules; the
shared guest application fails on explicitly deferred `util.format`. A separate
supported native-module differential passes Node/Jco/Wasmtime. Preserve these
known failures as separate future checks. They are historical regression
baselines rather than the status of the new working generation. The first full
app pass does not substitute for deeper native context, resource, lifecycle,
measurement and release gates under the original phase dependencies.

The [optional package-bundler follow-on](../../tests/node-compat/frameworks/package-bundler-execution-v1/README.md)
now passes real native CommonJS interop, supported-module and React-element
components on Jco/Wasmtime. A genuine replay retains seven failures without new
regressions. ReactDOM edge reaches a zero-import component and traps at a named
clock-subscription frame. The next dependency is the reviewed clock adapter and
an explicitly selected standard clock/poll profile, followed by real asynchronous
runtime checks. Node's renderer and Next entries still demand separate
async-context, process/filename/loader and crypto semantics. The optional bundler
does not change the accepted native checkpoint or imply a full Next server.

Each phase has a measurable gate. The initial deliverable supplies templates and source evidence; these phases describe the work required to turn them into a shipped profile.

The user has authorized execution of the full roadmap. The active
[execution ledger](execution-status.md) tracks every gate, current evidence and
remaining work; completing the initial milestone does not complete this plan.

The opt-in Buffer/stub slice has an [accepted immutable checkpoint](../../tests/node-compat/milestones/allocation-r2/README.md): corrected guest ABI packaging, strict initialization, zero-import pure components, two target HTTP hosts, and four genuine allocator failure scopes with recovery. General DEBUG indirect bindings remain unavailable. The historical performance figures require refresh after the clock-stub correction.

Accepted [entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md),
[foundations-v3](../../tests/node-compat/milestones/foundations-v3/README.md),
[foundations-v4](../../tests/node-compat/milestones/foundations-v4/results.json) and
[foundations-v5](../../tests/node-compat/milestones/foundations-v5/README.md)
checkpoints now cover bounded entropy, Path/loader, Events and ordinary UTF-8
encoder integration. Their exact artifacts pass the documented zero-import or
explicit0.2.10 HTTP worlds on stock hosts. Corrected-clock and matched native
allocation experiments have replaced the old timing claims; a frozen v5 [Weval comparison](../../tests/node-compat/weval-experiment/v5/RESULTS.md)
now reports both throughput gains and copying/memory counterexamples. See the execution ledger for its current state.

The [v8 checkpoint](../../tests/node-compat/milestones/foundations-v8/README.md)
accepts bounded Util, zeroed allocUnsafe and the guest correction for the
previously swallowed callback failures, with all prior module and both-host
gates. New [matched allocator measurements](../../tests/node-compat/foundation-alloc-unsafe/matched/measurement-v1/README.md)
show the initial allocation facade is slower than the portable Jco adapter;
an isolated direct-allocation proposal must earn its own evidence. Stream/web
codecs, iteration and DataView adapters now pass actual native integration,
ON/OFF, prior-module, strict-callback and both-host gates in the
[v9 checkpoint](../../tests/node-compat/milestones/foundations-v9/README.md).
The [v10 checkpoint](../../tests/node-compat/milestones/foundations-v10/README.md)
adds bounded native-backed `addAbortListener`,29 focused groups in both entropy
modes, combined-owner GC, optional-OFF and both-host HTTP evidence. Fresh
callback-return `.then` getter reads still differ (Node `1/1/0`, native `0/0/0`), as
does `Symbol.dispose` registry identity; neither is a parity pass. HTTP retains
six standard 0.2.10 interfaces, a type-only clock and counters1, without a reuse claim.

The earlier public allocation [v11 checkpoint](../../tests/node-compat/milestones/foundations-v11/README.md)
contains core m0.11 direct captured-Uint8Array allocation: fresh zeroed, unpooled
storage after unchanged validation and a 16 MiB limit. Three current Release
engines share 304 native inputs; 33 reports and 1,746 copied evidence files
preserve the accepted scope. All eight release gates pass (five same-engine
successes reverified, three strict suites retried fresh), alongside allocator GC,
19 focused Events components and the same HTTP bytes on both stock hosts, three
requests each, exit 0. The six standard 0.2.10 imports retain explicit random and
a type-only clock; counters `[1,1,1]` establish no reuse. Historical m0.10
Events-OFF is a separate control, not a fourth current engine.

No exports or C++ allocation kernel are added. Callback getter and disposal-symbol
parity remain false; GC combines several owners. Private CPU measurements retain
RSS/capacity/size counterexamples and do not establish accepted production
performance. The subsequent [v12 acceptance](../../tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md)
closes the private scheduler's diagnostic and production gates, using306 native
inputs and three independently verified production engines. All fresh eight-stage,
allocator/focused GC and same-byte both-host HTTP gates pass. Root rehashes4,150
indexed files and the unchanged v11 parent. Public API versions remain unchanged.
The classic-stream candidate and its allocation-order amendment are independently
reviewed and SDK syntax-checked. Its342-input layer is applied and four actual
Original Release variants are frozen/reviewed. Three bounded classic suites pass raw0
with independent [OFF](../../tests/node-compat/foundation-classic-streams/independent-normal-off-component-review-v1/README.md)
and [RuntimeOnly/GC](../../tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) reviews,
including RuntimeOnly/random-only and GC-OFF/zero-import scopes. Fresh replay,
allocator/focused followon and same-byte both-host HTTP now pass with independent
reviews. The [runtime receipt](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/runtime-gates-complete-v1.json)
counts40 replay+20 followon+15 classic+one HTTP occurrences, not global binary
uniqueness. HTTP retains exact six0.2.10 interfaces/type-only clock/no Preview1,
three responses per host/exit0 and counters[1,1,1], with no reuse/isolation claim.
New Node-host workload oracles at1/16 iterations retain14 canonical trace gaps:
write returns, event order and object callback encodings differ despite equal
outputs/checksums. The unchanged342 component independently reproduces four
minimal byte/event gaps on retained/fresh Jco and Wasmtime. The independently
reviewed11-case run confirms two object-encoding gaps (six total). The [corrected source generation](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
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

## Phase 0 Freeze and reproduce the engine

1. Freeze the revisions in the audit and record npm lockfile, engine/Wizer/SpiderMonkey/SDK artifact hashes and compiler flags. Build ComponentizeJS with `STARLINGMONKEY_SRC` pointing at this exact checkout, `HOST_API=wasi-0.2.10` and production debugger disabled. Preserve existing `add_as_subproject`, `add_builtin`, aggregate Rust and `engine` override mechanisms.
2. Run the existing StarlingMonkey E2E tests and ComponentizeJS pure/global/snapshot/error fixtures against that engine. Identify source/API incompatibilities before implementing more built-ins.
3. Build the zero-import profile test world. Print and inspect the final component's import/export types. Any unexpected interface is a failing gate, not an invitation to install another host provider.

Gate: reproducible custom engine, final component validates, explicit zero-import fixture instantiates on Wasmtime 42.0.1. Resolve wasmCloud 2.11.0 deployment entry/world requirements before claiming secondary-host portability. A capability-free custom export may need a test harness on wasmCloud; use its existing component workload facility or the separately declared standard HTTP export variant, never a new host service.

## Phase 1 Manifests and deterministic failure

Depends on Phase 0. Promote Node 22 export inventories into schema-validated module manifests. Generate plain finite registration objects and ESM exports; pin the facade interoperability contract and alias canonicalization. Implement `node:child_process` first: every exported callable is a named throwing function, construction throws, namespace/default inspection is safe, and no host capability is imported.

Add the profile bundler resolver before Jco adapter replacement, coherent global injection, and explicit CJS-to-ESM lowering for static builtin require. Test both aliases, namespace/default identities, unknown export link failure, ambiguous npm names, dynamic require rejection and accidental thenables. Confirm a top-level unsupported call fails componentization. Make strict initialization rejection handling an explicit decision, since not every unhandled rejection currently aborts snapshot creation.

Gate: exact namespace parity for the chosen stub, call/new failures in initialization and deployment, no `jco:*` or draft imports, one implementation of Buffer in the bundle graph.

## Phase 2 Bounded Buffer

Depends on Phase 1. Implement the documented bounded facade and native hex kernel through optional `add_builtin`, with explicit limits, no legacy constructor and no pool. Compile and review the C++ template against the pinned JSAPI. Resolve detached/resizable/shared backing-store handling and string-size checks before enabling it. Keep unsupported exports/methods explicit and identifiable; do not claim full Node Buffer API.

Add Node differential vectors, component tests, forced-GC and OOM/boundary tests, buffer-view identity and overlap checks. Test facade use through a minimal CommonJS dependency and global Buffer injection. Compare against Jco 1.40's existing adapter in equivalent capability-free components. Add UTF-8 native fast paths or native copy/search/numeric kernels only when measurements justify them.

Gate: supported overloads pass differential/component tests; declared deviations have explicit negative tests; compiled native implementation passes GC and allocator review; no added WASI imports; size/startup/memory/throughput results recorded. If the kernel does not improve the chosen workload, retain the simpler implementation.

## Phase 3 Pure foundations and scheduling

Depends on Phase 2 for Buffer-dependent APIs. Implement EventEmitter, string_decoder, assert, path, querystring and bounded util semantics. Retain JS for small semantic state machines. Bridge the native web stream exports only after checking identities, BYOB behavior and per-export availability. Implement classic Readable/Writable/Duplex/Transform/PassThrough plus stream/promises and stream/consumers; web streams alone do not satisfy this dependency.

Before exposing Node timers, process.nextTick or AsyncLocalStorage, define queue ordering, promise draining, cancellation, ref/unref and lifecycle. Integrate context tokens at the actual SpiderMonkey promise-job and native-task boundaries. Establish request teardown and sequential reuse; do not add an ALS facade that loses context on await.

Gate: stream backpressure/error/cancellation tests and interleaved context tests pass in a real component, no leaked interest count or request resources, and the scheduler's documented deviations are stable.

## Phase 4 Native compression and cryptography

Depends on byte ownership from Phase 2; streaming APIs depend on Phase 3. Evaluate native zlib reuse for gzip/deflate/deflateRaw; add Brotli only after a size/throughput decision. Reuse OpenSSL-backed web primitives for matching algorithms; implement Node key/Hash/Hmac semantics separately. Audit RNG use inside OpenSSL rather than treating deterministic crypto as permission for ambient entropy. No custom compression/crypto host services.

Gate: known-answer and malformed-input vectors, Node differential, streaming boundary tests, key lifetime/zeroization policy, final component size and operation benchmarks. Algorithm lists and OpenSSL flags remain versioned. Restrict entropy imports to variants that need random operations/key generation.

## Phase 5 Optional standard capabilities

Depends on Phase 3 lifecycle/scheduler. Design independent filesystem, HTTP, TCP/UDP/name-lookup, CLI and entropy variants with explicit standard `0.2.10` allowlists. Start with a small subset per module and publish deviations per export. No blanket `fs`, `net`, `dns`, `http` or `process` support label. Preserve preopen confinement and network grants. Reject unsupported socket/TLS/HTTP options rather than silently ignoring them.

TLS remains unavailable unless a guest TLS stack, certificate trust source, validation/time policy and socket integration are selected and measured. WASI HTTP HTTPS does not justify claiming `node:tls` or full `node:https`. Process creation, IPC, Node workers, V8/Inspector APIs and POSIX signals remain unavailable with the selected interfaces.

Gate: identical components validate and instantiate on both unmodified target hosts under documented grants, capability-denied tests fail predictably, and unused variants do not enlarge the pure profile's import set. Publish actual emitted imports for every profile variant.

## Phase 6 Expand only from measured demand

Depends on the relevant earlier phases. Add further encodings, numeric Buffer operations, search/copy kernels, module APIs and optional guest libraries in response to application traces. Require a manifest change, Node release differential, component fixture and size/performance comparison for each extension. Retargeting Node or WASI is a compatibility release, not an unreviewed inventory refresh.
