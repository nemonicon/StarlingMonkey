# Independent classic342 native verification preparation

This new reader is **prepared, unexecuted against native artifacts**. All four
actual pins remain null. It does not import the producer, launch Ninja, compile,
freeze, export/admit pins, load a componentizer or execute Wasm. The only checks
run during preparation are Python AST parsing and seven pure host test groups
over synthetic command strings and owned tiny text files. Those shape tests
do not establish a positive artifact path.

The source contract is the sealed
[integration packet](../integration-candidate-v1/README.md) and its independently
read [artifact contract](../integration-candidate-v1/artifact-tools/README.md).
The reader pins those two indices, source policy, helper, recipe and tool pins.
It derives an exact 405-copy set: native342, external3, label-specific13,
shared4, repository-tooling23, additional-license8 and artifact-tool12. The two
new classic licenses already belong to native342 and are deduplicated by path.
The producer also freezes the actual linked libcrypto; this is additional to
the prior scheduler native-freeze mechanism.

For each future normal-off, normal-runtime, gc-off or disabled-off artifact it:

- Requires independently reviewed engine/sidecar/freeze/launcher digests before
  reading any engine or creating output. The producer's UNREVIEWED export and
  null consumer pins cannot activate this reader.
- Rehashes every frozen copy and exact native342/external3 source membership,
  tool dependency, source policy/helper, licenses and recipe. It checks actual
  core-Wasm bytes, while making no import or guest-compatibility claim.
- Reads only label-specific frozen CMake cache and compile database. It maps
  the 61 native C++ rows to exact source operands, matches four strict rows,
  the private five, registration and queue to metadata, and checks O3/ThinLTO,
  strict/protected/tick/entropy macros. CLASSIC and GC must occur on exactly
  their intended private targets; disabled-off has no CLASSIC definition.
- Parses the separate recorded AFTER-build parent Ninja stdout as data and
  checks exactly one embedding9d compile operand/command. It does not invent
  before-build evidence or query a mutable build directory.
- Reconciles locked Cargo manifests/lock/command metadata, the existing
  OpenSSL 4,650-file before/after audit receipt, config/recipe/library/license
  hashes, and recorded finite source-admission output. It does not rerun the
  full OpenSSL source audit or execute relocated tooling copies.
- Checks terminal launcher result and build-log digest, explicit environment,
  lifecycle/evidence completeness, and, for GC, the separately anchored prior
  normal-OFF freeze before shared-project reconfiguration. It never reads the
  mutable original normal-OFF cache/database paths retained in sidecar bytes.
- Rehashes all consumed files after verification. Only then can it write a
  fresh result beneath this new review directory. No existing report changes.

After Root freezes a label, create a **new** independently reviewed anchor file
with state `REVIEWED_ACTUAL_CLASSIC_FREEZE_INPUTS_V1`, four variant keys and each
present variant containing exactly `engineSha256`, `engineBytes`,
`metadataSha256`, `freezeReceiptSha256`, `launcherResultSha256`. GC also needs
the normal-off record. Keep this preparation's null file unchanged. Use its
externally reviewed digest as `--pins-sha256`, then invoke:

```sh
python3 tests/node-compat/foundation-classic-streams/independent-native-verification-v1/verify.py normal-off --pins /absolute/new-reviewed-anchors.json --pins-sha256 REVIEWED_SHA --output /absolute/path/inside/this/review/normal-off/results.json
```

No actual engine, sidecar, freeze, launch result or guest pass is claimed here.
The future native proof still cannot establish namespace/aliases/CJS behavior,
stream semantics, first-classic ordering, GC root isolation, cancellation,
reset/reuse, ALS, target-host operation, output imports, size or performance.
