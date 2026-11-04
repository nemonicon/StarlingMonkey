The accepted [v6 checkpoint](../milestones/foundations-v6/README.md) now combines
Buffer/stub, Path, Events, StringDecoder, Assert/strict, Querystring and entropy
in the same component on stock Wasmtime42.0.1 and official wasmCloud2.11.0.
`http-v6.mjs` preserves ten computed first-deployed bare aliases; its final
imports remain the same six standard0.2.10 interfaces. All285native inputs,
16complete reports and source/harness copies are archived. Counters[1,1,1]
do not establish HTTP instance reuse. The60,299,681byte corpus-heavy component
is a correctness artifact, not a product-size measurement.

The following records preserve the earlier v4 joint fixture unchanged.

The joint Runtime v4 HTTP fixture passes three requests each on unmodified
Wasmtime 42.0.1 and official wash 2.11.0. It combines existing native Buffer/stub
and entropy checks with optional Path and Events. No native source changed for
this transport test, and no extra capability was selected.

[Full results](joint-results.json) preserve the 271-input engine receipt,
fixture hashes/source snapshots, exact final interface/type audit and both host
reports. Separate [Wasmtime](joint-wasmtime-results.json),
[wasmCloud](joint-wasmcloud-results.json), and [component audit](joint-component-audit.json)
records remain available.

- Engine: `c89d9b4f0b5d8decac81e76dec030167e716bf2071c073d58e58a95a2f510de7`.
- Same component on both hosts:
  `7a422b5f7f49452498241dd39c1aeb39f50a59bed97a24a5e21dec22926aa00a`.
- Exactly six standard 0.2.10 imports: HTTP types; IO error/poll/streams;
  monotonic-clock type-only (no callable clock); secure random.
- Per request: 381 Buffer string and 250 byte vectors plus existing stub/error/
  identity/ownership checks; eight WebCrypto ownership vectors and fresh runtime
  entropy; Path 15,696 lexical/4,046 glob/13 denied-budget/four adversarial cases;
  Events 27 semantic/mutation cases plus 13 deferred operations and three limits.

`http.mjs` statically imports canonical built-ins and performs no top-level
bare dynamic import. On deployed entry it computes six bare specifiers:
`buffer`, `child_process`, `path`, `path/posix`, `path/win32`, `events`.
The emitted bundle retains `import(id)` rather than resolving these literals to
canonical names. Each result validates repeated-import cache, all export value
identities, typed namespace/default/constants, safe Promise inspection and
explicit deferred call/construction errors. Existing ScriptLoader registration
only stores builtin values; `get_builtin_module` compiles/caches a namespace
when requested. This exercises the uncached deployed branch without a public
cache-observer API or custom host service.

Both hosts reported component request counters `[1,1,1]`. The report includes
per-component foundation/event/snapshot counters; these observations do not
establish same-instance reuse. Stock direct component tests separately exercise
retained calls. No AsyncLocalStorage, async Events helpers, Node HTTP/HTTPS,
raw DNS/socket or TLS-over-sockets compatibility is inferred.

The original entropy-only fixture was copied byte-for-byte to
[`../entropy/archived-fixtures/http.entropy-v1.mjs`](../entropy/archived-fixtures/http.entropy-v1.mjs)
with its original-location hash record before `runChecks` was exported for
composition. Earlier v1/v3 reports and accepted milestone records remain
unchanged. The joint fixture is independently selected through
`NODE_COMPAT_HTTP_ENTRY`; legacy fixture selection keeps its prior import set.
