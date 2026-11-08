# Standard handler return observer

The v2 observer is a real composed Component Model artifact. Parsing,
validation, WIT extraction and composition pass; its first deployed request is
pending. This is diagnostic work for the unresolved Next.js completion failure,
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

A successful marker would witness ordinary observer execution after the inner
synchronous canonical call and configured post-return complete. It would not
establish the observer's own return, host task completion, transport EOF,
private request/Store identity, cause, unchanged scheduling or Next acceptance.
Public metadata is absent from this first mechanism proof.
