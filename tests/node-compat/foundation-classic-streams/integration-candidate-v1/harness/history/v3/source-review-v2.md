# Source-only correction and snapshot review

The first nine files and receipt were copied byte-for-byte to `history/v1/`
before any correction. The predecessor receipt is SHA-256
`24cf74fd393a5391c1972b6812379cd63e94df039824723e7abbab6b95d572ee`.
No packager, native engine, guest, host, or component template was executed.
The copied 19-group checks, Node oracle source, and executed Node oracle receipt
are unchanged. That oracle was not rerun.

`implementation-candidate-v1/classic-streams.mjs:7–13` constructs the Error
message as `node:stream.<operation> is unavailable in sm-node-22.14.0-m0.12`
and separately defines its own `code`, `module`, `operation`, and `profile`.
Therefore a packaging wrapper's human failure message is not required to contain
`ERR_SM_NODE_UNSUPPORTED`. The corrected initializer vectors store the exact
factory operation/message; the driver requires that message in the wrapper's
failure text. Runtime catches and the caught initializer separately check own
coded fields inside the guest.

The Web overload messages are `pipeline(Web stream)`, `finished(Web stream)`,
and `addAbortSignal(Web stream)`; function stages use
`pipeline(function stage)`. Test labels such as `promise-pipeline` are labels,
not factory operation strings. All 48 deferred call/new vectors retain their
exact operation names, and the 17 overload vectors now state the distinct
factory operation explicitly.

`guest.mjs` creates `snapshotSource`, `snapshotToken`, `snapshotDefaults`, and
`snapshotHex` at module initialization. The source does not push the token or
start a read before deployment. The candidate Readable constructor installs the
provided read function and calls `destroyImpl.construct`; that helper returns
immediately when `_construct` is not a function (`classic-core.generated.mjs:636–639`).
No `_construct` option is supplied by this fixture. This is source evidence for
an empty guest stream at the snapshot, not actual snapshot execution evidence.

On exported call one the fixture pushes and reads the retained token, requires
identity, destroys that one stream, and waits on public completion. Later calls
intentionally report `snapshotIdentity:null` rather than reusing that destroyed
stream. The first-call identity check does not prove a chunk was queued before
the snapshot. The snapshot Buffer has an independent content check. Initial
HWM observations must remain `[65536,16]`; the ordinary checks explicitly reset
defaults before comparing with the Node reference and leave byte HWM777 at the
end, so call two and three require the retained777 value. A truly fresh
instantiation must return to65536 and call one. These are future assertions,
not current observations.

The generated Jco module is imported once for the three retained calls and with
a distinct module URL for the fresh assertion. A future run must demonstrate
the resulting call/default observations; this source-only review does not claim
that an unexecuted generated binding already proved independent instantiation.
Wasmtime is a separate fresh process. No failed instance is reused.

The parent preflight must bind the actual live repository adapter bytes (the
known988224… SHA-256), all current harness bytes, and the final producer/helper
sources in its immutable pre/post `recheck()`. The driver's local adapter hash
check is useful but is not a substitute for that full input recheck around
packaging. Future artifact pins remain null.
