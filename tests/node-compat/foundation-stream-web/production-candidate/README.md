# Uninstalled stream/web m0.9 production candidate

This directory prepares a concrete integration result for review. **No builtin,
option, shared generator, registration, module selection or production native
source is changed.** Profile `sm-node-22.14.0-m0.9` is reserved for this optional
module; m0.8 remains the separate core allocation milestone.

The [schema-valid manifest](export-manifest.stream-web.node-v22.14.0.json)
contains exactly seventeen named exports plus default for `node:stream/web`,
with alias `stream/web` and no required host interface. The
[explicit ESM template](stream-web.mjs) declares real finite bindings; its
private record import is an **uninstalled internal guest binding**, not a host
interface, existing embedding API or publicly available module. The ordinary
mutable default object initially shares named identities; later default-object
mutation does not synchronize named bindings. Literal CommonJS lowering to that
default object is the proposed existing bundler contract, not an executed new
module-resolution test in this directory.

The [single-argument factory](factory.mjs) composes native-bulk UTF8 codec
facades, serialized readable iteration and the DataView view adapter. The
sixteen-key native record contract is unchanged from the preceding stage.
There are no temporary stream constructions in the factory or native capture
proposal. Constructor/prototype identities remain native for the thirteen
reused stream/strategy classes. The two new codec names remain module exports,
without adding global names.

[codecs.mjs](codecs.mjs) derives from the preserved codec stage, adding own
error/metadata properties through captured defineProperty and null-prototype
descriptors. The private class record has a null prototype. Intermediate BYOB
and deferred-iteration writes and their unused captures are removed: the
composed installation replaces each of eight descriptors once. Native codec
algorithms, limits and supported overloads are unchanged.
[derivation.json](derivation.json) records the exact input/output hashes.

The candidate deliberately retains these boundaries:

- UTF8 decoder only; fixed, attached, unshared BufferSources. Encoder uses
  String(chunk), including Symbol, and retains one trailing high surrogate.
  Incoming source/input caps are 1 Mi UTF16 units and 16 MiB respectively.
- BYOB default/null/min1 and ordinary local fixed unshared views, with a
  16 MiB per-view cap. DataView maps through a Uint8Array over the same backing,
  then through the returned moved backing; no explicit byte copy is added.
  Minimum-fill greater than one, Proxy receivers, modified layout,
  subclass/cross-realm views and shared/resizable backing remain unavailable.
- Readable from uses async protocol preference, async-from-sync semantics and
  HWM0. Values/async iterator serialize calls, manage reader locks, support
  preventCancel and preserve source/cancel reason identities. There is no
  lifetime/queue-size cap or immunity to every mutated promise/protocol method.
- Compression/decompression are explicit deferred functions, on both call and
  construction. No native compression constructors are retained or invoked.
  Writable controller signal is missing. Retained native constructor arity and
  error codes have recorded differences; a released BYOB reader lacks Node's
  ERR_INVALID_STATE. Source TypeErrors are not relabeled by message parsing.
- Transform controller guards reject its uninitialized prototype before native
  delegation. The real native receiver patch remains unapplied and must be
  compiled and tested before production exposure.

These are per-operation limits, not limits on application-retained output,
unbounded producer lifetimes or the number of queued iterator calls. Buffer
validation can materialize inline typed-array backing. No throughput,
zero-copy, complete stream parity or allocation-failure guarantee is claimed.

## Reproducible candidate generation and checks

