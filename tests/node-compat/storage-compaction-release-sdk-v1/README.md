# Exact-one current Release guest SDK storage preparation

This source/dry-run packet changes no library bytes and has performed no
compression, linking, compiler or guest execution. It considers only
`/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/libspidermonkey.a`.
It is separate from all component-output whitelists and admits no SDK tree,
debug/private artifact or host runtime executable.

The [Root audit](../storage-candidate-audit-sdk-release-v1/results.json) and
[independent audit](../storage-candidate-audit-release-sdk-v1/results.json)
authenticate the library to exactly one regular member of the pinned Release
archive. Library SHA is `298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc`;
the unchanged archive SHA is `c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b`.
The helper streams that member without extracting a second library file.

[compact.py](compact.py) fixes the one path, both audit hashes and complete
required metadata. Its replacement/rollback block is byte-identical to the
reviewed earlier 92-file helper; metadata functions are AST-identical. The
differences in [changes.REVIEW.diff](changes.REVIEW.diff) select this data class
and authenticate archive provenance. The [dry run](dry-run-results.json) verifies
one eligible regular single-link flags-zero file, with no replacement or failure.

A future copy requires at least **1,143,449,716 available bytes** immediately
before its temporary allocation (`2 × logical size + 64 MiB`). Availability is
not reserved and external allocation can still cause failure. Repeat exact-file
open-file checks and task-build quiescence before any application. Retain the
original inode under the owned rollback link until a smaller copy matches SHA,
logical size, mode/owner/mtime, noncompression xattrs and ACL. Physical attributes
such as inode/ctime/birthtime change; the compression flag is intentionally added.
The pinned archive is never replaced. Recovery is unmeasured until execution.

This is transparent local filesystem representation, not a new guest dependency
or component-size/memory/performance result. Future link/runtime compatibility
still needs its ordinary build and component gates. Do not rerun a historical
preimage pass after adoption, and never overwrite its receipts. Reversal,
post-adoption failure, power loss and ENOSPC rollback branches are not tested by
this dry run.
