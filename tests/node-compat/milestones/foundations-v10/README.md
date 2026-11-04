# Bounded foundations v10 checkpoint

This checkpoint preserves completed bounded gates with a confirmed Node callback-return counterexample and a Symbol.dispose registry difference. Node parity for those observations is **false**. See results.json and reports/focused-callback-return-results.json.

Four Release engines share304 source inputs; generated engines/application components remain external. Five exact already-versioned host-API binary source assets are included to preserve the complete native source set. See acceptance-preparation/README.md for the reviewed acceptance plan and limitations.

The archive contains **3,445 independently byte-verified evidence files** and
**33 complete reports**. Core remains m0.8; Events is m0.10, with the layered
`sm-uncaught-event-v3-protected-abort-v2` policy. All seven earlier foundations,
Buffer/stub/allocator, stream/web and24 strict-callback components pass fresh
regressions. [Focused evidence](harness/foundation-add-abort/production-native-m0.10/README.md)
records29 Node-derived groups in both entropy modes, finite namespace/CJS/
snapshot behavior, fatal/discard and handled reuse, and eight valid native
byte-kernel GC roundtrips. GC verifies combined owners: the closure also owns
the Symbol, so prototype-only liveness is not isolated.

The same HTTP component
`0fcad53793003261f6f664ffadc758ae9fe3c6e1b7dd9f6599528f5a35075610`
(63,626,509B, including corpora) passes three requests on stock Wasmtime42.0.1
and official wasmCloud2.11.0. Both stop with code0. Fourteen computed bare
aliases and the protected29 corpus pass. Exact standard0.2.10 imports are HTTP
types, IO error/poll/streams, random and a type-only monotonic-clock dependency
with no callable clock function. No outgoing HTTP, DNS, socket, filesystem,
CLI or TLS capability is inferred. Counters `[1,1,1]` establish no HTTP
same-instance reuse or request-isolation guarantee.

The counterexample remains mandatory evidence: Node reads returned objects'
`then` getters for ordinary and fresh protected listeners once each; the native
target reads neither. Already-aborted queued returns are ignored by both. No
callable-then/rejection behavior was tested in that observation. Node `addCatch`/
returned-Promise/error-routing parity remains unimplemented. Target Symbol.dispose
is unregistered; Node uses `Symbol.for('nodejs.dispose')`. These are limits of
partial support, not failures recast as parity.

The first configure test used an old artifact namespace; its timeout and the
corrected19-case pass remain preserved. The first HTTP host attempt requested
an absent optional intrinsic-report field; the successful fresh host run uses
the same component bytes. The archive's first read-only copy plan rejected
three unapplied m0.11 metadata controls; their hashes remain validated/referenced
while their contents are excluded. No proposed m0.11 source or performance
promotion is included. Earlier checkpoints remain unchanged.
