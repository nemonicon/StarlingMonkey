# Combined candidate validation

The optimized facade and isolated scalar-unsigned ABI fix were validated together
on 2026-11-03. These records supplement the independent allocation
[investigation](README-probes.md) and matched before/after measurements; no
reference facade or JavaScript replacement hex kernel entered these components.

| Engine | SHA-256 |
| --- | --- |
| Combined release | `3f5bf602ad2d1507db5c1bcd5b938984aba9ca65af4c5a840b5bf8fcd09d370f` |
| Combined GC stress | `10d1c0e696deb43989d3b8005bda230c4fd6d603856a886883e0d94ee37fb779` |

Both engines passed the original 381 string and 250 byte cases, all nine stub
calls/constructions, four expected initialization failures, raw bare/prefixed
imports, dynamic ESM imports and caching checks. They ran twice in the same
Jco-instantiated component and directly on unmodified Wasmtime 42.0.1. Their
semantic components import zero host interfaces.

`intrinsics-checks.mjs` additionally ran against the **actual installed module**
after snapshot resumption. It checked sizes 0, 1, 63, 64, 65, 255, 256 and 4096;
on-demand backing-buffer identity; copied versus shared views; map/filter
species; prototype, wrong-typed-array and proxy spoofs; four throwing public input
property shadows; resizable/detached inputs; and numeric/non-numeric species
entry policy. Public TextEncoder/Decoder methods, Uint8Array fill, WeakSet add/has
and Object.setPrototypeOf were replaced temporarily. Their replacement-call
counter remained **zero**, and private-brand checks stayed correct. Every
replacement was restored before returning. The tests do not claim immunity to
arbitrary changes to every JavaScript intrinsic.

The same candidate HTTP component ran those additional checks on every request
through both unmodified target hosts:

- Wasmtime 42.0.1: three successful requests.
- Official wasmCloud `wash dev` 2.11.0, embedding Wasmtime 48.0.7: three successful
  requests, followed by clean shutdown.

The identical HTTP artifact was used on both hosts:
`6d89f735849d74b0af1ba42f2db814cf539a8199d71f172021cb21a3f1d03897`
(18,268,644 bytes, including the test corpus). Its imports are exactly HTTP
types, I/O error/poll/streams, and the monotonic-clock **duration-only** interface,
all at 0.2.10. The actual type graph has no clock functions and the core has no
clock or Preview1 imports. No outgoing handler or custom service was added.
Both hosts reported handler/core counters of one on every request. Same-instance
HTTP reuse and general request isolation remain unproven.

The official host binary SHA is
`365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954`.
Its local development route used loopback, isolated configuration, denied egress
and DNS grants, and no volumes/plugins/sidecars. This verifies that supported
local host workflow, not a Kubernetes/NATS cluster deployment.

Evidence is preserved separately from all earlier baseline records:

- [Combined acceptance record](candidate-validation-results.json) verifies the
  native reports, candidate engine hashes and identical cross-host artifact.
- [HTTP component audit](candidate-component-audit.json) records exact imports,
  structural duration proof and pinned guest packaging composition.
- [Wasmtime HTTP requests](candidate-wasmtime-http-results.json) and
  [wasmCloud HTTP requests](candidate-host-results.json) retain full response
  bodies, targeted-check fields, actual commands and process shutdown evidence.

## Reproduce

Use the pinned Node v22.14.0, npm toolchain and candidate engines with matching
adjacent metadata. All generated binaries/logs remain in a new external output
tree, default `/tmp/starling-node-compat/optimization`.

```sh
NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
NODE_COMPAT_CANDIDATE_ENGINE=/path/to/candidate.release.wasm \
NODE_COMPAT_CANDIDATE_STRESS_ENGINE=/path/to/candidate.gc-stress.wasm \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
NODE_COMPAT_WASM_TOOLS=/path/to/wasm-tools-1.235.0 \
NODE_COMPAT_WASH=/path/to/official-wash-2.11.0 \
  /path/to/node-v22.14.0 tests/node-compat/optimization/validate-candidate.mjs
```

`--collect-only` verifies existing completed runs and rebuilds the combined JSON
without executing components. `NODE_COMPAT_OPTIMIZATION_OUTPUT` selects another
external tree. The wrapper supplies candidate entry points and distinct output
paths explicitly; it does not overwrite historical `host-results.json` or
baseline engine/component artifacts. Engine source manifests, bundle imports and
component hashes remain gated by the underlying runners.

SharedArrayBuffer construction is not exposed by these guest engines, so those
guest cases are explicitly skipped; the separate Node semantic test covers the
rejection policy. Cross-realm creation is likewise not exposed by the production
component API. Rooted-boundary GC stress passed, but exhaustive OOM injection,
full GC zeal, AsyncLocalStorage and concurrent request isolation remain outside
these acceptance results. Artifact byte counts are not product-size or
whole-application performance claims.
