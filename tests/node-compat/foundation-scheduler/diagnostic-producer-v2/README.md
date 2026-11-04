# Diagnostic producer v2: parent-project compile evidence

This UNAPPLIED source-only amendment changes only the separate diagnostic build
recipe. It adds no native source, target, export or capability. Production306 and
the same diagnostic2 inputs remain separate; production admission still rejects
the diagnostic engine. No producer, Ninja query, configuration, compiler, guest
or host was executed while preparing this packet.

The preserved v1 attempt completed all109 native build steps, including compile/link, but failed
receipt generation at `Need one actual diagnostic target compilation`. The
directory-local `compile_commands.json` contains native SpiderMonkey/Starling
targets but omits the ComponentizeJS parent-project embedding and diagnostic
targets. Root preserved the actual Ninja commands, cache, database, launch/log
and failure under `production-adoption-v1/release-attempt-v1/`. The unadmitted
9,764,903-byte engine has no sidecar and was never run. The failed recipe380527…
and its source packet remain unchanged.

The [amendment](producer.UNAPPLIED.patch) follows the existing embedding mechanism:
query actual Ninja rules for `builtin_componentize_embedding` and
`builtin_diagnostics_internal_ticks`. It captures the combined stdout bytes
before and after the native build and refuses differing bytes. It selects exactly
one command for each target by parsing the exact `-c` source operand with `shlex`;
it never evaluates command strings. Those arrays feed the existing embedding and
diagnostic policy fields and retain their original Release/macro/source checks.
There are no invented compile-database rows and no global CMake export flag.

Before the native build it also copies the actual CMake cache and native compile
database. Both must remain byte-equal afterwards. The existing pre/post generated
builtin-installation check, 306-source and2-source guards, embedding-input guards,
recipe/patch hashes, locked Rust and OpenSSL source checks remain intact.

`internalTickDiagnosticPolicy.parentTargetCommandEvidence` records:

- Version `ninja-parent-target-commands-before-after-v2`, the exact Ninja argv and
  configured build directory.
- `before` / `after` files with path, SHA256 and byte count, plus exact equality.
- `targets.embedding` / `targets.diagnostic`, each with target name, actual source
  path and its one compile command. Existing metadata arrays must match these.
- `configuration.cmakeCache` / `configuration.compileCommands`, each with the
  before/after file identities and exact equality. After paths are the existing
  actual cache/database paths and retain their existing metadata digests.

The semantic diagnostic version and finite test IDs remain v1; the required new
producer recipe/evidence hashes distinguish this correction. New pins are in
[pins.json](pins.json). The separate freezer and diagnostic preflight must check
the raw files, configuration snapshots and parsed-array equality before any
future raw componentization. A recipe completion is not runtime acceptance.

The namespace replaces `diagnostic-ticks-v1` with same-length
`diagnostic-ticks-v2`. It changes source, build, artifact and witness names while
preserving the failed attempt. Command evidence uses a directory named for the
artifact and fixed short leaf names, avoiding additional NAME_MAX pressure for
the Release-GC variant. A pre-existing evidence directory is refused rather than
overwritten. Root's new launcher/freezer use the external
`foundation-scheduler-v2` namespace; no artifact tag is required.

Only `bash -n`, five embedded Python AST parses, patch applicability and source
hash checks were performed. No new native or runtime result is claimed. Reset,
cancellation, ALS and public process remain OPEN/absent. The stopped DEBUG/OOM/
fault/raw-memory branch is excluded.

This also supplements the frozen regression-plan-v1 wording about reconstructing
actual compilation: the native database covers native TUs; parent embedding and
diagnostic TUs need their separately captured Ninja target evidence. Production
recipe869 already records an actual Ninja-derived embedding command array, but
does not preserve external pre/post raw command files. This amendment does not
change that production recipe or retroactively add evidence to old receipts. A
future finite production producer/preflight must distinguish those sources and
capture any additional parent-command evidence explicitly.
