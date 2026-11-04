# Diagnostic freezer v2: source-only

[The new helper](freeze-diagnostic-engine-v2.py) preserves the reviewed v1 helper.
It has passed Python AST parsing and a source-level schema comparison with the
new diagnostic producer. It has not been imported, executed or used to copy an
engine. See [source review](freeze-diagnostic-engine-v2.source-review.json) for
exact helper/producer/pins/failed-attempt hashes.

The future output is `/tmp/starling-node-compat/foundation-scheduler-v2/native-freeze`,
with `diagnostic-release` and `diagnostic-gc` labels. Coherent adoption of the
v2 producer, real build and separate diagnostic preflight precede any use.
The helper requires the actual61 native database commands and derives the
embedding1/diagnostic1 parent commands from complete pre/post Ninja stdout.
It parses exact `-c` source operands with shlex, never evaluates shell text and
never fabricates compile-database entries. Metadata arrays must match derivation.

The raw before/after stdout, cache and native database snapshots require exact
byte/hash/length equality. Frozen variant filenames are:

- `<label>-parent-targets.before.commands.txt` and `.after.commands.txt`.
- `<label>-CMakeCache.before.txt` and `<label>-CMakeCache.txt`.
- `<label>-compile_commands.before.json` and `<label>-compile_commands.json`.
- `<label>.engine.wasm`, byte-identical `.build.json`, `<label>-builtins.incl`
  and `<label>-freeze-receipt.json`.

Shared `source/` retains308 inputs (306 production plus2 diagnostic); shared
`componentize-source/` retains exactly3 external inputs. Source/producer/policy
pins, generated installation, Cargo, OpenSSL audit/configuration and licenses
are checked/copied. Linked libcrypto is rehashed reference-only; cache sources
and libraries are not duplicated. The receipt records every copied source/path,
digest, byte count and shared/variant distinction plus parent-evidence schema.

All shared and variant destinations are validated before writing. New files use
exclusive creation; existing shared files must match and variant files must be
absent. Every source/destination is rehashed before receipt publication. A later
copy failure preserves an unaccepted partial freeze; never overwrite it on retry.
The helper assumes held trusted directories, not a hostile concurrent filesystem.
Run the separate diagnostic preflight again after actual freezing. This source
check adds no runtime, GC, OOM, reset/reuse, compatibility or performance result.
