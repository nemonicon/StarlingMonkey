# WASI HTTP result-error adapter correction

This unconstructed Source successor changes the two raw entries only through
their inline adapter. It preserves the complete Next preparation code, corrected
default-Node ALS control, pure main-global alias, all16 dependency IDs, neutral
prepare-once/fresh-request boundaries, selected13 standard0.2.10 interfaces,
whole WIT dependencies and unchanged application contract. Native engine,
manifests, application bytes and host capabilities do not change.

The actual profile2 dependency run returned two strict16-pass GET responses,
then POST500 while reading the incoming body (`streamFailure: undefined`). Its
failure and full responses remain retained and unaccepted. The failure did not
capture the original thrown object's own-property shape, so the diagnosis is
Source-coupled: the pinned private Rust splicer uses the GuestExport ABI for
WASI imports, selects ThrowResultErr and disables unwrapped errors. Its genuine
js-component-bindgen emits `throw new ComponentError(retCopy.val)`, with the WIT
variant in an own DATA `payload`. The previous adapter checked `error.tag`.

The adapter recognizes only direct WIT stream-error records and that explicit
own-payload representation. Wrapped `closed` is EOF only during input reads;
it closes the Web stream and completes/drops the actual incoming resources.
`last-operation-failed` calls the real error resource's synchronous DATA
`toDebugString` method, retains the original throw as `cause`, then drops that
resource once. Payload/tag/debug-method accessors are refused or ignored
without invocation; Promise/thenable diagnostic returns are never assimilated.
Unknown throws retain their original identity, including falsy values.

Output still uses actual `blockingWriteAndFlush` in chunks at most4096 bytes;
it does not use `checkWrite`. Both return WIT stream-error results under the
same binding policy. Output errors, including `closed`, remain failures; the
adapter does not convert them to successful completion. No new output API or
capability is introduced. General Proxy/hostile resource tampering is not an
attested capability of this trusted WIT resource boundary.

The host-only regression executes the previous adapter's actual wrapped-EOF
failure and the successor's success. It runs the existing13 ownership cases in
both direct-variant and ABI-shaped ComponentError modes, plus unknown-throw,
accessor and synchronous-diagnostic cases. These exercise host Web streams and
resource models, not native/component/guest behavior. Read-only
`python3 -B check-source.py` verifies whole assembly and parent identities;
the pinned Node can run `test-ownership.mjs`. Results and grammar terminals are
retained here. Do not rerun writers in this held family.

Root must bind these new entry/family descriptors in a fresh construction and
runtime authority. All actual-proof and action slots remainNULL; this Source
does not grant construction, execution, public adoption, snapshot/reset,
Store-death or full Next acceptance. All prior Source and runtime evidence
remain unchanged.
