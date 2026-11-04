# Completed mature v5-v7 output storage pass

This new supplementary pass compresses only 59 completed generated component/core
Wasm files in these 20 explicitly authorized directories beneath
`/tmp/starling-node-compat`:

- `foundations-v7`: add-abort-initialization, add-abort-late-binding, assert,
  buffer, events, http-joint, path, querystring and util.
- `foundations-v6`: assert, buffer, events, http-joint, path, querystring and
  string-decoder.
- `foundations-v5`: codec, http-joint, native and runtime-codec.

The fresh inventory matches the prior estimate exactly: 59 regular nonsymlink
files, each with one link and no initial file flags. No listed file was open in
the exact-path lsof check; root and both peers confirmed no active job touching
these outputs and held them throughout. Eighteen input/source/node_modules
subtrees were excluded. Engines/native-freeze, source, project/build/input,
private/candidate/probe, DEBUG/OOM, symlink and other file names remain excluded.
No old component was executed.

Independent verification passed for all 59 files and
1,109,479,826 unchanged logical bytes. Per-file allocation changed
from 1,109,577,728 to 399,781,888 bytes, a total of
709,795,840 bytes recovered. Available disk after verification
was 1,979,379,712 bytes (about 1.84 GiB),
below the requested 2 GiB pre-build threshold. No build or guest job was started.
These are filesystem allocation observations, not runtime performance, smaller
logical components, shared-extent proof or exclusive attribution of system-wide
free-space changes.

The new helper copies the audited v11-pass4 mutation algorithm. Its source-only
changes are the exact roots/receipt namespace, stronger input/candidate/probe
exclusions, fixed59 count and an explicit expected-inventory argument. Before
any adoption, apply must match the frozen dry-run roots, path set, SHA-256,
required metadata and stable file identities. All-root operation is intentional;
a subset dry run also encounters the global59 guard. Toolchain's independent
read-only review found no blocker and made no edits or compaction calls.

Actual ditto stdout/stderr and return codes are journalled; the algorithm stops
on its first copy failure. This pass had no copy failures. New same-directory
compressed copies pass hash, size, mode, uid/gid, nanosecond mtime, noncompression
xattr-digest and ACL checks before atomic replacement. Original-inode rollback
links remain until successful readback; all were released. The post-adoption
restoration-on-failure branch was not induced. Inode/ctime/birthtime/compression
representation and blocks may change; required metadata and paths remain.

The independent verifier reread every adopted file and journal, rehashed the
frozen inventory and checked all prior helper/receipt pins plus accepted v11's
results hash. A fresh uncompressed demonstration copy passed byte/metadata checks
and was removed only after verification; its compressed-preservation control
remains. Old helpers, results, sources, engines and immutable archives were not
modified. See [results.json](results.json), [inventory-review.json](inventory-review.json)
and [index.json](index.json) for exact paths and digests; raw stdout/journals and
frozen preimages remain separately indexed under the new external namespace.
