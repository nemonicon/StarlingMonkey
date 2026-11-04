# Completed v11 Runtime/GC/getter groups: storage pass4

This pass covers only completed add-abort-runtime, add-abort-gc,
callback-return-observation and allocator-gc-v1 beneath foundations-v11.
The getter group's existing Node parity result remains false; file compression
is storage validation and does not change its semantics or compatibility status.

Independent verification covers all 24 generated component/Jco core Wasm files
and 292,006,386 unchanged logical bytes. Per-file allocation decreased from
292,069,376 to 112,754,688 bytes, totaling 179,314,688 bytes in
the audited physicalBytesRecovered field. Available disk after verification was
1,722,687,488 bytes. These are filesystem allocation observations,
not guest performance, component-size savings, shared-extent proof or an
attribution of earlier externally/system-freed space.

The copied audited algorithm differs only in its exact four-root allowlist,
receipt namespace, frozen count and prior-helper/receipt immutability pins.
Actual copy stdout/stderr capture and first-failure stop remain in place.
Frozen preimages, fsync journals, required bytes/size/mode/uid/gid/nanosecond mtime,
xattr digests and ACLs are checked before and after adoption. Original-inode
rollback links are released only after successful readback. All links were
released; the post-adoption restoration-on-failure branch was not induced.
Inode/ctime/ditto birthtime/compression representation and blocks change while
required metadata and logical paths remain. A fresh decompression round trip
passed; only its new demonstration copy was removed, and the preservation
control remains.

Only explicit generated component/core Wasm names are eligible. Native sources,
engines/native-freeze, private/input/source/log/receipt and active outputs remain
excluded; symlink/link/flag checks and all earlier helper/result pins are intact.
See results.json and index.json for exact paths and hashes. No native build,
guest execution or timing ran in this pass. HTTP may proceed only in its separately
released serial slot and with at least 1.5 GiB initial headroom.
