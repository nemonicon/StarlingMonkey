# Independent postverification of the two Release-input COW adoptions

[results.json](results.json) records an independent read-only pass over Root's
20261103T185556Z-6973297f operation. The verifier did not import or rerun cow.py,
call clonefile/compression, execute a library/compiler/guest, or write any source
or target. Only this new verification packet was written; hash reads may change
unprotected access times.

All four complete hashes match the exact Release library298b… and archivec57…
pins. Both canonical source device/inode/required metadata are unchanged. Each
improved-build target has the required bytes, size, mode, uid/gid, nanosecond
mtime, all xattrs and ACL, a new inode distinct from its old target/source,
link count1 and flags0. The ordered journal records two return0 calls, two verified
adoptions and release of each rollback link. All four known temporary/rollback
paths across the operation namespace are absent. The frozen source/dry-run
index47e9… and all12 referenced files remain byte-identical.

The operation's **nonexclusive** free-space delta is3,612,672 bytes only.
This does not prove unique/shared extents or722MB recovery. st_blocks is not an
exclusive-extent measurement; the independent free-space observation is also
nonexclusive. This is storage integrity verification, not runtime compatibility,
link execution, performance or capacity-target acceptance. Rollback/failure
branches were not induced. The closed SDK-compression operation was not retried.
