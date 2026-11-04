# Opt-in Node compatibility profile

Current accepted checkpoint: [foundations-v13, bounded classic streams](../../../tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

The latest accepted core `sm-node-22.14.0-m0.11` profile provides a bounded `node:buffer`
and an importable `node:child_process` stub. It does not provide general Node.js
compatibility or complete Buffer support. The API reference and differential
oracle are Node.js **v22.14.0**.

Latest acceptance is [v12](../../../tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md),
with unchanged core m0.11, Events m0.10 and seven optional foundations. Three
production Release engines share306 native inputs; separate diagnostic Release/
GC, fresh eight-stage replay, allocator/focused GC and both-host HTTP pass.
Root verifies4,150 indexed evidence files and the unchanged v11 parent. Private
ticks default OFF and add no public process/nextTick/ALS API. Classic streams
have an applied default-OFF342 source layer and four reviewed original Release freezes.
Independent [OFF](../../../tests/node-compat/foundation-classic-streams/independent-normal-off-component-review-v1/README.md)
and [RuntimeOnly/GC](../../../tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) component reviews
confirm three raw0 bounded suites with19/48/17/3/65 checks, retained/fresh calls
and explicit failure/discard limits. OFF/GC import nothing; RuntimeOnly imports
only standard random@0.2.10. GC retains combined owners, not an isolated VM root.
Fresh replay-v3 and followon gates now pass, with independent reviews. The
[runtime receipt](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/runtime-gates-complete-v1.json)
records40 replay+20 followon+15 classic+one HTTP component occurrences, not global
binary uniqueness. HTTP25eb1a1c… passes three responses per stock host, exact six
standard0.2.10 imports/type-only clock/no Preview1 and clean shutdown;
[independent final review](../../../tests/node-compat/foundation-classic-streams/independent-combined-http-results-review-v1/README.md)
passes. Counters[1,1,1] do not establish reuse/isolation. New Node-host measurement
workloads retain14 canonical trace gaps at1/16 iterations, despite exact output
and checksum equality. The unchanged342 component reproduces four minimal
byte/event gaps on retained/fresh Jco and Wasmtime with independent verification.
The independently reviewed11-case run confirms two object-encoding gaps (six
total). The [corrected source generation](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
retains four reviewed production freezes, 474 files each, and its reviewed
26-file runtime family with 6,414 consumed inputs and 22 tool links. The three
[corrected classic suites](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-classic-runtime-root-results-v1.json)
finish at Root-observed exit 0, publishing 90/91/90 files and 15 component
occurrences. OFF/GC import nothing; RuntimeOnly imports only
`wasi:random/random@0.2.10`. The [independent all-four result review](../../../tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md),
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

Diagnostic producer-v3 has successful [ON](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-on-native-root-results.json)
and [OFF](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-off-native-root-results.json)
build/freeze/read-only checks, each at exit 0 with 109 build steps and 525 frozen
files. Independent native reviews [ON `c05afb8d…`](../../../tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-on-native-review-v1/README.md)
and [OFF `ca2debb8…`](../../../tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-off-native-review-v1/README.md)
pass. Root's separate [ON-only pins](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-on-pins.json)
(`2e9811a5…`) and [authority](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-on-root-review-receipt.json)
(`9681578e…`) do not constitute a measurement pair.
The [correctness companion138a](../../../tests/node-compat/foundation-classic-streams/measurement-correctness-candidate-v1/README.md),
mandatory [reporting amendment0558](../../../tests/node-compat/foundation-classic-streams/measurement-correctness-reporting-amendment-v1/README.md)
and [source review c695](../../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-source-review-v1/README.md)
remain bound to the [ce2f activator](../../../tests/node-compat/foundation-classic-streams/measurement-correctness-activation-candidate-v1/README.md)
(19 files/6,908 inputs, 27 Root source checks and [peer ee4d5](../../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-activation-source-review-v1/README.md)).
[Source activation and artifact preflight](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/correctness-source-activation-and-preflight-root-results.json)
pass, creating family `4728c365…f33f49` (21 files/7,489 inputs), whose
[generated-family review634077e4](../../../tests/node-compat/foundation-classic-streams/independent-measurement-correctness-family-review-v1/README.md) passes.

The [first full 20-workload/14-boundary attempt](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-timeout-attempt1-root-results.json)
(`e8165564…`, session90660) exits 1 after a 55-second Wasmtime child timeout.
It publishes no final result, completion or semantic counterexample. The
original timed-out case is unknown; unretained Jco observations cannot count as
passes. The [independent failure review c5a0a80f](../../../tests/node-compat/foundation-classic-streams/independent-workload-timeout-failure-review-v1/README.md)
passes within that evidence scope. Separate fresh case0 Jco and Wasmtime
controls match the full Node oracle. A [separate fresh case5 control](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-public-case5-root-results.json)
(`793a2f0d…`, session16818) returns child exit 0 after 177.338 operational seconds
under a 600-second cap; its complete trace, setup and checksum equal Node case5.
This proves neither the original timeout's case/cause nor deadline adequacy for
all cases or a performance result. The original failure remains unchanged.

The [persistence amendment60a8687e](../../../tests/node-compat/foundation-classic-streams/measurement-correctness-persistence-amendment-v1/README.md)
and [peer6fb6](../../../tests/node-compat/foundation-classic-streams/independent-correctness-persistence-source-review-v1/README.md)
lead through the reviewed v2 activator to [source418ff8fe](../../../tests/node-compat/foundation-classic-streams/measurement-correctness-activated-v2/README.md)
(22 files/7,542 inputs; [family peer c30b596a](../../../tests/node-compat/foundation-classic-streams/independent-correctness-v2-family-review-v1/README.md)).
The [fresh full v2 run](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-workload-v2-root-results.json)
finishes at Root-observed raw exit0 (session66794, receipt `6218afd5…`).
[Independent result review0f59a0da](../../../tests/node-compat/foundation-classic-streams/independent-workload-v2-results-review-v1/README.md)
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

The separate [measurement-execution source4b6fdfa5](../../../tests/node-compat/foundation-classic-streams/measurement-execution-candidate-v1/README.md)
has 43 files/7,004 inputs. [Independent review96bc44a3](../../../tests/node-compat/foundation-classic-streams/independent-measurement-execution-source-review-v1/README.md)
requires mandatory M1 deadline/capture fixes and permits no activation. A
[new amendment](../../../tests/node-compat/foundation-classic-streams/measurement-execution-deadline-amendment-v1/README.md) is sealed at index `b0975b54…` (25 files/7,112 inputs), with 36 source/reversal,
18 pure deadline and11 syntax checks. Its [independent source review9e602ec9](../../../tests/node-compat/foundation-classic-streams/independent-measurement-execution-deadline-source-review-v1/README.md)
passes. A separate Root review now authenticates both actual diagnostic variants.
The [new source family and both preflights](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-source-and-preflights-root-results.json)
pass at Root-observed exit0 (69131/24691): index1b801439… has35 files/7,709 inputs.
[Independent family review4e986ca1](../../../tests/node-compat/foundation-classic-streams/independent-common-byte-v2-family-review-v1/README.md) passes.
The [four-arm attempt25227](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json) finishes at raw exit1 in the
host stock graph checker before stock componentization. The inventory has no
`provider` field; its three original guest paths are explicit sourceBeforeAfter
rows. Native-on, canonical-on and canonical-off completed their full arms.
[Independent reviewbf9fa2a6](../../../tests/node-compat/foundation-classic-streams/independent-common-byte-v2-three-arm-failure-review-v1/README.md) verifies231 durable observations against
all14 Node oracles, identity/probes, raw calls and final source closure. A new
[stock-only correction and composition source](../../../tests/node-compat/foundation-classic-streams/measurement-stock-composition-candidate-v1/README.md) passes
[independent reviewddbbe2a7](../../../tests/node-compat/foundation-classic-streams/independent-stock-graph-composition-source-review-v1/README.md). Root source checks pass; a separate
[three-arm authorityafdbc0bc](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-common-byte-three-arms-for-stock-only-v1.json) permits fresh stock execution.
[Stock run91122](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-stock-only-root-results-v1.json) and [composition12839](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composition-root-results-v1.json) finish
at exit0. [Independent actual reviewab100c83](../../../tests/node-compat/foundation-classic-streams/independent-common-byte-stock-and-composition-results-review-v1/README.md) verifies all308
observations against14 Node cases, exact raw calls, component/graph data and
each arm origin. Both required actual-proof documents are indexed. Original
source1b801, arm records and parent exit1 stay unchanged; this is new composed
evidence, not a pass for the original failed run. Timing was still disabled at that preparation checkpoint. Future
authority templates stay NULL; no external timing phase or timing result exists.

The [corrected replay producer8851](../../../tests/node-compat/foundation-classic-streams/trace-replay-activation-candidate-v1/README.md)
passes [source review c373](../../../tests/node-compat/foundation-classic-streams/independent-trace-replay-activation-source-review-v1/README.md)
and its source activation creates [family a08aec2d](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-source-activation-root-results.json)
with 83 files and 2,293/2,292 root/capability inputs; [generated-family review8529](../../../tests/node-compat/foundation-classic-streams/independent-trace-replay-family-review-v1/README.md) passes.
Root's [preflight environment failure](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflight-attempt1-root-env-failure.json)
is preserved: native OFF/RuntimeOnly/GC pass, then Release OFF lacks the required
explicit `NODE_COMPAT_WASMTIME`. The [corrected-environment retry and combined preflights](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflights-root-results.json)
pass without source/native changes or a guest in those preflight attempts.
The [fresh eight-stage replay](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-release-replay-root-results.json)
then passes at Root-observed exit 0, covering six optional foundations and 40
component occurrences, including one fresh historical control. All import
nothing. Five allocator-GC/focused/getter follow-ons also pass, with
[20 component import audits](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-followon-imports-root-results.json):
only the eight RuntimeOnly components import standard random@0.2.10.
Independent [replay6a67](../../../tests/node-compat/foundation-classic-streams/independent-corrected-replay-results-review-v1/README.md)
and [follow-on d116](../../../tests/node-compat/foundation-classic-streams/independent-corrected-followon-results-review-v1/README.md)
result reviews pass, including source/native/tool/completion seals and control
origins. These are occurrences, not globally unique binaries. Replay retains
eight fatal raw streams and one independently decoded alias return; 30 other
Wasmtime records have parsed-only or digest-only evidence. Follow-on allocator
GC has a parsed observation without raw stdout or digest; getter Node/Jco values
are parsed-only, while its Wasmtime return independently decodes. Getter/Symbol
parity remains false, GC covers combined owners and failed instances are discarded.

The [corrected HTTP source and whole-entry bundle](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-source-and-bundle-root-results.json)
pass with17 expected imports and no bundled JS built-in adapters. The
[first packaging attempt](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-packaging-attempt1-root-env-failure.json)
retains prepared inputs; build stderr asserts missing `NODE_COMPAT_WASM_TOOLS`
before output creation. Its outer terminal status was lost to context and is
not inferred. The [fresh same-input buildv2 and packaging audit](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-package-root-results.json) finish at Root-observed raw0
(session71459, explicit tool): component24d76605… is64,058,731 bytes, with the
17-import application bundle and exact six standard WASI0.2.10 interfaces;
monotonic-clock duration is type-only, with no callable clock. Production
admission completion exists; the collector verifies25 artifact references and
the7,496-input closure, including a fresh static WIT audit. The
[fresh combined host result](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-combined-root-results.json)
finishes at Root-observed raw0 for Wasmtime, wash and audit (session60088).
Both hosts return three successful responses and stop at exit0 on identical
component24d76605 bytes. [Independent result review2f5df929](../../../tests/node-compat/foundation-classic-streams/independent-corrected-http-results-review-v1/README.md)
passes all six bodies and source/native/tool/configuration evidence. Counters
are1/1/1 on each host; no instance reuse or request isolation is inferred.
Measurement is complete; targeted memory/startup, artifact/archive and acceptance remain incomplete; bounded
v12 stays accepted and the roadmap is unfinished.
The completed [measurement](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json) finishes raw0:42 calibration/126 timed workers plus final source audit,1,037 output files. [Integrity review3843d019](../../../tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and the [numerical analysis](../../node-compat/classic-stream-measurement-v1/README.md) are separate evidence. The [Root strategy decision](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the shared guest-JS stream state machine and native byte primitives; registered imports avoid a duplicate bundle and save7.85% measured component bytes, with no consistent same-engine warm-speed or memory advantage. The optional unused installation stays OFF. Stock-provider differences include a different provider/scheduler; FNV/validation stays timed and controls are not subtracted. Public RSS includes proof/V8 overhead, and raw timing-call compact returns were not retained. The smaller-worker [process RSS supplement](../../../tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v1/README.md) passed source review, but the [actual attempt](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v1-preworker-failure-root-results.json) exits1 before any worker: setup is signed32, while the probe expected strings. The corrected [v2 source](../../../tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v2/README.md) passes independent review; the [actual v2 run](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-root-results.json) finishes raw0 with18 fresh workers,126 retained typed returns,599 files and final source audit. [Independent result/numerical review](../../../tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md) passes all18 workers/126 typed returns; same-engine pre-final maximum RSS ratios cross1 and no controls are subtracted. It excludes full proof reports from workers and retains public raw returns. No private heap or production-engine performance claim follows.

Historical failures/counterexamples remain unchanged. The61-case [zlib corpus
and harness a7eca234](../../../tests/node-compat/foundation-zlib/component-validation-candidate-v1/README.md) and
[control-evidence amendment fd3ec6ef](../../../tests/node-compat/foundation-zlib/component-validation-control-evidence-amendment-v1/README.md)
retain the [240fdc77 source hold](../../../tests/node-compat/foundation-zlib/independent-component-validation-source-review-v1/README.md).
The new [bootstrap/coverage amendment a376c32b](../../../tests/node-compat/foundation-zlib/component-validation-bootstrap-coverage-amendment-v1/README.md)
(15 files/8,640 inputs) addresses the call-counter, native error-field-type and
repeated-namespace identity gaps and rebinds producer v3. Its [independent source
review654f077f](../../../tests/node-compat/foundation-zlib/independent-component-validation-coverage-source-review-v1/README.md)
passes. The [v4 publisher rebindcd458](../../../tests/node-compat/foundation-zlib/component-validation-v4-rebind-amendment-v1/README.md)
(8 files/8,770 inputs, nine publisher edits) passes [independent review74109e3f](../../../tests/node-compat/foundation-zlib/independent-component-validation-v4-rebind-source-review-v1/README.md).
The a376 payload stays exact:61 Node cases,28 full-byte fixtures,40 bindings and
107 typed constants. Separate [Root validation-only pinsb61e1f38](../../../tests/node-compat/foundation-zlib/reviewed-native-v4-validation-bootstrap-pins-v1.json)
and [review7274a874](../../../tests/node-compat/foundation-zlib/native-v4-validation-bootstrap-root-review-v1.json) bind the three actual native variants; the
normal production selector stays closed. The first activation wrapper omitted
required arguments and stopped before publication. The corrected-argument
[attempt49004](../../../tests/node-compat/foundation-zlib/validation-source-activation-attempt2-context-failure-root-results.json) then stops at a historical preparation-path
collection error; no source family or guest is published. A [context-only
amendmentf6f0e191](../../../tests/node-compat/foundation-zlib/component-validation-preparation-context-amendment-v1/README.md) is sealed, but [review541b2779](../../../tests/node-compat/foundation-zlib/independent-component-validation-preparation-context-source-review-v1/README.md) holds it on ZVCTX-M2:
the publisher treats an indexed-only peer as a preparation family and reads a
manifest that does not exist. The [Root origin correction](../../../tests/node-compat/foundation-zlib/validation-source-activation-attempt2-root-origin-correction.json)
retains the original diagnosis and records this earlier observed failure; the
later relocated-bootstrap-path issue is independently confirmed. A new publisher
correction now distinguishes those family roles explicitly. The [indexed-peer successorbd66](../../../tests/node-compat/foundation-zlib/component-validation-indexed-peer-amendment-v1/README.md) and [postseal inventory evidence5aa0](../../../tests/node-compat/foundation-zlib/component-validation-indexed-peer-regression-evidence-v1/index.json) pass [independent source review6cbe](../../../tests/node-compat/foundation-zlib/independent-component-validation-indexed-peer-source-review-v1/README.md): all8,904 inventory rows agree, required preparation manifests remain mandatory, and the indexed-only peer requires all five indexed files. Root [source activation-v3](../../../tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) finishes raw0 and publishes family8868d212 (19 files/10,964 consumed inputs). Its [generated-family review999df5f8](../../../tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) holds on ZV6-M1: four component-harness loaders are physically absent from the native stage and omitted from the consumed manifest. The [tooling successor daa7d28a](../../../tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) now passes [source review567c3214](../../../tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) and Root22 physical/source checks plus six syntax commands. [Activation-v4](../../../tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0, publishing v7/d67971d0 (21 files/11,036 inputs). Its native configured root and fully sealed component-tool root are distinct. [Generated-family review178ab2d0](../../../tests/node-compat/foundation-zlib/independent-component-validation-v7-family-review-v1/README.md) passes. The [first normal codec attempt](../../../tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) then finishes raw1 during componentization: its snapshot uses unsupported Buffer.from(Array). No component, final result or deployed codec observation is published; the failure source recheck passes. The same input kind also occurs in constructor-refusal arguments and the ordinary-GC fixture. The [three-expression Uint8Array amendment b0ced580](../../../tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) passes12 Root host-only regression checks using explicit test doubles and [independent source reviewc277823a](../../../tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md). [Fresh source activation-v5](../../../tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0 and publishes corrected v8/8af9a213 (21 files/11,107 inputs). [Generated-family review1e966afe](../../../tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md) passes. [Normal validation-v2](../../../tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile codec observations over61 cases and1,544 completion artifacts. [GC validation-v1](../../../tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) finishes raw0 with three codec cases, combined-owner ordinary-GC and fresh Wasmtime checks,49 completion artifacts. Both components import nothing. [Independent normal reviewa36758db](../../../tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC review461dec9c](../../../tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) pass. The [combined Root result review](../../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 Node/profile error-case differences (16 outcome/code, six additional errno-only), including11 originally unlabelled rows. The [per-case difference ledger](../../../tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/node-profile-difference-ledger.json) binds exact oracle/raw citations; no61-case Node parity is claimed. Source-coupled public VERNUM evidence does not rewrite metadata backend proof; operational admission remains closed. Separately, [actual disabled validation](../../../tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0 with eight pre-componentization denials, five Buffer/stub observations and imports[]; [independent result review5b199668](../../../tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) passes. This does not prove codec support or a unique cause for its generic direct-import rejection. The guest, driver, Node fixtures and native evidence remain unchanged.

The [independent timing-input review372256](../../../tests/node-compat/foundation-classic-streams/independent-composed-timing-inputs-review-v1/README.md) passes all non-authority data checks for the unapproved timing candidate and four Root prerequisite reviews. The three issuance gates remain closed: candidate state, timingAllowed:false and NOT_ISSUED quiet window. No timing has run.

The [conditional integration56a6](../../../tests/node-compat/foundation-zlib/integration-candidate-v1/README.md)
and [SDK syntax evidence e757/peer4ef](../../../tests/node-compat/foundation-zlib/independent-sdk-syntax-review-v1/README.md)
remain bounded source/syntax evidence:350 proposed native paths, two syntax
commands and1,048 dependency files (2 CPP+1,046 headers), with static `MOZ_Z_*`
mapping. Old [3ff/dafaff Z350-M1](../../../tests/node-compat/foundation-zlib/independent-native-integration-source-review-v1/README.md)
and [c65/89bc Z350-M2](../../../tests/node-compat/foundation-zlib/independent-native-integration-v2-source-review-v1/README.md)
holds remain unchanged. The [two-identifier correction c92e](../../../tests/node-compat/foundation-zlib/descriptor-shadow-amendment-v1/README.md)
and [producer v3 index3929e24d](../../../tests/node-compat/foundation-zlib/native-integration-candidate-v3/README.md)
(81 files/2,146 inputs) pass [source reviewf471ec27](../../../tests/node-compat/foundation-zlib/independent-native-integration-v3-source-review-v1/README.md).
[Root's eight source checks and isolated staging](../../../tests/node-compat/foundation-zlib/native-integration-v3-root-stage-results.json)
pass (76544/964346f9), followed by [actual stage reviewc75f3484](../../../tests/node-compat/foundation-zlib/independent-native-integration-v3-stage-review-v1/README.md):
869 exact copied rows =350 native+522 tooling−3 overlaps, plus the exact proposal
and isolated Git54b base. Original preparation context is retained.

The first ordinary Release normal-OFF attempt (Root62113) finishes at raw exit1.
It reaches the final108/108 copy entry and then postbuild evidence collection.
The actual CMake chain has one compiler `-o` and another for `wasm-opt`;
`codec.link_commands` counts both across the compound line and asserts. The
[Root failure receipt accf4b05](../../../tests/node-compat/foundation-zlib/native-integration-v3-build-attempt1-failure-root-results.json)
retains11 references, recipe/launcher exit1 and completed cleanup. No standalone
CMake exit receipt was captured. The [independent failure reviewc319](../../../tests/node-compat/foundation-zlib/independent-native-zlib-v3-build-failure-review-v1/README.md)
and [Root label clarification](../../../tests/node-compat/foundation-zlib/native-integration-v3-build-failure-labels-root-clarification.json)
retain that distinction. Raw v3 engine62d8e6d8… remains unchanged and UNADMITTED
at9,995,287 bytes, with no metadata sidecar, freeze or backend/runtime proof.

The [v4 source d384af81](../../../tests/node-compat/foundation-zlib/native-integration-candidate-v4/README.md)
(85 files/2,261 preparation inputs) passes [source review31d5408e](../../../tests/node-compat/foundation-zlib/independent-native-integration-v4-source-review-v1/README.md).
[Root checks and staging](../../../tests/node-compat/foundation-zlib/native-integration-v4-root-stage-results.json)
record nine source-check commands at0 (34385/42f14b), then plan/apply, staged
verification, factory and Git checks at0 (89971). The [independent actual-stage
review5d857788](../../../tests/node-compat/foundation-zlib/independent-native-integration-v4-stage-review-v1/README.md)
passes:979 exact copies=350 native+632 tooling−3 overlaps,85 proposal files plus
index, ordinary Git54b clone and original-context preparation references.

The one-job ordinary Release normal-OFF retry finishes at exit0 (Root69972) from
`/tmp/starling-node-compat/zlib-source-v4`, with fresh `zlib-v4-build` and
`production-zlib-v4` namespaces and2GiB start/800MiB stop guards, without
DEBUG/OOM. The separate [four-file cache preseed47668](../../../tests/node-compat/foundation-zlib/native-integration-v4-cache-preseed-root-results.json)
contains only three archive downloads and cbindgen; no engine, configuration,
source or old proof was copied. [Build, freeze and verification](../../../tests/node-compat/foundation-zlib/native-integration-v4-normal-off-root-results.json)
finish at Root-observed exit0 (69972/30705/85956). Engine fb165689… is9,995,295
bytes; all1,024 frozen copies and1,022 original references rehash. The actual
350-source build records62 native units, four strict, six private and one separate
embedding command. [Independent ordinary native reviewba0451db](../../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-normal-off-review-v1/README.md) passes.
The [GC variant](../../../tests/node-compat/foundation-zlib/native-integration-v4-gc-off-root-results.json) also finishes build/freeze/verification at exit0
(44299/71826/23840). All ordinary frozen
copies remain unchanged after the expected shared build-cache reconfiguration.
[Independent GC review90e9e6e3](../../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-gc-off-review-v1/README.md) passes. The [disabled variant](../../../tests/node-compat/foundation-zlib/native-integration-v4-disabled-off-root-results.json)
also finishes build/freeze/verification at exit0 (66192/28710/63712), and
[independent reviewac8d15ac](../../../tests/node-compat/foundation-zlib/independent-native-zlib-v4-disabled-off-review-v1/README.md) confirms its61 native/five private
commands and kernel omission. All three frozen sets remain intact. Runtime backend proof
remains false/null/null; checked-in future pins stay NULL, while the external
Root authority permits validation only. The later [bounded runtime results](../../../tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) now include normal codec, combined-owner GC and disabled-control components with independent reviews. Operational admission, explicit Node differences, matched codec costs and new-engine selected-host/release gates remain open. Historical host/ECHO vectors and syntax remain separate evidence; metadata backend-proof fields stay false. Complete `node:zlib` support is not claimed.

Enable the profile explicitly when building StarlingMonkey or its ComponentizeJS
embedding:

```sh
cmake -S . -B cmake-build-node-profile -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_BUILTIN_NODE_COMPAT=ON
```

The option defaults to OFF. Normal builds do not install these modules or global
Buffer. The profile requires the existing text-codec builtin. Its hexadecimal
kernels are native guest code; the overload/error/view semantics live in a small
JavaScript facade. Neither module adds a host service or calls WASI directly.
The final component import set still depends on the application world and
ComponentizeJS feature selection, and must be inspected after composition.

Seven independent optional foundations are compiled and tested in the
[v12 acceptance](../../../tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md).
All default to OFF and require the core option above:

| CMake option | Bounded modules |
| --- | --- |
| `NODE_COMPAT_PATH=ON` | `path`, `path/posix`, `path/win32`; fixed cwd/platform policy and bounded glob matching |
| `NODE_COMPAT_EVENTS=ON` | Synchronous EventEmitter and bounded `addAbortListener`; `once`, `on`, `EventEmitterAsyncResource` and other manifest refusals remain deferred |
| `NODE_COMPAT_STRING_DECODER=ON` | StringDecoder UTF8/hex; other known encodings throw |
| `NODE_COMPAT_ASSERT=ON` | Assert/strict scalar assertions; deep/async/CallTracker operations throw |
| `NODE_COMPAT_QUERYSTRING=ON` | Legacy Querystring with explicit input/output/field caps and deferred overloads |
| `NODE_COMPAT_UTIL=ON` | Bounded Util/types/sys;29 captured-intrinsic predicates, pure helpers and native codec aliases; remaining calls throw |
| `NODE_COMPAT_STREAM_WEB=ON` | Exactly18 stream/web exports over real native classes; bounded UTF8 codecs, iteration and ordinary DataView/BYOB adapters; compression call/new throws. Requires web streams and text-codec builtins |

The accepted private `NODE_COMPAT_INTERNAL_TICKS` queue defaults OFF and exposes
no public process/nextTick API. The experimental default-OFF
`NODE_COMPAT_CLASSIC_STREAMS` option requires Events, StringDecoder and private
ticks. Its applied source/compiled artifacts and ordinary-component result are
tracked separately from accepted runtime support; see the
[current adoption ledger](../../../tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md).

Each has its own versioned manifest and generated header, with real named/default
bindings and both canonical/bare registration. These modules add no host
capability. The checkpoint validates strict factory execution, selected bundler
imports, aliases, snapshot state and deployed errors; it is not general Node
compatibility. The [compatibility matrix](../../node-compat/compatibility-matrix.md)
and individual manifests define each bounded contract.

Events m0.10 passes 29 focused Node groups in both entropy modes, alias/CJS/
snapshot/error checks and separate fatal/discard controls. Its fresh ordinary
and protected callback returns omit Node's `.then` getter read: Node
`1/1/0` versus native `0/0/0`, ordered ordinary/protected/already-aborted.
The getters return undefined; callable-then/rejection parity is not established.
The target uses its well-known nonregistry `Symbol.dispose`, differing from
Node's `Symbol.for('nodejs.dispose')`. These are
[confirmed limitations](../../../tests/node-compat/milestones/foundations-v11/reports/callbackReturn.json).
The Release GC proof combines signal/listener/closure-held Symbol owners across eight
public hex roundtrips; it does not isolate prototype-only Symbol liveness or add
an OOM/fault result.

Stream/web retains ten corresponding native global constructor identities and
three hidden native class constructors. Its codec constructors are module-only.
Input limits are1Mi UTF16 units per encoder chunk and16MiB per decoder/BYOB
input; fixed attached unshared local unmodified views and min1 only. These caps
do not bound total retained queues or output. Writable-controller signal,
Proxy/layout/cross-realm inputs, several native error codes and controller arity
remain gaps. Both OFF import names fail bundling and actual initialization;
no adapter fallback occurs. See the [m0.9 manifest](../../../builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json)
and [executed native gates](../../../tests/node-compat/foundation-stream-web/production-adoption/README.md).

## Supported Buffer subset

| API | Contract |
| --- | --- |
| `Buffer.alloc(size, fill?)` | Integer size from 0 to 16 MiB; numeric fill only, zero by default. No pool. |
| `Buffer.allocUnsafe(size)` | Primitive finite raw number from0 through16MiB; accepted fractions truncate. After unchanged validation, m0.11 directly returns privately branded captured native Uint8Array storage: fresh exact zeroed backing at offset0, no pool. This intentionally differs from Node's uninitialized/slab storage; allocUnsafeSlow remains deferred. |
| `Buffer.from(string, encoding?)` | UTF-8 (`utf8`, `utf-8`) or hexadecimal (`hex`), case-insensitive. At most 1,048,576 UTF-16 source units. Hex truncates at the first invalid pair and drops an odd final nibble. |
| `Buffer.from(Uint8Array)` | Copies the visible bytes to independent storage. |
| `Buffer.from(ArrayBuffer, offset?, length?)` | Shares fixed-length backing storage; nonnegative integer offset/length only; view length at most 16 MiB. |
| `Buffer.isBuffer`, `Buffer.isEncoding` | Private instance brand and explicit profile encoding allowlist. |
| `Buffer.byteLength` | Selected string encodings, fixed attached ArrayBuffer or Uint8Array. Shared, resizable and detached storage is rejected. |
| `buf.toString(encoding?, start?, end?)` | UTF-8 or hex; integer range arguments with clipping. UTF-8 preserves a leading BOM and replaces malformed input. |
| `buf.slice`, `buf.subarray` | Shared backing storage and Buffer identity, with Uint8Array range normalization. |
| `.buffer`, `.byteOffset`, `.byteLength`, `.length`, indices, `.parent`, `.offset` | Real Uint8Array backing relationships and legacy view aliases. |

Core m0.11 adds no exports, encodings, C++ allocation kernel, raw byte borrow or
allocator transfer. The same JS-owned zeroing and 16 MiB cap apply; acceptance
establishes bounded correctness, not a current performance or memory advantage.

Instances have genuine typed-array internal slots. Both constructor and prototype
inherit from Uint8Array; species operations such as map/filter create independent
Buffer instances. Inherited Uint8Array operations remain available except methods
that Node overloads and this profile explicitly rejects.

Array-like/valueOf/JSON input, non-Uint8 typed arrays, DataView, SharedArrayBuffer,
resizable backing storage for construction, the legacy Buffer constructor,
additional encodings, numeric readers/writers, copying/searching/writing/fill
methods, concat, uninitialized allocation, allocUnsafeSlow and full inspection/serialization are outside
the subset. Invalid supported arguments use selected Node error codes; excluded
overloads throw `ERR_SM_NODE_UNSUPPORTED`. Full coercion, error-order and message
parity are not promised.

The finite manifest accounts for every Node 22 `node:buffer` export. Blob, File,
SlowBuffer, atob, btoa, isAscii, isUtf8, resolveObjectURL and transcode are explicit
throwing callable bindings in this milestone. Constants remain numeric:
`INSPECT_MAX_BYTES` is 50, `kMaxLength`/`constants.MAX_LENGTH` are 16 MiB and
`kStringMaxLength`/`constants.MAX_STRING_LENGTH` are 32 MiB. These are profile caps,
not Node's platform maxima; memory pressure may still cause allocation failure.

## Module and bundler contract

Native installation uses the existing `add_builtin` and
`api::Engine::define_builtin_module`. Both `node:` and bare aliases are registered
with the same exported values. Global Buffer is the same constructor as the
module export. Namespace objects remain cached by specifier; aliases need not
have equal namespace-object identity unless the bundler canonicalizes them.

In the core Buffer/stub modules, every named export equals the corresponding
default-object member; their defaults and constants are frozen. Optional
foundations have their own declared default graphs: Path/Querystring/StringDecoder
defaults are mutable objects, Events/Assert defaults are mutable functions, and
named bindings retain the initially registered references. There is no runtime CommonJS loader or
`syncBuiltinESMExports` mutation protocol. Unknown names fail ESM linking;
unadmitted modules have no implicit empty stub.

A bundler must preserve the selected native imports before an adapter plugin can
replace them. The finite resolver in `tests/node-compat/profile-bundler.mjs`
canonicalizes modules selected by the actual engine receipt, externalizes their `node:` imports,
rejects other builtins/custom adapters, and lowers a deliberately narrow literal
CommonJS require contract for local `.cjs` files imported by explicit path. It is
not a general npm CommonJS package loader. Applications using Jco's default Node
adapter bundling
do not automatically use this native profile. Global injection must use the
canonical native Buffer and must not bring in another Buffer implementation.

`node:child_process` has nine callable exports plus default: ChildProcess,
_forkChild, exec, execFile, execFileSync, execSync, fork, spawn and spawnSync.
Calls and construction always throw an Error with `code`, `module`, `operation`
and `profile` fields. This applies during snapshot initialization and deployed
execution. Importing and inspecting the namespace/default object is safe; neither
is an accidental thenable. No process-spawn or custom host capability is imported.

## Native ownership and generated sources

The byte kernels allocate JS-managed typed arrays or owned staging memory. All
JS objects/strings are rooted across allocation. Typed-data pointers are borrowed
only inside no-GC regions, after allocation and validation, and never retained
across a callback or suspension. Hex encoding copies owned staging bytes into a
JS string. The production UTF8 encoder now writes directly into an exactly sized
GC-owned Uint8Array; TextDecoder owns its UTF16 staging allocation and releases
the borrowed input before result-string creation. These remain distinct paths,
without a blanket zero-copy claim. No Rust/C++ allocation is implicitly
transferred to an incompatible allocator.

Fresh, bounded outputs from captured native producers receive prototype and
private WeakSet branding without reading their backing-buffer getter. This
avoids materializing SpiderMonkey's small inline arrays unnecessarily. External
inputs and observable species/view outputs keep full validation. The
[allocation follow-up](../../node-compat/buffer-optimization-and-abi-fix.md)
records the mechanism, matched experiment and limits.

The facade and stub sources and their versioned manifest live under
`builtins/node-compat`. The checked-in generated factory header keeps normal CMake
builds independent of Node/npm. The accompanying deterministic generator checks
that the header agrees with those sources and validates the manifest against its
[versioned restricted schema](../../node-compat/manifest-validation.md).
Factories execute as strict script in the content realm
after native text codecs are installed, before application module evaluation.

`NODE_COMPAT_GC_STRESS` is a development-only build setting for forced collection
at rooted kernel boundaries. It is not a Node API or host capability. It must not
be enabled for performance measurements.

## Integration validation

`tests/node-compat` builds the pinned ComponentizeJS embedding against this source
and tests surviving native imports, aliases, CommonJS conversion, global identity,
the Buffer subset and predictable stub failures. The runner requires an explicit
custom engine, an exact Node v22.14.0 oracle and Wasmtime 42.0.1. It validates final
imports against the empty allowlist for the pure test world.

Earlier normal and compacting-GC-stress native engines passed the full component
suite on Wasmtime 42.0.1: 381 string vectors and 250 byte-array vectors against
Node v22.14.0, shared/copying views, native static/dynamic imports and aliases,
snapshot state, CommonJS/global identities, 91 unavailable Buffer methods and all
nine child-process callable exports. Direct/constructed/awaited top-level stub
calls and unknown named imports failed componentization. Both final test
components had zero host imports. SharedArrayBuffer was not exposed by the engine,
so native shared-input construction tests were skipped explicitly.

The accepted [v11 release batch](../../../tests/node-compat/milestones/foundations-v11/reports/releaseEight.json)
contains eight passing gates: five successful same-engine results were reverified,
and three strict suites ran fresh after a preserved storage failure. The first
allocator attempt's missing `pathToFileURL` import was a harness failure, also
preserved before its successful fresh retry. Neither failure changes native
source or establishes failure reuse.

The new [allocator GC gate](../../../tests/node-compat/milestones/foundations-v11/reports/allocatorGc.json)
covers three retained Jco calls and fresh Wasmtime, with eight valid native hex
roundtrips per call; it is narrower than rerunning the full byte corpus under GC.
The [19 focused Events components](../../../tests/node-compat/milestones/foundations-v11/reports/focusedReceipt.json)
retain the callback getter/Symbol counterexamples and combined-owner limitation.
No new genuine OOM/fault result, ALS or request teardown is established.

The same v11 HTTP component, SHA-256
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`,
passes three requests on stock Wasmtime 42.0.1 and official wash 2.11.0; both stop
with exit 0. Its [six exact standard 0.2.10 imports](../../../tests/node-compat/milestones/foundations-v11/reports/httpAudit.json)
are `wasi:http/types`, `wasi:io/{error,poll,streams}`, `wasi:random/random` and
type-only `wasi:clocks/monotonic-clock` for `duration`. No clock function, outgoing
HTTP, socket, DNS, TLS, filesystem, CLI/environment or custom service is inferred.
Counters `[1,1,1]` on both hosts prove neither same-instance reuse nor request
isolation. The [immutable checkpoint](../../../tests/node-compat/milestones/foundations-v11/README.md)
records all three current engines and their exact sources and configuration.

The following v10 and earlier results retain their historical artifact scope.

The historical v10 release batch replays the core and prior foundations, with
four source-pinned engines sharing 304 native inputs and 33 primary reports.
Exact hashes, configs and executed scope are in the
[immutable checkpoint](../../../tests/node-compat/milestones/foundations-v10/results.json).
Its separate combined-owner GC gate is narrower than rerunning the entire byte
corpus under a new GC engine.

That v10 HTTP component, SHA-256
`0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610`,
passes three requests on stock Wasmtime 42.0.1 and official wash 2.11.0; both stop
with exit 0. Its [six exact standard 0.2.10 imports](../../../tests/node-compat/milestones/foundations-v10/reports/http-audit.json)
are `wasi:http/types`, `wasi:io/{error,poll,streams}`, `wasi:random/random` and
type-only `wasi:clocks/monotonic-clock` for `duration`. Random is explicitly
selected; no clock function, outgoing HTTP, socket, DNS, TLS, filesystem,
environment or custom service is inferred. Counters are `[1,1,1]` on both hosts;
this proves neither same-instance reuse nor request isolation. The corrected
Wasmtime-v2 result and failed first harness attempt are preserved separately.

The HTTP packaging script uses a hash-guarded composition of the pinned stock
splicer's real APIs to keep manual HTTP bindings while removing outgoing HTTP.
It restores its process-local function replacement afterward. The native engine,
installed npm files and host binaries remain unchanged. Its final core has no
Preview1 imports and is wrapped without an adapter. These packaging details and
the exact emitted type graph are part of the reproduction record.

The [A/B measurement results](../../../tests/node-compat/bench/README.md)
compare supported operations with Jco's actual Buffer adapter using the same
release engine and capability-free world. Conversion throughput improved in the
measured non-Weval mode; copying throughput was about 4–15% lower, and peak memory
was higher in some small-buffer cases. The
[result summary](../../node-compat/portability-and-performance.md) separates those
tradeoffs from component size and startup observations. A separate
[ABI diagnostic](../../../tests/node-compat/bench/abi-results.json) reproduced
incorrect high-`u32` result transport without Buffer code. The current build
recipe applies a versioned guest-source patch for scalar export results; its
[direct regression](../../../tests/node-compat/abi-fix/README.md) passes 339 Jco
checks and direct Wasmtime controls. This is a local ComponentizeJS guest patch,
not a fix in released 0.23.0. A separately reproduced high-`u32` imported-callback
argument defect required a separate imported-I32 splicer patch; the current
explicit v2 packager includes that correction and the disabled-clock errno fix.
Both fixes have separate pinned source/provenance gates. Benchmark checksums retain signed
`s32` to preserve their original matched protocol.

The original architecture audit and frozen semantic templates are in
`docs/node-compat`; their released-engine/reference-kernel results must not be
confused with tests of the current native implementation. Complete Node
semantics, exhaustive OOM injection, shared input construction, concurrent
request isolation and production cluster deployment remain separate gates.

Current [corrected-clock](../../../tests/node-compat/bench-clock-v2/RESULTS.md)
and [Weval](../../../tests/node-compat/weval-experiment/v5/RESULTS.md) measurements
retain their own exact engines and workload limits. Native byte codecs improve
the measured throughput, while small copying constructors and several memory
cases remain counterexamples. The copying scenario calls `Buffer.from(existing
Buffer)`; it does not validate the still-deferred `Buffer.prototype.copy` API.
