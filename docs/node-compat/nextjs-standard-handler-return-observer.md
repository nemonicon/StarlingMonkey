# Standard handler return observer

The v2 observer is a real composed Component Model artifact. Parsing,
validation, WIT extraction, composition and its first deployed request pass.
This is diagnostic work for the unresolved Next.js completion failure,
not a fix or production promotion.

The actual Next component has a synchronous `handle` lift with an explicit
`cabi_post_wasi:http/incoming-handler@0.2.10#handle` post-return option. Its child
export shim aliases that function and its resource types. The observer forwards
both owned arguments through a standard handler import, then prints a fixed
ordinary-code marker. It does not consume the request body or set the outparam.
Observer and Starling are sibling instances using the same imported resource
types. No host modification or custom external interface is introduced.

Root built WAC CLI0.12.0 from cached commit
`5a7480c69ae7a4dc9eb161f485cbcb8c95e372c9`, using pinned Rust/Cargo1.88.0 and
`--offline --locked --no-default-features`. Source/lock remain unchanged; the
original900-second owner exits0. Cargo reports32.77 seconds of compilation.
The actual native `wasm-tools` is1.235.0, distinct from the0.259.0 wit-component
producer used by ComponentizeJS0.23.0/Jco1.40.0.

V1 parses and validates, and its composition validates, but standalone/final
WIT reconstruction panic on duplicate type mappings. Both failures are retained.
V2 changes only the final export to Starling's existing type-only export-shim
pattern. Core forwarding, markers, ownership and protocol remain unchanged.
Neither parser nor host is patched.

The [composition DATA review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-composition-review.json)
joins all seven successful tool steps and the independent structural review.
Observer `c754465c` is2,648 bytes. Envelope `e08b368b` is37,170,412 bytes and
contains the exact unchanged37,156,919-byte `d04c4289` probe. Its external surface
is exactly the same thirteen standard WASI0.2.10 interfaces and only the handler
export; the internal handler import is composed away. Observer memory is fixed
at64KiB. These are artifact/declaration measurements, not RSS or throughput.

The first runtime is one GET `/none`, with no mounts, guest environment,
outgoing workload, HTTP warmup or retry. A bounded literal94-byte marker check
controls shutdown; semantics require normal child shutdown and complete capture.
The original180-second owner and genuine inner build/world admission remain in
use. The envelope has a separate composition review, not a fabricated constructor
frame.

The first deployed GET finishes raw0/clean under original owner79199/180 seconds.
It returns the expected complete371-byte HTTP200 body and exactly one94-byte
success marker, with complete finalized capture and normal child shutdown. The
[runtime DATA review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-return-probe-runtime-review.json)
joins the original owner, body, Source and composition proof. No target rerun
occurs during review.

That marker witnesses ordinary observer execution after the inner synchronous
canonical call and configured post-return complete. It does not
establish the observer's own return, host task completion, transport EOF,
private request/Store identity, cause, unchanged scheduling or Next acceptance.
Public metadata is absent from this first mechanism proof.

The v3 implementation adds a bounded public-header snapshot before forwarding
and emits it at the same later site. All seven actual parse/validate/WIT/compose/
print steps pass. Its 5,519-byte observer produces a 37,173,284-byte probe envelope
with the same standard external surface. The [v3 composition review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-v3-composition-review.json)
verifies exact child bytes, shared fields types and canonical getter options.

All six fixed deployed metadata cases pass: missing, valid, uppercase and
duplicate header values, GET/POST, and both admitted paths. The probe fixture
intentionally returns GET404 and POST405 on those paths; every response remains
correct. The [runtime DATA review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-metadata-probes-runtime-review.json)
verifies one original900-second owner, six fresh normal-shutdown host processes,
complete captures and exact canonical records. There are no retries or warmups.
Allocator failure limits and trapped-instance cleanup remain unproved.

The unchanged real Next component now also composes with v3. Four actual
composition/validation/WIT/print steps pass; the envelope is37,298,513 bytes,
with the same thirteen standard WASI imports. The new full-app runtime Source
keeps the inner constructor evidence separate from the served envelope and its
composition proof. The declared application comparison now completes once in each arm:

| Gate | Wasm with observer | Matched Node22 |
| --- | --- | --- |
| HTTP cases |24/24 pass|24/24 pass|
| Explicit portable cache |52 checks pass|52 checks pass|
| Supplemental checks |80 pass|80 pass|
| Incremental stream |5 chunks, pass|5 chunks, pass|
| Functional browser interactions |2 pass|2 pass|
| Legacy process-global counter |1→1, failed|1→2, pass|
| Strict POST capture |failed|failed|
| Original full suite |failed|failed|

Both strict browser samples preserve POST7 `net::ERR_ABORTED` and body/finished/
sizes capture errors. Both original owners finish cleanly with protected inputs;
no retry or replacement occurs. The Node failure prevents attributing this
sample's strict failure specifically to the guest runtime.

The finite [raw comparison packet](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/next-pair-records-v1/manifest.json)
retains185 selected files/5,066,749 bytes, including browser/NetLog/capture/body
records and both original-owner trees. App copies, packages and large binaries
remain outside this packet. The [fixed declaration](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/fixed-next-pair-declaration.json)
records order, shared app/browser/public inputs and no-retry policy before launch.
The [native public DATA review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-next-observer-public-review.json)
verifies51 typed outer records,54 guest records and6 native records. Exactly one
valid POST `/actions` record contains the declared public action value at the
later import-return site. Seven unknown-route POST competitors keep the
protocol's conservative outer join failed. Browser/NetLog/public guest tuples
agree, without establishing physical identity or causality. The [combined runtime
DATA review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/actual-next-pair-runtime-review.json)
verifies both failed suites, original owners and all retained raw copies.

The [Source audit and next control](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/next-steps.md)
find no proved deliberate POST cancellation. In this Node sample, same-document
navigation precedes the request failure, which occurs before fixture closure;
one failed request supplies three capture errors. This is the matched bridge
profile, rather than a pristine standalone server. A separate non-redirecting
real Server Action with the same strict observer is the next discriminating
control. Its implementation and execution remain pending.

Future runtime checks must use a fresh declared namespace and authority, the
same complete strict gates and current genuine construction/composition guards.
These first-run controllers deliberately refuse to overwrite their evidence.
Keep the original failed fixtures as regression evidence. No complete Next.js,
Node or Buffer compatibility, production promotion or measured performance
advantage follows from this diagnostic.
