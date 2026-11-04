# Unapplied m0.11 core integration proposal on current m0.10 source

This review packet rebases the measured direct-allocation expression on the
current live m0.10 **source** snapshot. It is **not applied, built, componentized
or timed**. Current m0.10 native proof is pending. Private v8-ancestry experiment
results support the proposal but do not establish the combined implementation.
The original195-file source,25-file private controller and128-file raw timing
checkpoints remain immutable.

[The concrete patch](./core-m0.11-rebased.patch) changes four core files and seven
test/fixture files, with no public export/API expansion or host interface added.
[source-receipt.json](./source-receipt.json) captures all304 native ancestry inputs;
only buffer-facade.mjs, unsupported.mjs, core manifest and core generated header
change. The current m0.10 generator reproduces those **exact four reviewed private
candidate core hashes**. All300 other native inputs, the protected10-source guard,
Events m0.10 local profile, stream/web m0.9, native kernel, CMake, generator,
registration, recipe and current admission selector remain byte-identical.

The direct method keeps primary type/finite/raw16MiB/truncation validation and
captured own error fields, then returns `tagTrusted(new U8(unsafeTrunc(length)))`.
The existing captured native Uint8Array and private WeakSet/prototype path provide
JS-owned zeroed no-pool storage without a new C++ kernel, raw borrow or allocator
transfer. Supported methods, exports, caps and encodings stay unchanged;
allocUnsafeSlow and all91 deferred own prototype functions remain refused.
The approved out-of-contract Number.isInteger/secondary isFinite hook difference
remains explicit; primary invalid-input errors are unchanged. Genuine OOM/fault/
DEBUG behavior is untested.

## Exact source-selected harness contract

The core expectation table adds only the finite m0.11 entry with exact facade,
helper, manifest, generated-header and buffer.cpp hashes. Its test-only policy
`zeroed-no-pool-direct-u8-v1` distinguishes the changed body from m0.8's delegated
`zeroed-no-pool-v1`; it is not a runtime feature toggle. m0.1/m0.8 entries retain
their original shapes, hashes, deferred/supported lists and refusal controls.
No observed flag, engine hash or missing-flag fallback is invented. The current
selector's stream legacy allowlist and m0.10 protected ABI guards are unchanged.

The main guest corpus tests finite policy selection and counts the secondary
numeric hooks: m0.11 must invoke neither, m0.8 must invoke each once on valid3.75;
all changes restore in finally before assertions. Main strict initialization
patterns now quote literal module/operation/version and reject lookalike versions.
Host main/HTTP validators require the direct policy's actual guest proof while
accepting unchanged historical m0.1/m0.8 report shapes. Guest policy metadata
contains semantic fields only, preserving the no-inline-facade guard.

The new proposed `http-v11.mjs` retains the current foundation imports and v9-style
positive checks; HTTP builder recognition adds that explicit entry without changing
selected interfaces or host operations. **It does not yet exercise the forthcoming
protected-abort HTTP-v10 cases.** Root will add HTTP-v10 after the focused m0.10
corpus is ready. This packet freezes the first current-source proposal; before
application/promotion, those new positive/handled HTTP cases and their builder
recognition must be additively rebased into v11 and rechecked. Fatal components
must stay separate. No future v10 host acceptance is assumed.

## Completed source/host checks

[host-results.json](./host-results.json) records four forms: base/source ESM and
exact generated strict factories, each10 Node groups, five allocation-policy
groups and240 safely scoped pure-JS refusals. The two direct forms additionally
pass six numeric-hook cases. Ten malformed policy/runtime-proof cases reject;
three strict operation/version regex cases reject punctuation lookalikes and
version prefixes. Real v7/v8/v9 engine bytes/receipts and source roots preserve
their exact m0.1/m0.8 mappings with the unchanged live selector. These are real
historical receipt/source checks, not new engine execution or synthetic flags.

The main source bundle retains only native `node:buffer`/`node:child_process`
imports and excludes JS facades/kernels/adapters. Nine changed JavaScript files
pass syntax; both current generator and `--check`, all304 source comparisons,
protected guards and patch apply-check pass. Host kernel use is an explicit
reference test double; no Node native codec/error oracle or actual child-process
capability runs in inherited-field poison windows. The early host-regex escaping
draft was corrected before freezing, with its source/patch diagnostic preserved.

## Promotion rationale and remaining gates

The private same-path experiment observed lower allocUnsafe call and construction
times at64B/4KiB/512KiB in both orders. That motivates the simpler expression and
removing redundant delegation/validation/fill, without isolating which cost
dominates. Controls had seven slowdowns and five direction reversals; n2
independent processes and seven correlated samples limit any general conclusion.
No older timing is transferred to the rebased source.

The tradeoffs are retained: candidate peakRSS was higher in29/30 comparisons,
capacity higher in4/30, and the minimal snapshot **8,513B larger** despite a14B
smaller engine. No memory, component-size, current-Jco, whole-application,
Wasmtime-throughput, C++-kernel or fill-isolated win is claimed. The initial
incorrect preview1-adapter path and corrected fresh-directory gate remain in the
immutable private experiment.

Before any production claim: finish current m0.10 native acceptance; rebase the
forthcoming HTTP-v10 harness; review/apply the coherent source/test patch; build
fresh actual configured receipts with all protected layout macros; run full core/
allocator/refusal/strict/alias/CJS/snapshot/view gates, ordinary moving-GC ownership
gates, final import audit and the joint fixture on unmodified Wasmtime42 and
official wasmCloud2.11. Preserve historical controls and do not treat the private
experiment as a replacement. Classic Streams, Blob and scheduler work stay
separate. The [ledger proposal](./ledger-proposal.md) changes no active status.
