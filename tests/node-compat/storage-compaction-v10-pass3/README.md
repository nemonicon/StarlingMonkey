# Completed v10 outputs: supplementary third pass

This pass covers only generated component and Jco core Wasm files in four
completed directories: `add-abort-runtime`, `add-abort-gc`,
`callback-return-observation` and `events-off-admission`, under
`/tmp/starling-node-compat/foundations-v10`.

[results.json](./results.json) records 24 independently rehashed files and
291,908,590 unchanged logical bytes. Allocated space fell from 291,962,880 to
112,857,088 bytes, recovering **179,105,792 physical bytes** (about 171 MiB).
Available disk space after verification was 2,149,863,424 bytes (2.00 GiB).
These are filesystem allocation observations, not guest performance results.

The copied compactor's algorithm is unchanged; only its description, four-root
allowlist and new receipt namespace differ from pass 2. The verifier retains
the same audit/reversal algorithm, with the exact frozen count of 24 and added
previous-helper/receipt immutability pins. The inventory freezes exact paths,
preimage hashes, required metadata, xattr digests and ACLs before replacement.
The allowlist admits only `*.component.wasm` and `*.core[digits].wasm`, excludes
engine names, and refuses symlinks, multiple links, unexpected flags and
source/native-freeze/DEBUG/OOM/private directories. Logs, receipts, native
sources, engines, private m0.11 inputs and prior scripts/results are unchanged.

Each fresh same-directory compressed copy must preserve bytes, logical size,
mode, uid/gid, nanosecond mtime, required xattrs and ACLs and save physical
blocks. Atomic adoption retains the original inode through an owned rollback
link until successful readback. All 24 operations passed and released their
rollback links. The restoration-on-failure branch was not induced or tested.
Inode, ctime, ditto birthtime, compression representation and physical blocks
change; required metadata is checked exactly.

The authoritative apply receipt is
`/tmp/starling-node-compat/storage-compaction-v10-pass3/20261103T143241Z-12c31ac4.summary.json`.
Its frozen inventory, fsync journal and independent `verified-results.json`
are indexed separately. Independent verification rereads all logical bytes and
metadata, checks released rollback links and unchanged earlier helpers/results,
and demonstrates a fresh uncompressed-copy round trip. The new verified
decompression demonstration copy is removed; its source and the explicit
default-preservation control remain. No accepted logical path is deleted.

No native build, guest execution or timing ran in this pass. Work stops before
the separately coordinated m0.11 builds.
