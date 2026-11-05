# Node compatibility profile progress

Current accepted checkpoint: [foundations-v13, bounded classic streams](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

Last updated: 2026-11-05. Overall roadmap: **in progress**.

Git checkpoint requested on 2026-11-04: commit
`e7c6e2ce4f430811b90bcad77620c1e549963ca0` preserves the implementation,
documentation, source snapshots, validation evidence, historical failures and
unfinished templates. Follow-up commit
`c51cc993a536beea358ea78f4866b116300df0fb` collects the final in-flight work
and tracker. A further all-work checkpoint was requested on 2026-11-05 and
includes the subsequent source templates, executed results, independent reviews,
preserved HOLDs and this updated tracker. Work pauses at this checkpoint with
the roadmap still in progress. Native engines and external build/runtime artifacts
under `/tmp/starling-node-compat` remain outside this repository; committed
receipts retain their exact references and limits. The pinned
`54b3329b3ce818fd1f244e871e9c259b63667cda` remains the historical baseline;
the Git checkpoints do not automatically revalidate or repin earlier evidence.

The [crypto-v3 source correction](tests/node-compat/foundation-crypto/ownership-component-candidate-v3/README.md)
is now sealed at index `593a0e02…c492` with25 files. The draft checker's
`common.py` path was corrected to the actual `artifact_common.py` before its
checks. Preparation reports40 pure,1,759 source/data and8 parse checks;
Root separately verifies all25 indexed members and repeats the40 pure checks.
No bootstrap/component/key operation ran during that preparation. The separate
[independent source review](tests/node-compat/foundation-crypto/independent-ownership-component-v3-source-review-v1/README.md)
now passes at index `e9575477…80c6`, rehashing12,106 unique inputs and confirming
the actual configured context and adapter caller. A new
[Root component authority](tests/node-compat/foundation-crypto/ownership-component-v3-root-authority.json)
(`83f5dca5…2193`) launches construction-only Root session65197/PID5288. The
[actual build](tests/node-compat/foundation-crypto/ownership-component-v3-root-results.json)
finishes raw0 in38.340 operational seconds, with worker5394 raw0 and both owned
groups gone. Component `842f82e8…149d` is13,107,415 bytes, imports nothing and has
four ordinary WIT functions plus the empty non-WIT Jco `_util` helper. All22
indexed/24 actual files rehash. The separate
[artifact review](tests/node-compat/foundation-crypto/independent-ownership-component-v3-results-review-v1/README.md)
passes at index `8be6c70b…2200`, including independent WIT decode, exact nested
core bytes, core imports[]/no start and captured ESM/TLA loading-source checks.
No generated module import or key operation occurs in that construction scope.

The new [normal runtime source](tests/node-compat/foundation-crypto/ownership-runtime-candidate-v1/README.md)
is sealed at index `4cb0d2c3…9dea`:22 members,13,247 inputs,61 pure/counterexample
checks,13,274 source-data checks and7 JS/1 Python parse checks. It uses actual
four-function ESM loading, three fresh owned sessions, whole public returns and
a pinned host Node oracle. The separate
[runtime-source review](tests/node-compat/foundation-crypto/independent-ownership-runtime-source-review-v1/README.md)
passes at index `19e4dcdb…fec7`. New normal-only
[Root authority](tests/node-compat/foundation-crypto/ownership-runtime-v1-root-authority.json)
(`fc11d47b…77b4`) and the2400-second external controller launch Root61190/PID9872.
The [actual run](tests/node-compat/foundation-crypto/ownership-runtime-v1-root-results.json)
finishes raw0 in63.581 operational seconds; workers9893/9940/10005 also finish
raw0 with owned-group cleanup. All46 indexed/48 actual files rehash. Root decodes
23 complete public strings/20 case records: ten imports,55 sign attempts and50
verify attempts. All45 successful32-byte signature records match the pinned
Node/RFC oracle;45 verification booleans split25 true/20 false. Expected guarded
refusals are included in attempt counts. The
[independent actual-result review](tests/node-compat/foundation-crypto/independent-ownership-runtime-v1-results-review-v1/README.md)
passes at index `abcb6da3…2c42`, with stable contract `859649ed…7e4f`. It
independently checks every returned value/type and13,336 unique inputs, including
the full Node oracle, three distinct worker lifetimes, all raw strings and
guarded refusals. These are public/source-coupled observations, not native tracing.
The normal phase adds no Wasmtime key run, GC, OOM, reset,
finalizer/free/wipe/isolated-root observation or Node crypto export. Those and secret-temporary/allocation follow-ons
remain outstanding.

The [stock-Wasmtime source](tests/node-compat/foundation-crypto/ownership-wasmtime-candidate-v1/README.md)
now seals30 members/13,425 inputs at `6f5d38ec…6256`. Root's separate
[source review](tests/node-compat/foundation-crypto/independent-ownership-wasmtime-source-review-v1/README.md)
passes at `b51dc7f6…c37c`, including37 pure checks,59 exact JavaScript contract
comparisons and4 JS/4 Python parser checks. New
[Root authority](tests/node-compat/foundation-crypto/ownership-wasmtime-v1-root-authority.json)
(`5184d974…b9cb`) launches Root43833/PID15457 for three fresh literal
`validate()` calls on the same842f component. The [actual stock-host run](tests/node-compat/foundation-crypto/ownership-wasmtime-v1-root-results.json) finishes parent raw0 in878.006 operational seconds, with workers16735/17913/17995 raw0 and owned groups gone. All23 indexed/25 actual files rehash. Three complete decoded strings are byte-identical to the reviewed normal wrapper:12 case records, six imports,33 sign attempts,30 verify attempts,27 full tags and27 verification booleans (15 true/12 false). The [independent result review](tests/node-compat/foundation-crypto/independent-ownership-wasmtime-v1-results-review-v1/README.md) passes at `d1e3f9f1…357b`, contract `14626e81…e90e`. It strictly decodes all three raw WAVE strings, verifies47,187 decoded UTF8 bytes and every expected field, all process lifetimes and13,504 inputs. No generated JS, new Node oracle, GC, OOM, reset or timing runs; one outer export per process proves no separate-host-call interleaving or instance reuse.

The [independent control-v2 result review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v2-results-review-v1/README.md)
is now sealed at index `20380e3b…7ae9`. It verifies726 complete raw strings,
540 controls,90 setups,90 checkpoints and6 identity calls, the1,480-indexed/
1,482-actual-file output closure and all three worker exits/cleanup. This is
bounded public control correctness; it provides no private heap inspection or
global codec instrumentation. The original `pilotPrerequisitesSatisfied:false`
and `timingAllowed:false` remain unchanged; a new phase still needs its own
complete source and execution authority.

At commit `c51cc99`, the [pilot/timing source](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v1/README.md)
was eight explicitly unsealed WIP files. Its completed v1 seal is now
`55db1fc3…135b` (85 indexed files/699 external inputs), with90 pure/mock,
6,924 source-data and17 parse checks, plus separate bounded real host-only
lifecycle regressions. Independent review finds a concrete pre-action blocker:
its nested-proof reader applies a64MiB buffer limit to the actual108,619,024-byte
Node executable. Authentic prerequisite admission therefore refuses before any
worker. The sealed v1 and its [M1 review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-source-review-v1/README.md) stay unchanged. A thin v2 (`1a294044…30a2`) corrects M1 and passes17 genuine nested-descriptor read/hash tests. Its separate [M2 review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v2-source-review-v1/README.md) holds it because inherited parent lifecycle/collector files are absent from runtime source rechecks. The current donor bytes match; the guard coverage is incomplete. The [v3 source](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v3/README.md), index `c2ce5f08…64e9` (50 members/918 inputs), adds standard-only bootstraps and complete inherited-family/dependency authentication before custom imports and at final/failure rechecks. Its [independent source review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v3-source-review-v1/README.md) passes at `50102240…5bc8`; both held versions remain immutable. No codec pilot/timing
has run. The original360 workers/3,600 codec batch calls/2,160 N1 controls remain
planned. Pilot/timing phase/window/global-budget authority remains NULL. A separate [read-only plan action](tests/node-compat/foundation-zlib/cost-measurement-plan-v3-root-results.json) finishes Root76299/PID25616 raw0 in176.554 operational seconds after genuine full prerequisite guards. Its three-file output includes53,862-byte compact plan `c914e3a0…83b`, with90 expected arm/case fingerprints and three artifact tuples. No guest/codec/worker/pilot/timing action occurs. The [independent plan review](tests/node-compat/foundation-zlib/independent-cost-measurement-plan-v3-results-review-v1/README.md) passes at index `5e81da01…73c`, contract `c2240eca…bf4a`: all90 rows and three artifact tuples are independently reconstructed and25,590 physical files rehashed. This read-only plan provides no measurement execution authority.

The [calibration source decision](tests/node-compat/foundation-zlib/cost-pilot-calibration-source-root-decision-v1.json)
selects fresh paired workers at each geometric N: three same-N warmups, then one
public-call sample, stopping at the first N where both arms reach50ms. Original
caps, budget formula, timing population and separate controls are unchanged.
This selects an implementation design; pilot/timing execution and quiet-window
authority remain false/NULL. The completed v3 source binds the actual
new control-result contract. The consumer355 HTTP gate remains in progress. The new
[consumer355 HTTP construction source](tests/node-compat/foundation-stream-consumers/http-construction-candidate-v1/README.md)
is sealed at index `dc98f465…5487` (39 files/12,789 preparation references),
with54 pure/12,714 source-data/20 parse checks. It preserves the original
protected29/classic19 guest bodies and oracles, adds two request-local iterable
probes, and binds the full original355 context and12,667-file tool/native/data
closure. The [independent source review](tests/node-compat/foundation-stream-consumers/independent-http-construction-source-review-v1/README.md) passes at `dbfa80ae…5efa`. The [actual source publication](tests/node-compat/foundation-stream-consumers/http-source-publication-v1-root-results.json) finishes Root27233/PID16764 raw0 in136.683 operational seconds:32 indexed/34 actual files,18 identical payload copies with distinct inodes and private/no-symlink output. The [independent publication review](tests/node-compat/foundation-stream-consumers/independent-http-source-publication-v1-results-review-v1/README.md) passes at `be271a1a…f3b7`; that copy phase runs no genuine helper or runtime action. A separate [bundle-only action](tests/node-compat/foundation-stream-consumers/http-bundle-v1-root-results.json) now finishes Root93103/PID19432 raw0 in75.079 operational seconds, worker19665 raw0/clean. Genuine full355 preflight succeeds; all19 indexed/21 actual files rehash, with6,614,128-byte bundle `ef192251…25a5`, exact18 native/standard imports and sole `incomingHandler` export. The [whole-entry bundle review](tests/node-compat/foundation-stream-consumers/independent-http-bundle-v1-results-review-v1/README.md) passes at `8129c85c…5980`, including all53 module identities, six complete virtual data modules, nine CJS bodies and original fixtures. The separate [actual component build](tests/node-compat/foundation-stream-consumers/http-component-v1-root-results.json) finishes Root20204/PID23572 raw0 in87.647 operational seconds, worker23812 raw0/clean. Component `2ce7d990…5f33` is64,098,281 bytes; all34 indexed/36 actual files rehash. Its [independent artifact review](tests/node-compat/foundation-stream-consumers/independent-http-component-v1-results-review-v1/README.md) passes at `da7a8d79…6bad`, verifying actual decoded six0.2.10 imports, type-only duration clock/no callable core clocks, sole incoming-handler and full source/native/core provenance. The host source is sealed but held on failure-evidence capture, as recorded below; no new host request or wire-body adapter has run.
Crypto construction and bounded normal key validation above are complete;
timing has not started. Its new external watchdog/ACK path has separately run
bounded benign host-only success/refusal/timeout regressions; the first evidence-
serialization failure is preserved and the original timing v1/v2 sources remain held while the corrected v3 has passed source review and actual read-only plan preparation.

The [HTTP host source](tests/node-compat/foundation-stream-consumers/http-host-candidate-v1/README.md)
is sealed at `4b7c36f2…0e70`. Its [independent source review](tests/node-compat/foundation-stream-consumers/independent-http-host-source-review-v1/README.md)
is **HOLD**, index `58ec38a3…c641`: a failure after receiving headers or body
chunks can discard available raw response data while claiming full retention.
The other bounded source/admission/lifecycle paths pass review. No new host
request ran. A fresh correction, independent review and separately authorized
both-host execution remain outstanding; the held packet stays unchanged.

The [crypto GC source proposal](tests/node-compat/foundation-crypto/ownership-gc-candidate-v1/README.md)
seals an isolated-build/hex-pressure design at `3b6f0480…3dcf`.
Existing `NODE_COMPAT_BUILD_ROOT` supports a fresh build root; GC freeze must
also use a separate root to preserve normal exact membership and both mutable
normal CMake originals. Public Buffer hex paths reach the real stress-GC hook;
`Buffer.alloc` alone supplies allocation pressure. The [independent v1 review](tests/node-compat/foundation-crypto/independent-ownership-gc-source-review-v1/README.md)
holds it at `2ac980be…d597` because its inherited false GC/entropy flag contradicts
deliberate pressure. The [thin v2 correction](tests/node-compat/foundation-crypto/ownership-gc-candidate-v2/README.md),
index `7988586f…88b0`, removes that field and introduces versioned observations:
per-run pressure request counts[4,4,8,0], outer16, entropy false and actual native
GC count unobserved. Its full typed collector and parse checks are source-only;
independent review remains pending. The separate [isolated native implementation](tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v1/README.md),
index `2fbc01ad…05a`, contains staged build/freeze/export/bootstrap templates and
also awaits independent review. Root's native-source inspection is unfinished.
No GC stage/build/reconfiguration, key/GC workload or new GC pin/action authority
exists. Actual native/freeze/bootstrap proofs, selected-Buffer component and
complete raw runtime collection remain outstanding.

Checkpoint checks: the existing manifest test passes again under pinned
Node22.14.0 (exact Buffer/child_process namespaces and19 malformed-manifest
rejections), and all942 local links in the three current-status documents resolve.
The bounded644-file hygiene scan found no credential patterns or copied build
caches. The staged whitespace check flags one final blank line in each of the
sealed GC native `export-body.py`/`freezer-body.py` and independent timing-v3
`read-source.py`; these bytes are preserved because their seals depend on them.
The historical `deps/patches/rand.patch` trailing-space line is also preserved.
Full native/component suites are not rerun for the commit; their previously
executed, bounded evidence remains linked below. The roadmap remains in progress.

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
| Accepted production checkpoint | Bounded foundations-v13 classic streams. | Continue experimental355 consumers and the remaining roadmap gates. |
| Corrected classic streams | Full 20-workload/14-boundary gate passes all 105 observations; fresh replay, follow-on and HTTP gates pass. | Accepted in v13; preserve bounded contracts and continue remaining roadmap phases. |
| Corrected HTTP component | Both hosts, combined audit and independent final review pass; included in bounded v13. | Preserve the one-request-per-instance limitation; test new experimental engines separately. |
| Performance comparison | All168 timing workers plus18 corrected RSS workers/126 typed returns pass independent review. | Preserve the separate measurement scopes and failed RSS v1. Same-engine peak RSS ratios cross1; no universal or guest-heap benefit. |
| Codec cost tooling | Fresh source copy and55-call Node oracle pass independent review; Root input capsule is complete. All three source bundles finish raw0 and per-arm source proofs pass. The WIT/glue corrections pass review. All three v3 component builds finish raw0 with imports[]/seven-function ABI; per-arm artifact reviews pass. | V3 retention, full untimed correctness, stock Wasmtime string transport, control-v2 results and the read-only90-row plan pass independent review. Timing v1/v2 holds stay preserved; v3 source review passes. Actual pilots/timing and their explicit phase/window/budget remain pending. No performance conclusion follows. |
| Crypto key ownership | Owner/prototype source, native355 normal-OFF provenance, read-only bootstrap, actual no-import component, runtime source and first normal-key results pass independent review. | All23 whole strings/20 cases, Node oracle,45 tags/45 verify booleans and three worker lifetimes pass. Three actual stock-Wasmtime validations finish raw0 and match the whole normal wrapper; independent result review passes. GC, runtime lifetimes, secret-temporary/allocation and Node crypto API follow-ons remain. Construction holds stay preserved. |
| Native zlib extension | Three native variants and bounded normal/GC/control component results pass independent review;22 Node error-case differences are recorded. | Complete matched cost, Node-deviation contract and new-engine host/release gates; operational admission remains closed. |
| Stream consumers | Four native355 variants and bounded normal/GC/control components pass review. Context/data-closure failures remain preserved. The corrected v3 family and admission checks pass review; its entire eight-stage release retry now finishes raw0. | The full eight-stage release and all five follow-ons pass independent review, with false getter parity and raw-output limits retained. Both-host HTTP and later acceptance gates remain. Blob-dependent APIs remain refusals. |
| Corrected classic checkpoint | Accepted in bounded foundations-v13 after independent preservation and post-promotion verification. | Preserve its limits; continue consumer355 runtime and later phases. |

The detailed evidence below also retains failed attempts. A source check, syntax
check, packaged component, runtime test and accepted checkpoint are separate
completion states.

The [timing-input candidate](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-phase-candidate-v1.UNREVIEWED.json) now names the exact composed correctness, full20+14, replay/follow-on and HTTP reports. Its four Root prerequisite reviews are recorded, and Root pure/syntax checks pass. The historical candidate remains unapproved (`timingAllowed:false`). A separate [Root-issued phase](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-composed-timing-phase-v1.json) and [quiet-window receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-window-root-review-v1.json) now authorize the unchanged protocol. The real read-only preflight finishes raw0; measurement finishes at Root-observed raw0 with all42 calibration/126 timed workers and final source audit complete. The [Root result](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json), [integrity review](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and [numerical report](docs/node-compat/classic-stream-measurement-v1/README.md) pass. Registered binding saves7.85% component bytes but has no consistent same-engine warm-speed advantage; the stock-provider comparison also retains higher RSS counterexamples. Raw per-timing-call checksum strings were not saved: checks are authenticated-code/terminal supported, separate from full308-observation correctness. The coordinated quiet window has ended. The separate18-worker process RSS supplement now passes independent review, excluding full proof reports from workers; no guest-heap claim follows.

The [corrected zlib harness](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) now passes [generated-family review](tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md). [Normal validation-v2](tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile records across61 cases. [GC validation-v1](tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) also finishes raw0 with three codec cases and combined-owner ordinary-GC checks under Jco/fresh Wasmtime. Both import nothing. [Independent normal](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC](tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) reviews pass. The [combined Root receipt](tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 error-case differences and source-coupled VERNUM4880 versus Node4865; no complete parity or temporary-root-isolation claim follows. The [first fixture failure](tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) remains preserved; its three unsupported Array inputs were changed to supported Uint8Array inputs without expanding Buffer.

The [disabled-component run](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) and [independent result review](tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) pass: eight bundler denials, five complete Buffer/stub observations, zero imports,50 completion files and one output link. Generic direct-import rejection does not uniquely prove its cause; codec/backend proof, operational admission and request reuse are not inferred. A new [source-based codec cost proposal](docs/node-compat/zlib-cost-comparison-proposal.md) identifies installed fflate0.8.3 as a possible browser-only guest comparand. Pinned Jco zlib uses a prohibited custom host service, so it is not a portable guest baseline. Five local dependency/source files are pinned. A [concrete source-only cost proposal](tests/node-compat/foundation-zlib/cost-comparison-candidate-v1/README.md), index `e29c596d…47ef8`, now seals83 files/401 source inputs and30 planned cases. Its browser-entry/provider/fixture/control templates and fresh350 selector snapshots leave pair/packaging/runtime/correctness authority null. [Independent source review](tests/node-compat/foundation-zlib/independent-zlib-cost-comparison-source-review-v1/README.md), index `661f8488…dfe29`, passes all83 files/401 inputs, five independently reconstructed fixture hashes and30 case rows. The fresh packaging sealer, context-aware350 diagnostic gate, actual oracles/ABI, full guest/worker/collector and pair/action authority remain unimplemented or null. Their successor tooling and independent guest/oracle sources are being implemented as source only. The draft now contains native-pair/action guards, a real Jco finite resolver and exclusive publisher; context/collector/action integration remains in progress. Root separately [captures and checks the exact guest draft](tests/node-compat/foundation-zlib/cost-guest-draft-pure-root-results-v1.json):99 structural/staging/base64/control checks finish raw0 with zero provider calls. The snapshot is retained under `/tmp/starling-node-compat/codec-cost-guest-draft-pure-root-v1`; this does not verify compressed streams or transfer to changed final source. The author adds typed host return/throw retention and seals [guest/oracle v1](tests/node-compat/foundation-zlib/cost-guest-oracle-candidate-v1/README.md), index `473c9979…5a046` (58 files/160 references). [Independent review](tests/node-compat/foundation-zlib/independent-cost-guest-oracle-source-review-v1/README.md), index `662bf8a5…bbe47`, holds it on COST-GUEST-M1:three exact extracted-predicate counterexamples show prior-output corruption can evade its old ownership checks, despite111 pure/25 source/16 parse checks passing. No real codec defect is observed. The [v2 successor](tests/node-compat/foundation-zlib/cost-guest-oracle-candidate-v2/README.md), index `ebe8fa90…a8eae8` (38 files/199 references), adds an immutable full prior-output baseline check after the next call and restoration. [Independent v2 source review](tests/node-compat/foundation-zlib/independent-cost-guest-oracle-v2-source-review-v1/README.md), index `259a7a31…636ed`, passes116 pure/32 source/17 parse checks and demonstrates all three old counterexamples rejected. Corpus/options/7-export ABI/timed batch remain unchanged; all positive action/oracle/component/correctness/timing slots remain null. An [explicit source protocol amendment](tests/node-compat/foundation-zlib/cost-source-protocol-amendment-root-decision-v2.json) adds bounded ordinary scalar stage/validate exports so other providers actual streams can reach guest decoders on the same component. The validation wrapper makes the explicit setup/stage/adjacent-observe sequence available to the stock single-invoke CLI; timing never uses it. This is seven proposed exports with actual ABI/CLI proof still required; v1 remains historical. New source/bundle bounds are32MiB UTF8 bytes each, distinct from1MiB codec input,16MiB codec output and2MiB UTF16 wire caps. Root observes current ARG_MAX1,048,576B; actual CLI argument/environment feasibility must be proved on real streams, with no truncation or skipped cases. The amendment fixes finite control IDs and six N1 control calls per primary worker, with no subtraction or extra control sample arms; no fflate codec, bundle, component or benchmark has run.

The [bounded strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the audited JavaScript classic state machine and selects native module registration to avoid duplicate bundled code where admitted. The measurements do not justify a C++ state-machine port or a universal CPU/memory advantage. The [small-worker process RSS proposal](tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v1/README.md) is sealed at index `41a6f1b9…e6271`:20 files,10,295 authenticated inputs,35 pure checks and four syntax checks. Its18 planned fresh workers exclude full proof reports, retain all seven public scalar returns before assertions, and measure small then large on one instance. The [independent source review](tests/node-compat/foundation-classic-streams/independent-memory-probe-source-review-v1/README.md), index `daad43d3…a108b`, passes. A separate [Root authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-process-rss-supplement-v1.json) and [source review](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-source-root-review-v1.json) authorize only this supplement. The [first actual attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v1-preworker-failure-root-results.json), Root session26865/PID6839, exits1 after14.128 operational seconds before any worker launches. The existing `setup` export returns signed32 numbers (`151852933` and `-1502831163` for the selected cases); the probe incorrectly required strings in its descriptor and comparison paths. Source reviews missed this type mismatch. The partial output contains only a self-manifest and empty worker directory, with no result, completion or RSS observation. All source/review/authority bytes and failed logs are preserved. The [source-only v2 successor](tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v2/README.md), index `6b0b82df…82def0`, now passes53 pure checks against actual WIT, declarations and Node oracles; its parent shares the tested descriptor builder and worker/parent comparisons share the strict typed guard. Root independently verifies all22 indexed files and repeats those53 checks at raw0. The [independent v2 source review](tests/node-compat/foundation-classic-streams/independent-memory-probe-v2-source-review-v1/README.md), index `73fa279b…ca6e`, passes. A separate [v2 Root source review](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-source-root-review.json) and [v2 authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-process-rss-supplement-v2.json) authorize the corrected source only. The [actual v2 run](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-root-results.json), parent11856/Root session17254, finishes raw0 in98.196 operational seconds. All18 unique fresh workers exit0 with owned-group cleanup; all126 raw returns (36 numbers/90 JSON strings),599 output files and final10,348-input source audit are retained. [Independent result/numerical review](tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md), index `14611521…2fe5`, passes, with312 summaries/396 paired ratios and full raw-value/type checks. The [v2 strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains registered shared JavaScript streams: same-engine pre-final peak RSS paired ratios span0.9837–1.0018, and no controls are subtracted. The source template stays null and the coordinated window has ended. This is whole-process RSS/stage-wall evidence, with no guest-heap, cold physical startup or universal memory advantage claim. The checked-in null template stays unchanged; the first coordinated window ended after that failure.

The current [consumer355 producer v2](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/README.md) passes [source review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-source-review-v1/README.md) and [actual staging review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-stage-review-v1/README.md):59 indexed files,3,420 preparation inputs and1,173 staged overlay files. Real SDK registration syntax ON/OFF also passes. The new module remains a bounded text/JSON proposal; arrayBuffer/blob/buffer are explicit refusals.

| Consumer355 variant | Actual build/freeze/read-only verification | Independent native review |
| --- | --- | --- |
| Normal ON, entropy OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-root-results.json); engine10,002,283B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-off-review-v1/README.md). |
| GC ON, entropy OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-root-results.json); engine10,003,832B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-gc-off-review-v1/README.md). |
| Consumers OFF, zlib ON | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-root-results.json); engine9,995,242B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-disabled-off-review-v1/README.md). |
| RuntimeOnly, GC OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-root-results.json); engine10,009,523B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-runtime-review-v1/README.md). |

