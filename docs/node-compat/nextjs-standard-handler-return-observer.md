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
composition proof. Its actual application regression remains pending.
