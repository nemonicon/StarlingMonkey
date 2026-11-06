# ComponentizeJS, Jco, WASI and host audit

The combined355 resource mapping experiment found a caller boundary issue in the
pinned Jco implementation. Its `transpileComponent` calls `prepOpts`, which
mutates the options object. The first caller later passed that same object to
its strict JSON writer and failed publication after generating and auditing the
mapped files. Its raw1 failure remains retained. The corrected caller saves the
pristine request before Jco import, passes a separate workcopy, and records a
typed post-call shape. [The fresh mapping run](../../tests/node-compat/foundation-scheduler/combined-native-runtime-v3-resource-map-root-results.json)
finishes raw0 and actually observes the added undefined `flagsAsBigInt` field;
[independent mapped DATA review](../../tests/node-compat/foundation-scheduler/independent-combined355-runtime-v3-resource-mapped-results-review-v1/results.json)
passes. That mapping action imported no application and invoked no guest export.
Ordinary runtime is a separate phase documented in [progress.md](../../progress.md).

The same post-call shape contains default map names for `jco:node/*` and
`wasi:tls/types@0.2.0-draft`. They are not selected capabilities in this profile.
The unchanged component imports only the three selected standard WASI0.2.10
clock/poll interfaces; the mapped static imports target only the official
clock/io shim files. Options-map entries are not emitted imports or capability
grants. Keep auditing the final component type graph and generated loading graph;
do not infer portable Node/TLS support from Jco's adapter names. WASI P2 sockets
alone still do not provide TLS. [progress.md](../../progress.md) records the
failed and corrected Source generations and actual review boundaries.

Historical source audit collected on 2026-11-02. Current executed build/ABI/host evidence is in the [allocation-r2](../../tests/node-compat/milestones/allocation-r2/README.md) and [entropy-v1](../../tests/node-compat/milestones/entropy-v1/README.md) checkpoints; the audit below predates those builds. **Source-verified findings** below do not establish that rebuilding ComponentizeJS against this StarlingMonkey checkout succeeds. External source archives were inspected under `/tmp/starling-node-audit`; installed tools and generated components are kept outside the repository.

## Exact baseline

