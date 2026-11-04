# Isolated bounded Assert foundation proposal

This is an isolated guest-JS prototype. It does not install `node:assert`, select a native
module, change CMake, or replace Jco adapters. The pinned Node22.14 oracle passes
**55 differential groups** (including 784 comparisons over a 14×14 primitive
grid), plus **22 prototype-only deferred/mutation/inspection cases**.
[node-results.json](./node-results.json) records source hashes and exact results.
[component-results.json](./component-results.json) verifies the same vectors in a
real component: two retained Jco calls, one fresh stock Wasmtime42 call, five
initialization failures, zero imports, and exactly `run: func() -> string` exported.
This establishes bundled prototype behavior, not native module installation.

## Source findings

The inventory comes from the actual pinned Node22.14 executable's ESM namespace
and embedded sources; hashes are in
[inventory.node-v22.14.0.json](./inventory.node-v22.14.0.json). Both modules expose
exactly 22 names, including `partialDeepStrictEqual`, and exclude the newer
`Assert` class. Source references are pinned
[lib/assert.js](https://github.com/nodejs/node/blob/v22.14.0/lib/assert.js),
[strict.js](https://github.com/nodejs/node/blob/v22.14.0/lib/assert/strict.js),
[AssertionError](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/assert/assertion_error.js)
and [innerOk](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/assert/utils.js).
The [pinned Node tests](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-assert.js)
were inspected for simple assertions, thrown-message identity, matcher behavior,
and error propagation; the full upstream suite has not run against this subset.

The actual graph is `root.default === root.ok`, `root.strict === strict.default`,
`strict.default.strict === strict.default`, and `strict.ok === root.ok`.
Strict `equal/notEqual/deepEqual/notDeepEqual` are the same function references as
root `strictEqual/notStrictEqual/deepStrictEqual/notDeepStrictEqual`. Each default
initially points to its named functions. Subsequent reassignment of a default's
property does not rewrite captured ESM bindings. Strict and root defaults are
different callable objects; no module is a universal Proxy or an accidental
thenable. [strict.mjs](./strict.mjs) declares all 22 exports explicitly.

The first real component exposed SpiderMonkey's lazy function-property creation:
the three ordinary `length/name/prototype` properties appeared after assigned
methods. [The rejected result](./rejected-lazy-order-results.json) and
[exact rejected source](./rejected-prototype-lazy-order.mjs) retain that evidence;
the other 54 differential groups and all 22 profile cases passed in that proposal.
The current prototype explicitly defines those ordinary descriptors in Node's
order before assigning methods. This preserves descriptor types and callable
identity while matching the observed own-property order after snapshotting.

[source-audit.json](./source-audit.json) hashes the existing locked implementations.
Jco 1.40.0's `createAssertBuiltin`/`assertAdapter` wraps Jco-std's Node 24 adapter and
includes `Assert`, so its export list cannot be used unchanged for Node22.
Unenv 2.0.0-rc.24's `isDeepEqual/isDeepStrictEqual` use JSON serialization, and its
Node error-code constructors alias generic `Error`; this prototype reuses neither.
The published locked trees expose `node:test`'s assertion helper but do not ship a
dedicated Assert adapter conformance suite in the inspected files.

The locked readable-stream 4.7.0 `lib` tree imports no Assert module. Its
`lib/ours/errors.js::assert` is a private helper used to validate internal error
formatting. This module is useful to applications/tests, but is not a demonstrated
readable-stream runtime blocker.

## Proposed contract

[The versioned manifest](./export-manifest.assert.node-v22.14.0.json) defines both
module names, future bare aliases, exports, support and deviations. This is an
isolated contract version; no production profile version is advanced.

| API | Proposal status | Validation |
| --- | --- | --- |
| `ok/default`, `strict` callable | Truthiness; missing argument; successful messages unread; failed Error message identity | Node oracle |
| `equal/notEqual` | JavaScript loose comparison plus Node's NaN case | Primitive grid and coercion vector |
| `strictEqual/notStrictEqual` | SameValue, including NaN and signed zero | Grid/reference/signed-zero vectors |
| `fail` | Zero or one argument, including null and Error identity | Node oracle |
| `throws/doesNotThrow` | Ordinary constructors/classes, predicates returning exactly true, native RegExp, primitive thrown values | Callback/matcher order, rethrow identity, lastIndex |
| `match/doesNotMatch` | Native RegExp brand/exec; input validation and AssertionError fields | Node oracle; overridden exec ignored |
| `ifError` | Null/undefined pass; all other values produce AssertionError retaining actual | Node oracle for fields |
| `AssertionError` | Same-realm Error subclass; ordinary options; meaningful fields and code | Node oracle; reference retention |
| Five deep equality functions | Deferred | Call and construct throw identifiable error |
| `rejects/doesNotReject` | Deferred | Call and construct throw synchronously; no fake Promise |
| `CallTracker` | Deferred, callable name/arity match pinned deprecated wrapper | Call and construct throw |
| Legacy `fail`, validation-object matchers, `AssertionError.details` | Deferred | Typed invocation errors |

Deferred operations throw `TypeError` with `code='ERR_SM_NODE_UNSUPPORTED'` and
`operation`; the message also contains the code so componentization diagnostics
can identify the failure. They cannot silently succeed at initialization.
A successful `doesNotThrow` does not consult an unused matcher, as Node does.
The five deep operations remain deferred even for superficially easy operands;
there is no JSON-based equality shortcut.

Messages are intentionally simpler: no V8 source-expression extraction, source
file reads, rich diff, color, custom inspector, or exact stack trimming.
Automatic diagnostics render objects opaquely and retain actual/expected by
reference. This changes diagnostic getter/inspection side effects relative to
Node, particularly `ifError`. Supplied ordinary Error messages are rethrown by
identity for `ok`, equality, `fail` and `match`; an unmatched `throws` matcher
renders its message, as Node does. Same-realm native errors are the supported boundary. Cross-realm
native-error detection, proxy impersonation, `details`, stack-start options,
custom diff decoration and native inspection helpers remain outside the claim.
String coercions required by loose equality, explicit diagnostic messages, and
RegExp exception matching still run application code as ordinary JS semantics.

Primordials used by the facade are captured at initialization. Mutating public
default properties is supported without making them privileged backdoors.
Regex matching preserves native `lastIndex`; this does not promise bounded
regex runtime. There are no profile-specific size or recursion limits yet.

## Lifecycle, build and next gates

The facade owns only ordinary GC-traced JS objects/functions and has no native
borrowed byte spans, allocator transfers, live handles, entropy, clocks, process
state, or host interfaces. Named/default relationships may be created during
snapshot initialization and remain shared in a reused component; there is no
request-associated state. Async rejection helpers are deferred until scheduler,
unhandled rejection and future AsyncLocalStorage propagation policies are tested.
A small JS semantic facade is appropriate here; native byte/compute machinery
would add complexity without a measured benefit for these simple checks.

Run the small source/oracle checks with the pinned executable:

```sh
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/foundation-assert/audit-sources.mjs
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/foundation-assert/run-node.mjs
```

[run-component.mjs](./run-component.mjs) uses the existing
audited profile bundler/componentizer. It validates frozen engine source hashes,
requires an ordinary Release entropy-OFF engine, selects the pinned preview1
adapter and a pure scalar WIT world, requests no interfaces, and audits zero
emitted imports and exact final WIT exports. It passed two retained Jco calls plus fresh stock Wasmtime42,
snapshot namespace identity, all oracle/profile vectors, and five failures from
application top-level code, including a deferred microtask. It writes a separate
component result only after those checks pass. No host services are added.

The verified run uses the v4 OFF engine `347025c9641820c50206a9b6dee3f5e0a60b4d40c326e5c3ca66853c44fa5087`
and all 271 frozen source inputs. The report includes complete engine metadata,
adapter/componentizer provenance, fixture hashes, final WIT and the stock
Wasmtime42 executable hash. Retained call counters are `[1,2]`; the fresh process
returns `1`. The test component includes the corpus and is not a size or speed
comparison with another implementation.

To reproduce, run the harness with `NODE_COMPAT_ENGINE`,
`NODE_COMPAT_ENGINE_SOURCE_ROOT`, `NODE_COMPAT_TOOLCHAIN`,
`NODE_COMPAT_COMPONENTIZE_MODULE`, `NODE_COMPAT_WASMTIME` and optional
`NODE_COMPAT_ASSERT_OUTPUT`. Before optional native registration, decide the exact
diagnostic subset and usefulness of deep comparison/async helpers. A later native
integration must add separate finite factories/manifests via existing extension
mechanisms, bundler external selection, real module-cache/alias tests, explicit
CommonJS lowering tests, an Assert-OFF admission control, and a standard HTTP
target-host gate. Those integration claims are not established by this bundled
prototype report.
