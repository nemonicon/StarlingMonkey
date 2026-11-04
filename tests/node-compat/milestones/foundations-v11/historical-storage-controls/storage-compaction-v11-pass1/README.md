# Completed v11 outputs: first supplementary compression pass

This pass covers only completed release-gates-v1/core, release-gates-v1/allocator,
release-gates-v2/allocator and release-gates-v2/stream-web beneath foundations-v11.
The v1 allocator ended in a host-harness import error: its fully written Wasm
files are storage-complete; compression does not claim a runtime pass.

All 14 generated component/Jco core files retain 186,777,707 logical bytes and
required mode, uid/gid, nanosecond mtime, xattr digests and ACLs. Physical allocation
fell by 114,855,936 bytes. The copied audited algorithm differs only in scope,
receipt namespace, frozen count and earlier-helper/receipt immutability pins.
Fixed inventory, fsync journal, fresh same-directory copy, original-inode rollback
link, atomic adoption/readback and independent hash/metadata/reversal checks pass.
All rollback links were released; the failure-restoration branch was not tested.
Inode/ctime/ditto birthtime/compression representation/physical blocks change.

No native source, engine, native-freeze, private input, active directory, log,
receipt or previous script/result was altered. Only explicit generated Wasm
names are admitted, with symlink/link/flag and excluded-directory guards retained.
A fresh decompression demonstration passed and only its new temporary copy was
removed; sources and the default-preservation control remain. See results.json
and the frozen index for exact preimages/journals and metadata contracts.

Concurrent test outputs consumed disk during the pass: only 261,021,696 bytes
were free after independent verification. Heavy guest work remains on hold;
root separately authorizes a further completed-output pass. No guest execution,
native build or performance measurement ran here.
