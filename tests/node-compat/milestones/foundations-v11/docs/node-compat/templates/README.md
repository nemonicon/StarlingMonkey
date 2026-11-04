# Baseline templates: `sm-node-22.14.0-m0.1`

These frozen audit templates precede the [compiled opt-in implementation](../../../builtins/node-compat/README.md)
and its [native integration results](../../../tests/node-compat/README.md).

These are reviewable architecture templates, not an enabled Node compatibility layer. The ESM stub and Buffer facade execute under Node v22.14.0; their differential checks passed against that exact release. The C++ sources, CMake integration, GC behavior and native performance have **not been compiled or tested**. A slow reference kernel exists only to test facade semantics. Nothing here claims complete Buffer support.

The export inventory is [export-manifest.node-v22.14.0.json](export-manifest.node-v22.14.0.json), derived from Node v22.14.0 [buffer.js](https://github.com/nodejs/node/blob/v22.14.0/lib/buffer.js) and [child_process.js](https://github.com/nodejs/node/blob/v22.14.0/lib/child_process.js), and checked against the exact binary. Before writing these templates, the audit inspected this checkout's native text codec/streams implementations, `tests/e2e/init-script`, and Jco v1.40.0 `packages/jco/src/node-builtins/buffer.ts` plus `packages/jco/test/node/buffer.js`. The Jco adapter's unenv/Feross implementation and its Node v24 constants are comparison inputs; this profile's oracle is Node v22.14.0.

## Executable semantics and uncompiled integration

| File | Purpose | Verification |
|---|---|---|
| [child-process.mjs](child-process.mjs) | Real ESM declarations for nine Node exports plus default | Exact namespace shape, identities, invocation, construction, inspection and direct prototype refusal checked under Node v22.14.0 |
| [buffer-facade.mjs](buffer-facade.mjs) | Auditable semantic factory using injected byte kernel and native web codecs | Differential subset checked under Node with the JS reference kernel |
| [node-buffer.mjs.in](node-buffer.mjs.in) | Explicit public ESM entry for a future facade-loading path | Uncompiled alternative entry; its internal import requires registration if this path is chosen |
| [native-buffer.cpp.in](native-buffer.cpp.in) | Native guest hex encoder/decoder | Source reviewed only; no host imports |
| [register-profile.cpp.in](register-profile.cpp.in) | Content-realm factory evaluation and module/global registration | Uncompiled |
| [generate-factories.mjs](generate-factories.mjs) | Bundle the same facade/stub into C++ string constants | Executed successfully with locked Rolldown 1.2.16; generated output evaluated in Node |
| [node-compat.cmake.in](node-compat.cmake.in) | Opt-in `add_builtin` integration | Unconfigured/uncompiled; production CMake files unchanged |
| [reference-kernel.mjs](reference-kernel.mjs) | Host-free JS test double | Explicitly excluded from production/native performance claims |

## Exact Buffer contract

Every instance is a genuine `Uint8Array`, with real typed-array internal slots and ordinary `buffer`, `byteOffset`, `byteLength`, indexing, iteration and typed-array operations. `Buffer.prototype` derives from `Uint8Array.prototype`. A private species allocator returns real typed arrays with the Buffer prototype; `map` and `filter` allocate copies with Buffer identity. No native class object pretends to have typed-array internal slots.

| Entry | Supported inputs and behavior |
|---|---|
| `Buffer.alloc(size, fill?)` | Finite integer number `size`, 0–16 MiB inclusive; omitted fill zeroes, numeric fill follows Uint8Array numeric conversion. No slab allocator. Fractional size and string/Buffer fill are unavailable. |
| `Buffer.from(string, encoding?)` | At most 1,048,576 UTF-16 source code units. `utf8`, `utf-8`, `hex`; case-insensitive. Omitted or empty encoding selects UTF-8. Native TextEncoder handles replacement of lone surrogates. Hex stops at first invalid pair and ignores an odd trailing nibble, matching Node. Newly allocated bytes become Buffer without a second byte copy. |
| `Buffer.from(Uint8Array)` | Copies exactly the visible byte range into independent storage, including input with nonzero offset. Profile Buffer input follows this same copy path. Shared/resizable backing stores unavailable. |
| `Buffer.from(ArrayBuffer, offset?, length?)` | Shares the original fixed-length ArrayBuffer. Offset/length must be nonnegative integer numbers; defaults are zero/remainder. `buffer` identity and byte offset preserved. Views larger than 16 MiB are refused. No numeric-string, fractional or negative coercions. |
| `Buffer.isBuffer(value)` | Private WeakSet brand; false for plain Uint8Array and prototype spoofs. Brand crosses the two registered aliases through shared bindings, not independently instantiated factories. |
| `Buffer.isEncoding(value)` | True only for string `utf8`, `utf-8`, `hex`, ignoring case. This intentionally reports profile support, rather than every encoding recognized by Node. |
| `Buffer.byteLength(value, encoding?)` | String encodings/source limit above, or ArrayBuffer/Uint8Array byteLength. This metadata-only operation also accepts resizable ArrayBuffers and shared/resizable-backed Uint8Arrays; construction from those stores is excluded. Direct SharedArrayBuffer input remains excluded. Hex length is floor(code units/2), even for invalid hex, matching Node. UTF-8 currently allocates TextEncoder output; a native length-only path is a later measurable optimization. |
| `buffer.toString(encoding?, start?, end?)` | Supported encodings above; omitted/default indexes or integer number indexes only. Indexes clamp to `[0,length]`; end before start yields empty output. Uses a view with the original offset. UTF-8 decoding replaces malformed bytes and preserves leading BOM (`ignoreBOM:true`). |
| `buffer.subarray(start?, end?)`, `buffer.slice(start?, end?)` | Uint8Array index normalization and species behavior; shared backing ArrayBuffer, adjusted byteOffset, Buffer identity. Buffer `slice` shares storage. |
| `buffer.parent`, `buffer.offset` | Legacy aliases for backing ArrayBuffer and byteOffset. |

Other own Node Buffer methods are declared as finite throwing functions, including numeric reads/writes, `copy`, `concat`, `compare`, `write`, searching, `fill`, swapping, JSON conversion, `toLocaleString`, and custom inspection. Inherited Uint8Array APIs that Node does not override remain typed-array APIs. Buffer's Node-overridden overloads such as `indexOf` are explicitly unavailable; they cannot silently fall back to incompatible Uint8Array rules. There are no universal Proxies or property-read traps.

All 14 named `node:buffer` exports exist, plus default. `Blob`, `File`, `SlowBuffer`, `atob`, `btoa`, `isAscii`, `isUtf8`, `resolveObjectURL` and `transcode` are callable refusals in this milestone. Blob/File and atob/btoa are candidates for reusing the web implementations after Node-specific semantic tests. `Buffer()` and `new Buffer()` also refuse use. No unsupported callable is replaced with an empty object.

`INSPECT_MAX_BYTES` is numeric 50; `kMaxLength`/`constants.MAX_LENGTH` are numeric 16,777,216, and `kStringMaxLength`/`constants.MAX_STRING_LENGTH` numeric 33,554,432. These are profile limits, not Node's implementation limits. `poolSize` is numeric zero; modifying it has no allocation effect. The source-string cap bounds UTF-8 temporary allocation to at most 3 MiB. Hex output is bounded to 32 MiB. These limits do not promise successful allocation under memory pressure: ordinary engine OOM is still possible.

Supported invalid-size types throw TypeError `ERR_INVALID_ARG_TYPE`; negative/nonfinite/excess size throws RangeError `ERR_OUT_OF_RANGE`; out-of-bounds ArrayBuffer offset/length throws RangeError `ERR_BUFFER_OUT_OF_BOUNDS`; an unknown encoding throws TypeError `ERR_UNKNOWN_ENCODING`. Message text is not Node-compatible. The facade validates `toString` encoding even for an empty selected range, whereas Node can return an empty string before validation; that is an explicit error-order deviation. Node-valid but unsupported encodings and overloads throw `ERR_SM_NODE_UNSUPPORTED`, as do fractional sizes. Missing input, arrays, array-like/valueOf/JSON forms, other typed arrays, DataView, SharedArrayBuffer, resizable backing stores and cross-realm overloads are outside the selected domain. Non-string encoding coercions are unavailable. Detached-buffer behavior remains inherited from SpiderMonkey's typed-array operations and requires real-component verification; this template does not claim a uniform profile error for every detached access.

## ESM, aliases and failure behavior

The public module contract is ESM with enumerated, versioned bindings. Each named export equals the same member of the default object. The default and constants objects are frozen, a documented deviation from Node's mutable CommonJS default object. Bare `buffer`/`child_process` aliases and `node:` names are registered with the same export objects. The existing loader maintains separate module namespace records by specifier; cross-alias **namespace-object** equality is not promised. Exported values and constructors must have equal identity across aliases and global Buffer.

CommonJS support is restricted to a configured bundler's statically analyzable conversion using this manifest. There is no dynamic `require`, CommonJS cache, or `syncBuiltinESMExports` mutation protocol. A bundler must externalize the selected specifiers before Jco's JavaScript adapters resolve them; preserving `node:` syntax alone does not guarantee that. See the main audit for toolchain routing gates.

Every unsupported callable immediately throws an Error with code `ERR_SM_NODE_UNSUPPORTED`, `module`, `operation`, and `profile`. The same rule applies during componentization. `ChildProcess`, `_forkChild`, `exec`, `execFile`, `execFileSync`, `execSync`, `fork`, `spawn`, and `spawnSync` are real function exports; invocation and construction fail. Direct `ChildProcess.prototype.spawn/kill/ref/unref` and `[Symbol.for('nodejs.dispose')]` calls also fail with that code. EventEmitter inheritance, live child instances, IPC, signals and process behavior are outside the stub contract. Namespace property reads, `Object.keys`, JSON inspection and Promise/await inspection are safe, with no accidental `then` member.

## Existing extension mechanisms and memory ownership

The integration template uses [`api::Engine::define_builtin_module`](../../../include/extension-api.h), consumed by [`get_builtin_module`](../../../runtime/script_loader.cpp), whose generated ESM source captures the explicit enumerable keys. This creates real ESM exports; arbitrary future properties do not appear automatically. Register eager data properties only: lazy getters could perform observable work at first import and complicate snapshots.

The CMake template reuses [`add_builtin`](../../../cmake/add_builtin.cmake), which creates/link static libraries with `spidermonkey` and `extension_api` and generates `builtins.incl`. `install(api::Engine*)` runs through [`install_builtins`](../../../builtins/install_builtins.cpp). It evaluates the bundled facade factory in the content realm through real SpiderMonkey `JS::Evaluate`/`JS::Call` APIs, then registers both aliases. It does not call `Engine::eval_toplevel` during builtin installation, where the engine's lifecycle assertion disallows it. The generated factory path passes the native kernel directly; `node-buffer.mjs.in` illustrates a separate explicit-ESM path requiring a registered private kernel module, and is not used by this installer.

Local `JS::RootedObject`/`RootedString`/`RootedValue` variables protect every GC object across allocations. The kernel retains no `JSObject*` or byte pointer in C++ state. Long-lived JS functions and objects remain reachable through the loader's traced persistent maps; the facade's WeakSet brands do not keep dead Buffer instances alive. There are no new finalizers, host handles, or native resources to snapshot. Any future C++ heap field holding a JS thing must use `JS::Heap<T>` plus an actual trace hook, not an untraced raw pointer.

Hex decoding allocates a real JS Uint8Array first, then borrows its byte pointer only inside `JS::AutoCheckCannotGC`. Encoding roots the input, allocates an owned `JS_malloc`/`JS::UniqueChars` staging buffer, reacquires the input pointer inside a no-GC scope, and creates the JS string after that scope ends. No JS callbacks or allocations occur while using borrowed pointers. The staged hex output is a remaining copy to measure, not a zero-copy claim. No Rust allocator ownership crosses into JS. Future direct ArrayBuffer adoption must use the allocator and success-only transfer pattern already demonstrated in [`TextEncoder::encode`](../../../builtins/web/text-codec/text-encoder.cpp); ownership stays with the caller on failure. Never adopt a Rust `Vec` pointer with a mismatched C++/JS deallocator.

## Checks and required next gates

The exact oracle invocation used for the executable template check was:

```sh
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node docs/node-compat/templates/template-test.mjs
```

It passed export inventories, default/named identities, every child export's invocation/construction, shared-vs-copying views, offsets, Uint8Array identity/species, UTF-8 malformed/BOM behavior, hex truncation, numeric fill, supported error codes, unsupported overloads and numeric limits. This is a deterministic facade/stub differential check with [reference-kernel.mjs](reference-kernel.mjs), not evidence that the native kernel works. The separate [real-component harness](../component-tests/README.md) also passed facade checks with the reference kernel on the released ComponentizeJS engine under Wasmtime 42: snapshot-created WeakSet brands, codec instances, Buffer instances, ArrayBuffer sharing/copy, species and errors survived componentization. That engine is distinct from this checkout; native-template and checkout-specific integration gates remain open.

Factory generation was executed with the same Node binary and `/tmp/starling-node-compat/toolchain/node_modules/rolldown/dist/index.mjs` (locked version 1.2.16), producing a 14,665-byte generated header in `/tmp` during the audit. Generated byte size is a source artifact measurement, not component-size evidence. `factory-test.mjs` verifies the resulting expressions evaluate to callable factories with matching identities/refusals.

Before enabling the CMake option: compile against the pinned SpiderMonkey headers; validate all JSAPI overloads; run GC zeal/stress and OOM injection; test empty/detached/shared/resizable inputs, cross-realm and species edge cases; run native kernel fuzz/differential tests inside a component; verify top-level unsupported calls fail componentization; test snapshot/resume/repeated requests; and instantiate the resulting component on both exact target hosts. Inspect emitted imports before and after composition/optimization. This kernel and stub must add no host imports. Compare component size, peak/retained memory, startup and byte throughput against the pinned Jco/unenv Buffer adapter before concluding the native path is worthwhile.
