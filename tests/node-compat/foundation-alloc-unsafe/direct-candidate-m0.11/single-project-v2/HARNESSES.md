# Prepared private correctness harnesses

Source preflights pass; **neither private native engine exists yet**. No Wizer,
actual component, timing or memory observation is inferred from these checks.
The25-file approved controller checkpoint and original195-file source checkpoint
remain byte-identical. New harness inputs have a separate supplementary index.

`run-installed.mjs --source-preflight` bundles the unchanged installed allocator/
refusal/demand/snapshot fixture plus a six-case numeric-hook helper for each arm.
Native `node:buffer` and `node:child_process` remain external; no facade, reference
kernel or replacement allocator appears in the guest bundle. Numeric-hook helper
results match the approved ESM host model for baseline/candidate. Host reference
kernel use is explicit and confined to this preflight, outside inherited-field
poison. No synthetic engine receipt or observedOFF flag is constructed.

The actual runner requires the controller's matched source/config/library
`pair-results.json` and `admitFrozenEngine(arm)` before running either installed
corpus. It uses the archived v8 harness/selector/packager, exact arm-specific
engine and frozen source receipts, semantic guest contract only, unchanged
10-group Node oracle, five allocation-policy groups,240 pure-JS refusals, exact
BufferList demand, aliases/default/global/static-CJS and deployed bare-cache
checks. It checks two retained Jco calls, fresh Wasmtime42, owned snapshot/shared
views and eleven top-level initialization failures in each arm. Six numeric-hook
cases explicitly test the approved out-of-contract difference after restoring
each hook. Native module registration is distinguished from a new C++ allocator
kernel; the candidate remains the existing registered JS facade using captured
native Uint8Array and private branding.

`run-minimal.mjs --source-preflight` validates the one-export batch source and
unchanged45-case Node oracle/fifteen scenario definitions. Its actual path first
requires **both** installed corpora matching the current exact private engine
hashes. It then packages the identical guest bundle/world/workload for baseline
and candidate; final imports must be empty. Each arm uses two fresh Jco instances,
45 cases each, full zero/no-pool checks at the three sizes, a post-corpus repeat,
and15 fresh Wasmtime42 cases. No host timer/RSS/byte-length sampling occurs.
The public instantiation helper only retains exported Memory objects during
correctness; it neither creates a raw view nor reads their bytes.

Source preflight exposed one missing packaging-only input in the copied helper
closure: archived capability-policy.mjs requires the exact standard0.2.10
interface catalogue. `harness-supplementary-inputs.json` records its internally
required SHA `a9b23a7158e4cfc1951ac166511a2b3d4b8d8b3714794a8757f5198597f80d01`
and the byte-copy in the private project. The catalogue is also archived here.
No approved controller source,293 native input map, private recipe or live
selector changes. It introduces no selected host capability; both component
worlds still require zero emitted imports.

Run actual correctness only after the three v9 builds and both authorized
private4job builds have finished. Use exact Node22, locked toolchain, audited
ComponentizeJS module and Wasmtime42 variables. A later timing run needs its own
coordinated window after both actual correctness/receipt gates pass. This
checkpoint prepares no automatic timing launch and transfers no old timings.
