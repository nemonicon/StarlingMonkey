The optional production-package bundler now gets real React19.3.1 and nested
CommonJS/native-builtin dependencies into capability-free components. Full
Next.js and ReactDOM rendering remain incomplete. The accepted finite profile
bundler and foundations-v13 native engine are unchanged.

The [v2 component matrix](results-component-matrix-v2/results.json) executes ten
actual application/library inputs with the new `packages-v2` selection:

| Input | Observed result |
| --- | --- |
| Nested CommonJS requiring bare/prefixed Buffer, Streams and Events | Pass: actual native default objects and constructors retain identity; no extra namespace default |
| Supported Buffer/foundations/web/classic-stream fixture | Pass: complete Node, three retained Jco and fresh Wasmtime values match |
| Real React element creation | Pass: complete Node/Jco/Wasmtime result matches |
| Real `react-dom/server.edge` renderer | Bundles and builds a zero-import 15,685,392-byte component; execution traps on both Jco and Wasmtime, with `subscribe-instant` in the retained stack |
| ReactDOM Node string renderer | Refuses the unselected `async_hooks` module |
| Next request/response and headers libraries | Still refuse unsupported loader/environment/native dependencies; see exact per-case logs |
| Genuine generated standalone/page/route entries | Remain refused; no full Next HTTP component is produced |

ReactDOM's actual production `startWork` calls `setTimeout(..., 0)`. The named
clock-subscription trap in the zero-capability test therefore motivates the
separate explicit standard-clock profile; no timer shim or extra import is
silently supplied. A selected-clock component still needs its own construction,
snapshot and both-host runtime tests. The [previous v1 matrix](results-component-matrix/results.json)
and [v1 Source HOLD](../package-bundler-implementation-review-v1/README.md)
remain unchanged.

The two initial direct Node controls for `next/server` and `next/headers` hit
Node ESM's extensionless-subpath resolution error. The
[corrected controls](node-library-controls.json) resolve the real CJS entry with
Node's `createRequire`: NextRequest/NextResponse succeed, while `headers()`
correctly reports a missing request scope. The runner now uses those same
resolved `.js` entries for its ESM control bindings. Original observations and
all guest results are unchanged; the resolver error is not a Next runtime result.

V2 uses the pinned Rolldown1.2.16 CommonJS machinery and official
`esmExternalRequirePlugin`. It canonicalizes native aliases before that plugin
and lets the plugin own its externals. Marking them external earlier leaves an
unusable runtime `require`; injecting ESM imports into `.cjs` fails parsing.
The [API/toy audit](../package-bundler-v1/README.md) records those counterexamples.

The [28 actual host differential/refusal cases](results-host-v2/results.json)
pass. V2 also uses a [tested lexical binding helper](../package-bundler-bindings-v2/README.md)
and finite recognition of `typeof`/if/and/or conditional presence guards. React's
optional `process.emit` branch remains ordinary, unmodified JavaScript. No
process object, runtime require, filesystem filename binding or Node host service
is provided. Local parameters named `process`/`global` are respected. The
[bounded v2 Source review](../package-bundler-v2-source-review/results.json)
passes its 45 expected host-only outcomes; its initial error-classification
mistake is retained separately from the corrected DATA interpretation.

This is a bundler interoperability contract. Ordinary mutable CommonJS named
imports can remain live in Rolldown while Node exposes snapshots; no general
Node loader or named-binding parity is claimed. Unknown dynamic requires,
loader aliases, unsupported native modules, residual dynamic imports and builtin
JS adapters refuse. Reflective JavaScript property access is not an exhaustive
static alias analysis or a supplied Node API. Logical transform-input hashes
are not a complete physical dependency/package-resolution closure. Generated
facade source is identified separately from filesystem modules. The complete
emitted chunk and actual component WIT/returns are retained.

Reproduce with Node22.14.0 and the pinned existing toolchain/engine:

```sh
NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/toolchain \
  node tests/node-compat/frameworks/package-bundler-execution-v1/host-test-v2.mjs \
  /private/tmp/package-host-fresh

node tests/node-compat/frameworks/package-bundler-execution-v1/run-components.mjs \
  --bundler packages-v2 \
  --application /private/tmp/starling-node-compat/nextjs-16.4.5-v13-run-20261105-02/application \
  --output /private/tmp/package-components-fresh \
  --record /private/tmp/package-components-evidence
```

The application is the real locked project produced by the
[Next.js runner](../nextjs/README.md). Override engine/source/tool paths only with
genuine pinned artifacts. The matrix passes its three required positive cases
while retaining every later failure; exit0 is not a Next compatibility claim.
Its initial v2 driver default-argument error occurred before any worker/output
creation and is preserved under `preparation-history-v2`.

All emitted application components select no host interfaces. Their engine,
metadata, source inputs, component hashes, WIT, whole typed results, raw process
streams and cleanup observations are recorded. Large components/cores and npm
dependencies remain external at their descriptors. Archived executed-source
copies are byte evidence, not relocated runnable helper contexts. No new native
profile, request reuse, GC/secret-erasure, performance or secondary-host claim
follows from this experiment.
