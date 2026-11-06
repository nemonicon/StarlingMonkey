# Portable Node compatibility profile for StarlingMonkey

Current accepted checkpoint: [foundations-v13, bounded classic streams](../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

The [experimental Hash/Hmac results](hash-hmac-results-2026-11-06.md) now cover
fourteen complete Jco/stock-Wasmtime returns:280 accepted Node-record comparisons
and112 separate native-policy checks. Both components import nothing; direct
native aliases share functions/default objects but retain separate namespace
objects. The new candidate remains outside production acceptance, with freeze,
lifecycle and cost gates open.

The [post-push Next.js report](nextjs-results-2026-11-06.md) records fresh
comprehensive application and component checks after `77659217`: Node controls
pass on replay,17 main Wasm failures and seven optional-package failures remain,
and supported-module/React-element differentials pass. An initial aborted
browser action request and changed generated-source identities stay documented.
The full Next server still does not compile to Wasm.

The [optional package-bundler follow-on](../../tests/node-compat/frameworks/package-bundler-execution-v1/README.md)
passes three complete Node/Jco/Wasmtime differentials: native CommonJS interop,
supported modules and real React elements. Its fresh ten-case replay retains
seven known guest failures; ReactDOM edge constructs a zero-import component
and traps at clock subscription. Full Next.js HTTP/Wasm execution remains
unavailable. Both framework runners and regression comparators are documented
and retained for future checks.

The experimental clock adapter passes core validation and complete WIT-package
review. Its corrected loader and real ReactDOM component pass source and
artifact review with exactly three standard 0.2.10 clock/poll imports. The
seven-return follow-up finishes raw0: three retained/one fresh Jco and three
fresh Wasmtime values all match the complete retained Node return. Independent
actual-result review passes; snapshot and broader clock gates remain open.

The combined355 native retry completes all 108 build steps and passes
independent BUILD review. Its complete 80-field sidecar and 2,596-copy freeze
pass independent DATA review. Export, validation-only bootstrap and the retained
read-only API also pass independent result review. The complete six-outcome
construction review accepts five components and identifies one unaccepted INIT
timer refusal. A separate pure Buffer control finishes raw0 with seven whole
Node-equal Jco/Wasmtime returns; independent runtime DATA review passes.
Broader clock lifecycle and operational admission remain open. Clock components
select only the standard WASI0.2.10 clock/poll interfaces.
The default-OFF Hash/Hmac candidate now compiles and links as a 357-source
engine. Its recipe exits0, but both wrappers exit1 after the staged Git index
changes hash and mode. Independent review validates the compiled candidate and
the recorded failure; it does not admit the engine. Read-only artifact
revalidation first fails on two retained system `/tmp` paths. Its narrow v2
correction passes actual full-input guard tests and independent Source review;
the genuine API retry exits0. A corrected review publication passes the whole
caller contract. A zero-import13,240,343-byte component passes actual artifact
review and returns80 Node-equal accepted Hash/Hmac records on Jco. A harness
counter-publication defect is preserved and being corrected before full runtime
acceptance; stock-host/direct-alias/lifecycle/cost gates remain open. The
original failures remain preserved.
The pinned Node oracle passes60 selected
observations; the separate guest result above is still experimental. Private clock diagnostic v2 passes
seven actual SDK frontends and Source review; linking and runtime remain
pending. These candidates and their open lifecycle gates are recorded in
[progress.md](../../progress.md).
See the [execution status](execution-status.md) for their exact evidence.
The original resource mapping fails at harness serialization; its partials and
raw failure remain retained. The v3 successor passes Source review, completes a
fresh mapping at raw0 and passes independent mapped DATA review. Pristine input
options and the actual typed post-call shape are separate; unused Jco default
rules grant no extra capability. A separately issued ordinary resource runtime
phase finishes raw0 with35 public strings/49 cases/98 callbacks and322
per-instance ID observations;
[independent runtime review](../../tests/node-compat/foundation-scheduler/independent-combined355-resource-runtime-v3-results-review-v1/results.json)
passes the whole schedule and publication/process/native protection. The separate
seven-return clock-snapshot and surviving-job suites also pass independent DATA
review. The disposable fatal observation finishes raw1: its generic Wasmtime trap
lacks source-specific callback evidence, so it stays cause-inconclusive and
unaccepted. Native cleanup/offset/invalid-queue and wider lifecycle gates remain
open. No public Node timers module or new production profile is admitted. See [progress.md](../../progress.md).
The separate secret355
component and corrected v3 guarded runtime also pass actual review: 23 complete
returns and 45 Node-oracle signatures. Three fresh stock-Wasmtime validations
finish raw0 with 27 matching tags and pass independent actual-result review.
Node crypto exports, native wiping and request reuse are not established.
[progress.md](../../progress.md) records evidence and remaining work. Accepted
production remains foundations-v13.

The [Next.js application experiment](../../tests/node-compat/frameworks/nextjs/README.md)
now has two real Node production builds,24 HTTP and two browser checks per run,
and19 isolated Wasm attempts. Full Next/React entries fail at the current CommonJS
bundler boundary; eight unavailable Node module imports refuse explicitly. The
shared application function builds a zero-import component but fails on deferred
`util.format`; a caught-error diagnostic identifies that refusal. A separate
supported Buffer/foundations/web/classic-stream fixture returns complete
Node-equal values on Jco and fresh Wasmtime. These findings add repeatable
regression checks and demand priorities, not complete Next.js compatibility or
new API support.

Current results and outstanding work are maintained in [progress.md](../../progress.md). Consumer355 HTTP passes its bounded both-host review. Crypto normal-key/stock-Wasmtime validation and the isolated GC native build, freeze, bootstrap and component artifact reviews pass. The first GC runtime attempt failed before guest execution on17 relative input paths; the corrected v2 source passes independent review and the new runtime finishes raw0, retaining23 complete public strings and45 Node-oracle-matching signatures. Independent actual-result review passes, and three stock-Wasmtime GC calls finish raw0 with entire results equal to Jco; their independent result review passes.

The scheduler resource/selector, native codec, guarded-key ownership and clock
adapter experiments retain separate source, actual-result and cost evidence.
Their latest bounded results and open adoption gates are maintained in
[progress.md](../../progress.md). Historical source-only and pending labels in
sealed packets describe those packets at creation; later evidence does not
rewrite them. Accepted production remains bounded foundations-v13.

This directory preserves the initial architecture audit and opt-in implementation templates for a bounded `node:buffer` and an importable, explicitly unavailable `node:child_process`. The initial audit did not add runtime built-ins or establish complete Node or Buffer compatibility. The compatibility reference is **Node.js v22.14.0**. Native code below means code compiled into the Wasm guest, with no additional host service.

Execution of the full roadmap is now active. See the
[gate-by-gate execution ledger](execution-status.md) for implemented, tested and
remaining work, and the repository [continuing tracker](../../progress.md).
Earlier checkpoints retain immutable reports and bounded claims.
The historical [foundations-v12 checkpoint](../../tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md)
adds the bounded private scheduler source layer with no new public API. Three
production engines share 306 native inputs; separate diagnostic Release/GC,
fresh eight-stage replay, allocator/focused GC and same-byte both-host HTTP
gates pass. Root independently verifies 4,150 indexed evidence files and the
unchanged v11 parent. Private ticks default OFF; public process/nextTick/ALS
remain unavailable. Frozen archive pending labels preserve its construction
state; the linked separate Root receipt records acceptance.

Core remains `sm-node-22.14.0-m0.11`, including privately branded captured native
Uint8Array allocation: at most 16 MiB, fresh zeroed backing and no pool. V12 adds
no Buffer export or C++ allocation kernel. The independently reviewed classic
stream source layer is [applied](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md)
with a default-OFF flag and342 inputs. Four original Release variants are frozen and
reviewed; normal-OFF, RuntimeOnly and GC-OFF classic component suites pass raw0
with independent [OFF](../../tests/node-compat/foundation-classic-streams/independent-normal-off-component-review-v1/README.md)
and [RuntimeOnly/GC](../../tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) reviews.
Fresh replay and followon gates now pass with independent evidence reviews:
40 replay,20 followon,15 classic and one combined HTTP component occurrences.
The [runtime composition receipt](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/runtime-gates-complete-v1.json)
does not claim global binary uniqueness. The same64,057,853-byte HTTP component
passes three requests per stock host, exact six0.2.10 imports/type-only clock/no
Preview1 and clean shutdown; [independent final review](../../tests/node-compat/foundation-classic-streams/independent-combined-http-results-review-v1/README.md)
passes. Counters[1,1,1] establish neither reuse nor request isolation.
Old replay/harness failures remain preserved. New Node-host workload checks at
1/16 iterations retain14 canonical-factory trace counterexamples despite exact
matching output bytes/text/values and checksums. HWM-boundary return values,
event ordering and object callback encodings need separate source fixes. The
unchanged342 component reproduces four minimal byte/event gaps on retained and
fresh Jco/Wasmtime, with independent verification. The independently reviewed
11-case run confirms two further object-encoding gaps (six total). The [corrected source generation](../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
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

The earlier [allocation acceptance](../../tests/node-compat/milestones/foundations-v11/results.json)
cover all eight release gates (five reverified same-engine successes and three
fresh strict retries), a separate allocator GC gate and 19 focused Events
components. Twenty-nine focused groups pass in both entropy modes. Callback-return
`.then` getter parity remains false: Node reads `1/1/0` for
ordinary/protected/already-aborted callbacks; both native hosts read `0/0/0`.
The getters return undefined; callable-then behavior is not established. Target
`Symbol.dispose` lacks Node's registry identity. GC combines signal, listener and
closure-held Symbol owners; prototype-only liveness remains unproved. Historical
m0.10 Events-OFF evidence is a separate control, not a fourth current engine.

The same HTTP component passes three requests per stock host; both hosts stop
with exit 0. Its six standard 0.2.10 interfaces include explicit random and a
type-only monotonic clock. Counters are `[1,1,1]`; instance reuse and request
isolation are unproved. Historical audit dispositions below are not current
support claims.

The [source adoption](../../tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
now has fresh production acceptance. The frozen proposal's earlier UNAPPLIED
label remains historical. Private measurements retain higher RSS/capacity and
size counterexamples; they establish no performance advantage for this accepted
production source. Public scheduling/ALS, classic streams and consumers, Blob/File,
compression, Node crypto and optional capability variants remain roadmap work.

Earlier [v7 ordinary controls](../../tests/node-compat/milestones/foundations-v7/README.md)
exposed a strict-initialization gap in callback exception reporting. Private
guest corrections now pass bounded synchronous, post-binding, deployed and
finalizer/getter gates on the new production engine. The original counterexamples
remain preserved. See the [execution ledger](execution-status.md) for exact scope,
remaining event/lifecycle deviations, accepted bounded stream/web and native
compression work.

The subsequent native integration lives in [`builtins/node-compat`](../../builtins/node-compat) with its own [`tests/node-compat`](../../tests/node-compat) and [developer contract](../src/developer/node-compat.md). The inventories and findings in this directory describe the original audited revision; current integration evidence is recorded separately.

The subsequent [wasmCloud validation](../../tests/node-compat/wasmcloud/README-host.md)
executes a standard HTTP variant on the official unmodified 2.11.0 local host.
The [A/B experiment](../../tests/node-compat/bench/README.md) compares supported
Buffer operations with Jco's actual JavaScript adapter using the same release
engine. Those records distinguish observed results from this original audit's
proposed support and validation plans.

The [portability and performance results](portability-and-performance.md)
summarize the executed host checks, all benchmark tradeoffs and the export
binding defect found during measurement.

## Deliverables and evidence

| Deliverable | Artifact | Evidence level |
| --- | --- | --- |
| A. Architecture | [integration findings](integration-findings.md), [toolchain findings](toolchain-findings.md) | Source inspection at the exact revisions below |
| B. API matrix | [readable matrix](compatibility-matrix.md), [per-API records](api-matrix.csv), [exact namespace inventory](node-v22.14.0-exports.json), [policy](policy.json) | Inventory executed with Node v22.14.0; profile dispositions are proposed |
| C. Roadmap | [dependency ordered roadmap](roadmap.md) | Engineering proposal with acceptance gates |
| D. Templates | [template contract](templates/README.md) and files in that directory | JavaScript checks and uncompiled C++ distinguished there |
| E. Validation | [validation plan](validation.md), [real-component fixtures](component-tests/) | Executed results are recorded separately from required future gates |

The audit started from a clean worktree at **`54b3329b3ce818fd1f244e871e9c259b63667cda`**. Its initial additions were confined to `docs/node-compat`. The subsequent runtime profile remains opt-in; no Node module or global is installed by default.

## Frozen baseline

| Dependency or contract | Pin |
| --- | --- |
| StarlingMonkey source | `54b3329b3ce818fd1f244e871e9c259b63667cda` |
| SpiderMonkey artifact tag | `FIREFOX_147_0_4_RELEASE_STARLING` (`cmake/spidermonkey.cmake:1`) |
| Native build dependencies | WASI SDK `30.0` (`cmake/wasi-sdk.cmake:1`), Rust `1.88.0` / `wasm32-wasip1` (`rust-toolchain.toml`), OpenSSL `3.0.17` with the source hash in `cmake/openssl.cmake:3` |
| Node oracle | `v22.14.0`, official `darwin-arm64` binary; tarball SHA-256 `e9404633bc02a5162c5c573b1e2490f5fb44648345d64a958b17e325729a5e42` checked against release SHASUMS |
| Node API inventory input | [versioned all.json](https://nodejs.org/download/release/v22.14.0/docs/api/all.json), SHA-256 `fdbeac15985adfb8b5298d9e3175263900d0d4dbf49c6c80a96dd5724a080301` |
| ComponentizeJS | npm `0.23.0`, source `4d812f5a7b524cea5bcfd565cac55f3fab876a57` |
| Jco | npm `1.40.0`, source `42cd21e0a31362dbb519f4749f3689bba0fbdb1d` |
| Selected production WASI family | Only explicitly admitted interfaces in `wasi:{cli,clocks,filesystem,http,io,random,sockets}@0.2.10`; not all seven packages for every component |
| Selected milestone test world | `starling:node-compat-test/profile@0.1.0`, application export `run: func() -> string`, **zero host imports required** |
| Existing engine binding world | `local:bindings/bindings`, includes `wasi:cli/command@0.2.10` and `wasi:http/proxy@0.2.10`; audit baseline, not the desired minimal application contract |
| Existing CLI adapter world | `local:bindings/command-extended`, CLI command plus outgoing HTTP at `0.2.10` |
| Direct target | Unmodified Wasmtime `42.0.1` (also this repository's build-tool pin) |
| Secondary target | Unmodified wasmCloud `2.11.0`, source `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff`; embeds Wasmtime `48.0.7` |

A custom local WIT **world** can group standard interfaces and export application functions; it must not import custom host services. The zero-import test world is a concrete minimal contract, not a promise that the current raw engine's broad import set automatically shrinks. ComponentizeJS's splicer and final component inspection must establish that property for the custom engine. A production HTTP variant will select `wasi:http/proxy@0.2.10` with an explicit interface allowlist; optional filesystem and sockets variants have separate allowlists.

The original smoke tests used the released ComponentizeJS engine, rather than a
rebuilt engine from this checkout. Replacement uses the existing
`STARLINGMONKEY_SRC` extension and `engine` option described in the toolchain
audit. The frozen baseline alone established no custom-engine or wasmCloud
deployment result; later bounded builds and deployments are recorded in the
[execution ledger](execution-status.md) and accepted checkpoints above. Node's
oracle release fixes API semantics; it is not a deployment recommendation.

## Architecture decision

Use existing `add_builtin` and `Engine::define_builtin_module`, with finite export manifests and real ESM bindings. Keep the JavaScript facade responsible for overload selection, branding, typed-array relationships, errors and stream state machines. Put measured expensive byte kernels in native guest code. Reuse the existing native UTF-8 codecs, web streams, zlib and OpenSSL implementations only where semantics match. The first native Buffer kernel is hexadecimal conversion; a template is insufficient evidence of a performance win.

Preserve selected `node:` imports through bundling. Jco's existing adapter plugin otherwise replaces them before the runtime resolver sees them. Bundle CommonJS dependencies to ESM with a narrowly defined static-require mapping, and inject global Buffer from the same canonical module. Do not provide a general CommonJS loader or claim `syncBuiltinESMExports`. Unknown modules/exports fail resolution/linking; admitted stub functions always throw on invocation, including snapshot-time application evaluation.

Reject final imports outside the selected standard WASI allowlist. In particular, Jco's `jco:node/*`, wasmCloud-specific services, Preview1 imports left on the final component, and draft `wasi:tls` imports are outside this profile. Standard P2 sockets provide TCP, UDP and IP lookup; they do not provide TLS. Host-managed HTTPS through `wasi:http` cannot implement arbitrary Node TLS socket behavior. These limits are reflected per API in the matrix.

## Ownership and lifecycle policy

Root JS objects across every allocating/calling JSAPI operation. Use SpiderMonkey-managed ArrayBuffers and views for the baseline. Acquire native byte pointers only within a no-GC region after coercions, roots, lengths and output allocation are complete; release them before further JS execution or allocation. Rooting keeps objects reachable but does not pin movable raw data. No borrowed span crosses a callback, yield or async suspension. Long-lived JS fields require traced `JS::Heap` storage or engine-owned persistent roots with explicit teardown. Do not create static roots with a longer lifetime than the engine.

The baseline copies `Buffer.from(Uint8Array)` and shares `Buffer.from(ArrayBuffer, offset, length)`, `slice` and `subarray`. It retains the real `.buffer`, `.byteOffset`, byte length, index access and inherited Uint8Array behavior. A native codec may allocate its result once and return a view over that allocation. UTF-8 facade paths may still have an avoidable intermediate allocation; measure and remove it only after semantics are validated. A separately allocated Rust/C++ block is not automatically adoptable by `NewArrayBufferWithContents`: allocation family, failure ownership and finalizer must match. `JS_realloc` canonical-ABI storage is likewise not a blanket ownership-transfer mechanism.

Snapshot initialization permits deterministic module state and byte arrays, not deployed host handles or captured build secrets. Launch Wizer with a sanitized environment, source-only temporary preopens and explicitly disabled capabilities. Top-level entropy, environment access, clocks or host I/O require a declared policy; the recommended profile rejects capability-bearing operations during initialization rather than caching their results. Build-time source loading is an embedding concern with temporary resources closed before snapshotting. This is a profile change to implement and test, not a guarantee supplied by `__wasilibc_deinitialize_environ`.

At deployed entry, acquire environment/args from the granted `wasi:cli/environment` capability when enabled, reset time origins, and obtain fresh entropy from `wasi:random/random`. Never reuse a snapshotted random pool, TLS state, resource identifier or build-time environment cache. Deterministic pure modules require none of these imports. Wall time and monotonic time are distinct; Node scheduling uses the latter. Math.random initialization and cryptographic entropy require separate tests.

Initially permit one request lifetime per instance for stateful HTTP applications; pure explicit component exports may be called repeatedly under their documented state model. The current singleton fetch event and `Engine::reset` do not prove request isolation. Request entry must create a fresh context; every resource/task needs a close/cancel owner; entry failure and normal completion must release them. Reject concurrent reentry into a single JS engine until explicitly supported. Component reuse must separately define which application module state persists and which request roots, handles and callbacks are cleared.

Future AsyncLocalStorage must capture context when promise reactions and callbacks are registered, carry it with each queued job/task, restore it for callback execution and restore the prior context on every return/throw. Use rooted context tokens, not a mutable request-global variable. `run`, `enterWith`, `exit`, `disable`, binding and snapshot helpers have different contracts. A custom SpiderMonkey job queue or an equivalent verified embedding hook is needed; wrapping Promise.then and timers alone misses await continuations and native reactions. The actual pinned SpiderMonkey hook choice remains open.

## Regenerate the API records

Run the generator with the exact Node oracle and its versioned API JSON:

```sh
curl -fL https://nodejs.org/download/release/v22.14.0/docs/api/all.json -o /tmp/node-v22.14.0-api.json
/path/to/node-v22.14.0/bin/node docs/node-compat/scripts/inventory.mjs /tmp/node-v22.14.0-api.json
```

The generator refuses other Node releases and different API JSON bytes, enumerates namespaces and global descriptors without executing getters, adds prefix-only `node:test`, `node:test/reporters`, `node:sea`, `node:sqlite`, and supplements reflected exports/static/prototype members with documented overloads, events, properties and globals. Runtime data such as process environment, argv and loader-cache contents is excluded from member enumeration. The generated inventory is platform-specific where Node itself is platform-specific. No Darwin constants are silently adopted as Wasm ABI constants. Documentation paths can represent the same API as a reflected path; these are complementary evidence records, not distinct implemented operations.
