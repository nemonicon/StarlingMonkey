# Isolated bounded Querystring foundation

This prototype passes **32 differential groups**, including **210 delimiter
combinations** and **1,536 malformed-byte/BOM vectors**, plus **11 profile checks**
on pinned Node22.14 and in a real v5 component. The component uses the actual
native guest `node:buffer`; Querystring remains bundled guest JS. No production
registration, CMake changes, new globals or host capabilities were added.
This is a partial Querystring proposal, not complete Node compatibility.

[node-results.json](./node-results.json),
[component-results.json](./component-results.json) and
[source-audit.json](./source-audit.json) distinguish oracle, component and source
evidence. All accepted Assert/Events/joint HTTP records remain untouched.

## Pinned source and existing implementations

The exact Node inventory comes from the pinned executable and embedded
`querystring`/`internal/querystring` sources; their hashes are in
[inventory.node-v22.14.0.json](./inventory.node-v22.14.0.json).
Primary references are pinned
[lib/querystring.js](https://github.com/nodejs/node/blob/v22.14.0/lib/querystring.js),
[internal/querystring.js](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/querystring.js)
and [test-querystring.js](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-querystring.js).
The upstream tests were inspected for prototype-name keys, delimiters, arrays,
empty segments, primitive stringification and malformed escapes. The complete
upstream suite has not been run against this profile.

Jco1.40.0 `querystringAdapter` force-imports `UNENV_BUFFER_CORE` then reexports
unenv. Unenv2.0.0-rc.24 contains Node22.7-derived scanner/parser code, but its
local-function calls do not reproduce all pinned mutable default-object hooks.
No Jco-std Querystring implementation or dedicated adapter conformance suite was
found in the inspected published trees. The locked readable-stream4.7 `lib` tree
does not directly import Querystring, so this is not a proven streams blocker.

The native URL path is not a substitute. `crates/rust-url/src/lib.rs::params_init`
strips a leading `?` and uses `form_urlencoded::parse`; Querystring retains it as
part of a key. Serialization, space encoding and malformed input also differ.
The existing URLSearchParams tests cover coercion/atomic mutation and TextDecoder
tests cover option dictionaries; neither establishes Querystring semantics.
Their exact source hashes are recorded in the audit.

`runtime/engine.cpp` installs SpiderMonkey standard classes via
`JS::InitRealmStandardClasses`, so URI intrinsics require no external service.
`builtins/node-compat/buffer-facade.mjs::createBufferModule` already captures
native `TextDecoder('utf-8', {ignoreBOM:true})`; the proposal reuses that path for
replacement decoding rather than implementing a second UTF-8 decoder.

## Exact exports and supported boundary

[The finite draft manifest](./export-manifest.querystring.node-v22.14.0.json)
declares canonical `node:querystring`, proposed bare alias `querystring`, and
exactly eight ESM names. It is an isolated proposal format/version, not a newly
selected production manifest or a claim of validation against the stricter
production manifest schema. Production version/schema adaptation is a later gate.

| Export | Pinned function name/arity | Contract in this prototype |
| --- | --- | --- |
| `default` | ordinary object | Seven initial methods; same references as named exports |
| `parse`, `decode` | `parse`,4 | Same function; null-prototype results, duplicate aggregation, custom delimiters/decoder and maxKeys |
| `stringify`, `encode` | `stringify`,4 | Same function; own enumerable string keys, primitive conversion, arrays and custom encoder |
| `escape` | `qsEscape`,1 | Native URI fast path plus exact legacy surrogate repair/error behavior |
| `unescape` | `qsUnescape`,2 | Native URI fast path; byte fallback when it fails |
| `unescapeBuffer` | `unescapeBuffer`,2 | Genuine Buffer bytes for primitive string input |

Default owns `unescapeBuffer,unescape,escape,stringify,encode,parse,decode` in that
order, with an ordinary Object prototype. Named bindings capture initial methods;
reassigning default properties does not rewrite them. Parser/stringifier still
consult mutable default hooks as Node does. Safe initial namespace/default reads
have no fabricated `then` or universal Proxy. The JavaScript globals `escape` and
`unescape` are different legacy APIs and are not substituted or installed here.
Future selected literal CommonJS lowering can return default; runtime `require`
and `syncBuiltinESMExports` remain outside this milestone.

The parser retains Node's finite state machine, including overlapping/multicode
unit delimiters. It returns a null-prototype dictionary, so `__proto__`,
`constructor` and `hasOwnProperty` are ordinary data keys. Repeated keys become
arrays. Default `maxKeys=1000` counts segments, including empty ones; it is not a
distinct-key limit. Node decrements positive values without integer validation:
fractional positive values can fail to reach zero, while nonpositive/NaN values
select unlimited behavior and Infinity never reaches zero. These quirks are
preserved within profile hard caps. Getter access order is covered by the oracle.

Custom decoder callbacks receive `%20` for `+`, run for nonempty key/value strings,
and may return arbitrary values as pinned Node does. Exceptions deliberately fall
back through mutable default `unescape`. Successful returns are not type-checked
into a fabricated string API. Callback/getter effects and thrown coercions remain
ordinary JavaScript behavior. The custom encoder receives primitive-converted
values, including empty strings, while the default encoder has Node's primitive
fast paths. No input record or array is cloned merely to run these callbacks.

## Codec traps resolved before implementation

Native `encodeURIComponent` matches the escape alphabet and bytes for well-formed
UTF-16. Node22's legacy `encodeStr`, however, pairs **any** surrogate with the next
UTF-16 unit, using their low ten bits. Thus `escape('\uD800a')` encodes a scalar
instead of throwing. A terminal high or low surrogate throws `URIError` with
`code='ERR_INVALID_URI'`. The prototype uses the captured intrinsic first, then
repairs only that exceptional legacy path; non-URI failures propagate.

Malformed-percent fallback is byte-based, not TextEncoder conversion:

| Operation | Pinned result |
| --- | --- |
| `unescape('é%')` | replacement character plus `%` |
| `unescape('中%FF')` | `-` plus replacement character |
| `unescape('\uD800%FF')` | NUL plus replacement character |
| `unescape('a+b', true)` | `a+b` because native decoding succeeds |
| `unescape('a+b%', true)` | `a b%` because fallback handles spaces |

The scanner writes raw UTF-16 units modulo256 into fresh Buffer storage, decodes
valid percent bytes, and preserves malformed tokens. Nonfatal UTF-8 decoding
preserves BOM. Parser decode detection is also retained: a raw malformed `%`
without a valid byte triplet need not invoke the decoder at all. Consequently
`parse('x=é%').x` remains `é%`, while direct `unescape('é%')` takes byte fallback.
The corpus checks these differences using the actual guest decoder.

## Limits, ownership and lifecycle

| Additional profile limit | Value |
| --- | ---: |
| Direct codec/parser string input and coerced parse delimiter | 1,048,576 UTF-16 units |
| Scanned parse segments | 65,536 |
| Stringify own keys and total emitted values | 65,536 each |
| Stringify output | 16,777,216 UTF-16 units |

Limits throw `RangeError` with `ERR_SM_NODE_LIMIT` and `operation`; Node has no
corresponding hard caps and `maxKeys=0` cannot disable them. Limits may follow
earlier callbacks/getters, with no rollback. They do not bound arbitrary callback
execution or guarantee a peak-memory limit. Custom encoders can bypass the default
escape input-size check, but output and field caps still apply. Proxy arrays
reporting noninteger/nonfinite lengths are explicitly deferred.

Nonstring `unescapeBuffer` overloads throw `TypeError`
`ERR_SM_NODE_UNSUPPORTED` on call and construction. This also applies after failed
nonstring `unescape` coercion reaches fallback; successful native scalar/object
coercions remain supported. Both codes appear in messages for componentization
diagnostics. Unsupported initialization is never globally suppressed.

The scanner uses supported captured `Buffer.alloc` because baseline `allocUnsafe`
is deferred. It fills every returned byte; a shortened slice shares the scratch
backing ArrayBuffer without a byte copy. Zeroed unused backing and absence of
Node pooling follow the bounded Buffer profile. No C++ borrowed pointer is added:
strings, typed arrays, slices and closures are ordinary GC-traced guest objects.
UTF-8 string creation is an owned result of the existing native decoder.

Initialization captures URI intrinsics and byte allocation/slice references.
It creates no external handle, timer, entropy, environment value or request state.
Mutable default hooks persist if a component is reused; all parser scratch state
is call-local. Querystring has no async API and makes no AsyncLocalStorage claim.
The finite parser facade stays JavaScript; computational URI/UTF-8 work uses
existing native guest paths. Moving the remaining byte loop to native code needs
measured benefit and separate ownership/GC review.

## Verified component and remaining gates

The component uses ordinary Release v5 OFF engine
`165b59a1fac4f3bab14547a28063908193c2b98767bd5fa835ca00b9b6d8adfc` with
all271 frozen inputs verified. Node22.14, Jco1.40.0, ComponentizeJS0.23 plus the
audited v2 packager and pinned preview1 adapter are recorded in the full report.
The bundle retains exactly `node:buffer` as an external guest module. Final WIT
has **zero imports** and exactly `run: func() -> string` exported.

Both retained Jco calls pass all groups/profile checks with counters `[1,2]`;
fresh unmodified Wasmtime42.0.1 passes with counter1. Five componentization failures
cover unsupported call/new, nonstring unescape fallback, an input cap and an
uncaught deferred microtask. The runner handles Wasmtime's Rust debug-string
Unicode/apostrophe escaping while preserving literal backslash sequences; this
is test-output transport handling, not a guest semantic adjustment.

Reproduce with pinned Node using `audit-sources.mjs`, `run-node.mjs`, then
`run-component.mjs` and environment variables `NODE_COMPAT_ENGINE`,
`NODE_COMPAT_ENGINE_SOURCE_ROOT`, `NODE_COMPAT_TOOLCHAIN`,
`NODE_COMPAT_COMPONENTIZE_MODULE`, `NODE_COMPAT_WASMTIME`, and optional
`NODE_COMPAT_QUERYSTRING_OUTPUT`. Accepted output is under
`/tmp/starling-node-compat/foundation-querystring-prototype`.

Next integration decisions remain explicit: allocate a production profile version,
adapt/validate the production manifest schema, and choose an optional factory.
Existing `register.cpp::evaluate_factory` already accepts one rooted argument;
the rooted Buffer constructor available in `install` can be supplied privately to
a proposed Querystring factory, without inventing a host service or public JS
factory. This is a proposal, not an installed API. Registration must preserve both
alias value identities through `define_builtin_module`, and bundler selection must
externalize the selected module rather than silently choosing the current Jco
adapter. Native namespace/cache/late alias/CommonJS and Assert-OFF-style admission
tests, plus standard HTTP target-host execution, are still required.

No Querystring size/startup/memory/throughput advantage is claimed. The current
component includes its corpus. Compare stripped application fixtures against the
locked Jco/unenv adapter on the same frozen engine/host before proposing further
native byte processing or claiming a performance improvement.
