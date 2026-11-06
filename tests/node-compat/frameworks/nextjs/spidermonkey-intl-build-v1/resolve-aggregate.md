# Inert single-aggregate resolver helper

`resolve-aggregate.py` executes no subprocess or network operation. Importing it
starts nothing. Root must authenticate the helper/config and orchestrate every
issued Cargo command under the existing owned-process/disk-floor monitor.
No Intl SpiderMonkey artifact is needed for this Cargo-only metadata phase.

`--prepare CONFIG.json` requires a fresh absolute owned work path, explicit
locale/PATH directories, plain Cargo/Rustc executable descriptors, the actual
four-tree FFI manifest/root, current four-crate source inventory/root, actual
old aggregate lock and held fork-lock constraints. File descriptors have exact
`{path,sha256,bytes}` fields. The base inventory is
`{files:[{path:relativeToBaseRoot,sha256,bytes}]}` covering exactly the four
`crates/rust-{encoding,hooks,url,multipart}` trees. Root must join that inventory
to its real current native-source inputs. The exported read-only `inventory`
function can enumerate it; enumeration alone is not historical build proof.

Preparation authenticates inputs and copies only these source trees into new
work. It renders one staticlib manifest with exactly four old plus two new
dependencies, the existing `pub use` pattern, CAPI defaults disabled/four exact
features, and the three real fork overrides. HOME is inherited unchanged;
`home`/`CODEX_HOME` are preserved when present. Cargo homes, target and temporary
directories are private. Executable/source paths are caller inputs, with no
Mac-specific path embedded in the helper. Private Cargo homes and explicit Git
configuration suppress incidental user configuration; no OS-hermetic claim is
made. Source and copied files remain protected through `--recheck WORK`.

The output `Cargo.lock` is clearly marked **UNTRUSTED MERGED SEED**. It combines
the old graph and the conservative fork graph, disambiguates dependency IDs,
and adds only the two actual direct dependencies to the aggregate root. It is
not a resolved/accepted lock. No unused root dependency is added to influence
version selection. `cargo generate-lockfile` is deliberately not the first
command: its [documented behavior](https://doc.rust-lang.org/cargo/commands/cargo-generate-lockfile.html)
rebuilds an existing lock using current latest versions.

Root executes and retains these exact command packets from `plan.json`:

1. Online `cargo metadata --format-version 1 --filter-platform wasm32-wasip1`
   reconciles the seed. Capture whole stdout as `WORK/online-metadata.json` and
   complete stderr/terminal before calling `--audit WORK`. Do not add
   `--all-features`, run a build script or compile a crate.
2. Continue only after actual command success and a reviewed
   `lockPolicyPassed=true`: `cargo vendor --locked --versioned-dirs WORK/vendor`.
   It uses the online Cargo home, with no Mozilla source-replacement config
   accidentally inherited. Capture complete configuration stdout and stderr.
3. After vendor DATA checks, use the separate prepared offline Cargo home for
   `cargo metadata --offline --locked` with the same manifest/target. Preserve
   the real raw terminal and verify the lock stayed unchanged. Actual
   logical package/edge/feature equality is compared without pretending the
   differing cache/vendor manifest paths are byte-identical metadata.

Run `--recheck WORK` before and after each actual phase. It hashes the original
and copied source, helper/config, templates/seed/old lock/constraints and
executables. `--audit WORK` reads the actual retained outputs, reports all old
package identities removed/changed, refuses new identities outside the
old/fork pin sets, checks exact CAPI features/Bidi revision, and scans full
vendor package/file checksums against the lock. The vendored Bidi Rust sources
and parsed manifest must match the authenticated Mozilla patched copy; a
legitimate normalization difference fails visibly for review rather than
being silently tolerated. Its online git identity remains exact revision
`ca612daf1c08c53abe07327cb3e6ef6e0a760f0c`, then offline source replacement
preserves that identity. Registry Bidi is not a fallback.

Audit is DATA consistency, not authentication that Cargo actually ran. Root
must correlate raw monitored argv/status/output and enforce the three declared
gates. Old-package changes or unexpected versions make the audit CLI exit1;
preserve that output/failure before deciding any correction. No argument or
existing file substitutes for a genuine resolved lock, successful vendor or
offline `--locked` result. Native build/admission remains separately closed.

The companion templates remain unchanged. Twenty-six benign temporary-fixture
checks cover exact dependencies/features, HOME preservation, source identities,
exclusive copies, seed labeling, latest-ICU refusal, source/symlink/overwrite
and vendor checksum failures. Their fabricated metadata is explicitly test
DATA and never described as a Cargo result. No Cargo/native/guest ran during
these tests; temporary fixtures were removed.