All four build/freeze/read-only verification gates pass. All four independent native reviews pass; the first normal consumer355 component run and its independent result review now pass. Backend-proof fields remain false/null/null and operational admission is closed. Root separately issued [validation-only pins](tests/node-compat/foundation-stream-consumers/reviewed-native-v2-validation-bootstrap-pins-v1.json), a [Root review](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-review-v1.json) and [three successful read-only bootstrap results](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-results-v1.json), without changing the checked-in null templates. The [component-test source](tests/node-compat/foundation-stream-consumers/component-validation-candidate-v1/README.md) is sealed (65 files/5,151 inputs,38 cases); source review found a control-driver mismatch between ESM and literal-CJS bundler denial messages. No action ran. The v1 [source HOLD](tests/node-compat/foundation-stream-consumers/independent-component-validation-source-review-v1/README.md), index `2a76b6c5…5a04fb`, records the literal-CJS mismatch and a separate pre-type-assertion retention gap. The [sealed v2 correction](tests/node-compat/foundation-stream-consumers/component-validation-candidate-v2/README.md), index `a75ee76c…60002b`, fixes exact category/specifier checks and records typed returns before asserting string. All38 cases/eight denials and native authority templates remain unchanged. Preparation passes64+80+13+35 checks; Root separately repeats the80 correction checks at raw0. [Independent v2 source review](tests/node-compat/foundation-stream-consumers/independent-component-validation-v2-source-review-v1/README.md), index `13bc711d…30655a`, passes. A separate [Root source review](tests/node-compat/foundation-stream-consumers/component-validation-v2-source-root-review.json) authorizes activation only. [Actual source activation](tests/node-compat/foundation-stream-consumers/component-validation-v2-source-activation-root-results.json), Root34235/PID72182, finishes raw0 in14.489 operational seconds, creating47 indexed files/7,268 consumed rows at activated-v2 (index `bfb689fe…227835`). The actual three355 tuples and packaging snapshot are bound without native metadata changes. [Independent generated-family review](tests/node-compat/foundation-stream-consumers/independent-component-validation-v2-family-review-v1/README.md), index `e894a968…90722`, passes all47 files and the exact7,268-input union. Root has separately authorized the [actual read-only preflights](tests/node-compat/foundation-stream-consumers/component-validation-v2-actual-preflight-root-review-v1.json) for normal/GC/control. [Attempt1](tests/node-compat/foundation-stream-consumers/component-validation-v2-preflight-attempt1-root-results.json) fails before native bootstrap because Root omitted the pinned toolchain environment; [Fresh attempt2](tests/node-compat/foundation-stream-consumers/component-validation-v2-actual-preflight-root-results-v1.json) passes all three actual preflights at Root-observed raw0 in57.955 operational seconds with the exact sealed environment. A [separate normal-runtime authority](tests/node-compat/foundation-stream-consumers/normal-component-validation-v1-root-authority.json) now starts Root76866/PID75204:190 planned run observations, six namespace checks and11 uncaught initialization failures. The [actual normal run](tests/node-compat/foundation-stream-consumers/normal-component-validation-v1-root-results.json) finishes at Root-observed raw0 in184.075 operational seconds:190 text/JSON observations, six namespace checks,38 fresh Wasmtime cases and11 uncaught initialization failures. Component `77e65636…30b27` is13,117,207B and imports nothing. Root rehashes all1,318 regular output files and the one module link. [Independent actual-result review](tests/node-compat/foundation-stream-consumers/independent-normal-component-validation-v1-results-review-v1/README.md), index `0f068937…9351d`, now passes all196 complete raw returns, all38 Wasmtime decodes, five1MiB strings,1,176 typed refusal records and1,318 files/one link, with8,625 finite source/native/tool/raw paths rehashed. Reviewer parser/schema attempts are retained separately and are not product failures. The [reviewed-normal bridge](tests/node-compat/foundation-stream-consumers/reviewed-normal-component-validation-v1.json) and [separate GC authority](tests/node-compat/foundation-stream-consumers/gc-component-validation-v1-root-authority.json) ran Root98263/PID78733; the [actual GC result](tests/node-compat/foundation-stream-consumers/gc-component-validation-v1-root-results.json) finishes raw0 in41.459 operational seconds:three retained ordinary-GC records, one fresh Wasmtime record and two namespace observations. Component `ff4c2aae…53421` is13,118,622B with imports[],47 regular files and one link. [Independent GC review](tests/node-compat/foundation-stream-consumers/independent-gc-component-validation-v1-results-review-v1/README.md), index `319cb371…ad5f`, passes all six complete raw returns, four GC records, two full namespaces, fresh Wasmtime decoding and47 files/one link;7,362 finite paths rehash successfully. Strong application/VM coowners remain; no isolated-temporary-root, actual-GC-count, reset/reuse, release or performance claim follows. A [separate consumer-OFF authority](tests/node-compat/foundation-stream-consumers/disabled-component-validation-v1-root-authority.json) ran Root88048/PID76515; the [actual consumer-OFF result](tests/node-compat/foundation-stream-consumers/disabled-component-validation-v1-root-results.json) finishes raw0 in42.662 operational seconds:all eight ESM/literal-CJS bundler denials precede componentization and all five Buffer/stub observations pass. Component `404f905c…4ef64` is13,046,739B with imports[],60 regular output files and one link. [Independent control-result review](tests/node-compat/foundation-stream-consumers/independent-disabled-component-validation-v1-results-review-v1/README.md), index `d041164e…ef438`, passes all eight exact diagnostics (six ESM/two CJS), five complete raw returns, fresh Wasmtime transport and60 files/one link; static component/core inspection confirms imports[] and the run()->string ABI. No callback was supplied to the unsupported exec calls, so callback behavior was not empirically tested. GC/control still require their own actions and reviewed gates. Fresh namespace/text/JSON/refusal/snapshot/GC/control component gates remain. The two shared normal project files have retained pre-GC witnesses; frozen copies remain fixed. Source failures, staging/cache preparation and exact artifact details are retained in [consumer355 history](#consumer355-source-and-build-history).

The [artifact-closure and rollforward plan](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-closure-plan-v1/README.md) maps five live Root changes. Its [independent review](tests/node-compat/foundation-classic-streams/independent-artifact-closure-plan-review-v1/README.md), index `4929aae9…86c42c`, holds promotion on two findings:12 zlib manifests contain60 direct old-Root references, and one mutable README changed after the original inspection. The other17,884 inspected files match. The old README bytes have no identified witness and must not be claimed preserved or mapped to unequal new bytes. Seven current status documents have now been separately snapshotted for a successor plan. The [sealed current-context amendment](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-closure-current-context-amendment-v1/README.md), index `371132b3…53cb`, supplies a data-only reader, exact context holds and separately identified document snapshots. Its35 reader/context checks pass, including an [independent source review](tests/node-compat/foundation-classic-streams/independent-artifact-closure-current-context-review-v1/README.md), index `1c849e61…61c00`, which authenticates35 files/154 references and executes23+12 pure checks. Promotion and bulk-archive acceptance stay held. Old preflight rerunnability is not inferred. Finish the RSS supplement in the current source context before promotion. The [publisher source](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-preservation-candidate-v1/README.md), index `fb9baef5…456b73`, and [independent source review](tests/node-compat/foundation-classic-streams/independent-artifact-preservation-source-review-v1/README.md), index `d11fd5f2…180581`, pass. A [separate Root copy config](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-private-artifact-preservation-copy-v1.json) authorizes only private PENDING preservation. The [actual copy](tests/node-compat/foundation-classic-streams/production-adoption-v1/private-artifact-preservation-copy-root-results-v1.json), Root4241/PID65406, exits0 in59.861 operational seconds:21,682 regular files/zero symlinks,10,835 copied objects including source/review capsules,17,884 protected descriptors and50,894 selected context tuples. The one unavailable README remains an omission, seven snapshots are distinct and SDK/host references remain references. Independent actual byte/context validation is underway. Root separately [accepts the declared preservation scope](tests/node-compat/foundation-classic-streams/production-adoption-v1/private-artifact-preservation-root-acceptance-v1.json) after [actual independent validation](tests/node-compat/foundation-classic-streams/independent-artifact-preservation-results-review-v1/README.md), index `f804d28f…13f7d`, which rehashes all21,682 archive files and original inputs. The archive bytes and embedded PENDING labels stay unchanged. A [new exact five-file review](tests/node-compat/foundation-classic-streams/production-adoption-v1/five-file-corrected-classic-source-promotion-root-review-v1.json) then authorizes only three corrected classic sources plus the recipe/admission tools. [Promotion](tests/node-compat/foundation-classic-streams/production-adoption-v1/five-file-corrected-classic-source-promotion-root-results-v1.json) applies at raw0:all342 live native inputs match all four corrected production manifests, with339 other inputs unchanged and file modes preserved. Independent post-promotion review now passes; its result is included in the separate v13 acceptance. The old12 zlib contexts remain held per the explicit context policy; old preflights are not rerun or redirected. A [narrow independent v13 acceptance audit](tests/node-compat/foundation-classic-streams/independent-classic-v13-acceptance-review-v1/README.md), index `2cbf351b…9a2901`, verifies11 proof indices/230 members and13 Root references, finding no concrete scope overclaim. The [post-promotion review](tests/node-compat/foundation-classic-streams/independent-five-file-classic-source-promotion-review-v1/README.md), index `b6630d51…6df0a0`, passes all five afterimages/modes, all342 source inputs and unchanged archive bytes/holds. The separate [bounded v13 acceptance](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md), index `398ecd52…2b8b2`, accepts the corrected classic checkpoint; consumer355/zlib350 remain experimental and the full roadmap is incomplete.

The [combined consumer validation receipt](tests/node-compat/foundation-stream-consumers/reviewed-component-validation-results-v1.json), SHA `36964b2d…ded65b`, now records all three independently reviewed runs:207 complete returned strings across190 normal records, four combined-owner GC records, five control records and eight namespace observations;11 initialization rejections are separate. All three components import nothing. This accepts only the bounded experimental validation result. Native source promotion, operational admission, performance, RuntimeOnly, broader regression and both-host HTTP/release gates remain separate; foundations-v13 stays the accepted production checkpoint.

The release/host source audit finds that unchanged producer9edf already supports `normal-runtime`; existing corrected342 release wrappers cannot consume355 validation pins unchanged. A [separate Root fourth-build authority](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-build-root-review.json) preserves all3,492 frozen rows of the old three variants and launches existing `build-one.py normal-runtime` under Root7122/PID80946. The [actual RuntimeOnly result](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-root-results.json) now finishes raw0 for build/freeze/read-only verification:108 build steps in297.418 operational seconds,4.822s freeze and2.870s verification. Engine `b227a8d2…8ad60` is10,009,523B, metadata `9668b23d…77b49`, freeze `3180f5b8…c5040`,1,164 frozen copies/1,162 original entries. All3,492 older frozen rows still match after build and freeze. The [release/host source plan](tests/node-compat/foundation-stream-consumers/release-host-plan-v1/README.md), index `24a71405…24350`, maps the required new context-aware355 families. The unchanged exporter also finishes raw0 for a separate four-variant **unreviewed** candidate (Root48484/PID2948,12.781 operational seconds); that data does not replace reviewed pins. [Independent RuntimeOnly native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-runtime-review-v1/README.md), index `b34b0d0c…08b9a`, passes7,247 finite references,1,164 frozen/1,162 original entries and its distinct4,650-file OpenSSL source tree. A fresh [four-variant reviewed pin document](tests/node-compat/foundation-stream-consumers/reviewed-native-v2-validation-bootstrap-pins-v2.json), SHA `93512520…a5d67b`, and [Root review](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-review-v2.json), SHA `6359ca0b…470ce4`, preserve all three earlier reviewed pin objects exactly. [All four actual read-only bootstraps](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-results-v2.json), Root9088, finish raw0. The old bdb/22fe authority, three-variant bfb family and checked-in null templates remain fixed. The [fresh release/follow-on source candidate](tests/node-compat/foundation-stream-consumers/release-gates-candidate-v1/README.md), index `a74dc603…9e5372`, now seals1,778 files/9,042 original inputs,23 reversible host edits, a102-module selected graph and complete physical tooling. All355 native bytes and176 inherited case/oracle/fixture files remain unchanged. Preparation records2,638 source checks,61 pure checks and parse-only syntax success; independent source review and actual exclusive publication remain required. It includes the eight new release stages and separate allocator/focused/getter scopes, with HTTP deferred. No RuntimeOnly component or host pass is claimed. [Root independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-source-review-v1/README.md), index `852b4bb6…b84d2`, passes all1,778/9,042 rows,23 exact reversals,1,677 source origins and the actual tooling/selected graph. The [source-only activation authority](tests/node-compat/foundation-stream-consumers/release-gates-source-v1-root-review.json), SHA `a01a8711…7a5cc`, runs the unchanged publisher as Root94949/PID21607:raw0 in9.879 operational seconds. [Root publication verification](tests/node-compat/foundation-stream-consumers/release-gates-source-v1-root-results.json), SHA `39a90af4…06e12`, checks all1,726 indexed/1,727 actual generated files. Generated index `10d6df02…4289b` binds12,544 original/local input rows; [Independent generated-source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v1-source-review-v1/README.md), index `7be057cd…7d4b7`, now passes the complete1,727-file/12,544-row closure and actual four-native lineage. Its first [actual read-only preflight](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v1-root-failure-v2.json), Root76766/PID25354, fails raw1 in12.776 operational seconds before guest execution. `metadata-admission.admit` receives the frozen355 native-source tree, which lacks the configured checkout’s767 tooling dependencies and `tests/` directory. RuntimeOnly/GC are not started. CONSUMERS-RELEASE-CONTEXT-M1 is a missed source/generated-review mismatch; original a74dc/852b/10d6/7be records remain unchanged. A separate correction must authenticate and distinguish the configured native/tool root from the frozen runtime source root, with fresh source/publication review before retry. All new runtime/release/HTTP gates remain pending. [Independent failure audit](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v1-results-review-v1/README.md), index `ffafa473…29600`, confirms the raw1/empty stdout/1,165-byte stderr and both unstarted variants. The genuine host admission helpers executed; bootstrap completion is only a source control-flow inference in this failed run. No separate persisted bootstrap pass, guest/compiler/native-code or timing result is claimed. A [bounded context correction](tests/node-compat/foundation-stream-consumers/release-gates-context-amendment-v1/README.md), index `9080e48f…79b70`, adds five reversible bridge edits and an explicit two-root helper. [Independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-context-source-review-v1/README.md), index `fc72ebac…b089a`, passes23/3,270 amendment and1,778/9,042 parent rows, both355 source roots and unchanged core/data contracts. Its [new source authority](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-root-review.json), SHA `e05c4478…128fdf`, runs Root21799/PID29349 raw0 in8.899 operational seconds. [Root generated-v2 verification](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-root-results.json), SHA `ba79b44f…36eb9`, passes1,727 indexed/1,728 actual files and12,569 union rows; generated index `562e4236…79250` awaits independent review before any retry. An [external planning-template erratum](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-planning-template-erratum.json) records one inherited, unconfigured basename still saying v1; executable publisher requires v2 and that planning field grants no authority. Sealed bytes remain unchanged. The [independent generated-v2 review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v2-source-review-v1/README.md), index `97124320…6e48`, now passes the complete1,728-file/12,569-row context, both355 source roots,767 configured tools, four native tuples and103/196 graph. Root54698 is retrying only the actual read-only normal-OFF/RuntimeOnly/GC preflights against exact562e, with separate raw logs/terminals; no guest/component action is authorized by these reads. The [actual three-mode result](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v2-root-results.json), SHA `170251e3…2cec7`, now finishes Root54698 raw0 in all modes: normal-OFF PID31713/32.536s, RuntimeOnly31933/31.953s, GC32059/26.963s, with complete224/228/220-byte JSON returns and empty stderr. [Independent actual-result review](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v2-results-review-v1/README.md), index `a17bd8ef…36d10`, passes all three and the current12,629-path source/native/tool/log closure. These are genuine read-only admission passes. A separate [release-OFF runtime authority](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v1-root-authority.json), SHA `1c2c1b9d…2633f`, starts Root6561/PID33623 for eight fresh serial correctness stages under exact562e. The [actual release attempt](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v1-failure-root-results-v2.json) stops Root6561/PID33623 raw1 after731.356 operational seconds: core/allocator/stream-web top jobs0, optional path/events/string-decoder/assert/querystring0, then util1. Four strict stages are not started. CONSUMERS-RELEASE-DATA-CLOSURE-M2 is a missing separately pinned Node-oracle producer source file in the final explicit util sourceFiles provenance list (distinct from its earlier oracle.sources builtin-hash check). Initial Root commentary incorrectly placed that failure before componentization; actual partial components and source ordering show util builds/calls occurred before line39. No completed util report/pass or independently recovered raw returns is inferred. All partial files/logs and successful stage reports remain preserved, without overall release acceptance or pass reuse; a bounded dynamic-data closure correction and fresh family/runtime retry are required. [Independent actual failure review](tests/node-compat/foundation-stream-consumers/independent-release-off-v1-failure-review-v1/README.md), index `584b9178…98a5`, validates1,933 hashes,195 regular outputs/nine links/16 components and the exact partial/raw1 scope, without decoding uncaptured util returns or adopting old passes. The [minimal report-data amendment](tests/node-compat/foundation-stream-consumers/release-gates-report-data-amendment-v1/README.md), index `b0eab614…94674`, now seals15/1,897 rows and41 source/pure checks: one immutable2251-byte producer DATA file (`fe48fc80…3c4ba`),69 explicit late reads,160/259 graph and fresh activated-v3/runtime namespaces. Current Node oracle and all runner/case/guest/native bytes remain unchanged. Independent source review and new publication/validation/runtime retry remain required. [Independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-report-data-source-review-v1/README.md), index `8c3b7cc0…54043`, now passes12,621 unique hashes, complete1897/9042 contexts and all69 finite reads/160-row graph, with no owner action. A [new source-only authority](tests/node-compat/foundation-stream-consumers/release-gates-report-data-v1-root-review.json), SHA `25a200c5…61e1`, runs the unchanged publisher Root34763/PID45020 raw0 in8.946 operational seconds. [Root v3 publication verification](tests/node-compat/foundation-stream-consumers/release-gates-report-data-v1-root-results.json), SHA `e592056d…910c`, passes1,729 indexed/1,730 actual files,12,681 union rows and the exact2251-byte datum. Generated-v3 index `a986e9b2…64916` now passes [independent generated review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v3-source-review-v1/README.md), index `897d7496…0e6ea`:1,729 indexed/1,730 actual files, exact12,681-row union and14,289 unique input tuples. It verifies all69 actual caller/data reads, four native tuples and the sole new producer datum; no helper/runtime action is performed by that review. The [actual v3 admission result](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v3-root-results.json), SHA `b7308ac4…2575cd`, finishes Root24109 raw0 for all three modes: normal-OFF PID48977/28.269s, RuntimeOnly49129/27.516s and GC49259/27.134s. All complete expected JSON returns and empty stderr are retained; admission helpers execute, with no guest/component/native compiler/host/timing action. [Independent v3 admission review](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v3-results-review-v1/results.json), index `4f49bddd…9f16f`, passes14,316 current input tuples and exactly those three outcomes. A [new release-OFF authority](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v2-root-authority.json), SHA `207a4f92…85f7`, starts Root90406/PID50986 for the entire eight-stage batch under exacta986 and a fresh v3 runtime output. The [whole eight-stage retry](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v2-root-results.json), SHA `bd402511…a57b7`, finishes Root90406/PID50986 raw0 in1,752.267 operational seconds, with empty outer stdout/stderr, clean controller/child0 and a final source recheck. All core/allocator/stream-web/optional/strict-sync/strict-runtime/strict-late/strict-callback jobs are fresh0, including util and all four previously unstarted strict stages. Root verifies346 regular outputs/13 output links/40 files matching*.component.wasm (occurrences, not unique binaries) and every producer report/completion/log hash; no old partial pass is reused. [Independent whole-release review](tests/node-compat/foundation-stream-consumers/independent-release-gates-release-off-v2-results-review-v1/results.json), index `75e18ca4…a390a`, passes13,078 current paths, all eight jobs/six optional modules,346 outputs/13 links and40 component occurrences. It independently reads zero top-level imports on those40 binaries. Typed observations include30 complete first/retained/fresh comparisons and eight paired fatal/discard cases;19 successful Wasmtime records retain hashes/decoded values without complete raw stdout, and core initializer excerpts are qualified. No unique trap-origin or global binary-uniqueness claim follows. The host controller prefix changes to v3; native/guest/runner case bodies and Node oracles stay unchanged.

A [source-only crypto inspection](docs/node-compat/crypto-native-source-notes-v1/README.md), index `570d84e0…4303c`, identifies reusable owned digest staging and the actual OpenSSL/ArrayBuffer transfer path. It also identifies a key-owner gap: CryptoKey stores released native key pointers but inherits an empty finalizer policy; the HMAC vector owner is discarded. [Independent source review](docs/node-compat/independent-crypto-native-source-notes-review-v1/README.md), index `1dd2fac2…04c02`, confirms the two note members/11 inputs and these ownership paths. It also records that CryptoKey overrides init_class directly, so a future owner fix must preserve that actual installation behavior. This remains source evidence with no runtime leak probe or source change. Key cleanup/secret lifetime must be resolved before reusing that path for Node Hmac/KeyObject; one-shot digest remains a separate candidate.

The [isolated CryptoKey owner candidate](tests/node-compat/foundation-crypto/key-owner-candidate-v1/README.md), index `216d0272…c47d0`, now seals four unapplied afterimages/18 reversible edits. It retains and cleanses owned HMAC vector storage, registers an undefined-safe foreground finalizer for vector/EVP owners, preserves actual constructor/global behavior and fixes the RSA ArrayBuffer allocator/null-view path. Two actual SDK147 Release frontend checks and37 source checks pass, with1,104 observed dependencies hashed after compilation. [Independent bounded source review](tests/node-compat/foundation-crypto/independent-key-owner-source-review-v1/README.md), index `a213a1e2…720e5`, passes35 files/1,185 inputs and all four afterimages. Full native/link/crypto/GC/lifetime integration remains required; BIGNUM error cleanup, other private copies and allocation/length policy are explicit follow-ons. No live source or existing engine is changed. The independent audit also identifies an existing prototype-as-key safety gap in sign/verify: initialized-key helpers assume reserved slots that the prototype lacks. Borrowing conclusions apply to factory-created keys; source guards must be reviewed before any such negative runtime probe. The separate [prototype-key guard candidate](tests/node-compat/foundation-crypto/prototype-key-guard-candidate-v1/README.md), index `73fbf4f2…da831`, now seals30 files/1,228 references. Two sign/verify conditions reject the intrinsic prototype through the existing invalid-key TypeError branch before slot helpers. Its four donor owner afterimages remain byte-exact; the combined source is five files/20 edits. Preparation records1,137 source/data checks, ten synthetic branch rows and one composed SDK147 Release frontend pass with1,089 post-only observed dependencies. [Independent delta source review](tests/node-compat/foundation-crypto/independent-prototype-key-guard-source-review-v1/README.md), index `f11a739c…1a648`, now passes all30/1,228 rows, exact two-edit reversal/control-flow checks and donor/review authentication. The first Root reader rejected the explicitly declared SDK clang++ alias; that raw failure remains preserved, and the corrected reader authenticates its exact target without executing it. Native/runtime integration remains required; no unsafe old path, key operation, GC, link or guest runs.

The [fresh native350 cost-pair data review](tests/node-compat/foundation-zlib/reviewed-cost-native-pair-v1/README.md), index `58c62276…66077`, now rehashes all2,048 ON/OFF frozen rows,350 source rows each and the separately streamed selected SDK archive/four headers. It grants no action authority or backend-version claim. Tooling v1 is [held](tests/node-compat/foundation-zlib/independent-cost-tooling-source-review-v1/README.md) on outside-binding environment selection and late descriptor capture. [Tooling v2](tests/node-compat/foundation-zlib/cost-tooling-candidate-v2/README.md), index `6793721e…0891b`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-tooling-v2-source-review-v1/README.md), index `9fc93b14…4c364`, with those findings closed. Its first [actual private-copy authority](tests/node-compat/foundation-zlib/cost-source-publication-v2-root-authority.json) runs Root37530/PID16564 and [fails raw1 before copying](tests/node-compat/foundation-zlib/cost-source-publication-v2-precopy-failure-root-results.json), SHA `072dafb2…89457`, in1.923 operational seconds. All5,058 base source modes match;20 dynamic proof files are0644 but the publisher mistakenly checks their desired0600 output mode as source permissions. The destination remains absent. [Independent failure review](tests/node-compat/foundation-zlib/independent-cost-source-publication-v2-failure-review-v1/README.md), index `064b8d44…a5bd5`, confirms COST-TOOLING-M3. Existing source, permissions, authority, earlier source PASS and failed receipts remain unchanged; a new v3 separates source/output modes and adds a real0644→0600 text-copy check. No Node-zlib/fflate/oracle/bundle/component/guest or timing action had run before that corrected copy. The [v3 source correction](tests/node-compat/foundation-zlib/cost-tooling-candidate-v3/README.md), index `ff208e72…b36b8`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-tooling-v3-source-review-v1/README.md), index `5fd8ea24…bb240`. A fresh [Root source-copy authority](tests/node-compat/foundation-zlib/cost-source-publication-v3-root-authority.json), SHA `3579dcb5…30524`, invokes the unchanged publisher. Root50439/PID20075 finishes raw0 in11.064 operational seconds. [Root output verification](tests/node-compat/foundation-zlib/cost-source-publication-v3-root-results.json), SHA `f292fc92…f67a7`, rehashes all10,187 indexed files and checks10,189 actual regular files,22 rebased links,471 private directories, exact source/output modes and distinct original/copy inodes. The actual index is `4621f7e7…7387b`; [Independent actual-copy review](tests/node-compat/foundation-zlib/independent-cost-source-publication-v3-results-review-v1/README.md), index `f3e17fc6…6f591`, now passes all10,189 files,5,092 independent source copies and all20 actual0644→0600 proof copies. This is a358,037,108-byte indexed source copy, not a codec or timing result. A [separate untimed Node authority](tests/node-compat/foundation-zlib/cost-node-oracle-v3-root-authority.json), SHA `31c57db9…2b150`, then invokes the exact published oracle entry under Node22.14. Root9280/PID21386 finishes raw0 in26.288 operational seconds. The [Root observation](tests/node-compat/foundation-zlib/cost-node-oracle-v3-root-results.json), SHA `b67a7de1…4f21b`, authenticates194 indexed/196 actual files,190 retained raw records and55 codec calls (30 encodes/25 decodes). It captures15 Node streams and30 case associations, an11,934,953-byte oracle and2,106,468-byte rendered module. [Independent actual oracle/render review](tests/node-compat/foundation-zlib/independent-cost-node-oracle-v3-results-review-v1/README.md), index `c0ec7f02…4957d`, passes all190 retained files,55 calls, full fixtures/streams/decoder-consumption records and byte-exact rendered-module reconstruction. The [Root reviewed-input capsule](tests/node-compat/foundation-zlib/reviewed-cost-node-oracle-v3/README.md), index `9de0a274…b5234`, rehashes all194 raw/18 peer files and contains exact independent oracle/module copies with a separate bounded review result. No fflate codec, component, guest or benchmark has executed. A minimal [source-bundle action wrapper](tests/node-compat/foundation-zlib/cost-bundle-action-candidate-v1/README.md), index `367e7960…7ce7c`, now supplies the missing CLI around the existing reviewed preflight/bundler functions. It authenticates its own source and published guard closure, accepts only the three fixed arms/new output, and retains unreviewed code/graphs. Parser-only validation and [independent source review](tests/node-compat/foundation-zlib/independent-cost-bundle-action-source-review-v1/README.md), index `70e2ac6b…06e90`, pass. A new [bundle-only Root authority](tests/node-compat/foundation-zlib/cost-bundle-v1-root-authority.json), SHA `0776fdf9…70572`, launches the unchanged wrapper367e as Root63317/PID24635. The [actual source-bundle capture](tests/node-compat/foundation-zlib/cost-bundle-v1-root-results.json), SHA `194d8ec8…17a8b`, finishes Root63317/PID24635 raw0 in91.995 operational seconds. All10 indexed/12 actual files hash correctly. Native source is2,139,474 bytes with Buffer/zlib residual imports; both FF sources are byte-identical2,158,735-byte bundles with Buffer only. Every bundle declares seven exports; physical source counts are11/12/12 and all virtual-ID arrays are empty. Three [per-arm source proofs](tests/node-compat/foundation-zlib/independent-cost-bundles-source-results-review-v1/native-on/index.json) now pass, with exact code/graphs, original source paths,7 exports and no virtual helpers: native index `d67a3411…aba7c`, FF-ON `4373b853…a91d5`, FF-OFF `5ebf8f2e…5826b`. The [shared source-bundle review](tests/node-compat/foundation-zlib/independent-cost-bundles-source-results-review-v1/README.md), index `955707ea…faaf6`, now seals20 files and passes the full12-output/10,187-publication-record closure, both1,024-row frozen native inventories and selected SDK references. These are source proofs, with no codec-provider execution or correctness transfer. A [new native-only component authority](tests/node-compat/foundation-zlib/cost-component-native-on-v1-root-authority.json), SHA `a515f2eb…86c16`, now launches actual build/ABI capture as Root53303/PID27236. That [first component attempt](tests/node-compat/foundation-zlib/cost-component-native-on-v1-failure-root-results.json) fails raw1 in23.401 operational seconds; owned worker27301 exits1 in950ms with its group cleaned up. The actual selected componentizer/splicer rejects the reserved WIT parameter name `record` in stage/validate. Nine partial files and both raw terminals/logs remain preserved; no completed component, emitted-import list, actual ABI or ordinary guest call is produced. COST-COMPONENT-WIT-M1 requires a versioned two-name WIT correction, actual old-fail/new-pass parser regression and fresh output/action before retry. Original a2fa/3279/a515 and the successful Node/source-bundle evidence remain unchanged. [Independent actual failure audit](tests/node-compat/foundation-zlib/independent-cost-component-native-on-v1-failure-review-v1/README.md), index `0075de18…610a7`, confirms141 finite inputs, all9 partials, persisted parent/worker1 and clean group shutdown. Published packager order places the WIT failure before Wizer/check_init; no ABI or Jco result is inferred. The [actual pinned WIT-parser regression](tests/node-compat/foundation-zlib/cost-component-wit-parameter-parser-regression-root-v1/README.md), index `5fe4a9a5…abb4b`, now demonstrates original raw1/corrected raw0 with only the two `record`→`input` parameter-name replacements. `wasm-tools1.235.0` creates a797-byte synthetic dummy metadata module; no StarlingMonkey guest or engine is run. A minor initial Root version assertion omitted the observed build suffix and stopped before embed; that preparation correction is retained. The [thin component correction](tests/node-compat/foundation-zlib/cost-component-wit-amendment-v1/README.md), index `e7252156…57caa`, now passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-component-wit-source-review-v1/README.md), index `6d54fd8a…015a4`:20/48 rows, full donor/tooling indices, four reversals and the complete78-row prospective child-critical closure. The unchanged worker reads the new physical WIT; separate own/base source identities and fresh v2 outputs are explicit. [Native-only v2 authority](tests/node-compat/foundation-zlib/cost-component-native-on-v2-root-authority.json), SHA `96c8eec8…199e0`, launches Root47928/PID30570 for the corrected actual packager/ABI retry. Ordinary guest workloads and timing remain disallowed. The [v2 actual attempt](tests/node-compat/foundation-zlib/cost-component-native-on-v2-failure-root-results.json) finishes parent raw1 in30.863 operational seconds and owned worker30609/raw1 in5,099ms with clean group shutdown. It successfully retains a21,404,256-byte component (`3d194a73…b1229`), actual seven-function WIT/imports[], Jco seven-function metadata, core/glue/d.ts, then fails the static JS export checker because pinned Jco also emits `export const _util = {}`. Twenty partial files remain unaccepted; seven WIT functions and the extra glue helper must be validated separately in a bounded successor. [Independent actual-failure audit](tests/node-compat/foundation-zlib/independent-cost-component-native-on-v2-failure-review-v1/README.md), index `45ded562…49cbe`, verifies163 inputs/20 partials/78 critical tuples, retained WIT/metadata/d.ts/glue and parent/worker1. It does not claim a new peer binary-WIT decode or component acceptance. No ordinary guest workload or timing call runs, and the failed build is not relabelled successful. The [bounded glue correction source](tests/node-compat/foundation-zlib/cost-component-glue-amendment-v1/README.md), index `cf3110b3…5d794`, now records39 pure/captured-source AST checks and11 parse checks, including rejection by the old checker and exact function/helper classification by the proposed checker. Its host Rolldown parser library executes only for AST data parsing; generated JS, Jco transpile, componentizer and guest do not run. Fresh v3 output roots and separate own/WIT/base/tooling identities are explicit. [Independent source review](tests/node-compat/foundation-zlib/independent-cost-component-glue-source-review-v1/README.md), index `7cb9b2b9…c5c6c`, passes469 finite hashes,20/91 own rows, all donor/tooling indices, three reversals and78 prospective critical tuples. Its exact7-function/8-name helper policy remains a finite pinned-source check. After the consumer batch stops, [native v3](tests/node-compat/foundation-zlib/cost-component-native-on-v3-root-results.json) finishes Root49919/PID38397 raw0 in35.700 operational seconds; [FF-ON](tests/node-compat/foundation-zlib/cost-component-fflate-on-v3-root-results.json) and [FF-OFF](tests/node-compat/foundation-zlib/cost-component-fflate-off-v3-root-results.json) finish serially under Root78290/PIDs38958/39049 raw0 in41.571/51.159s. Components are21,404,160/21,450,767/21,419,907 bytes, each with25 indexed/27 actual files, imports[], seven WIT/metadata/d.ts functions and exactly eight JS names including empty `_util`. Root fully rehashes each index/membership. [Per-arm native artifact review](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/native-on/index.json), index `8199f3af…01b97`, [FF-ON](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/fflate-on/index.json) `72d1d507…c1e8d1`, and [FF-OFF](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/fflate-off/index.json) `1a3774fa…33e6ec` pass raw lifecycle, source/native/oracle/code/17-descriptor bindings, emitted records and unique core/component byte relation. The [shared artifact review](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/results.json), index `9ab82077…d9893`, now seals26 files and rechecks11,836 unique inputs across all three arms, including publication/native/source/critical/SDK closures and distinct raw terminal evidence. These are componentization/static ABI results, with no ordinary guest calls, new independent binary-WIT decode, target-host execution or performance conclusion. The separate [component-build source cut](tests/node-compat/foundation-zlib/cost-component-candidate-v1/README.md), index `a2fa62b3…22f9`, seals25 files/294 references with51 pure/317 source/12 parse checks. It uses the real selected componentizer,53512-byte adapter, seven scalar exports, imports[] audit and owned worker lifecycle; all actual component/oracle/bundle proof and action slots remain separate. Its explicit proposed64MiB artifact cap/600s operational ceiling need future action authority. [Independent component-source review](tests/node-compat/foundation-zlib/independent-cost-component-source-review-v1/README.md), index `3279eb04…66512`, now passes all25/294 rows,286 base members and five copied mechanisms. The later first actual componentizer call fails on the WIT parse error above; source-level review had not exercised a WIT parser. Actual ABI/imports/Jco/ordinary guest correctness remain unproved, and no transpiler or ordinary guest action runs.

