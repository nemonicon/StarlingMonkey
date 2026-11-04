# Node compatibility profile progress

Last updated: 2026-11-04. Overall roadmap: **in progress**.

This file tracks completed work, work in progress, and outstanding gates for the
portable StarlingMonkey Node compatibility profile. It is not a claim of complete
Node.js or Buffer support. The detailed [execution ledger](docs/node-compat/execution-status.md),
[API matrix](docs/node-compat/compatibility-matrix.md), and
[dependency-ordered roadmap](docs/node-compat/roadmap.md) contain the underlying
contracts and evidence. No overall completion percentage is assigned: remaining
phases have substantially different sizes and unresolved design decisions.

## Current work at a glance

| Work | Status | Next required step |
| --- | --- | --- |
| Architecture audit, API matrix, roadmap, Buffer and explicit-stub baseline | Delivered; implementations and templates are distinguished below. | Keep the bounded compatibility contract and known deviations explicit. |
| Accepted production checkpoint | Bounded foundations-v12. | Complete corrected-source gates before accepting a successor. |
| Corrected classic streams | Full 20-workload/14-boundary gate passes all 105 observations; fresh replay, follow-on and HTTP gates pass. | Finish the performance comparison and corrected checkpoint review. |
| Corrected HTTP component | Both hosts, combined audit and independent final review pass. | Include the result in the corrected checkpoint and timing prerequisites. |
| Performance comparison | All168 workers and final source audit finish raw0; integrity and numerical reviews pass. | Record bounded strategy/cost decisions. A smaller RSS/startup probe is being prepared to avoid retaining proof reports in measured workers. |
| Native zlib extension | Three native builds/freezes and the disabled-component result pass independent review. Normal and GC codec runs and their independent result reviews pass, within the bounded contract. | Review the bounded results and Node differences, then close operational admission and cost gates. |
| Stream consumers | Corrected355-source proposal passes source review and real SDK registration syntax ON/OFF. It remains uninstalled. | Finish reviewed producer/staging/native/runtime gates; Blob-dependent operations remain refusals. |
| Final corrected checkpoint | Outstanding. | Review results, preserve the artifact closure, and issue a separate bounded acceptance decision. |

The detailed evidence below also retains failed attempts. A source check, syntax
check, packaged component, runtime test and accepted checkpoint are separate
completion states.

