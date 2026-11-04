# Future classic-stream component gates

These are **unexecuted component templates** for the coherent, unapplied
classic-stream candidate. No candidate engine has been admitted. All four actual
engine pins remain null in the parent candidate's preflight configuration. No
componentizer, native engine, guest, Wasmtime, or wasmCloud was executed for this
harness preparation.

The sole executed check is `node-oracle.mjs` under the exact Node v22.14.0
executable. It compares the immutable original 19 groups against their sealed
Node output, then compares the copied checks against the same output. It imports
only actual Node modules, not the candidate factory, reference kernel, or native
guest scheduler. `node-oracle-results.json` records all input hashes and the Node
executable hash. The result does not validate the classic implementation.

`checks.mjs` exports `async checks(stream, promises, Buffer)`. Its bytes are the
sealed `implementation-candidate-v1/checks.mjs` with exactly one replacement:

```js
// Original host-only lifetime wait:
await new Promise(resolve=>process.nextTick(resolve));
// Copied component-safe lifetime wait:
await promises.finished(source).catch(()=>{});
```

The replacement waits on the public completion contract after early async
iterator return. Its rejection is ignored because destruction is expected in
this case. No scheduler substitute, public process object, or microtask shim is
introduced. Identical output for these 19 groups does not establish identical
next-tick scheduling in the guest.

## Admission and future invocation

`run.mjs` imports the parent `runtime-preflight.mjs`, awaits
`classicPreflight({variant})`, and awaits its immutable `recheck()` before
dynamically importing the component driver. Thus null/unreviewed engine pins
must fail before componentizer or toolchain loading. The required preflight
result is `{enginePath, sourceRoot, metadata, pin, variant, recheck}`. The driver
uses no environment override to bypass that admission. It calls `recheck()`
around bundling, packaging, fixture execution, and failure vectors, including
its final return. Parent admission must bind the reviewed engine, source,
configuration, module selection, producer receipts, and these template sources.

The future entry point, **after separate approval and actual pin publication**,
is:

```sh
NODE_COMPAT_CLASSIC_VARIANT=normal-off \
NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock \
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
tests/node-compat/foundation-classic-streams/integration-candidate-v1/harness/run.mjs
```

`NODE_COMPAT_CLASSIC_OUTPUT` selects a new output directory. Artifacts use
exclusive writes so an old receipt is never silently overwritten. The current
preflight's null pins intentionally make this future command unavailable.

| Variant | Classic modules | GC stress | Entropy mode | Exact final WASI imports |
| --- | --- | --- | --- | --- |
| `normal-off` | Selected | Off | OFF | `[]` |
| `normal-runtime` | Selected | Off | RUNTIME_ONLY | `wasi:random/random@0.2.10` only |
| `gc-off` | Selected | On | OFF | `[]` |
| `disabled-off` | Unselected | Off | OFF | No component is packaged |

The runtime variant follows the existing capability policy, keeps the random
feature enabled, and selects the exact secure random interface. The repository
Preview1 adapter is pinned to SHA-256 `988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0`.
No WIT version string is rewritten. The runtime variant's random import is a
consequence of the selected engine entropy policy; classic algorithms themselves
request no host service. The OFF variants disable all five ComponentizeJS host
features. No filesystem, clock, HTTP, socket, DNS, process, or custom service is
selected.

The future ordinary host is the previously measured stock Wasmtime 42.0.1
macOS arm64 binary, SHA-256
`a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c`.
The driver verifies its bytes and version; it does not introduce a custom host.
Other platform binaries require their own reviewed pins. This template does not
perform wasmCloud deployment.

## Component fixture contract

`guest.mjs` imports real `node:stream`, `stream`, `node:stream/promises`, and
`stream/promises`. Literal CommonJS calls cover all four spellings and must be
lowered by the existing static CJS bundler contract to the matching default
bindings. There is no runtime public `require` and no candidate implementation
factory in the application bundle. The future candidate must first apply its
module-selection update; the live helper currently does not admit classic
streams. The driver fails if a candidate source/factory or a JavaScript builtin
adapter appears in the bundled module graph.

The WIT world exports only `run: func() -> string`. The driver checks final
interfaces and exports, rather than interpreting the application's JavaScript
imports as host capabilities. The exported JSON includes:

* The 19 ordinary groups, compared structurally to the exact sealed Node output.
* Exact 24/3 namespace keys; real ESM namespace shape, alias identity, callable
  Stream/default graph, existing EventEmitter ancestry, safe namespace inspection,
  static CJS/default identities, and `globalThis.Buffer === imported Buffer`.
