# Source-only deployed-error additions

The preceding ten-file revision is preserved byte-for-byte in `history/v2/`.
Its receipt is SHA-256
`b3992cce4159add3c3533349416f1dcdd3aea990add71c9ff3eea502dfdd1617`.
The earlier nine-file revision remains in `history/v1/`. No bundler,
componentizer, native build, guest, or target host was executed for this change.
The exact transformed 19-group checks and original executed Node oracle/source
are unchanged; the oracle was not rerun.

The ordinary guest now asserts that the imported canonical Buffer constructor
is the actual global Buffer constructor, rather than merely checking its byte
behavior. The combined stream/callback/AbortSignal/disposer rooting control is
unchanged; it remains eight native hex round trips, not a queue-only substitute.

The new deployed fixture source is packaged before invocation. The fatal export
then directly calls the explicit deferred `stream.compose`. The driver invokes
one fresh Jco child and one fresh Wasmtime instance once apiece, requires a
failure, and discards both instances. Import/instantiation errors occur outside
the Jco child's `try` block. A timeout, spawn failure, or signal termination
cannot satisfy the Wasmtime negative assertion. No code calls a failed instance
again. A host trap alone does not expose a JavaScript error's own fields; the
report states that limit and uses clean paired controls to check the actual
coded error.

The caught control checks own `code`, `module`, `operation`, and `profile`
inside the guest, returns their values, and runs three times on one successful
instance. The handled-later control registers a reaction which calls compose,
then awaits a resolved Promise before attaching the rejection handler. The
earlier reaction must have run before that handler is attached, using a public
side effect as the ordering assertion. The handler checks the same own error
fields. It also has three retained successful calls. Both controls get a fresh
Wasmtime success call. These are planned tests of handling before the final
checkpoint; they are not a new rejection-tracker implementation or an ALS claim.

Every subprocess timeout in the current driver is 55,000ms. Packaging and guest
templates remain unavailable while the parent artifact pins are null. The
immutable parent preflight/recheck must bind all current harness files and the
live988224… repository adapter before and after future packaging and execution.