| Item | Selected pin | Evidence / qualification |
| --- | --- | --- |
| StarlingMonkey | `54b3329b3ce818fd1f244e871e9c259b63667cda` | Current checkout; a replacement engine must be built from this source. |
| Node API / differential oracle | `v22.14.0` | A fixed compatibility target, not a claim of support for every Node export. Jco's adapters often target Node 24 and must not determine this profile's export inventory. |
| ComponentizeJS | npm `@bytecodealliance/componentize-js@0.23.0`; source `4d812f5a7b524cea5bcfd565cac55f3fab876a57` | [release source](https://github.com/bytecodealliance/ComponentizeJS/tree/4d812f5a7b524cea5bcfd565cac55f3fab876a57); source gitlink pins StarlingMonkey `9dda8ba7fcda2e17c6795d402f0478cf4c1f7f37`, different from this checkout; packaged engine hash is recorded separately. |
| Jco | npm `@bytecodealliance/jco@1.40.0`; source `42cd21e0a31362dbb519f4749f3689bba0fbdb1d` | [package manifest](https://github.com/bytecodealliance/jco/blob/42cd21e0a31362dbb519f4749f3689bba0fbdb1d/packages/jco/package.json); depends on ComponentizeJS `^0.23.0`. Pin both directly and retain npm lockfile. |
| SpiderMonkey | `FIREFOX_147_0_4_RELEASE_STARLING` | Current `cmake/spidermonkey.cmake:1`; record archive hashes in build CI. |
| WASI | `wasi:cli`, `wasi:clocks`, `wasi:filesystem`, `wasi:http`, `wasi:io`, `wasi:random`, `wasi:sockets` all `0.2.10` when selected | Current `host-apis/wasi-0.2.10/wit/deps/*/package.wit` and default `CMakeLists.txt:19`. Selecting this host API does not prove every imported interface is required by an application. |
| Existing engine bindings world | `local:bindings/bindings` | `host-apis/wasi-0.2.10/wit/main.wit` includes `wasi:cli/command@0.2.10` and `wasi:http/proxy@0.2.10`. |
| Existing CLI adapter world | `local:bindings/command-extended` | `host-apis/wasi-0.2.10/wit/command-extended.wit`; CLI command plus outgoing HTTP handler. Package inherited from sibling `main.wit`. |
| Direct deployment target | Wasmtime `42.0.1`, release commit prefix `6844a83b5` | Repository's existing `cmake/wasmtime.cmake:1`; [release](https://github.com/bytecodealliance/wasmtime/releases/tag/v42.0.1). |
| Secondary target | wasmCloud `2.11.0`, commit `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff` | Annotated release tag dereferences to this commit; [source](https://github.com/wasmCloud/wasmCloud/tree/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff). Its Wasmtime dependencies are `48.0.7` (`Cargo.toml:134–138`); distinguish this embedded version from the standalone target. |

The application test world is deliberately capability-free: `starling:node-compat-test/profile@0.1.0`, exporting `run: func() -> string`. This is an application export, not a host service. Future HTTP variants should explicitly select `wasi:http/proxy@0.2.10`; command variants select `wasi:cli/command@0.2.10`. Do not publish the union world as the mandatory import contract for Buffer-only applications.

## Existing ComponentizeJS mechanisms

Verified from the pinned source:

- `CMakeLists.txt:3–20` accepts `STARLINGMONKEY_SRC` and includes StarlingMonkey's `cmake/add_as_subproject.cmake`; it registers `componentize::embedding` through `add_builtin(... SRC embedding/embedding.cpp)`. Reuse that extension mechanism.
- The Makefile accepts `STARLINGMONKEY_SRC`; its release target produces `lib/starlingmonkey_embedding.wasm`. Build using this checkout and pass that artifact through the documented `engine` option (`src/componentize.js:getEnginePath`, lines 502–512). A stock StarlingMonkey `starling-raw.wasm` without the ComponentizeJS embedding is not interchangeable with this engine.
- `src/componentize.js:64` defaults to `stdio`, `random`, `clocks`, `http`, `fetch-event`. Baseline Buffer/stub fixtures disable all five. The `enableFeatures` option is destructured but this release builds the feature set by subtracting `disableFeatures` from defaults; validate emitted imports instead of assuming an option guarantees pruning.
- `src/componentize.js:151–170` splices the selected WIT bindings, writes an initializer, and later invokes Wizer using `componentize.wizer`, inherited environment, and temporary preopens (`315–347`). Snapshot creation executes application top-level code. `350–369` turns nonzero process status or signal into failure; `374` onward additionally checks the initialization state.
- `embedding/embedding.cpp:366–409` invokes `__wizer_initialize`, takes the source module namespace, and binds exported functions through the initializer. `call` at `160` resets Math.random on first deployed call and resets `performance.timeOrigin` only when clocks are enabled. These existing resets are not a complete entropy, environment, request-state or live-handle policy.
- `embedding/embedding.cpp:253–300` resolves the result through a promise and drives `Engine::run_event_loop`; arbitrary host imports are not native Node event-loop operations.
- `embedding/embedding.cpp:139–157`, `cabi_realloc`, allocates and reallocates through `JS_realloc` / `JS_free`; borrowed canonical ABI memory and JS ArrayBuffers require explicit ownership and lifetime review.
- `crates/spidermonkey-embedding-splicer/src/stub_wasi.rs:18` knows exact WASI versions through `0.2.10`; its `stub_wasi` logic strips/stubs engine imports using features and world imports. Import validation must inspect the final component after this processing and Preview1 adaptation.

Tests inspected before proposing new code: `test/builtins.js`, `test/builtins/{pure,globals,error-sync,error-async,math-random,math-random-disabled,now-disabled,crypto-random-disabled}.js`, `test/{api,bindings,util}.js`, and repeated-call/resource fixtures. `test/util.js:28–83` componentizes, transpiles the real component and imports its generated JavaScript; this is different from running application JavaScript directly in Node.

## Existing Jco Node adapters

[Jco's pinned adapter directory](https://github.com/bytecodealliance/jco/tree/42cd21e0a31362dbb519f4749f3689bba0fbdb1d/packages/jco/src/node-builtins) already contains extensive Node compatibility work. It must be measured and audited before replacement.

| Existing implementation | Source-verified behavior | Consequence for this profile |
| --- | --- | --- |
| `buffer.ts:14–141` | Wraps audited unenv `2.0.0-rc.24` Feross Buffer core; normalizes base64url; uses native web Blob/File where present; some exports throw. Uses a Proxy only to guard deprecated constructor invocation, not as ESM namespace. Constants and allocation ceilings follow a different runtime/Node target. | Useful existing benchmark. Replace only selected heavy kernels, generate the Node 22 manifest separately, and validate exact semantics and limits. Do not equate JavaScript Buffer with native guest Buffer. |
| `stream.ts:createStreamBuiltin` | Provides classic streams, promises, consumers and `stream/iter`; redirects audited readable-stream dependencies to common Buffer/EventEmitter/StringDecoder and a scheduler. | Streams are foundational. Native Buffer resolution must also replace this internal dependency path; `stream/iter` is not part of the selected Node 22 inventory. |
| `index.ts:70–166` | `nodeBuiltinPlugin` composes virtual adapters; `node:` names resolve directly, bare aliases consult installed packages first, special CommonJS paths exist for events/assert/stream. | Do not assume all bare aliases currently mean the native built-in. Profile alias policy must be explicit and tested. |
| `cmd/componentize.ts:286–330` | With bundling enabled, creates global injection plus `nodeBuiltinPlugin`, collects WIT requirements, and selects socket bindings `0.2.10` for StarlingMonkey. | Merely registering `node:buffer` in StarlingMonkey will not override the bundler's JavaScript adapter or its global Buffer injection. |
| `bundle.ts:100–175` | Rolldown neutral-platform bundling, config merged aliases/plugins, one ESM chunk, no split assets. WASI and `jco:node/` are default externals (`22–25`, `182–190`). | Explicitly externalize selected native `node:` imports before adapter replacement, and route Buffer global injection to that same identity. Reject residual custom capabilities. |
| `net.ts:createNetBuiltin`, `wasi-sockets.ts` | Already constructs an adapter over standard P2 socket imports, using `0.2.10` for StarlingMonkey. | Candidate for audited future reuse; do not introduce custom services. Node 24 additions in its export list still need filtering against Node 22. |
| `crypto.ts:createCryptoBuiltin` | Default cryptographic operations use the portable guest implementation; the explicit `direct` KDF mode injects `jco:node/crypto-kdf@0.1.0`. | Measure the portable path; replace selected kernels with native guest code. Disallow the direct host path. |
| `fs.ts`, `dns.ts` | Add FS/DNS requirements through `node-wit.ts`, including custom Node host interfaces for the broad Node API. | These whole adapters are outside the profile; future restricted filesystem/name lookup should use only selected standard P2 interfaces and declare semantic gaps. |
| `zlib.ts:createZlibBuiltin`, `node-wit.ts:173` | Standard-library adapter adds `jco:node/zlib@0.1.0`. | This is a custom host capability; disallowed in this portable profile. Reuse codec code in the guest only after licensing/build/size audit. |
| `child-process.ts`, `node-wit.ts` | Adapter adds custom `jco:node/child-process@0.1.0`. | Do not use in this profile. Import-only explicit ESM stub is the appropriate first milestone. |
| `tls.ts`, `node-wit.ts:125–151`; tests `test/node/tls.js:91` | Uses draft `wasi:tls/types@0.2.0-draft` and/or custom Node adapter requirements. | Draft TLS is outside this profile's explicitly selected standard WASI 0.2.x contract. TCP/UDP sockets do not provide TLS. Future TLS needs guest TLS plus an explicit trust policy, or remains unavailable. |

Tests inspected: `packages/jco/test/node/{buffer,builtins,stream-classic,globals,tls,cluster,zlib}.js`, `packages/jco/test/helpers.js` and fixtures under `test/fixtures/componentize/node-buffer`. Buffer tests compare adapter behavior with host Node and execute a generated component. The tests' Node 24 inventory and custom capability hosts do not establish compliance with the Node 22 / standard-only profile.

## Bundler integration proposal

The first milestone should bypass Jco's automatic Node adapter bundling. Use a small profile bundler invocation with a manifest-controlled resolver, retaining one ESM application chunk; then call ComponentizeJS directly with the custom engine. For names in the versioned native manifest, return the canonical `node:` specifier as external before Jco adapter resolution. Canonicalize both `buffer` and `node:buffer` according to the profile contract; resolve npm packages named `buffer/` separately and document any difference from Jco's installed-package-first behavior.

Bundle CommonJS dependencies to ESM, lowering statically analyzable `require('buffer')` to the same native module. Choose and test the rule `require('buffer')` receives the default object with named members; native named bindings are the same values as its properties. Do not claim runtime CommonJS loader support, `module.createRequire`, dynamic require, or mutable Node builtin synchronization. A profile-specific CommonJS wrapper may be required: leaving `require('node:buffer')` external can retain a dynamic require helper that does not work in StarlingMonkey.

Global Buffer injection must use `{ Buffer }` from canonical native `node:buffer`; disable Jco's `globals.ts` Buffer injection or override it in the profile bundler. Existing audited stream `buffer` dependencies and unenv Buffer side effects must also be remapped or rejected. Assert the bundled text/module graph retains exactly the expected native imports and contains no Feross/unenv Buffer core. Then inspect final emitted component imports and reject `jco:*`, `wasmcloud:*`, draft TLS and every WASI interface absent from the selected allowlist.

An eventual upstream Jco option could select `nativeBuiltins: manifest` and make this override coherent across resolution, CJS lowering and globals. That is proposed toolchain work, not an existing option.

## Host compatibility boundaries

wasmCloud 2.11.0's `crates/wash-runtime/src/engine/mod.rs` registers P2 CLI, clocks, filesystem, random, HTTP and socket linker functions, alongside P3 and optional extensions. Its P2 socket integration is standard-interface-based (`add_wasi_to_linker`, lines 77–184); grants/policy still determine usable capabilities. These source findings do not prove target instantiation of the new engine or any particular world. The acceptance run must deploy an unchanged component with standard imports only to the selected unmodified host and record its grants. Do not add wasmCloud services, custom WIT or host modifications to make an adapter pass.

WASI HTTP grants HTTP-level requests/responses and host-managed HTTPS; it does not expose Node's socket lifecycle, full agent pooling, TLS sockets, ALPN policy, raw upgrades, HTTP/2 session control or process networking. Filesystem operations are preopen/capability-based and cannot promise arbitrary Node absolute paths, host process cwd or unrestricted symlinks. P2 name lookup resolves IP addresses, not the complete `dns.resolve*` record inventory. Environment values are explicitly granted deployment data; they must not be snapshotted from the build environment.

## Reproduction and validation boundary

Install in an external work directory:

```sh
npm install --prefix /tmp/starling-node-compat/toolchain --save-exact --no-audit --no-fund \
  @bytecodealliance/componentize-js@0.23.0 @bytecodealliance/jco@1.40.0
```

Retain the generated package-lock JSON and `npm ls --all` output in CI to freeze all transitive packages. Source pins alone do not pin downloaded engine/Wizer binaries. Hash those artifacts separately.

For the custom engine build, use ComponentizeJS source at the selected commit, set `STARLINGMONKEY_SRC` to the audited checkout, and use the existing release build. Set `HOST_API=wasi-0.2.10` explicitly. Pass the resulting `lib/starlingmonkey_embedding.wasm` through `engine` in the direct ComponentizeJS call or Jco `--engine`. Confirm module registration and event-loop/snapshot compatibility by compiling and running the integration tests; do not present this recipe as an executed build.

`component-tests/run.mjs` supplies a reproducible real-component smoke test of the explicit stub, initialization failure and persistent instance state. Its engine option is explicit: omitting `NODE_COMPAT_ENGINE` uses ComponentizeJS's released engine, which validates the toolchain/stub but does not validate native C++ templates or this checkout. The runtime result and imports are recorded separately in that directory's results JSON.
