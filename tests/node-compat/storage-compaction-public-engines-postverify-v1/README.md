# Independent postverification of 72 public engine compression results

**PASS:** all 72 ordinary Release engine files retain their full accepted byte
hashes and required metadata. Every current file is regular, has `nlink=1` and
exact `UF_COMPRESSED=32`, and matches the recorded new inode/allocation. The 144
recorded copy/rollback paths are absent and all 72 rollback-release events are
ordered after successful verification. No source engine was executed.

The executed preimage is byte-identical to the reviewed dry-run preimage
`5e09c1fb…`. Summary `342c53de…` and journal `95130b80…` match the supplied exact
digests. All 38 milestone/sidecar/audit witnesses, both audit/helper source
indexes, the parent helper and all 306 current native policy inputs remain
unchanged. The verifier reads these independently; it never imports or reruns
the compactor.

Summed file allocation fell from **698,212,352** to **275,595,264 bytes**, a
**422,617,088-byte** reduction. The operation's recorded global free space rose
from 1,565,437,952 to 1,827,217,408 bytes, a separate **261,779,456-byte**
nonexclusive observation. Neither value proves unique extent recovery. The
independent later free-space observation is 1,838,886,912 bytes, still below the
2 GiB native-build start requirement. This packet authorizes no build or lower
guard and supplies no compatibility, runtime-memory or performance result.

Required preservation covers logical length, mode, uid/gid, mtime, ordinary
xattrs and ACL. Read-atime, ctime, birthtime and newly introduced filesystem
`com.apple.decmpfs` compression metadata are outside that equality contract.
Flags and inode replacement are checked as the intended representation change.

[results.json](results.json) records full file, cleanup and witness verification.
[verify.py](verify.py) only reads files and platform metadata and writes this new
packet. No compiler, linker, build, component, guest, binary or storage mutation
was executed by the verification.
