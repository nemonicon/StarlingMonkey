# Actual relocated Cargo source restoration

On 2026-11-07 Root ran the held `native-cargo-restore-v1` source-only writer
once. `stage-process.json` records its literal pinned Python3.11 argv and
terminal0; `stage.stdout.log` and `stage.stderr.log` retain its raw streams.
The writer creates no Cargo/compiler/network/guest process. The external
output is `/private/tmp/starling-node-compat/native-cargo-restore-v1-first-archives`.

The donors are explicit in `donors.archives.json`:75 registry archives bound
to the final lock checksums, the authenticated Firefox FFI source tree,
and21 native-policy files from the actual portable825 selection. The restored
3506 payload files contain47,176,588 logical bytes; its unchanged receipt is
SHA256 `42559665c9c0a77bab374a6ac84e11f2197e776f79f1742f59cf20ce2304c252`,
3,207,856 bytes. The minimum sampled write-boundary free space was715,485,184
bytes. This is neither a continuous disk observation nor a measured peak.

The original V1 read-only admission failed with `owned root identity`:
receipt publication changed APFS directory nlink6 to7. The historical
`v1-admission-failure.*` files preserve that failure. The source tree,
producer and receipt have not been rewritten or rerestored.

The separate held `native-cargo-restore-admission-v2` reader corrects only
that comparison across publication. It compares stable root dev/ino/mode,
checks exact membership and every source physical record, and still guards
the current complete root row within the read. Its genuine Root readback
passes3507 files including the receipt and464 directories including root.
`stage-readback-v2.json` preserves this structural result and both nlink
observations. Structural consistency does not attest process execution.

`stage-observation.json` joins the original producer, entry, donor config,
receipt and exact argv to the actual terminal0/raw streams. This is an
ordinary Root process observation, without monitor or OS sandbox attestation.
The corrected admission Source is a separate descriptor in the readback.

No Cargo metadata, source compilation, engine rebuild or application trial
is proved by this family. Future metadata must run genuinely against these
relocated inputs; the older offline graph is only its comparison reference.
Private paths are explicit historical inputs and may require restoration on
another machine. Preserve these records when recording any later result.

`restore-result.json.gz` preserves the exact original receipt bytes for future
DATA inspection. `retained-receipt.json` records both compressed and decoded
digests. This stored receipt cannot replace the live restored tree required by
the admission API or establish current file identities on another machine.
