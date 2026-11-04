# Successful v11 storage pass2 with preserved failed attempts

This supplementary pass covers exactly four completed directories beneath
foundations-v11: add-abort-off, release-gates-v2/optional,
release-gates-v2/strict-sync and release-gates-v2/strict-runtime. The last directory
ended with a Wizer ENOSPC error; its fully written generated files are storage
complete, and their compression does not establish a runtime pass.

results.json records independent verification of all 64 files and 858,484,404
unchanged logical bytes. Per-file allocated blocks fell from 858,640,384 to
324,558,848 bytes: the audited physicalBytesRecovered field totals 534,081,536
bytes (about 509 MiB). Disk availability after verification was 2,557,476,864
bytes (about 2.38 GiB). These are filesystem storage observations, not execution,
startup or throughput results, nor an independent shared-extent accounting proof.

Space attribution is deliberately separate. Root's bootstrap first observed
2,040,545,280 bytes already free: external/system activity had restored about
1.8 GiB BEFORE any root artifact action. That gain is not attributed to the
bootstrap or this pass. Root reported only a 35,856,384-byte observed increase
during its three-artifact restore operation; cp's COW option alone does not
prove shared physical extents. Our canonical recovery figure above is the
sum of the admitted files' allocated-block decreases, not all system-free change.

The final apply receipt is
/tmp/starling-node-compat/storage-compaction-v11-pass2/20261103T151041Z-85e289e9.summary.json.
Its frozen inventory and fsync journal precede adoption; all64 actual ditto
return codes are zero and stdout/stderr are empty. Independent verification
rehashes original logical bytes and required mode/uid/gid/nanosecond mtime,
xattr digests and ACLs; confirms all rollback links released; and performs a
fresh uncompressed-copy round trip. The original-inode restoration-on-failure
branch was not induced. Inode/ctime/ditto birthtime/compression representation
and blocks change, while required metadata and accepted logical paths remain.

Only explicit generated component/core Wasm names are admitted. Native sources,
engines/native-freeze, private inputs, active output, logs, receipts and earlier
scripts/results are excluded. The copied algorithm retains its original checks
and rollback design. Root approved two error-handling improvements: actual
stdout/stderr (including raw hex) and return-code journaling, and stopping after
the first failure while publishing its failed summary. No adoption precedes all
existing metadata/byte/space-saving checks. Scope and frozen count are explicit.

Failure history remains immutable. The first50 copy failures retained only generic
CalledProcessError text, so their cause is UNCONFIRMED. All50 original hashes,
required metadata and inodes were independently verified unchanged. A count-check
draft also ran before its inventory completed; its assertion and unchanged-scope
apply are documented. The next64-file inventory was complete before its count
check. Its first copy failed with captured No space left on device, and stopped
before adoption. Root's separate code0 copy did not inspect flags/savings and is
not an adoption or compression proof. Histories, original journals, frozen inputs,
stdout and diagnostics are retained. The successful retry uses fresh run IDs;
no failed evidence was overwritten.

No guest execution or native build ran here. Further guest work is strictly serial
and requires root release; no older historical compaction was needed.
