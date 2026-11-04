# Roadmap execution status

Goal: complete the [dependency-ordered roadmap](roadmap.md), documenting code,
decisions, executed evidence and remaining gates. The goal is active. The
initial Buffer/stub milestone does not complete that roadmap.
The repository [continuing tracker](../../progress.md) records handoff state.

Status terms: **verified** means the linked evidence covers the stated bounded
requirement; **partial** means required work remains; **in progress** identifies
current work; **pending** means implementation or adequate evidence is absent.
Historical engine/component hashes remain evidence for those exact artifacts,
not automatic validation of a changed worktree.

The latest accepted [v10 checkpoint](../../tests/node-compat/milestones/foundations-v10/results.json)
preserves 304 native inputs, four engines and 33 primary reports. Its bounded
Events m0.10 extension passes 29 groups in both entropy modes and a separate
combined-owner Release GC gate. Fresh callback-return `.then` getter parity is
**false**: Node `1/1/0` versus native `0/0/0`; the target's nonregistry
`Symbol.dispose` also differs from Node. HTTP passes the same bytes on both
hosts with six standard 0.2.10 interfaces, type-only clock and counters `[1,1,1]`,
without proving reuse/isolation.

Current worktree m0.11 source is
[applied](../../tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
after source/host checks, but fresh native/runtime/GC/two-host gates remain
pending. The frozen proposal's UNAPPLIED wording remains historical; latest
acceptance is v10. Private timings suggest possible CPU gains only, with higher
RSS in 29/30 comparisons, higher capacity in 4/30 and an 8,513-byte larger minimal
snapshot; they do not establish this rebased source's performance.

## Completion gates

| ID | Requirement | State | Evidence or remaining work |
| --- | --- | --- | --- |
| 0.1 | Exact engine, Node, packaging tools, WIT, SDK, libraries and host pins | verified, bounded | [Toolchain audit](toolchain-findings.md), existing build sidecars and [flag audit](../../tests/node-compat/optimization/build-flags-audit.json); import-I32, scalar-export and signed-BigInt fixes have locked, byte-pinned packaging/native proofs; [entropy-v1 engines](../../tests/node-compat/milestones/entropy-v1/README.md) have actual CMake/entry/OpenSSL/library receipts and real component regressions; v2 adds complete dependency-source checks before/after compilation |
| 0.2 | Existing StarlingMonkey E2E and ComponentizeJS pure/global/snapshot/error tests against custom engine | partial | [Selected upstream gate](../../tests/node-compat/upstream/README.md): 19 adapted E2E, all15 builtin fixtures across explicit policy modes, two ownership and nine initializer cases pass. [Entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md) closes the old crypto trap: same upstream233-subtest component passes both hosts. Full untouched suites are not claimed |
| 0.3 | Explicit world/import validation and target host instantiation | verified, bounded | [Accepted v10](../../tests/node-compat/milestones/foundations-v10/results.json): pure OFF components and one exact six-interface 0.2.10 HTTP component on Wasmtime 42.0.1 and official wash 2.11.0. Clock is type-only, random explicit, counters restart at 1; no reuse/isolation claim. Changed engines require fresh gates |
| 1.1 | Versioned finite manifests with schema and inventory validation | verified, bounded | Eight selected manifests cover fourteen canonical namespaces. [Schema](manifest-validation.md), [328 admission checks](../../tests/node-compat/milestones/foundations-v10/reports/selection.json) and corrected 19 configure guards preserve finite bindings, flags, aliases and fail-closed selection. New extensions need fresh release gates |
| 1.2 | Real ESM bindings, aliases, default identities, selected CommonJS lowering, canonical global Buffer | verified, bounded | [Bundler](../../tests/node-compat/profile-bundler.mjs), integration and raw alias/cache tests; runtime CommonJS loader and mutable export synchronization excluded |
| 1.3 | Unsupported call/new behavior during initialization and execution, strict rejection boundary | verified, bounded | [Accepted v10](../../tests/node-compat/milestones/foundations-v10/results.json) replays 24 strict component audits; focused m0.10 adds 8 rejected initializers and 5 fatal/discard cases per entropy mode/host. Handled controls remain reusable. Callback-return getter parity is explicitly false; Symbol identity, full reset/teardown and broader async-listener semantics remain bounded |
| 2.1 | Bounded Buffer semantics and compiled native ownership/GC review | verified, bounded | [Developer contract](../src/developer/node-compat.md), release and compacting-GC tests; cross-realm and unavailable shared-input construction remain unverified |
| 2.2 | Allocation failure, limits, surviving state and recovery | verified, bounded | [Accepted allocator gate](../../tests/node-compat/milestones/allocation-r2/oom/results.json): four genuine native API failure scopes, 32 recovery pairs and moving-GC checks per call; three retained Jco calls and fresh Wasmtime pass. Scalar-only DEBUG world; general indirect DEBUG ABI and engine-wide exhaustive OOM excluded |
| 2.3 | Matched component size/startup/memory/throughput evidence | partial | Earlier corrected-clock/Weval byte-codec measurements retain their exact engines. New [v8 allocator comparison](../../tests/node-compat/foundation-alloc-unsafe/matched/measurement-v1/README.md) uses the actual portable Jco adapter and same engine:15scenarios/60fresh workers/twoorders, public RSS/capacity/startup observations. Initial allocUnsafe is slower in bothorders/all3sizes; memory counterexamples and n=2/correlated/shared-desktop limits are explicit. Minimal optional variants and further optimization decisions remain |
| 2.4 | Remaining UTF-8 allocation and Weval decision | partial | Corrected-clock64-byte UTF8 encode requests35.06MiB native versus9.06MiB JS, despite lower large-input memory. Private exact GC-owned U8 candidate passes77,769 codec checks and moving-GC variants; oldcontrol exposes missing Symbol TypeError. [Same-project ordinary Release pair](../../tests/node-compat/utf8-direct/README.md) now passes:64-byte RSS51.64→24.58MiB,+8.8%throughput;512KiB1.66x/sameRSS. Ordinary production change passes v5 codec/Buffer gates; newscalar OOM gate failed and furtherdiagnostics were automaticallyblocked; Weval v5 engine/cache and 58-check typed ABI/snapshot/strict-init smoke pass; [matched two-order Weval timing](../../tests/node-compat/weval-experiment/v5/RESULTS.md) passes240fresh instances/1,680batches; native byte codecs improve throughput, copying constructor and several memory cases remain counterexamples; full Weval release gates and new OOM remain unverified |
| 3.1 | EventEmitter, string_decoder, assert, path, querystring and bounded util | partial | [Accepted v10](../../tests/node-compat/milestones/foundations-v10/results.json) replays the six earlier modules and adds bounded addAbortListener with 29 groups in both entropy modes, combined-owner GC and optional-OFF denials. Node `1/1/0` versus native `0/0/0` getter reads and Symbol.dispose registry gap remain; once/on/AsyncResource and broader Events behavior stay deferred |
| 3.2 | Native stream/web bridge with constructor/BYOB/encoding parity | verified, bounded | [Accepted v10](../../tests/node-compat/milestones/foundations-v10/results.json) replays installed m0.9 classes/codecs/iteration/DataView/aliases/CJS/snapshot and 7 initializer failures, plus prior modules/strict and both-host HTTP. The [v9](../../tests/node-compat/milestones/foundations-v9/README.md) direct native OFF/controller and module-denial proofs remain separate. UTF8/fixed-unshared/min1, signal/proxy/code/arity/lifecycle limits persist |
| 3.3 | Classic Readable/Writable/Duplex/Transform/PassThrough, promises and consumers | in progress | [Dependency audit](../../tests/node-compat/foundation-stream/README.md): bounded allocUnsafe/addAbortListener are now accepted dependencies, with remaining callback/scheduler gaps. Existing text/json component proof remains isolated; [Blob/File integration packet](../../tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) is source-only/unlinked. Classic backpressure/lifecycle/cancellation and Blob-dependent consumers remain required |
| 3.4 | Scheduler, request lifecycle and native AsyncLocalStorage propagation | in progress | [Async-context probes](../../tests/node-compat/async-context/README.md) establish bounded store mechanics, not production ALS. The [private tick packet](../../tests/node-compat/foundation-scheduler/README.md) has Node ordering oracles and uncompiled integration design only. Actual native completion/cancellation, resource ownership, request teardown/reuse and complete propagation remain open |
| 4.1 | Native gzip/deflate/deflateRaw and Node facade | in progress | [Source audit and isolated native template](../../tests/node-compat/foundation-zlib/README.md): current streaming input borrow, cleanup and inflate-error gaps block reuse. Bounded owned-byte one-shot algorithm passes 86 host tests, including incompressible output and the full output cap, plus actual SDK30/SM147 syntax. It is unlinked, has no JS/WIT binding and proves no component support. Options, Node error mapping, streaming and size/throughput gates remain |
| 4.2 | Brotli inclusion decision | pending | Empirical size/throughput/API demand decision, rather than implicit full zlib support |
| 4.3 | Matching native crypto, Node key/Hash/Hmac semantics | pending | Algorithm inventory, known answers, malformed inputs, ownership/zeroization and component tests required |
| 4.4 | RNG and entropy resumption policy | verified, bounded | [Entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md): OFF/runtime-only private entry barrier, P2/OpenSSL bridge, seven snapshot denials and eight owned-input Node cases per mode, repeated/fresh scalar instances; minimal HTTP and original233-subtest suite on both stock hosts. v2 scalar gate rerun passes; no Node crypto export support added |
| 5.1 | Optional filesystem variant | pending | Explicit preopens/rights, bounded descriptors/read/write/stat, confinement/denial/close tests on both hosts |
| 5.2 | Optional Node HTTP/HTTPS variant | pending | Existing HTTP test transport is not node:http; streaming/trailers/cancellation and rejected unsupported socket/TLS options required |
| 5.3 | Optional TCP/UDP/IP-lookup variants | pending | Standard P2 resources, policy-denied behavior, family/partial-write/datagram/teardown tests; no TLS inference |
| 5.4 | Optional CLI/environment/stdio/exit, clocks and entropy variants | pending | Initialization versus execution policy, no fabricated OS process facts, exact per-variant imports and host grants |
| 5.5 | Capability/lifecycle portability gate | partial | Pure/HTTP local-host checks exist; optional variants, denial paths, request teardown/reuse and production lifecycle evidence remain |
| 6.1 | Trace-based expansion with versioned manifests and release gates | pending | Record demand from actual applications/dependencies; every extension needs Node differential, component and size/performance evidence; no blanket Node compatibility claim |

## Work sequence

1. Preserve the accepted [allocation-r2](../../tests/node-compat/milestones/allocation-r2/README.md),
   [entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md) and
   [foundation checkpoints through v10](../../tests/node-compat/milestones/foundations-v10/README.md).
   Later source changes require their own receipts and regressions.
2. Preserve accepted stream/web m0.9 and Events m0.10 bounded gates and their
   explicit callback/Symbol differences. Validate the newly applied m0.11 source
   with fresh native, strict, GC and both-host gates before promotion; continue
   scheduler/Blob dependencies for classic streams.
3. Retain [corrected-clock](../../tests/node-compat/bench-clock-v2/RESULTS.md),
   [matched UTF8 allocation](../../tests/node-compat/utf8-direct/README.md) and
   [Weval](../../tests/node-compat/weval-experiment/v5/RESULTS.md) measurements
   with their exact engines. Keep Weval experimental until its broader release
   gates pass, and measure minimal deployment variants separately. The stopped
   new OOM branch remains unverified.
4. Complete scheduler/lifecycle and production ALS resource ownership, including
   actual native completions, cancellation and request teardown/reuse. Isolated
   store-propagation evidence is not a complete ALS implementation.
5. Continue native compression/crypto and independently selected capability
   variants, keeping every gate explicit until proved.

## Accepted production integration v6

Accepted v6 selects StringDecoder (m0.4), Assert/strict (m0.5) and
Querystring (m0.6) through independent default-OFF CMake flags, finite manifests
and generated headers. Registration uses the existing private factory evaluator
and `Engine::define_builtin_module`; it introduces no host service. The common
evaluator now uses pinned SpiderMonkey 147 `CompileOptions::setForceStrictMode()`
to retain canonical ESM receiver semantics after syntax removal. In particular,
plain `StringDecoder()` must throw without modifying the global object.

The reviewed TextDecoder ownership change is applied to ordinary production
source; its exact cleaned source hash is
`4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c`.
This differs from the tested private candidate by replacing the empty-input
integer sentinel with addressable local byte storage and comment cleanup.
Both OFF and RuntimeOnly production engines compile with 285 identical captured
source inputs and identical build recipe; OFF ordinary API regressions pass. Shared input
rejection, fatal-decoding lifecycle limitations and Rust infallible allocation
remain explicit; no new allocation-failure result is claimed.

The build recipe now refuses existing engine/receipt paths before source
preparation, and checks actual registration compile commands against all five
optional feature flags. All six generated headers pass source regeneration
checks. The expanded [selection tests](../../tests/node-compat/milestones/foundations-v6/selection.json)
pass 153 cases, including all 32 independent feature combinations and rejected
flag/manifest/adapter mismatches. The [CMake/recipe guard test](../../tests/node-compat/milestones/foundations-v6/cmake-policy.json)
passes 15 configure/sentinel cases; unrelated targets are mocked and this is no
compilation claim. The fresh all-enabled OFF engine is
`33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516`
(9,700,373 bytes); RuntimeOnly is
`d2df3d27e9fed343f457dd6bfda381ffe2dd9a0ac8f83a59aa09afcad9a7a87c`
(9,707,433 bytes). Actual registration flags, complete dependency source checks
and both engine receipts pass. New module gates and Buffer/Path/Events
regressions pass on OFF. The same corpus-heavy Runtime HTTP component passes
three requests each on stock Wasmtime 42.0.1 and official wasmCloud 2.11.0, with
ten first-deployed aliases and unchanged six standard 0.2.10 imports. Both hosts
stop with code 0; counters remain [1,1,1], without an HTTP reuse/isolation claim.
The immutable [v6 checkpoint](../../tests/node-compat/milestones/foundations-v6/README.md)
contains 331 byte-checked files, 16 complete reports and all 285 native inputs.

## Util and core v8 integration

The v7 candidate added `NODE_COMPAT_UTIL`, default OFF, with the
`sm-node-22.14.0-m0.7` manifest. It selects `node:util`, `node:util/types` and
`node:sys`, plus their bare aliases, through the existing strict factory and
module-registration API. The sys namespace is separate while exported values
share util's default graph. No process warning or host capability is added.

Its source/factory gate passes 2,523 shared Node checks and 108 deferred-call/
construction checks per variant. The isolated prototype passes 2,436 shared
checks on two retained Jco calls and a fresh Wasmtime instance, with zero imports.
Twenty-nine predicates call captured native ECMAScript intrinsics; inherits,
promisify and toUSVString have bounded JS semantics, and native web codec
constructors retain their identities and existing deviations. Other APIs remain
explicit stubs. Proposed additional C++ type helpers remain uncompiled.

The expanded admission gate passes 213 checks, including all 64 independent
feature combinations; CMake/recipe guards pass 17 cases. Both v7 engines compile
from 293 identical inputs with actual registration flags and complete build
receipts. Installed util and all prior module regression gates now pass. The same Runtime
HTTP component passes three requests on each stock host, with thirteen deployed
aliases and unchanged six standard interfaces. The [v7 bounded archive](../../tests/node-compat/milestones/foundations-v7/results.json)
retains 359 copied files and 21 complete reports. Additional ordinary listener
controls then exposed the strict-initialization counterexamples above. Broader
profile promotion is withheld; a separately built guest checkpoint fix is next.
Earlier bounded v6/v7 reports do not prove this newly tested requirement.

The separately tested [zeroed allocUnsafe candidate](../../tests/node-compat/foundation-alloc-unsafe/README.md)
passes ten Node differential groups and five profile groups plus the traced
BufferList allocation paths in real zero-import components. It is an isolated
static-field simulation, fully restored between calls. Its evidence remains
distinct from the subsequent installed implementation.

Root has now [applied the reviewed m0.8 v2 core and harness](../../tests/node-compat/foundation-alloc-unsafe/production-v8/source-adoption.json).
The four source changes add only bounded zeroed allocUnsafe and harden shared
refusal errors with captured Error/defineProperty and own data fields. Native
buffer.cpp and all91 excluded prototype functions remain unchanged. Actual ESM
and strict generated factories each pass ten allocation groups, five policy
groups and240 pure-JS refusal poison checks. The receipt-selected test harness
passes46 cases/39rejections, all seven generators and213 admission checks pass.
Both ordinary v8 engines now build from the same293 native inputs and recipe.
The [installed allocator/helper gate](../../tests/node-compat/foundation-alloc-unsafe/installed/README.md)
passes on retained Jco and fresh Wasmtime with zero imports, eleven initialization
failures and immutable v7 refusal controls. A same-source Release GC test engine
passes three retained calls and fresh Wasmtime with new allocation/view/brand
and snapshot state around eight native hex roundtrips. All prior modules and
the shared HTTP fixture pass; the [immutable v8 checkpoint](../../tests/node-compat/milestones/foundations-v8/README.md)
contains417 copied evidence files and22 complete reports. No new genuine
allocation-failure or performance result is claimed.

## Strict callback correction v3

Private v1 retains the first uncaught synchronous event value in a persistent
root and checks actual job/finalizer/initialization boundaries. A separate
ComponentizeJS checkpoint is required after export-object binding getters run.
Its ordinary Release moving-GC gate retains a thrown object across eight native
byte-kernel collections. That proof remains tied to v1, not later engines.

Private v2 additionally checks the actual unhandled-Promise set after deployed
jobs and finalizers drain, before result marshalling. Five fatal cases fail on
Jco and fresh Wasmtime; four caught or later-handled controls survive three
retained calls and fresh execution. Six late-binding controls and the sixteen
initialization controls pass. All components have zero imports. Import-free
fatal exports expose a trap; the source-defined rejection marker is not an
observable error-property channel without selected standard diagnostics.

Three subsequent callback controls preserve v2's remaining counterexamples.
A direct finalizer actually calls unsupported spawn yet componentizes; an
armed handleEvent getter throws to the dispatch caller and skips the next
listener. Registration-time getter evaluation also differs from Node. The v3
proposal captures direct finalizer/getter failures and restores dispatch
cleanup; registration timing remains an explicit separate deviation. A
source-only invalidated-iterator finding in once-listener re-add was corrected
before any such path was exercised on a new engine. No old invalid path or
stopped fault diagnostic is executed.

Private v3 engine
`8594fe89fb7048cca5feed57fe073d4040a5f0636fabddb6721df463202c905a`
now passes the repeated synchronous/runtime/late-binding gates, eight new
initializer rejections and five new controls on retained Jco and fresh Wasmtime
with zero imports. Root applied the exact four reviewed native files and
checked their hashes against the private source receipt. The independently
reviewed [production recipe is also applied](../../tests/node-compat/foundation-add-abort/production-candidate-v3/production-recipe-adoption.json),
with a separate artifact namespace, exact fourth embedding patch and actual
strict-macro checks in all relevant translation units. All seventeen CMake and
no-clobber guards pass. Fresh production v8 then passes all four bounded strict
suites; its [separate production receipt](../../tests/node-compat/foundation-add-abort/production-v8-evidence-receipt.json)
retains exact source/configuration/runner hashes. Private v3 also passes its own
ordinary moving-GC gate; current-core m0.8 has a separate GC supplement. These
new proofs do not retroactively validate v7. Registration-time getter behavior,
function-listener receiver, full reset and request teardown remain separate.

## Evidence corrections

The documentation supplement previously treated Node API JSON's placeholder
property labels `Type` and `return` as member names, and treated four
documentation chapters as builtin module IDs. The corrected
[inventory regression](inventory-correction-results.json) preserves all 4,132
runtime reflection/CommonJS records and the exact 72 module namespaces, corrects
137 `Type` and five `return` addresses, and records 55 non-module chapter entries
as exclusions. The matrix now has 6,795 evidence rows; duplicate documentation
and reflection records are not distinct implemented APIs. This correction adds
no runtime support. The matrix's historical proposed dispositions remain
separate from current implementation evidence and the gates above.
