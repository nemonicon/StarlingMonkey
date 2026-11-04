# Bounded foundations v8 checkpoint

This checkpoint accepts **core m0.8 and strict callback policy v3** with the six
previous optional foundations. It does not establish full Node, Buffer, event,
stream or process compatibility. [results.json](results.json) pins 417 copied
evidence files, 22 complete reports, all 293 native inputs and the exact external
embedding source. Earlier checkpoints and their counterexamples are unchanged.

| Engine | SHA-256 | Bytes |
| --- | --- | --- |
| Ordinary OFF | `e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9` | 9,724,864 |
| Ordinary RuntimeOnly | `59ff97845e1376853067639cf56f4180c93a9cef75c2d2df1f5087552300bc36` | 9,731,917 |
| Release moving-GC test | `69bf0d270ad408353f962d5e2ab7ac3bc0f3804e432540b10ea8098a22133879` | 9,726,413 |

All three have identical 293 source inputs and build recipe; actual CMake,
compiler commands, locked Cargo and complete OpenSSL source/library checks are
retained. Configuration copies are immutable: raw receipts preserve original
build paths, which may later be reconfigured. The selected guest embedding adds
the reviewed post-binding and deployed rejection checkpoints; neither host is
modified. Node is v22.14.0, StarlingMonkey base is
`54b3329b3ce818fd1f244e871e9c259b63667cda`, and remaining toolchain/host pins are
in the [architecture audit](../../../../docs/node-compat/README.md).

Core `allocUnsafe` validates a primitive finite nonnegative raw size at most
16 MiB, truncates accepted fractions, and returns fresh zeroed exact backing
without pooling. This differs from Node's unsafe/slab behavior. Shared refusal
errors capture Error/defineProperty and define four own data fields. The
[installed gate](allocator.json) passes ten differential groups, five policy
groups, traced BufferList allocation excerpts, 240 refusal checks per call,
snapshot/alias/CJS identities and eleven initialization failures. All 91
excluded own Buffer prototype functions and five remaining static functions
remain explicit refusals. The [main Buffer gate](buffer.json) preserves the
381 string/250 byte corpus and zero-import aliases/default/global contract.

[Strict reports](strict-sync.json), [runtime rejection](strict-runtime.json),
[post-binding](strict-late.json) and [finalizer/getter](strict-callback.json)
cover the previously swallowed unsupported calls, thrown undefined/numeric
values, continuation/cleanup/once re-add, late-handled controls, retained
successful calls and fatal/discard behavior. They record 24 components with
zero imports, 24 rejected componentizations, 50 Jco export calls and 24 fresh
Wasmtime invocations. Registration getter timing, function-listener receiver,
explicit reset and complete request teardown remain separate deviations/gates.

The [current-core moving-GC gate](allocator-gc.json) retains new allocations,
shared views, private brands and snapshotted backing relationships across eight
native hex roundtrips per call, three retained Jco calls and fresh Wasmtime.
It uses existing rooted Shrink boundaries in ordinary Release. No new fault,
DEBUG, raw-memory, genuine OOM or exhaustive-GC result is claimed. Prior accepted
kernel failure scopes remain separately scoped; the stopped newer diagnostic
remains unverified.

All six previous module gates pass on this OFF engine: Path, Events,
StringDecoder, Assert/strict, Querystring and Util. Their [replay index](optional-index.json)
records ten zero-import component audits and preserved historical controls.
All 213 admission cases and seventeen CMake/no-clobber guards pass.

The **same** Runtime HTTP component
`a54f17c28e03b35439559ce2e4b32e22f44dff24d44bd57ccd47b2af8fbd6b74`
(60,782,998 bytes including correctness corpora) passes three requests each on
stock Wasmtime42.0.1 and official wash2.11.0. Both stop with SIGINT/code0.
Thirteen computed bare aliases and the bounded corpora run after deployment.
The six exact standard 0.2.10 imports are HTTP types, IO error/poll/streams,
random/random and a **type-only** monotonic-clock dependency. No clock function,
outgoing HTTP, filesystem, DNS, socket, environment, custom service or TLS API
is selected. Counters are [1,1,1] on each host; request isolation/reuse is not
inferred. This corpus artifact is not minimal deployment size or a benchmark.

One core preflight failed before packaging because full receipt metadata put a
`buffer-facade.mjs` filename in the guest policy, triggering the no-inline-facade
guard. The corrected harness sends semantic fields only and retains the full
receipt in host audits; the guard remains. The first Assert replay used a wrong
historical control filename and was corrected without changing native code or
expectations. Failed logs are preserved externally. The initial archive script
also stopped before staging on a host-report field-name mismatch; its corrected
version archives the existing successful host reports without rerunning them.

The roadmap remains active: stream/web m0.9 is prepared but uninstalled, and
classic streams, production async context, compression/crypto and optional
standard capability modules remain required. New matched allocator timing and
memory measurements are separate from this checkpoint.
