# Node compatibility profile progress

Last updated: 2026-11-03. Overall roadmap: **in progress**.

This file tracks completed work, work in progress, and outstanding gates for the
portable StarlingMonkey Node compatibility profile. It is not a claim of complete
Node.js or Buffer support. The detailed [execution ledger](docs/node-compat/execution-status.md),
[API matrix](docs/node-compat/compatibility-matrix.md), and
[dependency-ordered roadmap](docs/node-compat/roadmap.md) contain the underlying
contracts and evidence. No overall completion percentage is assigned: remaining
phases have substantially different sizes and unresolved design decisions.

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
| Protected abort listeners and combined regressions | **Latest accepted checkpoint: [foundations-v10](tests/node-compat/milestones/foundations-v10/README.md).** Events m0.10 adds bounded `addAbortListener`, native protected dispatch and receiver guards. Core remains m0.8; stream/web remains m0.9. This checkpoint contains 3,445 independently byte-verified evidence files, 33 complete reports, 304 native source inputs and four Release engine receipts. |
| v10 focused and full runtime gates | [Focused report](tests/node-compat/foundation-add-abort/production-native-m0.10/README.md) records 29 Node-derived groups, namespace/default/alias/CommonJS behavior, initializer failures, fatal/discard and handled reuse, Events-OFF admission, and valid native byte-kernel GC roundtrips. Full core/allocator, earlier foundations, stream/web and 24 strict-callback component regressions pass. |
| v10 HTTP on both target hosts | [HTTP-v10 evidence](tests/node-compat/foundations/http-v10.md) validates the same component bytes on both hosts, three requests each and clean shutdown. Its six standard 0.2.10 imports cover HTTP types, IO error/poll/streams, random and a type-only monotonic-clock dependency with no callable clock function. No other network/filesystem/process capability is inferred. |
| Performance measurements with counterexamples retained | Matched Jco-adapter and private allocation-pair experiments are documented, including slower results, larger artifacts and higher memory observations. Measurements do not establish a universal native-code advantage. See [allocation work](tests/node-compat/foundation-alloc-unsafe/README.md) and the current proposal below. |

Older accepted checkpoints and failed attempts remain unchanged. Later results
supersede only the explicitly identified claims; they do not erase prior evidence.

## Current work in progress

### m0.11 allocation change: runtime gates passed, archive pending

The [second integration packet](tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11-v2/README.md)
has now been **applied coherently to the worktree**. Its 11-file patch preserves the complete
verified HTTP-v10 corpus and changes four native profile source inputs. It
replaces a secondary allocation-facade call with a captured Uint8Array
allocation, retaining the declared primary validation, zeroed independent
storage, no-pool policy and 16 MiB limit. It adds no C++ allocator kernel,
ownership transfer, host import or newly supported Buffer API.

