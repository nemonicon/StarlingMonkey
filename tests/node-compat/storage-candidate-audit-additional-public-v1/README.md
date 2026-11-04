# Additional completed public outputs: read-only inventory

The exact [67-file inventory](inventory.json) has 881,274,880 allocated bytes
(about840.4 MiB), slightly above the requested0.8 GiB allocation threshold. Its
logical size is 881,151,952 bytes; the largest file is19,223,955 bytes. These are
allocation measurements, not measured compression recovery or a guarantee that
the2 GiB native-build launch gate can be met.

The scope contains ordinary completed v2 native/entropy/ownership outputs, an
older ordinary integration HTTP component, initial native/Release-GC and JS
facade/stub outputs, and completed public Path/Buffer benchmark arms. Each
component matches an original final report hash. Core dependencies have either
an explicit report hash or a generated-JavaScript reference to a paired reported
component. Build-only benchmark records do not become runtime or timing passes.

The15 original e2e attempt files come from a terminal4-passed/15-failed report.
Their failures remain failures, and every one differs from the later corrected
accepted component bytes. They are repeated public attempts, not byte-identical
accepted duplicates. This packet makes no release-acceptance, Node-compatibility,
benchmark-quality or performance claim.

All67 preimages were hashed and their metadata captured: regular single-link
files, flags0, mode0644, uid501/gid0, ACL[], provenance-only xattr. Prior compressed
files were not selected. Dynamic diagnostics, probe/partial Path outputs,
benchmark diagnostic arms and all private/debug/OOM/probe/candidate/raw-memory/
native-engine/SDK/source/configuration paths are excluded.

[Quiescence](quiescence.json) observed no task-owned/selected-path operations and
exact-path `lsof` returned1 with empty stdout/stderr. Forty-one terminal/report/JS
witnesses were independently rehashed. Two unrelated long-running runtimes were
observed and left untouched. This is a point-in-time observation; repeat it before
any separately authorized mutation. No compression, deletion, build or guest ran.

This inventory is a candidate whitelist, not the previous compactor's frozen
preimage format. Any future representation change needs a separately reviewed
exact-file helper, a matching dry run, per-file headroom and metadata/hash/rollback
verification. Current availability is not reserved.
