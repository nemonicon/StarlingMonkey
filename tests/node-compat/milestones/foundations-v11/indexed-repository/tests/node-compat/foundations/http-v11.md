# Bounded m0.11 joint HTTP validation

One component, SHA-256
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`
(63,635,975 bytes including test oracles), passed three requests each on stock
Wasmtime 42.0.1 and official wash 2.11.0. Both hosts stopped with exit code 0.
Counters were `[1,1,1]` on both; no component-instance reuse or general request
lifecycle claim follows. The exact artifact was sealed before either host ran.

The RuntimeOnly engine is
`2e3731ce248be1d8ede0f5672dd87b48fb1731dfddb045bfaabaeea02534a36d`,
with fixed receipt
`9adc95f3966ea5b12a4d2b6753b32f2f72ce736990e649d55bf367e808bbc07a`.
The input receipt captured 24 integration sources before packaging. Exact
304-source/layout/actual macro admission ran before the protected receiver
cases; the final audit repeats it after both hosts and rechecks all 24 inputs.

The fixture retains complete schema 5: the previous bounded foundation corpus,
first-deployed computed bare aliases and cache/default identities, static
CommonJS interop, safe inspection and deferred-operation errors, plus all
29 protected-abort groups (16 public, four nested-once, nine receivers). Fatal
initializer/deployed cases remain in their separate runner. Each HTTP response
also proves the installed core m0.11 allocation policy's observed secondary
Number-hook counts are zero with length truncated to three. No allocator is
replaced and no JS builtin adapter or native factory is bundled into the app.

Final imports are exactly HTTP types, IO error/poll/streams, secure random and
the type-only monotonic-clock interface, all at WASI 0.2.10. No callable clock
function is imported. The official host's outgoing-host, name-lookup and
loopback-port allowlists are empty. No outgoing HTTP, filesystem, DNS, socket
or TLS behavior is exercised; no host modification or custom service is used.

Node parity remains partial. The separately measured fresh OFF-component
callback-return getter counts are Node ordinary/protected/already-aborted
`1/1/0`, versus native Jco and Wasmtime `0/0/0`. Those getters return undefined;
no callable-then or rejection test follows, and they were not rerun inside HTTP.
HTTP directly observes the disposal-symbol gap: Node uses registry key and
description `nodejs.dispose`, while the target uses description `Symbol.dispose`
and no registry key. Descriptor attributes match. The companion
[known limitations](./http-v11-known-limitations.json) records
`nodeCompatibilityPassed: false`. The allocation change fixes neither gap.
Passing the bounded positive corpus establishes no complete Node, Buffer,
EventTarget, stream or process compatibility.

Artifacts and full host reports remain under
`/tmp/starling-node-compat/foundations-v11`: `http-joint/`,
`http-joint/wasmtime-v1/wasmtime-results.json`, and
`http-joint-wasmcloud-results.json`. There was one HTTP packaging attempt and
one successful execution on each host, with no HTTP retry or source relaxation.
Earlier allocator-import and disk-space failures remain separately preserved.
These correctness artifacts establish no performance, memory or component-size
advantage; the earlier measured RSS and snapshot-size counterexamples remain.
