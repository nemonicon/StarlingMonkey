# Additional completed public outputs: dry-run packet

This separate packet prepares transparent filesystem compression for exactly **67 completed ordinary public component/core outputs**. Preparation ran a successful dry run and compressed nothing. The [audit](../storage-candidate-audit-additional-public-v1/inventory.json) is pinned at SHA-256 `dc9e37e95736b9ccd8a630513d02c8ad35e2be24d72b2f3f4743c3393e993e96`, with its exact index pin checked by the helper. No existing helper, receipt, accepted archive or artifact bytes were edited.

Completion is not release acceptance. The inventory includes 15 files from an original terminal failed e2e attempt, build/correctness-only benchmark outputs and ordinary host reports. Their `terminalProof` and kind labels remain in the frozen inventory and run summary. Failed results stay failed; build-only outputs do not become runtime/timing passes. This packet makes no compatibility or performance claim.

[compact.py](compact.py) derives from the independently verified [92-file helper](../storage-compaction-earlier-v1/compact.py) (`0c69a1bc…`). [changes.REVIEW.diff](changes.REVIEW.diff) shows only the new hash-pinned finite input/schema/receipt namespace and evidence labels. The per-file copy/adoption/rollback algorithm and `2 × logicalBytes + 64 MiB` free-space guard are unchanged. The maximum required reserve is105,556,774 bytes for a19,223,955-byte file. The reserve is not a guarantee against unrelated allocations or hidden filesystem costs.

The helper yields **only** the67 explicit audited paths in36 directories, without a broad scan. It authenticates all audit-index entries, original terminal/host/final/later-corrected reports, generated-JavaScript references and paired component digests:63 deduplicated witnesses. Every file must still match its audited SHA, inode/device, logical/allocated size, flags/nlink, mode, uid/gid, mtime, ACL and application-xattr digests. Engines, SDK/library members, source/configuration/native-freeze/private/debug/OOM/probe/diagnostic paths, symlinks, multiple hardlinks and already compressed files are outside this scope.

[dry-run-results.json](dry-run-results.json) pins the external summary and frozen preimages:67 eligible, zero failures, zero compressed files,881,151,952 logical bytes and881,274,880 allocated bytes. Candidate allocation is not a promised recovery amount. The audit's [quiescence observation](../storage-candidate-audit-additional-public-v1/quiescence.json) must be repeated immediately before any separately authorized apply.

The command below is review material; **this preparation did not execute it**:

```sh
python3 tests/node-compat/storage-compaction-additional-public-v1/compact.py --apply \
  --expected-inventory /tmp/starling-node-compat/storage-compaction-additional-public-v1/20261103T180727Z-168da6d2.frozen-inputs.json
```

The unchanged algorithm creates one fresh same-directory `ditto --hfsCompression --noclone` copy, verifies logical bytes and required metadata, and adopts only a physically smaller representation. An owned hardlink retains the verified original inode through atomic replacement and readback; it is released only after success. Before-adoption failures preserve the original. After-adoption verification failures attempt restoration. Journal/rollback branches were not induced, and no crash/directory-fsync guarantee is claimed. In inherited comments, “accepted source” means a verified preimage admitted by the storage algorithm, not milestone release acceptance.

Successful adoption preserves paths, logical size/SHA, mode, uid/gid, mtime, ACL and application xattrs; the compression representation changes. Atime is restored after success. Inode/ctime/birthtime are outside that preservation contract. Summed file-block reductions are not exclusive APFS volume attribution. Reversal requires a separate `ditto --nohfsCompression --nopreserveHFSCompression --noclone` copy, hash/metadata verification and reviewed replacement; it was not executed here.

[source-receipt.json](source-receipt.json) and [index.json](index.json) freeze this source/dry-run packet. A future authorized apply has its own external journal/summary, preserving this dry-run evidence. No compression, deletion of public artifacts, native build, guest invocation, SDK modification or host-service change was performed by this preparation.