The [timing-input candidate](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-phase-candidate-v1.UNREVIEWED.json) now names the exact composed correctness, full20+14, replay/follow-on and HTTP reports. Its four Root prerequisite reviews are recorded, and Root pure/syntax checks pass. The historical candidate remains unapproved (`timingAllowed:false`). A separate [Root-issued phase](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-composed-timing-phase-v1.json) and [quiet-window receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-window-root-review-v1.json) now authorize the unchanged protocol. The real read-only preflight finishes raw0; measurement finishes at Root-observed raw0 with all42 calibration/126 timed workers and final source audit complete. The [Root result](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json), [integrity review](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and [numerical report](docs/node-compat/classic-stream-measurement-v1/README.md) pass. Registered binding saves7.85% component bytes but has no consistent same-engine warm-speed advantage; the stock-provider comparison also retains higher RSS counterexamples. Raw per-timing-call checksum strings were not saved: checks are authenticated-code/terminal supported, separate from full308-observation correctness. The coordinated quiet window has ended. Additional process RSS/startup work will exclude proof reports from workers; no guest-heap claim follows.

The [corrected zlib harness](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) now passes [generated-family review](tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md). [Normal validation-v2](tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile records across61 cases. [GC validation-v1](tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) also finishes raw0 with three codec cases and combined-owner ordinary-GC checks under Jco/fresh Wasmtime. Both import nothing. [Independent normal](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC](tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) reviews pass. The [combined Root receipt](tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 error-case differences and source-coupled VERNUM4880 versus Node4865; no complete parity or temporary-root-isolation claim follows. The [first fixture failure](tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) remains preserved; its three unsupported Array inputs were changed to supported Uint8Array inputs without expanding Buffer.

The [disabled-component run](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) and [independent result review](tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) pass: eight bundler denials, five complete Buffer/stub observations, zero imports,50 completion files and one output link. Generic direct-import rejection does not uniquely prove its cause; codec/backend proof, operational admission and request reuse are not inferred.

The [consumers proposal](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/README.md) is source-only. Its [independent review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-source-review-v1/README.md) holds on CONS355-M1: two post-link paths name a missing child codec-evidence.py instead of the authenticated parent350 helper. The [v2 successor](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/README.md) and [independent source review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-v2-source-review-v1/README.md) now pass (39 files/506 inputs). Native355 payload bytes remain unchanged. [Actual SDK frontend checks](tests/node-compat/foundation-stream-consumers/sdk-registration-syntax-v1/README.md) pass consumer ON/OFF with empty diagnostics and1,036/1,035 dependency hashes. This is syntax/API evidence only; no355 configure/build/link/install or runtime action has run. The genuine355 producer is being prepared with distinct native/tool/original-preparation contexts. Positive Web inputs must select the existing node:stream/web iteration wrapper; raw global ReadableStream is not implicitly adapted.

The [artifact-closure and rollforward plan](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-closure-plan-v1/README.md) checks17,885 files and maps five live Root changes, but preservation and independent plan review remain required. Old absolute source references must use an explicit archived-context reader; old preflight rerunnability is not inferred. Current350/355 preparation dependencies are being audited before any live promotion. No bulk archive or Root source promotion has occurred.

## Detailed evidence and limits

Current position: **foundations-v12 is accepted, bounded**, through the
[Root acceptance receipt](tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md).
All private scheduler diagnostic and production gates pass, including fresh
eight-stage replay, allocator/focused GC and same-byte HTTP on both stock hosts.
The public API versions remain unchanged; no public process/nextTick/ALS API
was added. Known getter, Symbol, ownership, reset/reuse and performance limits
remain explicit. The original classic342 layer is applied: four Release variants are
frozen and three bounded classic component suites pass with independent reviews.
Its original-generation runtime gates and independent reviews are complete:40 replay,
20 followon,15 classic and one combined HTTP component occurrences. The
[runtime composition receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/runtime-gates-complete-v1.json)
does not claim76 globally unique binaries. New Node-host workload comparisons
retain14 trace counterexamples against the canonical factory. The unchanged
original342 component reproduces four minimal Node gaps on three retained
Jco calls and fresh Jco/Wasmtime, with independent result verification. The
expanded11-case run adds two object-encoding differences (six total); its
independent result review passes. The
[six-gap acceptance hold](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-acceptance-hold-v2.json)
keeps the old-source counterexamples separate from corrected-source proof.
The [corrected source generation](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
retains four reviewed production freezes, 474 files each, and its reviewed
26-file runtime family with 6,414 consumed inputs and 22 tool links. The three
[corrected classic suites](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-classic-runtime-root-results-v1.json)
finish at Root-observed exit 0, publishing 90/91/90 files and 15 component
occurrences. OFF/GC import nothing; RuntimeOnly imports only
`wasi:random/random@0.2.10`. The [independent all-four result review](tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md),
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

Diagnostic producer-v3 has successful [ON](tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-on-native-root-results.json)
and [OFF](tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-off-native-root-results.json)
build/freeze/read-only checks, each at exit 0 with 109 build steps and 525 frozen
files. Independent native reviews [ON `c05afb8d…`](tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-on-native-review-v1/README.md)
and [OFF `ca2debb8…`](tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-off-native-review-v1/README.md)
pass. Root's separate [ON-only pins](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-on-pins.json)
(`2e9811a5…`) and [authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-on-root-review-receipt.json)
(`9681578e…`) do not constitute a measurement pair. A separate
[actual pair review](tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-pair-root-review-receipt.json)
now authenticates both variants and their independent proofs, rechecking 525
frozen copies and 521 original references per variant. Its
[pair pins](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-pair-pins.json)
are `f3626851…`; the earlier ON-only authority remains unchanged. This permits
source preparation, with timing still disabled.
The [correctness companion138a](tests/node-compat/foundation-classic-streams/measurement-correctness-candidate-v1/README.md),
mandatory [reporting amendment0558](tests/node-compat/foundation-classic-streams/measurement-correctness-reporting-amendment-v1/README.md)
and [source review c695](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-source-review-v1/README.md)
remain bound to the [ce2f activator](tests/node-compat/foundation-classic-streams/measurement-correctness-activation-candidate-v1/README.md)
(19 files/6,908 inputs, 27 Root source checks and [peer ee4d5](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-activation-source-review-v1/README.md)).
[Source activation and artifact preflight](tests/node-compat/foundation-classic-streams/production-adoption-v1/correctness-source-activation-and-preflight-root-results.json)
pass, creating family `4728c365…f33f49` (21 files/7,489 inputs), whose
[generated-family review634077e4](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-family-review-v1/README.md) passes.

The [first full 20-workload/14-boundary attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-timeout-attempt1-root-results.json)
(`e8165564…`, session90660) exits 1 after a 55-second Wasmtime child timeout.
It publishes no final result, completion or semantic counterexample. The
original timed-out case is unknown; unretained Jco observations cannot count as
passes. The [independent failure review c5a0a80f](tests/node-compat/foundation-classic-streams/independent-workload-timeout-failure-review-v1/README.md)
passes within that evidence scope. Separate fresh case0 Jco and Wasmtime
controls match the full Node oracle. A [separate fresh case5 control](tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-public-case5-root-results.json)
(`793a2f0d…`, session16818) returns child exit 0 after 177.338 operational seconds
under a 600-second cap; its complete trace, setup and checksum equal Node case5.
This proves neither the original timeout's case/cause nor deadline adequacy for
all cases or a performance result. The original failure remains unchanged.

The [persistence amendment60a8687e](tests/node-compat/foundation-classic-streams/measurement-correctness-persistence-amendment-v1/README.md)
and [peer6fb6](tests/node-compat/foundation-classic-streams/independent-correctness-persistence-source-review-v1/README.md)
lead through the reviewed v2 activator to [source418ff8fe](tests/node-compat/foundation-classic-streams/measurement-correctness-activated-v2/README.md)
(22 files/7,542 inputs; [family peer c30b596a](tests/node-compat/foundation-classic-streams/independent-correctness-v2-family-review-v1/README.md)).
The [fresh full v2 run](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-workload-v2-root-results.json)
finishes at Root-observed raw exit0 (session66794, receipt `6218afd5…`).
[Independent result review0f59a0da](tests/node-compat/foundation-classic-streams/independent-workload-v2-results-review-v1/README.md)
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

The separate [measurement-execution source4b6fdfa5](tests/node-compat/foundation-classic-streams/measurement-execution-candidate-v1/README.md)
has 43 files/7,004 inputs. [Independent review96bc44a3](tests/node-compat/foundation-classic-streams/independent-measurement-execution-source-review-v1/README.md)
requires mandatory M1 deadline/capture fixes and permits no activation. A
[new amendment](tests/node-compat/foundation-classic-streams/measurement-execution-deadline-amendment-v1/README.md) is sealed at index `b0975b54…` (25 files/7,112 inputs), with 36 source/reversal,
18 pure deadline and 11 syntax checks. Its [independent source review](tests/node-compat/foundation-classic-streams/independent-measurement-execution-deadline-source-review-v1/README.md)
passes (`9e602ec9…`). Root's fresh source/reversal and pure deadline checks
also pass, with seven syntax checks. Source activation of the mandatory
successor finishes at Root-observed exit 0 (session69131), publishing index
`1b801439…07612` with 35 files and 7,709 consumed inputs. Both read-only
variant preflights pass at exit 0 (session24691), recorded in the
[source and preflight receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-source-and-preflights-root-results.json).
The [independent family review](tests/node-compat/foundation-classic-streams/independent-common-byte-v2-family-review-v1/README.md)
passes (`4e986ca1…`). The [four-arm attempt25227](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json) finishes at raw exit1 in the
host stock graph checker before stock componentization. The inventory has no
`provider` field; its three original guest paths are explicit sourceBeforeAfter
rows. Native-on, canonical-on and canonical-off completed their full arms.
[Independent reviewbf9fa2a6](tests/node-compat/foundation-classic-streams/independent-common-byte-v2-three-arm-failure-review-v1/README.md) verifies231 durable observations against
all14 Node oracles, identity/probes, raw calls and final source closure. A new
[stock-only correction and composition source](tests/node-compat/foundation-classic-streams/measurement-stock-composition-candidate-v1/README.md) passes
[independent reviewddbbe2a7](tests/node-compat/foundation-classic-streams/independent-stock-graph-composition-source-review-v1/README.md). Root source checks pass; a separate
[three-arm authorityafdbc0bc](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-common-byte-three-arms-for-stock-only-v1.json) permits fresh stock execution.
[Stock run91122](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-stock-only-root-results-v1.json) and [composition12839](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composition-root-results-v1.json) finish
at exit0. [Independent actual reviewab100c83](tests/node-compat/foundation-classic-streams/independent-common-byte-stock-and-composition-results-review-v1/README.md) verifies all308
observations against14 Node cases, exact raw calls, component/graph data and
each arm origin. Both required actual-proof documents are indexed. Original
source1b801, arm records and parent exit1 stay unchanged; this is new composed
evidence, not a pass for the original failed run. Timing was still disabled at that preparation checkpoint. Checked-in future
authority templates stay NULL; the external timing phase does not exist and
no timing has run.

The [corrected replay producer8851](tests/node-compat/foundation-classic-streams/trace-replay-activation-candidate-v1/README.md)
passes [source review c373](tests/node-compat/foundation-classic-streams/independent-trace-replay-activation-source-review-v1/README.md)
and its source activation creates [family a08aec2d](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-source-activation-root-results.json)
with 83 files and 2,293/2,292 root/capability inputs; [generated-family review8529](tests/node-compat/foundation-classic-streams/independent-trace-replay-family-review-v1/README.md) passes.
Root's [preflight environment failure](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflight-attempt1-root-env-failure.json)
is preserved: native OFF/RuntimeOnly/GC pass, then Release OFF lacks the required
explicit `NODE_COMPAT_WASMTIME`. The [corrected-environment retry and combined preflights](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflights-root-results.json)
pass without source/native changes or a guest in those preflight attempts.
The [fresh eight-stage replay](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-release-replay-root-results.json)
then passes at Root-observed exit 0, covering six optional foundations and 40
component occurrences, including one fresh historical control. All import
nothing. Five allocator-GC/focused/getter follow-ons also pass, with
[20 component import audits](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-followon-imports-root-results.json):
only the eight RuntimeOnly components import standard random@0.2.10.
Independent [replay6a67](tests/node-compat/foundation-classic-streams/independent-corrected-replay-results-review-v1/README.md)
and [follow-on d116](tests/node-compat/foundation-classic-streams/independent-corrected-followon-results-review-v1/README.md)
result reviews pass, including source/native/tool/completion seals and control
origins. These are occurrences, not globally unique binaries. Replay retains
eight fatal raw streams and one independently decoded alias return; 30 other
Wasmtime records have parsed-only or digest-only evidence. Follow-on allocator
GC has a parsed observation without raw stdout or digest; getter Node/Jco values
are parsed-only, while its Wasmtime return independently decodes. Getter/Symbol
parity remains false, GC covers combined owners and failed instances are discarded.

The [corrected HTTP source and whole-entry bundle](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-source-and-bundle-root-results.json)
pass with17 expected imports and no bundled JS built-in adapters. The
[first packaging attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-packaging-attempt1-root-env-failure.json)
retains prepared inputs; build stderr asserts missing `NODE_COMPAT_WASM_TOOLS`
before output creation. Its outer terminal status was lost to context and is
not inferred. The [fresh same-input buildv2 and packaging audit](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-package-root-results.json) finish at Root-observed raw0
(session71459, explicit tool): component24d76605… is64,058,731 bytes, with the
17-import application bundle and exact six standard WASI0.2.10 interfaces;
monotonic-clock duration is type-only, with no callable clock. Production
admission completion exists; the collector verifies25 artifact references and
the7,496-input closure, including a fresh static WIT audit. The
[independent packaging review](tests/node-compat/foundation-classic-streams/independent-corrected-http-package-review-v1/README.md)
passes (`62dbb34b…`), including the public component/core/type graph and actual
application bundle. A separate [Root phase](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-component-phase-root-review-v1.json)
binds these exact bytes (`b7cfeb6b…`). Fresh Wasmtime/wash runs and their combined
audit finish at Root-observed exit0 in session60088. The
[combined Root receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-combined-root-results.json)
(`6c4eb6de…`) rechecks 29 evidence files and all 7,496 source rows. Each host
returns three successful responses and stops at exit0; both counter sequences
are1/1/1. The [independent final result review](tests/node-compat/foundation-classic-streams/independent-corrected-http-results-review-v1/README.md)
passes (`2f5df929…`), independently checking all six responses and the deployment,
configuration and source/native/tool evidence. No instance reuse or request
isolation is inferred.
Measurement is complete; targeted memory/startup, artifact/archive and acceptance remain incomplete; bounded v12 stays accepted and the roadmap is unfinished.
The completed [measurement](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json) finishes raw0:42 calibration/126 timed workers plus final source audit,1,037 output files. [Integrity review3843d019](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and the [numerical analysis](docs/node-compat/classic-stream-measurement-v1/README.md) are separate evidence. The [Root strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v1.json) retains the shared guest-JS stream state machine and native byte primitives; registered imports avoid a duplicate bundle and save7.85% measured component bytes, with no consistent same-engine warm-speed or memory advantage. The optional unused installation stays OFF. Stock-provider differences include a different provider/scheduler; FNV/validation stays timed and controls are not subtracted. Public RSS includes proof/V8 overhead, and raw timing-call compact returns were not retained. A smaller RSS/startup supplement is being prepared; no private heap or production-engine performance claim follows.

Historical failures/counterexamples remain unchanged. The61-case [zlib corpus
and harness a7eca234](tests/node-compat/foundation-zlib/component-validation-candidate-v1/README.md) and
[control-evidence amendment fd3ec6ef](tests/node-compat/foundation-zlib/component-validation-control-evidence-amendment-v1/README.md)
retain the [240fdc77 source hold](tests/node-compat/foundation-zlib/independent-component-validation-source-review-v1/README.md).
The new [bootstrap/coverage amendment a376c32b](tests/node-compat/foundation-zlib/component-validation-bootstrap-coverage-amendment-v1/README.md)
(15 files/8,640 inputs) addresses the call-counter, native error-field-type and
repeated-namespace identity gaps and rebinds producer v3. Its [independent source
review654f077f](tests/node-compat/foundation-zlib/independent-component-validation-coverage-source-review-v1/README.md)
passes. The [v4 publisher rebindcd458](tests/node-compat/foundation-zlib/component-validation-v4-rebind-amendment-v1/README.md)
(8 files/8,770 inputs, nine publisher edits) passes [independent review74109e3f](tests/node-compat/foundation-zlib/independent-component-validation-v4-rebind-source-review-v1/README.md).
The a376 payload stays exact:61 Node cases,28 full-byte fixtures,40 bindings and
107 typed constants. Separate [Root validation-only pinsb61e1f38](tests/node-compat/foundation-zlib/reviewed-native-v4-validation-bootstrap-pins-v1.json)
and [review7274a874](tests/node-compat/foundation-zlib/native-v4-validation-bootstrap-root-review-v1.json) bind the three actual native variants; the
normal production selector stays closed. The first activation wrapper omitted
required arguments and stopped before publication. The corrected-argument
[attempt49004](tests/node-compat/foundation-zlib/validation-source-activation-attempt2-context-failure-root-results.json) then stops at a historical preparation-path
collection error; no source family or guest is published. A [context-only
amendmentf6f0e191](tests/node-compat/foundation-zlib/component-validation-preparation-context-amendment-v1/README.md) is sealed, but [review541b2779](tests/node-compat/foundation-zlib/independent-component-validation-preparation-context-source-review-v1/README.md) holds it on ZVCTX-M2:
the publisher treats an indexed-only peer as a preparation family and reads a
manifest that does not exist. The [Root origin correction](tests/node-compat/foundation-zlib/validation-source-activation-attempt2-root-origin-correction.json)
retains the original diagnosis and records this earlier observed failure; the
later relocated-bootstrap-path issue is independently confirmed. A new publisher
correction now distinguishes those family roles explicitly. The [indexed-peer successorbd66](tests/node-compat/foundation-zlib/component-validation-indexed-peer-amendment-v1/README.md) and [postseal inventory evidence5aa0](tests/node-compat/foundation-zlib/component-validation-indexed-peer-regression-evidence-v1/index.json) pass [independent source review6cbe](tests/node-compat/foundation-zlib/independent-component-validation-indexed-peer-source-review-v1/README.md): all8,904 inventory rows agree, required preparation manifests remain mandatory, and the indexed-only peer requires all five indexed files. Root [source activation-v3](tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) finishes raw0 and publishes family8868d212 (19 files/10,964 consumed inputs). Its [generated-family review999df5f8](tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) holds on ZV6-M1: four component-harness loaders are physically absent from the native stage and omitted from the consumed manifest. The [tooling successor daa7d28a](tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) now passes [source review567c3214](tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) and Root22 physical/source checks plus six syntax commands. [Activation-v4](tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0, publishing v7/d67971d0 (21 files/11,036 inputs). Its native configured root and fully sealed component-tool root are distinct. [Generated-family review178ab2d0](tests/node-compat/foundation-zlib/independent-component-validation-v7-family-review-v1/README.md) passes. The [first normal codec attempt](tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) then finishes raw1 during componentization: its snapshot uses unsupported Buffer.from(Array). No component, final result or deployed codec observation is published; the failure source recheck passes. The same input kind also occurs in constructor-refusal arguments and the ordinary-GC fixture. The [three-expression Uint8Array amendment b0ced580](tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) passes12 Root host-only regression checks using explicit test doubles and [independent source reviewc277823a](tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md). [Fresh source activation-v5](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0 and publishes corrected v8/8af9a213 (21 files/11,107 inputs). [Generated-family review1e966afe](tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md) passes. [Normal validation-v2](tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile codec observations over61 cases and1,544 completion artifacts. [GC validation-v1](tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) finishes raw0 with three codec cases, combined-owner ordinary-GC and fresh Wasmtime checks,49 completion artifacts. Both components import nothing. [Independent normal reviewa36758db](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC review461dec9c](tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) pass. The [combined Root result review](tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 Node/profile error-case differences (16 outcome/code, six additional errno-only), including11 originally unlabelled rows. The [per-case difference ledger](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/node-profile-difference-ledger.json) binds exact oracle/raw citations; no61-case Node parity is claimed. Source-coupled public VERNUM evidence does not rewrite metadata backend proof; operational admission remains closed. Separately, [actual disabled validation](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0 with eight pre-componentization denials, five Buffer/stub observations and imports[]; [independent result review5b199668](tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) passes. This does not prove codec support or a unique cause for its generic direct-import rejection. The guest, driver, Node fixtures and native evidence remain unchanged.

The [independent timing-input review372256](tests/node-compat/foundation-classic-streams/independent-composed-timing-inputs-review-v1/README.md) passes all non-authority data checks for the unapproved timing candidate and four Root prerequisite reviews. The three issuance gates remain closed: candidate state, timingAllowed:false and NOT_ISSUED quiet window. No timing has run.

### Zlib preparation history

The following preparation record predates the current normal-v2 run; the overview above states the current gates. Failed attempts and source-only evidence remain separate from actual component results.

The [source activation-v3 receipt](tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) records raw exit0, new family8868d212 (19 indexed files/10,964 consumed inputs, two tool trees/22 links), and the unchanged three actual350 tuples. Root then found that the configured native stage lacks the component harness loaders (`toolchain.mjs`, `componentizer.mjs`, `profile-bundler.mjs` and `foundations/native-scalar-harness.mjs`). The input manifest also omits them. [Generated-family review999df5f8](tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) confirms ZV6-M1; no known-failing component run was started. A separate, fully sealed component-tool closure is required while preserving actual native source authority. The [tooling successor daa7d28a](tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) is sealed (15 files/11,015 inputs). [Root checks](tests/node-compat/foundation-zlib/component-tool-closure-root-source-results-v1.json) pass22 physical/source checks and six syntax commands. [Independent source review567c3214](tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) passes; [Fresh activation-v4](tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0 and publishes v7/d67971d0 (21 files/11,036 inputs). Generated-family review178ab passes; normal attempt1 raw1 fails at the unsupported array fixture before component publication. No deployed codec observation is available. Its configured native root remains separate from nine local tool modules, eight selected data/adapter files and package-resolution checks. The [three-input fixture amendmentb0ced580](tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) is sealed and passes12 Root host-only checks using the actual frozen Buffer/zlib facades with explicit reference-hex/Node-codec test doubles. Old six constructor argument errors came from Buffer; the corrected68 zlib refusal assertions and snapshot/ordinary-GC conversions pass on the host. This is not native codec proof; [Independent source reviewc277823a](tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md) passes; [Source activation-v5](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0, publishing v8/8af9a213 (21 files/11,107 inputs); generated-family review is in progress. The [consumers proposal d768d712](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/README.md) covers only bounded text/JSON:355 proposed native inputs (five additions/two replacements),37 packet files/464 references,32 derivation and21 admission checks, no new C++ translation unit. Independent source review is underway; no live355 integration or native/guest execution has occurred. Positive Web input tests must select the existing `node:stream/web` iteration wrapper: raw global ReadableStream remains non-iterable in this profile.

The independent [disabled-build validation source](tests/node-compat/foundation-zlib/disabled-validation-candidate-v1/README.md) is prepared separately. Its own Buffer/stub smoke uses supported ArrayBuffer/Uint8Array inputs, so the normal-fixture error does not affect that source. Root15 synthetic/source assertions and [independent source review7ccc3c42](tests/node-compat/foundation-zlib/independent-disabled-validation-source-review-v1/README.md) pass. The [actual disabled run](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0: eight bundler denials precede all componentization, and five Buffer/stub observations pass across three retained Jco calls, fresh Jco and fresh Wasmtime. Component154b43e4 is12,913,583 bytes with imports[] and one public scalar export;50 completion files plus one link are checked. The generic direct-native import refusal does not uniquely identify its cause. Independent result review is outstanding, with codec/backend proof and operational admission still closed. Host-only checks remain separate from this actual component evidence.

The [conditional integration56a6](tests/node-compat/foundation-zlib/integration-candidate-v1/README.md)
and [SDK syntax evidence e757/peer4ef](tests/node-compat/foundation-zlib/independent-sdk-syntax-review-v1/README.md)
remain bounded source/syntax evidence:350 proposed native paths, two syntax
commands and1,048 dependency files (2 CPP+1,046 headers), with static `MOZ_Z_*`
mapping. Old [3ff/dafaff Z350-M1](tests/node-compat/foundation-zlib/independent-native-integration-source-review-v1/README.md)
and [c65/89bc Z350-M2](tests/node-compat/foundation-zlib/independent-native-integration-v2-source-review-v1/README.md)
holds remain unchanged. The [two-identifier correction c92e](tests/node-compat/foundation-zlib/descriptor-shadow-amendment-v1/README.md)
and [producer v3 index3929e24d](tests/node-compat/foundation-zlib/native-integration-candidate-v3/README.md)
(81 files/2,146 inputs) pass [source reviewf471ec27](tests/node-compat/foundation-zlib/independent-native-integration-v3-source-review-v1/README.md).
[Root's eight source checks and isolated staging](tests/node-compat/foundation-zlib/native-integration-v3-root-stage-results.json)
pass (76544/964346f9), followed by [actual stage reviewc75f3484](tests/node-compat/foundation-zlib/independent-native-integration-v3-stage-review-v1/README.md):
869 exact copied rows =350 native+522 tooling−3 overlaps, plus the exact proposal
and isolated Git54b base. Original preparation context is retained.

The first ordinary Release normal-OFF attempt (Root62113) finishes at raw exit1.
It reaches the final108/108 copy entry and then postbuild evidence collection.
The actual CMake chain has one compiler `-o` and another for `wasm-opt`;
`codec.link_commands` counts both across the compound line and asserts. The
[Root failure receipt accf4b05](tests/node-compat/foundation-zlib/native-integration-v3-build-attempt1-failure-root-results.json)
retains11 references, recipe/launcher exit1 and completed cleanup. No standalone
CMake exit receipt was captured. The [independent failure reviewc319](tests/node-compat/foundation-zlib/independent-native-zlib-v3-build-failure-review-v1/README.md)
and [Root label clarification](tests/node-compat/foundation-zlib/native-integration-v3-build-failure-labels-root-clarification.json)
retain that distinction. Raw v3 engine62d8e6d8… remains unchanged and UNADMITTED
at9,995,287 bytes, with no metadata sidecar, freeze or backend/runtime proof.

The [v4 source d384af81](tests/node-compat/foundation-zlib/native-integration-candidate-v4/README.md)
(85 files/2,261 preparation inputs) passes [source review31d5408e](tests/node-compat/foundation-zlib/independent-native-integration-v4-source-review-v1/README.md).
[Root checks and staging](tests/node-compat/foundation-zlib/native-integration-v4-root-stage-results.json)
record nine source-check commands at0 (34385/42f14b), then plan/apply, staged
verification, factory and Git checks at0 (89971). The [independent actual-stage
review5d857788](tests/node-compat/foundation-zlib/independent-native-integration-v4-stage-review-v1/README.md)
passes:979 exact copies=350 native+632 tooling−3 overlaps,85 proposal files plus
index, ordinary Git54b clone and original-context preparation references.

The one-job ordinary Release normal-OFF retry finishes at exit0 (Root69972) from
`/tmp/starling-node-compat/zlib-source-v4`, with fresh `zlib-v4-build` and
`production-zlib-v4` namespaces and2GiB start/800MiB stop guards, without
DEBUG/OOM. The separate [four-file cache preseed47668](tests/node-compat/foundation-zlib/native-integration-v4-cache-preseed-root-results.json)
contains only three archive downloads and cbindgen; no engine, configuration,
source or old proof was copied. [Build, freeze and verification](tests/node-compat/foundation-zlib/native-integration-v4-normal-off-root-results.json)
finish at Root-observed exit0 (69972/30705/85956). Engine fb165689… is9,995,295
bytes; all1,024 frozen copies and1,022 original references rehash. The actual
350-source build records62 native units, four strict, six private and one separate
embedding command. [Independent ordinary native reviewba0451db](tests/node-compat/foundation-zlib/independent-native-zlib-v4-normal-off-review-v1/README.md) passes.
The [GC variant](tests/node-compat/foundation-zlib/native-integration-v4-gc-off-root-results.json) also finishes build/freeze/verification at exit0
(44299/71826/23840), with independent GC review pending. All ordinary frozen
copies remain unchanged after the expected shared build-cache reconfiguration.
[Independent GC review90e9e6e3](tests/node-compat/foundation-zlib/independent-native-zlib-v4-gc-off-review-v1/README.md) passes. The [disabled variant](tests/node-compat/foundation-zlib/native-integration-v4-disabled-off-root-results.json)
also finishes build/freeze/verification at exit0 (66192/28710/63712), and
[independent reviewac8d15ac](tests/node-compat/foundation-zlib/independent-native-zlib-v4-disabled-off-review-v1/README.md) confirms its61 native/five private
commands and kernel omission. All three frozen sets remain intact. Runtime backend proof
remains false/null/null; checked-in future pins stay NULL, while the external
Root authority permits validation only. No zlib guest has run. Runtime version, codec/cross-decode,
ownership/GC, components/hosts and costs remain future gates. Historical host/
ECHO vectors and syntax do not supply guest evidence. No installed `node:zlib`
support is claimed.

The initial A–E audit/template deliverables exist; the full roadmap is unfinished.

## Baseline and constraints

- StarlingMonkey HEAD: `54b3329b3ce818fd1f244e871e9c259b63667cda`.
  The profile includes working-tree changes; HEAD alone does not reproduce it.
  Accepted checkpoints record exact source inputs and artifact hashes.
- Compatibility oracle: Node.js **22.14.0**. Packaging baseline:
  ComponentizeJS **0.23.0** and Jco **1.40.0**, with the audited packaging
  corrections and exact revisions recorded in the
  [toolchain audit](docs/node-compat/toolchain-findings.md).
- Selected final standard interfaces: **WASI 0.2.10**. Pure profile components
  have no host imports; entropy and HTTP variants have explicit allowlists.
  No custom host service or Wasmtime/wasmCloud modification is permitted.
- Validated target hosts: stock Wasmtime **42.0.1** and official wasmCloud
  **2.11.0** local host. These are tested pins, not claims about every release.
- Test worlds: `starling:node-compat-test/profile@0.1.0` and the separately
  selected `starling:node-compat-http-test/profile@0.1.0` incoming-handler world.
  Application exports do not authorize custom host imports.

## Completed and verified, within the declared bounds

| Work | Completion evidence and limits |
| --- | --- |
| Architecture audit, API inventory, roadmap, initial templates | [Audit entry point](docs/node-compat/README.md), pinned Node export inventory, matrix, native/facade/stub templates and source integration findings exist. Initial templates remain labeled separately from subsequently compiled implementations. |
| Native Buffer and explicit unsupported module | Opt-in native byte processing plus a small facade, finite manifests, real module registration, aliases, selected static CommonJS lowering, canonical Buffer injection, and explicit `node:child_process` call/construction failures are implemented. Initial [allocation-r2 checkpoint](tests/node-compat/milestones/allocation-r2/README.md) records real component, ownership, initialization, and allocator evidence. Buffer remains a precisely bounded subset. |
| Capability separation and entropy | [Entropy-v1](tests/node-compat/milestones/entropy-v1/README.md) validates explicit entropy policy and standard imports. Pure components retain zero imports; random capability is selected separately. |
| Pure foundational modules | Bounded Path, EventEmitter, StringDecoder, Assert, Querystring and Util implementations have pinned manifests and real-component regressions. Their supported members and explicit refusals are recorded per module; namespace availability does not imply full module support. |
| Strict initialization and deployed failure boundaries | [v8](tests/node-compat/milestones/foundations-v8/README.md) and subsequent regressions cover formerly swallowed callback failures, initialization rejection, deployed fatal failure and handled controls. Failed deployed instances must be discarded. This does not implement Node process error events. |
| Bounded stream/web bridge | [v9](tests/node-compat/milestones/foundations-v9/README.md) validates native constructors, bounded UTF-8 codecs, iteration, selected DataView/BYOB behavior, controller guards, optional selection and both hosts. The [installed matrix supplement](tests/node-compat/foundation-stream-web/installed-matrix-v9.README.md) distinguishes tested members from mere constructor availability. Full classic-stream/consumer acceptance remains outstanding; current bounded classic gates are tracked below. |
| Protected abort listeners and combined regressions | The accepted [v10 checkpoint](tests/node-compat/milestones/foundations-v10/README.md) Events m0.10 adds bounded `addAbortListener`, native protected dispatch and receiver guards. Core remains m0.8; stream/web remains m0.9. This checkpoint contains 3,445 independently byte-verified evidence files, 33 complete reports, 304 native source inputs and four Release engine receipts. |
| v10 focused and full runtime gates | [Focused report](tests/node-compat/foundation-add-abort/production-native-m0.10/README.md) records 29 Node-derived groups, namespace/default/alias/CommonJS behavior, initializer failures, fatal/discard and handled reuse, Events-OFF admission, and valid native byte-kernel GC roundtrips. Full core/allocator, earlier foundations, stream/web and 24 strict-callback component regressions pass. |
| v10 HTTP on both target hosts | [HTTP-v10 evidence](tests/node-compat/foundations/http-v10.md) validates the same component bytes on both hosts, three requests each and clean shutdown. Its six standard 0.2.10 imports cover HTTP types, IO error/poll/streams, random and a type-only monotonic-clock dependency with no callable clock function. No other network/filesystem/process capability is inferred. |
| Earlier public allocation checkpoint: foundations-v11 | [v11](tests/node-compat/milestones/foundations-v11/README.md) accepts bounded m0.11 allocation after release, GC, focused and both-host HTTP gates. Its 1,746 copied evidence records and 304-input source archive remain unchanged. |
| Latest accepted checkpoint: foundations-v12 | [Acceptance](tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md) covers the private scheduler layer, three production engines, separate diagnostic Release/GC, fresh eight-stage replay, allocator/focused gates and both-host HTTP. Root independently verifies 4,150 indexed files, 4,148 copied records, 212 external references and the unchanged v11 parent. Public API versions are unchanged. |
| Performance measurements with counterexamples retained | Matched Jco-adapter and private allocation-pair experiments are documented, including slower results, larger artifacts and higher memory observations. Measurements do not establish a universal native-code advantage. See [allocation work](tests/node-compat/foundation-alloc-unsafe/README.md) and the measured limitations below. |

Older accepted checkpoints and failed attempts remain unchanged. Later results
supersede only the explicitly identified claims; they do not erase prior evidence.

## Latest completed milestone: foundations-v12

**Accepted, bounded:** the [acceptance receipt](tests/node-compat/foundation-scheduler/production-acceptance-v12/acceptance-receipt.json)
is the current authority for the [frozen archive](tests/node-compat/milestones/foundations-v12/README.md).
The archive's pending labels preserve its earlier construction state; this
separate acceptance record advances status without rewriting evidence.

Root independently rehashed all **4,150 indexed files**, **4,148 copied records**
(163,492,404 bytes), **212 external references**, **4,881 input mappings** and
the unchanged **1,746-record v11 parent**. The current native inventory is 306:
299 v11 inputs unchanged, five changed and two queue files added, with three
external embedding inputs separate. Three production engines and two diagnostic
engines have distinct receipts and validation scopes.

Fresh production/control validation covers **61 components**: 60 current and one
historical delegated control. The **20 private diagnostic components** remain
separate. All eight normal-OFF stages pass with no earlier result reuse;
allocator GC, focused OFF/RuntimeOnly/GC and the safe getter observation pass
their bounded checks. Getter parity remains **false**. The same HTTP component
passes three requests per stock host and clean exit0, with exactly six selected
standard WASI 0.2.10 interfaces and a type-only clock dependency.

No public module version advanced: core/Buffer remains m0.11, Events m0.10 and
stream/web m0.9. Private ticks default OFF. Reset, ALS, request isolation,
first-ever classic startup, isolated VM-root proof and a performance advantage
remain unproved. The overall roadmap is unfinished.

## Previous public allocation milestone: foundations-v11

**Accepted, bounded:** [checkpoint](tests/node-compat/milestones/foundations-v11/README.md),
[full results](tests/node-compat/milestones/foundations-v11/results.json), and
[independent acceptance receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/v11-acceptance-receipt.json).
Root independently rehashed all **1,746 copied files** (76,656,667 bytes), including
**33 full reports**, after the producer verified the exact plan and every copy.
The parent v10 archive remains unchanged. This completes the m0.11 milestone;
the full roadmap remains active.

The reviewed [11-file integration packet](tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11-v2/README.md)
was applied coherently. Four of 304 native inputs changed; the other 300,
protected abort-listener integration, CMake, build recipe, embedding and native
Buffer kernel remain unchanged. `allocUnsafe` now allocates through captured
Uint8Array directly after the same primary validation. It retains fresh zeroed
storage, no pool, a 16 MiB limit, truncation and the declared backing/view/error
contract. It adds no C++ allocator kernel, ownership transfer, host import or
supported Buffer method. The proposal packet's earlier UNAPPLIED label is
historical; the [adoption receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
records its actual application.

The [three-build receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/native-build-results.json)
records exact source/configuration, compile commands and dependency evidence:

| v11 Release engine | SHA-256 |
| --- | --- |
| Entropy OFF | `1eb2b55a391e2bc83478fefee124a6f282cfed148cc0623754125f6c5e9b0458` |
| RuntimeOnly | `2e3731ce248be1d8ede0f5672dd87b48fb1731dfddb045bfaabaeea02534a36d` |
| Existing GC-stress instrumentation, entropy OFF | `b79fd7dba35288e233ec07134e490ddd2ae51f212a2be506ecd70a728f5e6bc4` |

[Source admission](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-admission-results.json)
passes eight generator checks, 328 module-admission checks, schema checks
including 19 malformed-manifest rejections, and the bundler contract. The
[eight-job release batch](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/release-gate-results.json)
passes core, allocator, stream/web, six earlier foundations and four strict
callback groups. Five earlier same-engine successes were byte-verified and
reused; three strict suites passed fresh retries.

The [allocator GC gate](tests/node-compat/foundation-alloc-unsafe/installed/gc-v11-results.json)
passes three retained Jco calls and fresh Wasmtime with eight valid native hex
roundtrips per call, checking brands, owned backing, shared views, zeroed/empty
allocation and snapshot state. The
[focused receipt](tests/node-compat/foundation-add-abort/production-native-m0.11/evidence-receipt.json)
covers four reports and 19 application components: OFF and RuntimeOnly each
pass 29 groups, with separate protected-owner GC and callback-return observation.
Eleven components import nothing; eight import only `wasi:random/random@0.2.10`.
Known getter parity remains **false** and GC still proves combined owners only.

[HTTP-v11](tests/node-compat/foundations/http-v11.md) passes three requests on each
stock target host with the same component
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`,
63,635,975 bytes including test corpora. Both hosts stop with code 0 and counters
`[1,1,1]`; this proves neither same-instance reuse nor request isolation. The six
selected standard WASI 0.2.10 imports and type-only clock remain unchanged.
This is a correctness artifact, not a product-size comparison.

Failure history is preserved: the new allocator host runner initially omitted
`pathToFileURL`, and a later strict-runtime packaging attempt exhausted local
disk space. The corrected harness and fresh runtime retries pass; incomplete
attempts are not counted as passes. Byte/metadata-verified output compression
and the [duplicate-artifact recovery receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/cow-bootstrap-results.json)
retain the evidence. Most space had recovered before that operation; its
35,856,384-byte observed delta is nonexclusive. Storage observations are not
guest memory or performance results.

Private paired allocation measurements remain contextual: candidate peak RSS
was higher in **29/30** comparisons, capacity higher in **4/30**, and the minimal
snapshot **8,513 bytes larger**. Seven slower controls, five control reversals
and only two independent processes per arm limit interpretation. No private
throughput result is transferred to this production engine, and no memory,
size or whole-application advantage is claimed.

## Current work in progress

The [classic342 source layer](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md)
is applied with a default-OFF flag. The coherent41-path adoption preserves the
306-input branch and existing embedding/standard-interface contracts. Root's
source checks and independent reviews remain recorded in the adoption ledger;
the original null-pin proposals stay unchanged.

All four actual Release variants are built, frozen and independently reviewed:
normal-OFF (`b8279ee1…`), RuntimeOnly (`1a3f4628…`), GC-OFF
(`f9f48f4f…`) and classic-disabled OFF (`27e625a7…`). Each has405 frozen
copies, native342/ext3 and native61/strict4 observations. CLASSIC is private to
the five profile TUs when enabled and absent in the disabled control. Each has
a separate AFTER-only embedding9d command witness. Normal-OFF was frozen before shared
project reconfiguration for GC. The [native build receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/native-build-results.json)
and [Root authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/root-pin-review-receipt.json)
bind all four tuples. The disabled control passes eight ESM/CommonJS admission
denials without componentization; it is an actual fourth variant, not a projected
older receipt.

Three actual classic component suites finish with raw terminal0 and independent
evidence reviews:

| Suite | Published output hashes | Final component imports | Review |
| --- | --- | --- | --- |
| Normal-OFF, activated runtime-v2 | 90 | Five components, all imports[] | [Independent OFF review](tests/node-compat/foundation-classic-streams/independent-normal-off-component-review-v1/README.md) |
| RuntimeOnly, activated runtime-v3 | 91 | Five components, only `wasi:random/random@0.2.10` | [Independent Runtime/GC review](tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) |
| GC-OFF, activated runtime-v3 | 90 | Five components, all imports[] | [Independent Runtime/GC review](tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) |

Each suite covers19 Node22 ordinary groups,48 deferred call/new checks,
17 overload refusals, three buffered-state limits,65 expected initializer
failures, three retained main calls and fresh Jco/Wasmtime observations.
Separate deployed cases cover one fatal/discard and two caught/handled controls;
the caught initializer component is preserved. Snapshot identity is true only
on first/fresh calls and null on retained calls two/three, whose prior default
is777. The Jco fatal catcher exits0; Wasmtime's generic134 trap does not identify
the originating error. Only successful instances are reused. GC-OFF additionally
exercises eight valid native hex rounds per call with combined stream/listener/
decoder/Buffer owners; this does not isolate a VM queue or prototype key.

Earlier failures remain separate and preserved. Initial ESM `require()` placement
failed host bundling before componentization; the [explicit CJS amendment](tests/node-compat/foundation-classic-streams/harness-cjs-contract-amendment-v1/README.md)
retains the bundler contract. Runtime-v2 then hit exclusive creation of a shared
generated interface declaration; the [same-run identical-declaration amendment](tests/node-compat/foundation-classic-streams/shared-transpile-interface-amendment-v1/README.md)
allows only already-tracked byte-identical direct `interfaces/*.d.ts` reuse.
A collector's incorrect retained snapshot-identity assumption and the independent
reader's initial embedding ThinLTO assumption are preserved observer corrections,
not native or guest failures.

The fresh baseline replay-v3 now finishes **all eight stages with raw0** and
[independent result verification](tests/node-compat/foundation-classic-streams/independent-regression-v3-results-review-v1/README.md):
346 output files,40 final components (39 current and one fresh historical m0.8
control), all with zero imports. Historical controls and counterexamples remain
explicit. Replay-v1 first stopped before any child
because its owned parent directory was absent, then stopped at an absent copied
Path Node-oracle subprocess entry. The [registrar/Path amendment](tests/node-compat/foundation-classic-streams/registrar-ancestry-oracle-amendment-v1/README.md)
keeps old Node oracles unchanged, binds exact19eef→2848 Classic registrar ancestry,
and tests safe Node subprocesses into fresh output without old writes.
The new replay-v2 again passes core/allocator/stream-web and Path fresh, but stops
at Events' exact old strict-policy tag before that component is built.
Its partial raw0 stages are not a complete eight-stage pass or reusable acceptance.
The [five-tag/GC-schema amendment](tests/node-compat/foundation-classic-streams/exact-policy-tag-amendment-v1/README.md)
uses exact full Classic lineage equality and actual GC pin/config fields.
It audits all64 bodies and passes124 data-only checks.
[Replay producer-v3](tests/node-compat/foundation-classic-streams/replay-activation-candidate-v3/README.md)
and its independent source review pass: both amendments are mandatory,
57/64 inherited bodies remain identical, and seven host harness bodies change.
Guest/facade/oracle semantics and all four native artifacts are unchanged.
Root repeats124 tag/pin data checks and14 source groups, then publishes the
[new replay-v3 source family](tests/node-compat/foundation-classic-streams/production-regression-activated-v3/README.md)
with raw0:82 records,2,055 root/2,054 capability inputs and actual runtime-v3
delegation. The [independent generated-source review](tests/node-compat/foundation-classic-streams/independent-activated-regression-review-v3/README.md)
passes, and three actual native-mode admissions plus Release OFF preflight finish
raw0. The [fresh full eight-stage replay-v3](tests/node-compat/foundation-classic-streams/production-adoption-v1/release-replay-v3-root-results.json)
finishes terminal0 with all child exits0, six optional modules, complete input
rechecks and a final report seal. No earlier partial pass was reused.
The separate [allocator Release-GC](tests/node-compat/foundation-classic-streams/production-adoption-v1/allocator-gc-v3-root-results.json)
and focused [OFF](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-off-v3-root-results.json)/[RuntimeOnly](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-runtime-v3-root-results.json)
gates finish raw0. Each focused ordinary gate covers29 Node public groups,
eight expected initializer failures and five fatal/discard cases. The separate [focused combined-owner GC](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-gc-v3-root-results.json)
and [getter counterexample observation](tests/node-compat/foundation-classic-streams/production-adoption-v1/getter-v3-root-results.json)
also finish raw0. Getter parity remains false: Node1/1/0 versus Jco/Wasmtime0/0/0;
GC does not isolate individual root owners. [Independent followon verification](tests/node-compat/foundation-classic-streams/independent-followon-result-review-v1/README.md)
passes all five gates, deriving20 final components (allocator1, focused OFF8,
Runtime8, focused GC2, getter1). All OFF/GC imports are empty; Runtime imports
only standard random0.2.10. The actual source82/2,055/2,054, tool trees and all
four405-copy native freezes are rechecked without new guest execution.

The [combined HTTP proposal](tests/node-compat/foundation-classic-streams/classic-http-candidate-v1/README.md)
has63 sealed files/7,518 source inputs, all eight LIVE WIT/adapter inputs,
26 Root pure checks and an actual-entry host bundle with exactly17 native/WASI
imports. [Independent source review](tests/node-compat/foundation-classic-streams/independent-classic-http-source-review-v1/README.md)
passes. It adds ordinary classic19 to the unchanged baseline schema5/protected29
through a scoped wrapper of the real WASI handler. Root's prepare and packaging
jobs now finish raw0. The actual component is64,057,853 bytes,
`25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d`,
with the same `2fab5aab…` bundle, exact six standard0.2.10 imports, type-only
clock and no Preview1 import. [Independent pre-host review](tests/node-compat/foundation-classic-streams/independent-http-prehost-verification-v1/README.md)
passes, and a separate Root-reviewed external phase binds these exact original
paths and bytes. The first Wasmtime attempt fails after receiving HTTP because
Root enabled an optional historical intrinsic assertion whose diagnostic fields
this fixture does not export. Its raw1/logs/partial output are preserved in the
[attempt receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wasmtime-attempt1-root-results.json);
no pass is counted for that attempt. A [fresh output wrapper](tests/node-compat/foundation-classic-streams/http-host-output-retry-candidate-v1/README.md)
passes13 Root source checks and [independent review](tests/node-compat/foundation-classic-streams/independent-http-host-output-retry-review-v1/README.md).
The [Wasmtime-v2 retry](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wasmtime-v2-root-results.json)
passes three HTTP200 responses and clean owned-host exit0. The unchanged wasmCloud wrapper passes three HTTP200 responses and clean
owned-host exit0 with the same component; its [Root capture](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wash-root-results.json)
records terminal0. The [final combined-host audit](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-combined-root-results.json)
also finishes raw0, retaining all six combined responses and18 audited artifacts.
Both counters are[1,1,1], proving neither reuse nor isolation. The
[independent final evidence review](tests/node-compat/foundation-classic-streams/independent-combined-http-results-review-v1/README.md)
passes8,067 declared paths, all six raw-response assertion sets and18 artifact
records, including current native/tool/source seals and both official host
binaries/configurations. The local phase pin stays null and
sealed. This transport does
not implement `node:http`, and this corpus-heavy artifact is not a size comparison.

The [measurement extension proposal](tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1/README.md)
passes [independent source review and SDK syntax](tests/node-compat/foundation-classic-streams/independent-measurement-extension-review-v1/README.md)
with1,022 actual header dependencies; it has no admitted benchmark artifact or
result. The old-generation diagnostic producer/freezer/admission source packet has43 sealed
files/666 inputs, independent source review and72 Python/19 Node Root checks;
that old producer has no native-action result. A new common seven-scenario/three-control Node22
workload captures exact checksums and bounded traces at1/16 iterations. All
output byte/text/value assertions and checksums match, but14 ordinary host-model
trace comparisons differ: synchronous HWM-boundary write returns, event order
and object callback encodings remain counterexamples. Two failed host attempts
were ordinary assertion-diff formatting failures and are preserved; no guest or
fault-injection work ran. Bounded reporting retains the differences without
changing the canonical factory or stock scheduler. The sealed [workload source](tests/node-compat/foundation-classic-streams/measurement-workload-candidate-v1/README.md)
has58 files/5,297 inputs, actual native/canonical/stock source graphs and null
future pins. Both original canonical and stock providers retain14 trace gaps;
three controls match. Its independent source review is running.
The sealed [minimal reproduction source](tests/node-compat/foundation-classic-streams/stream-trace-regression-candidate-v1/README.md)
has15 files/6,015 inputs and eight Node/model cases; Root repeats13 source
checks and independent source review passes. Its [actual component result](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-component-root-results.json)
finishes raw0 as a completed observation with Node parity false. The unchanged
b827 engine produces component f896b7c2… (12,933,484 bytes), imports[], three
retained calls and fresh Jco/Wasmtime with the same four Node differences:
synchronous64-byte writes at HWM64/63 and the two source-PassThrough event traces.
[Independent verification](tests/node-compat/foundation-classic-streams/independent-stream-trace-component-review-v1/README.md)
confirms the raw public Wasmtime result and completion chain. The [11-case successor](tests/node-compat/foundation-classic-streams/stream-trace-regression-candidate-v2/README.md)
adds ordinary one-argument/callback/UTF8 object-mode encoding probes with typed
undefined/null/string outputs. Its43 files/6,062 inputs and original eight
Node/model records pass Root rehashes;14 Root source checks and independent
delta review pass. Its [actual11-case result](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-component-v2-root-results.json)
finishes raw0 as an observation with Node parity false and six differences:
the four original byte/event gaps plus one-argument/callback object encodings.
Guest hooks receive UTF8 for both, while Node receives undefined/null. The
explicit UTF8 control matches; payload identity and hook/user callback counts
match. Three retained calls and fresh Jco/Wasmtime agree, with imports[]. The
original eight actual records remain exact. [Independent result verification](tests/node-compat/foundation-classic-streams/independent-stream-trace-component-review-v2/README.md)
passes all11 observations, public binary/core/glue, raw Wasmtime decoding and
the source/native/output completion seals without another guest run.
The separate [semantic fix proposal](tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/README.md)
has65 files/488 inputs and five transformed-writable edits, producing three
proposed generated-source afterimages. Node-host tests match20 workload cases,
eight minimal cases,14 boundary cases and the inherited19-case corpus. Ablation
shows the post-write return correction also restores the observed minimal event
order; an unnecessary broader scheduling experiment is preserved and excluded.
Object-mode encoding is the other model-verified correction. [Independent source review](tests/node-compat/foundation-classic-streams/independent-trace-semantics-source-review-v1/README.md)
confirms the three-file reconstruction and stored20+8+14 data; the legacy19
observed array was not retained, so only its owner assertion/reported equality
is corroborated until fresh actual gates. The first two workload Node failure
sources/facts are preserved, but their full raw stderr remains tool-history-only.
Original-workspace native342 and the four old pins remain unchanged. These are
source/model results, not installed-guest fix
proof. The [integration source proposal](tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/README.md)
has159 files/1,175 inputs, a new exact342 policy (339 unchanged+3 corrected),
recipe/admission/tooling afterimages and null future pins. Strict/protected
boundary tags and m0.12 exports remain exact. Root's read/hash/AST verifier
finishes raw0 and [independent source review](tests/node-compat/foundation-classic-streams/independent-trace-integration-source-review-v1/README.md)
passes. The [isolated checkout receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-source-checkout-root-results.json)
records a detached54b3329 base plus exact339+3 native and two changed tooling
files, with the selector unchanged. It passes the original proposal's1175-input
preparation check and the separate checkout's342 native/92 tooling/copied159
checks. The original workspace and four old freezes stay unchanged. The first
new normal-OFF Release build finishes107 steps/raw0 and its freezer finishes
raw0, with474 actual copies (native342/external3). The
[Root native receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-normal-off-native-root-results.json)
records engine d54446dc… (9,973,355 bytes), metadata bfaec95e… and freeze1f2a49ac….
All four corrected builds/freezes now finish raw0: OFF107 steps, RuntimeOnly107,
disabled-control107 and incremental GC16, with474 actual copies each.
[OFF](tests/node-compat/foundation-classic-streams/independent-trace-native-normal-off-review-v1/README.md),
[RuntimeOnly](tests/node-compat/foundation-classic-streams/independent-trace-native-runtime-review-v1/README.md)
and [disabled-control](tests/node-compat/foundation-classic-streams/independent-trace-native-disabled-review-v1/README.md)
artifact reviews pass, as does the [GC review](tests/node-compat/foundation-classic-streams/independent-trace-native-gc-review-v1/README.md). The OFF freeze precedes GC
reconfiguration. One-job/2GiB start/800MiB stop guards remain in force.
The four-label exporter remains unreviewed history. Root's separate reviewed
pin document is `182e8b72…fab5eb`; its review receipt is `ce88ac34…a8be0`.
[Runtime activation](tests/node-compat/foundation-classic-streams/production-trace-runtime-activated-v1/README.md)
finishes raw0, producing26 files and6,414 consumed inputs/22 tool links; index
`e1f87cd6…175b78` passes [independent family review](tests/node-compat/foundation-classic-streams/independent-trace-runtime-family-review-v1/README.md).
The [four runtime-family preflights](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-runtime-source-and-preflights-root-results.json)
and separately reviewed corrected Node11 gate pass. The three fresh corrected
classic suites and disabled admission control now pass the
[independent all-four review](tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md)
(`8c3da4a2…41e8cc`): 15 classic component occurrences plus the separate Node11
component, with exact OFF/GC empty and RuntimeOnly random-only imports. It
rechecks 26/6,414 source/input files, 365 source mappings, four 474-file freezes,
15 static WIT audits and 12 core/component/glue relationships. Each enabled suite
retains 19/48/17/3/65 checks, three retained calls, fresh Jco/Wasmtime, snapshot
identity and default-before 65536 then 777, fatal-discard and two clean controls.
Only parsed main/clean Wasmtime success observations and stdout hashes remain;
raw stdout cannot be independently decoded. Fatal raw streams are retained and
generic traps do not identify origin; GC proves combined owners only.

The diagnostic-v2 metadata-import failure remains preserved. Diagnostic-v3 ON/OFF
native checks and both independent reviews now pass (109 steps/525 copies each).
The fresh persistence-enabled full20+14 run66794 now passes Root6218 and
independent0f59 review:105 full Node-exact returned records,632 completion files
and21 independently decoded raw Wasmtime streams. The original90660 failure
still has an unknown timed-out case and unretained Jco data. Separate case5
equality is not reused. Measurement source4b6/96bc and its reviewed M1 successor
now lead to actual source family1b801 with reviewed diagnostic pair and both
preflights. Family review4e986 passes; four-arm component correctness is running
and no timing is authorized.

Corrected replay sourcea08/peer8529 and the explicit-Wasmtime preflight retry
pass. The fresh eight-stage replay23947 and five follow-ons now pass independent
reviews6a67/d116:40+20 component occurrences, with separately identified historical
controls and raw-output availability limits. Only RuntimeOnly follow-ons import
random@0.2.10. The original Root environment failure, old-source passes and all
six actual trace counterexamples remain preserved. Corrected HTTP packaging71459
now finishes raw0 after a preserved missing-tool attempt with unknown outer
terminal status; its64,058,731-byte component has exact six0.2.10 interfaces and
type-only clock. Both-host HTTP, cost/artifact/archive and Root acceptance remain
open. Accepted checkpoint
remains bounded v12, with no full Node or performance claim.

The following records retain the completed v12 execution history; their passes
belong to those exact306-input engines, not the changed classic342 artifacts.

### Completed execution history for v12

The [fresh link1 Release build](tests/node-compat/foundation-scheduler/link1-execution-v1/release-native-results.json)
completes all 109 compile/link/copy steps and publishes engine
`46fc6588397bc7ca332369600fe3d561897001d79611b25d7dca1d9b462a373b`
(9,764,917 bytes). The [actual freeze/full preflight](tests/node-compat/foundation-scheduler/link1-execution-v1/release-freeze-results.json)
validates 345 copies, native306 + diagnostic2, native61/strict4/queue1 commands,
separate parent1+1 commands, and all four final-link witnesses. The original
normal configuration was frozen before any GC reconfiguration.

The [new ordinary component result](tests/node-compat/foundation-scheduler/link1-execution-v1/ordinary-release-results.json)
passes ten packaged artifacts, five expected initialization failures, three
paired successful controls and three fresh fatal/discard observations. Main
runs three retained Jco calls and fresh Wasmtime. All ten components emit zero
imports. The [32-input driver](tests/node-compat/foundation-scheduler/diagnostic-link1-driver-v2/README.md)
adds the exact live adapter to the pre/post seal and retains the full corpus;
56 host checks pass. [Independent verification](tests/node-compat/foundation-scheduler/link1-ordinary-release-verification-v1/README.md)
rehashes 494 canonical files/495 path references and confirms the recorded scope.
This is ordinary Release, without forced-GC proof or production acceptance.

The [separate Release-GC build](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-native-results.json)
completes 16 incremental compile/link/copy steps and publishes
`949d24f653903923bb7055c441b7a5131922a787d94465f014d62a8d680b802b`
(9,766,466 bytes). Its [freeze/full preflight](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-freeze-results.json)
passes the same 345-copy and command/witness checks, including the actual Buffer
GC macro. The [actual GC component result](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-component-results.json)
now passes the complete ten-artifact/five-initializer/three-control/three-fatal
protocol, three retained main Jco calls and fresh Wasmtime, with zero imports.
All 32 inputs and the live adapter match before/after. Eight valid native hex
operations run while inline callback/object/unregistered-Symbol values are
pending, with actual kernel GC instrumentation enabled. Application strong
co-owners are removed; VM temporary retention is **uninstrumented**. This is not
isolated VM-root proof, reset/reuse support or production acceptance.
[Independent GC verification](tests/node-compat/foundation-scheduler/link1-gc-verification-v1/README.md)
confirms the frozen sources/configuration, all 32 inputs, ten zero-import
components and the actual GC flags without rerunning the guest.

The private tick scheduler is **source-applied** through the reviewed seven-file
[native layer and recipe](tests/node-compat/foundation-scheduler/production-adoption-v1/source-adoption-receipt.json).
All 306 intended native inputs match the layered policy. The existing traced
TaskQueue owns the bounded FIFO; the feature defaults OFF and adds no public
Node export or host capability. The
[finite admission adoption](tests/node-compat/foundation-scheduler/production-adoption-v1/admission-adoption-receipt.json)
passes **110** independent checks, including optional stream/web OFF and rejection
of diagnostic engines. Seven historical receipt selections remain unchanged.
These source/admission checks are separate from runtime proof.

The [production launcher review](tests/node-compat/foundation-scheduler/production-execution-v1/launcher-root-review.json)
checks its exact source, all eight unchanged lifecycle helpers, recipe869 and
all 306 current native inputs. Independent source review agrees. The actual
normal-OFF build completes all **107** steps with exit0 and engine
`6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84`
(9,759,293 bytes). The [native receipt](tests/node-compat/foundation-scheduler/production-execution-v1/normal-off-native-results.json)
and [actual freeze](tests/node-compat/foundation-scheduler/production-execution-v1/normal-off-freeze-results.json)
record 335 copied files, native306/external3, native61/strict4 and a separate
actual embedding command. Its raw Ninja evidence is **after-build only**;
no before-build witness is invented. The normal configuration is frozen before
GC reconfiguration. The freezer/exporter packet passes **85** fresh Root host
checks and independent source review. Unreviewed exports cannot activate
consumers. [Independent normal-OFF verification](tests/node-compat/foundation-scheduler/production-normal-off-verification-v1/README.md)
passes and the real finite selector admits eight manifests against frozen
sources. The separate RuntimeOnly build also completes **107** steps with exit0,
engine `479821f8eefbc6aacbfe9df8538c5ee0a8745e530a474ecee8cb34251c0a1943`
(9,766,342 bytes), and its [335-file freeze](tests/node-compat/foundation-scheduler/production-execution-v1/normal-runtime-freeze-results.json)
passes. [Independent RuntimeOnly verification](tests/node-compat/foundation-scheduler/production-normal-runtime-verification-v1/README.md)
confirms both entropy macros in all 62 native/embedding commands. GC-OFF
completes **16 incremental steps** with exit0, after the launcher validates the
normal-OFF freeze before reconfiguration. Its engine
`502320aaed8c78ace92d8d8d782a355307868beee707b22e03c96f67cd42c833`
(9,760,842 bytes) has a passing [335-file freeze](tests/node-compat/foundation-scheduler/production-execution-v1/gc-off-freeze-results.json)
and actual kernel GC flags. [Independent GC verification](tests/node-compat/foundation-scheduler/production-gc-off-verification-v1/README.md)
passes, including the preserved normal-OFF prerequisite freeze. All three native
jobs are terminal. Root's separate [actual pin review](tests/node-compat/foundation-scheduler/production-pin-review-v1/README.md)
rehashes all 335 copies per variant and all three independent proof packets.
The original candidate export stays **unreviewed** and unchanged. New common-v5,
OFF-v3 and release-v3 revisions now bind the reviewed data and sealed parent
indices, with 667/755/1,442 runtime inputs respectively. Root freshly passes
**227** host/source checks, rehashes all three indices and the fixed 778-input
capability closure, and passes the complete release read-only preflight.
Independent activation review and all five separate read-only admissions pass.
The actual serial eight-stage normal-OFF replay is now running with fresh
outputs and no prior runtime pass reuse. Sealed null-pin predecessors remain
unchanged. GC/focused/HTTP runtime gates and acceptance remain outstanding.

The [full eight-stage batch](tests/node-compat/foundation-scheduler/production-runtime-v1/off-release-root-results.json)
now passes with exit0: core Buffer/explicit-stub behavior, allocator, installed
stream/web, all six foundational modules and all four strict-callback suites.
Every report/completion/log hash matches and no earlier runtime pass is reused.
The [separate allocator GC gate](tests/node-compat/foundation-scheduler/production-runtime-v1/allocator-gc-root-results.json)
also passes on GC-OFF: three retained calls and fresh Wasmtime around eight
valid native hex roundtrips, with zero imports and post-run source checks.
Focused OFF and RuntimeOnly each pass 29 groups, eight initializer failures,
five fresh fatal cases and nine retained successful calls plus fresh Wasmtime
controls. OFF imports nothing; RuntimeOnly imports exactly
`wasi:random/random@0.2.10`. Focused GC also passes three retained calls/fresh
Wasmtime with eight native roundtrips; ownership remains **combined**, not
prototype-only Symbol proof. The safe getter observation reconfirms Node
`1/1/0` versus native `0/0/0`, with `nodeCompatibilityPassed:false`.

The [independent eight-stage verification](tests/node-compat/foundation-scheduler/production-runtime-verification-v1/README.md)
validates all reports/seals and 40 zero-import application components: **39
current production and one freshly packaged historical delegated control**.
The [separate focused/GC/getter verification](tests/node-compat/foundation-scheduler/production-focused-runtime-verification-v1/README.md)
passes: 20 current components, eight importing only standard random and twelve
importing nothing. Getter parity remains explicitly false.

HTTP packaging and [independent pre-host review](tests/node-compat/foundation-scheduler/production-http-prehost-verification-v1/README.md)
pass. Root [reviewed the actual component phase pin](tests/node-compat/foundation-scheduler/production-http-phase-review-v1/README.md)
and sealed the final capability index without changing any of the 778 prepack
inputs. Component `ccc87ae3f9a00195ae243fa1077a07f9cd68e5ad3a8220708400187eee7a2ba6`
(63,639,194 bytes, including test corpora) now passes three requests on each
stock host, both exiting0. The [combined audit](tests/node-compat/foundation-scheduler/production-runtime-v1/http-final-root-results.json)
passes with exactly six standard WASI 0.2.10 imports, only incoming-handler
exported, type-only clock and no callable clock import. Both counters are
`[1,1,1]`; reuse and request isolation remain unproved. Independent post-host
verification and Root archive acceptance subsequently pass. These passes do not complete
the roadmap or establish reset/reuse/ALS or a performance advantage.

The [third ordinary Release attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-v4-build-results.json)
completed ten incremental steps from the verified partial project, publishing
engine `a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b`
(9,764,903 bytes) and its full sidecar. The executed v2 freezer verifies **337**
source/configuration/dependency copies. Native61 compile commands come from the
database; one embedding and one diagnostic command come from raw Ninja.
Before/after configuration and parent-command bytes are identical.

The [ordinary real-component gate](tests/node-compat/foundation-scheduler/production-adoption-v1/ordinary-release-results.json)
passes **ten packaged components**, including three deliberately fatal deployed
fixtures, **five expected initialization failures**, **three paired successful
controls** and **three fresh-instance fatal-boundary observations**. Main runs
three retained Jco calls and fresh Wasmtime; all ten components emit **zero
imports**. Initial ESM, task/export and Promise-job ordering, 5,000 FIFO callbacks,
argument/queue/work limits, subsequent configured classic evaluation, INIT
completion before content and final binding pass their stated checks. The
[independent 462-file verification](tests/node-compat/foundation-scheduler/ordinary-release-verification-v1/README.md)
passes. This engine has `gcStress=false`: eight ordinary native hex operations
do not prove forced-GC ownership. First-ever classic startup, INIT tick priority,
original fatal-cause identity, actual reset and request isolation are not proved.
No post-fatal instance reuse occurs.

The [driver packet](tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/README.md)
retains 27 indexed files and 24 consumed hashes, checked before and after the
run. Its historical `UNEXECUTED` filename is not its current execution status.
Its earlier adapter-seal limitation is historical; the new 32-input driver and
both diagnostic gates above supersede it. Finite production OFF/RuntimeOnly/GC
builds, all prior public regressions and both-host HTTP remain required before scheduler acceptance.
The production selector continues to reject diagnostic engines.

The [read-only linker audit](tests/node-compat/foundation-scheduler/link-resource-audit-v1/README.md)
found that one Ninja job did not bound LLD's own threading. The pinned SDK's
print-only Clang command forwards `--threads=1 --thinlto-jobs=1` while retaining
all other link arguments. The separately frozen
[link1 producer candidate](tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1/README.md)
passes 24 synthetic command cases, syntax and patch checks; Root rehashed all
30 indexed files and an [independent source review](tests/node-compat/foundation-scheduler/independent-link1-review-v1/README.md)
found no concrete blocker to the proposal. The exact
[diagnostic producer change is now source-applied](tests/node-compat/foundation-scheduler/link1-adoption-v1/source-adoption-receipt.json),
with [new finite consumers](tests/node-compat/foundation-scheduler/diagnostic-link1-consumers-v1/README.md).
Root independently passes **46** host checks, verifies all 31 consumed inputs
and rehashes both source packets. The new freezer authenticates four final-link
witnesses; the launcher retains eight unchanged lifecycle definitions and the
same capacity thresholds. Original frozen packets remain unchanged; their earlier
UNAPPLIED descriptions are historical. Native306, diagnostic2 and production
recipe869 are unchanged. Actual link1 builds/freezes and the ordinary guest pass
are now recorded above; earlier preparation-only statements remain historical.
Generated Clang flags are observed; spawned LLD arguments, thread counts and
resource benefits are unobserved. Both diagnostic gates pass; all production gates remain
required.
No memory benefit, performance gain or lower start guard is proved.
O3, ThinLTO and the complete functional test scope remain the selected baseline.

The [reset audit](tests/node-compat/foundation-scheduler/reset-design-v1/README.md)
finds a source-level lifetime hazard: `Engine::reset` clears owning task references
before `timers::reset` traverses raw pointers in `TIMERS_MAP`. The selected
ComponentizeJS embedding has no automatic `Engine::reset` call, so this is not
presented as a per-export failure. No reset experiment has run. Transactional
registration, traced cancellation ownership, idempotence, resource cleanup,
bounded jobs/finalizers and request epochs must precede safe reset/reuse and ALS.

### Preserved failures and execution history

- The [first diagnostic attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-attempt-v1/receipt.json)
  linked all 109 native steps but rejected an incomplete compiler receipt. Its
  raw engine has no published sidecar and was never admitted or executed.
- The [second attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-attempt-v2-interrupted/receipt.json)
  was interrupted during disk exhaustion; its native exit status was not saved.
  No successful build or specific native stop cause is inferred.
- The corrected producer captures actual parent-target Ninja commands before and
  after the build. The one-job v4 launcher requires 2 GiB to start and stops below
  800 MiB, with process-group cleanup and status preservation. Six benign host
  lifecycle checks pass; the subsequent ordinary Release success is separately
  recorded above. The subsequent link1 Release-GC build and component gate also
  pass, as separately recorded above.
- The first production-regression implementation passed 34 host checks, but
  final review found an unbound manifest/pin recheck. V2 and its initial review
  are preserved as superseded. V3 captures initial primitive digests and rejects
  changes before parsing or following new entries. Root independently passes
  all 41 checks, including seven owned-scratch seal cases; actual pins stayed
  null throughout and no runtime reached the defective path.

### Storage preparation, separate from runtime results

All completed passes below preserve logical bytes and required metadata with
independent postverification. No historical component was executed for storage
work, and native build intermediates were retained. Allocation reductions are
filesystem observations, not guest memory or throughput results.

| Completed operation | Verified observation |
| --- | --- |
| [59 mature v5–v7 artifacts](tests/node-compat/storage-compaction-mature-v5-v7/README.md) | 709,795,840-byte summed allocation reduction. |
| [92 earlier accepted artifacts](tests/node-compat/storage-compaction-earlier-adoption-v1/results.json) | 810,020,864-byte reduction; 71 witnesses unchanged. |
| [67 additional terminal public artifacts](tests/node-compat/storage-compaction-additional-public-adoption-v1/results.json) | 542,859,264-byte reduction; 63 witnesses unchanged. Failed/build-only/benchmark labels retained. |
| [20 newly passed ordinary Release artifacts](tests/node-compat/storage-compaction-current-release-corpus-adoption-v1/results.json) | 149,131,264-byte reduction; all 32 witnesses and the ordinary result hash unchanged; 40 temporary/rollback paths absent. No corpus rerun. |
| [72 accepted public Release engine files](tests/node-compat/storage-compaction-public-engines-adoption-v1/results.json) | 422,617,088-byte summed allocation reduction; all 38 witnesses and bytes/required metadata unchanged. Independent verification checks flags/link counts and 144 absent temporary/rollback paths. Recorded global free-space increase was only 261,779,456 bytes and is nonexclusive. No binary executed. |
| [Two Release input copy-on-write replacements](tests/node-compat/storage-cow-release-inputs-adoption-v1/results.json) | Both direct clonefile calls succeeded; source identities and all bytes/required metadata preserved, target inodes intentionally changed. Observed global free-space delta only 3,612,672 bytes, nonexclusive. No 722 MB or unique-extent recovery claim. |

The [v8–v10 audit](tests/node-compat/storage-candidate-audit-v8-v10/results.json)
found all 255 eligible artifacts already compressed and selected none. The
[SDK compression attempt](tests/node-compat/storage-compaction-release-sdk-adoption-v1/results.json)
rejected its temporary copy before adoption because the required compression flag
was absent; the original remained unchanged at that point and zero recovery is
counted. Later, the separate verified copy-on-write operation intentionally
changed the target inode while retaining its bytes and required metadata.
Global free space is volatile; nominal input sizes are not recovered capacity.

The subsequent [public-engine audit](tests/node-compat/storage-candidate-audit-public-engines-v1/README.md)
identified 72 ordinary accepted engines with 698,212,352 summed allocated bytes.
The reviewed [contingency helper](tests/node-compat/storage-compaction-public-engines-v1/README.md)
has now run successfully, after fresh preimage/quiescence/open-file checks.
Their current summed allocation is 275,595,264 bytes; the earlier source/dry-run
packet's UNAPPLIED description is historical. Its bytes and audit are unchanged.
The [declared native-output audit](tests/node-compat/storage-candidate-audit-public-native-inputs-v1/README.md)
adds 472 object/archive files across five completed public builds, 84,680,704
allocated bytes. The [final-link archive audit](tests/node-compat/storage-candidate-audit-public-link-archives-v1/README.md)
found all 140 in-root archives already counted, with no additional paths.
The original combined 782,893,056-byte ceiling preceded compressed output and
shared-block effects; it was not a recovery estimate. Additional storage
capacity was needed at that point. The user subsequently freed space and the
native start guard now passes. That later recovery is not attributed to these
filesystem operations.

### Preparation and remaining acceptance gates

Root's [corrected source-readiness receipt](tests/node-compat/foundation-scheduler/corrected-production-readiness-v1/README.md)
records **214 fresh host checks** and independent rehashes of all four source
packets and their 666/733/1,409/773 listed inputs. The separate
[activation correction review](tests/node-compat/foundation-scheduler/independent-activation-seal-correction-v2/README.md)
confirms the three rewired packets, unchanged predecessor files and preserved
case/control bodies. Those source-preparation predecessors retain null pins;
their reviewed-pin successors below supply the current execution gates.

| Packet | Completed preparation | Still required |
| --- | --- | --- |
| [Private tick scheduler](tests/node-compat/foundation-scheduler/production-adoption-v1/README.md) | Accepted in bounded v12 after diagnostic, three-engine production, fresh replay, focused/GC, both-host HTTP and independent archive gates. | Public `process`/nextTick/timers/ALS and safe reset/reuse remain outside this accepted internal layer. |
| [Production core/allocator activation v5](tests/node-compat/foundation-scheduler/production-regression-candidate-v5/README.md) | Reviewed actual pins, 667-input closure, 55 Root host checks and fresh core/allocator/GC gates; included in accepted v12. | Future source changes require new artifacts and gates. Earlier null-pin preparations remain unchanged. |
| [Normal OFF strict/Web activation v3](tests/node-compat/foundation-scheduler/production-followon-off-v3/README.md) | Reviewed parent binding, 755 inputs and 32 Root host checks. Stream/web and all four strict suites pass fresh; included in accepted v12. | New source changes need fresh validation. Earlier packets and controls remain unchanged. |
| [Fresh serial OFF replay v3](tests/node-compat/foundation-scheduler/production-release-runner-v3/README.md) | Reviewed parent indices, 1,442 inputs and 49 Root host checks. All eight stages and independent 40-component verification pass; included in accepted v12. | No reuse of these results as validation for a changed future engine. |
| [Capability activation v3](tests/node-compat/foundation-scheduler/production-followon-capability-v3/README.md) | Reviewed pins, sealed final index, 778-input closure, focused gates and both-host HTTP all independently verified; included in accepted v12. | Existing getter/Symbol/GC/reuse and capability limits remain declared. |
| [Classic streams](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md) | Corrected native/classic/Node11, replay40/follow-on20 and full20+14 v2 reviews pass. Root66794/peer0f59 verifies105 complete Node-exact returns,632 completion files and21 raw Wasmtime decodes. HTTP packaging71459 finishes raw0 with exact six0.2.10 interfaces/type-only clock. | HTTP both-host/phase and independent2f5 review pass; cost/archive/acceptance remain open. Original90660 unknown-case timeout and missing HTTP-attempt1 outer status are preserved. Native queue counters unavailable; combined-GC/raw-output limits remain explicit. Diagnostic pair reviewed; timing candidate data review passes but remains unapproved; no timing; bounded v12/counterexamples unchanged. |
| [Reset and request ownership](tests/node-compat/foundation-scheduler/reset-design-v1/README.md) | Seven task kinds and concrete ownership/cancellation/resource problems mapped; guarded traced-owner protocol and dependency-ordered ALS/reuse plan written. | Implement and validate transactional registration, safe timer ownership, resource cancellation, bounded jobs/finalizers and request epochs before exercising reset. Mixed real/immediate polling can require a callable clock capability beyond today's type-only HTTP clock import. |
| [Blob/File integration](tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) | Ownership/receiver correction candidate, source receipts, Node oracles and future test harness. | Native integration and guest validation; resolve constructor coercion, MIME/endings, File naming/time, Promise ordering, stream cancellation and lifetime gaps. Buffer Blob/File exports remain explicit refusals. |
| [Native compression](tests/node-compat/foundation-zlib/README.md) | V4 source d384/31d and actual-stage5d857788 pass:979 copies=350+632−3,85 proposal files/2261 original-context inputs. One-job normal-OFF build69972, freeze30705 and verify85956 finish0;1,024 copies/1,022 originals rehash. | All three native/freeze reviews pass; validation-only authority is separate, with runtime gates still open. V3 failure accf/c319 and raw engine62d8 remain unadmitted. Activation-v3 raw0 publishes v6; independent999d holds the missing component-tool closure. Payload a376/654f and all native evidence stay unchanged. Old3ff/dafaff+c65/89bc+a7/fd/240f holds remain; no installed support/performance claim. |

The [roadmap completion audit](docs/node-compat/roadmap-completion-audit-v1/README.md) maps the initial A–E deliverables, all24 ledger gates and remaining phase dependencies. Its [independent reviewe2816746](docs/node-compat/roadmap-completion-audit-review-v1/README.md) passes the snapshot scope: all24 gates,52 references and local links are accounted for. It is a source/evidence inventory, not a new runtime validation.

## Outstanding work, in dependency order

1. Preserve accepted v12, all historical failures/counterexamples and corrected
   native/classic/replay/follow-on/full20+14 reviews. HTTP packaging, both hosts and independent result review pass;
   retain the reviewed308-observation composition, then complete measurements and cost/artifact/archive/acceptance gates.
2. Retain full v2 correctness evidence without transferring the unknown-case90660
   failure or separate controls. Measurement M1 successor is source-reviewed;
   actual pair/source-family and completed timing reviews pass.
   Targeted RSS/startup evidence, archive preservation and bounded acceptance remain. Finish the61-case zlib corpus
   component validation. Broader streams, consumers, overloads,
   heap/teardown/ALS/reuse and performance remain separate work.
3. Resolve Blob/File ownership and semantic gaps before promoting consumer
   byte/blob operations. Verify all affected fetch/FormData/clone callers.
4. Complete a correct AsyncLocalStorage propagation design and implementation:
   capture at actual promise/native-resource creation, restore around execution,
   trace tokens, restore prior context on every exit and release request owners.
   Isolated probes do not establish production propagation across `await`.
5. Integrate measured guest compression and suitable cryptographic primitives.
   Audit algorithm/key semantics, allocation bounds, entropy selection, lifetime
   and final component size. Reuse native web code only where semantics and
   ownership match.
6. Define independent optional filesystem, HTTP, DNS/socket and CLI profiles
   with per-export contracts, exact standard import allowlists and capability
   denial tests. Validate identical artifacts on both hosts. WASI P2 sockets
   provide **no TLS**; TLS requires a separately selected guest stack, trust and
   time policy. Process creation, IPC, V8/Inspector and Node worker behavior
   remain unavailable with the selected capabilities.
7. Close lifecycle and reuse gates: environment/clock/entropy snapshot policies,
   final post-binding initialization, live-handle restrictions, cancellation,
   component reuse and request-associated state. Run broader upstream coverage
   and final size/startup/memory/throughput comparisons for released variants.
   The [native body-task cancellation implementations](host-apis/wasi-0.2.0/host_api.cpp)
   explicitly lack a supported cancellation contract for `BodyWriteAllTask` and
   `BodyAppendTask`. Reset cancellation ownership and future callback reentrancy
   therefore remain open; an idle tick-queue check alone does not close them.
8. Expand APIs only with explicit manifest changes, Node differential tests,
   actual component tests, emitted-import checks and measured demand. Retargeting
   Node/WASI/hosts requires a new compatibility baseline.

## Known limitations and decisions to preserve

- **Node callback-return parity is false for an observed case.** Node reads a
  returned object's `then` getter for an ordinary and a fresh protected listener
  once each; native Jco/Wasmtime read neither. Already-aborted queued callbacks
  ignore the returned object on both. Observed counts are `1/1/0` versus `0/0/0`.
  Callable-then and rejection behavior was not tested by this observation;
  Node `addCatch`/returned-Promise/error-routing semantics remain unimplemented.
- Target `Symbol.dispose` is an unregistered well-known symbol; pinned Node uses
  `Symbol.for('nodejs.dispose')`. No global symbol-identity rewrite is claimed.
- The v10 GC test validates combined owners: the listener closure also retains
  the disposal symbol. It does not isolate prototype-only symbol liveness.
- HTTP request counters `[1,1,1]` prove neither same-instance reuse nor request
  isolation. Those lifecycle gates remain open.
- Buffer methods, encodings, allocation and stream support are bounded by their
  manifests. Deferred callable operations throw identifiable errors; importable
  namespaces and constructors are not evidence of complete API behavior.
- Full untouched upstream suites, complete EventTarget semantics, cross-realm
  behavior, general Promise result handling, process handlers, AsyncResource,
  complete Buffer support and complete Node compatibility are not verified.
- Uncompiled templates, host-only tests, private experiments and real-component
  evidence are separate evidence classes. A new engine requires fresh runtime
  gates; a source receipt alone does not validate it.

## Keeping this tracker current

Update this file when a packet is applied, a gate passes or fails, an accepted
checkpoint changes, or a blocker/decision is discovered. Record the concrete
artifact and validation scope, retain counterexamples, and move work to completed
only when its required gates have passed. Detailed logs and immutable receipts
belong in the linked evidence directories rather than being duplicated here.
