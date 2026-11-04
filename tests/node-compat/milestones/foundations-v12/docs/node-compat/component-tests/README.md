# Executed component smoke tests

Executed on macOS arm64, 2026-11-02, using the downloaded pinned Node.js v22.14.0 oracle, ComponentizeJS 0.23.0, Jco 1.40.0, Rolldown 1.2.16 and Wasmtime 42.0.1. See [results.json](results.json) for output, exact component hash, size and emitted WIT. No generated binaries are committed. Component sizes/hashes identify the recorded run; deterministic snapshot builds have not been established.

This tests the **released ComponentizeJS engine**, not a rebuild of StarlingMonkey revision 54b3329b3ce818fd1f244e871e9c259b63667cda. ComponentizeJS 0.23.0 source pins its StarlingMonkey submodule to `9dda8ba7fcda2e17c6795d402f0478cf4c1f7f37`; the packaged engine hash is recorded below. The C++ Buffer template was not compiled and no wasmCloud deployment was performed. The ESM stub is bundled into an application module; native runtime module registration and `node:` resolver identity still need a rebuilt-engine test.

The stub fixture verifies inside the component:

- Nine callable `node:child_process` exports plus default, matching named/default identities.
- Safe namespace enumeration, missing `then` inspection and `Promise.resolve(namespace)`.
- Every callable operation throws `ERR_SM_NODE_UNSUPPORTED` on invocation and construction, with module/operation attribution.
- Two calls to the same Jco-instantiated component retain instance state (`calls` 1 then 2).
- Wasmtime 42.0.1 instantiates and calls that same real component, with no host capabilities granted.
- A separate application's top-level `spawn()` fails during Wizer componentization.
- Final component WIT contains **zero imports** and the `run: func() -> string` export.

`buffer-check.mjs` additionally creates the Buffer semantic facade with the explicit JavaScript reference hex kernel during initialization. It checks ten UTF-8/hex cases differentially against Node v22.14.0, malformed UTF-8, BOM preservation, ArrayBuffer sharing and offsets, copied views, shared slices/subarrays, typed-array species, constructor inheritance and BYTES_PER_ELEMENT, constants, selected error codes and unsupported operations. The same component runs successfully through Jco and Wasmtime, preserves invocation state across two calls, and emits zero imports. This tests snapshot persistence of the facade's WeakSet brand, encoder/decoder and a Buffer instance; it does not test native C++ rooting or resource ownership. That component measured **12,074,190 bytes**.

The size of 11,974,315 bytes is a stub smoke-component observation with the released engine and no optimization beyond ComponentizeJS defaults. It is not a native-Buffer performance result or a before/after size comparison. A top-level marker plus persistent call counter demonstrates initialization data and instance state survive; it does not validate environment refresh, entropy reseeding, clock rebasing, request isolation or live resource handling.

Reproduce with binaries installed outside the checkout:

```sh
mkdir -p /tmp/starling-node-compat/toolchain
cp docs/node-compat/component-tests/toolchain/package*.json /tmp/starling-node-compat/toolchain/
npm ci --prefix /tmp/starling-node-compat/toolchain --no-audit --no-fund
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 docs/node-compat/component-tests/run.mjs
```

For native integration verification, set `NODE_COMPAT_ENGINE` to a ComponentizeJS embedding engine built against the exact audited StarlingMonkey revision and native templates. The fixture currently uses bundled stubs, so add a resolver-preserving case that imports `node:child_process` from that engine's module registry before claiming native resolution coverage.

Artifact SHA-256 values from this run:

| Artifact | SHA-256 |
| --- | --- |
| npm lockfile | `bd852f41ddaa956d9135640690dffb4b05c47c326210ccd277cd632449aca952` |
| Released `starlingmonkey_embedding.wasm` | `6094cd93d966f9bec9b01332db6e0eedbaf22f60b745c9f823f21e33cbd4d365` |
| `wasmtime-v42.0.1-aarch64-macos.tar.xz` | `69c56932453483f31cac7636f850bbd3bf884eaa7315b2c3b92857a2b0c6762e` |

The runtime verifies the exact Wasmtime version before invoking the component. The committed npm lockfile freezes resolved transitive dependencies for `npm ci`; npm installation scripts can fetch platform binaries, so CI should additionally verify platform-specific artifact hashes.