`generate-factory.mjs` uses only Node standard modules and the existing manifest
validator. It emits the checked-in self-contained strict
`kStreamWebFactorySource` header without npm or a bundler at normal build time.
It rejects unexpected imports/exports, validates exact ESM/manifest agreement
and checks raw-string delimiter collisions. This generator is not wired into
the shared production generator.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/production-candidate/generate-factory.mjs --check
/path/to/node-v22.14.0 --experimental-vm-modules tests/node-compat/foundation-stream-web/production-candidate/check-header-and-esm.mjs
python3 tests/node-compat/foundation-stream-web/production-candidate/check-native-capture-syntax.py
```

[Host header/ESM results](header-esm-results.json) run the emitted literal as a
strict vm.Script, matching native strict compilation, and run the real ESM
bindings with a deployed host fixture supplying the private guest record.
Both execute the recorded 41 constructor, 250 codec, 67 iteration and 26
DataView Node cases, restore all descriptors and preserve native identities.
ESM namespace inspection, named/default snapshot behavior and an actual
top-level compression failure pass. This does not snapshot temporary streams
or verify native module registration.

The [native capture source](native-kernel.UNLINKED.cpp) is byte-identical to
the reviewed public-API template. [Syntax results](native-capture-syntax-results.json)
use the actual LLVM21.1.4/wasi-sdk30 compiler, SM147 headers and immutable v6
source overlay. It **passes syntax-only; it is unlinked, uninstalled and not
runtime-verified**. Runtime JS_GetClassObject identities and the actual
JS::IsReadableStreamBYOBReader callback remain gates. The earlier native
Transform-controller patch has a separate syntax-only receipt and remains
unapplied.

## Composed component proof and remaining integration

[Composed results](../composed/component-results.json) retain all 285 native
input hashes, candidate source hashes, selected patched packager and final
zero-import audit. The fixture component
`5537d66545049f8faa8c9e95b5ddf9b060890bb09359dc573253ae5a00765ce2`
is 13,551,802 bytes including oracles. Two Jco-hosted Wasm calls and fresh stock
Wasmtime42.0.1 pass the combined 41 constructor, 250 codec, four cancellation,
24 guard, twelve view, six controller, 67 iteration and 26 DataView cases;
sixteen plus six policy checks; three captured-operation groups; and ten
own-error checks. The three guard policy differences and released-reader code
gap remain explicit. Shared input rejections are checked in Node only because
SharedArrayBuffer is absent from this guest. Fixture reader branding is not
general native/cross-realm proof.

The initial composed Node log is preserved externally: native Node22 fatal
decode aborted when Error.prototype.code had a throwing setter. That known
combination is not repeated. Final checks test pure JavaScript error creation
inside the inherited-accessor window and native fatal decoding after restoring
it; no native crash equivalence, fault recovery or performance claim follows.

Proposed next integration is a **default-OFF NODE_COMPAT_STREAM_WEB** selection
on the existing core builtin, with builtin_web_streams and builtin_web_text_codec
prerequisites and the source-root include directory for the capture kernel.
The content realm must be current and returned native records rooted. Actual
initializer order follows add_builtin declaration order, not add_dependencies
topology; missing prerequisite prototype roots must fail closed. Production
selection should evaluate this strict factory only when the feature is enabled
and admit only the versioned finite manifest. It needs no new host capability.

Before declaring installed support: compile/link the capture and native receiver
guard; test actual brands, identities, invalid receivers and initializers on the
new engine; add manifest/hash/observed-flag admission; run ESM aliases/cache,
literal CommonJS and top-level componentization failures; and repeat native and
joint HTTP suites on both target hosts. Root owns those shared changes.

[Source pins](source-pins.json) retain the frozen candidate hashes, parent
proofs and Node MIT attribution. Earlier 11-case audit, constructor receipts,
failed DataView control and accepted individual stage receipts remain intact.

## Prepared installed-native runners (unexecuted)

[prepared-native-runners.json](prepared-native-runners.json) separately pins the
new test harness. **Only parsing has been checked; neither runner has been
componentized or executed.** The earlier source-stage component/header receipts
remain unchanged. Root must first link the actual native capture, corrected
controller guard, feature selection and admission support.

`run-native-component.mjs` requires streamWebEnabled true, observed
NODE_COMPAT_STREAM_WEB=ON, a Release entropy-OFF engine, all actual native input
hashes, the exact corrected decoder/controller files, native capture source,
selected manifest and strict generated factory literal. It rejects old engines
before packaging. The planned test uses real external node:stream/web and bare
imports plus selected literal CommonJS; no factory or registry is bundled.
It covers the full public corpus, actual reader brands, ten global and three
hidden native constructor identities, immutable named/default bindings,
snapshot-created pure state, repeated component reuse, uncached dynamic alias
loading and seven top-level deferred/unknown-export failures. Fourteen public
policy and nine own-error checks omit only the private factory-record cases,
which are not application APIs and retain their prior source-stage proof.

`run-native-controller-off.mjs` requires the same exact corrected native guard
sources with streamWebEnabled false and observed NODE_COMPAT_STREAM_WEB=OFF.
It verifies that the four controller operations are actual native functions,
then tests the guarded prototype, sixteen other ordinary invalid receiver calls
and valid closed/errored states. This independently exercises native C++ without
the ON profile's Node-facing wrappers. Native WrongReceiver errors lack the
Node code; the ON wrappers retain ERR_INVALID_THIS rather than losing it.
The temporary ordinary streams used to observe retained constructors are
created and cleaned up only during deployed run, never to initialize a factory.

The fail-closed [preflight contract](native-preflight-contract.json) records the
known candidate hashes for future promotion. Purposeful integration source
changes require a new reviewed contract/receipt; the runner provides no bypass.
Generated bookkeeping outside the evaluated factory literal may change without
changing the literal pin. Both future runners select an empty standard-interface
list and audit zero emitted imports. Their planned commands are intentionally
not executed against the existing engine:

```sh
# Future corrected ON engine + immutable sourceRoot + locked toolchain/v2
# packager/Wasmtime42 environment required by native-preflight.mjs.
NODE_COMPAT_STREAM_WEB_OUTPUT=/path/to/fresh-on-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/production-candidate/run-native-component.mjs
# Repeat with the same corrected source built STREAM_WEB=OFF.
NODE_COMPAT_STREAM_GUARD_OFF_OUTPUT=/path/to/fresh-off-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/production-candidate/run-native-controller-off.mjs
```
