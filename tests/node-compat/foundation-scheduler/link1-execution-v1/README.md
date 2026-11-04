Both **private diagnostic** link1 variants completed their native build, freeze,
full frozen preflight and32-input component gates. This aggregate captures
those terminal sessions; it does not run a build, verifier or guest again.
Production acceptance and the latest accepted v11 milestone are separate.

| Variant | Frozen engine | Metadata | Freeze receipt | Full component report |
| --- | --- | --- | --- | --- |
| Normal Release |`46fc6588397b…`,9,764,917 bytes |`99ee415e3893…` |`c0d04828d69c…` |`bf0f0697107e…` |
| Release-GC |`949d24f65390…`,9,766,466 bytes |`23e2e4d61023…` |`b170ea87854e…` |`7d3fe437922d…` |

Exact hashes/paths are in [execution-summary.json](execution-summary.json).
Full sidecars, schema3 freeze receipts, CMake/command/link evidence, wrapper,
Rust/OpenSSL text and source policy are under [native-freeze-text](native-freeze-text/).
Native306 plus diagnostic2, external embedding3, native DB61 (including queue),
strict subset4 and separate parent Ninja1+1 are preserved. Each independent
verification rehashed345 frozen copies and all32 test inputs, including the live
adapter before/after. Four final-link witnesses establish generated command
data; actual spawned LLD arguments and thread counts were not observed.

Per variant,10 components were successfully packaged with imports`[]`: seven
positive execution cases and three fresh fatal/discard cases. Five expected
initialization failures remain distinct. The complete scope includes three
retained main Jco calls and fresh Wasmtime, Node ESM/task/job traces, subsequent
configured-classic evaluation, recorded INIT glue append, late getters, FIFO/
arguments/work limits, queue ownership, three handled/finite-budget controls and
three paired fatal boundaries. The finite control executes65536 callbacks.

Release-GC selects actual kernel instrumentation and retains eight valid hex
roundtrips while callback/object/unregistered Symbol entries are pending without
an application strong co-owner. VM temporary retention is uninstrumented; this
does not prove exclusive VM-root ownership. Ordinary Release does not claim
forced GC. Engine reset was not executed. Fatal instances are discarded and
generic traps may hide the original reason; there is no post-fatal reuse,
general cancellation, request teardown, public process or ALS proof.

Root observed both build/component sessions terminal0. The normal build records
109 steps; the GC reconfiguration records16 incremental steps after the normal
evidence was frozen. Those operational times/free-space readings are not a
resource comparison. No RSS, disk, LLD-thread or performance benefit is claimed.

The exact raw launcher/freezer/component stdout and stderr are under [raw](raw/),
launch records/results/build logs under [launchers](launchers/), and full component
reports plus actual application/initializer text under [components](components/).
The existing root preflight stdout/stderr and phase receipts remain unchanged.
[root-observer-attempt1.json](root-observer-attempt1.json) preserves the incorrect
old-state-label check: the driver exited0, its actual source-defined state was
valid, and the corrected observer passed. It is not hidden or counted as a guest
failure.

Independent read-only normal and GC verification records are copied under
[independent](independent/): results`7459eb2d…`/index`b1ef…` and
results`caca4d68…`/index`90151bc…`. The aggregate rehashed/copied their exact bytes
without rerunning them. [capture-inventory.json](capture-inventory.json) maps166
exact text copies and17 preserved root records to original paths and records51
external binary hash references. It includes the full application/initializer
source for all15 packaging attempts per variant. No engine, component, core Wasm
or object bytes are copied into this repository aggregate.

[index.json](index.json) seals the complete captured text inventory after this
write. Frozen source packets, external artifacts, prior observer evidence and
accepted archives are not modified.
