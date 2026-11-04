# Accepted bounded foundations v6

This immutable checkpoint installs optional StringDecoder(m0.4), Assert/strict
(m0.5) and Querystring(m0.6) alongside the existing bounded Buffer/stub, Path and
Events modules. It does not establish complete Node or Buffer compatibility.
[results.json](results.json) indexes331 byte-checked evidence files, including
16 complete reports and all285 compiled source inputs under [source](source/).
The [acceptance script](accept-v6.py) archives already executed results; it does
not run or replace the semantic tests. A separate [license supplement](license-supplement.json)
retains the accompanying project/Node/vendor license files without changing the
compiled-input receipt.

The base revision remains `54b3329b3ce818fd1f244e871e9c259b63667cda`, with Node
22.14.0, ComponentizeJS0.23.0 plus the recorded guest ABI/entry fixes, Jco1.40.0,
SpiderMonkey147 and exact selected WASI0.2.10 interfaces. Both engines have the
same285 input hashes and build recipe. Their actual registration compile
commands prove all five optional flags are ON, alongside complete OpenSSL and
locked Rust receipts:

| Engine | SHA256 | Bytes |
| --- | --- | ---: |
| [OFF](engine-off.json) | `33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516` | 9,700,373 |
| [RuntimeOnly](engine-runtime.json) | `d2df3d27e9fed343f457dd6bfda381ffe2dd9a0ac8f83a59aa09afcad9a7a87c` | 9,707,433 |

Production TextDecoder reads dictionary options before borrowing input, obtains
fresh native lengths/data after observable getters and output allocation,
scopes the synchronous Rust input borrow, and creates the result string after
that borrow ends. Its cleaned source hash is
`4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c`.
Empty slices use addressable local storage. Shared views remain rejected; fatal
decoder lifecycle and Rust infallible allocation remain unresolved. The factory
evaluator uses actual `CompileOptions::setForceStrictMode()` to preserve ESM
receiver semantics, including rejected plain StringDecoder calls without global
pollution.

OFF component gates pass with zero final imports:

- [StringDecoder](string-decoder.json):2,982 sequences/8,886 writes per call,
  40generic native codec cases(38 exact Node observations plus two explicitly
  preserved ordering deviations), three retained Jco calls and fresh Wasmtime;
  snapshot carry, intrinsic capture, detached owned state, ESM/CJS/default
  identities, two raw aliases/cache and three initialization failures.
- [Assert](assert.json):55 groups/784 primitive comparisons and22 profile cases
  per call, retained Jco[1,2] and fresh Wasmtime1;22exports per namespace,
  root/strict graph, snapshot Error identity, raw aliases/cache, CommonJS and
  nine initialization failures. Deep/async/CallTracker operations remain deferred.
- [Querystring](querystring.json):32groups/210delimiter combinations/1,536
  malformed-byte vectors and11profile cases per call, retained Jco[1,2] and
  fresh Wasmtime1; native Buffer ownership, null-prototype dictionaries,
  aliases/CJS/private-constructor injection and eight initialization failures.
- [Buffer](buffer.json), [Path](path.json) and [Events](events.json) full bounded
  regressions pass on this new engine. These are Release checks, without a new
  GC-stress or allocator-fault claim.
- [Selection](selection.json):153admission/bundle checks, including32independent
  feature combinations. [CMake/recipe](cmake-policy.json):15configure/sentinel
  checks with unrelated target creation mocked, including no-clobber behavior.

The same [joint HTTP component](http-audit.json), SHA
`89b40e0458e0c9b7b172cf6d36209c96b12d80e477e55d18b804a9954624310b`,
passes three requests each on [stock Wasmtime42.0.1](wasmtime-http.json) and
[official wasmCloud2.11.0 local wash host](wasmcloud-http.json). It includes all
the bounded module corpora and entropy checks, ten first-deployed computed bare
aliases, cache/export/default identity checks and explicit deferred-operation
failures. Both host processes stop with exit code0. Counters are[1,1,1] on both
hosts; HTTP instance reuse or request isolation is not established.

Its only imports are `wasi:http/types`, `wasi:io/error`, `wasi:io/poll`,
`wasi:io/streams`, `wasi:clocks/monotonic-clock` and `wasi:random/random`, all
version0.2.10. The clock dependency is duration-type-only, without callable
clock imports. It exports only `wasi:http/incoming-handler@0.2.10`. No custom
host service or Wasmtime/wasmCloud modification is used. The component is
60,299,681bytes because it retains correctness corpora and initialization state;
this is not a minimal product-size or performance measurement.

The separately frozen-v5 [Weval experiment](../../weval-experiment/v5/RESULTS.md)
has its own source/artifact/protocol evidence. It supports bounded native byte
codecs, records copying-constructor and memory counterexamples, and remains
experimental pending its broader release gates. No Weval result transfers to
v6 automatically. The stopped newer private OOM gate remains unverified; prior
accepted Buffer allocator scopes remain separate.

Next work is bounded util, verified stream/web bridging, classic streams and
scheduler/lifecycle/ALS integration, followed by native compression/crypto and
independent standard-capability variants. Those roadmap gates remain open.
