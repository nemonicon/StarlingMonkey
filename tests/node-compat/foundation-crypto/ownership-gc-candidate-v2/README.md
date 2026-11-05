Thin SOURCE correction of held GC proposal3b6f and formal HOLD2ac980be.

The old proposal and HOLD remain immutable. The original no-key-at-INIT HMAC guest,
normal component, native355 source and every normal proof are unchanged. The new
guest reverses exactly through six edits to the held pressure guest, then through
its original eight edits to the original sealed HMAC source.

The inherited `gcOrEntropyRequested:false` field is removed. It is not redefined
as a direct-JS-only claim. `gcObservation` has version
`public-buffer-gc-pressure-v1` and an explicit scope. It reports deliberate public
pressure requests, completed pressure records, `entropyRequested:false`, and
`actualNativeGcCountObserved:false`. This counter tracks the source pressure-call
attempt before Buffer allocation; it does not count native collections or prove a
compaction. A failed pressure attempt can truthfully report one requested call and
zero completed records. Failed run returns also retain the observation, while the
complete collector still refuses the failed fixture.

For successful fresh `validate()`, per-run requested/completed pressure counts are
4, 4, 8 and 0; their request flags are true, true, true and false. The prototype-only
fourth run makes no new pressure request. The outer validate observation reports
true with 16 requests and 16 complete records. Outer schemaVersion2 and kind
`crypto-owner-within-export-gc-validation-v2` make the changed typed schema explicit.
All original HMAC operation, key metadata, refusal, sentinel/window, full signature,
verification boolean and counter fields remain unchanged.

The public pressure mechanism is unchanged: Buffer.alloc(64,0xa5), one public
toString('hex') and one Buffer.from(hex,'hex'), with every encoded/decoded byte
checked. The six native source hook sites per completed pressure record remain
source-coupled expectations, not an observed count. Keys remain strongly held by
the module and arguments alongside other live values. No isolated native temporary
root, pending operation, native global counter, finalizer, free, wipe, all private
copies, WebCrypto-internal collection, performance or memory claim is added.

`collector.py` is a pure, complete typed-record model. The full accepted normal
expected record comes from the sealed independent WT review d1e3f9f1; the new model
adds only the explicit GC schema/observations and 16 pressure records. The future
collector compares every field and rejects unknown fields, the old false field,
a blanket true flag on run3, altered counters/tags, missing records or clipped
hex. It does not discard new observations or normalize an actual GC result into
an old normal pass. Tests use synthetic expected DATA only; no actual GC result
exists or is accepted.

Source/read-hash preparation proves 8+6 exact reversals, whole underlying HMAC-field
equality, correct scoped counters and meaningful negative cases. The pinned Node
parser separately checks only syntax with `--check`; it imports/evaluates no guest.
The prior held packet's old pending parser labels remain historical DATA.

Isolated native source2fbc is a separate unreviewed source implementation. This
packet does not grant its stage/build/freezer/bootstrap authorities or adopt an
actual GC engine, pin or component. Root must first obtain independent source and
actual native/freeze/bootstrap reviews, then a new selected-Buffer component source
and actual artifact review, a complete raw typed collector and explicit GC export
authority. Existing normal component guards must continue to refuse this import,
GC variant and engine. Every actual/proof/action/Root/pin slot remains NULL/false.
