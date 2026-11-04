# Small-worker process RSS supplement — source proposal

This packet prepares a separate process RSS/startup supplement. It has not run a parent collector, worker, native preflight, WebAssembly compile/instantiate, guest, host or benchmark. The completed [throughput report](../../../../docs/node-compat/classic-stream-measurement-v1/README.md), its 168 workers and original source family remain unchanged. The checked-in authority is null and refuses before historical evidence/artifact imports or output creation.

The old workers authenticated and retained composition/proof data before observing RSS. The new worker never loads composition, replay, HTTP, native-proof reports or source inventories. The full audits run in `parent.mjs` before launching any worker and once after all workers, using the original composed admission, source/native preflight and reviewed authorities. Those parent checks may overlap internally; there is no proof audit in an RSS worker. Parent memory pressure and shared-machine background effects remain uncontrolled.

`worker.mjs` accepts a parent-hashed descriptor of at most 16 KiB and a three-file self/helper manifest of at most 4 KiB. The manifest binds this worker, the pure descriptor validator and the byte-identical [original loadCompiled](../measurement-execution-activated-v2/instantiate.mjs). Before dynamic code, it authenticates those files and the descriptor. It streams SHA-256 over only the exact component, core, Jco glue, declaration and 18-byte ancestor `package.json` critical files. It neither reads the native engine nor imports a measurement/admission/consumed-seal entry. Its descriptor carries native engine/metadata hashes as provenance data, explicitly separate from native proof access.

The four artifact tuples come from the already issued phase `a822a7b…6890`: native/canonical ON and canonical OFF under `/tmp/starling-node-compat/production-common-byte-correctness-v2`, and stock ON under `/tmp/starling-node-compat/production-common-byte-stock-only-v1`. Parent-only native authority remains the genuine diagnostic pair under `/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze`, with canonical source `/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source`. No production pin, diagnostic metadata or artifact is projected or rewritten.

The finite schedule is 18 fresh processes: each existing comparison has two arms, with three pairs ordered AB, BA, AB. The comparisons remain separate:

| Comparison | A | B |
| --- | --- | --- |
| Same engine, binding strategy | native-on | canonical-on |
| Same canonical bundle, whole profile | canonical-on | canonical-off |
| Different provider/scheduler | canonical-on | stock-on |

Each worker creates exactly one instance and calls public `identity`, `checkpointProbe`, `setup(1)`, `batch(1,1)`, `setup(5)`, `batch(5,1)` and a final probe. The small and large public pipelines consume 8,192 and 4,194,304 bytes respectively. Setup and batch expected values derive from the unchanged Node common-byte oracles and original `compactExpected` helper in the parent. Whole raw scalar strings are durably saved before exact JSON comparisons, so checksums, units and callback results remain independently readable. There are no warmups, throughput samples, pilots, changes to workload/provider/scheduler, or private queue counters.

RSS snapshots retain bootstrap, pre-critical-hash, post-critical-hash, post compile-and-binding-load, post instantiate, post identity/probe, each setup and small/large batch, and final hash stages. `process.memoryUsage().rss` is recorded in bytes; `resourceUsage().maxRSS` retains its public API kilobyte unit, both before final validation hashing and at terminal observation. The original `loadCompiled` combines core compilation and binding import, so the stage is named **compile-and-binding-load**, not isolated compile. Public stage wall times and whole-worker elapsed time are operational context, not throughput or physical cold-start estimates.

The large case follows the small case on the same instance. Compiler cache, earlier allocations and allocator retention therefore affect it. AB/BA/AB has a 2:1 first-arm imbalance; n=3 remains small. Process RSS includes Node/V8, small validation buffers, streaming I/O and allocator retention. It is not guest heap, linear-memory capacity, unique physical pages, memory-growth count, engine reset, isolated GC or request-reuse proof. No forced GC, allocator trim, private export, raw guest memory or heap capture is used.

Future execution requires a separately issued Root authority with state `ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V1`, this final index SHA, `memorySupplementAllowed:true`, `throughputReplacement:false`, `runtimeAcceptanceClaim:false`, and explicit absolute path/SHA pairs for the exact phase, prior timing report, Root timing receipt and independent integrity index. Their required hashes are in `contracts.mjs`; caller-supplied SHA is checked before parsing the authority. The existing phase's timing permission does not authorize this supplement. Root must review the new source and issue the new authority before any action.

```sh
# Future action only; not executed during source preparation.
NODE_COMPAT_MEMORY_PROBE_APPROVED=1 /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  /ABSOLUTE/PACKET/parent.mjs NEW_SOURCE_INDEX_SHA \
  /ABSOLUTE/ROOT_AUTHORITY.json ROOT_AUTHORITY_SHA \
  /tmp/starling-node-compat/FRESH_OUTPUT
```

The parent requires at least 2 GiB free before output creation and 800 MiB before each launch. It uses the original owned-process collector, streams raw stdout/stderr to exclusive files, allows a fixed 600-second worker deadline, records partial progress and requires terminal exit zero plus owned-group cleanup. A deadline is an operational bound, not an adequacy claim for every host. No resume or prior observation reuse is implemented. Result publication follows all 18 successful workers and the final parent audit; completion hashes all actual output files and requires a separately retained real parent exit-zero record. A crash/storage failure may leave partial files and cannot publish a successful completion.

`tests.mjs` imports only the pure validator and reads source text. Its synthetic shape tokens are not engine/source authorities. It rejects full-measure entry substitution, foreign/oversized/extra payloads, unknown artifact roots, metadata/critical-file mutation, reversed case order, N16, proof-report/engine-path smuggling, null/unreviewed authority and wrong phase/report authority. Source checks cover the worker import boundary, authentication order, raw-before-assert order and the finite 18-worker schedule. These tests do not establish runtime success or memory savings.
