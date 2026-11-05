The optional production-package bundler now gets real React19.3.1 and nested
CommonJS/native-builtin dependencies into capability-free components. Full
Next.js and ReactDOM rendering remain incomplete. The accepted finite profile
bundler and foundations-v13 native engine are unchanged.

The [fresh post-push v2 run](results-post-push-v2/results.json), executed after
commit `d8034839`, repeats all ten cases with the corrected Node subpath controls.
It exits 0 for complete observations and its three required positives: native
CommonJS identity, supported modules and real React elements. All 17 parent
commands finish cleanly. Four real components are emitted with no imports.
ReactDOM edge again fails on both hosts; its fresh component is 15,685,263 bytes
and the retained Wasmtime stack starts at `subscribe-instant`. NextRequest and
NextResponse succeed on Node, while `headers()` correctly throws outside a request
scope. The six bundling refusals below remain unchanged. This run reuses the exact
locked application already built and HTTP/browser-tested by the comprehensive
Next fixture; it does not repeat or reinterpret those Node-only controls.

A [genuine fresh replay](results-post-push-v2-replay/results.json) also completes
all ten observations. Its [actual comparison](results-post-push-v2-replay/comparison.json)
exits 0 with no regressions, improvements or changed blockers and all seven guest
failures retained. The comparator passes [40 injected cases](results-post-push-v2/comparator-self-tests.json),
including changed trap diagnostics, missing fixtures/oracles, return mismatches,
interface widening and relocation of unchanged source identities.

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

A separate explicitly selected standard-clock component now returns the complete
Node-equal ReactDOM edge result on both execution paths: three retained Jco
calls, one fresh Jco call and three fresh Wasmtime calls finish raw0. The
[actual Root records](../../foundation-scheduler/clock-v13-runtime-v2-root-results.json)
cover the unchanged v13 native engine and retained bundle, with only the three
standard clocks/poll interfaces at0.2.10. [Independent actual-result review](../../foundation-scheduler/independent-clock-v13-runtime-v2-results-review-v2/results.json)
passes. The original pure-profile failures above stay unchanged; broader
clock/resource/snapshot/teardown and full Next gates remain open.

[check-clock-render.mjs](check-clock-render.mjs) is a separate read-only checker
for that pinned experimental generation:

```sh
node tests/node-compat/frameworks/package-bundler-execution-v1/check-clock-render.mjs \
  /private/tmp/starling-node-compat/clock-v13-runtime-v2 \
  tests/node-compat/foundation-scheduler/clock-v13-runtime-v2-root-results.json \
  --self-test
```

It verifies the complete publication hashes, seven raw/decoded Node-equal values,
five inner terminals and recorded native/interface scope. The argument can name
a complete relocated copy; original metadata contents remain unchanged. It does
not execute a component or re-audit its type graph, external native inputs or
outer process provenance. Eighteen injected semantic changes and two separate
publication-integrity negatives are rejected. A changed source/component pin
needs a new reviewed baseline. The ten-case comparator remains unchanged.

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

node tests/node-compat/frameworks/package-bundler-execution-v1/check-components.mjs \
  tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2/results.json \
  /private/tmp/package-components-evidence/results.json
```

The application is the real locked project produced by the
[Next.js runner](../nextjs/README.md). Override engine/source/tool paths only with
genuine pinned artifacts. The matrix passes its three required positive cases
while retaining every later failure; exit0 is not a Next compatibility claim.
Its initial v2 driver default-argument error occurred before any worker/output
creation and is preserved under `preparation-history-v2`.

The [matrix comparator](check-components.mjs) reads retained evidence relative to
each `results.json`, including all three Jco returns, fresh Wasmtime values,
recorded interface scope and command terminals. Exit 0 means no regression or
changed blocker; the seven known guest failures remain visible. Exit 1 means
missing/inconsistent evidence, regression or incompatible pins, and exit 2 means
a changed blocker needs review. Run its injected checks with `--self-test`.
The exact Node/bundler/engine/Wasmtime identities are checked from recorded fields;
the matrix alone has no installed Next/React version record. Use the locked
application produced by the full Next runner, which verifies those versions.
This metadata/evidence comparison does not reinstantiate components or establish
unrecorded runtime behavior. Use the separate Next runner/comparator for the full
HTTP/browser baseline. `nextjs/run.mjs` uses the original profile path; optional
bundler checks require this matrix's explicit `--bundler packages-v2` selection.

All emitted application components select no host interfaces. Their engine,
metadata, source inputs, component hashes, WIT, whole typed results, raw process
streams and cleanup observations are recorded. Large components/cores and npm
dependencies remain external at their descriptors. Archived executed-source
copies are byte evidence, not relocated runnable helper contexts. No new native
profile, request reuse, GC/secret-erasure, performance or secondary-host claim
follows from this experiment.