## Detailed evidence and limits

Current position: **foundations-v13 is accepted, bounded**, through the
[Root classic acceptance receipt](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). Its [v12 parent](tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md) remains historical evidence.
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
The completed [measurement](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json) finishes raw0:42 calibration/126 timed workers plus final source audit,1,037 output files. [Integrity review3843d019](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and the [numerical analysis](docs/node-compat/classic-stream-measurement-v1/README.md) are separate evidence. The [Root strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the shared guest-JS stream state machine and native byte primitives; registered imports avoid a duplicate bundle and save7.85% measured component bytes, with no consistent same-engine warm-speed or memory advantage. The optional unused installation stays OFF. Stock-provider differences include a different provider/scheduler; FNV/validation stays timed and controls are not subtracted. Public RSS includes proof/V8 overhead, and raw timing-call compact returns were not retained. The separate18-worker process RSS supplement passes [independent result review](tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md); no private heap or production-engine performance claim follows.

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
| [Classic streams](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md) | Corrected native/classic/Node11, replay40/follow-on20, full20+14, HTTP both hosts and308-observation composition pass independent reviews. The168-worker timing protocol, integrity and numerical reviews pass; bounded strategy is recorded. | Preserve the independently reviewed18-worker process RSS result and the artifact closure, resolve old-Root context dependencies and review bounded acceptance. Original failures and raw-output/combined-GC limits remain explicit; v12 is still the accepted checkpoint. |
| [Reset and request ownership](tests/node-compat/foundation-scheduler/reset-design-v1/README.md) | Seven task kinds and concrete ownership/cancellation/resource problems mapped; guarded traced-owner protocol and dependency-ordered ALS/reuse plan written. | Implement and validate transactional registration, safe timer ownership, resource cancellation, bounded jobs/finalizers and request epochs before exercising reset. Mixed real/immediate polling can require a callable clock capability beyond today's type-only HTTP clock import. |
| [Blob/File integration](tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) | Ownership/receiver correction candidate, source receipts, Node oracles and future test harness. | Native integration and guest validation; resolve constructor coercion, MIME/endings, File naming/time, Promise ordering, stream cancellation and lifetime gaps. Buffer Blob/File exports remain explicit refusals. |
| [Native compression](tests/node-compat/foundation-zlib/README.md) | Three actual350 builds/freezes pass independent review. Corrected v8 harness normal validation has283 bounded records/138 full-byte successes; GC has three codec records; disabled selection has eight bundler denials/five Buffer-stub records. All result reviews pass. | Operational admission,22 Node error-case differences/VERNUM release contract, matched codec cost, new350 selected-host/release regressions and archive gates remain. Metadata backend-proof fields stay false. Original failed native/harness/fixture attempts remain historical failures. |

The [roadmap completion audit](docs/node-compat/roadmap-completion-audit-v1/README.md) maps the initial A–E deliverables, all24 ledger gates and remaining phase dependencies. Its [independent reviewe2816746](docs/node-compat/roadmap-completion-audit-review-v1/README.md) passes the snapshot scope: all24 gates,52 references and local links are accounted for. It is a source/evidence inventory, not a new runtime validation.

### Consumer355 source and build history

Initial source-only stage (historical; superseded by the build/runtime states above):

The [consumers proposal](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/README.md) is source-only. Its [independent review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-source-review-v1/README.md) holds on CONS355-M1: two post-link paths name a missing child codec-evidence.py instead of the authenticated parent350 helper. The [v2 successor](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/README.md) and [independent source review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-v2-source-review-v1/README.md) now pass (39 files/506 inputs). Native355 payload bytes remain unchanged. [Actual SDK frontend checks](tests/node-compat/foundation-stream-consumers/sdk-registration-syntax-v1/README.md) pass consumer ON/OFF with empty diagnostics and1,036/1,035 dependency hashes. This is syntax/API evidence only; no355 configure/build/link/install or runtime action has run. The genuine355 producer is being prepared with distinct native/tool/original-preparation contexts. Positive Web inputs must select the existing node:stream/web iteration wrapper; raw global ReadableStream is not implicitly adapted.

The following records preparation checkpoints and completed build attempts; the current table above takes precedence over historical pending statements.

The [consumer355 producer](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1/README.md) is sealed at index `ab88215a…8e25`:53 files,3,357 preparation references,767 native-tool rows,50 pure checks and three syntax checks. All three planned variants keep zlib ON; the disabled variant disables only consumers. The source framework distinguishes configured, frozen and original preparation roots, and is not a component-packaging closure. The [independent producer review](tests/node-compat/foundation-stream-consumers/independent-native-integration-source-review-v1/README.md), index `6e24de20…f6c5bc`, holds C355-M1: the configured parent codec helper can execute before the current767 tool hashes are checked. Staging, native builds, installation and runtime validation remain unexecuted; the v1 packet remains held. The [v2 producer correction](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/README.md), index `9edf31c1…3a378`, authenticates current tool dependencies at the start of the frozen reader. Its59 files/3,420 inputs,50 source checks,19 ordering/scratch checks and three syntax checks pass. The native355 payload is unchanged. [Independent v2 source review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-source-review-v1/README.md), index `28300826…827811`, passes. Root [source review](tests/node-compat/foundation-stream-consumers/native-integration-v2-root-source-review.json) authorizes staging only. [Actual publication](tests/node-compat/foundation-stream-consumers/native-integration-v2-root-stage-results.json), Root session7465/PID11018, exits0 in6.090 operational seconds and publishes1,173 files at `/tmp/starling-node-compat/consumers-source-v2`, on genuine detached54b HEAD with no Git alternates. Root independently verifies its59 staged indexed files; [Full actual-stage review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-stage-review-v1/README.md), index `371b7880…1b64d`, passes:1,173 overlay files plus508 genuine baseline files,3,420 original-context inputs and only three genuine documentation symlinks outside the consumed overlay. The [normal-OFF build review](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-build-root-review.json) authorizes one fresh Release build. That build ran under Root session4055/PID14781 with consumers/zlib ON, entropy OFF, one job and2GiB/800MiB disk guards. The [normal build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-root-results.json) now finishes raw0 for all three commands:108 build steps,10,002,283-byte engine `661ef794…f0c79`, metadata `860e9521…62f92`, freeze `fadc83ce…26096`,1,164 frozen copies and1,162 original-reference entries. Its [independent native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-off-review-v1/README.md), index `b80489f4…124d6c`, passes:1,164 frozen files,1,162 pre-GC original entries,62/4/6 native command groups plus the separate embedding command, selected native codec/header/install order and complete locked dependency provenance. A separate [GC build review](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-build-root-review.json) follows the reviewer’s complete pre-GC original checkpoint; [GC build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-root-results.json), Root sessions60577/57664/26486, also finishes raw0:17 incremental steps,engine `b378dea3…910e7` (10,003,832 bytes),metadata `675131c9…87672`,freeze `0268e073…1101e` and1,164 frozen files. [Independent GC native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-gc-off-review-v1/README.md), index `010fbd51…a9db91`, passes the actual GC files/commands and rechecks all normal frozen copies; no guest-GC/root-isolation claim follows. The [consumer-OFF control](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-build-root-review.json) ran under Root99558/PID39882 on its separate s0 project, with zlib ON and the same62/private6 layout; its [build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-root-results.json), Root99558/3263/24291, now finishes raw0:108 steps,engine `81ffa152…e5110` (9,995,242 bytes),metadata `8e05a705…f76ac`,freeze `9d6fd222…4a4e1` and1,164 frozen files. Independent control review is underway. All three native artifacts were exported into a separate unreviewed candidate document at exporter raw0; no admission or runtime proof was issued. Only the two expected shared normal CMake/compile-database originals may reconfigure; their retained snapshots and all frozen normal files remain strict. No component or guest has run. [Cache preparation attempt2](tests/node-compat/foundation-stream-consumers/native-integration-v2-cache-preseed-attempt2-root-results.json) separately copies four hash-verified download/tool cache files into the fresh build directory, with independent inodes. The initial helper failed before copying files because local Python lacks hashlib.file_digest; its [failed receipt](tests/node-compat/foundation-stream-consumers/native-integration-v2-cache-preseed-root-results.json) and empty-directory observation are retained. The corrected streaming-hash retry passes. No checked-out source, engine, metadata or codec evidence was copied.

## Outstanding work, in dependency order

1. Preserve bounded foundations-v13, its v12 parent, historical failures and
   counterexamples. Corrected classic source promotion, declared archive scope,
   runtime/HTTP gates, timing and small-worker RSS reviews are complete. Keep the
   old twelve zlib contexts held; future executions need fresh context-aware
   families rather than rerunning or redirecting old preflights.
2. Complete consumer355 registered-module runtime validation: the normal190-observation/11-initializer run finishes raw0 after all three
   native and preflight gates pass. Its independent result review and GC4 review pass behind the
   reviewed-normal gate. The separate disabled8-
   denial/5-smoke gate and its independent result review pass. RuntimeOnly build/freeze/verify, independent review and four-variant read-only bootstrap pass; fresh full regression
   and same-artifact host gates remain, with their source integration plan
   being prepared separately. Zlib350 normal/GC/control results
   pass within their bounded contract; operational admission, the explicit
   22-case Node-difference contract, matched cost, RuntimeOnly and new-engine
   host/release gates remain. The new codec cost work is source-only. Broader
   streams, consumers, overloads, heap/teardown/ALS/reuse and performance require
   separate evidence.
3. Resolve Blob/File ownership and semantic gaps before promoting consumer
   byte/blob operations. Verify all affected fetch/FormData/clone callers.
4. Complete a correct AsyncLocalStorage propagation design and implementation:
   capture at actual promise/native-resource creation, restore around execution,
   trace tokens, restore prior context on every exit and release request owners.
   Isolated probes do not establish production propagation across `await`.
5. Integrate measured guest compression and suitable cryptographic primitives.
   Audit algorithm/key semantics, allocation bounds, entropy selection, lifetime
   and final component size. Correct the independently confirmed CryptoKey
   native-owner/finalizer gap before Hmac/KeyObject reuse; a bounded one-shot
   digest can be assessed separately. Reuse native web code only where semantics
   and ownership match.
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

The [correctness loader v2 source](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v2/README.md), index `d2516c93…befeb`, seals51/493 rows with193 pure/parser,74 source/data and21 syntax checks. It implements the observed ESM/TLA/relative-core/package contract and a228-worker untimed schedule, while all actual proofs/action slots remain NULL. Independent source inspection finds a concrete pre-action boundary defect: Node cross-input retention accepts only Buffer, but the genuine stage decoder first supplies a plain Uint8Array. That would reach the JSON writer and fail before its codec call. [Independent source HOLD](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v2-source-review-v1/README.md), index `751147af…28ecd`, confirms51/493 rows,13 exact copies and the planned schedules while identifying ZLIB-JCO-CORRECTNESS-V2-M1. The immutable source stays held. A [thin v3 source successor](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v3/README.md), index `0124b94f…8cb8c`, seals26 files/22 own references and three afterimages/28 reversible edits while retaining the complete51/493 donor unchanged. The actual callback snapshots precisely the ordinary Uint8Array/Buffer window before awaiting persistence. Preparation passes36 pure retention tests,1,333 source/data and five syntax checks, including genuine stageRecord DATA reproducing the old failure without a codec call. [Independent v3 source review](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-source-review-v1/results.json), index `abeb157a…aa5a`, passes all26/22 own and51/493 donor rows plus28 reversible edits, closing M1 within its source scope. The sealed template stays NULL. A separate [Root untimed authority](tests/node-compat/foundation-zlib/cost-jco-correctness-v3-root-authority.json), SHA `235d391b…7daf6`, binds the exact three actual artifact reviews and unchanged construction authorities. Root86618/PID49994 starts the first real Jco/Node correctness action with228 planned owned workers and a7500-second outer operational deadline. The [actual full correctness result](tests/node-compat/foundation-zlib/cost-jco-correctness-v3-root-results.json), SHA `8a9a2141…6a21d`, finishes Root86618/PID49994 raw0 in1,637.224 operational seconds. Root rehashes11,440 indexed/11,442 actual files and712,222,394 indexed bytes,228 raw0/clean worker terminals,360 primary observations,135 main crossdecode edges and separate FF-OFF15 encodings/15 fresh Node/45 guest edges. Index `e8da5ddb…5aa7e` and completion `d3e0bfb5…7d3e1` bind the complete20,237,274-byte result. Three retained/90 fresh/90 main guest/45 OFF guest processes are actual; all60 Node decoder edges retain full typed/input/output records through the corrected U8 binary boundary. [Independent full correctness review](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-results-review-v1/results.json), index `e03bb0db…48083`, now passes23,454 current input tuples, all3,828 complete primitive returns,1,980 full output payloads,60 fresh Node edges/160 U8/Buffer binary files and228 unique clean workers. Its [stable result contract](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-results-review-v1/result-contract.json), SHA `25411f2e…936f1`, records5,448 named entries/2,475 guest codec calls/495 untimed codec N1 calls and explicitly zero executed controls. Ownership/input/prior stability is verified as full returned bytes plus instrumented reports, with no post-exit heap inspection. Actual control workloads remain required before pilot/timing. Stock Wasmtime, native builds, source promotion, pilot and timing remain forbidden by this Jco action.

The [crypto native integration source](tests/node-compat/foundation-crypto/native-integration-candidate-v1/README.md), index `10a87c1d…26db`, seals38 files/1,271 bounded references for a genuine new355 identity: exactly five composed owner/guard replacements and350 unchanged native sources. New policy/recipe/named build-only validator/stage/freeze namespaces have NULL pins/actions, with no ordinary-selector reopening. Preparation records74 source/data, five negative models and19 syntax checks. The [independent v1 integration review](tests/node-compat/foundation-crypto/independent-crypto-owner355-native-integration-source-review-v1/README.md), index `109a929f…6f7c`, holds the JS context contract: Python authenticates configuredSourceRoot, but the JS wrapper drops it despite its documentation. No caller or native staging failure is inferred. A [v2 context successor](tests/node-compat/foundation-crypto/native-integration-candidate-v2/README.md), index `68b6f2a5…5575`, returns and rechecks the genuine configured/frozen roots, with fresh recipe/tool hashes and stage/build/freeze namespaces. All five native payloads and the full355 policy/helper remain unchanged. Preparation passes74 source/data,21 pure mapping fixtures and21 syntax checks without calling the helpers; [Independent correction review](tests/node-compat/foundation-crypto/independent-crypto-owner355-native-integration-v2-source-review-v1/results.json), index `ebbfda80…60dac`, passes44/1,323 rows,1,711 unique hashes and16 reversals, resolving the bounded context defect. The sealed template pins/actions stay NULL. A [separate source-stage authority](tests/node-compat/foundation-crypto/native-integration-v2-source-stage-root-authority.json), SHA `f7e168d2…22a1f`, runs the unchanged publisher as Root91711/PID50423 raw0 in1.387 operational seconds. [Root actual-copy verification](tests/node-compat/foundation-crypto/native-integration-v2-source-stage-root-results.json), SHA `a0654a8e…5d101`, checks all1,311 new copies, modes and distinct source/destination inodes, full355 native/922 tool rows and detached54b/no-alternates clone. [Independent actual-copy review](tests/node-compat/foundation-crypto/independent-native-integration-v2-stage-review-v1/results.json), index `8c0583a4…41c79`, passes all1,311 copies and2,632 unique file tuples, exact modes/inodes and clone metadata using read/hash checks only. A separate [normal Release/OFF build authority](tests/node-compat/foundation-crypto/native-integration-v2-normal-off-build-root-authority.json), SHA `e7a59da2…047b2`, starts Root62629/PID53008 with jobs1, GC/OOM/debug off,2GiB start/800MiB stop guards and a7200-second operational ceiling. The [actual normal-OFF native result](tests/node-compat/foundation-crypto/native-integration-v2-normal-off-build-root-results.json), SHA `0749a034…c8e28`, finishes Root62629/PID53008 raw0 in646.200 operational seconds, with owned build-group cleanup and empty stderr. Engine `36bd8508…ebc05` is10,002,820B; sidecar `8bafca1a…3ca37` is362,391B. Root rehashes all1,311 staged sources/modes after build and verifies full355+external3, exact five owner/guard replacements,62 native/4 strict/6 private/1 embedding commands, actual WebCrypto cache ON/install1/three changedCPP commands. An initial Root reader wrongly assumed WebCrypto was in the selected observed-option subset; its KeyError is retained separately and corrected by reading the authenticated CMake cache/build evidence. This is a reader-preparation error, not a native build failure. No new native artifact is independently accepted yet. A pre-execution freeze audit finds the unchanged freezer still expects the old CONSUMERS selector state, while the actual named admission returns CRYPTO_OWNER355. Freeze is held before any invocation/output pending a bounded separate correction; the build/staged source remains immutable. Link/lifetime/guarded-key tests and required private-copy/bounds follow-ons remain open; no new Node crypto export is implemented.

The [untimed correctness preparation](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v1/README.md), index `61029551…f305a`, seals32 files/609 references with168 pure/data,210 source/data and16 syntax checks. It provides360 planned primary observations and135 planned provider edges, plus separate FF-OFF15/15/45 schedules and raw-before-assert collectors. These360 observations are distinct from the proposed360 timing workers. This source entry always refuses until an observed-glue loader and actual component/ABI proofs are implemented and reviewed; no provider, guest, codec or worker runs. The [Node-deviation contract proposal](tests/node-compat/foundation-zlib/node-deviation-contract-candidate-v1/README.md), index `de59758c…31469`, separately preserves all22 differences,11 original null labels and absent messages. It proposes classifications for explicit profile limits and six errno fix candidates; all runtime/policy/operational decisions remain unapproved.


The deviation proposal’s [qualified independent review](tests/node-compat/foundation-zlib/independent-node-deviation-contract-source-review-v1/README.md), index `8ccd5a15…28100`, passes6/129 data integrity and the22/100/22 row mappings, but holds its broad mutability wording: pinned Node already freezes `codes`. A [bounded wording amendment](tests/node-compat/foundation-zlib/node-deviation-contract-mutability-amendment-v1/README.md), index `b8ec1f65…9413a`, withdraws that claim and preserves all22 observations; no uncaptured prototype/own-property claim or runtime decision is introduced. Both policy proposals remain unapproved. [Independent bounded wording review](tests/node-compat/foundation-zlib/independent-node-deviation-mutability-source-review-v1/README.md) now passes7/eight reference hashes and both exact afterimage reversals, verifies pinned Node’s ObjectFreeze(codes), and confirms every other contract value unchanged. Only the narrow wording correction is accepted; no runtime or policy decision is made.

The [stock Wasmtime transport source proposal](tests/node-compat/foundation-zlib/cost-wasmtime-transport-candidate-v1/README.md), index `345ce70f…1be56`, inspects pinned42.0.1 help/source and exact wasm-wave dependency. It supplies WAVE string escaping, a strict typed-string stdout parser and argv accounting, with49 pure/40 data/two syntax preparation checks. Current ARG_MAX is1,048,576 bytes: the known largest retained Node gzip requires699,737 expression bytes, while the broader allowed1MiB compressed input needs1,398,104 base64 bytes alone and cannot fit that aggregate limit. These are DATA/accounting findings, not actual largest-record execution or per-argument proof. [Independent transport source review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-transport-source-review-v1/results.json), index `ca663930…b7fd2`, passes29/52 source rows,78 unique paths,21 locked crate members and15 exact Node sizing models; no runtime feasibility is inferred. A separate [Root identity-only authority](tests/node-compat/foundation-zlib/cost-wasmtime-identity-v1-root-authority.json), SHA `7e79829f…c98a6`, runs three fresh stock Wasmtime42 processes as Root25871/PIDs67649/68741/69829. All finish raw0 with1102/1096/1096-byte complete stdout, empty stderr and observed owned-group cleanup. [Root typed-return validation](tests/node-compat/foundation-zlib/cost-wasmtime-identity-v1-root-results.json), SHA `2fa1e262…b74f0`, fsyncs raw files before decoding, validates all three WAVE-string/inner-JSON values and exact argv/environment accounting. Each first identity shows empty prepared/staged/retained state, one identity entry and zero codec/control calls. [Independent actual identity review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-identity-v1-results-review-v1/results.json), index `49090a30…d94f5`, passes11,953 current tuples, retains independent fsynced raw copies and decodes the complete three WAVE strings/full inner identities. Exact argv/environment models are286/286/287 bytes. Root exports execute; reviewer runs read/hash/data code only. No string argument, stage/validate, codec, reuse or largest-record proof follows. Actual small/all-provider-largest host probes remain required with exact environment accounting and no truncated/skipped streams.

The [pre-execution crypto freeze-contract audit](tests/node-compat/foundation-crypto/independent-native-integration-v2-freeze-contract-review-v1/results.json), index `62cf4f2c…cbc912`, preserves91 original/staged source tuples and identifies the single old-state comparison. It also requires the corrected active freezer to be frozen under its actual bytes and keeps the old staged freezer explicitly as donor DATA; native recipe/policy/helper/tool922 identities need not change for that separate operation. The genuine verifier is a function API, not a CLI. A separate bounded freezer-source successor is being prepared with exact staged context, own/peer/Root authority checks, active/donor provenance and a14-group native evidence checklist. The old freezer is not executed, build inputs stay unchanged, and no frozen crypto artifact or runtime result is claimed.

The [first bounded ownership harness source](tests/node-compat/foundation-crypto/ownership-validation-candidate-v1/README.md), index `21816be7…2d0cd`, seals21 text files/75 inputs and82 static/data/two parse checks. It proposes four ordinary scalar exports and raw/JWK/retained/new-guard HMAC-SHA256 cases, full32-byte tags and input-window/key-copy observations, backed by the actual existing Promise/event-loop scalar bridge. Its within-one-export validate wrapper is separate from host interleaving or instance reuse. All native/component/tool/ABI/action slots remain NULL, with no crypto/Node-oracle/component/helper/guest execution. [Independent harness source review](tests/node-compat/foundation-crypto/independent-ownership-validation-source-review-v1/results.json), index `6918a280…075d9`, passes21/75 rows,87 unique paths and actual Promise bridge/refusal/counter contracts. No finalizer-count, isolated-root, all-copy-erasure or broader Node crypto claim follows.

The [corrected freezer source](tests/node-compat/foundation-crypto/native-freezer-source-amendment-v1/README.md), index `0ff37e52…ecccd`, passes [independent source review](tests/node-compat/foundation-crypto/independent-native-freezer-source-review-v1/results.json), index `aa25647e…4a06b`:13/65 rows,1,390 unique tuples and seven exact reversals. A [separate freeze authority](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-root-authority.json), SHA `9d41c006…6b81`, runs the actual corrected entry Root25578/PID79054 raw0 in9.588 operational seconds. A [read-only verifier authority](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-verify-root-authority.json), SHA `1e355a0c…f89ed`, authenticates all configured/source/control bytes and calls the genuine staged `verify_frozen_variant(normal-off, return_receipt_digest=True)` function as Root43902/PID80524 raw0 in4.169s. [Root combined freeze/verification](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-root-results.json), SHA `88cfe19d…d4bba`, checks1,390 frozen copies/1,387 originals,1,391 actual files, no symlinks, full355+external3 and actual active/donor tooling. Freeze receipt `d088286c…f7760` retains engine `36bd8508…ebc05`/10,002,820B and exact sidecar `8bafca1a…3ca37`. Backend proof remains false/null; no metadata is projected or rewritten. [Independent normal-OFF native provenance review](tests/node-compat/foundation-crypto/independent-native-crypto-owner355-v2-normal-off-review-v1/results.json), index `27b88cae…44f36`, passes8,821 unique files, all1,390 copies/1,387 originals and14 evidence groups, including actual SDK30/LLVM21/wrapper/optimizer chain,4,650 pinned OpenSSL sources/locked Rust and selected codec witnesses. Pure GNU archive-index decoding finds unique OPENSSL_cleanse and EVP_PKEY_free definitions in the selected linked archive; no symbol tool or crypto operation is run by the reviewer. A normal-original checkpoint protects all current original bytes and identifies exactly two prospective live CMake cache/DB exceptions for a future separately authorized reconfigure; all frozen copies stay strict. Reviewed bootstrap data and actual packaging/ABI/HMAC/lifetime validation remain separate gates. No key, crypto, GC, guest/host or timing operation runs in build/freeze/verification.

A separate [five-scope follow-on authority](tests/node-compat/foundation-stream-consumers/release-gates-followons-v2-root-authority.json), SHA `c64b28c5…8eeea`, starts Root90775/PID82335 for fresh serial allocator-GC/focused-OFF/focused-RuntimeOnly/focused-GC/getter checks under exacta986. Independent release review remains pending; these additional tests do not adopt its results as acceptance. Each scope has its own new output/controller/raw logs and30-minute inner/31-minute outer operational bound. The unused v1 authority is preserved: it incorrectly put a generated-index descriptor in the informational review field; v2 supplies the complete source-review pair before any action. HTTP, native builds, timing, source promotion and acceptance remain forbidden by this action.

The [all-provider argv DATA model](tests/node-compat/foundation-zlib/cost-all-provider-argv-model-v1-root-data.json), SHA `7ce260e8…27a6f`, authenticates the60 actual Node/native/FF-ON/FF-OFF records from the completed Root-observed correctness output, checks full encoded bytes/SHA and models each decoder component with the exact proposed one-variable environment. The largest is Node large-PRNG gzip:700,013/700,013/700,014 modeled argv/environment/pointer bytes for native/FF-ON/FF-OFF, all below current ARG_MAX. This runs only pure JSON/base64/hash/WAVE/accounting code; no guest/codec/host invocation, per-argument/kernel proof, accepted correctness transfer or action authority follows. Actual stock-Wasmtime small/largest input tests and actual controls remain gates before pilot/timing.

[Independent five-followon review](tests/node-compat/foundation-stream-consumers/independent-release-gates-followons-v1-results-review-v1/results.json), index `063abec9…b475c`, now verifies Root90775 all five raw0 scopes: allocator-GC82335/106.127s, focused-OFF83082/182.966s, RuntimeOnly84049/175.922s, focused-GC84800/159.509s and getter85675/125.458s. It rehashes12,985 paths,221 regular outputs/five links/20 component occurrences. RuntimeOnly eight components import only standard random@0.2.10; the other12 import nothing. Full16+4+9 Node arrays match across retained OFF/Runtime records, eight complete raw quoted returns decode,11 fatal/discard pairs and combined-owner GC commands match. Allocator-GC Wasmtime stdout is decoded-only. Getter observationCompleted remains true while Node compatibility remains false: Node1/1/0, guest0/0/0; it is a confirmed counterexample, not parity. HTTP, source promotion, timing and production acceptance remain open.

The [actual small/largest stock-Wasmtime string result](tests/node-compat/foundation-zlib/cost-wasmtime-strings-v1-root-results.json), SHA `4e37c006…e3e0f`, now finishes Root37792 with six fresh raw0/gone-group processes and complete6,232-byte small/1,404,206-byte large stdout records, empty stderr and12 full returned outputs equal to the64-byte/512KiB fixtures. The separate [Root codec-string authority](tests/node-compat/foundation-zlib/cost-wasmtime-strings-v1-root-authority.json), SHA `91d57160…917f5`, allows only those six validations. [Independent transport review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-strings-v1-results-review-v1/results.json), index `663324c5…396d`, verifies23,596 inputs, all60 requests/180 per-arm argv models and the unique maximum:699,738 NUL-inclusive argument bytes and700,013/700,013/700,014 aggregate bytes accepted on this pinned Darwin/Wasmtime host. The [stable transport contract](tests/node-compat/foundation-zlib/independent-cost-wasmtime-strings-v1-results-review-v1/result-contract.json), SHA `bdd4fee8…208c4`, records six outer validates/30 named entries/12 codec calls/zero controls. Returned state stays prepared/staged with retained output; no idle/reset/reuse/interleaving, general per-argument/future-record/resource bound or performance claim follows. Actual controls remain required.

The [control supplement source](tests/node-compat/foundation-zlib/cost-jco-control-correctness-candidate-v1/README.md), index `ad0d651f…f7a23`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-jco-control-source-review-v1/results.json), index `d6f72a45…7bb58`, after127 pure/206 data/seven parse preparation checks. It proposes three fresh sessions/726 returns/540 controls/zero codecs via narrow loader/collector afterimages. Its [first actual control authority](tests/node-compat/foundation-zlib/cost-jco-control-v1-root-authority.json), SHA `b805d8e1…7608c`, runs Root54743/PID91129 and [fails raw1 before any worker](tests/node-compat/foundation-zlib/cost-jco-control-v1-failure-root-results.json), SHA `1e1b07e4…6a38`, after196.405 operational seconds. COST-CONTROL-PARENT-DIRECTORY-M1:parent creates jobs but not the processes directory required by the genuine durable logger; lstat fails before launch record/spawn. Exact partials are one descriptor and failure.json, completedOrigins is empty and post-failure source audit passes. Read-only prerequisite helpers execute; no worker/generated module/guest control/codec runs. Prior correctness and transport proofs remain valid. [Independent actual failure review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v1-failure-review-v1/results.json), index `534f2d86…429a5`, verifies558 files/530 descriptor-critical rows, exact raw1 and the pre-launch caller/callee path. It explicitly records the missed directory precondition in the old source PASS. A [thin v2 correction](tests/node-compat/foundation-zlib/cost-jco-control-correctness-candidate-v2/README.md), index `3b566083…d1ff1`, seals29 files/190 references, two afterimages/ten reversible edits and passes79 source/data, five parse and eight genuine benign-lifecycle checks. The old missing-dir path fails before launch; the prepared directory path runs one benign Node child at raw0 with cleanup and complete four-file closure. No guest/provider/preflight/control/codec runs during preparation. [Independent control-v2 source review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v2-source-review-v1/results.json), index `20cb3efa…6bbdeb`, passes29/190 rows,228 unique hashes, ten reversals and the complete benign regression. A [new v2 Root authority](tests/node-compat/foundation-zlib/cost-jco-control-v2-root-authority.json), SHA `38f6a045…3ddef7`, starts Root4837/PID96423 against the fresh v2 output, with the same726-return/540-control/zero-codec schedule. The [actual v2 control result](tests/node-compat/foundation-zlib/cost-jco-control-v2-root-results.json), SHA `9b22479e…92dde`, now finishes Root4837/PID96423 raw0 in219.064 operational seconds. Root rehashes1,480 indexed/1,482 actual files and2,513,957 indexed bytes, all three clean worker terminals and the complete726-return/90-setup/270-distinct-case/540-control/zero-codec result. Index `723ccdb0…ce2ea`, results `6c9f9df2…62c59` and completion `06c26897…39249` are retained. Independent actual-control review is running; public FNV/sentinel/state/counter evidence does not expose internal copied buffers or prove independent heap reads. The original v1 failure and earlier control0 proof remain unchanged. Old source, authority, source PASS and failed files stay fixed.

The crypto exporter supports an explicit subset of labels. A [normal-only export authority](tests/node-compat/foundation-crypto/native-v2-normal-off-pin-export-v1-root-authority.json), SHA `13993e6f…b1cb4`, runs the actual staged exporter Root10542/PID89088 raw0 in3.313s, preserving [unreviewed candidate DATA](tests/node-compat/foundation-crypto/native-v2-normal-off-pin-candidate-v1.UNREVIEWED.json), SHA `cf05a57c…d56f`. Separate [reviewed normal-only pins](tests/node-compat/foundation-crypto/reviewed-native-v2-validation-bootstrap-pins-v1.json), SHA `e6bdb310…943a9`, and [Root build-input review](tests/node-compat/foundation-crypto/native-v2-validation-bootstrap-root-review-v1.json), SHA `071666bd…b0bb`, change only review state/flag and four native-proof fields; all other pin data stays exact and three variants remain NULL. [Root derivation/bootstrap receipt](tests/node-compat/foundation-crypto/native-v2-validation-bootstrap-root-results-v1.json), SHA `63471df1…9d4d8`, records the real cryptoOwnerBootstrapPreflight plus explicit recheck as Root41620/PID91553 raw0 in12.167s. The complete884,436-byte frame and finite summary preserve actual configured/frozen roots and full355 ownership metadata. Intermediate Python helper objects are not separately retained; their rechecks are code/clean-terminal supported. A post-reader != syntax typo is retained separately and corrected before any reader I/O; no product failure is inferred. [Independent pin/bootstrap review](tests/node-compat/foundation-crypto/independent-native-v2-validation-bootstrap-results-review-v1/results.json), index `c3fb6181…ad2b8`, now passes9,214 inputs, exact candidate/metadata/freeze reconstruction, six normal-pin review-field changes, other variants NULL and complete metadata/pin/11 selected manifests. Its [stable contract](tests/node-compat/foundation-crypto/independent-native-v2-validation-bootstrap-results-review-v1/result-contract.json), SHA `d1a59bf2…da746`, preserves the build-only scope. Internal helper objects, complete inherited environment and process-group-gone probes are not separately retained, so none are claimed. No engine, HMAC/key/crypto, GC, component, guest/host or timing operation runs here. The normal-only ownership component construction source is in preparation, with later ABI/loading/key-operation authorities still NULL.

The first [crypto ownership component construction template](tests/node-compat/foundation-crypto/ownership-component-candidate-v1/README.md), index `eb648e19…b5c30`, seals28 files/5,059 source references with39 pure/14,901 data/13 parse checks and no component/key action. It uses the genuine normal-only bootstrap and authenticated packaging roles, four proposed scalar exports and an explicitly closed future key-export path. Independent source inspection catches a construction caller/options defect before action: parent descriptor lacks adapter, while componentOptions dereferences d.adapter.path instead of using authenticated packaging.adapter. [Independent construction-source HOLD](tests/node-compat/foundation-crypto/independent-ownership-component-source-review-v1/results.json), index `57679053…89fb6`, verifies28/5,059 rows,5,088 unique paths and all4,934 physical packaging-role files/22 links, but withholds the required PASS on exactly CRYPTO-OWNER355-COMPONENT-ADAPTER-M1. The old template is held, with no actual component/native/crypto artifact failure inferred. A thin successor with an actual pure caller/options old-fail/new-pass seam test is being prepared after the control-directory fix; all key/component/loading/ABI/WT/runtime proof slots remain unfulfilled.

The [thin crypto adapter successor](tests/node-compat/foundation-crypto/ownership-component-candidate-v2/README.md), index `b03d1edb…34bc7`, seals20 files/5,097 references, three afterimages/23 exact reversals and15 actual-options caller pure/113 source-data/six parse checks. The genuine worker/options seam reproduces the old TypeError and succeeds with authenticated packaging.adapter, without invoking componentization or keys. New source/Root/output/peer V2 identities stay NULL pending independent correction review; old28-member donor/native/guest/WIT/tool bytes remain fixed. Independent source review is running. A separate source-only new355 HTTP integration/body-adapter audit is also in preparation; no new HTTP component or host pass is claimed.

The crypto b03 adapter correction closes the first pure caller/options defect, but source review finds a second pre-action context defect: its inherited bootstrapEntry descriptor points to the preparation repository. Identical code there derives the live old342 checkout via sibling Python helpers; the actual c3fb bootstrap proof used the configured355 staged executable. No component action is attempted. The next thin successor must keep original source provenance separate from the authenticated configured executable and bind the actual two-context bootstrap proof; native metadata/paths must not be projected or rewritten. The focused new355 HTTP analysis also confirms the inherited handler consumes direct WASI incomingRequest resources, not a Fetch Request.body. Any request-local ordinary-iterable consumer probes and later real wire-body adapter must be labeled separately; no wire-body support is inferred.

The focused [consumers355 HTTP integration source packet](tests/node-compat/foundation-stream-consumers/http-gate-candidate-v1/README.md), index `de518786…2fa10`, seals18 files/25 finite references with78 source/data/five parse checks. It is not a full execution closure or runner:publisher/whole closure/phase/host authorities stay NULL. The plan retains protected29/classic19 bodies and adds two per-request ordinary-iterable text/json fixtures, with exact6 standard0.2.10 interfaces/type-only clock and one-request-per-instance limitations. It explicitly distinguishes direct WASI incomingRequest resources from native Fetch Request.body and records the native cancellation TODO/no-op. No real wire-body adapter, resource-cancel cleanup proof, Blob/File support or new host result follows.
