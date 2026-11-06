# Actual old-four-dependency feature control

The single Root-authorized offline Cargo metadata invocation returned **0** in
0.575 seconds. Its original 0af monitor observed Cargo and a Rustc query process;
both exited, with no timeout, signals, errors, forced cleanup or remaining owned
processes. This command did not compile Rust, execute guest code or use a network
resolution phase. HOME retained its inherited value.

The original collector remains **failed** in `old-feature-control-v1-result.json`.
Its post-command assertion incorrectly required all 49 lock entries to appear in
the default metadata graph. The actual old graph contains 48 nodes: the old lock
includes `serde_derive@1.0.218`, while this default graph does not select it. No
command was rerun, and neither the collector nor its failed result was edited.

`old-feature-control-v1-data-review.json` is the separate successful read-only
reconciliation. The old/new locks contain 49/84 packages; all 49 old package
identities and versions remain. The actual old/new metadata graphs contain
48/84 nodes. All 48 old nodes remain, 45 retain their feature sets, and three gain
features:

| Package | Added features | Source of request |
| --- | --- | --- |
| `serde@1.0.218` | `derive`, `serde_derive` | Diplomat core requests `derive,alloc`. |
| `smallvec@1.14.0` | `union` | The new Unicode-bidi FFI enables Unicode-bidi's Smallvec feature. |
| `syn@2.0.99` | `full` | Diplomat and Diplomat core request `full,extra-traits`. |

There are no removed old nodes or features. `serde_derive@1.0.218` becomes a
selected metadata node with its default feature; it was already in the old lock.
Serde itself had `alloc` in old metadata. Neither Serde package has an old build
fingerprint. The 47 retained old package fingerprints match the control feature
sets exactly, including target Smallvec and host Syn.

Cargo metadata feature arrays are logical package-level unions, not compiled
unit records. The source dependency graph places the new Smallvec request under
target Unicode-bidi FFI and the Syn/Serde requests under host Diplomat proc
macros. This control does not establish the final new host/target compilation
units, an Intl library link, or native/guest admission.

The authentic resolver's before/final checks preserved 2,296 original/copied
source files. The control additionally retained exact hash/mode/inode bookends
for its inputs/tools and rehashed all 2,354 vendor files. Free space was
4,409,970,688 bytes before and 4,409,036,800 after; no periodic disk monitoring
claim is made. Registry/Git identities use exact name/version/source; the five
path package identities use name/version/source-null plus authenticated source
bytes, rather than claiming root-dependent package IDs are identical.

The two copy maps authenticate deterministic gzip copies of the entire control
metadata stdout, empty stderr, original terminal/start/owned-process records,
control manifest/source/lock/config and combined offline metadata. Decompressing
a retained copy yields the exact original bytes. The retained index covers this
bounded control only. The original helper, combined lock/vendor and earlier
failed resolution are unchanged.
