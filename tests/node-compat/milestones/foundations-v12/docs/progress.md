# Node compatibility profile progress

Last updated: 2026-11-03. Overall roadmap: **in progress**.

This file tracks completed work, work in progress, and outstanding gates for the
portable StarlingMonkey Node compatibility profile. It is not a claim of complete
Node.js or Buffer support. The detailed [execution ledger](docs/node-compat/execution-status.md),
[API matrix](docs/node-compat/compatibility-matrix.md), and
[dependency-ordered roadmap](docs/node-compat/roadmap.md) contain the underlying
contracts and evidence. No overall completion percentage is assigned: remaining
phases have substantially different sizes and unresolved design decisions.

Current position: **foundations-v11 is accepted**; the newer private scheduler's
fresh link1 ordinary Release and Release-GC diagnostic gates now pass with 32
sealed inputs. Both evidence sets are independently verified.
The user freed storage; the unchanged build guard now passes. Production
reviewed pins and complete production validation remain outstanding.
The production normal-OFF engine is built, frozen and independently verified.
RuntimeOnly and GC-OFF are also independently verified. Actual artifact pins
have passed Root review and the new runner activation has independent review.
The fresh serial eight-stage normal-OFF regression batch passes in full. The
separate allocator GC and focused OFF/RuntimeOnly/GC gates also pass. The getter
counterexample is reconfirmed. The same HTTP component passes both stock hosts
and the combined audit. Independent post-host verification and the v12
checkpoint archive remain before acceptance.
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
| Bounded stream/web bridge | [v9](tests/node-compat/milestones/foundations-v9/README.md) validates native constructors, bounded UTF-8 codecs, iteration, selected DataView/BYOB behavior, controller guards, optional selection and both hosts. The [installed matrix supplement](tests/node-compat/foundation-stream-web/installed-matrix-v9.README.md) distinguishes tested members from mere constructor availability. Classic Node streams remain outstanding. |
| Protected abort listeners and combined regressions | The accepted [v10 checkpoint](tests/node-compat/milestones/foundations-v10/README.md) Events m0.10 adds bounded `addAbortListener`, native protected dispatch and receiver guards. Core remains m0.8; stream/web remains m0.9. This checkpoint contains 3,445 independently byte-verified evidence files, 33 complete reports, 304 native source inputs and four Release engine receipts. |
| v10 focused and full runtime gates | [Focused report](tests/node-compat/foundation-add-abort/production-native-m0.10/README.md) records 29 Node-derived groups, namespace/default/alias/CommonJS behavior, initializer failures, fatal/discard and handled reuse, Events-OFF admission, and valid native byte-kernel GC roundtrips. Full core/allocator, earlier foundations, stream/web and 24 strict-callback component regressions pass. |
| v10 HTTP on both target hosts | [HTTP-v10 evidence](tests/node-compat/foundations/http-v10.md) validates the same component bytes on both hosts, three requests each and clean shutdown. Its six standard 0.2.10 imports cover HTTP types, IO error/poll/streams, random and a type-only monotonic-clock dependency with no callable clock function. No other network/filesystem/process capability is inferred. |
| Latest accepted checkpoint: foundations-v11 | [v11](tests/node-compat/milestones/foundations-v11/README.md) accepts the bounded m0.11 allocation change after all release, GC, focused and both-host HTTP gates. The archive has 1,746 independently byte-verified evidence files, 33 full reports, 304 native inputs and three current Release engines. Events-OFF is a historical v10 control. No Node API or host capability was added. |
| Performance measurements with counterexamples retained | Matched Jco-adapter and private allocation-pair experiments are documented, including slower results, larger artifacts and higher memory observations. Measurements do not establish a universal native-code advantage. See [allocation work](tests/node-compat/foundation-alloc-unsafe/README.md) and the measured limitations below. |

Older accepted checkpoints and failed attempts remain unchanged. Later results
supersede only the explicitly identified claims; they do not erase prior evidence.

## Latest completed milestone: foundations-v11

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

| Current Release engine | SHA-256 |
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

