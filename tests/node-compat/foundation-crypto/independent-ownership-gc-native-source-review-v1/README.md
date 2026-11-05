Independent isolated GC native source review: **HOLD** for `GC-NATIVE-FRAME-M1`.

The [guard](../ownership-gc-native-candidate-v1/guard.py) returns a frame with
`rootAuthority`. The [freezer wrapper](../ownership-gc-native-candidate-v1/freeze.py)
adds its engine, metadata and active/donor tooling fields, but never `authority`.
The retained [freezer body](../ownership-gc-native-candidate-v1/freezer-body.py)
reads `context['authority']` when constructing correction provenance. That lookup
would raise `KeyError` after the read-only admission/Ninja helpers and before
`execute_plan`. This is a source finding; no actual phase was invoked.

The independent [reader](reader.py) rehashes all39 indexed source members and
2,843 distinct physical files. It checks the1,311 staged-copy rows and modes,
1,387 normal original references/1,378 unique originals, exact1,391-file normal
freeze membership,14 Python ASTs and12+1 donor reversals. Its pure AST field model
derives the actual frame keys and every direct freezer-context read; the only
missing direct key is `authority`. The [field ledger](context-fields.json) and
[finding](findings.json) retain that evidence.

The suspected inherited source-root environment issue is refuted: the captured
environment has no source override, and the genuine recipe derives its physical
repository from its own path and exports `STARLINGMONKEY_SRC` accordingly. The
separate work/freeze roots and unchanged explicit-root donor APIs remain present.
The dormant phase, pin and proof guards were inspected; they do not cure the
missing frame key. Other source checks are finite evidence, not runtime acceptance.

The correction requires a thin immutable successor using the actual Root
authority descriptor, an exact reversible donor edit, and a complete context-key
and descriptor-binding regression. The separately reviewed external controller
remains another implementation gate. Preserve the original source and this HOLD.

No owner test, phase entry, configured helper, native build, freezer, bootstrap,
componentizer, generated module, guest, key operation or GC workload was imported
or executed. Only new standard-library read/hash, AST and pure DATA code ran.
No stage/build/freeze/export/bootstrap or runtime authority is granted.
