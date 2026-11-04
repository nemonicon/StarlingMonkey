# Earlier accepted public outputs: storage-only compaction

This separate packet contains a frozen helper and a successful **dry run only**. No component, core module, engine, or source bytes were changed by this packet's preparation. It does not modify any accepted milestone archive.

The [candidate audit](../storage-candidate-audit-earlier-v1/results.json) pins exactly 92 completed public component/core files in 45 directories. Its SHA-256 is `6a3664ff4ebe283910672090ed4481123ab3d634146781ff7a9321a1302378a8`; the helper authenticates the corresponding index and revalidates 71 deduplicated accepted-report/generated-JavaScript witnesses. It yields only those explicit paths, with no broad filesystem walk. Engines, source/build inputs, private proposals, native freezes, DEBUG/OOM artifacts, symlinks, multiple hardlinks, and already compressed files are excluded.

[compact.py](compact.py) is derived from the completed [v5–v7 helper](../storage-compaction-mature-v5-v7/compact.py). [changes.REVIEW.diff](changes.REVIEW.diff) records the changes: the finite audit-backed whitelist, matching each audited preimage, and a per-file free-space check before creating a copy. The check requires `2 × logicalBytes + 64 MiB` (at most 141,687,260 bytes for this list). This is a reserve policy, not a guarantee against unrelated allocations or filesystem exhaustion.

[dry-run-results.json](dry-run-results.json) pins the external summary and frozen inventory. The dry run completed with 92 eligible files, no failures, and zero compressed files. It observed 1,307,936,237 logical bytes and 1,308,119,040 allocated bytes. This is candidate allocation, not a promised recovery amount. The separate [quiescence review](../storage-compaction-earlier-peer-review-v1/quiescence-results.json) observed no selected paths open; root must repeat that observation immediately before applying.

The reviewed apply command, **not executed by this preparation**, is:

```sh
python3 tests/node-compat/storage-compaction-earlier-v1/compact.py --apply \
  --expected-inventory /tmp/starling-node-compat/storage-compaction-earlier-v1/20261103T174137Z-f18132d7.frozen-inputs.json
```

Applying creates one fresh same-directory copy with `/usr/bin/ditto --hfsCompression --noclone`. Before adoption it verifies logical SHA-256, size, mode, uid/gid, mtime, ACL and application xattrs; only the filesystem compression representation may change. It adopts only a physically smaller copy, retains the original inode through an owned rollback hardlink, atomically replaces the path, and verifies readback before releasing the rollback link. Every before/after step is journalled. Existing accepted paths and logical bytes remain the same. The algorithm does not claim crash/directory-fsync guarantees, induced rollback coverage, or exclusive APFS volume-space attribution. Atime is restored after success; inode/ctime/birthtime and compression metadata are outside the preserved contract.

To reverse compression, first create a separate copy using `ditto --nohfsCompression --nopreserveHFSCompression --noclone`, verify its logical digest and required metadata, and only then replace the path. That reversal is a documented procedure, not an operation performed here. No guest, native build, deletion of accepted files, or host-service change is involved.

[source-receipt.json](source-receipt.json) and [index.json](index.json) freeze this source/dry-run packet independently of the accepted checkpoints. Any later apply run has its own external journal and summary; this dry-run receipt remains historical evidence.
