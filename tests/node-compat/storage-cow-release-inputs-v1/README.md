# Exact two-pair Release input CoW proposal

This packet is **source plus dry run only**. It has executed no `clonefile` or
ctypes function call, temporary clone/reservation, replacement, SDK input,
compiler or guest. Root separately decides any apply after source/peer review.
The earlier rejected compression attempt and accepted milestones are unchanged.

The only admitted pairs are the library and archive below. Each source is under
`/tmp/starling-node-compat/native-build`; its target is the corresponding path
under `/tmp/starling-node-compat/improved-build`.

| Relative path in each root | Logical bytes | Pinned SHA-256 |
| --- | ---: | --- |
| `spidermonkey-dist-release/libspidermonkey.a` | 538,170,426 | `298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc` |
| `spidermonkey-release.tar.gz` | 184,568,633 | `c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b` |

There is no directory walk, wildcard, arbitrary path argument or other data
class. Both independent earlier library/member audits are hash-pinned. Library
bytes equal their recorded exact Release archive member; both archive paths
equal the pinned archive SHA. This dry run rehashes all four files; it does not
repeat archive extraction/member streaming or link/execute anything.

[cow.py](cow.py) uses the installed MacOSX26.5 `sys/clonefile.h` declaration:
`c_char_p,c_char_p,c_uint32 -> c_int`, with `CLONE_NOFOLLOW=1`. The ABI is checked
from that local header before preparing a run, and its digest is frozen. The
[Apple primary manual](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/man/man2/clonefile.2)
documents shared data blocks, independent attributes, nonexistent destination,
zero success and errno failure; ownership/mode/ACL exceptions are reasons to
verify attributes rather than assume their preservation. [abi-source.json](abi-source.json)
records the inspected source and interpretation. No cp, ditto, shutil data-copy,
archive extraction or other fallback exists.

The [corrected dry-run receipt](dry-run-results.json) pins two source/target
preimages, each with logical SHA, inode/device, flags/nlink, size/allocation,
mode, uid/gid, mtime, every xattr digest and ACL. All four are regular,
single-link, flags0 files with distinct source/target inodes on the same
filesystem. Source postchecks passed. There were zero clone calls, adoptions,
failures or evidence errors. The earlier provisional source/dry run is retained
under [history/provisional-v1](history/provisional-v1/index.json), followed by
the [pre-backup-review revision](history/pre-backup-ownership-review-v2/index.json).
Their snapshots are historical and must not be used with the final helper.

The reviewed **future** command is:

```sh
python3 tests/node-compat/storage-cow-release-inputs-v1/cow.py --apply \
  --root-build-quiescent \
  --expected-inventory /tmp/starling-node-compat/storage-cow-release-inputs-v1/20261103T185203Z-23662832.frozen-inputs.json
```

The acknowledgement requires Root to stop relevant builds/tasks first; it is
not an automated whole-machine process proof. Apply independently requires an
exact-path `lsof` result1 with empty stdout/stderr, matching frozen preimages,
and at least64MiB operational metadata headroom before each clone. The reserve
does not guarantee freedom from external allocation or ENOSPC.

Only apply resolves libSystem's `clonefile`, reserves/unlinks its own fresh
same-directory temporary name and calls that function once per pair. A nonzero
result stops with no data-copy fallback. Return0 establishes temporary ownership
**before** journal I/O, so later logging failure still reaches owned-clone cleanup.
A failed syscall never authorizes deletion of an unexpected destination.

Only the owned temporary may receive `utime`, restoring the original target's
mtime/atime before replacement; no source or adopted-target timestamp setter is
called. All other required clone metadata must already match the original
target or the operation rejects. Sources receive no programmatic writes or
unlinks. Protected source identity/metadata excludes atime changes caused by
reading; it does not claim every stat field is immutable. Target inode must
change; ctime/birthtime and read-atime are outside the preservation contract.

Before replacement the helper verifies digest, metadata, flags0, nlink1 and a
distinct same-filesystem clone inode, then rechecks both preimages. An owned
hardlink retains the old target inode until atomic replacement and successful
target readback/source recheck. Only then is that rollback link released. The
backup becomes owned only after `os.link` succeeds; every restore/unlink checks
the old device/inode first. An EEXIST path is never considered owned. Cleanup
errors retain owned paths and reach the final failure status. The
verified adoption count and prebuilt result entry are committed immediately
after release, before another fallible journal write. Per-target rollback is
attempted on earlier post-replacement failure; an un-restorable backup is kept.
These are two individual operations, not a two-target transaction: a second
failure can leave the first verified clone adopted, with identical logical bytes.

Required journal failures stop further adoption and latch evidence errors;
failure logging does not suppress cleanup. Final journal/summary storage errors
leave in-memory adoption counts and full status on stdout, marked incomplete
and nonzero. Publication/rollback/crash/ENOSPC branches were **not induced or
tested** here; no crash-atomicity or directory-fsync guarantee is claimed.

`st_blocks` is reported only as file allocation metadata. It does not reveal
unique extents or prove reclamation. A future report can establish direct
syscall return0 and observe a **nonexclusive** free-space delta; it cannot
promise538MiB,722MiB or any other recovery amount from these bytes. No capacity,
performance, future-link or compatibility result follows from this proposal.

[source-receipt.json](source-receipt.json) and [index.json](index.json) freeze the
corrected helper, dry run, ABI evidence, review diff and provisional history.
