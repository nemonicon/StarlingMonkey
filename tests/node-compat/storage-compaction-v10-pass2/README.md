# Frozen completed v10 outputs: second independent pass

This supplementary storage receipt covers only completed generated component
and Jco core Wasm files in:

- `/tmp/starling-node-compat/foundations-v10/add-abort-off`
- `/tmp/starling-node-compat/foundations-v10/http-joint`
- `/tmp/starling-node-compat/foundations-v10/release-gates-v1/strict-late`
- `/tmp/starling-node-compat/foundations-v10/release-gates-v1/strict-callbacks`

[results.json](results.json) records **34 files**, 516,179,606 unchanged logical
bytes and **324,378,624 physical bytes recovered** (309 MiB). Allocated space
decreased from 516,272,128 to 191,893,504 bytes. Disk availability after the
independent verification was 2.62 GiB. These are filesystem allocation
observations, not guest execution/performance measurements.

Before any replacement the copied helper freezes the exact candidate paths,
SHA-256 digests, stat metadata, required extended-attribute digests and ACLs in
a new `*.frozen-inputs.json`. The loop uses that fixed list and checks each
preimage again; files appearing later cannot enter the pass. Every admitted
source starts as a regular nonsymlink file with one link and no unexpected
flags. Source/native-freeze/engine/DEBUG/OOM/private paths and logs/receipts are
excluded. Only `*.component.wasm` and `*.core[digits].wasm` are admitted.

Each new same-directory compressed copy must match logical bytes, size, mode,
uid/gid, nanosecond mtime, extended attributes except compression storage
metadata, and ACLs, and must use fewer physical blocks. The original inode is
then retained through an owned temporary hardlink while the fresh copy is
atomically adopted and read back. Only after success is that additional link
released. A post-adoption verification error has an original-inode restoration
path; **that failure branch was not induced or tested**. All34 operations
succeeded, all rollback links were released, and every accepted logical path
remained present with identical bytes. Inode/ctime/ditto birthtime/compression
representation change as documented in the earlier helper; required mtime
metadata remains exact.

The authoritative run is
`/tmp/starling-node-compat/storage-compaction-v10-pass2/20261103T132319Z-de666b2a.summary.json`,
with its frozen inventory and fsync-before/after journal. Independent
`verified-results.json` rehashes all34 files against those original preimages,
checks all required metadata and released rollback links, and confirms a fresh
uncompressed-copy round trip. Reversal uses
`ditto --nohfsCompression --nopreserveHFSCompression --noclone`; the default
preservation control is retained, and only the new verified decompression
demonstration copy was removed.

```sh
python3 tests/node-compat/storage-compaction-v10-pass2/compact.py          # freeze/inventory
python3 tests/node-compat/storage-compaction-v10-pass2/compact.py --apply  # explicit new pass
python3 tests/node-compat/storage-compaction-v10-pass2/verify.py           # independent audit
```

The accepted [v8/v9](../storage-compaction/README.md) and
[first v10](../storage-compaction-v10/README.md) helpers/results remain byte
identical; their receipt digests are checked by this verifier. No native source,
engine binary, build tree, frozen input, private m0.11 input, accepted milestone
archive, log or existing receipt was modified, and no new build or guest test
was performed.
