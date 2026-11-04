# Current ordinary Release corpus: independent postverification

This packet only reads the existing20 compressed files, their metadata and
receipts. It imports no compactor and executes no build, packager, guest,
reversal or corpus rerun. It writes only its own new verification files.

[verify.py](verify.py) authenticates the source/preapply packet at index
`d785bc81…`, the exact20-file audit, frozen preimages, application summary
`8502cb57…` and journal. All20 logical SHA/size/mode/uid/gid/mtime/application
xattrs/ACL values must match their original preimages. Compression metadata is
the intended representation change; every file must be regular, single-link
and have exactly `UF_COMPRESSED=32`. Current allocations and inodes must match
the20 journal after-records. The40 known temporary/rollback names must be absent,
with20 successful copy/headroom/release records and no failure/rollback event.

The32 ordinary report/source/binding witnesses are independently rehashed.
Ten actual component hashes/WIT digests remain bound to the prior independent
Release verification, and ten Jco core files must remain directly referenced by
their reported module. The ordinary report remains byte-identical at SHA
`c865931b5e5573f036d9386517d8b3720224ab80baf27b521cda87860e056161`;
its previous verification and source/preapply packet are not rewritten.

[results.json](results.json) records the measured per-file allocation reduction
and current nonreserved free space. These are not exclusive volume-space causal
proof or a guarantee of future capacity. No new runtime, compatibility, GC-stress,
failure-branch or performance result is claimed. [index.json](index.json) freezes
this separate read-only packet; Root archives adoption independently.
