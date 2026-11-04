# Read-only capacity audit of older accepted public outputs

The exact [92-file whitelist](results.json) occupies 1,308,119,040 allocated bytes
(about 1.22 GiB). Its logical size is 1,307,936,237 bytes. These are compression
candidates, not measured recoverable bytes. No compression, deletion, build or
guest execution occurred.

Each component's current SHA matches an immutable accepted allocation-r2,
entropy-v1, foundations-v3 or foundations-v4 report. Those reports and their
current original copies also match the milestone's recorded SHA. The remaining
core files are tied either to explicit packaging-core hashes in those reports or
to generated JavaScript dependencies of their paired accepted components. The
report records these two kinds separately; no engine or packaging tool binary is
selected.

Every candidate is a regular single-link file with flags0, mode0644, uid501/gid0,
no ACL and only the recorded `com.apple.provenance` xattr. Logical SHA, inode,
size, allocation, mtime and required metadata are recorded. The prior audited
compression algorithm can preserve these metadata types; no new compression
success is inferred. A fresh compactor dry run must match these exact paths,
hashes and metadata before any separately authorized mutation.

The largest candidate is 37,289,198 logical bytes (about35.6 MiB). Serial
one-file temporary copying bounds the main transient data to one such file;
journal/metadata overhead and a free-space margin remain necessary. The original
inode must retain its verified rollback link until replacement verification
succeeds. Filesystem availability can change independently, so the current
statvfs observation is not a capacity reservation.

The whitelist excludes unaccepted v1 Path, the earlier duplicate e2e attempt,
all v2 outputs without an explicit immutable accepted report closure, v3
benchmarks/adapter controls, and every private/debug/OOM/probe/candidate/engine/
source/SDK/configuration tree. It does not recursively admit whole run trees.
Only explicit completed roots and exact matching files are listed.

The initial77-file audit conservatively missed15 accepted corrected e2e leaf
directories. Its report is preserved under `history/`; the final92-file audit
adds only component SHAs from the accepted19-case, failed0 report. Earlier
read-only validator corrections used that initialization report's actual `pass`
field and the host's `/usr/bin/xattr` API. No artifact was changed by those
failed checks.

The separate [build-intermediate capacity report](build-intermediates.json)
measures only the new failed scheduler v1/v2 `cargo/build` trees and CMake object
files. It is a size observation, not deletion authorization or a file-removal
plan. Raw engines, source, SDK and frozen configuration are outside that scope.

V8-v10 have no remaining eligible candidates: all255 public matching artifacts
are already compressed, as recorded in the separate v8-v10 audit. They must not
be selected again.
