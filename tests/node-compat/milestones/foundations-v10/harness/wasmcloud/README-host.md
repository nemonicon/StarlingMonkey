# Native profile on unmodified wasmCloud 2.11.0

The native Buffer/explicit `child_process` profile passed three HTTP requests through the **official wasmCloud 2.11.0 `wash dev` host**, on 2026-11-03 Europe/Zurich. Each request executed 381 string cases and 250 byte cases against the pinned Node v22.14.0 oracle vectors, checked Buffer/global/CommonJS identity and unsupported methods, and verified nine unsupported calls plus nine constructions. The handler also returned the expected attributed errors for `spawn()` and `new ChildProcess()`.

See [host-results.json](host-results.json) for the full responses, exact commands, effective host configuration, component audit and hashes. The host listened only on `127.0.0.1:51523` for this run, then stopped after SIGINT with exit code 0. The recorded address is ephemeral; reproduction chooses another free loopback port. All component request counters were `1`, so **instance reuse was not established**.

This uses the released product's local development deployment workflow, not a custom Rust host or a linker harness. `wash dev` builds and starts `wash-runtime::Host` and deploys the component through the normal workload machinery. Its default HTTP router dispatches requests to the deployed workload. No source or binary changes to wasmCloud or Wasmtime were required. The release source pins Wasmtime `48.0.7`. [wasmCloud CLI implementation](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash/src/cli/dev.rs), [release dependency manifest](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/Cargo.toml)

| Artifact | Verified identity |
| --- | --- |
| wasmCloud source release | `v2.11.0`, commit `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff` |
| Official host binary | `wash-aarch64-apple-darwin`; SHA-256 `365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954` |
| Native ComponentizeJS engine | SHA-256 `da69618da72315c3b3f20d105708fd625a3b7c0691f49329201036c3c2fd5796` |
| HTTP test component | 18,190,456 bytes; SHA-256 `d32752b8f240d8edaa2f868469c4b788bd31da8cf0739230b7ed2884f3206f7f` |
| Node oracle/build driver | `v22.14.0` |

The runner downloads the [official binary](https://github.com/wasmCloud/wasmCloud/releases/download/v2.11.0/wash-aarch64-apple-darwin) into `/tmp` and checks its release digest. The user's installed `wash` binary and configuration remain unchanged. Linux and Intel macOS download identities are provided in the runner; this recorded execution was macOS arm64.

## Selected capabilities

The emitted component exports only `wasi:http/incoming-handler@0.2.10`. Its imports are exactly:

| Interface | Role |
| --- | --- |
| `wasi:http/types@0.2.10` | Incoming request and outgoing response resources. |
| `wasi:io/error@0.2.10` | I/O error resources. |
| `wasi:io/poll@0.2.10` | Pollable resources and I/O polling. |
| `wasi:io/streams@0.2.10` | Response output stream methods. |
| `wasi:clocks/monotonic-clock@0.2.10` | **Type-only:** `duration = u64`, required by HTTP request-options signatures. No clock function is imported. |

[type-audit.mjs](type-audit.mjs) decodes the component's type graph using pinned `wasm-tools 1.235.0` and requires that the clock interface has only the `duration` type, no functions and no core clock imports. The audited core imports use only the four executable interfaces above. The host runner independently inspects the final component with the official `wash inspect` command and compares imports/exports with the component audit before deployment.

No outgoing HTTP handler, socket, DNS, filesystem, CLI/environment, random, wall-clock, draft TLS, custom Node or wasmCloud interface is imported. The temporary project's effective configuration is checked with `wash config show` **before** starting the host: network, DNS and host-loopback allowlists are explicitly empty, with no volumes, custom host plugins, sidecars or workload configuration values. No Docker or NATS process/container was started. Default built-in host plugins remain part of the released binary; this component does not import them.

These checks establish the selected interface surface and the successful inbound HTTP execution. They do not test denied outgoing calls or provide a broader filesystem/network/process compatibility result.

## Guest packaging

ComponentizeJS 0.23.0's ordinary final feature pass stubs HTTP type methods when both HTTP and fetch-event features are disabled, even when the WIT world explicitly imports those methods. Enabling its ordinary HTTP feature preserves the needed methods but also retains outgoing HTTP. This is a guest packaging issue; the host remains unchanged.

[http-stubbing.mjs](http-stubbing.mjs) uses the pinned stock splicer's actual `stubWasi` API twice: first preserving HTTP types while stubbing outgoing HTTP, then stubbing clocks, entropy and stdio while retaining HTTP types and I/O. It hash-checks the exact ComponentizeJS JavaScript and splicer Wasm files, temporarily replaces one function in this build process, and restores that function afterward. The initial binding generation uses manual HTTP bindings with fetch-event disabled.

The final core contains no Preview1 imports, so it is wrapped with the existing `Jco componentNew(finalCore, [], false)` API and no adapter. A repository Preview1 adapter is supplied to the intermediate ComponentizeJS invocation, hashed and recorded, but is **not used in the final component**. No shared npm file, native engine, host or runtime was patched.

[componentize-http.patch](componentize-http.patch) is a proposed upstream source correction only. It was **not applied, compiled or used** for these results. The recorded workaround remains specific to the pinned ComponentizeJS release; migration requires repeating the import and execution checks.

## Reproduction

First build the custom engine using [build-engine.sh](../build-engine.sh), and install the portable pinned [npm toolchain](../toolchain/package.json) with its lockfile in an external directory. Use the exact Node v22.14.0 executable for each command:

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-npm-toolchain \
NODE_COMPAT_ENGINE=/path/to/starlingmonkey_embedding.wasm \
  /path/to/node-v22.14.0 tests/node-compat/wasmcloud/build-http.mjs

NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 tests/node-compat/wasmcloud/test-wasmtime-http.mjs

/path/to/node-v22.14.0 tests/node-compat/wasmcloud/run-host.mjs
```

The default component/audit paths are `/tmp/starling-node-compat/wasmcloud-http/native-profile-http.component.wasm` and `/tmp/starling-node-compat/wasmcloud-http/component-audit.json`. Override them with `NODE_COMPAT_HTTP_COMPONENT` and `NODE_COMPAT_HTTP_AUDIT`. `NODE_COMPAT_WASH` can select an existing official binary; its version and release digest must match and the runner will not modify it. `NODE_COMPAT_WASMCLOUD_OUTPUT` changes the external work/cache location, and `NODE_COMPAT_WASMCLOUD_RESULTS` changes the saved result file.

The host runner deploys an immutable per-run copy of the audited component, isolates CLI caches/configuration through XDG directories and an explicit empty user configuration, waits for actual HTTP success, validates three full reports and response headers, then stops its own host process. It uses HTTP readiness because noninteractive CLI INFO logs may be empty. All binaries and deployment directories stay outside the checkout.

The component contains the full oracle corpus, so its size is not a product size or a Buffer performance comparison. This validates the bounded native profile through standard WASI HTTP on the released local host. It does not establish general Node HTTP, complete Buffer support, Kubernetes/NATS deployment, HTTP instance reuse, AsyncLocalStorage propagation or untested capability semantics.
