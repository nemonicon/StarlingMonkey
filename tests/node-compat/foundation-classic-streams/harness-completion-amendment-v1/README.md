This source-only amendment is required by a future classic-stream activation.
It does not change the immutable integration candidate or its 191-file index
`5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d`.
The files under `proposed/harness/` are afterimages for a **new** activated
harness family, not an instruction to patch the sealed predecessor in place.
All actual artifact pins in the predecessor remain null.

The old driver wrote a success-looking `results.json` before its final
`admission.recheck()` in `finally`. A later failure could leave that report on
disk. It also recorded component hashes without a completion inventory for the
generated Jco cores and glue. The new driver collects the report in memory,
finishes the final input recheck, and only then calls the completion publisher.
The disabled path leaves the same labeled execution block and follows the same
publication order. A recheck failure therefore publishes neither result nor
completion. The already-packaged caught initializer control now also has its
component bytes preserved; its semantic source and execution scope are unchanged.

All existing output writes use a private tracked writer with exclusive creation.
This includes the actual names returned by each `transpile(...).files` loop;
there is no guessed core count or directory scan. The publisher hashes these
ordinary files, writes and reads back `results.json`, and exclusively writes
`completion.json` with path, byte count and SHA-256 for each artifact. Output
paths are confined to the run directory, symlinked parents/files are rejected,
and `node_modules` is excluded. All partial output is preserved on failure.
The completion file is excluded from its own hash list.

**External raw terminal exit code zero is mandatory.** A collector must require
that status, parse both files, and rehash every completion row, including the
results row, before treating a run as completed. A results file alone, a
completion file alone, or a child timeout/nonzero status is not acceptance. This
is not a crash-proof multi-file transaction or protection against arbitrary
concurrent writers. No helper observes its own eventual process exit or grants
runtime acceptance. A future activation must add both afterimages and this
dependency to its fresh pre/post source seal; no old pin or manifest is reused
as if it covered the amendment.

`transformation-proof.json` records exact reversible edits restoring the old
driver hash `949a9c8ca9310341db2351fbad8e314d1c13101f82d5c08806237a5f8a2cc0c6`.
The complete ordinary 19-group checks, 48 deferred call/construct cases, 17
overloads, 65 initializer failures, two handled deployed controls and fresh
fatal case remain inherited unchanged. Snapshot coverage remains an empty
initializer-created Readable plus ordinary objects/Buffer; it does not establish
a queued pre-snapshot chunk. The GC fixture retains combined owners. Node
comparisons use the pinned original and transformed 19-group oracle. Generic
fatal output still does not identify an inaccessible trap cause.

Only source generation, syntax checking, hashing and 13 tests using tiny owned
text files were run under Node22.14.0. Filename suffixes in those host tests
exercise inventory classification; their bytes are explicitly plain text and
are never parsed or executed as Wasm. No engine pin, compiler, componentizer,
guest, Wasmtime or wasmCloud was used. The future component driver remains
unexecuted.
