# Lossless v8/v9 generated-artifact storage compaction

This separate housekeeping receipt records filesystem compression of completed
generated component and Jco core Wasm outputs. WebAssembly bytes, filenames,
existing receipts, accepted milestone archives, sources, and engine binaries
remain unchanged. This is neither an execution test nor a performance result.

The authoritative per-file before/prepared/after journals and summaries are in
`/tmp/starling-node-compat/storage-compaction-v1`. [results.json](results.json)
pins those receipts and the helpers, and records an independent complete
readback. The accepted v9 archive predates this supplementary receipt and was
not modified.

| Root | Files | Old allocated bytes | New allocated bytes | Recovered bytes |
| --- | ---: | ---: | ---: | ---: |
| foundations-v9 | 79 | 1,156,907,008 | 432,709,632 | 724,197,376 |
| foundations-v8 | 88 | 1,302,814,720 | 486,105,088 | 816,709,632 |
| Total | 167 | 2,459,721,728 | 918,814,720 | 1,540,907,008 |

All 2,459,323,006 logical bytes were rehashed against the pre-replacement
SHA-256 digests. The 1.44 GiB recovered is the sum of differences in
`st_blocks * 512`; free-space readings are observations affected by concurrent
filesystem activity. Disk availability after the operation was about 3.8 GiB.

`compact.py` walks only the two explicit roots without following links. It
selects `*.component.wasm` and `*.core[digits].wasm`, excluding engines,
native-freeze/source subtrees, DEBUG/OOM/private paths, files with multiple
hardlinks, other nonregular files, and unexpected filesystem flags. Each
replacement uses a fresh same-directory temporary file and:

1. Journals the original digest, logical size, allocation, flags, inode, and
   timestamps, plus mode, ownership, extended-attribute digests, and ACLs.
2. Copies with `/usr/bin/ditto --hfsCompression --noclone`.
3. Verifies identical logical bytes, size, mode, uid/gid, nanosecond mtime,
   extended attributes (except compression storage metadata), and ACLs.
4. Atomically replaces only when the copy uses fewer physical blocks and the
   original still matches the prepared digest and metadata.
5. Reads the replacement again and journals the verified result.

All 167 replacements succeeded without skips caused by metadata or byte
differences. Inode, ctime, ditto's copied birthtime, allocated blocks, and the
`UF_COMPRESSED` flag change with this filesystem representation. Required
mtime metadata is preserved exactly. Normal reads and independent validation
can update atime.

```sh
# Default is a nonmutating candidate inventory, apart from new journal files.
python3 tests/node-compat/storage-compaction/compact.py --root v9
# Explicit, tightly bounded application, in the recorded order.
python3 tests/node-compat/storage-compaction/compact.py --root v9 --apply
python3 tests/node-compat/storage-compaction/compact.py --root v8 --apply
# Rehash every adopted file and verify a fresh-copy decompression round trip.
python3 tests/node-compat/storage-compaction/verify.py
```

The verifier confirmed decompression into a fresh demonstration copy with the
same bytes, required metadata, no compression flag, and greater physical
allocation. It removed only that new demonstration copy after verification;
its compressed source was retained. A separate compressed control remains in
the authoritative receipt directory. Stock ditto enables
`--preserveHFSCompression` by default, so `--nohfsCompression` alone retained
the compressed representation; this control is recorded rather than treated
as a successful decompression.

```sh
# Reversible representation, always into a fresh destination first:
/usr/bin/ditto --nohfsCompression --nopreserveHFSCompression --noclone SOURCE FRESH_COPY
# Verify SHA-256, metadata, and uncompressed flags before adopting FRESH_COPY.
```

The original copy-only experiment and the failed assumption about ditto's
default preservation policy are retained as evidence. No native build, guest
code edit, host binary change, DEBUG/OOM probe, accepted-artifact deletion, or
private m0.11 input modification was performed.
