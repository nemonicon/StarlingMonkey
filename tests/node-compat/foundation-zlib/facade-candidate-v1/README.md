This is an **uninstalled, unlinked source proposal** for a bounded `node:zlib`
facade. It adds no native source, CMake flag, registry entry, bundler admission,
component or host interface. Accepted runtime support remains unchanged.

`zlib-facade.generated.mjs` is an internal factory, not a public Node module.
Its returned finite record has the pinned Node22 namespace: 39 named bindings
plus default. A future integration must pass this record to the existing
`Engine::define_builtin_module` mechanism used in
[`register.cpp`](../../../../builtins/node-compat/register.cpp), registering
`node:zlib` and `zlib` from the same record. That actual registration, factory
bundling/header generation, CMake source membership and finite production
admission are outstanding. No new embedding API is proposed.

The [export contract](export-contract.proposal.json) is a source proposal,
not an installed production manifest. It declares six partial synchronous
operations: `deflateSync`, `inflateSync`, `gzipSync`, `gunzipSync`,
`deflateRawSync`, and `inflateRawSync`. They would call the separately
[syntax-checked JSAPI template](../jsapi-candidate-v1/README.md). All 31 other
callables have explicit named declarations and throw `ERR_SM_NODE_UNSUPPORTED`
on call and construction. Implemented sync operations also explicitly refuse
construction, a deliberate Node deviation. No Proxy or placeholder namespace
is used. There are no callback, streaming, Brotli, CRC32 or auto-detect APIs.

The admitted inputs are fixed, attached, unshared ArrayBuffers and their full
typed-array/DataView byte windows, including profile Buffers. Strings are an
explicit refusal. Input is bounded to 1 MiB; result bytes to 16 MiB. Options
are undefined or an ordinary object/null-prototype record with only an own
data property `maxOutputLength`, undefined or an integer from 1 to 16 MiB.
All other own keys, symbols, accessors and nonordinary prototypes are explicit
refusals, including otherwise valid Node codec defaults. Inherited properties
are ignored. Arbitrary Proxy traps and adversarial reflection are outside
this ordinary-record contract. Node accepts a wider input/options domain;
error messages, coercion and validation order are not fully reproduced.

Input views share their backing until the private C++ call stages bytes;
the existing wrapper allocates before its NoGC borrow and copies into owned
native staging. It publishes only complete successful output into a fresh
JS-owned Uint8Array. The facade wraps that backing with captured
`Buffer.from(ArrayBuffer, offset, length)`, adding no further byte copy.
Rooting, moving GC and ownership of that complete path remain unverified in a
real component. The output limit is not a peak-memory bound. Single complete
member/no trailing input and dictionary refusal remain narrower than Node.

`constants` and `codes` preserve the pinned values and number/string types.
Both are frozen null-prototype records; the default object is frozen, unlike
Node's mutable CommonJS export object. Its legacy numeric constants remain
nonenumerable. Named/default callable and data identities match within the
factory record. Namespace reads and Promise assimilation are safe; no `then`
binding exists. CommonJS lowering would use the existing selected static
bundler contract, not a runtime CommonJS loader or mutable-export sync.

These are compatibility-inventory values, not an assertion about the compiled
backend version. In particular Node's `ZLIB_VERNUM` is4865 (`0x1301`), while the
audited SpiderMonkey zlib header is4880 (`0x1310`). Before production promotion,
resolve whether to expose the actual compiled value with a declared deviation
or pin a matching backend. No compressed-byte identity across versions is
claimed. That version decision remains open in this source-only proposal.

The first host-only attempt caught a pre-existing inventory serialization gap:
Node's numeric `Z_MAX_CHUNK = Infinity` had become JSON null. The original
inventory remains unchanged. [Nonfinite supplement](nonfinite-supplement.json)
records a fresh observation in pinned Node22 and generates an actual numeric
Infinity. The failed source/observation and the first successful 80-check
report are retained under `preparation-history`.

The final host suite uses Node's codec as a stand-in for the private kernel.
It checks finite exports, 31 deferred call/new pairs, six construction refusals,
constants/descriptors, normal byte-value results, views/backing, caps, options
and captured intrinsics. This validates facade routing/semantics only, not
native compression or JSAPI integration. The native codec's separate 86 host
vectors and SDK syntax check have their own scopes; no guest pass, malformed
native call, GC, target-host, size, memory or performance result is claimed.
Real ESM/alias/CommonJS bindings, top-level initializer failures, runtime
errors, native input/output/GC/limit behavior, exact emitted imports and both
stock hosts must pass after actual integration.