* Both custom-promisify getter identities and descriptors, mutable default promise
  bindings, and independent named binding snapshots, with mutations restored.
* Forty-eight deferred call/construct results and 17 unsupported overload results,
  checking identifiable own error properties. `deferred-snippets.mjs` supplies the
  same 65 application-top-level failures plus a caught initialization control.
  Top-level errors must fail componentization; import-only success is insufficient.
  The packaging failure text is matched against the actual factory's operation
  and human message (`node:stream.<operation> is unavailable in
  sm-node-22.14.0-m0.12`). Its own `code` field is checked inside guest catches;
  Wizer error reporting is not assumed to print that field.
* Writable object-unit and readable chunk-count boundaries of 4096, plus the
  readable non-object byte-unit boundary of 16,777,216. Each failed stream is
  discarded. Atomic rollback and a bound on arbitrary application payload or
  total memory are not claimed.

Snapshot state consists of ordinary guest objects, an empty stream, default
HWM observations, and a Buffer created by the native hex entry point. The first
call pushes the retained token after resumption and verifies the stream returns
that same object. This does not test a chunk queued before the snapshot.
`snapshotIdentity` is `true` only on that first call and is `null` on subsequent
calls because the stream has been consumed and destroyed. Three calls on one generated
Jco instance check retained state; a separately instantiated Jco module and a
fresh Wasmtime invocation check reset-to-snapshot state. This explicitly observes
retention; it does not claim request cleanup or safe reuse after a failed export.

The rooting control retains a stream, chunk, callback, AbortSignal, protected
listener, and disposable across eight native hex decode/encode round trips,
then checks their identities and behavior. Only the separately reviewed
`gc-off` engine makes those existing native allocation boundaries perform stress
GC. No private GC export, allocation-fault hook, memory observer, or host clock
is introduced. The normal variants run the same control without claiming a
collection occurred. Source inspection alone does not prove moving-GC safety.

`deployed-fixtures.mjs` separately supplies a fatal export which calls
`stream.compose()`, plus caught and handled-later controls. The fatal fixture is
packaged without calling the deferred operation during initialization. Each
future Jco child and fresh Wasmtime process invokes it exactly once, requires
failure, and is discarded. No failed instance is called again. Generic host trap
text is not interpreted as an observable JavaScript own error code; the paired
clean guest controls inspect that code, module, operation, and profile directly.
Spawn errors, timeouts, and signal termination do not count as a passing negative
test.

The caught control runs successfully three times on its own retained instance.
The handled-later control queues the rejecting reaction first and attaches its
handler from a later Promise job in the same checkpoint, then also runs three
successful retained calls. Each has an additional fresh Wasmtime success check.
This tests eventual handling of a transient rejection, without wrapping
`Promise.then`, changing the guest scheduler, or claiming failed-instance reuse.
All future Node child and Wasmtime subprocess timeouts are 55 seconds.

`disabled-off` bundles each of the four module spellings through both ESM and
literal CJS and requires module-admission failure before componentizer selection.
The ESM inputs use `.mjs`; the valid CommonJS inputs use `.cjs` and
`module.exports = require(...)`, so an unrelated file-format refusal cannot
substitute for missing-module admission.
It does not run receiver-negative operations or instantiate a classic module.

## Still required before reporting a native milestone

Review and publish each actual artifact/source/build pin; keep the disabled
control unselected; apply the coherent producer/admission patch; and run the
ordinary Release gates before the separately pinned GC gate. Check emitted
imports against the table for every successful component, save the exact
componentizer/toolchain/host provenance and bundle graphs, and preserve all
failed-attempt evidence. The future results file must show actual counts and
observations; this directory's receipt records all component tests as unexecuted.

The current limit vectors do not cover every inherited Buffer/StringDecoder
limit or decoded UTF16-unit boundary. Add those targeted tests before broadening
that claim. Neither this candidate nor these templates claim complete Node
streams, Web/function-stage overloads, composition/operators/disposal support,
external I/O, timer propagation, AsyncLocalStorage, async_hooks, full reflection,
request teardown, or a performance improvement.

The original nine-file preparation is preserved byte-for-byte under
`history/v1/`; the following ten-file message-correction revision is preserved
under `history/v2/`. Those global Buffer identity and deployed error/control
additions are preserved in `history/v3/`. The current source receipt records the
following disabled-CJS file-format correction. The 19-group check body
and its executed Node oracle are unchanged; that oracle was not rerun for these
source-only changes.