**Current gate:** independent HTTP post-host verification and the v12 checkpoint
archive/acceptance.
The serial eight-stage normal-OFF batch, allocator GC and focused OFF/
RuntimeOnly/GC pass on the reviewed frozen engines. All
three frozen production artifacts are independently verified. Both link1 diagnostic
component corpora have independent verification. The user
freed storage; more than 60 GiB was available at the latest check. The **2 GiB** native start
guard, **800 MiB** stop threshold and one-job policy remain unchanged. Production
acceptance remains v11; diagnostic engines do not supply production admission.

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
verification and the pending v12 archive remain. These passes do not complete
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
| [Private tick scheduler](tests/node-compat/foundation-scheduler/production-adoption-v1/README.md) | Native/recipe/admission applied; diagnostic Release/GC gates pass. All three production artifacts are independently verified. Fresh normal-OFF eight-stage replay and allocator GC pass. | Finish focused/HTTP gates and independent acceptance. Reset safety stays open. No public `process`, timers or AsyncLocalStorage support is supplied. |
| [Production core/allocator activation v5](tests/node-compat/foundation-scheduler/production-regression-candidate-v5/README.md) | Reviewed actual pins, 667-input closure, 55 Root host checks and real read-only OFF/GC admissions. Fresh core, allocator and allocator-GC component gates pass. | Final aggregate acceptance with focused/HTTP gates. V4 and earlier null-pin preparations remain unchanged and retain their historical holds. |
| [Normal OFF strict/Web activation v3](tests/node-compat/foundation-scheduler/production-followon-off-v3/README.md) | Reviewed parent binding, 755 inputs and 32 Root host checks. Installed stream/web and all four strict suites pass fresh on the new normal-OFF engine. | Final aggregate acceptance. Earlier source packets and controls remain unchanged. |
| [Fresh serial OFF replay v3](tests/node-compat/foundation-scheduler/production-release-runner-v3/README.md) | Reviewed parent indices, 1,442 inputs and 49 Root host checks. All eight stages pass with exit0, no reused results and post-run source seals. Independent verification covers 40 zero-import components, including one historical control. | Separate focused/HTTP verification and final aggregate acceptance. |
| [Capability activation v3](tests/node-compat/foundation-scheduler/production-followon-capability-v3/README.md) | Reviewed engine/component pins, sealed final index, unchanged 778-input closure, focused gates and independent verification. Same HTTP bytes pass both stock hosts and the combined audit; six standard imports/type-only clock are retained. | Independent HTTP post-host verification and aggregate checkpoint acceptance. |
| [Classic streams](tests/node-compat/foundation-classic-streams/source-audit-v1/README.md) | Exact Node22 inventory/dependency audit is complete. An unapplied captured factory implementation is being prepared from the finite 24-file graph, with initial host-only differential checks and explicit deferred members. The existing private scheduler callable is identified for native integration. | Finish the source candidate and independent review, then integrate only after scheduler production acceptance. Native/private scheduling, actual guest lifecycles, queue limits and Web bridges need real-component validation. No classic module is installed. |
| [Reset and request ownership](tests/node-compat/foundation-scheduler/reset-design-v1/README.md) | Seven task kinds and concrete ownership/cancellation/resource problems mapped; guarded traced-owner protocol and dependency-ordered ALS/reuse plan written. | Implement and validate transactional registration, safe timer ownership, resource cancellation, bounded jobs/finalizers and request epochs before exercising reset. Mixed real/immediate polling can require a callable clock capability beyond today's type-only HTTP clock import. |
| [Blob/File integration](tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) | Ownership/receiver correction candidate, source receipts, Node oracles and future test harness. | Native integration and guest validation; resolve constructor coercion, MIME/endings, File naming/time, Promise ordering, stream cancellation and lifetime gaps. Buffer Blob/File exports remain explicit refusals. |
| [Native compression](tests/node-compat/foundation-zlib/README.md) | Bounded native zlib template, host vectors and SDK syntax checks. | Resolve web-compression ownership/lifetime gaps or select an independent safe kernel; add real JS bindings, guest malformed-input/resource-limit tests, Node differential and size/performance evidence. No installed `node:zlib` support yet. |

## Outstanding work, in dependency order

1. Complete independent HTTP post-host verification and aggregate acceptance. Three
   production builds/freezes, full fresh eight-stage OFF replay and allocator
   GC pass. New link1 diagnostic Release/GC gates are independently verified;
   production checkpoint acceptance is pending.
   Keep reset/reuse unaccepted until the ownership redesign has safe validation.
2. Implement foundational classic Readable/Writable/Duplex/Transform/PassThrough,
   then stream/promises and stream/consumers. Validate backpressure, cancellation,
   errors, listener cleanup and cross-boundary scheduling in real components.
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
