# Accepted public ordinary Release engines: read-only capacity inventory

This inventory selects exact engine hashes from accepted milestone results,
then checks terminal frozen build sidecars with Release, GC-stress OFF and OOM
testing OFF. It derives frozen engines, original artifacts, final-target outputs
and embedding-project library outputs from those receipts. The allocation-r2
project output is additionally bound to its archived recipe. No engine is run.

The 22 accepted ordinary sidecars yield 78 existing candidate paths. Full hashing
excludes six overwritten mutable project outputs that no longer match an admitted
ordinary hash. **72 paths and 72 distinct inodes remain**, all without
`UF_COMPRESSED`: **698,052,574 logical bytes** and **698,212,352 summed allocated
bytes**. Their exact paths, accepted milestone references, sidecar digests,
content hashes, flags, ownership, mode, timestamp, ACL and xattr digests are in
[results.json](results.json). Stat identity is checked around each reading.

Even eliminating every reported block would not reach 720 MB or 750 MB. That is
an allocation ceiling, not achievable compression recovery: new compressed data
still needs space, and APFS shared extents are not measured. The v11 raw duplicate
engines have known prior `cp -c` restoration provenance against frozen copies;
distinct inodes and `st_blocks` do not establish exclusive allocation. No unique
extent or free-space gain is inferred. No compression attempt is recommended on
the strength of this inventory alone.

Only explicitly derived public paths under `/tmp/starling-node-compat` were
considered. SDK libraries/tools, DEBUG/OOM/private-fault/probe inputs and source
trees are not targets. No existing file, representation, engine, native build,
component, receipt or archive was modified. The first unfrozen reader attempt
lacked `os.listxattr` in this host Python; its source and error are preserved in
`history/`. The final reader uses read-only platform xattr commands and publishes
no result until the inventory succeeds.