Completed: two source reviews, all 2,404 packet-file hashes, all 11 live
before/after hashes, 304 native input checks, coherent application, eight
generator checks and 328 module-admission checks. The
[source adoption receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
records four changed native inputs and 300 unchanged inputs, including the
unchanged protected-listener and build mechanisms. Host semantic/bundler checks
and a private same-project paired experiment preceded adoption. Post-application
[schema and bundler checks](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-admission-results.json)
also pass, including 19 malformed-manifest rejections. The runtime gates
described below now pass; checkpoint archival remains pending. Private
experimental timings do not establish performance of the rebased production
implementation.

The fresh ordinary entropy-OFF engine is built and frozen as
`1eb2b55a391e2bc83478fefee124a6f282cfed148cc0623754125f6c5e9b0458`.
Its exact receipt, all 304 source inputs, configuration and compile-command
digests pass the new production preflight. RuntimeOnly is also built and frozen
as `2e3731ce248be1d8ede0f5672dd87b48fb1731dfddb045bfaabaeea02534a36d`.
Release GC is also built and frozen as
`b79fd7dba35288e233ec07134e490ddd2ae51f212a2be506ecd70a728f5e6bc4`.
The [three-build receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/native-build-results.json)
records actual configurations, source/embedding inputs and dependency evidence.
The production core component gate passes. The first allocator run stopped
because its new host test runner omitted a `pathToFileURL` import; the
[failed harness attempt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/harness-history/attempt1)
is preserved, and the fix changes only that import. A
[fresh retry](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/release-retry-preparation.json)
reused only the independently byte-verified successful core result. Checkpoint
acceptance still awaits final evidence verification and archival.

The retry has passed allocator, stream/web, all six earlier foundations and
strict synchronous callback gates. The focused entropy-OFF protected-listener
replay also passes. A later strict-runtime packaging attempt exhausted local disk
space (`No space left on device`); that attempt was incomplete and established
no native semantic result. Further job launches were held while completed
artifacts received byte- and metadata-verified filesystem compression. The
failed attempt remains preserved; the gate subsequently passed in a fresh
directory. Successful immutable results were reused only after verification.
Storage has since recovered to approximately 1.9 GiB free; this increase was
already present before the small duplicate-artifact recovery operation and its
cause is not established. The [storage receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/cow-bootstrap-results.json)
records three new raw engine copies restored at their original paths with
identical bytes and required metadata, while frozen engines remained intact.
Completed-output compression now independently verifies all 64 files, retaining
858,484,404 logical bytes and recovering 534,081,536 physical bytes. Free space
after verification was approximately 2.38 GiB. The
[eight-job release batch](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/release-gate-results.json)
now **passes**: core, allocator, stream/web, six earlier foundations, and four
strict callback groups. Five successful jobs were reused after rehashing their
reports, runners, logs and recorded artifacts; strict-runtime, late binding and
callback cleanup passed fresh retries. The
[allocator GC gate](tests/node-compat/foundation-alloc-unsafe/installed/gc-v11-results.json)
also passes: three retained Jco calls and fresh Wasmtime preserve zeroed owned
backing, shared views, brands and snapshot state across eight valid native hex
roundtrips per call; emitted imports are empty. The
[focused replay receipt](tests/node-compat/foundation-add-abort/production-native-m0.11/evidence-receipt.json)
now covers all four completed reports and 19 application components. OFF and
RuntimeOnly pass 29 groups each; RuntimeOnly imports only
`wasi:random/random@0.2.10`. The protected-owner GC gate passes, with its
combined-owner limitation retained. A fresh returned-object observation again
records Node `1/1/0` versus native `0/0/0`; parity remains false. HTTP-v11 now
passes three requests on each stock host with the same component
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`,
63,635,975 bytes including test corpora. Both hosts stop with code 0 and counters
`[1,1,1]`; this does not prove instance reuse or request isolation. Imports remain
the same six selected standard WASI 0.2.10 interfaces, with a type-only clock.
Final source/evidence verification and checkpoint archival remain outstanding;
latest accepted status remains v10 until those finish.
No storage observation is a guest memory or performance result.

The private experiment found faster allocation batches in its measured pairs,
but candidate peak RSS was higher in **29/30** comparisons, observed capacity
was higher in **4/30**, and the minimal snapshot was **8,513 bytes larger**.
Seven slower controls, five control reversals and only two independent processes
per arm limit interpretation. No memory, size, general application, Wasmtime
throughput or isolated native-fill win is claimed.

### Source-only preparation for subsequent phases

| Packet | Completed preparation | Still required |
| --- | --- | --- |
| [Private tick scheduler](tests/node-compat/foundation-scheduler/README.md) | Actual engine, job queue, native task, initialization, export and reset boundaries mapped; pinned Node ordering oracles; [TaskQueue-owned integration packet](tests/node-compat/foundation-scheduler/taskqueue-owner-v2/README.md) adds a concrete unapplied diff, finite diagnostic access and ownership/reset audit. [Five actual-SDK syntax checks](tests/node-compat/foundation-scheduler/taskqueue-owner-v2-syntax-v1/results.json) pass in an isolated stage with Release flags and `-Werror`; the [separate diagnostic realm guard](tests/node-compat/foundation-scheduler/taskqueue-owner-v3/README.md) also passes its changed-TU syntax check. | No live application, linked engine or guest execution yet. Real-component ordering, reentrancy, exception, allocation and snapshot gates remain; a coherent layered build-policy integration is being prepared. Reset safety stays open. No public `process`, timers or AsyncLocalStorage support is supplied. |
| [Blob/File integration](tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) | Ownership/receiver correction candidate, source receipts, Node oracles and future test harness. | Native integration and guest validation; resolve constructor coercion, MIME/endings, File naming/time, Promise ordering, stream cancellation and lifetime gaps. Buffer Blob/File exports remain explicit refusals. |
| [Native compression](tests/node-compat/foundation-zlib/README.md) | Bounded native zlib template, host vectors and SDK syntax checks. | Resolve web-compression ownership/lifetime gaps or select an independent safe kernel; add real JS bindings, guest malformed-input/resource-limit tests, Node differential and size/performance evidence. No installed `node:zlib` support yet. |

## Outstanding work, in dependency order

1. Finish m0.11 validation and all fresh gates, or retain the accepted m0.8
   allocation implementation if its declared contract cannot be preserved.
   Archive the outcome without transferring private timing claims.
2. Integrate the bounded private tick scheduler at actual native boundaries.
   Preserve initial ESM versus task/export ordering, tracing and strict failure
   policy; prove final snapshot emptiness and reset behavior.
3. Implement foundational classic Readable/Writable/Duplex/Transform/PassThrough,
   then stream/promises and stream/consumers. Validate backpressure, cancellation,
   errors, listener cleanup and cross-boundary scheduling in real components.
4. Resolve Blob/File ownership and semantic gaps before promoting consumer
   byte/blob operations. Verify all affected fetch/FormData/clone callers.
5. Complete a correct AsyncLocalStorage propagation design and implementation:
   capture at actual promise/native-resource creation, restore around execution,
   trace tokens, restore prior context on every exit and release request owners.
   Isolated probes do not establish production propagation across `await`.
6. Integrate measured guest compression and suitable cryptographic primitives.
   Audit algorithm/key semantics, allocation bounds, entropy selection, lifetime
   and final component size. Reuse native web code only where semantics and
   ownership match.
7. Define independent optional filesystem, HTTP, DNS/socket and CLI profiles
   with per-export contracts, exact standard import allowlists and capability
   denial tests. Validate identical artifacts on both hosts. WASI P2 sockets
   provide **no TLS**; TLS requires a separately selected guest stack, trust and
   time policy. Process creation, IPC, V8/Inspector and Node worker behavior
   remain unavailable with the selected capabilities.
8. Close lifecycle and reuse gates: environment/clock/entropy snapshot policies,
   final post-binding initialization, live-handle restrictions, cancellation,
   component reuse and request-associated state. Run broader upstream coverage
   and final size/startup/memory/throughput comparisons for released variants.
   The [native body-task cancellation implementations](host-apis/wasi-0.2.0/host_api.cpp)
   explicitly lack a supported cancellation contract for `BodyWriteAllTask` and
   `BodyAppendTask`. Reset cancellation ownership and future callback reentrancy
   therefore remain open; an idle tick-queue check alone does not close them.
9. Expand APIs only with explicit manifest changes, Node differential tests,
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
