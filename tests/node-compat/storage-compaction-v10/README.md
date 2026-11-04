# Completed v10 output compaction, supplementary receipt

Root authorized transparent filesystem compression of completed outputs in only
`/tmp/starling-node-compat/foundations-v10/release-gates-v1/{core,allocator,stream-web,optional,strict-sync,strict-runtime}`.
The copied helper has this exact six-directory allowlist. The accepted
[v8/v9 helper and receipt](../storage-compaction/README.md) were not modified.

[results.json](results.json) records **61 files**, 839,312,748 unchanged logical
bytes, and **522,235,904 physical bytes recovered** (498 MiB). Allocated space
decreased from 839,458,816 to 317,222,912 bytes. Every file passed independent
SHA-256, logical-size, mode, uid/gid, nanosecond-mtime, extended-attribute digest,
and ACL checks. The fresh-copy decompression round trip also passed.

The authoritative fsync-before/after journals, run summary, and complete
independent receipt are in `/tmp/starling-node-compat/storage-compaction-v10`.
No existing artifact was deleted. No source, receipt, raw log, native-freeze,
engine, build tree, DEBUG/OOM output, active callback/latency output, or private
m0.11 input was selected. Inode/ctime/ditto birthtime and filesystem compression
representation change as documented by the original helper; required mtime
metadata and logical bytes remain exact.

```sh
python3 tests/node-compat/storage-compaction-v10/compact.py          # inventory
python3 tests/node-compat/storage-compaction-v10/compact.py --apply  # explicit application
python3 tests/node-compat/storage-compaction-v10/verify.py           # full independent readback
```

Reversal uses a fresh destination with
`ditto --nohfsCompression --nopreserveHFSCompression --noclone` before hash and
metadata verification. `--nohfsCompression` alone preserves stock ditto's
default compressed representation; its control copy is retained. Only the new
successful decompression demonstration copy was removed after verification.

This independent storage receipt makes no new compatibility, execution, or
performance claim and does not alter an accepted milestone archive.
