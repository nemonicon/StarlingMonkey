# Bounded util v7 evidence; strict initialization gate open

The bounded module tests pass, but **this is not full profile acceptance**.
Additional ordinary tests found synchronous EventTarget and AbortSignal
listeners that invoke unsupported `child_process.spawn`, have their exceptions
dumped/cleared, and incorrectly permit componentization. A valid export-interface
getter also demonstrates a later binding boundary. See the
[acceptance correction](acceptance-correction.json) and preserved
[counterexamples](known-gaps/initialization-results.json). A separately reviewed
guest checkpoint fix is required before broader profile promotion.

The original [bounded results index](results.json) remains unchanged:359
byte-checked files,21 complete reports and all293 captured native inputs, plus
the project/vendor licenses. Its success state describes those executed module
gates; the correction adds counterevidence rather than rewriting their outcomes.
Earlier bounded checkpoints do not prove this newly tested initialization policy.

This revision adds optional `NODE_COMPAT_UTIL`, default OFF, using the finite
`sm-node-22.14.0-m0.7` manifest. Existing core Buffer/child_process remains m0.1;
`Buffer.allocUnsafe` is still deferred. All six optional flags are ON in these
engines, with the same293 input hashes and build recipe:

| Engine | SHA256 | Bytes |
| --- | --- | ---: |
| [OFF](engine-off.json) | `ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09` | 9,719,461 |
| [RuntimeOnly](engine-runtime.json) | `53047d1652db4d9c92ec8d7652a306eb3bd6564f7a457033f708e386955ee004` | 9,726,719 |

The base revision is still `54b3329b3ce818fd1f244e871e9c259b63667cda`, Node
22.14.0, SpiderMonkey147, ComponentizeJS0.23.0 with the recorded guest patches,
Jco1.40.0 and selected WASI0.2.10. Actual registration flags, locked Rust and
complete OpenSSL source/configuration/library receipts are retained.

`node:util` and `node:sys` each have exactly47 named exports plus default;
`node:util/types` has42 predicates plus default. Sys has a separate namespace
with the same values/default as util; util.types is the types default object.
The supported slice is inherits, promisify, toUSVString, existing native web
TextEncoder/Decoder identities and29 predicates over captured native ECMAScript
intrinsics. Inspect metadata remains meaningful and safe to read, while41 root
and13 type callables explicitly throw on invocation/construction. Additional
C++ type helpers are proposals, not code compiled into these engines. Sys and
promisify warning emission is omitted; native codec deviations remain explicit.

[Installed util evidence](util.json) covers2 retained Jco calls and fresh stock
Wasmtime42:2,436 shared Node checks plus108 deferred checks per call, complete
namespace/default/CJS/symbol graphs, snapshot state and captured Error/Assign
behavior. A separate unbundled fixture exercises six first-deployed aliases,
cache identities and safe namespace inspection on both backends. Eight direct
initialization/link failures pass, including Node24-only exports that must remain
absent. An actual frozen v6 engine rejects util before adapter fallback. The
[source/factory gate](util-source.json) independently passes2,523 shared checks
plus108 deferred checks per variant. These direct cases do not cover the later
event-listener counterexamples.

[Buffer](buffer.json), [Path](path.json), [Events](events.json),
[StringDecoder](string-decoder.json), [Assert](assert.json) and
[Querystring](querystring.json) regressions all rerun on the new OFF engine.
[Admission](selection.json) passes213 cases, including64 independent feature
combinations; [CMake/recipe guards](cmake-policy.json) pass17 configure/sentinel
cases. Pure semantic components emit zero imports. No new OOM/GC-stress or
performance result is inferred from these Release regressions.

The same [joint Runtime HTTP component](http-audit.json), SHA
`5085994793baedb5268bd3c7f3c6b7aece17b77ec932bceb7622117a70f8b3b1`,
passes3 requests each on [stock Wasmtime42.0.1](wasmtime-http.json) and
[official wasmCloud2.11.0 local host](wasmcloud-http.json), including all bounded
module corpora,2,436 util checks/108 deferred checks and13 computed bare aliases
per request. Both processes stop with code0. Counters remain[1,1,1]; HTTP
instance reuse and request isolation are not established.

Imports remain exactly HTTP types, IO error/poll/streams, monotonic-clock
duration type only, and secure random, all0.2.10. The only export is the standard
incoming HTTP handler. No custom host service or host runtime modification is
used. The60,773,900byte correctness component retains large corpora and is not
a minimal-size or performance observation. The separately frozen-v5 Weval
measurements remain attached to their own artifacts.

The next priority is the confirmed initialization-policy fix. The isolated
zeroed allocUnsafe, codec-stream/BYOB and consumer candidates remain uninstalled;
their later integration must use new receipts and retain these controls.
